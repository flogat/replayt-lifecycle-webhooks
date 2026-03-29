"""HMAC-SHA256 verification for replayt-compatible lifecycle webhook bodies."""

from __future__ import annotations

import hashlib
import hmac
import time
from typing import Final

from .metrics import LifecycleWebhookMetrics

# HTTP header name for the HMAC (case-insensitive on the wire; use this spelling in docs).
LIFECYCLE_WEBHOOK_SIGNATURE_HEADER: Final[str] = "Replayt-Signature"


class WebhookSignatureError(Exception):
    """Base class for signature verification failures."""


class WebhookSignatureMissingError(WebhookSignatureError):
    """Raised when the signature header value is missing or empty."""


class WebhookSignatureFormatError(WebhookSignatureError):
    """Raised when the signature header is present but not a usable ``sha256`` hex digest."""


class WebhookSignatureMismatchError(WebhookSignatureError):
    """Raised when the MAC does not match the body and secret."""


def _secret_key(secret: str | bytes) -> bytes:
    if isinstance(secret, str):
        return secret.encode("utf-8")
    return secret


def _parse_signature_header(value: str) -> bytes:
    raw = value.strip()
    if not raw:
        raise WebhookSignatureFormatError(
            "signature header is empty after stripping whitespace"
        )
    hex_part = raw[7:].strip() if raw.lower().startswith("sha256=") else raw
    try:
        digest = bytes.fromhex(hex_part)
    except ValueError as exc:
        raise WebhookSignatureFormatError("signature is not valid hexadecimal") from exc
    if len(digest) != hashlib.sha256().digest_size:
        raise WebhookSignatureFormatError(
            f"signature digest length is {len(digest)} bytes; expected "
            f"{hashlib.sha256().digest_size} for HMAC-SHA256"
        )
    return digest


def _verify_lifecycle_webhook_signature_core(
    *,
    secret: str | bytes,
    body: bytes,
    signature: str | None,
) -> None:
    if signature is None or not signature.strip():
        raise WebhookSignatureMissingError(
            f"missing or empty {LIFECYCLE_WEBHOOK_SIGNATURE_HEADER!r} header value"
        )
    provided = _parse_signature_header(signature)
    expected = hmac.new(_secret_key(secret), body, hashlib.sha256).digest()
    if not hmac.compare_digest(expected, provided):
        raise WebhookSignatureMismatchError(
            "webhook signature does not match body and secret"
        )


def verify_lifecycle_webhook_signature(
    *,
    secret: str | bytes,
    body: bytes,
    signature: str | None,
    metrics: LifecycleWebhookMetrics | None = None,
) -> None:
    """Verify an incoming lifecycle webhook using HMAC-SHA256 over the raw body.

    Expected delivery shape (replayt-compatible automation):

    - **Body:** the raw POST bytes as read from the HTTP layer. Do not parse JSON first;
      signing uses the exact octets received.
    - **Header:** ``Replayt-Signature`` (see :data:`LIFECYCLE_WEBHOOK_SIGNATURE_HEADER`) with value
      ``sha256=<64-char lowercase or uppercase hex>``, or the bare 64-character hex digest.

    **Raises**

    - :class:`WebhookSignatureMissingError` — ``signature`` is ``None`` or blank.
    - :class:`WebhookSignatureFormatError` — value is not ``sha256`` hex of the right length.
    - :class:`WebhookSignatureMismatchError` — MAC does not match ``body`` and ``secret``.

    **Secret:** When ``secret`` is a ``str``, it is encoded as UTF-8 for the HMAC key.

    Uses :func:`hmac.compare_digest` on raw digests (constant-time for equal-length inputs).

    **Metrics:** When ``metrics`` is not ``None``, records a coarse verify outcome and verify-only
    duration (via :func:`time.monotonic`) before raising or returning. When ``metrics`` is ``None``,
    no metrics methods run and no monotonic timer is started solely for metrics.
    """
    if metrics is None:
        _verify_lifecycle_webhook_signature_core(
            secret=secret, body=body, signature=signature
        )
        return

    t0 = time.monotonic()
    try:
        _verify_lifecycle_webhook_signature_core(
            secret=secret, body=body, signature=signature
        )
    except WebhookSignatureMissingError:
        metrics.record_verify_outcome(
            outcome="missing_signature",
            duration_sec=time.monotonic() - t0,
        )
        raise
    except WebhookSignatureFormatError:
        metrics.record_verify_outcome(
            outcome="format_error",
            duration_sec=time.monotonic() - t0,
        )
        raise
    except WebhookSignatureMismatchError:
        metrics.record_verify_outcome(
            outcome="mismatch",
            duration_sec=time.monotonic() - t0,
        )
        raise
    else:
        metrics.record_verify_outcome(
            outcome="success",
            duration_sec=time.monotonic() - t0,
        )


def compute_lifecycle_webhook_signature_header(
    *, secret: str | bytes, body: bytes
) -> str:
    """Return a ``Replayt-Signature`` header value (``sha256=<hex>``) for ``body`` octets.

    Uses the same HMAC-SHA256 keying and digest as :func:`verify_lifecycle_webhook_signature`.
    Intended for local demos, tests, and compatible senders — not a substitute for upstream
    replayt delivery semantics.
    """
    digest = hmac.new(_secret_key(secret), body, hashlib.sha256).hexdigest()
    return f"sha256={digest}"
