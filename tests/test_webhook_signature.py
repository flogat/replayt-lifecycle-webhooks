"""Unit tests for lifecycle webhook HMAC verification (no network)."""

from __future__ import annotations

import hashlib
import hmac

import pytest

from replayt_lifecycle_webhooks import (
    LIFECYCLE_WEBHOOK_SIGNATURE_HEADER,
    WebhookSignatureFormatError,
    WebhookSignatureMismatchError,
    WebhookSignatureMissingError,
    verify_lifecycle_webhook_signature,
)

_SECRET = "test-webhook-secret"
_BODY = b'{"event":"run_finished","run_id":"r1"}'


def _sign(body: bytes, secret: str | bytes = _SECRET) -> str:
    mac = hmac.new(
        secret.encode("utf-8") if isinstance(secret, str) else secret,
        body,
        hashlib.sha256,
    )
    return f"sha256={mac.hexdigest()}"


def test_valid_signature_hex_prefix() -> None:
    verify_lifecycle_webhook_signature(
        secret=_SECRET,
        body=_BODY,
        signature=_sign(_BODY),
    )


def test_valid_signature_bare_hex() -> None:
    bare = _sign(_BODY).removeprefix("sha256=")
    verify_lifecycle_webhook_signature(secret=_SECRET, body=_BODY, signature=bare)


def test_wrong_secret() -> None:
    with pytest.raises(WebhookSignatureMismatchError):
        verify_lifecycle_webhook_signature(
            secret=_SECRET,
            body=_BODY,
            signature=_sign(_BODY, secret="other-secret"),
        )


def test_tampered_body() -> None:
    sig = _sign(_BODY)
    tampered = bytearray(_BODY)
    tampered[0] ^= 0x01
    with pytest.raises(WebhookSignatureMismatchError):
        verify_lifecycle_webhook_signature(
            secret=_SECRET,
            body=bytes(tampered),
            signature=sig,
        )


@pytest.mark.parametrize("signature", [None, "", "   ", "\t"])
def test_missing_or_blank_signature(signature: str | None) -> None:
    with pytest.raises(WebhookSignatureMissingError):
        verify_lifecycle_webhook_signature(secret=_SECRET, body=_BODY, signature=signature)


def test_malformed_signature_not_hex() -> None:
    with pytest.raises(WebhookSignatureFormatError):
        verify_lifecycle_webhook_signature(
            secret=_SECRET,
            body=_BODY,
            signature="sha256=not-hex",
        )


def test_malformed_signature_wrong_digest_length() -> None:
    with pytest.raises(WebhookSignatureFormatError):
        verify_lifecycle_webhook_signature(
            secret=_SECRET,
            body=_BODY,
            signature="sha256=" + "ab" * 16,  # 32 hex chars = 16 bytes, not 32
        )


def test_header_constant_documents_wire_name() -> None:
    assert LIFECYCLE_WEBHOOK_SIGNATURE_HEADER == "Replayt-Signature"
