import pytest

from src.config import ConfigError, resolve_config
from src.prompts import DEFAULT_PROMPT


def test_default_descriptive_formal_long():
    cfg = resolve_config({"dataset_url": "https://example.com/a.zip"})
    assert cfg.mode == "descriptive"
    assert cfg.tone == "formal"
    assert cfg.length == "long"
    assert cfg.max_new_tokens == 512
    assert cfg.greedy is False
    assert cfg.overwrite is False
    assert cfg.quantization == "none"
    assert cfg.batch_size == 1
    assert cfg.prompt_text == DEFAULT_PROMPT
    assert "prompt" in cfg.public_dict()
    assert cfg.public_dict()["prompt"] == DEFAULT_PROMPT


def test_quick_preset_is_greedy():
    cfg = resolve_config({"image_url": "https://example.com/a.jpg", "preset": "quick"})
    assert cfg.greedy is True
    assert cfg.max_new_tokens == 256
    assert cfg.prompt_text == DEFAULT_PROMPT


def test_input_overrides_env_and_preset(monkeypatch):
    monkeypatch.setenv("MODE", "straightforward")
    monkeypatch.setenv("MAX_NEW_TOKENS", "128")
    cfg = resolve_config({
        "dataset_url": "https://example.com/a.zip",
        "mode": "descriptive",
        "max_new_tokens": 512,
    })
    assert cfg.mode == "descriptive"
    assert cfg.max_new_tokens == 512
    assert cfg.sources["mode"] == "input"
    assert cfg.sources["max_new_tokens"] == "input"


def test_env_overrides_preset(monkeypatch):
    monkeypatch.setenv("DATASET_URL", "https://example.com/from-env.zip")
    monkeypatch.setenv("GREEDY", "true")
    cfg = resolve_config({}, env=None)
    assert cfg.dataset_url.endswith("from-env.zip")
    assert cfg.greedy is True
    assert cfg.sources["dataset_url"] == "env"


def test_requires_image_or_dataset():
    with pytest.raises(ConfigError, match="image_url or dataset_url"):
        resolve_config({"mode": "descriptive"})


def test_rejects_bad_urls():
    with pytest.raises(ConfigError, match="dataset_url must be an http"):
        resolve_config({"dataset_url": "ftp://x/y.zip"})
    with pytest.raises(ConfigError, match="image_url must be an http"):
        resolve_config({"image_url": "not-a-url"})


def test_rejects_secrets_in_input():
    with pytest.raises(ConfigError, match="secrets must not"):
        resolve_config({"dataset_url": "https://example.com/a.zip", "hf_token": "hf_xxx"})
    with pytest.raises(ConfigError, match="secrets must not"):
        resolve_config({"dataset_url": "https://example.com/a.zip", "api_key": "x"})


def test_redacts_upload_url_in_public_dict():
    cfg = resolve_config({
        "dataset_url": "https://example.com/a.zip",
        "upload_url": "https://bucket.example/presigned?sig=secret",
    })
    assert cfg.public_dict()["upload_url"] == "<presigned url>"


def test_custom_prompt_warns():
    cfg = resolve_config({
        "dataset_url": "https://example.com/a.zip",
        "prompt": "Describe this photo like a haiku.",
    })
    assert cfg.prompt_text == "Describe this photo like a haiku."
    assert any("not a general instruction follower" in w for w in cfg.warnings)


def test_unknown_mode_and_extra_option():
    with pytest.raises(ConfigError, match="mode"):
        resolve_config({"dataset_url": "https://example.com/a.zip", "mode": "qwen-vl"})
    with pytest.raises(ConfigError, match="extra_options"):
        resolve_config({
            "dataset_url": "https://example.com/a.zip",
            "extra_options": ["make it spicy"],
        })


def test_extra_options_slug_and_official_string():
    cfg = resolve_config({
        "dataset_url": "https://example.com/a.zip",
        "extra_options": ["lighting", "Include information about camera angle."],
    })
    assert "Include information about lighting." in cfg.prompt_text
    assert "Include information about camera angle." in cfg.prompt_text
    assert "Include information about lighting." in cfg.extra_options


def test_casual_and_straightforward_and_word_count():
    casual = resolve_config({
        "dataset_url": "https://example.com/a.zip",
        "mode": "descriptive",
        "tone": "casual",
        "length": "short",
    })
    assert "casual tone" in casual.prompt_text
    assert "short" in casual.prompt_text
    straight = resolve_config({
        "dataset_url": "https://example.com/a.zip",
        "mode": "straightforward",
    })
    assert "straightforward caption" in straight.prompt_text
    wc = resolve_config({
        "dataset_url": "https://example.com/a.zip",
        "mode": "descriptive",
        "word_count": 40,
    })
    assert "40 words or less" in wc.prompt_text
