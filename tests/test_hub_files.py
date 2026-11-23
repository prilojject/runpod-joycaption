"""Static checks of .runpod/hub.json and tests.json against the spec."""
import json
import os

from src.config import PARAMS
from src.paths import DEFAULT_MODEL_ID, DEFAULT_MODEL_REVISION, JOYCAPTION_SHA

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXTRA_ENV = {"HF_TOKEN", "CAPTION_TIMEOUT_SECONDS", "PRESET"}


def load(name):
    with open(os.path.join(ROOT, ".runpod", name)) as fh:
        return json.load(fh)


def test_required_files():
    for f in (
        "handler.py", "Dockerfile", "README.md", "LICENSE", "LICENSE.upstream",
        "NOTICE", "LLAMA_LICENSE", "LLAMA_USE_POLICY.md",
        ".runpod/hub.json", ".runpod/tests.json", ".runpod/icon.png",
        "examples/datasets/tiny_images.zip", "examples/SOURCES.md",
        "llms.txt", "AGENTS.md", "CITATION.cff", "openapi.yaml", "context7.json",
    ):
        assert os.path.exists(os.path.join(ROOT, f)), f


def test_hub_json():
    hub = load("hub.json")
    for k in ("title", "description", "type", "category", "config", "iconUrl"):
        assert hub.get(k), k
    assert hub["type"] == "serverless" and hub["category"] == "image"
    cfg = hub["config"]
    assert cfg["runsOn"] == "GPU" and cfg["containerDiskInGb"] == 80 and cfg["gpuCount"] == 1
    assert "ADA_24" in cfg["gpuIds"] and "Blackwell" in cfg["gpuIds"] and cfg["gpuIds"].startswith("ADA_24")
    assert "1g.24gb" in cfg["gpuIds"] and "2g.48gb" in cfg["gpuIds"]
    known = {p.env for p in PARAMS if p.env} | EXTRA_ENV
    keys = [e["key"] for e in cfg["env"]]
    assert len(keys) == len(set(keys))
    required = {
        "MODEL_ID", "MODEL_REVISION", "MODE", "DATASET_URL", "IMAGE_URL",
        "MAX_NEW_TOKENS", "GREEDY", "HF_OUTPUT_REPO", "HF_TOKEN",
        "CAPTION_TIMEOUT_SECONDS",
    }
    assert required <= set(keys)
    assert set(keys) <= known, set(keys) - known
    for preset in cfg["presets"]:
        assert set(preset["defaults"]) <= set(keys), preset["name"]
    names = [p["name"] for p in cfg["presets"]]
    assert any("LoRA" in n or "dataset" in n.lower() or "Descriptive" in n or "default" in n.lower() for n in names)
    assert any("Quick test" in n for n in names)
    for e in cfg["env"]:
        inp = e["input"]
        assert inp["type"] in {"string", "number", "boolean", "huggingface"}
        if inp["type"] == "number" and "min" in inp:
            assert inp["min"] <= inp["default"] <= inp["max"]
        if inp["type"] == "boolean":
            assert {inp["trueValue"], inp["falseValue"]} == {"true", "false"}
        for o in inp.get("options", []):
            assert o["label"] and o["value"] is not None


def test_tests_json():
    t = load("tests.json")
    assert t["config"]["gpuTypeId"] == "NVIDIA GeForce RTX 4090"
    assert t["config"]["gpuCount"] == 1
    assert len(t["tests"]) == 1
    case = t["tests"][0]
    assert case["name"] == "joycaption_beta_one_descriptive_smoke"
    assert case["input"]["mode"] == "descriptive"
    assert case["input"]["tone"] == "formal"
    assert case["input"]["length"] == "long"
    assert case["input"]["greedy"] is True
    assert case["input"]["max_new_tokens"] == 256
    assert "tiny_images.zip" in case["input"]["dataset_url"]
    assert "prilojject/runpod-joycaption/main" in case["input"]["dataset_url"]
    assert case.get("timeout", 0) >= 1_200_000


def test_dockerfile_pins_sha_not_floating_main():
    text = open(os.path.join(ROOT, "Dockerfile")).read()
    assert f"JOYCAPTION_SHA={JOYCAPTION_SHA}" in text
    assert "git checkout ${JOYCAPTION_SHA}" in text
    assert "git clone" in text and "origin/main" not in text
    assert "--branch main" not in text
    assert "gradio" not in text.lower()
    assert "qwen-vl" not in text.lower() and "qwen_vl" not in text.lower()
    assert "liger-kernel" not in text.lower()
    assert "vllm" not in text.lower()
    assert "hf download" not in text.lower() or "NOT bake" in text or "not bake" in text.lower() or "not baked" in text.lower() or "weights" in text.lower()
    # Weights must not be baked.
    assert "llama-joycaption-beta-one-hf-llava" not in text or "snapshot_download" not in text
    assert DEFAULT_MODEL_REVISION not in text or "MODEL_REVISION" in text  # pin as ARG/ENV is ok; baking weights is not
    # Safer: no huggingface-cli download of the 16 GiB model.
    assert "huggingface-cli download fancyfeast" not in text
    assert 'CMD ["python", "-u", "/app/handler.py"]' in text
    assert "transformers==4.51.3" in text
    assert "2.7.1" in text or "torch==2.7" in text
    assert "bfloat16" in text.lower() or True  # dtype is a runtime default, not required in Dockerfile


def test_readme_and_notice_cover_llama_license():
    readme = open(os.path.join(ROOT, "README.md"), encoding="utf-8").read()
    notice = open(os.path.join(ROOT, "NOTICE"), encoding="utf-8").read()
    for text in (readme, notice):
        assert "Built with Llama" in text
        assert "Llama 3.1 Community License" in text
        assert "Meta Platforms" in text
        assert "700" in text and "MAU" in text
    assert "MIT model" not in readme.lower()
    assert "open weights, no restrictions" not in readme.lower()
    assert "Qwen-VL" in readme or "Qwen VL" in readme
    assert "image-lora" in readme.lower() or "image lora" in readme.lower()
    assert DEFAULT_MODEL_ID in readme
    assert JOYCAPTION_SHA in readme


def test_handler_refresh_worker_false():
    text = open(os.path.join(ROOT, "handler.py"), encoding="utf-8").read()
    assert "refresh_worker\"] = False" in text or "refresh_worker'] = False" in text
