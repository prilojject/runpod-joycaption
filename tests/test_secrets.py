import logging

from src.secret_utils import RedactFilter, redact


def test_redact_replaces_hf_token(monkeypatch):
    monkeypatch.setenv("HF_TOKEN", "hf_supersecret_token_value")
    monkeypatch.delenv("BUCKET_ACCESS_KEY_ID", raising=False)
    monkeypatch.delenv("BUCKET_SECRET_ACCESS_KEY", raising=False)
    text = redact("failed with token hf_supersecret_token_value trailing")
    assert "hf_supersecret_token_value" not in text
    assert "***" in text


def test_log_filter_redacts(monkeypatch, caplog):
    monkeypatch.setenv("HF_TOKEN", "hf_supersecret_token_value")
    monkeypatch.setenv("BUCKET_SECRET_ACCESS_KEY", "awssecretvalueXXXX")
    log = logging.getLogger("test-joycaption-redact")
    log.handlers.clear()
    log.addFilter(RedactFilter())
    log.setLevel(logging.INFO)
    with caplog.at_level(logging.INFO, logger="test-joycaption-redact"):
        log.info("tok=%s key=%s", "hf_supersecret_token_value", "awssecretvalueXXXX")
    # Filter rewrites record.msg when secrets appear in getMessage().
    # Depending on handler timing, also check redact() directly (already covered)
    # and that the filter does not drop the record.
    rec = logging.LogRecord("test-joycaption-redact", logging.INFO, __file__, 1,
                            "tok=hf_supersecret_token_value", (), None)
    assert RedactFilter().filter(rec) is True
    assert "hf_supersecret_token_value" not in rec.getMessage()
