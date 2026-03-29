# Spec: SQLite reference idempotency store for `event_id`

**Backlog:** Reference SQLite-backed idempotency store for `event_id` (`d10cf76f-e11e-4674-9d81-6d06899b4a64`).  
**Audience:** Spec gate (2b), Builder (3), Tester (4), integrators, operators.

## Purpose

**[SPEC_DELIVERY_IDEMPOTENCY.md](SPEC_DELIVERY_IDEMPOTENCY.md)** and **[SPEC_REPLAY_PROTECTION.md](SPEC_REPLAY_PROTECTION.md)** define **`event_id`** deduplication semantics and the **`LifecycleWebhookDedupStore`** protocol (**`try_claim(key: str) -> bool`**). **`InMemoryLifecycleWebhookDedupStore`** is a **single-process** reference.

This document specifies a **second reference implementation** backed by **SQLite** so small teams can persist idempotency keys **without** Redis or another server, while **other integrators remain free to use any store** that implements **`LifecycleWebhookDedupStore`**.

## Non-goals

- **Not** a requirement to use SQLite in production; it is a **reference** and **optional** adoption path.
- **Not** a distributed or highly available dedupe service; SQLite fits **one host / shared disk** patterns and **small** traffic.
- **Not** a replacement for **`InMemoryLifecycleWebhookDedupStore`** in tests that do not need persistence.

## Dependencies

- **Mandatory third-party packages:** **none**. Implementation **must** use the **stdlib** **`sqlite3`** module only (same bar as **`InMemoryLifecycleWebhookDedupStore`** in **SPEC_REPLAY_PROTECTION** **§ Reference implementation requirements**).

## Semantic contract

The SQLite store **must** satisfy **`LifecycleWebhookDedupStore`**: **`try_claim`** returns **`True`** on the **first** successful claim of **`key`** inside the retention window and **`False`** when **`key`** was already claimed and **not** yet expired.

Normative alignment:

- **Keys:** Raw **`str`** values, typically the payload **`event_id`** after **`parse_lifecycle_webhook_event`** (same guidance as **SPEC_REPLAY_PROTECTION** **§ Pluggable deduplication store**).
- **TTL:** Configurable **`ttl_seconds`** (or equivalent name). A claim remains valid until **`now + ttl`**; after eviction / expiry, **`try_claim`** for the same **`key`** **may** return **`True`** again (late duplicate risk per **SPEC_DELIVERY_IDEMPOTENCY** **§ TTL**).
- **Injectable time:** **`now`** (or equivalent **`Callable[[], datetime]`**) **must** be injectable for deterministic unit tests, matching **`InMemoryLifecycleWebhookDedupStore`**.

### Persistence schema (normative minimum)

The implementation **must** document the on-disk schema. A **minimal** acceptable shape:

| Column | Role |
| ------ | ---- |
| **`key`** | **Primary key** — dedupe string (e.g. **`event_id`**). |
| **`expires_at`** | UTC (or timezone-aware) instant after which the row is treated as expired. |

Implementations **may** add helper columns (e.g. created-at) if documented; they **must not** weaken **`try_claim`** semantics.

### Expiry strategy

Implementations **may** use **lazy** eviction (delete or ignore expired rows on read), **periodic** cleanup, or **`INSERT OR REPLACE`** with updated expiry, as long as **`try_claim`** behavior matches the protocol. Callers **must** still size **`ttl_seconds`** using **SPEC_DELIVERY_IDEMPOTENCY** guidance.

## Concurrency and SQLite locking

The reference implementation **must** document, in the **module docstring** (or this spec cross-linked from there), integrator-facing notes covering at least:

1. **Single-writer** behavior: concurrent **`try_claim`** calls contend on the database file; connections **should** use a non-zero **`timeout`** ( **`sqlite3.connect(..., timeout=...)`** ) so writers wait briefly instead of failing immediately with **`database is locked`**.
2. **Multi-threaded servers:** If the process serves traffic on multiple threads, either use **one connection per thread** with **`check_same_thread=False`** where appropriate, or serialize access to a single connection—**document** which pattern the shipped class uses.
3. **Multi-process workers (e.g. Gunicorn):** A **single** SQLite file can become a **bottleneck**; operators **may** prefer **WAL** mode (**`PRAGMA journal_mode=WAL`**) and/or **one DB file per worker**; this package **does not** mandate a deployment topology.

**Tests:** See **SQ3** in **SPEC_AUTOMATED_TESTS.md** (**§ Backlog `d10cf76f`**).

## Public API (when implemented)

Stable name (**normative for Builder**):

| Symbol | Role |
| ------ | ---- |
| **`SqliteLifecycleWebhookDedupStore`** | Concrete **`LifecycleWebhookDedupStore`** using **`sqlite3`** and a filesystem path (or suitable URI accepted by **`sqlite3.connect`**). |

