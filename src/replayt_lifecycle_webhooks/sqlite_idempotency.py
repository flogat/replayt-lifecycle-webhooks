"""SQLite-backed :class:`LifecycleWebhookDedupStore` (``docs/SPEC_SQLITE_IDEMPOTENCY_STORE.md``).

Uses **stdlib** :mod:`sqlite3` only. Table **``lifecycle_webhook_dedup``**: **``key``** (**TEXT**, primary key),
**``expires_at``** (**REAL**, Unix timestamp in UTC; expired when ``expires_at <= now``).

**Concurrency (integrators):**

1. **Single-writer:** concurrent :meth:`SqliteLifecycleWebhookDedupStore.try_claim` calls contend on the database file.
   Connections use a non-zero ``timeout`` (``sqlite3.connect(..., timeout=...)``) so writers wait briefly instead of failing
   immediately with **``database is locked``**.
2. **Multi-threaded servers:** This class keeps **one** connection and serializes all access with a **``threading.Lock``**
   so ``try_claim`` is safe to share across threads in one process. For very high concurrency, prefer one connection per
   thread with ``check_same_thread=False`` and your own coordination, or an external store.
3. **Multi-process workers (e.g. Gunicorn):** A single SQLite file can be a bottleneck; operators may prefer **WAL** mode
   (``PRAGMA journal_mode=WAL``) and/or one DB file per worker; this package does not mandate a deployment topology.
   WAL is enabled on open for this reference implementation.
"""

from __future__ import annotations

import sqlite3
import threading
from datetime import datetime, timedelta, timezone
from os import PathLike
from typing import Callable


def _default_now() -> datetime:
    return datetime.now(timezone.utc)


class SqliteLifecycleWebhookDedupStore:
    """Filesystem dedupe store with TTL and injectable clock (**SPEC_SQLITE_IDEMPOTENCY_STORE**).

    Same :meth:`try_claim` semantics as :class:`replay_protection.InMemoryLifecycleWebhookDedupStore`.
    """

    def __init__(
        self,
        *,
        path: str | PathLike[str],
        ttl_seconds: float,
        now: Callable[[], datetime] | None = None,
        connect_timeout: float = 5.0,
    ) -> None:
        self._ttl = timedelta(seconds=ttl_seconds)
        self._now: Callable[[], datetime] = now or _default_now
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(
            str(path),
            timeout=connect_timeout,
            check_same_thread=False,
            isolation_level=None,
        )
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS lifecycle_webhook_dedup (
                key TEXT NOT NULL PRIMARY KEY,
                expires_at REAL NOT NULL
            )
            """
        )

    def try_claim(self, key: str) -> bool:
        with self._lock:
            cur = self._conn.cursor()
            now_dt = self._now().astimezone(timezone.utc)
            now_ts = now_dt.timestamp()
            cur.execute(
                "DELETE FROM lifecycle_webhook_dedup WHERE expires_at <= ?",
                (now_ts,),
            )
            cur.execute(
                "SELECT 1 FROM lifecycle_webhook_dedup WHERE key = ?",
                (key,),
            )
            if cur.fetchone() is not None:
                return False
            expires_ts = (now_dt + self._ttl).timestamp()
            cur.execute(
                "INSERT INTO lifecycle_webhook_dedup (key, expires_at) VALUES (?, ?)",
                (key, expires_ts),
            )
            return True
