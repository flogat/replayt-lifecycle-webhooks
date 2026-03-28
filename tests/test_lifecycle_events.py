"""Golden fixtures and validation for ``docs/EVENTS.md`` payload shapes (no network)."""

from __future__ import annotations

import hashlib
import hmac
import json
from pathlib import Path

import jsonschema
import pytest
from pydantic import ValidationError

from replayt_lifecycle_webhooks.handler import handle_lifecycle_webhook_post
from replayt_lifecycle_webhooks.signature import (
    LIFECYCLE_WEBHOOK_SIGNATURE_HEADER,
    WebhookSignatureMismatchError,
    verify_lifecycle_webhook_signature,
)
from replayt_lifecycle_webhooks.events import (
    LIFECYCLE_WEBHOOK_EVENT_TYPES,
    SUPPORTED_LIFECYCLE_WEBHOOK_SCHEMA_VERSIONS,
    parse_lifecycle_webhook_event,
)

_REPO_ROOT = Path(__file__).resolve().parents[1]
_FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures" / "events"
_LIFECYCLE_SCHEMA_PATH = _REPO_ROOT / "docs" / "schemas" / "lifecycle_webhook_payload-1-0.schema.json"
_SECRET = "fixture-verify-secret"


@pytest.mark.parametrize(
    ("filename", "expected_event_type"),
    [
        ("run_started.json", "replayt.lifecycle.run.started"),
        ("run_started_redelivery.json", "replayt.lifecycle.run.started"),
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


def test_supported_schema_versions_match_events_spec() -> None:
    assert SUPPORTED_LIFECYCLE_WEBHOOK_SCHEMA_VERSIONS == frozenset({"1.0"})


def test_parse_accepts_omitted_schema_version() -> None:
    data = json.loads((_FIXTURES_DIR / "run_started.json").read_bytes())
    del data["schema_version"]
    event = parse_lifecycle_webhook_event(data)
    assert event.schema_version is None
    assert event.event_type == "replayt.lifecycle.run.started"


@pytest.mark.parametrize(
    "bad_version",
    ["2.0", "1.0.0", "v1.0", "1"],
)
def test_parse_rejects_unsupported_schema_version(bad_version: str) -> None:
    data = json.loads((_FIXTURES_DIR / "run_started.json").read_bytes())
    data["schema_version"] = bad_version
    with pytest.raises(ValidationError):
        parse_lifecycle_webhook_event(data)


def test_informative_lifecycle_schema_is_valid_json() -> None:
    raw = _LIFECYCLE_SCHEMA_PATH.read_bytes()
    schema = json.loads(raw)
    assert schema["$schema"] == "http://json-schema.org/draft-07/schema#"


def test_event_fixtures_validate_against_informative_json_schema() -> None:
    schema = json.loads(_LIFECYCLE_SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = jsonschema.Draft7Validator(schema)
    for name in (
        "run_started.json",
        "run_started_redelivery.json",
        "run_completed.json",
        "run_failed.json",
        "approval_pending.json",
        "approval_resolved.json",
    ):
        data = json.loads((_FIXTURES_DIR / name).read_bytes())
        validator.validate(data)


def test_i3_same_logical_emission_duplicate_delivery_fixtures_match() -> None:
    """I3 / SPEC_DELIVERY_IDEMPOTENCY: same logical emission reuses event_id and body octets."""
    first = (_FIXTURES_DIR / "run_started.json").read_bytes()
    redelivery = (_FIXTURES_DIR / "run_started_redelivery.json").read_bytes()
    assert first == redelivery
    a = parse_lifecycle_webhook_event(json.loads(first))
    b = parse_lifecycle_webhook_event(json.loads(redelivery))
    assert a.event_id == b.event_id == "7b2c4f8e-0d01-4a5b-9c3d-111111111111"


@pytest.mark.parametrize(
    ("path_a", "path_b"),
    [
        ("run_started.json", "run_completed.json"),
        ("run_completed.json", "run_failed.json"),
        ("approval_pending.json", "approval_resolved.json"),
    ],
)
def test_i3_distinct_logical_emissions_distinct_event_ids(path_a: str, path_b: str) -> None:
    """I3: distinct lifecycle emissions use distinct event_id values in fixtures."""
    ea = parse_lifecycle_webhook_event(json.loads((_FIXTURES_DIR / path_a).read_bytes()))
    eb = parse_lifecycle_webhook_event(json.loads((_FIXTURES_DIR / path_b).read_bytes()))
    assert ea.event_id != eb.event_id


def test_i4_duplicate_signed_post_idempotent_side_effects_pattern() -> None:
    """I4: integrator dedupes on event_id so two identical deliveries do not double side effects."""
    raw = (_FIXTURES_DIR / "run_started.json").read_bytes()
    mac = hmac.new(_SECRET.encode("utf-8"), raw, hashlib.sha256).hexdigest()
    header = f"sha256={mac}"
    side_effects: list[str] = []
    seen_ids: set[str] = set()

    def on_success(payload: object) -> None:
        event = parse_lifecycle_webhook_event(payload)
        if event.event_id in seen_ids:
            return
        seen_ids.add(event.event_id)
        side_effects.append("processed")

    for _ in range(2):
        result = handle_lifecycle_webhook_post(
            secret=_SECRET,
            method="POST",
            body=raw,
            headers={LIFECYCLE_WEBHOOK_SIGNATURE_HEADER: header},
            on_success=on_success,
        )
        assert result.status == 204
    assert side_effects == ["processed"]
    assert seen_ids == {"7b2c4f8e-0d01-4a5b-9c3d-111111111111"}


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


def test_parse_rejects_missing_envelope_detail() -> None:
    data = json.loads((_FIXTURES_DIR / "run_started.json").read_bytes())
    del data["detail"]
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
