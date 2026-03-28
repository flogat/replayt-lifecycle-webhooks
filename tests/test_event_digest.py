"""SPEC_EVENT_DIGEST acceptance DG1–DG6 (golden digests, determinism, optional fields)."""

from __future__ import annotations

import json
import pathlib

import pytest

import replayt_lifecycle_webhooks as rlw
from replayt_lifecycle_webhooks.events import parse_lifecycle_webhook_event


def _repo_root() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parents[1]


def _canon(obj: object) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


# --- DG2: normative worked examples (SPEC_EVENT_DIGEST) ---

_RUN_COMPLETED_FIXTURE = {
    "schema_version": "1.0",
    "event_type": "replayt.lifecycle.run.completed",
    "occurred_at": "2026-03-28T14:31:12Z",
    "event_id": "8c3d5g9f-1e12-5b6c-0d4e-222222222222",
    "correlation": {
        "run_id": "run_01jqexampleabcd",
        "workflow_id": "wf_invoice_automation_v3",
        "deployment_id": "dep_staging_west",
    },
    "summary": "Run completed: Invoice automation v3 (success)",
    "detail": {
        "workflow_name": "Invoice automation v3",
        "outcome": "success",
        "duration_ms": 72000,
    },
}

_EXPECTED_RUN_COMPLETED_TEXT = """Digest: Run completed (success)
Workflow: Invoice automation v3
Run: run_01jqexampleabcd
Workflow ID: wf_invoice_automation_v3
When: 2026-03-28T14:31:12Z
Event ID: 8c3d5g9f-1e12-5b6c-0d4e-222222222222
Deployment: dep_staging_west
Duration (ms): 72000"""

_APPROVAL_RESOLVED_APPROVED_FIXTURE = {
    "schema_version": "1.0",
    "event_type": "replayt.lifecycle.approval.resolved",
    "occurred_at": "2026-03-28T15:45:22Z",
    "event_id": "1f6g8j2i-4h45-8e9f-3g7h-555555555555",
    "correlation": {
        "run_id": "run_01jqapprovaldemo",
        "workflow_id": "wf_release_train",
        "approval_request_id": "apr_01jqexamplegate",
        "deployment_id": "dep_prod_eu",
    },
    "summary": "Approval approved: Release train — production deploy step",
    "detail": {
        "step_name": "production_deploy",
        "decision": "approved",
        "resolved_by_role": "approver",
    },
}

_EXPECTED_APPROVAL_APPROVED_TEXT = """Digest: Approval approved
Step: production_deploy
Run: run_01jqapprovaldemo
Workflow ID: wf_release_train
When: 2026-03-28T15:45:22Z
Event ID: 1f6g8j2i-4h45-8e9f-3g7h-555555555555
Deployment: dep_prod_eu
Approval request: apr_01jqexamplegate
Resolved by role: approver"""

_RUN_FAILED_FIXTURE = {
    "schema_version": "1.0",
    "event_type": "replayt.lifecycle.run.failed",
    "occurred_at": "2026-03-28T14:31:05Z",
    "event_id": "9d4e6h0g-2f23-6c7d-1e5f-333333333333",
    "correlation": {
        "run_id": "run_01jqexamplefail1",
        "workflow_id": "wf_invoice_automation_v3",
        "deployment_id": "dep_staging_west",
    },
    "summary": "Run failed: Invoice automation v3 — upstream API timeout",
    "detail": {
        "workflow_name": "Invoice automation v3",
        "error_code": "STEP_FAILED",
        "error_message": "Upstream payment API did not respond within the configured timeout.",
    },
}

_EXPECTED_RUN_FAILED_TEXT = """Digest: Run failed
Workflow: Invoice automation v3
Run: run_01jqexamplefail1
Workflow ID: wf_invoice_automation_v3
When: 2026-03-28T14:31:05Z
Event ID: 9d4e6h0g-2f23-6c7d-1e5f-333333333333
Deployment: dep_staging_west
Error code: STEP_FAILED
Error: Upstream payment API did not respond within the configured timeout."""


def test_dg2_run_completed_golden_matches_spec() -> None:
    event = parse_lifecycle_webhook_event(_RUN_COMPLETED_FIXTURE)
    assert rlw.lifecycle_event_to_digest_text(event) == _EXPECTED_RUN_COMPLETED_TEXT


