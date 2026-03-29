"""LG1–LG4: optional serve / handler webhook diagnostics and redaction (backlog ``0bab43f3``).

Normative: ``docs/SPEC_STRUCTURED_LOGGING_REDACTION.md`` § **Optional diagnostic logging (serve and handler paths)**.
Rows **LG1**–**LG4** in ``docs/SPEC_AUTOMATED_TESTS.md`` § **Backlog `0bab43f3`**.
"""

from __future__ import annotations

import hashlib
import hmac
import io
import json
import logging
from typing import Any

import pytest

from replayt_lifecycle_webhooks.handler import (
    WEBHOOK_DIAGNOSTIC_LOGGER_NAME,
    make_lifecycle_webhook_wsgi_app,
)
from replayt_lifecycle_webhooks.redaction import REDACTED_PLACEHOLDER
from replayt_lifecycle_webhooks.serve import (
    DEFAULT_WEBHOOK_PATH,
    make_reference_lifecycle_webhook_wsgi_app,
)

_SECRET = "lg-test-hmac-secret"
_BEARER_SECRET = "fake_bearer_high_entropy_7Qk9mZp2vLx4nR8wY1tH6jF3cD0sA5bE"


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
    authorization: str | None = None,
) -> dict[str, Any]:
    env: dict[str, Any] = {
        "REQUEST_METHOD": method,
        "PATH_INFO": path,
        "CONTENT_LENGTH": str(len(body)),
        "wsgi.input": io.BytesIO(body),
    }
    if signature is not None:
        env["HTTP_REPLAYT_SIGNATURE"] = signature
    if authorization is not None:
        env["HTTP_AUTHORIZATION"] = authorization
    return env


def _diagnostic_records(caplog: pytest.LogCaptureFixture) -> list[logging.LogRecord]:
    return [r for r in caplog.records if r.name == WEBHOOK_DIAGNOSTIC_LOGGER_NAME]


def _record_extra_snapshot(rec: logging.LogRecord) -> str:
    parts: list[str] = [rec.getMessage()]
    for name in (
        "webhook_method",
        "webhook_path",
        "webhook_status_code",
        "webhook_body_bytes_len",
        "webhook_error_code",
        "lifecycle_event_id",
        "lifecycle_run_id",
        "lifecycle_workflow_id",
        "lifecycle_approval_request_id",
    ):
        if hasattr(rec, name):
            parts.append(str(getattr(rec, name)))
    if hasattr(rec, "webhook_headers"):
        parts.append(repr(rec.webhook_headers))
    return "\n".join(parts)


