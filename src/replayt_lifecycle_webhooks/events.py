"""Pydantic models for lifecycle webhook JSON bodies (``docs/EVENTS.md``).

Use after :func:`replayt_lifecycle_webhooks.verify_lifecycle_webhook_signature` succeeds.

**EVENTS.md** documents payload schema **1.0**. Optional ``schema_version`` may be ``\"1.0\"`` or omitted
(equivalent to **1.0** per the spec). The field is not checked against an allowlist; treat unexpected
values in application code until **EVENTS.md** defines more versions.
"""

from __future__ import annotations

from typing import Annotated, Any, Literal, TypeAlias, Union

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter

__all__ = [
    "LIFECYCLE_WEBHOOK_EVENT_TYPES",
    "LifecycleCorrelation",
    "LifecycleWebhookEvent",
    "ApprovalPendingDetail",
    "ApprovalPendingEvent",
    "ApprovalResolvedDetail",
    "ApprovalResolvedEvent",
    "RunCompletedDetail",
    "RunCompletedEvent",
    "RunFailedDetail",
    "RunFailedEvent",
    "RunStartedDetail",
    "RunStartedEvent",
    "parse_lifecycle_webhook_event",
]


class LifecycleCorrelation(BaseModel):
    """Opaque ids for dashboards and routing (``EVENTS.md`` correlation object)."""

    model_config = ConfigDict(extra="ignore")

    run_id: str
    workflow_id: str
    approval_request_id: str | None = None
    deployment_id: str | None = None


class RunStartedDetail(BaseModel):
    model_config = ConfigDict(extra="ignore")

    workflow_name: str
    trigger: str | None = None


class RunCompletedDetail(BaseModel):
    model_config = ConfigDict(extra="ignore")

    workflow_name: str
    outcome: Literal["success"]
    duration_ms: int | None = None


class RunFailedDetail(BaseModel):
    model_config = ConfigDict(extra="ignore")

    workflow_name: str
    error_code: str
    error_message: str


class ApprovalPendingDetail(BaseModel):
    model_config = ConfigDict(extra="ignore")

    step_name: str
    policy_hint: str | None = None


class ApprovalResolvedDetail(BaseModel):
    model_config = ConfigDict(extra="ignore")

    step_name: str
    decision: Literal["approved", "rejected"]
    resolved_by_role: str | None = None


class RunStartedEvent(BaseModel):
    model_config = ConfigDict(extra="ignore")

    schema_version: str | None = None
    event_type: Literal["replayt.lifecycle.run.started"]
    occurred_at: str
    event_id: str
    correlation: LifecycleCorrelation
    summary: str
    detail: RunStartedDetail


class RunCompletedEvent(BaseModel):
    model_config = ConfigDict(extra="ignore")

    schema_version: str | None = None
    event_type: Literal["replayt.lifecycle.run.completed"]
    occurred_at: str
    event_id: str
    correlation: LifecycleCorrelation
    summary: str
    detail: RunCompletedDetail


class RunFailedEvent(BaseModel):
    model_config = ConfigDict(extra="ignore")

    schema_version: str | None = None
    event_type: Literal["replayt.lifecycle.run.failed"]
    occurred_at: str
    event_id: str
    correlation: LifecycleCorrelation
    summary: str
    detail: RunFailedDetail


class ApprovalPendingEvent(BaseModel):
    model_config = ConfigDict(extra="ignore")

    schema_version: str | None = None
    event_type: Literal["replayt.lifecycle.approval.pending"]
    occurred_at: str
    event_id: str
    correlation: LifecycleCorrelation
    summary: str
    detail: ApprovalPendingDetail


class ApprovalResolvedEvent(BaseModel):
    model_config = ConfigDict(extra="ignore")

    schema_version: str | None = None
    event_type: Literal["replayt.lifecycle.approval.resolved"]
    occurred_at: str
    event_id: str
    correlation: LifecycleCorrelation
    summary: str
    detail: ApprovalResolvedDetail


LifecycleWebhookEvent: TypeAlias = Annotated[
    Union[
        RunStartedEvent,
        RunCompletedEvent,
        RunFailedEvent,
        ApprovalPendingEvent,
        ApprovalResolvedEvent,
    ],
    Field(discriminator="event_type"),
]

_LIFECYCLE_EVENT_ADAPTER = TypeAdapter(LifecycleWebhookEvent)

LIFECYCLE_WEBHOOK_EVENT_TYPES: tuple[str, ...] = (
    "replayt.lifecycle.run.started",
    "replayt.lifecycle.run.completed",
    "replayt.lifecycle.run.failed",
    "replayt.lifecycle.approval.pending",
    "replayt.lifecycle.approval.resolved",
)


def parse_lifecycle_webhook_event(data: Any) -> RunStartedEvent | RunCompletedEvent | RunFailedEvent | ApprovalPendingEvent | ApprovalResolvedEvent:
    """Validate a mapping (e.g. from ``json.loads``) against ``docs/EVENTS.md``.

    Raises:
        pydantic.ValidationError: payload is not a supported lifecycle object.
        TypeError: ``data`` is not a ``dict`` (JSON object).
    """
    if not isinstance(data, dict):
        msg = f"lifecycle webhook payload must be a JSON object, got {type(data).__name__}"
        raise TypeError(msg)
    return _LIFECYCLE_EVENT_ADAPTER.validate_python(data)
