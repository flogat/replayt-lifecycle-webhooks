"""Golden fixtures and validation for ``docs/EVENTS.md`` payload shapes (no network)."""

from __future__ import annotations

import hashlib
import hmac
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from replayt_lifecycle_webhooks import (
    LIFECYCLE_WEBHOOK_SIGNATURE_HEADER,
    WebhookSignatureMismatchError,
    handle_lifecycle_webhook_post,
    verify_lifecycle_webhook_signature,
)
from replayt_lifecycle_webhooks.events import (
    LIFECYCLE_WEBHOOK_EVENT_TYPES,
    parse_lifecycle_webhook_event,
)

_FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures" / "events"
_SECRET = "fixture-verify-secret"


@pytest.mark.parametrize(
    ("filename", "expected_event_type"),
    [
        ("run_started.json", "replayt.lifecycle.run.started"),
        ("run_completed.json", "replayt.lifecycle.run.completed"),
        ("run_failed.json", "replayt.lifecycle.run.failed"),
        ("approval_pending.json", "replayt.lifecycle.approval.pending"),
        ("approval_resolved.json", "replayt.lifecycle.approval.resolved"),
    ],
)
def test_golden_fixture_parses(filename: str, expected_event_type: str) -> None:
    raw = (_FIXTURES_DIR / filename).read_bytes()
    data = json.loads(raw)
    event = parse_lifecycle_webhook_event(data)
    assert event.event_type == expected_event_type
    assert event.schema_version == "1.0"
    assert event.event_id
    assert event.occurred_at
    assert event.summary
    assert event.correlation.run_id
    assert event.correlation.workflow_id


def test_run_started_fixture_detail_and_correlation() -> None:
    data = json.loads((_FIXTURES_DIR / "run_started.json").read_bytes())
    event = parse_lifecycle_webhook_event(data)
    assert event.event_type == "replayt.lifecycle.run.started"
    assert event.detail.workflow_name == "Invoice automation v3"
    assert event.detail.trigger == "schedule"
    assert event.correlation.deployment_id == "dep_staging_west"
    assert event.correlation.approval_request_id is None


def test_run_completed_outcome_and_duration() -> None:
    data = json.loads((_FIXTURES_DIR / "run_completed.json").read_bytes())
    event = parse_lifecycle_webhook_event(data)
    assert event.event_type == "replayt.lifecycle.run.completed"
    assert event.detail.outcome == "success"
    assert event.detail.duration_ms == 72000


def test_run_failed_error_fields() -> None:
    data = json.loads((_FIXTURES_DIR / "run_failed.json").read_bytes())
    event = parse_lifecycle_webhook_event(data)
    assert event.event_type == "replayt.lifecycle.run.failed"
    assert event.detail.error_code == "STEP_FAILED"
    assert "timeout" in event.detail.error_message.lower()


def test_approval_fixtures_share_approval_request_id() -> None:
    pending = parse_lifecycle_webhook_event(
        json.loads((_FIXTURES_DIR / "approval_pending.json").read_bytes()),
    )
    resolved = parse_lifecycle_webhook_event(
        json.loads((_FIXTURES_DIR / "approval_resolved.json").read_bytes()),
    )
    assert pending.event_type == "replayt.lifecycle.approval.pending"
    assert resolved.event_type == "replayt.lifecycle.approval.resolved"
    assert pending.correlation.approval_request_id == "apr_01jqexamplegate"
    assert resolved.correlation.approval_request_id == pending.correlation.approval_request_id
    assert pending.detail.step_name == resolved.detail.step_name == "production_deploy"
    assert resolved.detail.decision == "approved"
    assert resolved.detail.resolved_by_role == "approver"


def test_registry_matches_documented_event_types() -> None:
    assert LIFECYCLE_WEBHOOK_EVENT_TYPES == (
        "replayt.lifecycle.run.started",
        "replayt.lifecycle.run.completed",
        "replayt.lifecycle.run.failed",
        "replayt.lifecycle.approval.pending",
        "replayt.lifecycle.approval.resolved",
    )


def test_parse_rejects_non_object() -> None:
    with pytest.raises(TypeError, match="JSON object"):
        parse_lifecycle_webhook_event([])


def test_parse_rejects_wrong_detail_for_event_type() -> None:
    data = json.loads((_FIXTURES_DIR / "run_started.json").read_bytes())
    data["event_type"] = "replayt.lifecycle.run.completed"
    with pytest.raises(ValidationError):
        parse_lifecycle_webhook_event(data)


def test_parse_rejects_missing_correlation_field() -> None:
    data = json.loads((_FIXTURES_DIR / "run_started.json").read_bytes())
    del data["correlation"]["run_id"]
    with pytest.raises(ValidationError):
        parse_lifecycle_webhook_event(data)


def test_parse_rejects_unknown_event_type() -> None:
    data = json.loads((_FIXTURES_DIR / "run_started.json").read_bytes())
    data["event_type"] = "replayt.lifecycle.run.unknown"
    with pytest.raises(ValidationError):
        parse_lifecycle_webhook_event(data)


def test_verify_then_parse_fixture_body_ordering() -> None:
    """E2 / E5: signature on raw bytes; JSON interpretation only after verify."""
    raw = (_FIXTURES_DIR / "run_started.json").read_bytes()
    mac = hmac.new(_SECRET.encode("utf-8"), raw, hashlib.sha256).hexdigest()
    header = f"sha256={mac}"
    seen: list[object] = []

    def on_success(payload: object) -> None:
        seen.append(parse_lifecycle_webhook_event(payload))

    result = handle_lifecycle_webhook_post(
        secret=_SECRET,
        method="POST",
        body=raw,
        headers={LIFECYCLE_WEBHOOK_SIGNATURE_HEADER: header},
        on_success=on_success,
    )
    assert result.status == 204
    assert len(seen) == 1
    assert seen[0].event_type == "replayt.lifecycle.run.started"


def test_verify_rejects_body_before_json_applies() -> None:
    raw = (_FIXTURES_DIR / "run_started.json").read_bytes()
    bad_sig = "sha256=" + "0" * 64
    with pytest.raises(WebhookSignatureMismatchError):
        verify_lifecycle_webhook_signature(
            secret=_SECRET,
            body=raw,
            signature=bad_sig,
        )
