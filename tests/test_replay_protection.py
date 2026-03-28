"""Replay window and dedupe store (SPEC_REPLAY_PROTECTION **RP4** / **RP5**; no network)."""

from __future__ import annotations

import hashlib
import hmac
import json
from datetime import datetime, timezone
from http import HTTPStatus
from pathlib import Path

import pytest

from replayt_lifecycle_webhooks.handler import handle_lifecycle_webhook_post
from replayt_lifecycle_webhooks.replay_protection import (
    InMemoryLifecycleWebhookDedupStore,
    LifecycleWebhookReplayPolicy,
    ReplayFreshnessRejected,
    ensure_occurred_at_within_replay_window,
)
from replayt_lifecycle_webhooks.signature import LIFECYCLE_WEBHOOK_SIGNATURE_HEADER

_FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures" / "events"
_SECRET = "replay-test-secret"


def _sign(body: bytes) -> str:
    mac = hmac.new(_SECRET.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return f"sha256={mac}"


def test_ensure_occurred_at_accepts_fixture_instant_relative_to_now() -> None:
    data = json.loads((_FIXTURES_DIR / "run_started.json").read_bytes())
    now = datetime(2026, 3, 28, 14, 35, 0, tzinfo=timezone.utc)
    ensure_occurred_at_within_replay_window(
        data["occurred_at"],
        now=now,
        max_event_age_seconds=900.0,
        max_future_skew_seconds=300.0,
    )


def test_ensure_occurred_at_rejects_stale() -> None:
    now = datetime(2026, 3, 28, 15, 0, 0, tzinfo=timezone.utc)
    with pytest.raises(ReplayFreshnessRejected):
        ensure_occurred_at_within_replay_window(
            "2020-01-01T00:00:00Z",
            now=now,
            max_event_age_seconds=900.0,
            max_future_skew_seconds=300.0,
        )


def test_ensure_occurred_at_rejects_too_far_future() -> None:
    now = datetime(2026, 3, 28, 15, 0, 0, tzinfo=timezone.utc)
    with pytest.raises(ReplayFreshnessRejected):
        ensure_occurred_at_within_replay_window(
            "2030-01-01T00:00:00Z",
            now=now,
            max_event_age_seconds=900.0,
            max_future_skew_seconds=300.0,
        )


def test_ensure_occurred_at_rejects_unparseable_instant() -> None:
    now = datetime(2026, 3, 28, 15, 0, 0, tzinfo=timezone.utc)
    with pytest.raises(ReplayFreshnessRejected):
        ensure_occurred_at_within_replay_window(
            "not-a-valid-rfc3339-instant",
            now=now,
            max_event_age_seconds=900.0,
            max_future_skew_seconds=300.0,
        )


def test_rp4b_malformed_occurred_at_replay_rejected_not_uncaught() -> None:
    """Invalid **``occurred_at``** must not escape as **``ValueError``** when freshness checks run."""
    data = json.loads((_FIXTURES_DIR / "run_started.json").read_bytes())
    data["occurred_at"] = "not-a-valid-rfc3339-instant"
    raw = json.dumps(data, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    header = _sign(raw)
    result = handle_lifecycle_webhook_post(
        secret=_SECRET,
        method="POST",
        body=raw,
        headers={LIFECYCLE_WEBHOOK_SIGNATURE_HEADER: header},
        replay_policy=LifecycleWebhookReplayPolicy(),
    )
    assert result.status == HTTPStatus.UNPROCESSABLE_ENTITY
    err = json.loads(result.body.decode("utf-8"))
    assert err["error"] == "replay_rejected"


def test_in_memory_dedup_store_ttl_allows_reclaim_after_expiry() -> None:
    t0 = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    clock: list[datetime] = [t0]
    store = InMemoryLifecycleWebhookDedupStore(
        ttl_seconds=60.0,
        now=lambda: clock[0],
    )
    assert store.try_claim("evt-1") is True
    assert store.try_claim("evt-1") is False
    clock[0] = t0.replace(minute=5)
    assert store.try_claim("evt-1") is True


def test_rp4_stale_occurred_at_valid_mac_replay_rejected_no_on_success() -> None:
    """**RP4:** valid MAC, **``occurred_at``** outside window → **``replay_rejected``**, no side effects."""
    data = json.loads((_FIXTURES_DIR / "run_started.json").read_bytes())
    data["occurred_at"] = "2020-01-01T00:00:00Z"
    raw = json.dumps(data, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    header = _sign(raw)
    fixed_now = datetime(2026, 3, 28, 15, 0, 0, tzinfo=timezone.utc)
    policy = LifecycleWebhookReplayPolicy(now=lambda: fixed_now)
    calls: list[object] = []

    def on_success(_: object) -> None:
        calls.append(_)

    result = handle_lifecycle_webhook_post(
        secret=_SECRET,
        method="POST",
        body=raw,
        headers={LIFECYCLE_WEBHOOK_SIGNATURE_HEADER: header},
        replay_policy=policy,
        on_success=on_success,
    )
    assert result.status == HTTPStatus.UNPROCESSABLE_ENTITY
    err = json.loads(result.body.decode("utf-8"))
    assert err["error"] == "replay_rejected"
    assert err["message"] == (
        "Delivery is outside the accepted time window or was already processed."
    )
    assert calls == []


def test_rp5_dedup_store_second_post_204_without_on_success() -> None:
    """**RP5:** library **``dedup_store``** prevents double **``on_success``** for same **``event_id``**."""
    raw = (_FIXTURES_DIR / "run_started.json").read_bytes()
    header = _sign(raw)
    store = InMemoryLifecycleWebhookDedupStore(ttl_seconds=3600.0)
    calls: list[object] = []

    def on_success(p: object) -> None:
        calls.append(p)

    for _ in range(2):
        result = handle_lifecycle_webhook_post(
            secret=_SECRET,
            method="POST",
            body=raw,
            headers={LIFECYCLE_WEBHOOK_SIGNATURE_HEADER: header},
            dedup_store=store,
            on_success=on_success,
        )
        assert result.status == HTTPStatus.NO_CONTENT
    assert len(calls) == 1


def test_replay_hooks_reject_non_object_json() -> None:
    raw = b"[1]"
    header = _sign(raw)
    result = handle_lifecycle_webhook_post(
        secret=_SECRET,
        method="POST",
        body=raw,
        headers={LIFECYCLE_WEBHOOK_SIGNATURE_HEADER: header},
        replay_policy=LifecycleWebhookReplayPolicy(),
    )
    assert result.status == HTTPStatus.BAD_REQUEST
    err = json.loads(result.body.decode("utf-8"))
    assert err["error"] == "invalid_payload_shape"


def test_replay_hooks_unknown_event_type_422() -> None:
    data = json.loads((_FIXTURES_DIR / "run_started.json").read_bytes())
    data["event_type"] = "replayt.lifecycle.run.unknown"
    raw = json.dumps(data, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    result = handle_lifecycle_webhook_post(
        secret=_SECRET,
        method="POST",
        body=raw,
        headers={LIFECYCLE_WEBHOOK_SIGNATURE_HEADER: _sign(raw)},
        replay_policy=LifecycleWebhookReplayPolicy(check_occurred_at=False),
    )
    assert result.status == HTTPStatus.UNPROCESSABLE_ENTITY
    err = json.loads(result.body.decode("utf-8"))
    assert err["error"] == "unknown_event_type"
