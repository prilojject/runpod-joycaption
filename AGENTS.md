# Agent notes — runpod-joycaption

## What this worker is

A Runpod Serverless **headless JoyCaption batch captioner** for LoRA / diffusion datasets. Input: one `image_url` and/or a zip of images. Output: kohya-style sidecar `.txt` next to each image, plus `captions.json`.

Wrap official `scripts/batch-caption.py` on the pinned SHA. Do **not** start Gradio or ComfyUI. Do **not** fold this into `runpod-image-lora-trainer`. Do **not** add or preview a Qwen-VL path. Do **not** bake weights into the image.

## Pinned upstream

- Code: `fpgaminer/joycaption` @ SHA `8445b2e55db7856d522e44ae84e7415fcf3413f6` (written to `/opt/joycaption.commit`). There are no upstream tags. Do **not** clone a floating `main`.
- Weights: `fancyfeast/llama-joycaption-beta-one-hf-llava` @ `ebf414ea497a020da0f82df3913e5b6cb8e9663a` (~15.8 GiB, public, no token). Cache under `/runpod-volume/joycaption/models/`.
- The SHA is the Docker pin only. GitHub releases of *this* repo must use `targetCommitish=main` (a SHA target breaks Runpod Hub's `git clone -b`).
- `scripts/README.md` still claims the default model is Alpha Two. That is stale. `batch-caption.py` on this SHA already defaults to Beta One. Always pass an explicit local `--model` / model path.

## Defaults to keep

- Beta One, **bfloat16** (not fp16), ~17 GB VRAM, default GPU 24 GB (RTX 4090), `batch_size=1`
- Mode: Descriptive, formal, long. Default prompt: `Write a long descriptive caption for this image in a formal tone.`
- `max_new_tokens=512` for long descriptive (official script default is 256)
- Decode: sampling T=0.6, top-p=0.9; greedy is an option (use it for smoke)
- `refresh_worker=false` (keep the model in memory)
- `containerDiskInGb=80`
- DataLoader `num_workers`: 1–2
- Prompts and Extra Options must be copied verbatim from the official README / `gradio-app/app.py` on the pinned SHA (`src/prompts.py` is Apache-2.0)
- Use the official script path only: 384×384 Pillow resize, official LLaVA chat template, official system prompt. Do not mix AutoProcessor into that path. Do not “improve” the template. Do not add a safety bypass around Llama refusals.
- Enforce a reasonable pixel/byte limit in the handler. Do not copy the official script’s `PIL.Image.MAX_IMAGE_PIXELS = 933120000`.

## License (strict)

- Worker code: MIT
- Upstream code: Apache-2.0
- Weights: **Llama 3.1 Community License, not MIT**. README and NOTICE must say “Built with Llama” and include: “Llama 3.1 is licensed under the Llama 3.1 Community License, Copyright © Meta Platforms, Inc. All Rights Reserved.” Ship `LLAMA_LICENSE` and `LLAMA_USE_POLICY.md`. Mention the 700M MAU threshold. Never claim “MIT model” or “open weights, no restrictions.”

## Tests

- Unit tests (`tests/`) must run without a GPU and without model weights.
- The Hub smoke test is one case only: `joycaption_beta_one_descriptive_smoke` — descriptive formal, greedy, 256 tokens, `tiny_images.zip` (NASA public-domain images documented in `examples/SOURCES.md`), RTX 4090, timeout 20 min.
- After a paid GPU test: delete the endpoint, pod and registry auth. Confirm with GraphQL that leftover smoke endpoints are gone. Leave protected pods `92anyumh6q7jrf` and `oejzh2afh8hcym` (and volumes `13faqbphuo`, `fv2c638zex`) untouched.

## Secrets

Never print `RUNPOD_API_KEY`, `HF_TOKEN`, `gh` tokens, or `BUCKET_*` values. Never accept tokens in the job input.
