"""Optional metrics callbacks for verify and HTTP handler outcomes (stdlib-only).

See ``docs/SPEC_METRICS_HOOKS.md``. Callbacks must not receive raw bodies, secrets, or full signature values.
"""

from __future__ import annotations

import threading
from collections import Counter
from typing import Literal, Protocol

# Coarse verify outcomes (SPEC_METRICS_HOOKS); stable string literals for integrator adapters.
LifecycleWebhookVerifyOutcome = Literal[
    "success",
    "missing_signature",
    "format_error",
    "mismatch",
]


class LifecycleWebhookMetrics(Protocol):
    """Optional narrow surface for recording verify and handler outcomes."""

    def record_verify_outcome(
        self,
        *,
        outcome: LifecycleWebhookVerifyOutcome,
        duration_sec: float,
    ) -> None:
        """Record signature verification result.

        ``duration_sec`` covers verify-only work (HMAC parse + compare), measured with
        :func:`time.monotonic` when metrics are enabled.

        **Not passed:** raw body bytes, secret material, or the full ``Replayt-Signature`` header value.
        """
        ...

    def record_handler_outcome(
        self,
        *,
        http_status: int,
        error_code: str | None,
        duration_sec: float,
    ) -> None:
        """Record the HTTP-level outcome for one handler invocation.

        ``duration_sec`` is wall time from handler entry to exit, **including** verification
        and JSON work, so it is **>=** the verify slice reported by :meth:`record_verify_outcome`
        when both run for the same request.

        ``error_code`` is the JSON ``error`` field when the handler returns a structured 4xx body;
        use ``None`` for 2xx and for responses without that field (for example **204**).
        """
        ...


class NullLifecycleWebhookMetrics:
    """No-op metrics implementation for explicit wiring tests."""

    def record_verify_outcome(
        self,
        *,
        outcome: LifecycleWebhookVerifyOutcome,
        duration_sec: float,
    ) -> None:
        return None

    def record_handler_outcome(
        self,
        *,
        http_status: int,
        error_code: str | None,
        duration_sec: float,
    ) -> None:
        return None


class InMemoryLifecycleWebhookMetrics:
    """In-process counters and last durations (tests and local debugging only)."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.verify_outcomes: Counter[str] = Counter()
        self.handler_outcomes: Counter[tuple[int, str | None]] = Counter()
        self.last_verify_duration_sec: float | None = None
        self.last_handler_duration_sec: float | None = None

    def record_verify_outcome(
        self,
        *,
        outcome: LifecycleWebhookVerifyOutcome,
        duration_sec: float,
    ) -> None:
        with self._lock:
            self.verify_outcomes[outcome] += 1
            self.last_verify_duration_sec = duration_sec

    def record_handler_outcome(
        self,
        *,
        http_status: int,
        error_code: str | None,
        duration_sec: float,
    ) -> None:
        with self._lock:
            self.handler_outcomes[(http_status, error_code)] += 1
            self.last_handler_duration_sec = duration_sec
