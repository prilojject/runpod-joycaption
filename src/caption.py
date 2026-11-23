"""Run official scripts/batch-caption.py (in-process so the model can stay loaded)."""

from __future__ import annotations

import importlib.util
import logging
import os
import random
from pathlib import Path
from typing import Any, Callable

from .paths import JOYCAPTION_DIR, JOYCAPTION_SHA
from .secret_utils import redact

log = logging.getLogger(__name__)

Progress = Callable[[dict], None]

_BATCH_MOD = None
_TOKENIZER = None
_MODEL = None
_MODEL_KEY: tuple | None = None


def _load_official_module():
    """Import the official batch-caption.py from the pinned SHA clone."""
    global _BATCH_MOD
    if _BATCH_MOD is not None:
        return _BATCH_MOD
    script = os.path.join(JOYCAPTION_DIR, "scripts", "batch-caption.py")
    if not os.path.isfile(script):
        raise RuntimeError(f"official batch-caption.py not found at {script}")
    # Confirm the Docker pin when the stamp file exists.
    stamp = "/opt/joycaption.commit"
    if os.path.isfile(stamp):
        got = open(stamp).read().strip()
        if got != JOYCAPTION_SHA:
            log.warning("joycaption SHA mismatch: /opt/joycaption.commit=%s expected %s", got, JOYCAPTION_SHA)
    spec = importlib.util.spec_from_file_location("joycaption_batch_caption", script)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not import {script}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    # Do not inherit the official script's extremely high pixel cap.
    try:
        from PIL import Image
        from .dataset import MAX_IMAGE_PIXELS
        Image.MAX_IMAGE_PIXELS = MAX_IMAGE_PIXELS
    except Exception:
        pass
    _BATCH_MOD = mod
    return mod


def gpu_info() -> dict[str, Any]:
    info: dict[str, Any] = {"gpu": None}
    try:
        import torch
        if not torch.cuda.is_available():
            return info
        idx = 0
        props = torch.cuda.get_device_properties(idx)
        info.update({
            "gpu": torch.cuda.get_device_name(idx),
            "vram_gb": round(props.total_memory / 2**30, 2),
            "compute_capability": f"{props.major}.{props.minor}",
            "cuda": torch.version.cuda,
        })
    except Exception as exc:
        info["error"] = redact(str(exc)).splitlines()[0][:200]
    return info


def _load_model(model_path: str, quantization: str):
    """Load (or reuse) the official LlavaForConditionalGeneration path.

    Matches official batch-caption.py for bf16, and the official Gradio app's
    BitsAndBytesConfig for 8-bit (vision tower skipped — same comment as upstream).
    """
    global _TOKENIZER, _MODEL, _MODEL_KEY
    key = (os.path.abspath(model_path), quantization)
    if _MODEL is not None and _MODEL_KEY == key:
        return _TOKENIZER, _MODEL
    # Drop a previous quantization / path.
    if _MODEL is not None:
        try:
            del _MODEL
            import gc
            import torch
            gc.collect()
            torch.cuda.empty_cache()
        except Exception:
            pass
        _MODEL = None
        _TOKENIZER = None

    from transformers import AutoTokenizer, LlavaForConditionalGeneration, PreTrainedTokenizer, PreTrainedTokenizerFast

    tokenizer = AutoTokenizer.from_pretrained(model_path, use_fast=True)
    assert isinstance(tokenizer, (PreTrainedTokenizer, PreTrainedTokenizerFast)), type(tokenizer)

    if quantization == "8bit":
        import torch
        from transformers import BitsAndBytesConfig
        qnt_config = BitsAndBytesConfig(
            load_in_8bit=True,
            # Official Gradio comment: Transformer's Siglip implementation has bugs
            # when quantized, so skip the vision tower and projector.
            llm_int8_skip_modules=["vision_tower", "multi_modal_projector"],
        )
        model = LlavaForConditionalGeneration.from_pretrained(
            model_path, torch_dtype="auto", device_map=0, quantization_config=qnt_config,
        )
    else:
        model = LlavaForConditionalGeneration.from_pretrained(
            model_path, torch_dtype="bfloat16", device_map=0,
        )
    assert isinstance(model, LlavaForConditionalGeneration)
    model.eval()
    _TOKENIZER, _MODEL, _MODEL_KEY = tokenizer, model, key
    return tokenizer, model


