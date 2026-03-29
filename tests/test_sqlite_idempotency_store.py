"""SQLite idempotency store (**SPEC_SQLITE_IDEMPOTENCY_STORE** **SQ1**–**SQ4**; no network)."""

from __future__ import annotations

import hashlib
import hmac
import json
import threading
from datetime import datetime, timezone
from http import HTTPStatus
from pathlib import Path

from replayt_lifecycle_webhooks import (
    SqliteLifecycleWebhookDedupStore,
    handle_lifecycle_webhook_post,
)
from replayt_lifecycle_webhooks.signature import LIFECYCLE_WEBHOOK_SIGNATURE_HEADER

_FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures" / "events"
_SECRET = "replay-test-secret"


def _sign(body: bytes) -> str:
    mac = hmac.new(_SECRET.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return f"sha256={mac}"


def test_sq1_duplicate_key_first_true_second_false(tmp_path: Path) -> None:
    store = SqliteLifecycleWebhookDedupStore(
        path=tmp_path / "dedup.sqlite",
        ttl_seconds=3600.0,
    )
    assert store.try_claim("evt-1") is True
    assert store.try_claim("evt-1") is False


def test_sq2_expiry_allows_reclaim(tmp_path: Path) -> None:
    t0 = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    clock: list[datetime] = [t0]
    store = SqliteLifecycleWebhookDedupStore(
        path=tmp_path / "dedup.sqlite",
        ttl_seconds=60.0,
        now=lambda: clock[0],
    )
    assert store.try_claim("evt-1") is True
    assert store.try_claim("evt-1") is False
    clock[0] = t0.replace(minute=5)
    assert store.try_claim("evt-1") is True


def test_sq3_concurrent_try_claim_single_winner(tmp_path: Path) -> None:
    store = SqliteLifecycleWebhookDedupStore(
        path=tmp_path / "dedup.sqlite",
        ttl_seconds=3600.0,
    )
    n = 16
    barrier = threading.Barrier(n)
    results: list[bool] = []

    def worker() -> None:
        barrier.wait()
        results.append(store.try_claim("concurrent-key"))

    threads = [threading.Thread(target=worker) for _ in range(n)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert results.count(True) == 1
    assert results.count(False) == n - 1


def test_sq4_handler_duplicate_post_sqlite_dedup_on_success_once(
    tmp_path: Path,
) -> None:
    """**SQ4:** two **``handle_lifecycle_webhook_post``** calls, same **``event_id``**, SQLite **``dedup_store``** → **204** twice; **``on_success``** once."""
    raw = (_FIXTURES_DIR / "run_started.json").read_bytes()
    header = _sign(raw)
    store = SqliteLifecycleWebhookDedupStore(
        path=tmp_path / "dedup.sqlite",
        ttl_seconds=3600.0,
    )
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
    payload = json.loads(raw.decode("utf-8"))
    assert calls[0] == payload
