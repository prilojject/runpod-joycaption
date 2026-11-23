"""Input schema for the headless JoyCaption batch worker.

Every parameter comes from (highest priority first):

1. the job ``input`` object,
2. an environment variable (what the Runpod Hub deploy form sets),
3. the preset defaults,
4. the built-in default.

Dependency-free so it can be unit-tested and used for a dry run without a GPU.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from typing import Any, Mapping

from .paths import DEFAULT_MODEL_ID, DEFAULT_MODEL_REVISION
from .prompts import assemble_prompt

HF_REPO_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*/[A-Za-z0-9][A-Za-z0-9._-]*$")
URL_RE = re.compile(r"^https?://\S+$")
RUN_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,99}$")

TRUE_STRINGS = {"1", "true", "yes", "y", "on", "enabled"}
FALSE_STRINGS = {"0", "false", "no", "n", "off", "disabled", ""}

QUANTIZATION = ("none", "8bit")
TONES = ("formal", "casual")

# Default max_new_tokens is 512 for long descriptive (the official script
# default is 256; the official README / Gradio slider uses 512).
MAX_NEW_TOKENS_DEFAULT = 512

PRESETS: dict[str, dict[str, Any]] = {
    "default": {
        "mode": "descriptive",
        "tone": "formal",
        "length": "long",
        "max_new_tokens": MAX_NEW_TOKENS_DEFAULT,
        "greedy": False,
        "batch_size": 1,
    },
    "quick": {
        "mode": "descriptive",
        "tone": "formal",
        "length": "long",
        "max_new_tokens": 256,
        "greedy": True,
        "batch_size": 1,
    },
}


@dataclass(frozen=True)
class Param:
    name: str
    type: type
    default: Any
    env: str | None = None
    min: float | None = None
    max: float | None = None
    choices: tuple | None = None
    help: str = ""


PARAMS: list[Param] = [
    Param("image_url", str, "", "IMAGE_URL",
          help="https URL of a single image (jpg/png/webp/...). Use instead of, or together with, dataset_url."),
    Param("dataset_url", str, "", "DATASET_URL",
          help="https URL of a .zip / .tar(.gz) of images. Sidecar .txt files are written next to each image."),
    Param("mode", str, "descriptive", "MODE",
          help="Caption mode. Default descriptive. Also straightforward, and the other official JoyCaption types."),
    Param("tone", str, "formal", "TONE", choices=TONES,
          help="Tone for descriptive mode: formal (default) or casual."),
    Param("length", str, "long", "LENGTH",
          help="Caption length: long (default), medium, short, very short, very long, any, or a word count."),
    Param("word_count", int, 0, "WORD_COUNT", min=0, max=2048,
          help="If >0, use the official numeric word-count prompt template and ignore length."),
    Param("prompt", str, "", "PROMPT",
          help="Custom prompt. Overrides mode/tone/length. Beta One is not a general instruction follower."),
    Param("character_name", str, "", "CHARACTER_NAME",
          help="Name substituted into the official 'refer to them as {name}' Extra Option."),
    Param("max_new_tokens", int, MAX_NEW_TOKENS_DEFAULT, "MAX_NEW_TOKENS", min=1, max=2048,
          help="Maximum caption tokens. 512 is the default for long descriptive; the official script default is 256."),
    Param("greedy", bool, False, "GREEDY",
          help="Greedy decoding (useful for smoke tests). Default is sampling at T=0.6, top-p=0.9."),
    Param("temperature", float, 0.6, "TEMPERATURE", min=0.0, max=2.0),
    Param("top_p", float, 0.9, "TOP_P", min=0.0, max=1.0),
    Param("top_k", int, 0, "TOP_K", min=0, max=1000,
          help="Optional top-k. 0 means the official default (None)."),
    Param("batch_size", int, 1, "BATCH_SIZE", min=1, max=8,
          help="Official default is 1. Keep small on a 24 GB GPU."),
    Param("overwrite", bool, False, "OVERWRITE",
          help="Overwrite existing sidecar .txt files. The official script skips them by default."),
    Param("prepend", str, "", "PREPEND", help="String prepended to every caption (official --prepend)."),
    Param("append", str, "", "APPEND", help="String appended to every caption (official --append)."),
    Param("quantization", str, "none", "QUANTIZATION", choices=QUANTIZATION,
          help="none (default bf16) or 8bit for 16 GB cards. Default on a 4090 is none."),
    Param("model_id", str, DEFAULT_MODEL_ID, "MODEL_ID",
          help="Hugging Face model id. Default is JoyCaption Beta One."),
    Param("model_revision", str, DEFAULT_MODEL_REVISION, "MODEL_REVISION",
          help="Pinned weights revision. Do not switch to a floating main."),
    Param("hf_repo_id", str, "", "HF_OUTPUT_REPO",
          help="Upload the captions zip + captions.json here (needs HF_TOKEN with write)."),
    Param("hf_private", bool, True, "HF_PRIVATE"),
    Param("upload_url", str, "", None, help="Presigned HTTP PUT URL for the captions zip."),
    Param("upload_to_bucket", bool, True, "UPLOAD_TO_BUCKET",
          help="If BUCKET_* env vars are set, upload the artifacts and return URLs."),
    Param("return_captions_in_response", bool, True, "RETURN_CAPTIONS_IN_RESPONSE",
          help="Include {file, caption} objects in the job output (no image bytes)."),
    Param("run_name", str, "", "RUN_NAME",
          help="Folder name for outputs. Default: the Runpod job id."),
    Param("seed", int, 1234, "SEED", min=0),
    Param("dry_run", bool, False, "DRY_RUN",
          help="Download + validate images, check that weights are reachable. No GPU work."),
    Param("preset", str, "default", "PRESET", choices=tuple(PRESETS),
          help="Named defaults. 'default' is descriptive formal long; 'quick' is greedy with 256 tokens."),
    Param("num_workers", int, 2, "NUM_WORKERS", min=1, max=2,
          help="DataLoader workers. Official script default is 4; 1–2 is enough on Serverless."),
]

PARAM_BY_NAME = {p.name: p for p in PARAMS}

ALIASES = {
    "dataset": "dataset_url",
    "zip_url": "dataset_url",
    "image": "image_url",
    "url": "image_url",
    "caption_mode": "mode",
    "caption_type": "mode",
    "caption_length": "length",
    "max_tokens": "max_new_tokens",
    "do_sample": "greedy",  # inverted later if needed — actually don't invert; ignore
    "output_repo": "hf_repo_id",
    "presigned_url": "upload_url",
    "name": "character_name",
    "quant": "quantization",
    "dtype_quant": "quantization",
}


class ConfigError(ValueError):
    def __init__(self, errors: list[str]):
        super().__init__("; ".join(errors))
        self.errors = errors


@dataclass
class ResolvedConfig:
    values: dict[str, Any]
    sources: dict[str, str] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    extra_options: list[str] = field(default_factory=list)
    prompt_text: str = ""

    def __getattr__(self, item: str) -> Any:
        try:
            return self.values[item]
        except KeyError as exc:  # pragma: no cover
            raise AttributeError(item) from exc

    def public_dict(self) -> dict[str, Any]:
        out = dict(self.values)
        if out.get("upload_url"):
            out["upload_url"] = "<presigned url>"
        out["extra_options"] = list(self.extra_options)
        out["prompt"] = self.prompt_text
        return out


def _coerce(param: Param, raw: Any) -> Any:
    t = param.type
    if t is bool:
        if isinstance(raw, bool):
            return raw
        if isinstance(raw, (int, float)) and raw in (0, 1):
            return bool(raw)
        s = str(raw).strip().lower()
        if s in TRUE_STRINGS:
            return True
        if s in FALSE_STRINGS:
            return False
        raise ValueError(f"{param.name}: expected boolean, got {raw!r}")
    if t is int:
        if isinstance(raw, bool):
            raise ValueError(f"{param.name}: expected integer, got boolean")
        if isinstance(raw, float):
            if not raw.is_integer():
                raise ValueError(f"{param.name}: expected integer, got {raw!r}")
            return int(raw)
        s = str(raw).strip()
        try:
            return int(float(s)) if re.fullmatch(r"-?\d+(\.0+)?", s) else int(s)
        except ValueError as exc:
            raise ValueError(f"{param.name}: expected integer, got {raw!r}") from exc
    if t is float:
        if isinstance(raw, bool):
            raise ValueError(f"{param.name}: expected number, got boolean")
        if isinstance(raw, (int, float)):
            return float(raw)
        try:
            return float(str(raw).strip())
        except ValueError as exc:
            raise ValueError(f"{param.name}: expected number, got {raw!r}") from exc
    if t is str:
        if not isinstance(raw, (str, int, float)) or isinstance(raw, bool):
            raise ValueError(f"{param.name}: expected string")
        return str(raw).strip()
    raise TypeError(t)  # pragma: no cover


def _parse_extra_options(raw: Any) -> list[str]:
    if raw is None or raw == "":
        return []
    if isinstance(raw, str):
        # comma-separated slugs or a single official sentence
        if "\n" in raw:
            items = [p.strip() for p in raw.split("\n") if p.strip()]
        elif raw.startswith("["):
            import json
            items = json.loads(raw)
        else:
            # A single official sentence often contains commas; only split on
            # commas when every part looks like a slug (no spaces, or short).
            if ", " in raw and any(c.isupper() for c in raw):
                items = [raw]
            else:
                items = [p.strip() for p in raw.split(",") if p.strip()]
    elif isinstance(raw, (list, tuple)):
        items = list(raw)
    else:
        raise ValueError(f"extra_options: expected a list or string, got {type(raw).__name__}")
    return [str(x) for x in items]


def resolve_config(job_input: Mapping[str, Any] | None,
                   env: Mapping[str, str] | None = None) -> ResolvedConfig:
    env = dict(os.environ if env is None else env)
    raw_in = dict(job_input or {})
    errors: list[str] = []
    warnings: list[str] = []
    values: dict[str, Any] = {}
    sources: dict[str, str] = {}

    normalized_input: dict[str, Any] = {}
    extra_raw = None
    extra_source = "default"
    for key, val in raw_in.items():
        name = ALIASES.get(key, key)
        if name == "do_sample":
            # do_sample is the inverse of greedy; only honor it when greedy is unset.
            continue
        if name == "extra_options":
            extra_raw = val
            extra_source = "input"
            continue
        if name in normalized_input and name != key:
            warnings.append(f"alias {key} ignored; {name} already set")
            continue
        normalized_input[name] = val

    if extra_raw is None and env.get("EXTRA_OPTIONS"):
        extra_raw = env["EXTRA_OPTIONS"]
        extra_source = "env"

    preset_name = "default"
    for candidate, source in (
        (normalized_input.get("preset"), "input"),
        (env.get("PRESET"), "env"),
    ):
        if candidate is not None and str(candidate).strip() != "":
            name = str(candidate).strip().lower()
            if name not in PRESETS:
                errors.append(f"preset: unknown value {candidate!r} (use default or quick)")
            else:
                preset_name = name
            break

    preset = dict(PRESETS[preset_name])

    for param in PARAMS:
        raw = None
        source = "default"
        if param.name in normalized_input and normalized_input[param.name] is not None and normalized_input[param.name] != "":
            raw = normalized_input[param.name]
            source = "input"
        elif param.env and env.get(param.env) not in (None, ""):
            raw = env[param.env]
            source = "env"
        elif param.name in preset:
            raw = preset[param.name]
            source = f"preset:{preset_name}"
        else:
            raw = param.default
            source = "default"

        if raw is None:
            values[param.name] = param.default
            sources[param.name] = source
            continue
        try:
            val = _coerce(param, raw)
            if param.name == "tone":
                val = str(val).strip().lower()
            if param.name == "mode":
                val = str(val).strip()
            if param.name == "quantization":
                val = str(val).strip().lower().replace("int8", "8bit").replace("8-bit", "8bit")
                if val in {"bf16", "bfloat16", "fp16", "none", "no", "off"}:
                    val = "none"
            if param.name == "length":
                val = str(val).strip()
            if param.choices and val not in param.choices:
                raise ValueError(f"{param.name}: expected one of {param.choices}, got {val!r}")
            if param.min is not None and isinstance(val, (int, float)) and val < param.min:
                raise ValueError(f"{param.name}: {val} is below the minimum {param.min}")
            if param.max is not None and isinstance(val, (int, float)) and val > param.max:
                raise ValueError(f"{param.name}: {val} is above the maximum {param.max}")
            values[param.name] = val
            sources[param.name] = source
        except ValueError as exc:
            errors.append(str(exc))

    extras: list[str] = []
    try:
        from .prompts import resolve_extra_options
        extras = resolve_extra_options(_parse_extra_options(extra_raw))
    except ValueError as exc:
        errors.append(str(exc))
    except Exception as exc:  # json errors etc.
        errors.append(f"extra_options: {exc}")

    # Tokens must never arrive in the job input.
    for banned in ("hf_token", "token", "authorization", "api_key", "secret", "password",
                   "aws_secret_access_key", "bucket_secret_access_key"):
        if banned in {k.lower() for k in raw_in}:
            errors.append("secrets must not be sent in the job input; use Runpod secrets / env")
            break

    if not values.get("image_url") and not values.get("dataset_url"):
        errors.append("image_url or dataset_url is required")
    if values.get("image_url") and not URL_RE.match(values["image_url"]):
        errors.append("image_url must be an http(s) URL")
    if values.get("dataset_url") and not URL_RE.match(values["dataset_url"]):
        errors.append("dataset_url must be an http(s) URL")
    if values.get("upload_url") and not URL_RE.match(values["upload_url"]):
        errors.append("upload_url must be an http(s) URL")
    if values.get("hf_repo_id") and not HF_REPO_RE.match(values["hf_repo_id"]):
        errors.append("hf_repo_id must look like 'user/repo'")
    if values.get("run_name") and not RUN_NAME_RE.match(values["run_name"]):
        errors.append("run_name may only contain letters, digits, '.', '_' and '-'")

    prompt_text = ""
    if not errors:
        try:
            wc = values["word_count"] or None
            prompt_text, prompt_warnings = assemble_prompt(
                mode=values["mode"],
                tone=values["tone"],
                length=values["length"],
                extra_options=extras,
                name=values["character_name"],
                custom_prompt=values["prompt"] or None,
                word_count=wc if wc else None,
            )
            warnings.extend(prompt_warnings)
        except ValueError as exc:
            errors.append(str(exc))

    if errors:
        raise ConfigError(errors)

    values["preset"] = preset_name
    sources.setdefault("preset", "default" if preset_name == "default" else sources.get("preset", "input"))
    return ResolvedConfig(
        values=values,
        sources=sources,
        warnings=warnings,
        extra_options=extras,
        prompt_text=prompt_text,
    )
