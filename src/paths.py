"""Where models, datasets and outputs live."""

from __future__ import annotations

import os

NETWORK_VOLUME = "/runpod-volume"
JOYCAPTION_DIR = os.environ.get("JOYCAPTION_DIR", "/opt/joycaption")
JOYCAPTION_SHA = "8445b2e55db7856d522e44ae84e7415fcf3413f6"
DEFAULT_MODEL_ID = "fancyfeast/llama-joycaption-beta-one-hf-llava"
DEFAULT_MODEL_REVISION = "ebf414ea497a020da0f82df3913e5b6cb8e9663a"
# Shard sizes on the pinned revision (bytes). Used to verify a complete download.
EXPECTED_SHARDS = {
    "model-00001-of-00004.safetensors": 4_886_313_648,
    "model-00002-of-00004.safetensors": 4_999_820_904,
    "model-00003-of-00004.safetensors": 4_915_917_680,
    "model-00004-of-00004.safetensors": 2_158_029_896,
}


def has_volume() -> bool:
    return os.path.isdir(NETWORK_VOLUME) and os.access(NETWORK_VOLUME, os.W_OK)


def model_cache_dir() -> str:
    if os.environ.get("MODEL_CACHE_DIR"):
        return os.environ["MODEL_CACHE_DIR"]
    if has_volume():
        return os.path.join(NETWORK_VOLUME, "joycaption", "models")
    return "/tmp/joycaption/models"


def output_root() -> str:
    if os.environ.get("OUTPUT_ROOT"):
        return os.environ["OUTPUT_ROOT"]
    if has_volume():
        return os.path.join(NETWORK_VOLUME, "joycaption", "runs")
    return "/tmp/joycaption/runs"


def configure_caches() -> None:
    if has_volume():
        os.environ.setdefault("HF_HOME", os.path.join(NETWORK_VOLUME, "joycaption", "hf-home"))
        os.environ.setdefault("HUGGINGFACE_HUB_CACHE", os.path.join(NETWORK_VOLUME, "joycaption", "hf-hub"))
        os.environ.setdefault("TRANSFORMERS_CACHE", os.path.join(NETWORK_VOLUME, "joycaption", "hf-hub"))
    os.makedirs(model_cache_dir(), exist_ok=True)
    os.makedirs(output_root(), exist_ok=True)
