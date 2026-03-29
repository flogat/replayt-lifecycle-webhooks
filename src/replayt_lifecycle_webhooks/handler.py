"""Minimal HTTP POST handler for signed lifecycle webhooks (verify-before-JSON).

Status policy (see ``docs/SPEC_MINIMAL_HTTP_HANDLER.md``):

- **405** — not POST (includes ``Allow: POST`` where applicable).
- **401** — missing, empty, or malformed ``Replayt-Signature``.
- **403** — well-formed signature that does not match body and secret.
- **400** — verification passed but body is not valid UTF-8 JSON text (or wrong top-level JSON type when replay/dedupe
  hooks are enabled).
- **422** — lifecycle validation, replay window, or duplicate policy (see optional **``dedup_store``** /
  **``replay_policy``**).
- **204** — accepted (empty body); duplicate **``event_id``** when **``dedup_store``** rejects a second claim also yields **204**
  without calling **``on_success``**.

Client errors (**405**, **401**, **403**, **400**) return a JSON body per
``docs/SPEC_WEBHOOK_FAILURE_RESPONSES.md`` (**``error``** + **``message``**) and
``Content-Type: application/json; charset=utf-8``.

Uses :func:`replayt_lifecycle_webhooks.verify_lifecycle_webhook_signature` only;
no JSON parsing runs until verification succeeds.
"""

from __future__ import annotations

import json
import logging
import os
import time
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from http import HTTPStatus
from typing import Any

from pydantic import ValidationError

from .events import parse_lifecycle_webhook_event
from .metrics import LifecycleWebhookMetrics
from .redaction import format_safe_webhook_log_extra
from .replay_protection import (
    LifecycleWebhookDedupStore,
    LifecycleWebhookReplayPolicy,
    ReplayFreshnessRejected,
    ensure_occurred_at_within_replay_window,
)
from .signature import (
    LIFECYCLE_WEBHOOK_SIGNATURE_HEADER,
    WebhookSignatureFormatError,
    WebhookSignatureMismatchError,
    WebhookSignatureMissingError,
    verify_lifecycle_webhook_signature,
)

_JSON_CONTENT_TYPE = "application/json; charset=utf-8"

# Opt-in per-request diagnostics (stdlib ``logging`` only). See ``docs/SPEC_STRUCTURED_LOGGING_REDACTION.md``
# § Optional diagnostic logging (serve and handler paths).
WEBHOOK_DIAGNOSTIC_LOGGER_NAME = "replayt_lifecycle_webhooks.handler"


def _env_webhook_diagnostics_enabled() -> bool:
    v = os.environ.get("REPLAYT_LIFECYCLE_WEBHOOK_DIAGNOSTICS", "").strip().lower()
    return v in ("1", "true", "yes", "on")


def _resolve_webhook_diagnostics(explicit: bool | None) -> bool:
    if explicit is not None:
        return explicit
    return _env_webhook_diagnostics_enabled()


