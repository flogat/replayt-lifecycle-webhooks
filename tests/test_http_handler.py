"""Tests for minimal lifecycle HTTP handler (H1–H8; **H9**–**H12** in ``test_replay_protection``; no network)."""

from __future__ import annotations

import hashlib
import hmac
import io
import json
from datetime import datetime, timezone
from http import HTTPStatus
from pathlib import Path
from typing import Any

from replayt_lifecycle_webhooks.handler import (
    handle_lifecycle_webhook_post,
    make_lifecycle_webhook_wsgi_app,
)
from replayt_lifecycle_webhooks.replay_protection import LifecycleWebhookReplayPolicy
from replayt_lifecycle_webhooks.signature import LIFECYCLE_WEBHOOK_SIGNATURE_HEADER

_SECRET = "handler-test-secret"
_GOOD_BODY = b'{"event":"run_finished","run_id":"r1"}'
_EVENTS_FIXTURE = (
    Path(__file__).resolve().parent / "fixtures" / "events" / "run_started.json"
)


def _sign(body: bytes, secret: str | bytes = _SECRET) -> str:
    key = secret.encode("utf-8") if isinstance(secret, str) else secret
    mac = hmac.new(key, body, hashlib.sha256)
    return f"sha256={mac.hexdigest()}"


def _fake_headers(signature: str | None) -> dict[str, str]:
    h: dict[str, str] = {}
    if signature is not None:
        h[LIFECYCLE_WEBHOOK_SIGNATURE_HEADER] = signature
    return h


def _assert_json_error(
    result: Any,
    *,
    status: HTTPStatus,
    error: str,
    content_type: str = "application/json; charset=utf-8",
) -> None:
    assert result.status == status
    hdrs = list(result.headers)
    assert ("Content-Type", content_type) in hdrs
    data = json.loads(result.body.decode("utf-8"))
    assert data["error"] == error
    assert isinstance(data["message"], str) and data["message"]
    assert set(data.keys()) == {"error", "message"}


def _call_wsgi(
    app: Any,
    environ: dict[str, Any],
) -> tuple[str, list[tuple[str, str]], bytes]:
    status_info: list[str] = []
    headers_info: list[list[tuple[str, str]]] = []

    def start_response(status: str, headers: list[tuple[str, str]], exc_info: Any = None) -> None:
        status_info.append(status)
        headers_info.append(headers)

    chunks = list(app(environ, start_response))
    body = b"".join(chunks)
    return status_info[0], headers_info[0], body


def test_h1_fake_request_object_end_to_end() -> None:
    """H1: exercise handler with a minimal request view (method, body, headers)."""
    result = handle_lifecycle_webhook_post(
        secret=_SECRET,
        method="POST",
        body=_GOOD_BODY,
        headers=_fake_headers(_sign(_GOOD_BODY)),
    )
    assert result.status == HTTPStatus.NO_CONTENT
    assert result.body == b""


def test_h2_success_2xx() -> None:
    """H2: valid signature and valid JSON yield 2xx."""
    result = handle_lifecycle_webhook_post(
        secret=_SECRET,
        method="POST",
        body=_GOOD_BODY,
        headers=_fake_headers(_sign(_GOOD_BODY)),
    )
    assert result.status == HTTPStatus.NO_CONTENT


def test_h3_bad_signature_4xx() -> None:
    """H3: missing / malformed / mismatch map to 401 or 403 per documented policy."""
    missing = handle_lifecycle_webhook_post(
        secret=_SECRET,
        method="POST",
        body=_GOOD_BODY,
        headers={},
    )
    _assert_json_error(missing, status=HTTPStatus.UNAUTHORIZED, error="signature_required")

    malformed = handle_lifecycle_webhook_post(
        secret=_SECRET,
        method="POST",
        body=_GOOD_BODY,
        headers=_fake_headers("sha256=zz"),
    )
    _assert_json_error(malformed, status=HTTPStatus.UNAUTHORIZED, error="signature_malformed")

    mismatch = handle_lifecycle_webhook_post(
        secret=_SECRET,
        method="POST",
        body=_GOOD_BODY,
        headers=_fake_headers(_sign(_GOOD_BODY, secret="other-secret")),
    )
    _assert_json_error(mismatch, status=HTTPStatus.FORBIDDEN, error="signature_mismatch")


def test_h4_bad_json_400_after_good_signature() -> None:
    """H4: valid signature but invalid JSON → 400."""
    raw = b"not-json-{"
    result = handle_lifecycle_webhook_post(
        secret=_SECRET,
        method="POST",
        body=raw,
        headers=_fake_headers(_sign(raw)),
    )
    _assert_json_error(result, status=HTTPStatus.BAD_REQUEST, error="invalid_json")


def test_h5_verify_before_json_invalid_signature_bad_json_is_401_not_400() -> None:
    """H5: invalid signature with bad JSON must not return 400 (verification first)."""
    garbage = b"{{{not-json"
    no_sig = handle_lifecycle_webhook_post(
        secret=_SECRET,
        method="POST",
        body=garbage,
        headers={},
    )
    _assert_json_error(no_sig, status=HTTPStatus.UNAUTHORIZED, error="signature_required")

    wrong_mac = handle_lifecycle_webhook_post(
        secret=_SECRET,
        method="POST",
        body=garbage,
        headers=_fake_headers(_sign(garbage, secret="other")),
    )
    _assert_json_error(wrong_mac, status=HTTPStatus.FORBIDDEN, error="signature_mismatch")