def run_caption(
    cfg,
    image_paths: list[str],
    model_path: str,
    progress: Progress | None = None,
) -> dict[str, Any]:
    """Caption images using the official ImageDataset + generate loop.

    The official script always reloads the model. This wrapper keeps it in
    process memory so refresh_worker=false is useful on Serverless.
    """
    if not image_paths:
        return {"captioned": 0, "failed": 0}

    mod = _load_official_module()
    if progress:
        progress({"stage": "loading_model", "quantization": cfg.quantization, "dtype": "bfloat16"})
    tokenizer, llava_model = _load_model(model_path, cfg.quantization)

    import torch
    from torch.utils.data import DataLoader

    seed = int(cfg.seed)
    random.seed(seed)
    torch.manual_seed(seed)

    prompts = [mod.Prompt(prompt=cfg.prompt_text, weight=1.0)]
    dataset = mod.ImageDataset(
        prompts,
        [Path(p) for p in image_paths],
        tokenizer,
        llava_model.config.image_token_index,
        llava_model.config.image_seq_length,
    )
    workers = int(cfg.num_workers)
    loader = DataLoader(
        dataset,
        collate_fn=dataset.collate_fn,
        num_workers=workers,
        shuffle=False,
        drop_last=False,
        batch_size=int(cfg.batch_size),
    )
    end_of_header_id = tokenizer.convert_tokens_to_ids("<|end_header_id|>")
    end_of_turn_id = tokenizer.convert_tokens_to_ids("<|eot_id|>")
    assert isinstance(end_of_header_id, int) and isinstance(end_of_turn_id, int)

    prepend = cfg.prepend or ""
    append = cfg.append or ""
    captioned = 0
    failed = 0
    if progress:
        progress({"stage": "captioning", "images": len(image_paths)})

    # The generate / trim / write loop below follows official main() on the pinned SHA.
    for batch in loader:
        if not batch["paths"]:
            continue
        vision_dtype = llava_model.vision_tower.vision_model.embeddings.patch_embedding.weight.dtype
        vision_device = llava_model.vision_tower.vision_model.embeddings.patch_embedding.weight.device
        language_device = llava_model.language_model.get_input_embeddings().weight.device

        import torchvision.transforms.functional as TVF

        pixel_values = batch["pixel_values"].to(vision_device, non_blocking=True)
        input_ids = batch["input_ids"].to(language_device, non_blocking=True)
        attention_mask = batch["attention_mask"].to(language_device, non_blocking=True)

        pixel_values = pixel_values / 255.0
        pixel_values = TVF.normalize(pixel_values, [0.5], [0.5])
        pixel_values = pixel_values.to(vision_dtype)

        generate_ids = llava_model.generate(
            input_ids=input_ids,
            pixel_values=pixel_values,
            attention_mask=attention_mask,
            max_new_tokens=int(cfg.max_new_tokens),
            do_sample=not bool(cfg.greedy),
            suppress_tokens=None,
            use_cache=True,
            temperature=float(cfg.temperature),
            top_k=(None if not cfg.top_k else int(cfg.top_k)),
            top_p=float(cfg.top_p),
        )
        assert isinstance(generate_ids, torch.Tensor)
        generate_ids = generate_ids.tolist()
        generate_ids = [mod.trim_off_prompt(ids, end_of_header_id, end_of_turn_id) for ids in generate_ids]
        captions = tokenizer.batch_decode(generate_ids, skip_special_tokens=False, clean_up_tokenization_spaces=False)
        captions = [c.strip() for c in captions]
        for path, caption in zip(batch["paths"], captions):
            try:
                mod.write_caption(Path(path), prepend + caption + append)
                captioned += 1
            except Exception as exc:
                log.error("failed to write caption for %s: %s", path, redact(str(exc)))
                failed += 1
        if progress:
            progress({"stage": "captioning", "captioned": captioned, "total": len(image_paths)})

    return {"captioned": captioned, "failed": failed}


def collect_captions(images_dir: str, image_paths: list[str]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for path in image_paths:
        rel = os.path.relpath(path, images_dir)
        txt = os.path.splitext(path)[0] + ".txt"
        caption = ""
        if os.path.isfile(txt):
            try:
                caption = open(txt, encoding="utf-8").read()
            except OSError:
                caption = ""
        rows.append({"file": rel.replace("\\", "/"), "caption": caption})
    return rows
