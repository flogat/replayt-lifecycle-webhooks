"""Property fuzz: signature verification (**PF5**, **PF8**, **PF10**).

**PF9** (optional handler fuzzing via ``handle_lifecycle_webhook_post`` / WSGI) is omitted; fuzzing stays on
``verify_lifecycle_webhook_signature`` and ``parse_lifecycle_webhook_event`` only.

**Hypothesis:** ``max_examples=50`` per property keeps local/CI runs bounded; ``deadline=None`` avoids timing flakes on
shared runners.
"""

from __future__ import annotations

import pytest

pytest.importorskip("hypothesis")

from hypothesis import given, settings
from hypothesis import strategies as st

from replayt_lifecycle_webhooks.signature import (
    WebhookSignatureFormatError,
    WebhookSignatureMismatchError,
    WebhookSignatureMissingError,
    compute_lifecycle_webhook_signature_header,
    verify_lifecycle_webhook_signature,
)

_ALLOWED_SIGNATURE_EXCEPTIONS = (
    WebhookSignatureMissingError,
    WebhookSignatureFormatError,
    WebhookSignatureMismatchError,
)

# Bounded wire-ish sizes (SPEC: tens of KiB at most).
_MAX_BODY_BYTES = 16 * 1024
_MAX_SECRET_UNIT = 256
_MAX_SIGNATURE_TEXT = 512

_secrets = st.one_of(
    st.text(max_size=_MAX_SECRET_UNIT),
    st.binary(max_size=_MAX_SECRET_UNIT),
)
_bodies = st.binary(max_size=_MAX_BODY_BYTES)
_signatures = st.one_of(st.none(), st.text(max_size=_MAX_SIGNATURE_TEXT))


@pytest.mark.property_fuzz
@settings(max_examples=50, deadline=None)
@given(secret=_secrets, body=_bodies, signature=_signatures)
def test_verify_signature_raises_only_documented_exceptions(
    secret: str | bytes,
    body: bytes,
    signature: str | None,
) -> None:
    """**PF5:** Only missing/format/mismatch errors (or success)."""
    try:
        verify_lifecycle_webhook_signature(
            secret=secret, body=body, signature=signature
        )
    except _ALLOWED_SIGNATURE_EXCEPTIONS:
        return
    except BaseException as exc:  # pragma: no cover - property failure path
        pytest.fail(f"unexpected exception: {type(exc).__name__}: {exc}")


@pytest.mark.property_fuzz
@settings(max_examples=50, deadline=None)
@given(secret=_secrets, body=_bodies)
def test_verify_accepts_computed_signature_header(
    secret: str | bytes,
    body: bytes,
) -> None:
    """**PF8:** Header from ``compute_lifecycle_webhook_signature_header`` always verifies."""
    header = compute_lifecycle_webhook_signature_header(secret=secret, body=body)
    verify_lifecycle_webhook_signature(secret=secret, body=body, signature=header)
