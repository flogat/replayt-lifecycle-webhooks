"""Reference HTTP server (S3, S4, S6; no public socket binding)."""

from __future__ import annotations

import hashlib
import hmac
import io
import json
from typing import Any

from replayt_lifecycle_webhooks.serve import (
    DEFAULT_WEBHOOK_PATH,
    HEALTH_PATH,
    make_reference_lifecycle_webhook_wsgi_app,
)

_SECRET = "ref-server-test-secret"
_GOOD_BODY = b'{"event":"run_finished","run_id":"r1"}'


def _sign(body: bytes, secret: str | bytes = _SECRET) -> str:
    key = secret.encode("utf-8") if isinstance(secret, str) else secret
    mac = hmac.new(key, body, hashlib.sha256)
    return f"sha256={mac.hexdigest()}"


def _call_wsgi(
    app: Any,
    environ: dict[str, Any],
) -> tuple[str, list[tuple[str, str]], bytes]:
    status_info: list[str] = []
    headers_info: list[list[tuple[str, str]]] = []

    def start_response(
        status: str, headers: list[tuple[str, str]], exc_info: Any = None
    ) -> None:
        status_info.append(status)
        headers_info.append(headers)

    chunks = list(app(environ, start_response))
    body = b"".join(chunks)
    return status_info[0], headers_info[0], body


def _environ(
    *,
    method: str,
    path: str,
    body: bytes = b"",
    signature: str | None = None,
) -> dict[str, Any]:
    env: dict[str, Any] = {
        "REQUEST_METHOD": method,
        "PATH_INFO": path,
        "CONTENT_LENGTH": str(len(body)),
        "wsgi.input": io.BytesIO(body),
    }
    if signature is not None:
        env["HTTP_REPLAYT_SIGNATURE"] = signature
    return env


def test_s3_get_health_ok_without_signature() -> None:
    """S3: GET /health is 200 with a small body; no webhook secret header required."""
    app = make_reference_lifecycle_webhook_wsgi_app(secret=_SECRET)
    status, hdrs, out = _call_wsgi(app, _environ(method="GET", path=HEALTH_PATH))
    assert status.startswith("200 ")
    assert ("Content-Type", "text/plain; charset=utf-8") in hdrs
    assert out == b"ok"


def test_s4_post_webhook_success_matches_handler() -> None:
    """S4: POST on the default webhook path matches minimal handler (204)."""
    app = make_reference_lifecycle_webhook_wsgi_app(secret=_SECRET)
    status, _hdrs, out = _call_wsgi(
        app,
        _environ(
            method="POST",
            path=DEFAULT_WEBHOOK_PATH,
            body=_GOOD_BODY,
            signature=_sign(_GOOD_BODY),
        ),
    )
    assert status.startswith("204 ")
    assert out == b""


def test_s4_post_webhook_bad_signature_json_errors() -> None:
    """S4: signature failures use the same JSON error bodies as the handler."""
    app = make_reference_lifecycle_webhook_wsgi_app(secret=_SECRET)
    status, hdrs, body = _call_wsgi(
        app,
        _environ(method="POST", path=DEFAULT_WEBHOOK_PATH, body=_GOOD_BODY),
    )
    assert status.startswith("401 ")
    assert ("Content-Type", "application/json; charset=utf-8") in hdrs
    assert json.loads(body.decode("utf-8"))["error"] == "signature_required"


def test_s4_post_webhook_verify_before_json() -> None:
    """S4: invalid MAC with garbage body stays 401/403, not 400."""
    app = make_reference_lifecycle_webhook_wsgi_app(secret=_SECRET)
    garbage = b"{{{"
    status, hdrs, body = _call_wsgi(
        app,
        _environ(
            method="POST",
            path=DEFAULT_WEBHOOK_PATH,
            body=garbage,
            signature=_sign(garbage, secret="other-secret"),
        ),
    )
    assert status.startswith("403 ")
    assert ("Content-Type", "application/json; charset=utf-8") in hdrs
    assert json.loads(body.decode("utf-8"))["error"] == "signature_mismatch"


def test_s4_post_webhook_wrong_method_405() -> None:
    """S4: non-POST on the webhook path is rejected by the inner handler with Allow: POST."""
    app = make_reference_lifecycle_webhook_wsgi_app(secret=_SECRET)
    status, hdrs, body = _call_wsgi(
        app,
        _environ(method="PUT", path=DEFAULT_WEBHOOK_PATH, body=b""),
    )
    assert status.startswith("405 ")
    assert ("Allow", "POST") in hdrs
    assert json.loads(body.decode("utf-8"))["error"] == "method_not_allowed"


def test_s4_unknown_path_404() -> None:
    """Wrong path for POST is not handled as a webhook."""
    app = make_reference_lifecycle_webhook_wsgi_app(secret=_SECRET)
    status, _hdrs, out = _call_wsgi(
        app,
        _environ(
            method="POST",
            path="/nope",
            body=_GOOD_BODY,
            signature=_sign(_GOOD_BODY),
        ),
    )
    assert status.startswith("404 ")
    assert out == b"not found"


def test_s6_in_process_wsgi_only() -> None:
    """S6: full reference routes exercised via WSGI callables (no sockets)."""
    app = make_reference_lifecycle_webhook_wsgi_app(
        secret=_SECRET,
        webhook_path="/custom-hook",
    )
    st_h, _, b_h = _call_wsgi(app, _environ(method="GET", path=HEALTH_PATH))
    assert st_h.startswith("200 ")
    st_w, _, b_w = _call_wsgi(
        app,
        _environ(
            method="POST",
            path="/custom-hook",
            body=_GOOD_BODY,
            signature=_sign(_GOOD_BODY),
        ),
    )
    assert st_w.startswith("204 ")
    assert b_w == b""


def test_s4_custom_header_name_replayt_signature() -> None:
    """WSGI header mapping still supplies Replayt-Signature for the inner app."""
    app = make_reference_lifecycle_webhook_wsgi_app(secret=_SECRET)
    body = _GOOD_BODY
    env = _environ(method="POST", path=DEFAULT_WEBHOOK_PATH, body=body)
    env["HTTP_REPLAYT_SIGNATURE"] = _sign(body)
    status, _, out = _call_wsgi(app, env)
    assert status.startswith("204 ")
    assert out == b""
