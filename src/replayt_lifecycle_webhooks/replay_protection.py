"""Replay window checks and idempotency store hooks (``docs/SPEC_REPLAY_PROTECTION.md``).

Use **after** :func:`replayt_lifecycle_webhooks.verify_lifecycle_webhook_signature` succeeds.
Freshness uses payload **``occurred_at``** (RFC 3339) vs an injectable **``now``** so tests stay deterministic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Callable, Protocol


class LifecycleWebhookDedupStore(Protocol):
    """Pluggable idempotency store keyed by raw strings (typically **``event_id``**).

    **``try_claim``** returns **``True``** the first time a key is seen inside the retention window
    (caller may apply side effects). **``False``** means duplicate delivery (ack without new work).
    """

    def try_claim(self, key: str) -> bool:
        """Return **``True``** if the key was newly claimed; **``False``** if already claimed."""


class ReplayFreshnessRejected(Exception):
    """Raised when **``occurred_at``** is outside **``max_event_age_seconds``** / **``max_future_skew_seconds``**."""


def _parse_rfc3339_instant(value: str) -> datetime:
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def ensure_occurred_at_within_replay_window(
    occurred_at: str,
    *,
    now: datetime,
    max_event_age_seconds: float = 900.0,
    max_future_skew_seconds: float = 300.0,
) -> None:
    """Reject stale or far-future **``occurred_at``** per **SPEC_REPLAY_PROTECTION** (payload freshness).

    Let **``delta = occurred_at - now``** in seconds. Raises :exc:`ReplayFreshnessRejected` when
    **``delta < -max_event_age_seconds``** or **``delta > max_future_skew_seconds``**.

    **``now``** must be timezone-aware (converted to UTC for the comparison).
    """
    instant = _parse_rfc3339_instant(occurred_at)
    now_utc = now.astimezone(timezone.utc)
    delta = (instant - now_utc).total_seconds()
    if delta < -max_event_age_seconds or delta > max_future_skew_seconds:
        raise ReplayFreshnessRejected("occurred_at outside accepted replay window")


def _default_replay_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True, slots=True)
class LifecycleWebhookReplayPolicy:
    """Post-MAC freshness settings for :func:`replayt_lifecycle_webhooks.handler.handle_lifecycle_webhook_post`.

    **``occurred_at``** is compared to **``now()``** using **``max_event_age_seconds``** (default **900**)
    and **``max_future_skew_seconds``** (default **300**). Override **``now``** in tests.
    """

    check_occurred_at: bool = True
    max_event_age_seconds: float = 900.0
    max_future_skew_seconds: float = 300.0
    now: Callable[[], datetime] = field(default_factory=lambda: _default_replay_now)


class InMemoryLifecycleWebhookDedupStore:
    """Stdlib in-process dedupe store with TTL and injectable clock (**SPEC_REPLAY_PROTECTION** reference).

    **Not** thread-safe beyond the CPython GIL dict semantics; use Redis or similar in production
    if multiple workers share traffic.
    """

    def __init__(
        self,
        *,
        ttl_seconds: float,
        now: Callable[[], datetime] | None = None,
    ) -> None:
        self._ttl = timedelta(seconds=ttl_seconds)
        self._now: Callable[[], datetime] = now or _default_replay_now
        self._expires: dict[str, datetime] = {}

    def try_claim(self, key: str) -> bool:
        current = self._now().astimezone(timezone.utc)
        self._evict_expired(current)
        if key in self._expires:
            return False
        self._expires[key] = current + self._ttl
        return True

    def _evict_expired(self, current: datetime) -> None:
        dead = [k for k, exp in self._expires.items() if exp <= current]
        for k in dead:
            del self._expires[k]
