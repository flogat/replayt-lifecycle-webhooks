"""Structured logging redaction (backlog fa75ecf3, SPEC_AUTOMATED_TESTS L1–L8)."""

from __future__ import annotations

import logging

import pytest

from replayt_lifecycle_webhooks.redaction import (
    REDACTED_PLACEHOLDER,
    DEFAULT_SENSITIVE_HEADER_NAMES,
    DEFAULT_SENSITIVE_MAPPING_KEYS,
    format_safe_webhook_log_extra,
    redact_headers,
    redact_mapping,
)


def test_l1_redacted_placeholder_constant() -> None:
    assert REDACTED_PLACEHOLDER == "[REDACTED]"
    assert REDACTED_PLACEHOLDER.isascii()


def test_l2_redact_headers_new_mapping_and_authorization() -> None:
    secret = "Bearer super_secret_token_value_9f3a2c"
    raw = {"Authorization": secret, "X-Request-Id": "abc"}
    redacted = redact_headers(raw)
    assert redacted is not raw
    assert raw["Authorization"] == secret
    assert redacted["Authorization"] == REDACTED_PLACEHOLDER
    assert secret not in redacted.values()
    assert redacted["X-Request-Id"] == "abc"


def test_l3_redact_headers_replayt_signature_case_insensitive() -> None:
    mac = "sha256=" + "a" * 64
    for name in ("Replayt-Signature", "replayt-signature", "REPLAYT-SIGNATURE"):
        redacted = redact_headers({name: mac})
        assert redacted[name] == REDACTED_PLACEHOLDER
        assert "sha256=" not in redacted[name]


def test_l4_redact_headers_x_signature_prefix() -> None:
    val = "v1deadbeef"
    redacted = redact_headers({"X-Signature-Custom": val})
    assert redacted["X-Signature-Custom"] == REDACTED_PLACEHOLDER
    assert val not in redacted.values()


def test_l5_extra_sensitive_header_names() -> None:
    token = "internal-hmac-material"
    redacted = redact_headers(
        {"X-Internal-Token": token},
        extra_sensitive_names=("X-Internal-Token",),
    )
    assert redacted["X-Internal-Token"] == REDACTED_PLACEHOLDER
    assert token not in str(redacted)


def test_l6_redact_mapping_shallow_default_key() -> None:
    inner = {"token": "nested-should-stay"}
    m = {"token": "top-secret", "ok": "visible", "nested": inner}
    r = redact_mapping(m)
    assert r is not m
    assert m["token"] == "top-secret"
    assert r["token"] == REDACTED_PLACEHOLDER
    assert r["ok"] == "visible"
    assert r["nested"] is inner
    assert r["nested"]["token"] == "nested-should-stay"


def test_l7_extra_sensitive_mapping_keys() -> None:
    redacted = redact_mapping(
        {"Custom-Deploy-Secret": "xyzzy"},
        extra_sensitive_keys=("custom-deploy-secret",),
    )
    assert redacted["Custom-Deploy-Secret"] == REDACTED_PLACEHOLDER
    assert "xyzzy" not in str(redacted)


def test_l8_caplog_no_secret_in_formatted_output(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.INFO)
    secret = "fake_bearer_high_entropy_7Qk9mZp2vLx4nR8wY1tH6jF3cD0sA5bE"
    log = logging.getLogger("replayt_lifecycle_webhooks.tests.redaction_l8")
    safe = redact_headers(
        {"Authorization": f"Bearer {secret}", "Replayt-Signature": "sha256=deadbeef"},
    )
    log.info("webhook_request headers=%r", safe)
    text = caplog.text
    assert REDACTED_PLACEHOLDER in text
    assert secret not in text
    assert "deadbeef" not in text


def test_default_sensitive_header_names_documents_builtins() -> None:
    assert "Authorization" in DEFAULT_SENSITIVE_HEADER_NAMES
    assert any(x.startswith("X-Signature") for x in DEFAULT_SENSITIVE_HEADER_NAMES)


def test_default_sensitive_mapping_keys_covers_spec_minimums() -> None:
    for k in ("token", "secret", "api_key", "signature"):
        assert k in DEFAULT_SENSITIVE_MAPPING_KEYS


def test_format_safe_webhook_log_extra_redacts_headers() -> None:
    extra = format_safe_webhook_log_extra(
        method="POST",
        path="/webhook",
        status_code=401,
        error_code="signature_required",
        headers={"Authorization": "Bearer x", "X-Foo": "bar"},
    )
    assert extra["webhook_method"] == "POST"
    assert extra["webhook_path"] == "/webhook"
    assert extra["webhook_status_code"] == 401
    assert extra["webhook_error_code"] == "signature_required"
    assert extra["webhook_headers"]["Authorization"] == REDACTED_PLACEHOLDER
    assert extra["webhook_headers"]["X-Foo"] == "bar"


def test_format_safe_webhook_log_extra_uri_fallback() -> None:
    extra = format_safe_webhook_log_extra(uri="/hooks/life")
    assert extra["webhook_path"] == "/hooks/life"


def test_redact_mapping_bytes_value() -> None:
    r = redact_mapping({"token": b"binary-secret"})
    assert r["token"] == REDACTED_PLACEHOLDER