def _json_error_body(error: str, message: str) -> bytes:
    return json.dumps(
        {"error": error, "message": message},
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")


@dataclass(frozen=True, slots=True)
class LifecycleWebhookHttpResult:
    """HTTP-style outcome from :func:`handle_lifecycle_webhook_post`."""

    status: int
    headers: tuple[tuple[str, str], ...] = ()
    body: bytes = b""


def _error_code_from_http_result(result: LifecycleWebhookHttpResult) -> str | None:
    if result.status < 400:
        return None
    if not result.body:
        return None
    try:
        obj = json.loads(result.body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    err = obj.get("error")
    return str(err) if isinstance(err, str) else None


def _lifecycle_fields_from_verified_json_body(body: bytes) -> dict[str, str]:
    try:
        payload = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {}
    if not isinstance(payload, dict):
        return {}
    try:
        event = parse_lifecycle_webhook_event(payload)
    except ValidationError:
        return {}
    corr = event.correlation
    fields: dict[str, str] = {
        "lifecycle_event_id": event.event_id,
        "lifecycle_run_id": corr.run_id,
        "lifecycle_workflow_id": corr.workflow_id,
    }
    if corr.approval_request_id is not None:
        fields["lifecycle_approval_request_id"] = corr.approval_request_id
    return fields


def _emit_webhook_request_diagnostic(
    *,
    environ: Mapping[str, Any],
    headers: Mapping[str, str],
    raw_body_len: int,
    raw_body: bytes,
    result: LifecycleWebhookHttpResult,
) -> None:
    log = logging.getLogger(WEBHOOK_DIAGNOSTIC_LOGGER_NAME)
    path = str(environ.get("PATH_INFO", "") or "/")
    method = str(environ.get("REQUEST_METHOD", "")).upper()
    err = _error_code_from_http_result(result)
    lf: dict[str, str] = {}
    if result.status == HTTPStatus.NO_CONTENT:
        lf = _lifecycle_fields_from_verified_json_body(raw_body)
    extra = format_safe_webhook_log_extra(
        headers=headers,
        method=method,
        path=path,
        status_code=result.status,
        error_code=err,
        webhook_body_bytes_len=raw_body_len,
        lifecycle_event_id=lf.get("lifecycle_event_id"),
        lifecycle_run_id=lf.get("lifecycle_run_id"),
        lifecycle_workflow_id=lf.get("lifecycle_workflow_id"),
        lifecycle_approval_request_id=lf.get("lifecycle_approval_request_id"),
    )
    log.info("lifecycle_webhook_request", extra=extra)


def _error_result(
    status: int,
    *,
    error: str,
    message: str,
    extra_headers: tuple[tuple[str, str], ...] = (),
) -> LifecycleWebhookHttpResult:
    body = _json_error_body(error, message)
    hdrs: tuple[tuple[str, str], ...] = (
        *extra_headers,
        ("Content-Type", _JSON_CONTENT_TYPE),
    )
    return LifecycleWebhookHttpResult(status, hdrs, body)


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
    dedup_store: LifecycleWebhookDedupStore | None = None,
    replay_policy: LifecycleWebhookReplayPolicy | None = None,
    metrics: LifecycleWebhookMetrics | None = None,
) -> LifecycleWebhookHttpResult:
    """Handle one lifecycle webhook HTTP request view (POST, raw body, headers).

    **Supported method:** POST only. **Secret:** supplied by the caller (not read from the environment).

    **Order:** reject wrong method, then verify signature on raw ``body``, then UTF-8 decode and
    :func:`json.loads`. On verification failure, JSON is not parsed.

    **Replay / dedupe (optional):** When ``dedup_store`` and/or ``replay_policy`` is set, the payload must be a JSON
    object that :func:`replayt_lifecycle_webhooks.events.parse_lifecycle_webhook_event` accepts. Processing order is
    freshness on ``occurred_at`` (if enabled in ``replay_policy``), then ``dedup_store.try_claim(event_id)``. A duplicate
    ``event_id`` returns **204** without calling ``on_success``. When both are ``None``, behavior matches pre–replay-hook
    releases: any JSON value is accepted and ``on_success`` receives the parsed value.

    **Raises:** This function does not raise for client errors; it returns 4xx
    :class:`LifecycleWebhookHttpResult` values with JSON bodies (see
    ``docs/SPEC_WEBHOOK_FAILURE_RESPONSES.md``). Verification exceptions are mapped to status codes only.

    **Metrics:** When ``metrics`` is not ``None``, :func:`verify_lifecycle_webhook_signature` records verify-only timing;
    this function additionally records one handler outcome per call with wall duration from entry to return (including
    verify and JSON work). When ``metrics`` is ``None``, no metrics run and no monotonic timer is started for handler
    metrics.

    See ``docs/SPEC_MINIMAL_HTTP_HANDLER.md`` for the full normative table.
    """
    t_handler: float | None = time.monotonic() if metrics is not None else None

    def finish(result: LifecycleWebhookHttpResult) -> LifecycleWebhookHttpResult:
        if metrics is not None and t_handler is not None:
            metrics.record_handler_outcome(
                http_status=result.status,
                error_code=_error_code_from_http_result(result),
                duration_sec=time.monotonic() - t_handler,
            )
        return result

    if method.strip().upper() != "POST":
        return finish(
            _error_result(
                HTTPStatus.METHOD_NOT_ALLOWED,
                error="method_not_allowed",
                message="Only POST is supported for this endpoint.",
                extra_headers=(("Allow", "POST"),),
            )
        )

    norm = _normalize_header_map(headers)
    signature = _signature_from_normalized_headers(norm)

    try:
        verify_lifecycle_webhook_signature(
            secret=secret,
            body=body,
            signature=signature,
            metrics=metrics,
        )
    except WebhookSignatureMissingError:
        return finish(
            _error_result(
                HTTPStatus.UNAUTHORIZED,
                error="signature_required",
                message="The Replayt-Signature header is missing or empty.",
            )
        )
    except WebhookSignatureFormatError:
        return finish(
            _error_result(
                HTTPStatus.UNAUTHORIZED,
                error="signature_malformed",
                message="The signature header is not a valid v1 value.",
            )
        )
    except WebhookSignatureMismatchError:
        return finish(
            _error_result(
                HTTPStatus.FORBIDDEN,
                error="signature_mismatch",
                message="Signature does not match the request body.",
            )
        )

    try:
        text = body.decode("utf-8")
        payload = json.loads(text)
    except (UnicodeDecodeError, json.JSONDecodeError):
        return finish(
            _error_result(
                HTTPStatus.BAD_REQUEST,
                error="invalid_json",
                message="Request body is not valid UTF-8 JSON.",
            )
        )

    if dedup_store is not None or replay_policy is not None:
        if not isinstance(payload, dict):
            return finish(
                _error_result(
                    HTTPStatus.BAD_REQUEST,
                    error="invalid_payload_shape",
                    message="Valid JSON but not the expected top-level object for lifecycle events.",
                )
            )
        try:
            event = parse_lifecycle_webhook_event(payload)
        except ValidationError:
            return finish(
                _error_result(
                    HTTPStatus.UNPROCESSABLE_ENTITY,
                    error="unknown_event_type",
                    message="Event type is not supported by this integration.",
                )
            )

        if replay_policy is not None and replay_policy.check_occurred_at:
            try:
                ensure_occurred_at_within_replay_window(
                    event.occurred_at,
                    now=replay_policy.now(),
                    max_event_age_seconds=replay_policy.max_event_age_seconds,
                    max_future_skew_seconds=replay_policy.max_future_skew_seconds,
                )
            except ReplayFreshnessRejected:
                return finish(
                    _error_result(
                        HTTPStatus.UNPROCESSABLE_ENTITY,
                        error="replay_rejected",
                        message="Delivery is outside the accepted time window or was already processed.",
                    )
                )

        if dedup_store is not None:
            if not dedup_store.try_claim(event.event_id):
                return finish(LifecycleWebhookHttpResult(HTTPStatus.NO_CONTENT, (), b""))

    if on_success is not None:
        on_success(payload)

    return finish(LifecycleWebhookHttpResult(HTTPStatus.NO_CONTENT, (), b""))


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
    dedup_store: LifecycleWebhookDedupStore | None = None,
    replay_policy: LifecycleWebhookReplayPolicy | None = None,
    metrics: LifecycleWebhookMetrics | None = None,
    webhook_diagnostics: bool | None = None,
) -> Callable[[Mapping[str, Any], Callable[..., Any]], list[bytes]]:
    """Build a WSGI application that handles POST lifecycle webhooks.

    Reads the raw body from ``wsgi.input`` (honors ``CONTENT_LENGTH``), collects ``HTTP_*`` headers
    into wire names, and delegates to :func:`handle_lifecycle_webhook_post`.

    **Optional diagnostics:** When ``webhook_diagnostics`` is ``True``, or when it is ``None`` and the environment
    variable ``REPLAYT_LIFECYCLE_WEBHOOK_DIAGNOSTICS`` is truthy (``1``, ``true``, ``yes``, ``on``, case-insensitive),
    each handled request emits one **INFO** record on logger :data:`WEBHOOK_DIAGNOSTIC_LOGGER_NAME` using
    :func:`replayt_lifecycle_webhooks.redaction.format_safe_webhook_log_extra`. ``False`` disables diagnostics even
    when the environment variable is set.

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
            dedup_store=dedup_store,
            replay_policy=replay_policy,
            metrics=metrics,
        )
        if _resolve_webhook_diagnostics(webhook_diagnostics):
            _emit_webhook_request_diagnostic(
                environ=environ,
                headers=hdrs,
                raw_body_len=len(raw),
                raw_body=raw,
                result=result,
            )
        status_enum = HTTPStatus(result.status)
        status_line = f"{result.status} {status_enum.phrase}"
        start_response(status_line, list(result.headers))
        if result.body:
            return [result.body]
        return []

    return app