- **Export:** **`SqliteLifecycleWebhookDedupStore`** **must** appear in the package root **`__all__`** in **table order** after **`InMemoryLifecycleWebhookDedupStore`** (see **SPEC_PUBLIC_API.md** **§ Planned: SQLite reference store**).
- **Internal module path:** Implementation **may** live in **`src/replayt_lifecycle_webhooks/sqlite_idempotency.py`** (or adjacent internal module); deep imports remain **unsupported** per **SPEC_PUBLIC_API** until explicitly promoted.
- **CHANGELOG** and **SPEC_PUBLIC_API** **must** be updated in the same release that ships the symbol.

## Wiring into the minimal HTTP handler

Integrators **may** pass an instance as **`dedup_store=`** to **`handle_lifecycle_webhook_post`** and **`make_lifecycle_webhook_wsgi_app`** per **SPEC_MINIMAL_HTTP_HANDLER** and **SPEC_REPLAY_PROTECTION** (same contract as **`InMemoryLifecycleWebhookDedupStore`**).

**Copy-paste shape (illustrative — exact constructor parameters are implementation-defined but must include TTL and path or equivalent):**

```python
from replayt_lifecycle_webhooks import (
    SqliteLifecycleWebhookDedupStore,
    handle_lifecycle_webhook_post,
)

dedup = SqliteLifecycleWebhookDedupStore(
    path="/var/lib/myapp/webhook_idempotency.sqlite",
    ttl_seconds=86_400,
)

result = handle_lifecycle_webhook_post(
    secret=secret,
    method=method,
    body=body,
    headers=headers,
    dedup_store=dedup,
    on_success=on_success,
)
```

**README** **must** point integrators at **this spec** from the **`dedup_store`** / idempotency discussion and state that **SQLite is optional**; the normative API names and test rows live here and in **SPEC_PUBLIC_API** (**§ Planned** until **SQ6**).

## Implementation status (this repository)

| Item | Status | Notes |
| ---- | ------ | ----- |
| Normative spec (this file) | **Done** (phase **2**) | Backlog **`d10cf76f`** |
| **`SqliteLifecycleWebhookDedupStore`** + tests **SQ1**–**SQ7** | **Pending** (phase **3**) | See **SPEC_AUTOMATED_TESTS.md** |
| **README** wiring snippet + link | **Pending** (phase **3**) | Short optional subsection |

## Acceptance criteria (Builder / Tester)

Mapped to **SPEC_AUTOMATED_TESTS.md** **§ Backlog `d10cf76f`** (**SQ1**–**SQ7**).

| # | Criterion | Verification |
|---|-----------|--------------|
| **SQ1** | **Duplicate key** — Two **`try_claim`** calls with the same **`key`** before expiry → first **`True`**, second **`False`**. | **`pytest`**, no network |
| **SQ2** | **Expiry** — After advancing injected **`now`** past TTL, **`try_claim`** for the same **`key`** returns **`True`** again (re-claim). | **`pytest`**, no network |
| **SQ3** | **Concurrency / locking** — Either (a) a **network-free** **`pytest`** that exercises concurrent **`try_claim`** from two threads against one store with documented connection settings, **or** (b) **module docstring** satisfies **§ Concurrency and SQLite locking** above **and** a **`pytest`** asserts that docstring contains required substrings (minimum: **`timeout`**, **`database is locked`** or **`locked`**, **`WAL`** or **`journal_mode`**). Prefer (a) when reliable on CI. | **`pytest`** |
| **SQ4** | **Handler integration** — Two **`handle_lifecycle_webhook_post`** calls with the same verified **`event_id`** and SQLite **`dedup_store`** → **204** both times; **`on_success`** runs once (same bar as **H10** / **RP5** for the SQLite backend). | **`pytest`**, no network |
| **SQ5** | **Integrator discoverability** — **README** links **this spec** from the handler / idempotency area (and/or overview). **Normative** copy-paste lives in **§ Wiring into the minimal HTTP handler** above; **README** **may** duplicate a short snippet once **`SqliteLifecycleWebhookDedupStore`** exists (must stay consistent with this spec). | Doc review |
| **SQ6** | **Public surface** — **`SqliteLifecycleWebhookDedupStore`** in package root **`__all__`** and **SPEC_PUBLIC_API** table; **CHANGELOG** **Unreleased** **Added**. | **`tests/test_public_api.py`** + doc review |
| **SQ7** | **No new mandatory deps** — **`pyproject.toml`** **`[project].dependencies`** unchanged for this feature. | **`pyproject.toml`** review |

## Related docs

- **[SPEC_DELIVERY_IDEMPOTENCY.md](SPEC_DELIVERY_IDEMPOTENCY.md)** — TTL guidance, at-least-once semantics.
- **[SPEC_REPLAY_PROTECTION.md](SPEC_REPLAY_PROTECTION.md)** — **`LifecycleWebhookDedupStore`**, **`InMemoryLifecycleWebhookDedupStore`**, handler hooks.
- **[SPEC_MINIMAL_HTTP_HANDLER.md](SPEC_MINIMAL_HTTP_HANDLER.md)** — **`dedup_store`** parameter, **H10**, **RP5** overlap.
- **[SPEC_PUBLIC_API.md](SPEC_PUBLIC_API.md)** — **`__all__`** ordering and supported imports.
- **[README.md](../README.md)** — operator entry; optional SQLite subsection (acceptance **SQ5**).
