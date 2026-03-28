"""PM/support digest formatters (``docs/SPEC_EVENT_DIGEST.md``).

Call only after verification and :func:`replayt_lifecycle_webhooks.parse_lifecycle_webhook_event`.
"""

from __future__ import annotations

from typing import Any

from .events import (
    ApprovalPendingEvent,
    ApprovalResolvedEvent,
    LifecycleWebhookEvent,
    RunCompletedEvent,
    RunFailedEvent,
    RunStartedEvent,
)

__all__ = ["lifecycle_event_to_digest_record", "lifecycle_event_to_digest_text"]


def _correlation_lines(event: RunStartedEvent | RunCompletedEvent | RunFailedEvent | ApprovalPendingEvent | ApprovalResolvedEvent) -> list[str]:
    c = event.correlation
    lines = [
        f"Run: {c.run_id}",
        f"Workflow ID: {c.workflow_id}",
        f"When: {event.occurred_at}",
        f"Event ID: {event.event_id}",
    ]
    if c.deployment_id is not None:
        lines.append(f"Deployment: {c.deployment_id}")
    if c.approval_request_id is not None:
        lines.append(f"Approval request: {c.approval_request_id}")
    return lines


def lifecycle_event_to_digest_text(
    event: LifecycleWebhookEvent,
) -> str:
    """Return deterministic digest text for a parsed lifecycle event (SPEC_EVENT_DIGEST)."""
    lines: list[str]
    if isinstance(event, RunStartedEvent):
        lines = ["Digest: Run started", f"Workflow: {event.detail.workflow_name}", *_correlation_lines(event)]
        if event.detail.trigger is not None:
            lines.append(f"Trigger: {event.detail.trigger}")
    elif isinstance(event, RunCompletedEvent):
        lines = ["Digest: Run completed (success)", f"Workflow: {event.detail.workflow_name}", *_correlation_lines(event)]
        if event.detail.duration_ms is not None:
            lines.append(f"Duration (ms): {event.detail.duration_ms}")
    elif isinstance(event, RunFailedEvent):
        lines = [
            "Digest: Run failed",
            f"Workflow: {event.detail.workflow_name}",
            *_correlation_lines(event),
            f"Error code: {event.detail.error_code}",
            f"Error: {event.detail.error_message}",
        ]
    elif isinstance(event, ApprovalPendingEvent):
        lines = ["Digest: Approval requested", f"Step: {event.detail.step_name}", *_correlation_lines(event)]
        if event.detail.policy_hint is not None:
            lines.append(f"Policy hint: {event.detail.policy_hint}")
    elif isinstance(event, ApprovalResolvedEvent):
        head = "Digest: Approval approved" if event.detail.decision == "approved" else "Digest: Approval rejected"
        lines = [head, f"Step: {event.detail.step_name}", *_correlation_lines(event)]
        if event.detail.resolved_by_role is not None:
            lines.append(f"Resolved by role: {event.detail.resolved_by_role}")
    else:
        msg = f"unsupported lifecycle event type: {type(event).__name__}"
        raise TypeError(msg)
    return "\n".join(lines)


def _digest_kind(
    event: RunStartedEvent | RunCompletedEvent | RunFailedEvent | ApprovalPendingEvent | ApprovalResolvedEvent,
) -> str:
    if isinstance(event, RunStartedEvent):
        return "run_started"
    if isinstance(event, RunCompletedEvent):
        return "run_completed"
    if isinstance(event, RunFailedEvent):
        return "run_failed"
    if isinstance(event, ApprovalPendingEvent):
        return "approval_pending"
    if isinstance(event, ApprovalResolvedEvent):
        return "approval_resolved"
    msg = f"unsupported lifecycle event type: {type(event).__name__}"
    raise TypeError(msg)


def lifecycle_event_to_digest_record(event: LifecycleWebhookEvent) -> dict[str, Any]:
    """Return the ``digest/1`` JSON record for a parsed lifecycle event (SPEC_EVENT_DIGEST)."""
    if not isinstance(
        event,
        (RunStartedEvent, RunCompletedEvent, RunFailedEvent, ApprovalPendingEvent, ApprovalResolvedEvent),
    ):
        msg = f"unsupported lifecycle event type: {type(event).__name__}"
        raise TypeError(msg)

    c = event.correlation
    record: dict[str, Any] = {
        "schema_version": "digest/1",
        "event_type": event.event_type,
        "digest_kind": _digest_kind(event),
        "occurred_at": event.occurred_at,
        "event_id": event.event_id,
        "run_id": c.run_id,
        "workflow_id": c.workflow_id,
    }
    if c.deployment_id is not None:
        record["deployment_id"] = c.deployment_id
    if c.approval_request_id is not None:
        record["approval_request_id"] = c.approval_request_id

    if isinstance(event, RunStartedEvent):
        record["workflow_name"] = event.detail.workflow_name
        if event.detail.trigger is not None:
            record["trigger"] = event.detail.trigger
    elif isinstance(event, RunCompletedEvent):
        record["workflow_name"] = event.detail.workflow_name
        record["outcome"] = "success"
        if event.detail.duration_ms is not None:
            record["duration_ms"] = event.detail.duration_ms
    elif isinstance(event, RunFailedEvent):
        record["workflow_name"] = event.detail.workflow_name
        record["error_code"] = event.detail.error_code
        record["error_message"] = event.detail.error_message
    elif isinstance(event, ApprovalPendingEvent):
        record["step_name"] = event.detail.step_name
        if event.detail.policy_hint is not None:
            record["policy_hint"] = event.detail.policy_hint
    elif isinstance(event, ApprovalResolvedEvent):
        record["step_name"] = event.detail.step_name
        record["decision"] = event.detail.decision
        if event.detail.resolved_by_role is not None:
            record["resolved_by_role"] = event.detail.resolved_by_role

    return record