def test_method_not_allowed_405() -> None:
    result = handle_lifecycle_webhook_post(
        secret=_SECRET,
        method="GET",
        body=_GOOD_BODY,
        headers=_fake_headers(_sign(_GOOD_BODY)),
    )
    assert result.status == HTTPStatus.METHOD_NOT_ALLOWED
    hdrs = list(result.headers)
    assert ("Allow", "POST") in hdrs
    assert ("Content-Type", "application/json; charset=utf-8") in hdrs
    data = json.loads(result.body.decode("utf-8"))
    assert data["error"] == "method_not_allowed"


def test_on_success_called_after_verify() -> None:
    seen: list[Any] = []

    def on_success(obj: Any) -> None:
        seen.append(obj)

    handle_lifecycle_webhook_post(
        secret=_SECRET,
        method="POST",
        body=_GOOD_BODY,
        headers=_fake_headers(_sign(_GOOD_BODY)),
        on_success=on_success,
    )
    assert seen == [{"event": "run_finished", "run_id": "r1"}]


def test_wsgi_path_in_process() -> None:
    """H1: WSGI harness exercises the same handler path without external sockets."""
    app = make_lifecycle_webhook_wsgi_app(secret=_SECRET)
    body = _GOOD_BODY
    env: dict[str, Any] = {
        "REQUEST_METHOD": "POST",
        "CONTENT_LENGTH": str(len(body)),
        "wsgi.input": io.BytesIO(body),
        "HTTP_REPLAYT_SIGNATURE": _sign(body),
    }
    status, _hdrs, out = _call_wsgi(app, env)
    assert status.startswith("204 ")
    assert out == b""


def test_wsgi_wrong_method_405() -> None:
    app = make_lifecycle_webhook_wsgi_app(secret=_SECRET)
    env: dict[str, Any] = {
        "REQUEST_METHOD": "PUT",
        "CONTENT_LENGTH": "0",
        "wsgi.input": io.BytesIO(b""),
    }
    status, hdrs, body = _call_wsgi(app, env)
    assert status.startswith("405 ")
    assert ("Allow", "POST") in hdrs
    assert ("Content-Type", "application/json; charset=utf-8") in hdrs
    assert json.loads(body.decode("utf-8"))["error"] == "method_not_allowed"


def test_h8_error_messages_match_failure_response_spec() -> None:
    """Stable operator-facing copy (SPEC_WEBHOOK_FAILURE_RESPONSES)."""
    expected = {
        "method_not_allowed": "Only POST is supported for this endpoint.",
        "signature_required": "The Replayt-Signature header is missing or empty.",
        "signature_malformed": "The signature header is not a valid v1 value.",
        "signature_mismatch": "Signature does not match the request body.",
        "invalid_json": "Request body is not valid UTF-8 JSON.",
        "invalid_payload_shape": (
            "Valid JSON but not the expected top-level object for lifecycle events."
        ),
        "unknown_event_type": "Event type is not supported by this integration.",
        "replay_rejected": (
            "Delivery is outside the accepted time window or was already processed."
        ),
    }
    raw = b"not-json"
    stale_event = json.loads(_EVENTS_FIXTURE.read_bytes())
    stale_event["occurred_at"] = "2020-01-01T00:00:00Z"
    stale_body = json.dumps(
        stale_event, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    cases: list[tuple[Any, str]] = [
        (
            handle_lifecycle_webhook_post(
                secret=_SECRET,
                method="GET",
                body=_GOOD_BODY,
                headers=_fake_headers(_sign(_GOOD_BODY)),
            ),
            "method_not_allowed",
        ),
        (
            handle_lifecycle_webhook_post(
                secret=_SECRET, method="POST", body=_GOOD_BODY, headers={}
            ),
            "signature_required",
        ),
        (
            handle_lifecycle_webhook_post(
                secret=_SECRET,
                method="POST",
                body=_GOOD_BODY,
                headers=_fake_headers("nope"),
            ),
            "signature_malformed",
        ),
        (
            handle_lifecycle_webhook_post(
                secret=_SECRET,
                method="POST",
                body=_GOOD_BODY,
                headers=_fake_headers(_sign(_GOOD_BODY, secret="x")),
            ),
            "signature_mismatch",
        ),
        (
            handle_lifecycle_webhook_post(
                secret=_SECRET,
                method="POST",
                body=raw,
                headers=_fake_headers(_sign(raw)),
            ),
            "invalid_json",
        ),
        (
            handle_lifecycle_webhook_post(
                secret=_SECRET,
                method="POST",
                body=b"[1]",
                headers=_fake_headers(_sign(b"[1]")),
                replay_policy=LifecycleWebhookReplayPolicy(check_occurred_at=False),
            ),
            "invalid_payload_shape",
        ),
        (
            handle_lifecycle_webhook_post(
                secret=_SECRET,
                method="POST",
                body=_GOOD_BODY,
                headers=_fake_headers(_sign(_GOOD_BODY)),
                replay_policy=LifecycleWebhookReplayPolicy(check_occurred_at=False),
            ),
            "unknown_event_type",
        ),
        (
            handle_lifecycle_webhook_post(
                secret=_SECRET,
                method="POST",
                body=stale_body,
                headers=_fake_headers(_sign(stale_body)),
                replay_policy=LifecycleWebhookReplayPolicy(
                    now=lambda: datetime(2026, 3, 28, 15, 0, 0, tzinfo=timezone.utc),
                ),
            ),
            "replay_rejected",
        ),
    ]
    for result, code in cases:
        data = json.loads(result.body.decode("utf-8"))
        assert data["message"] == expected[code]
