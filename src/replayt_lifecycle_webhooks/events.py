"""Pydantic models for lifecycle webhook JSON bodies (``docs/EVENTS.md``).

Use after :func:`replayt_lifecycle_webhooks.verify_lifecycle_webhook_signature` succeeds.

**EVENTS.md** documents payload schema **1.0**. Optional ``schema_version`` may be ``\"1.0\"`` or omitted
(equivalent to **1.0** per the spec). If ``schema_version`` is present, it must be one of
``SUPPORTED_LIFECYCLE_WEBHOOK_SCHEMA_VERSIONS`` (currently ``\"1.0\"`` only). Extend that set when **EVENTS.md**
adds a new supported wire version and matching models.
"""

from __future__ import annotations

from typing import Annotated, Any, Literal, TypeAlias, Union

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, field_validator

__all__ = [
    "SUPPORTED_LIFECYCLE_WEBHOOK_SCHEMA_VERSIONS",
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
    "lifecycle_event_to_digest_text",
    "lifecycle_event_to_digest_record",
]

SUPPORTED_LIFECYCLE_WEBHOOK_SCHEMA_VERSIONS: frozenset[str] = frozenset({"1.0"})


class _LifecycleEnvelopeBase(BaseModel):
    model_config = ConfigDict(extra="ignore")

    schema_version: str | None = None

    @field_validator("schema_version", mode="after")
    @classmethod
    def _schema_version_supported(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if v not in SUPPORTED_LIFECYCLE_WEBHOOK_SCHEMA_VERSIONS:
            allowed = ", ".join(sorted(SUPPORTED_LIFECYCLE_WEBHOOK_SCHEMA_VERSIONS))
            msg = f"unsupported lifecycle webhook schema_version {v!r}; use {allowed} or omit the field"
            raise ValueError(msg)
        return v


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


class RunStartedEvent(_LifecycleEnvelopeBase):
    event_type: Literal["replayt.lifecycle.run.started"]
    occurred_at: str
    event_id: str
    correlation: LifecycleCorrelation
    summary: str
    detail: RunStartedDetail


class RunCompletedEvent(_LifecycleEnvelopeBase):
    event_type: Literal["replayt.lifecycle.run.completed"]
    occurred_at: str
    event_id: str
    correlation: LifecycleCorrelation
    summary: str
    detail: RunCompletedDetail


class RunFailedEvent(_LifecycleEnvelopeBase):
    event_type: Literal["replayt.lifecycle.run.failed"]
    occurred_at: str
    event_id: str
    correlation: LifecycleCorrelation
    summary: str
    detail: RunFailedDetail


class ApprovalPendingEvent(_LifecycleEnvelopeBase):
    event_type: Literal["replayt.lifecycle.approval.pending"]
    occurred_at: str
    event_id: str
    correlation: LifecycleCorrelation
    summary: str
    detail: ApprovalPendingDetail


class ApprovalResolvedEvent(_LifecycleEnvelopeBase):
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


from .digest import lifecycle_event_to_digest_record, lifecycle_event_to_digest_text  # noqa: E402
