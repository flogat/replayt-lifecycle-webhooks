# Spec: delivery guarantees, `event_id`, and consumer idempotency

**Backlog:** Specify idempotency and replay-safe delivery semantics (`4280c054-4193-4754-8e4c-1da320975fac`).  
**Audience:** Spec gate (2b), Builder (3), Tester (4), integrators, operators.

## Purpose

HTTP lifecycle webhooks sit behind **retries**, **load balancers**, and **at-least-once** bridges. Consumers need a
**written contract** for:

- What the **sender** and **network** may do (duplicate deliveries, redelivery of the same logical event).
- How **`event_id`** relates to **deduplication** and what to do when senders misbehave.
- How this interacts with **HMAC v1** (integrity **without** built-in freshness).

**Normative field definitions** for the JSON envelope remain in **[EVENTS.md](EVENTS.md)**. This document adds **delivery
semantics** and **idempotency policy** that span envelope fields, verification, and operator runbooks.

## Delivery guarantees (consumer-facing)

| Guarantee | Status for this package’s contract |
| --------- | ----------------------------------- |
| **At-least-once on the wire** | **Assume yes.** Integrators SHOULD design handlers so **duplicate** HTTP POSTs of the **same** logical notification do not cause duplicate **side effects** (double approvals in **your** systems, duplicate tickets, duplicate metrics increments). This repository does **not** implement upstream delivery or HTTP client retry policy; it documents what **consumers** should expect. |
| **Exactly-once** | **Not guaranteed** between sender and consumer. Achieve **effectively-once** processing with an **application-level idempotency store** (see below). |
| **Ordering** | **Not guaranteed** across events. Use **`occurred_at`** (and your own ordering keys) for dashboards only unless upstream documents a stronger ordering contract. |
| **Freshness / anti-replay of old captures** | **Not part of HMAC v1.** Verification proves **integrity** with the shared secret, not that the POST is “new.” Bounded freshness requires **application policy** (TTL on idempotency records, optional future signed timestamps—see **[SPEC_WEBHOOK_SIGNATURE.md](SPEC_WEBHOOK_SIGNATURE.md)**). |

**Stronger guarantees:** If replayt or a compatible sender later documents **stronger** delivery semantics (e.g. dedupe
headers, signed timestamps), this repo SHOULD align **EVENTS.md**, **CHANGELOG.md**, and tests in a **minor** or **major**
release per **[EVENTS.md](EVENTS.md)** payload SemVer rules. Until then, treat the table above as normative for
integrators.

## `event_id`: role and sender expectations

### Primary idempotency key (recommended)

After **`verify_lifecycle_webhook_signature`** succeeds, integrators SHOULD use **`event_id`** as the **primary
idempotency key** for lifecycle processing:

- **First time** a given **`event_id`** is seen → run your normal post-verify pipeline (parse with
  **`parse_lifecycle_webhook_event`**, update state, notify, etc.).
- **Duplicate** POST with the **same** **`event_id`** and **byte-identical** body → treat as **redelivery**; **skip**
  new side effects (return **204** / **200** per your policy) or no-op your worker.

Because **v1** signs the **raw body**, a redelivery with the same logical meaning **must** carry the **same** octets to
produce the same MAC. Changing the body while reusing **`event_id`** would be a **sender bug** (and likely a MAC
failure).

### Stable per logical emission (normative recommendation for senders)

**Compatible senders (including reference fixtures and demos in this repo) SHOULD:**

1. Assign **one** **`event_id`** per **logical lifecycle emission** (one transition you intend-notify for: e.g. one
   **`run.completed`** for a given run, one **`approval.pending`** for a given gate).
2. Reuse that **`event_id`** and the **same** serialized JSON body for **every** HTTP delivery attempt of that emission
   (client retries, gateway retries, manual replays of the same payload).

**Corollary:** A **new** lifecycle transition **SHOULD** use a **new** **`event_id`**. That keeps “unique per logical
event” true at the **emission** granularity integrators care about for dedupe.

**This repository** does not control upstream replayt HTTP emitters. Until upstream publishes an authoritative rule,
**EVENTS.md** and **fixtures** in this repo **follow** the recommendation above so tests and copy-paste examples teach
safe consumer behavior.

### Composite / fallback keys (misbehaving or legacy senders)

If a sender issues a **new** **`event_id`** on every HTTP attempt for the **same** logical event, dedupe on **`event_id`**
alone **will not** collapse duplicates. Integrators MAY use a **composite key** at their own risk, for example:

- **`event_type`** + **`correlation.run_id`** + a **detail** discriminator appropriate to the event (e.g. terminal
  run outcomes: only one **`run.completed`** / **`run.failed`** per run in many deployments).
- For approvals: **`event_type`** + **`correlation.approval_request_id`** when present.

Composite keys are **not** globally unique across all possible senders; document **your** deployment’s mapping and test it.
Prefer negotiating **stable `event_id`** with the sender when possible.

## Consumer-side idempotency store

### Recommended shape