def test_lg1_default_off_no_new_diagnostic_records(
    caplog: pytest.LogCaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """LG1: diagnostics disabled → no INFO (or below) records on the diagnostic logger for POST/GET."""
    monkeypatch.delenv("REPLAYT_LIFECYCLE_WEBHOOK_DIAGNOSTICS", raising=False)
    caplog.set_level(logging.DEBUG)
    app = make_reference_lifecycle_webhook_wsgi_app(
        secret=_SECRET,
        webhook_diagnostics=False,
    )
    good = b'{"event_type":"replayt.lifecycle.run.started","occurred_at":"2026-01-01T00:00:00Z","event_id":"e1","correlation":{"run_id":"r1","workflow_id":"w1"},"summary":"s","detail":{"workflow_name":"n"}}'
    _call_wsgi(
        app,
        _environ(
            method="POST",
            path=DEFAULT_WEBHOOK_PATH,
            body=good,
            signature=_sign(good),
        ),
    )
    _call_wsgi(app, _environ(method="GET", path="/health"))
    assert _diagnostic_records(caplog) == []


def test_lg2_opt_in_redacts_authorization_and_signature(
    caplog: pytest.LogCaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """LG2: opt-in logs show redaction; bearer secret and signature digest do not leak."""
    monkeypatch.delenv("REPLAYT_LIFECYCLE_WEBHOOK_DIAGNOSTICS", raising=False)
    caplog.set_level(logging.INFO)
    app = make_reference_lifecycle_webhook_wsgi_app(
        secret=_SECRET,
        webhook_diagnostics=True,
    )
    good = b'{"event_type":"replayt.lifecycle.run.started","occurred_at":"2026-01-01T00:00:00Z","event_id":"e1","correlation":{"run_id":"r1","workflow_id":"w1"},"summary":"s","detail":{"workflow_name":"n"}}'
    sig = _sign(good)
    _call_wsgi(
        app,
        _environ(
            method="POST",
            path=DEFAULT_WEBHOOK_PATH,
            body=good,
            signature=sig,
            authorization=f"Bearer {_BEARER_SECRET}",
        ),
    )
    recs = _diagnostic_records(caplog)
    assert len(recs) == 1
    rec = recs[0]
    assert rec.levelno == logging.INFO
    hdrs = rec.webhook_headers
    assert hdrs["Authorization"] == REDACTED_PLACEHOLDER
    assert hdrs["Replayt-Signature"] == REDACTED_PLACEHOLDER
    blob = caplog.text + _record_extra_snapshot(rec)
    assert _BEARER_SECRET not in blob
    digest = sig.split("=", 1)[1]
    assert digest not in blob


def test_lg3_opt_in_success_path_no_raw_body_echo(
    caplog: pytest.LogCaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """LG3: 204 success logging must not contain a distinctive raw-body substring (same bar as L9)."""
    monkeypatch.delenv("REPLAYT_LIFECYCLE_WEBHOOK_DIAGNOSTICS", raising=False)
    caplog.set_level(logging.INFO)
    marker = "LG3_DISTINCTIVE_RAW_BODY_MARKER_9c4e71ab"
    body_dict = {
        "event_type": "replayt.lifecycle.run.started",
        "occurred_at": "2026-01-01T00:00:00Z",
        "event_id": "e1",
        "correlation": {"run_id": "r1", "workflow_id": "w1"},
        "summary": f"started {marker} tail",
        "detail": {"workflow_name": "n"},
    }
    raw = json.dumps(body_dict, separators=(",", ":"), ensure_ascii=True).encode(
        "utf-8"
    )
    assert marker.encode() in raw
    app = make_lifecycle_webhook_wsgi_app(secret=_SECRET, webhook_diagnostics=True)
    _call_wsgi(
        app,
        _environ(
            method="POST",
            path=DEFAULT_WEBHOOK_PATH,
            body=raw,
            signature=_sign(raw),
        ),
    )
    recs = _diagnostic_records(caplog)
    assert len(recs) == 1
    blob = caplog.text + _record_extra_snapshot(recs[0])
    assert marker not in blob


def test_webhook_diagnostics_env_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("REPLAYT_LIFECYCLE_WEBHOOK_DIAGNOSTICS", "1")
    app = make_lifecycle_webhook_wsgi_app(secret=_SECRET, webhook_diagnostics=None)
    good = b'{"event_type":"replayt.lifecycle.run.started","occurred_at":"2026-01-01T00:00:00Z","event_id":"e1","correlation":{"run_id":"r1","workflow_id":"w1"},"summary":"s","detail":{"workflow_name":"n"}}'
    records: list[logging.LogRecord] = []

    class Capture(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            records.append(record)

    log = logging.getLogger(WEBHOOK_DIAGNOSTIC_LOGGER_NAME)
    log.setLevel(logging.INFO)
    h = Capture()
    log.addHandler(h)
    try:
        _call_wsgi(
            app,
            _environ(
                method="POST",
                path=DEFAULT_WEBHOOK_PATH,
                body=good,
                signature=_sign(good),
            ),
        )
    finally:
        log.removeHandler(h)
    assert len(records) == 1


def test_webhook_diagnostics_kwarg_false_overrides_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("REPLAYT_LIFECYCLE_WEBHOOK_DIAGNOSTICS", "1")
    app = make_lifecycle_webhook_wsgi_app(secret=_SECRET, webhook_diagnostics=False)
    good = b'{"event_type":"replayt.lifecycle.run.started","occurred_at":"2026-01-01T00:00:00Z","event_id":"e1","correlation":{"run_id":"r1","workflow_id":"w1"},"summary":"s","detail":{"workflow_name":"n"}}'
    records: list[logging.LogRecord] = []

    class Capture(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            records.append(record)

    log = logging.getLogger(WEBHOOK_DIAGNOSTIC_LOGGER_NAME)
    log.setLevel(logging.INFO)
    h = Capture()
    log.addHandler(h)
    try:
        _call_wsgi(
            app,
            _environ(
                method="POST",
                path=DEFAULT_WEBHOOK_PATH,
                body=good,
                signature=_sign(good),
            ),
        )
    finally:
        log.removeHandler(h)
    assert records == []
