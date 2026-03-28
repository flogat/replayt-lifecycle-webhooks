# Spec: replay protection and idempotency hooks for deliveries

**Backlog:** Add replay protection and idempotency hooks for deliveries (`f9677140-0803-41c7-9d1c-82fc85f25f8d`).  
**Audience:** Spec gate (2b), Builder (3), Tester (4), integrators, operators.

## Purpose

**HMAC v1** proves **integrity** with the shared secret; it does **not** prove that a POST is **fresh** or **first-seen**.
An attacker who captures a valid request can **replay** it until the secret rotates. **Benign duplicate POSTs** (retries,
load balancers) are expected under **at-least-once** delivery and are solved with **`event_id`** idempotency
(**[SPEC_DELIVERY_IDEMPOTENCY.md](SPEC_DELIVERY_IDEMPOTENCY.md)**).

This document is the **normative consumer-side contract** for:

- Distinguishing **duplicate delivery** (same logical event) from **stale or malicious replay** (unacceptable freshness).
- Optional **wire-level** signals (headers or payload fields) used **after** successful MAC verification.
- A **pluggable store** interface plus an **in-memory** implementation suitable for **tests** and **local** demos.
- **Test** expectations that pair with backlog acceptance criteria.

**Relationship to other specs:** Run **`verify_lifecycle_webhook_signature`** (and the handler’s verify-before-JSON
ordering) **before** any replay or dedupe logic described here. Map policy violations to **`replay_rejected`** per
**[SPEC_WEBHOOK_FAILURE_RESPONSES.md](SPEC_WEBHOOK_FAILURE_RESPONSES.md)** when returning JSON errors.

## Threat model (integrator-facing)

| Scenario | Description | Primary defense (this package’s contract) |
| -------- | ----------- | ---------------------------------------- |
| **Benign duplicate** | Sender or network retries the **same** logical emission (**same** body octets, same **`event_id`**). | **Idempotency store** keyed by **`event_id`** (and TTL) per **SPEC_DELIVERY_IDEMPOTENCY**; second delivery **acks** without new side effects (**2xx**, often **204**). |
| **Stale replay** | Attacker (or ancient retry) posts a **still-valid MAC** for an **old** event outside your freshness window. | **Freshness policy** on **`occurred_at`** and/or optional timestamp headers vs receiver clock (injectable **`now`** in tests). |
| **Nonce / delivery-id reuse** | Attacker or bug replays the same **HTTP-scoped** identifier. | Optional **one-time** store entries for documented header values (when enabled). |