After verification, compute a dedupe key (prefer **`event_id`**; else your composite). Store it in a **durable or
semi-durable** store (database row, Redis `SETNX`, workflow engine idempotency slot) **before** or **as part of** the
transaction that commits side effects.

### TTL (time-to-live)

**No universal TTL is mandated**—choose from **your** workflow length, compliance retention, and storage limits.

**Guidance (starting point for operators):**

| Deployment pattern | Suggested minimum retention of “seen” keys |
| ------------------ | ------------------------------------------ |
| Short-lived automations | **24–72 hours** may be enough if runs and approvals complete within that window and late duplicates are acceptable to ignore after eviction. |
| Long-running workflows / approvals | **7–30 days** or align with the **longest** plausible retry + approval window in your org. |
| Audit-sensitive or compliance-heavy | Retain **longer** (or archive idempotency decisions) per policy; duplicates after TTL expiry may re-run side effects—document that risk. |

**TTL expiry** means a **late duplicate** could be processed twice. That is **acceptable** for many metrics/notifications;
it is **unacceptable** for irreversible actions unless another guard exists (e.g. downstream system idempotency).

### Interaction with HTTP responses

Returning **2xx** after successful processing tells senders and proxies to **stop retrying**. For **duplicate** deliveries,
**2xx** (often **204**) is appropriate so retries do not become error storms. See
**[SPEC_WEBHOOK_FAILURE_RESPONSES.md](SPEC_WEBHOOK_FAILURE_RESPONSES.md)** for **`replay_rejected`** when **your** policy
rejects a delivery (e.g. outside freshness window)—distinct from “already processed” duplicates you choose to ack
silently.

## Relationship to signing v1 and “replay”

- **HMAC v1** does **not** embed a nonce or timestamp in the signed bytes. An attacker with an **old** captured POST can
  replay it until you rotate the secret. **Consumer idempotency** and optional **freshness windows** (e.g. reject
  **`occurred_at`** older than *N* minutes **after** verification) are **application-layer** defenses—see
  **[SPEC_WEBHOOK_SIGNATURE.md](SPEC_WEBHOOK_SIGNATURE.md)** and **SPEC_WEBHOOK_FAILURE_RESPONSES** (**stale timestamp /
  replay** tables).

- **Duplicate delivery** (sender or network retries the **same** body) is **benign** if idempotency is correct; **replay
  of a different old event** is a **threat** if freshness is not enforced—do not conflate the two in runbooks.

## Implementation status (this repository)

| Item | Status | Follow-up |
| ---- | ------ | --------- |
| **Normative docs** (this file + **EVENTS.md** cross-links) | **Done** (phase **2** spec) | — |
| **Fixtures / synthetic examples** use **distinct** **`event_id`** per **distinct** logical event in examples | **Done** (examples in **EVENTS.md**) | Duplicate-delivery pair: **`run_started.json`** / **`run_started_redelivery.json`** (same bytes, same **`event_id`**) under **`tests/fixtures/events/`** and packaged **`replayt_lifecycle_webhooks/fixtures/events/`**. |
| **Automated tests** assert **`event_id`** uniqueness rules per logical event in fixtures | **Done** (phase **3**) | **`tests/test_lifecycle_events.py`** (**I3**, **I4**); see **Acceptance criteria** below. |
| **Upstream replayt** HTTP emitter guarantees | **Out of scope** for this repo | Track in **CHANGELOG** / **SPEC_REPLAYT_DEPENDENCY** when discovered. |

## Acceptance criteria (Builder / Tester)

Use with Spec gate and later phases.

| # | Criterion | Verification |
|---|-----------|--------------|
| I1 | **EVENTS.md** **`event_id`** description matches this spec (primary dedupe key; sender SHOULD stabilize per logical emission). | Doc review |
| I2 | **README** troubleshooting references duplicate delivery and points here. | Doc review |
| I3 | **Tests** (when implemented): for at least one **`event_type`**, two serialized payloads that represent the **same** logical emission use the **same** **`event_id`**; distinct emissions use **distinct** **`event_id`** (fixtures or generated examples). | **`tests/test_lifecycle_events.py`** (**pytest**) |
| I4 | Optional **duplicate POST** test: same raw body + signature twice → handler / integrator path acknowledges idempotent success without double side effect (where the project exposes a test seam). | **`tests/test_lifecycle_events.py`** **`test_i4_duplicate_signed_post_idempotent_side_effects_pattern`** (**pytest**) |

## Related docs

- **[EVENTS.md](EVENTS.md)** — envelope fields, **`event_type`** registry, **`schema_version`**.
- **[SPEC_WEBHOOK_SIGNATURE.md](SPEC_WEBHOOK_SIGNATURE.md)** — verification before JSON; v1 replay/freshness limits.
- **[SPEC_WEBHOOK_FAILURE_RESPONSES.md](SPEC_WEBHOOK_FAILURE_RESPONSES.md)** — **`replay_rejected`**, logging **`event_id`** safely.
- **[README.md](../README.md)** — operator entry and troubleshooting.
