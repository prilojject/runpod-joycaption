# JoyCaption Batch Captioner for Runpod

[![Runpod](https://img.shields.io/badge/Runpod-Hub-7c3aed)](https://console.runpod.io/hub/listing/prilojject/runpod-joycaption)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

A **Runpod Serverless** worker that batch-captions images for **LoRA / diffusion datasets** with official [JoyCaption Beta One](https://huggingface.co/fancyfeast/llama-joycaption-beta-one-hf-llava).

**Send** a zip (or one `image_url`). **Get** a kohya-style sidecar **`.txt` next to each image**, plus a `captions.json` manifest.

It is a headless wrapper around official [`scripts/batch-caption.py`](https://github.com/fpgaminer/joycaption/blob/8445b2e55db7856d522e44ae84e7415fcf3413f6/scripts/batch-caption.py). Gradio is never started.

This is **not** [runpod-image-lora-trainer](https://github.com/prilojject/runpod-image-lora-trainer) (that trains a LoRA; this only writes captions those trainers can read). It is also **not** a general VQA / Qwen-VL worker — a future Qwen-VL listing is separate and is not included here.

**Built with Llama.** The Beta One weights are licensed under the Llama 3.1 Community License, not MIT. See [License](#license) below.

## What you send / what you get

**Send** `image_url` and/or `dataset_url` (a `.zip` or `.tar.gz` of jpg/png/webp/…). Nested folders are kept. Existing sidecar `.txt` files are skipped unless you set `overwrite: true` (the official script does the same).

```
images.zip
  001.jpg
  002.png
  sub/003.webp
```

**Get** the same tree with captions beside each file, plus a manifest:

```
001.jpg
001.txt
002.png
002.txt
sub/003.webp
sub/003.txt
captions.json
```

Delivered as a zip to a Hugging Face repo, an S3-compatible bucket, a presigned PUT URL, or a Runpod network volume (`/runpod-volume/joycaption/runs/<run_name>/`). If none of those are configured, the job can still return the captions in the response, and a warning that the files will disappear when the worker stops.

## Defaults

| Setting | Default | Notes |
| --- | --- | --- |
| Model | **JoyCaption Beta One** | `fancyfeast/llama-joycaption-beta-one-hf-llava` @ `ebf414ea497a020da0f82df3913e5b6cb8e9663a` |
| Dtype | **bfloat16** (not fp16) | Native Llama 3.1 dtype; about **17 GB VRAM** |
| GPU | **RTX 4090 24 GB** | The official comfort zone; batch size 1 |
| Mode | **Descriptive, formal, long** | Default prompt: `Write a long descriptive caption for this image in a formal tone.` |
| Decode | sampling T=0.6, top-p=0.9 | Set `greedy: true` for deterministic smoke tests |
| `max_new_tokens` | **512** | Official script default is 256; 512 matches the official long-descriptive README / demo |
| `refresh_worker` | **false** | The 17 GB model stays in worker memory |

Public weights (~15.8 GiB, no token) are downloaded at job start and cached under `/runpod-volume/joycaption/models/` when a network volume is attached. They are **not** baked into the image. Without a volume, every cold start re-downloads them — attach a volume for anything other than a one-off test.

Upstream code is pinned to SHA `8445b2e55db7856d522e44ae84e7415fcf3413f6` (fpgaminer/joycaption has no tags). That SHA is the Docker pin only. Releases of *this* repo use `targetCommitish=main`.

> The upstream `scripts/README.md` still says the default model is Alpha Two. That document is stale. On this SHA, `batch-caption.py` already defaults to Beta One. This worker always passes an explicit `--model` path pointing at the local Beta One cache.

## Modes

`descriptive` (formal or casual) and `straightforward` are the official “most useful” modes. Other official types from the JoyCaption README are also available: Stable Diffusion Prompt, MidJourney, Danbooru / e621 / Rule34 / booru-like tag lists, Art Critic, Product Listing, Social Media Post.

Prompts and Extra Options are copied **verbatim** from the official README / `gradio-app/app.py` on the pinned SHA — they are not invented here. MidJourney, booru-like and SD-prompt modes can loop (~1.5–3% of the time). Casual descriptive is officially a bit rough. A custom `prompt` is allowed and logs a warning: Beta One is **not** a general instruction follower.

`8bit` quantization is an option for 16 GB cards (`quantization: "8bit"`). It is not the default on a 4090.

## Example job

```json
{
  "input": {
    "dataset_url": "https://example.com/images.zip",
    "mode": "descriptive",
    "tone": "formal",
    "length": "long",
    "hf_repo_id": "you/my-lora-captions"
  }
}
```

Single image:

```json
{
  "input": {
    "image_url": "https://example.com/photo.jpg",
    "mode": "straightforward",
    "greedy": true
  }
}
```

Hub presets:

1. **LoRA dataset (descriptive, formal, long)** — sampling, 512 tokens
2. **Quick test** — greedy, 256 tokens (for a 2–3 image pipeline check)

A tiny public-domain NASA set lives at [`examples/datasets/tiny_images.zip`](examples/datasets/tiny_images.zip). Sources and licenses are in [`examples/SOURCES.md`](examples/SOURCES.md).

## FAQ

**Is this part of the image-lora trainer?**  
No. This worker only writes sidecar `.txt` captions (and `captions.json`). Train the LoRA with [runpod-image-lora-trainer](https://github.com/prilojject/runpod-image-lora-trainer) or kohya / sd-scripts afterwards.

**Does this include Qwen-VL?**  
No. A future Qwen-VL listing is a separate worker. This repo does not ship or preview it.

**Why is there no Gradio UI?**  
This worker is meant for Runpod Serverless jobs. The official `scripts/batch-caption.py` path is what runs, including its 384×384 Pillow resize and its system prompt.

**Do I need a Hugging Face token for the weights?**  
No. Beta One is public (`gated: false`). A token is only required if you set `hf_repo_id` to upload the result.

**Why bfloat16, not fp16?**  
That is the native dtype of the Llama 3.1 language model inside JoyCaption. Loading it as fp16 is not the official path.

**Will it caption NSFW images?**  
Caption modes usually work. Occasional refusals come from the Llama 3.1 base model, not from an extra safety layer in this worker. This worker does not add a bypass around those refusals.

**Can I keep existing captions?**  
Yes — existing `.txt` sidecars are skipped by default. Pass `overwrite: true` to replace them. `prepend` / `append` are also supported.

## Development

```bash
python -m pip install -r requirements-dev.txt
python -m pytest tests -q
```

The GPU smoke test is `joycaption_beta_one_descriptive_smoke` in [`.runpod/tests.json`](.runpod/tests.json): Beta One / descriptive formal / greedy / 256 tokens / three NASA public-domain images, on an RTX 4090.

## License

The **worker code** in this repository is MIT, © 2026 prilojject.

Upstream JoyCaption **code** (`fpgaminer/joycaption`) is Apache-2.0, © 2024 fpgaminer@bitcoin-mining.com. See [LICENSE.upstream](LICENSE.upstream). Prompt-builder fragments in `src/prompts.py` stay Apache-2.0.

The **weights** are **not** MIT. JoyCaption Beta One is a Llama 3.1 derivative.

**Built with Llama.**

Llama 3.1 is licensed under the Llama 3.1 Community License, Copyright © Meta Platforms, Inc. All Rights Reserved.

See [NOTICE](NOTICE), [LLAMA_LICENSE](LLAMA_LICENSE) and [LLAMA_USE_POLICY.md](LLAMA_USE_POLICY.md). The Community License includes a 700 million monthly active user (MAU) threshold; if you exceed it you need a separate license from Meta. That threshold is not relevant to this listing itself.

Do not describe these weights as MIT-licensed, unrestricted, or free of conditions.
