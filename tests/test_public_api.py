"""SPEC_PUBLIC_API: package root and events ``__all__``, internal modules, deprecation doc anchors (no network)."""

from __future__ import annotations

import importlib
import pathlib

import pytest

import replayt_lifecycle_webhooks as rlw
from replayt_lifecycle_webhooks import events

# Canonical order: docs/SPEC_PUBLIC_API.md § Supported import paths (package root table). Keep in sync when the spec changes.
_PACKAGE_ROOT_EXPORT_ORDER: tuple[str, ...] = (
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
)
_EXPECTED_PACKAGE_ROOT_EXPORTS: frozenset[str] = frozenset(_PACKAGE_ROOT_EXPORT_ORDER)

# Order matches src/replayt_lifecycle_webhooks/events.py and SPEC_PUBLIC_API Events / parsing row.
_EVENTS_EXPORT_ORDER: tuple[str, ...] = (
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
)
_EXPECTED_EVENTS_EXPORTS: frozenset[str] = frozenset(_EVENTS_EXPORT_ORDER)


def _repo_root() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parents[1]


def _read_spec_public_api() -> str:
    return (_repo_root() / "docs" / "SPEC_PUBLIC_API.md").read_text(encoding="utf-8")


@pytest.mark.parametrize("name", list(rlw.__all__))
def test_package_root___all___names_are_importable(name: str) -> None:
    getattr(rlw, name)


def test_package_root___all___matches_spec_table() -> None:
    assert list(rlw.__all__) == list(_PACKAGE_ROOT_EXPORT_ORDER)
    assert frozenset(rlw.__all__) == _EXPECTED_PACKAGE_ROOT_EXPORTS
    assert len(rlw.__all__) == len(_EXPECTED_PACKAGE_ROOT_EXPORTS)


def test_events___all___matches_spec_events_row() -> None:
    assert list(events.__all__) == list(_EVENTS_EXPORT_ORDER)
    assert frozenset(events.__all__) == _EXPECTED_EVENTS_EXPORTS
    assert _EXPECTED_EVENTS_EXPORTS <= _EXPECTED_PACKAGE_ROOT_EXPORTS
    assert len(events.__all__) == len(_EXPECTED_EVENTS_EXPORTS)


def test_spec_lists_documented_internal_modules_as_importable() -> None:
    """SPEC_PUBLIC_API § Unsupported imports: paths exist for maintainers; integrators should use the package root."""
    internal = (
        "replayt_lifecycle_webhooks.signature",
        "replayt_lifecycle_webhooks.digest",
        "replayt_lifecycle_webhooks.handler",
        "replayt_lifecycle_webhooks.replay_protection",
        "replayt_lifecycle_webhooks.sqlite_idempotency",
        "replayt_lifecycle_webhooks.redaction",
        "replayt_lifecycle_webhooks.metrics",
        "replayt_lifecycle_webhooks.serve",
        "replayt_lifecycle_webhooks.demo_webhook",
        "replayt_lifecycle_webhooks.__main__",
    )
    for mod in internal:
        importlib.import_module(mod)


def test_spec_public_api_deprecation_policy_mentions_changelog_and_notice() -> None:
    text = _read_spec_public_api()
    assert "## Deprecation policy" in text
    dep = text.split("## Deprecation policy", 1)[1].split("## Pre-1.0 stability", 1)[0]
    assert "CHANGELOG" in dep
    assert "Deprecated" in dep
    assert "minor" in dep
    assert "0.x" in dep
