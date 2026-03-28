"""Minimal HTTP POST handler for signed lifecycle webhooks (verify-before-JSON).

Status policy (see ``docs/SPEC_MINIMAL_HTTP_HANDLER.md``):

- **405** — not POST (includes ``Allow: POST`` where applicable).
- **401** — missing, empty, or malformed ``Replayt-Signature``.
- **403** — well-formed signature that does not match body and secret.
- **400** — verification passed but body is not valid UTF-8 JSON text.
- **204** — accepted (empty body).

Uses :func:`replayt_lifecycle_webhooks.verify_lifecycle_webhook_signature` only;
no JSON parsing runs until verification succeeds.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from http import HTTPStatus
from typing import Any

from .signature import (
    LIFECYCLE_WEBHOOK_SIGNATURE_HEADER,
    WebhookSignatureFormatError,
    WebhookSignatureMismatchError,
    WebhookSignatureMissingError,
    verify_lifecycle_webhook_signature,
)


@dataclass(frozen=True, slots=True)
class LifecycleWebhookHttpResult:
    """HTTP-style outcome from :func:`handle_lifecycle_webhook_post`."""

    status: int
    headers: tuple[tuple[str, str], ...] = ()
    body: bytes = b""


def _normalize_header_map(
    headers: Mapping[str, str] | Iterable[tuple[str, str]],
) -> dict[str, str]:
    out: dict[str, str] = {}
    items = headers.items() if isinstance(headers, Mapping) else headers
    for raw_key, raw_val in items:
        key = raw_key.strip().lower()
        out[key] = raw_val
    return out


def _signature_from_normalized_headers(headers_norm: Mapping[str, str]) -> str | None:
    canon = LIFECYCLE_WEBHOOK_SIGNATURE_HEADER.lower()
    if canon not in headers_norm:
        return None
    val = headers_norm[canon]
    if not val or not str(val).strip():
        return None
    return str(val)


def handle_lifecycle_webhook_post(
    *,
    secret: str | bytes,
    method: str,
    body: bytes,
    headers: Mapping[str, str] | Iterable[tuple[str, str]],
    on_success: Callable[[Any], None] | None = None,
) -> LifecycleWebhookHttpResult:
    """Handle one lifecycle webhook HTTP request view (POST, raw body, headers).

    **Supported method:** POST only. **Secret:** supplied by the caller (not read from the environment).

    **Order:** reject wrong method, then verify signature on raw ``body``, then UTF-8 decode and
    :func:`json.loads`. On verification failure, JSON is not parsed.

    **Raises:** This function does not raise for client errors; it returns 4xx
    :class:`LifecycleWebhookHttpResult` values. Verification exceptions are mapped to status codes only.

    See ``docs/SPEC_MINIMAL_HTTP_HANDLER.md`` for the full normative table.
    """
    if method.strip().upper() != "POST":
        return LifecycleWebhookHttpResult(
            HTTPStatus.METHOD_NOT_ALLOWED,
            (("Allow", "POST"),),
            b"",
        )

    norm = _normalize_header_map(headers)
    signature = _signature_from_normalized_headers(norm)

    try:
        verify_lifecycle_webhook_signature(
            secret=secret,
            body=body,
            signature=signature,
        )
    except (WebhookSignatureMissingError, WebhookSignatureFormatError):
        return LifecycleWebhookHttpResult(HTTPStatus.UNAUTHORIZED, (), b"")
    except WebhookSignatureMismatchError:
        return LifecycleWebhookHttpResult(HTTPStatus.FORBIDDEN, (), b"")

    try:
        text = body.decode("utf-8")
        payload = json.loads(text)
    except (UnicodeDecodeError, json.JSONDecodeError):
        return LifecycleWebhookHttpResult(HTTPStatus.BAD_REQUEST, (), b"")

    if on_success is not None:
        on_success(payload)

    return LifecycleWebhookHttpResult(HTTPStatus.NO_CONTENT, (), b"")


def _wsgi_header_name(env_key: str) -> str:
    """Map ``HTTP_REPLAYT_SIGNATURE``-style keys to ``Replayt-Signature``."""
    rest = env_key[5:].replace("_", "-").lower()
    return "-".join(part.capitalize() for part in rest.split("-"))


def _headers_from_wsgi_environ(environ: Mapping[str, Any]) -> dict[str, str]:
    out: dict[str, str] = {}
    for key, value in environ.items():
        if not isinstance(key, str) or not key.startswith("HTTP_"):
            continue
        if not isinstance(value, str):
            continue
        out[_wsgi_header_name(key)] = value
    return out


def make_lifecycle_webhook_wsgi_app(
    secret: str | bytes,
    *,
    on_success: Callable[[Any], None] | None = None,
) -> Callable[[Mapping[str, Any], Callable[..., Any]], list[bytes]]:
    """Build a WSGI application that handles POST lifecycle webhooks.

    Reads the raw body from ``wsgi.input`` (honors ``CONTENT_LENGTH``), collects ``HTTP_*`` headers
    into wire names, and delegates to :func:`handle_lifecycle_webhook_post`.

    **Run locally (stdlib):**

    .. code-block:: python

        from wsgiref.simple_server import make_server

        app = make_lifecycle_webhook_wsgi_app(secret="…")
        with make_server("", 8000, app) as httpd:
            httpd.serve_forever()

    """

    def app(
        environ: Mapping[str, Any],
        start_response: Callable[..., Any],
    ) -> list[bytes]:
        method = environ.get("REQUEST_METHOD", "")
        try:
            length = int(environ.get("CONTENT_LENGTH") or "0")
        except ValueError:
            length = 0
        length = max(0, length)
        stream = environ.get("wsgi.input")
        if stream is None:
            raw = b""
        else:
            raw = stream.read(length)
        hdrs = _headers_from_wsgi_environ(environ)
        result = handle_lifecycle_webhook_post(
            secret=secret,
            method=str(method),
            body=raw,
            headers=hdrs,
            on_success=on_success,
        )
        status_enum = HTTPStatus(result.status)
        status_line = f"{result.status} {status_enum.phrase}"
        start_response(status_line, list(result.headers))
        if result.body:
            return [result.body]
        return []

    return app