def test_dg2_approval_resolved_golden_matches_spec() -> None:
    event = parse_lifecycle_webhook_event(_APPROVAL_RESOLVED_APPROVED_FIXTURE)
    assert rlw.lifecycle_event_to_digest_text(event) == _EXPECTED_APPROVAL_APPROVED_TEXT


def test_worked_example_run_failed_golden_matches_spec() -> None:
    event = parse_lifecycle_webhook_event(_RUN_FAILED_FIXTURE)
    assert rlw.lifecycle_event_to_digest_text(event) == _EXPECTED_RUN_FAILED_TEXT


@pytest.mark.parametrize(
    ("fixture", "expected_first_line"),
    [
        (
            {
                "event_type": "replayt.lifecycle.run.started",
                "occurred_at": "2026-01-01T00:00:00Z",
                "event_id": "e1",
                "correlation": {"run_id": "r1", "workflow_id": "w1"},
                "summary": "s",
                "detail": {"workflow_name": "My workflow"},
            },
            "Digest: Run started",
        ),
        (
            {
                "event_type": "replayt.lifecycle.run.completed",
                "occurred_at": "2026-01-01T00:00:00Z",
                "event_id": "e2",
                "correlation": {"run_id": "r1", "workflow_id": "w1"},
                "summary": "s",
                "detail": {"workflow_name": "My workflow", "outcome": "success"},
            },
            "Digest: Run completed (success)",
        ),
        (
            {
                "event_type": "replayt.lifecycle.run.failed",
                "occurred_at": "2026-01-01T00:00:00Z",
                "event_id": "e3",
                "correlation": {"run_id": "r1", "workflow_id": "w1"},
                "summary": "s",
                "detail": {
                    "workflow_name": "My workflow",
                    "error_code": "E",
                    "error_message": "m",
                },
            },
            "Digest: Run failed",
        ),
        (
            {
                "event_type": "replayt.lifecycle.approval.pending",
                "occurred_at": "2026-01-01T00:00:00Z",
                "event_id": "e4",
                "correlation": {"run_id": "r1", "workflow_id": "w1"},
                "summary": "s",
                "detail": {"step_name": "step_a"},
            },
            "Digest: Approval requested",
        ),
        (
            {
                "event_type": "replayt.lifecycle.approval.resolved",
                "occurred_at": "2026-01-01T00:00:00Z",
                "event_id": "e5",
                "correlation": {"run_id": "r1", "workflow_id": "w1"},
                "summary": "s",
                "detail": {"step_name": "step_a", "decision": "approved"},
            },
            "Digest: Approval approved",
        ),
        (
            {
                "event_type": "replayt.lifecycle.approval.resolved",
                "occurred_at": "2026-01-01T00:00:00Z",
                "event_id": "e6",
                "correlation": {"run_id": "r1", "workflow_id": "w1"},
                "summary": "s",
                "detail": {"step_name": "step_a", "decision": "rejected"},
            },
            "Digest: Approval rejected",
        ),
    ],
)
def test_dg1_digest_first_line_covers_all_registry_types(
    fixture: dict, expected_first_line: str
) -> None:
    event = parse_lifecycle_webhook_event(fixture)
    text = rlw.lifecycle_event_to_digest_text(event)
    assert text.split("\n", 1)[0] == expected_first_line


def test_dg3_digest_text_and_record_are_deterministic() -> None:
    event = parse_lifecycle_webhook_event(_RUN_COMPLETED_FIXTURE)
    t1 = rlw.lifecycle_event_to_digest_text(event)
    t2 = rlw.lifecycle_event_to_digest_text(event)
    assert t1 == t2
    assert not t1.endswith("\n")
    r1 = rlw.lifecycle_event_to_digest_record(event)
    r2 = rlw.lifecycle_event_to_digest_record(event)
    assert r1 == r2
    assert _canon(r1) == _canon(r2)


