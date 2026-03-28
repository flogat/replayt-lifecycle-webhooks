"""Reference lifecycle webhook HTTP server (stdlib WSGI routing).

Implements ``docs/SPEC_HTTP_SERVER_ENTRYPOINT.md`` defaults: ``GET /health``, ``POST`` on a
single configurable path (default ``/webhook``), delegating webhook handling to
:func:`replayt_lifecycle_webhooks.make_lifecycle_webhook_wsgi_app`.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from http import HTTPStatus
from typing import Any

from .handler import make_lifecycle_webhook_wsgi_app

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000
DEFAULT_WEBHOOK_PATH = "/webhook"
HEALTH_PATH = "/health"

_PLAIN_UTF8 = ("Content-Type", "text/plain; charset=utf-8")


def _normalize_path(path: str) -> str:
    p = path if path else "/"
    if len(p) > 1 and p.endswith("/"):
        p = p.rstrip("/")
    return p


def make_reference_lifecycle_webhook_wsgi_app(
    secret: str | bytes,
    *,
    webhook_path: str = DEFAULT_WEBHOOK_PATH,
    on_success: Callable[[Any], None] | None = None,
) -> Callable[[Mapping[str, Any], Callable[..., Any]], list[bytes]]:
    """WSGI app: ``GET /health`` plus ``POST`` on ``webhook_path`` (default ``/webhook``).

    All other requests receive **404** with a short plain-text body. Webhook **POST** semantics
    match :func:`make_lifecycle_webhook_wsgi_app` / ``docs/SPEC_MINIMAL_HTTP_HANDLER.md``.
    """
    inner = make_lifecycle_webhook_wsgi_app(secret, on_success=on_success)
    mount = _normalize_path(webhook_path)
    if not mount.startswith("/"):
        mount = "/" + mount
    health = _normalize_path(HEALTH_PATH)

    def app(
        environ: Mapping[str, Any],
        start_response: Callable[..., Any],
    ) -> list[bytes]:
        method = str(environ.get("REQUEST_METHOD", "GET")).upper()
        path = _normalize_path(str(environ.get("PATH_INFO", "") or "/"))

        if method == "GET" and path == health:
            start_response("200 OK", [_PLAIN_UTF8])
            return [b"ok"]

        if path == mount:
            return inner(environ, start_response)

        status = HTTPStatus.NOT_FOUND
        start_response(f"{status.value} {status.phrase}", [_PLAIN_UTF8])
        return [b"not found"]

    return app