Do **not** conflate **“duplicate”** (idempotent ok) with **“replay rejected”** (policy failure): the former should usually
still return **2xx** to stop retry storms; the latter returns **4xx**/**422** with **`replay_rejected`** when you expose a
JSON body (see **SPEC_WEBHOOK_FAILURE_RESPONSES**).

## Normative processing order (post-MAC)

After **`Replayt-Signature`** verification succeeds and (when using the typed pipeline) **`parse_lifecycle_webhook_event`**
produces a model with **`event_id`** and **`occurred_at`**:

1. **Freshness check** — If enabled, evaluate **`occurred_at`** (RFC 3339, see **[EVENTS.md](EVENTS.md)**) against
   **`now`** using **§ Default clock and age parameters**. If the event is **too old** or **too far in the future**,
   **reject** (do not run business **`on_success`**).
2. **Optional header gates** — If enabled, evaluate **§ Optional wire headers** (nonce, delivery id, timestamp header)
   against the same or a dedicated store.
3. **Idempotency / dedupe** — **`try_claim_event_id`** (or equivalent) against the **pluggable store**. If the key was
   already claimed within TTL, treat as **duplicate delivery**: **ack without new side effects** (still **2xx** if you
   follow **SPEC_DELIVERY_IDEMPOTENCY** interaction guidance).

Implementations **may** combine freshness and idempotency in one module; the **ordering above** is **normative** so
freshness failures cannot be bypassed by claiming an idempotency slot first.

## Payload-based freshness (`occurred_at`)

| Input | Source |
| ----- | ------ |
| **`occurred_at`** | Required envelope field on lifecycle events (**EVENTS.md**). Parsed to a timezone-aware **`datetime`**. |
| **`now`** | Receiver’s current instant. **Must** be **injectable** in library code (parameter or clock callback) so tests do not depend on real wall-clock sleeps. |

### Default clock and age parameters (recommended defaults for the reference implementation)

These are **defaults** the Builder **should** ship in the public helper/config object; integrators **may** override per
deployment.

| Parameter | Recommended default | Meaning |
| --------- | ------------------- | ------- |
| **`max_event_age_seconds`** | **900** (15 minutes) | Reject if **`now - occurred_at`** exceeds this value (event too stale). |
| **`max_future_skew_seconds`** | **300** (5 minutes) | Reject if **`occurred_at - now`** exceeds this value (clock skew or forgery). |

**Rationale:** Short **MAC-only** replay windows reduce exposure if a capture leaks; **5 minutes** future skew matches
common API **clock-skew** practice. Operators with long approval cycles **increase** **`max_event_age_seconds`** or rely
primarily on **`event_id`** TTL rather than tight wall-clock windows.

**Explicit rejection rule (normative for the helper):** Let **`delta = occurred_at - now`** (signed). Reject if
**`delta < -max_event_age_seconds`** OR **`delta > max_future_skew_seconds`**.

## Optional wire headers (forward-compatible)

Upstream **replayt** may later document dedicated headers. Until then, this repo **reserves** the following names for
**optional** consumer-side enforcement. **None** are required for **v1** MAC verification (**SPEC_WEBHOOK_SIGNATURE**).

| Header (suggested) | Purpose | Consumer behavior when present and feature enabled |
| ------------------ | ------- | --------------------------------------------------- |
| **`Replayt-Delivery-Id`** | Opaque string identifying **this HTTP delivery attempt** (may differ from **`event_id`** if the sender retries with a new attempt id). | **First-seen wins** in a store with TTL ≥ your retry horizon; a **second** POST with the **same** id → treat as **duplicate** (**2xx**, no new side effects) **or** reject if your policy treats id reuse as an error. |
| **`Replayt-Webhook-Timestamp`** | ISO 8601 / RFC 3339 instant for **when the sender issued the HTTP delivery** (distinct from payload **`occurred_at`** if both exist). | Compare to **`now`** with the **same** skew parameters as **§ Payload-based freshness** (or stricter). If both header and **`occurred_at`** are checked, **reject** if **either** fails. |
| **`Replayt-Nonce`** | One-time token per delivery. | Store until TTL; **duplicate nonce** → **`replay_rejected`**. |

**HTTP `Date`:** Integrators **may** use the standard **`Date`** header instead of or in addition to
**`Replayt-Webhook-Timestamp`** if their edge guarantees it reflects sender time; document **your** mapping in runbooks.
This package’s reference implementation **should** prefer **explicit replayt-prefixed** headers when implementing
header-based freshness to avoid ambiguous proxy behavior.

**Security note:** Unless a header value is **covered by the MAC** or otherwise bound to the body, it can be **spoofed**
by anyone who can POST to the endpoint. **Payload `occurred_at`** is inside the signed bytes and is the **preferred**
freshness signal for **v1**. Header checks are **optional hardening** when the deployment trusts the path that sets them
(e.g. mutual TLS + gateway injection).

## Pluggable deduplication store

### Semantic contract

The store answers: **“May this integrator-defined key cause side effects right now?”**

| Operation | Expected behavior |
| --------- | ----------------- |
| **`try_claim(key: str) -> bool`** (or equivalent) | Return **`True`** if this is the **first** time the key is claimed within the retention window (**side effects allowed**). Return **`False`** if the key was already claimed (**duplicate**; **no** new side effects). |
| **TTL / eviction** | Implementations **must** document eviction; callers **must** size TTL to **SPEC_DELIVERY_IDEMPOTENCY** guidance. |
| **Thread / process safety** | Production stores (**Redis**, DB) provide their own; the **in-memory** reference is **single-process** only. |

**Keys (normative guidance):**

- **Primary:** raw **`event_id`** string after successful parse.
- **Optional:** separate namespace for **`Replayt-Delivery-Id`** (e.g. prefix **`delivery:`**) if you enable header dedupe.

### Reference implementation requirements

| Item | Requirement |
| ---- | ----------- |
| **Protocol / ABC** | Expose a **`typing.Protocol`** (or abstract base) **`LifecycleWebhookDedupStore`** documenting **`try_claim`**. |
| **`InMemoryLifecycleWebhookDedupStore`** | Concrete implementation backed by a **`dict`** (or similar) with **configurable TTL**, suitable for **unit tests** and **examples**. **Must** allow **injectable time** for deterministic expiry tests. |
| **Mandatory dependency** | **No** new **mandatory** third-party dependencies for the store contract; **stdlib** only for the in-memory type. |

## Optional HTTP handler integration

When extending **`handle_lifecycle_webhook_post`** (**SPEC_MINIMAL_HTTP_HANDLER**), optional keyword parameters **may**
include:

- **`dedup_store: LifecycleWebhookDedupStore | None`** — if **`None`**, preserve today’s behavior (no idempotency in the
  library path).
- **`replay_policy`** — a small config object or **`None`**: freshness toggles, **`max_event_age_seconds`**,
  **`max_future_skew_seconds`**, optional header enable flags, and **`now`** / clock injection.

**Status codes:** Duplicate (**idempotent hit**) → **204** (or **200** per integrator policy) **without** invoking
**`on_success`** for new work. Freshness / nonce / policy failure → **422** (recommended) with **`replay_rejected`** JSON
per **SPEC_WEBHOOK_FAILURE_RESPONSES**.

Exact parameter names are **implementation details**; they **must** appear in **CHANGELOG.md** and package **`__all__`**
when stabilized.

## Acceptance criteria (Builder / Tester)

Maps to backlog acceptance: *documented strategy*, *code path rejects or de-duplicates*, *tests for replay + duplicate*.

| # | Criterion | Verification |
|---|-----------|--------------|
| **RP0** | This spec is linked from **README**, **MISSION**, **DESIGN_PRINCIPLES**, **SPEC_DELIVERY_IDEMPOTENCY**, **SPEC_WEBHOOK_SIGNATURE**, and **SPEC_AUTOMATED_TESTS**. | Doc review |
| **RP1** | **Documented** freshness strategy: **`occurred_at`** vs **`now`**, **`max_event_age_seconds`**, **`max_future_skew_seconds`**, optional headers per **§ Optional wire headers**. | Doc review + public API docstrings |
| **RP2** | **Code path** applies dedupe and/or freshness **after** MAC verify (and after JSON parse when using **`event_id`** / **`occurred_at`** from the typed model). | Code review |
| **RP3** | **`LifecycleWebhookDedupStore`** protocol (or equivalent) and **`InMemoryLifecycleWebhookDedupStore`** shipped in **`src/`**, re-exported or documented as public. | Code review + **CHANGELOG** |
| **RP4** | **Tests — replay / stale:** At least one **network-free** **pytest** case where the signature is **valid** but **`occurred_at`** is outside the configured window → outcome is **`replay_rejected`** (handler JSON) **or** documented exception from the standalone helper; **`on_success`** / side-effect counter **not** incremented. | **`pytest`** |
| **RP5** | **Tests — duplicate delivery:** At least one **network-free** **pytest** case where the **same** **`event_id`** is presented twice with valid MACs → **no double side effects**. **Normative:** **SPEC_DELIVERY_IDEMPOTENCY** **I4** / **`test_i4_duplicate_signed_post_idempotent_side_effects_pattern`** satisfies **RP5** when it remains green; new tests **may** consolidate or extend that pattern. | **`pytest`** |

## Implementation status (this repository)

| Item | Status | Notes |
| ---- | ------ | ----- |
| Normative spec (this file) | **Done** (phase **2**) | — |
| Public helpers + in-memory store + handler hooks | **Pending** (phase **3**+) | Follow **RP2**–**RP3** |
| **pytest** **RP4** / **RP5** | **Pending** (phase **3**+) | **RP5** overlaps **I4** |

## Related docs

- **[SPEC_DELIVERY_IDEMPOTENCY.md](SPEC_DELIVERY_IDEMPOTENCY.md)** — **`event_id`**, at-least-once semantics, TTL guidance.
- **[SPEC_WEBHOOK_SIGNATURE.md](SPEC_WEBHOOK_SIGNATURE.md)** — verify before JSON; v1 MAC does not include timestamps.
- **[SPEC_WEBHOOK_FAILURE_RESPONSES.md](SPEC_WEBHOOK_FAILURE_RESPONSES.md)** — **`replay_rejected`**, logging boundaries.
- **[SPEC_MINIMAL_HTTP_HANDLER.md](SPEC_MINIMAL_HTTP_HANDLER.md)** — **`handle_lifecycle_webhook_post`** status table.
- **[EVENTS.md](EVENTS.md)** — **`occurred_at`**, **`event_id`** envelope.
- **[SPEC_AUTOMATED_TESTS.md](SPEC_AUTOMATED_TESTS.md)** — CI invariants; backlog **`f9677140`** rows **RP4**–**RP5**.
