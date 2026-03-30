"""Consumer-side helpers for signed replayt lifecycle webhooks."""

from .events import (
    LIFECYCLE_WEBHOOK_EVENT_TYPES,
    SUPPORTED_LIFECYCLE_WEBHOOK_SCHEMA_VERSIONS,
    ApprovalPendingDetail,
    ApprovalPendingEvent,
    ApprovalResolvedDetail,
    ApprovalResolvedEvent,
    LifecycleCorrelation,
    LifecycleWebhookEvent,
    RunCompletedDetail,
    RunCompletedEvent,
    RunFailedDetail,
    RunFailedEvent,
    RunStartedDetail,
    RunStartedEvent,
    lifecycle_event_to_digest_record,
    lifecycle_event_to_digest_text,
    parse_lifecycle_webhook_event,
)
from .handler import (
    LifecycleWebhookHttpResult,
    handle_lifecycle_webhook_post,
    make_lifecycle_webhook_wsgi_app,
)
from .metrics import (
    InMemoryLifecycleWebhookMetrics,
    LifecycleWebhookMetrics,
    LifecycleWebhookVerifyOutcome,
    NullLifecycleWebhookMetrics,
)
from .replay_protection import (
    InMemoryLifecycleWebhookDedupStore,
    LifecycleWebhookDedupStore,
    LifecycleWebhookReplayPolicy,
    ReplayFreshnessRejected,
    ensure_occurred_at_within_replay_window,
)
from .sqlite_idempotency import SqliteLifecycleWebhookDedupStore
from .redaction import (
    DEFAULT_SENSITIVE_HEADER_NAMES,
    DEFAULT_SENSITIVE_MAPPING_KEYS,
    REDACTED_PLACEHOLDER,
    format_safe_webhook_log_extra,
    redact_headers,
    redact_mapping,
)
from .signature import (
    LIFECYCLE_WEBHOOK_SIGNATURE_HEADER,
    WebhookSignatureError,
    WebhookSignatureFormatError,
    WebhookSignatureMismatchError,
    WebhookSignatureMissingError,
    compute_lifecycle_webhook_signature_header,
    verify_lifecycle_webhook_signature,
)

# Order matches docs/SPEC_PUBLIC_API.md § Supported import paths (package root table).
__all__ = [
    "__version__",
    "LIFECYCLE_WEBHOOK_SIGNATURE_HEADER",
    "WebhookSignatureError",
    "WebhookSignatureFormatError",
    "WebhookSignatureMismatchError",
    "WebhookSignatureMissingError",
    "compute_lifecycle_webhook_signature_header",
    "verify_lifecycle_webhook_signature",
    "LifecycleWebhookVerifyOutcome",
    "LifecycleWebhookMetrics",
    "NullLifecycleWebhookMetrics",
    "InMemoryLifecycleWebhookMetrics",
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
    "LifecycleWebhookHttpResult",
    "handle_lifecycle_webhook_post",
    "make_lifecycle_webhook_wsgi_app",
    "LifecycleWebhookDedupStore",
    "InMemoryLifecycleWebhookDedupStore",
    "SqliteLifecycleWebhookDedupStore",
    "LifecycleWebhookReplayPolicy",
    "ReplayFreshnessRejected",
    "ensure_occurred_at_within_replay_window",
    "DEFAULT_SENSITIVE_HEADER_NAMES",
    "DEFAULT_SENSITIVE_MAPPING_KEYS",
    "REDACTED_PLACEHOLDER",
    "redact_headers",
    "redact_mapping",
    "format_safe_webhook_log_extra",
]

__version__ = "0.1.0"
