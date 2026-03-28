"""Tests for minimal lifecycle HTTP handler (H1–H7; no network)."""

from __future__ import annotations

import hashlib
import hmac
import io
from http import HTTPStatus
from typing import Any

from replayt_lifecycle_webhooks import (
    LIFECYCLE_WEBHOOK_SIGNATURE_HEADER,
    handle_lifecycle_webhook_post,
    make_lifecycle_webhook_wsgi_app,
)

_SECRET = "handler-test-secret"
_GOOD_BODY = b'{"event":"run_finished","run_id":"r1"}'


def _sign(body: bytes, secret: str | bytes = _SECRET) -> str:
    key = secret.encode("utf-8") if isinstance(secret, str) else secret
    mac = hmac.new(key, body, hashlib.sha256)
    return f"sha256={mac.hexdigest()}"


def _fake_headers(signature: str | None) -> dict[str, str]:
    h: dict[str, str] = {}
    if signature is not None:
        h[LIFECYCLE_WEBHOOK_SIGNATURE_HEADER] = signature
    return h


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
    assert missing.status == HTTPStatus.UNAUTHORIZED

    malformed = handle_lifecycle_webhook_post(
        secret=_SECRET,
        method="POST",
        body=_GOOD_BODY,
        headers=_fake_headers("sha256=zz"),
    )
    assert malformed.status == HTTPStatus.UNAUTHORIZED

    mismatch = handle_lifecycle_webhook_post(
        secret=_SECRET,
        method="POST",
        body=_GOOD_BODY,
        headers=_fake_headers(_sign(_GOOD_BODY, secret="other-secret")),
    )
    assert mismatch.status == HTTPStatus.FORBIDDEN


def test_h4_bad_json_400_after_good_signature() -> None:
    """H4: valid signature but invalid JSON → 400."""
    raw = b"not-json-{"
    result = handle_lifecycle_webhook_post(
        secret=_SECRET,
        method="POST",
        body=raw,
        headers=_fake_headers(_sign(raw)),
    )
    assert result.status == HTTPStatus.BAD_REQUEST


def test_h5_verify_before_json_invalid_signature_bad_json_is_401_not_400() -> None:
    """H5: invalid signature with bad JSON must not return 400 (verification first)."""
    garbage = b"{{{not-json"
    no_sig = handle_lifecycle_webhook_post(
        secret=_SECRET,
        method="POST",
        body=garbage,
        headers={},
    )
    assert no_sig.status == HTTPStatus.UNAUTHORIZED

    wrong_mac = handle_lifecycle_webhook_post(
        secret=_SECRET,
        method="POST",
        body=garbage,
        headers=_fake_headers(_sign(garbage, secret="other")),
    )
    assert wrong_mac.status == HTTPStatus.FORBIDDEN


def test_method_not_allowed_405() -> None:
    result = handle_lifecycle_webhook_post(
        secret=_SECRET,
        method="GET",
        body=_GOOD_BODY,
        headers=_fake_headers(_sign(_GOOD_BODY)),
    )
    assert result.status == HTTPStatus.METHOD_NOT_ALLOWED
    assert ("Allow", "POST") in list(result.headers)


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
    status, hdrs, _ = _call_wsgi(app, env)
    assert status.startswith("405 ")
    assert ("Allow", "POST") in hdrs