def test_dg4_optional_lines_omitted_when_fields_absent() -> None:
    minimal_started = {
        "event_type": "replayt.lifecycle.run.started",
        "occurred_at": "2026-01-01T00:00:00Z",
        "event_id": "e",
        "correlation": {"run_id": "r", "workflow_id": "w"},
        "summary": "s",
        "detail": {"workflow_name": "wf"},
    }
    event = parse_lifecycle_webhook_event(minimal_started)
    text = rlw.lifecycle_event_to_digest_text(event)
    for fragment in ("Trigger:", "Deployment:", "Approval request:"):
        assert fragment not in text
    record = rlw.lifecycle_event_to_digest_record(event)
    assert "trigger" not in record
    assert "deployment_id" not in record
    assert "approval_request_id" not in record

    minimal_completed = {
        "event_type": "replayt.lifecycle.run.completed",
        "occurred_at": "2026-01-01T00:00:00Z",
        "event_id": "e",
        "correlation": {"run_id": "r", "workflow_id": "w"},
        "summary": "s",
        "detail": {"workflow_name": "wf", "outcome": "success"},
    }
    ev2 = parse_lifecycle_webhook_event(minimal_completed)
    assert "Duration (ms):" not in rlw.lifecycle_event_to_digest_text(ev2)
    assert "duration_ms" not in rlw.lifecycle_event_to_digest_record(ev2)

    pending = {
        "event_type": "replayt.lifecycle.approval.pending",
        "occurred_at": "2026-01-01T00:00:00Z",
        "event_id": "e",
        "correlation": {"run_id": "r", "workflow_id": "w"},
        "summary": "s",
        "detail": {"step_name": "st"},
    }
    ev3 = parse_lifecycle_webhook_event(pending)
    assert "Policy hint:" not in rlw.lifecycle_event_to_digest_text(ev3)
    assert "policy_hint" not in rlw.lifecycle_event_to_digest_record(ev3)

    resolved = {
        "event_type": "replayt.lifecycle.approval.resolved",
        "occurred_at": "2026-01-01T00:00:00Z",
        "event_id": "e",
        "correlation": {"run_id": "r", "workflow_id": "w"},
        "summary": "s",
        "detail": {"step_name": "st", "decision": "approved"},
    }
    ev4 = parse_lifecycle_webhook_event(resolved)
    assert "Resolved by role:" not in rlw.lifecycle_event_to_digest_text(ev4)
    assert "resolved_by_role" not in rlw.lifecycle_event_to_digest_record(ev4)


def test_dg5_approval_resolved_rejected_digest_line() -> None:
    fixture = {
        "event_type": "replayt.lifecycle.approval.resolved",
        "occurred_at": "2026-01-01T00:00:00Z",
        "event_id": "e",
        "correlation": {"run_id": "r", "workflow_id": "w"},
        "summary": "s",
        "detail": {"step_name": "st", "decision": "rejected"},
    }
    event = parse_lifecycle_webhook_event(fixture)
    assert rlw.lifecycle_event_to_digest_text(event).startswith(
        "Digest: Approval rejected\n"
    )


def test_dg6_integrator_docs_mention_external_sharing_caution() -> None:
    readme = (_repo_root() / "README.md").read_text(encoding="utf-8")
    events_doc = (_repo_root() / "docs" / "EVENTS.md").read_text(encoding="utf-8")
    assert "not suitable for external sharing" in readme
    assert "SPEC_EVENT_DIGEST.md" in events_doc
    assert "not suitable for external sharing" in events_doc


def test_run_completed_record_matches_expected_shape() -> None:
    event = parse_lifecycle_webhook_event(_RUN_COMPLETED_FIXTURE)
    record = rlw.lifecycle_event_to_digest_record(event)
    expected = {
        "schema_version": "digest/1",
        "event_type": "replayt.lifecycle.run.completed",
        "digest_kind": "run_completed",
        "occurred_at": "2026-03-28T14:31:12Z",
        "event_id": "8c3d5g9f-1e12-5b6c-0d4e-222222222222",
        "run_id": "run_01jqexampleabcd",
        "workflow_id": "wf_invoice_automation_v3",
        "deployment_id": "dep_staging_west",
        "workflow_name": "Invoice automation v3",
        "outcome": "success",
        "duration_ms": 72000,
    }
    assert record == expected
    golden_json = (
        '{"deployment_id":"dep_staging_west","digest_kind":"run_completed","duration_ms":72000,'
        '"event_id":"8c3d5g9f-1e12-5b6c-0d4e-222222222222",'
        '"event_type":"replayt.lifecycle.run.completed","occurred_at":"2026-03-28T14:31:12Z",'
        '"outcome":"success","run_id":"run_01jqexampleabcd","schema_version":"digest/1",'
        '"workflow_id":"wf_invoice_automation_v3","workflow_name":"Invoice automation v3"}'
    )
    assert _canon(record) == golden_json
