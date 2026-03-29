"""SPEC_METRICS_HOOKS / SPEC_AUTOMATED_TESTS backlog ``42b8d5a9``: **M1**–**M7** (no network).

**M8** (package ``__all__`` / SPEC_PUBLIC_API alignment): ``tests/test_public_api.py`` (**API1**).
"""

from __future__ import annotations

import hashlib
import hmac
from http import HTTPStatus
from unittest.mock import MagicMock, patch

import pytest

from replayt_lifecycle_webhooks.handler import handle_lifecycle_webhook_post
from replayt_lifecycle_webhooks.metrics import InMemoryLifecycleWebhookMetrics
from replayt_lifecycle_webhooks.signature import (
    LIFECYCLE_WEBHOOK_SIGNATURE_HEADER,
    WebhookSignatureFormatError,
    WebhookSignatureMismatchError,
    WebhookSignatureMissingError,
    compute_lifecycle_webhook_signature_header,
    verify_lifecycle_webhook_signature,
)

_SECRET = "metrics-test-secret"
_BODY = b'{"event":"run_finished","run_id":"m1"}'


def _sign(body: bytes, secret: str | bytes = _SECRET) -> str:
    key = secret.encode("utf-8") if isinstance(secret, str) else secret
    return f"sha256={hmac.new(key, body, hashlib.sha256).hexdigest()}"


def _headers(signature: str | None) -> dict[str, str]:
    h: dict[str, str] = {}
    if signature is not None:
        h[LIFECYCLE_WEBHOOK_SIGNATURE_HEADER] = signature
    return h


def test_m1_verify_metrics_none_no_monotonic_and_no_hooks() -> None:
    """**M1:** default ``metrics=None`` does not start verify timing or call integrator hooks."""
    with patch(
        "replayt_lifecycle_webhooks.signature.time.monotonic",
        side_effect=AssertionError("monotonic must not run when metrics is None"),
    ):
        verify_lifecycle_webhook_signature(
            secret=_SECRET,
            body=_BODY,
            signature=_sign(_BODY),
            metrics=None,
        )


def test_m2_handler_metrics_none_no_monotonic_and_no_hooks() -> None:
    """**M2:** handler with ``metrics=None`` does not time handler metrics or call hooks."""
    with patch(
        "replayt_lifecycle_webhooks.handler.time.monotonic",
        side_effect=AssertionError("monotonic must not run when metrics is None"),
    ):
        handle_lifecycle_webhook_post(
            secret=_SECRET,
            method="POST",
            body=_BODY,
            headers=_headers(_sign(_BODY)),
            metrics=None,
        )
        handle_lifecycle_webhook_post(
            secret=_SECRET,
            method="POST",
            body=_BODY,
            headers=_headers(None),
            metrics=None,
        )


def test_m3_wired_verify_success_once() -> None:
    """**M3:** successful verify records ``success`` once per call."""
    m = MagicMock()
    verify_lifecycle_webhook_signature(
        secret=_SECRET, body=_BODY, signature=_sign(_BODY), metrics=m
    )
    m.record_verify_outcome.assert_called_once()
    m.record_handler_outcome.assert_not_called()
    assert m.record_verify_outcome.call_args.kwargs["outcome"] == "success"
    assert m.record_verify_outcome.call_args.kwargs["duration_sec"] >= 0.0


@pytest.mark.parametrize(
    ("exc_type", "sig_val", "expected_outcome"),
    [
        (WebhookSignatureMissingError, None, "missing_signature"),
        (WebhookSignatureFormatError, "not-hex", "format_error"),
        (WebhookSignatureMismatchError, _sign(b"other"), "mismatch"),
    ],
)
def test_m4_wired_verify_distinct_outcomes(
    exc_type: type[Exception],
    sig_val: str | None,
    expected_outcome: str,
) -> None:
    """**M4:** missing / format / mismatch map to distinct coarse outcomes."""
    m = MagicMock()
    with pytest.raises(exc_type):
        verify_lifecycle_webhook_signature(
            secret=_SECRET,
            body=_BODY,
            signature=sig_val,
            metrics=m,
        )
    m.record_verify_outcome.assert_called_once()
    assert m.record_verify_outcome.call_args.kwargs["outcome"] == expected_outcome
    assert m.record_verify_outcome.call_args.kwargs["duration_sec"] >= 0.0


def test_m5_wired_handler_4xx_error_code_in_handler_outcome() -> None:
    """**M5:** structured 4xx JSON ``error`` is passed as ``error_code`` to handler metrics."""
    m = MagicMock()
    handle_lifecycle_webhook_post(
        secret=_SECRET,
        method="POST",
        body=_BODY,
        headers=_headers(_sign(b"nope")),
        metrics=m,
    )
    m.record_verify_outcome.assert_called_once()
    m.record_handler_outcome.assert_called_once()
    assert (
        m.record_handler_outcome.call_args.kwargs["http_status"] == HTTPStatus.FORBIDDEN
    )
    assert (
        m.record_handler_outcome.call_args.kwargs["error_code"] == "signature_mismatch"
    )
    assert m.record_handler_outcome.call_args.kwargs["duration_sec"] >= 0.0


def test_m6_callback_args_no_body_secret_or_full_signature() -> None:
    """**M6:** metrics callbacks do not receive raw body text, secret, or full signature header."""
    token_body = "leak-check-body-42b8"
    secret = "leak-check-secret-42b8"
    body = f'{{"t":"{token_body}"}}'.encode()
    header = compute_lifecycle_webhook_signature_header(secret=secret, body=body)
    m = MagicMock()
    handle_lifecycle_webhook_post(
        secret=secret,
        method="POST",
        body=body,
        headers=_headers(header),
        metrics=m,
    )
    for name in ("record_verify_outcome", "record_handler_outcome"):
        meth = getattr(m, name)
        for call in meth.call_args_list:
            for v in call.kwargs.values():
                s = str(v)
                assert secret not in s
                assert token_body not in s
                assert header not in s


def test_m7_in_memory_metrics_golden_signed_post() -> None:
    """**M7:** reference recorder tallies a successful signed POST through the handler."""
    mem = InMemoryLifecycleWebhookMetrics()
    result = handle_lifecycle_webhook_post(
        secret=_SECRET,
        method="POST",
        body=_BODY,
        headers=_headers(_sign(_BODY)),
        metrics=mem,
    )
    assert result.status == HTTPStatus.NO_CONTENT
    assert mem.verify_outcomes["success"] == 1
    assert mem.handler_outcomes[(HTTPStatus.NO_CONTENT, None)] == 1
    assert (
        mem.last_verify_duration_sec is not None and mem.last_verify_duration_sec >= 0.0
    )
    assert (
        mem.last_handler_duration_sec is not None
        and mem.last_handler_duration_sec >= 0.0
    )


def test_handler_wall_duration_covers_verify_slice() -> None:
    """Handler ``duration_sec`` is at least verify-only ``duration_sec`` when both are recorded."""
    mem = InMemoryLifecycleWebhookMetrics()
    handle_lifecycle_webhook_post(
        secret=_SECRET,
        method="POST",
        body=_BODY,
        headers=_headers(_sign(_BODY)),
        metrics=mem,
    )
    assert mem.last_handler_duration_sec is not None
    assert mem.last_verify_duration_sec is not None
    assert mem.last_handler_duration_sec + 1e-9 >= mem.last_verify_duration_sec
