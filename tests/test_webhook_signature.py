"""Unit tests for lifecycle webhook HMAC verification (no network)."""

from __future__ import annotations

import hashlib
import hmac
import json
from unittest.mock import patch

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


def test_valid_signature_uppercase_hex() -> None:
    """Hex digits in the header may be uppercase (spec: case-insensitive hex)."""
    verify_lifecycle_webhook_signature(
        secret=_SECRET,
        body=_BODY,
        signature=_sign(_BODY).upper(),
    )


def test_valid_signature_secret_as_bytes() -> None:
    secret_bytes = _SECRET.encode("utf-8")
    verify_lifecycle_webhook_signature(
        secret=secret_bytes,
        body=_BODY,
        signature=_sign(_BODY, secret=secret_bytes),
    )


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


def test_compare_digest_used_for_success_path() -> None:
    """MAC equality uses constant-time comparison on digest bytes (spec: cryptographic hygiene)."""
    with patch.object(hmac, "compare_digest", wraps=hmac.compare_digest) as mock_compare:
        verify_lifecycle_webhook_signature(
            secret=_SECRET,
            body=_BODY,
            signature=_sign(_BODY),
        )
    mock_compare.assert_called_once()


def test_failure_messages_do_not_contain_secret() -> None:
    secret = "unique-webhook-secret-735b2c"
    body = b'{"ok":true}'
    sig = _sign(body, secret=secret)
    failures: list[BaseException] = []
    with pytest.raises(WebhookSignatureMissingError) as missing:
        verify_lifecycle_webhook_signature(secret=secret, body=body, signature=None)
    failures.append(missing.value)
    with pytest.raises(WebhookSignatureFormatError) as bad_hex:
        verify_lifecycle_webhook_signature(secret=secret, body=body, signature="sha256=zz")
    failures.append(bad_hex.value)
    with pytest.raises(WebhookSignatureMismatchError) as mismatch:
        verify_lifecycle_webhook_signature(
            secret=secret,
            body=body,
            signature=_sign(body, secret="other-secret"),
        )
    failures.append(mismatch.value)
    tampered = bytearray(body)
    tampered[0] ^= 0x01
    with pytest.raises(WebhookSignatureMismatchError) as tampered_exc:
        verify_lifecycle_webhook_signature(secret=secret, body=bytes(tampered), signature=sig)
    failures.append(tampered_exc.value)
    needle = secret.lower()
    for err in failures:
        assert needle not in str(err).lower()


def test_mismatch_messages_do_not_echo_header_digest_hex() -> None:
    """Failure text must stay generic (spec W9: do not leak computed MAC or full header value)."""
    sig = _sign(_BODY)
    hex_from_header = sig.removeprefix("sha256=").lower()
    with pytest.raises(WebhookSignatureMismatchError) as excinfo:
        verify_lifecycle_webhook_signature(
            secret=_SECRET,
            body=_BODY,
            signature=_sign(_BODY, secret="different"),
        )
    assert hex_from_header not in str(excinfo.value).lower()

    tampered = bytearray(_BODY)
    tampered[-1] ^= 0xFF
    with pytest.raises(WebhookSignatureMismatchError) as excinfo2:
        verify_lifecycle_webhook_signature(
            secret=_SECRET,
            body=bytes(tampered),
            signature=sig,
        )
    assert hex_from_header not in str(excinfo2.value).lower()


def test_verify_before_json_single_path() -> None:
    """Integrators should verify raw bytes before parsing (spec W8: no parallel unsigned trust path)."""
    raw = _BODY
    header = _sign(raw)
    verify_lifecycle_webhook_signature(secret=_SECRET, body=raw, signature=header)
    assert json.loads(raw.decode("utf-8"))["event"] == "run_finished"

    bad = bytearray(raw)
    bad[0] ^= 0x02
    with pytest.raises(WebhookSignatureMismatchError):
        verify_lifecycle_webhook_signature(secret=_SECRET, body=bytes(bad), signature=header)
    # Tampered bytes must not be treated as authentic JSON for application logic.
    with pytest.raises(json.JSONDecodeError):
        json.loads(bytes(bad).decode("utf-8"))
