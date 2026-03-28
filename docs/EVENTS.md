# Spec: lifecycle webhook JSON payload shapes (run and approval)

**Backlogs:**

- Map replayt run and approval events to webhook payload shapes (`076a56b7-afd9-4778-b46a-4dc8875a431f`).
- Define typed lifecycle event payloads (run + approval) (`0b929c17-525d-4ec7-b13c-a7b4f3f8ca10`).
- Define canonical webhook payload and event envelope schema (Mission Control `df51dbf9`; phase **2** spec refinement).
- Specify idempotency and replay-safe delivery semantics (`4280c054-4193-4754-8e4c-1da320975fac`).

**Audience:** Spec gate (2b), Builder (3), Tester (4), integrators, operators.

## Purpose and normative status

This document defines a **recommended JSON object model** for HTTP POST bodies that carry **run** and **approval**
lifecycle notifications, after **`Replayt-Signature`** verification succeeds. It exists so downstream systems get
**predictable fields** for routing, idempotency, dashboards, and **human-readable summaries** (Slack, email, PM tools;
sender-controlled wire **`summary`**). Stable **package-computed digests** for reporting (distinct from **`summary`**) are
implemented as **`lifecycle_event_to_digest_text`** / **`lifecycle_event_to_digest_record`** (see
**[SPEC_EVENT_DIGEST.md](SPEC_EVENT_DIGEST.md)**). **Fields and artifacts not suitable for external sharing** in that spec
also apply to digest lines built from payload strings.

**Canonical contract:** one JSON **object** per POST (the **event envelope**), sharing top-level keys (**`event_type`**,
**`occurred_at`**, **`event_id`**, **`correlation`**, **`summary`**, **`detail`**, optional **`schema_version`**). **`detail`**
holds the **event-specific** fields; **`event_type`** selects the expected **`detail`** shape. Run-category and
approval-category kinds are both **required** surface area for this spec (see **Event registry**).

### Backlog acceptance mapping (`df51dbf9`)

| Backlog criterion | Where addressed |
| ----------------- | --------------- |
| Documented schema covers **run** and **approval** lifecycle kinds | **Event registry** (three run + two approval `event_type` values) and matching **`detail`** tables |
| **Version** field or semantic strategy for payload evolution | **`schema_version`** in **Common envelope**; **Payload schema versioning** (below); independent of signing **v1** |
| **Breaking** vs **additive** changes for future releases | **Breaking vs additive changes** (below); **CHANGELOG.md** + package SemVer (below) |

| Topic | Where it lives |
| ----- | -------------- |
| **Integrity of the HTTP payload** (raw body + `Replayt-Signature`) | **[SPEC_WEBHOOK_SIGNATURE.md](SPEC_WEBHOOK_SIGNATURE.md)**, **[reference-documentation/REPLAYT_WEBHOOK_SIGNING.md](reference-documentation/REPLAYT_WEBHOOK_SIGNING.md)** |
| **Delivery retries, duplicate POSTs, `event_id` dedupe, idempotency store TTL** | **[SPEC_DELIVERY_IDEMPOTENCY.md](SPEC_DELIVERY_IDEMPOTENCY.md)** |
| **When events fire in the product** (workflow semantics) | **replayt** upstream documentation and runtime behavior — this repo **does not** redefine those moments |
| **Field names and examples below** | **Normative for integrators** who adopt this package’s documented payload contract; senders (automation or bridges) should emit compatible JSON when claiming compatibility with this spec |
| **Machine-readable JSON Schema (informative)** | **[schemas/lifecycle_webhook_payload-1-0.schema.json](schemas/lifecycle_webhook_payload-1-0.schema.json)** — mirrors the **`1.0`**-family shapes; if it disagrees with this file, **EVENTS.md** is authoritative |

Upstream **replayt** `0.4.25` does not publish a single canonical HTTP webhook JSON schema in the installed package.
This spec is a **consumer-side contract** maintained here: it **cross-references** replayt concepts (workflows, runs,
approvals) without requiring changes to **replayt** core. If upstream later publishes an official wire schema, align this
document and **CHANGELOG.md** with that authority.

## Verification before interpretation

Handlers must **verify** the request per **[SPEC_WEBHOOK_SIGNATURE.md](SPEC_WEBHOOK_SIGNATURE.md)** **before** parsing
JSON or branching on `event_type`. A forged body can contain arbitrary `event_type` strings; only verified payloads
should drive automation.

## Replayt concepts (informative)

The following names mirror **replayt**’s problem domain so operators can map payloads to docs and code they already
use. They are **not** a promise that the **replayt** Python API serializes these structures on the wire.

| Concept | Plain language |
| ------- | -------------- |
| **Workflow** | A defined automation graph or process being executed. |
| **Run** | One execution instance of a workflow from start through completion or failure. |
| **Approval** | A gate where execution pauses until a human or policy **approves** or **rejects** a pending step. |

Types such as **`RunResult`**, **`RunFailed`**, and **`ApprovalPending`** in the **replayt** library describe runtime
outcomes and control flow **inside** a runner; webhook payloads are **parallel notifications** for external systems and
may use **different** nesting but should preserve the **same identifiers** where possible (`run_id`, workflow identity).
**Automated boundary tests** **must** keep these imports working on the supported **replayt** floor—see
**[SPEC_REPLAYT_BOUNDARY_TESTS.md](SPEC_REPLAYT_BOUNDARY_TESTS.md)**.

## Common envelope (all events)

Every supported event is a single JSON **object** that **includes** the common fields below. Event-specific fields live
under **`detail`** (or top-level only when noted).

| Field | Type | Required | Description |
| ----- | ---- | -------- | ----------- |
| **`event_type`** | string | yes | Stable, namespaced identifier (see **Event registry**). Treat as an opaque enum in consumers; unknown values should be logged and ignored or dead-lettered per your policy. |
| **`occurred_at`** | string | yes | Timestamp when the sending system **emitted** the event, in **RFC 3339** form with explicit offset (prefer **UTC**, e.g. `2026-03-28T14:32:01Z`). Used for ordering and dashboards, **not** for MAC verification in v1. |
| **`event_id`** | string | yes | **Idempotency key** for this **logical lifecycle emission** (UUID string recommended). Compatible senders **SHOULD** reuse the **same** **`event_id`** and **same** serialized body for every HTTP attempt of that emission; each **new** emission **SHOULD** get a **new** **`event_id`**. Consumers **SHOULD** dedupe on **`event_id`** after verification; composite keys for legacy senders in **[SPEC_DELIVERY_IDEMPOTENCY.md](SPEC_DELIVERY_IDEMPOTENCY.md)**. |
| **`correlation`** | object | yes | Opaque identifiers safe to show in **dashboards** and support tickets (no secrets, no PII by default). See **Correlation object** below. |
| **`summary`** | string | yes | One-line, human-readable description suitable for **Slack** or **email** subject lines (UTF-8; keep under ~200 chars for UX). |
| **`detail`** | object | yes | Event-specific payload. Must not duplicate secret material; see **Prohibited content**. |
| **`schema_version`** | string | no | Payload schema version for this document, e.g. **`1.0`**. Omit if unknown; consumers should default to the behavior described for **`1.0`**. |

### Correlation object

| Field | Type | Required | Description |
| ----- | ---- | -------- | ----------- |
| **`run_id`** | string | yes | Stable identifier for this **run** within the sender’s universe. |
| **`workflow_id`** | string | yes | Stable identifier for the **workflow** definition or template. |
| **`approval_request_id`** | string | no | Present when the event pertains to a specific approval gate (pending or resolved). |
| **`deployment_id`** | string | no | Optional opaque id for the sending deployment or tenant slice (for routing in multi-tenant setups). |

All correlation values should be **opaque strings** (UUIDs, ULIDs, or stable slugs). Do **not** place API keys, bearer
tokens, or HMAC secrets in **`correlation`** or **`detail`**.

## Event registry

| `event_type` | Category | When it fires (informative) |
| ------------ | -------- | ---------------------------- |
| **`replayt.lifecycle.run.started`** | Run | A new run has been accepted and execution has begun. |
| **`replayt.lifecycle.run.completed`** | Run | A run finished **successfully** (terminal success). |
| **`replayt.lifecycle.run.failed`** | Run | A run ended in a **terminal failure** (error, timeout, etc.). |
| **`replayt.lifecycle.approval.pending`** | Approval | Execution is **blocked** waiting for approval on a step. |
| **`replayt.lifecycle.approval.resolved`** | Approval | A previously pending approval was **approved** or **rejected**. |

## `detail` shapes per `event_type`

### `replayt.lifecycle.run.started`

| Field | Type | Required | Description |
| ----- | ---- | -------- | ----------- |
| **`workflow_name`** | string | yes | Short display name for the workflow. |
| **`trigger`** | string | no | High-level trigger hint, e.g. `manual`, `schedule`, `webhook`. |

### `replayt.lifecycle.run.completed`

| Field | Type | Required | Description |
| ----- | ---- | -------- | ----------- |
| **`workflow_name`** | string | yes | Short display name for the workflow. |
| **`outcome`** | string | yes | Literal **`success`** for this event type. |
| **`duration_ms`** | integer | no | Wall-clock duration of the run in milliseconds, if available. |

### `replayt.lifecycle.run.failed`

| Field | Type | Required | Description |
| ----- | ---- | -------- | ----------- |
| **`workflow_name`** | string | yes | Short display name for the workflow. |
| **`error_code`** | string | yes | Stable machine-readable code (e.g. `RUNNER_TIMEOUT`, `STEP_FAILED`). |
| **`error_message`** | string | yes | Short operator-facing explanation; **not** a full stack trace or internal path dump. |

### `replayt.lifecycle.approval.pending`

| Field | Type | Required | Description |
| ----- | ---- | -------- | ----------- |
| **`step_name`** | string | yes | Label of the gated step. |
| **`policy_hint`** | string | no | Non-secret hint such as `security_review` or `two_person_rule` (no user emails in mandatory fields). |

`correlation.approval_request_id` **should** be set when this event is emitted.

### `replayt.lifecycle.approval.resolved`

| Field | Type | Required | Description |
| ----- | ---- | -------- | ----------- |
| **`step_name`** | string | yes | Label of the gated step. |
| **`decision`** | string | yes | **`approved`** or **`rejected`**. |
| **`resolved_by_role`** | string | no | Generic role label (e.g. `approver`, `admin`); avoid mandatory PII. |

`correlation.approval_request_id` **should** match the pending event for the same gate.

## Prohibited content

Payloads documented here must **not** include:

- Shared **secrets**, API keys, bearer tokens, or the **HMAC** signing secret
- **Full prompts**, full model transcripts, or large raw **LLM** outputs
- **Unredacted PII** in required fields (optional fields may exist upstream; this spec keeps required surfaces dashboard-safe)

Integrators may still apply **their own** redaction or allowlists after verification.

## Synthetic examples

All identifiers and text below are **fabricated** for documentation.

### `replayt.lifecycle.run.started`

```json
{
  "schema_version": "1.0",
  "event_type": "replayt.lifecycle.run.started",
  "occurred_at": "2026-03-28T14:30:00Z",
  "event_id": "7b2c4f8e-0d01-4a5b-9c3d-111111111111",
  "correlation": {
    "run_id": "run_01jqexampleabcd",
    "workflow_id": "wf_invoice_automation_v3",
    "deployment_id": "dep_staging_west"
  },
  "summary": "Run started: Invoice automation v3",
  "detail": {
    "workflow_name": "Invoice automation v3",
    "trigger": "schedule"
  }
}
```

### `replayt.lifecycle.run.completed`

```json
{
  "schema_version": "1.0",
  "event_type": "replayt.lifecycle.run.completed",
  "occurred_at": "2026-03-28T14:31:12Z",
  "event_id": "8c3d5g9f-1e12-5b6c-0d4e-222222222222",
  "correlation": {
    "run_id": "run_01jqexampleabcd",
    "workflow_id": "wf_invoice_automation_v3",
    "deployment_id": "dep_staging_west"
  },
  "summary": "Run completed: Invoice automation v3 (success)",
  "detail": {
    "workflow_name": "Invoice automation v3",
    "outcome": "success",
    "duration_ms": 72000
  }
}
```

### `replayt.lifecycle.run.failed`

```json
{
  "schema_version": "1.0",
  "event_type": "replayt.lifecycle.run.failed",
  "occurred_at": "2026-03-28T14:31:05Z",
  "event_id": "9d4e6h0g-2f23-6c7d-1e5f-333333333333",
  "correlation": {
    "run_id": "run_01jqexamplefail1",
    "workflow_id": "wf_invoice_automation_v3",
    "deployment_id": "dep_staging_west"
  },
  "summary": "Run failed: Invoice automation v3 — upstream API timeout",
  "detail": {
    "workflow_name": "Invoice automation v3",
    "error_code": "STEP_FAILED",
    "error_message": "Upstream payment API did not respond within the configured timeout."
  }
}
```

### `replayt.lifecycle.approval.pending`

```json
{
  "schema_version": "1.0",
  "event_type": "replayt.lifecycle.approval.pending",
  "occurred_at": "2026-03-28T15:00:00Z",
  "event_id": "0e5f7i1h-3g34-7d8e-2f6g-444444444444",
  "correlation": {
    "run_id": "run_01jqapprovaldemo",
    "workflow_id": "wf_release_train",
    "approval_request_id": "apr_01jqexamplegate",
    "deployment_id": "dep_prod_eu"
  },
  "summary": "Approval pending: Release train — production deploy step",
  "detail": {
    "step_name": "production_deploy",
    "policy_hint": "change_advisory_board"
  }
}
```

### `replayt.lifecycle.approval.resolved`

```json
{
  "schema_version": "1.0",
  "event_type": "replayt.lifecycle.approval.resolved",
  "occurred_at": "2026-03-28T15:45:22Z",
  "event_id": "1f6g8j2i-4h45-8e9f-3g7h-555555555555",
  "correlation": {
    "run_id": "run_01jqapprovaldemo",
    "workflow_id": "wf_release_train",
    "approval_request_id": "apr_01jqexamplegate",
    "deployment_id": "dep_prod_eu"
  },
  "summary": "Approval approved: Release train — production deploy step",
  "detail": {
    "step_name": "production_deploy",
    "decision": "approved",
    "resolved_by_role": "approver"
  }
}
```

## Upstream documentation (semantics vs wire JSON)

- **Product / library semantics:** Integrators should consult **[replayt on PyPI](https://pypi.org/project/replayt/)**
  (project description, release history, and any **Homepage** / **Source** links on that page) for what workflows,
  runs, and approvals mean in replayt itself.
- **HTTP lifecycle webhook JSON:** As of **replayt `0.4.25`**, the installed distribution does not ship a single
  canonical webhook body schema. For consumers of **this** package, the **normative** field contract for verified POST
  bodies is **this document** together with the **typed** Python surface in **`replayt_lifecycle_webhooks.events`**.
  If upstream later publishes an official wire schema, maintainers should align **EVENTS.md**, models, fixtures, and
  **CHANGELOG.md** with that authority.

## Payload schema versioning and migration

### `schema_version` on the wire

- **Field:** optional string on the **envelope** (see **Common envelope**). It labels the **JSON field contract** in
  this document, **not** the HMAC signing scheme (**[SPEC_WEBHOOK_SIGNATURE.md](SPEC_WEBHOOK_SIGNATURE.md)** **v1** is
  orthogonal: signing operates on **raw bytes** regardless of `schema_version`).
- **Format:** **`MAJOR.MINOR`**, each segment a non-negative integer (e.g. **`1.0`**, **`1.1`**, **`2.0`**). This spec
  does **not** use a third **PATCH** segment on the wire unless a future revision introduces one; editorial doc fixes
  alone do not imply a new payload version.
- **Initial family:** **`1.0`**. If **`schema_version`** is **omitted**, consumers of this package SHOULD treat the
  payload as the **`1.0`** behavior described here until **EVENTS.md** defines a different default for a newer era.

### Semver-style rules for payload evolution

- **MAJOR** bump (e.g. **`1.x` → `2.0`**): **breaking** JSON changes (see **Breaking vs additive changes**). Integrators
  MUST upgrade parsers, reject unknown majors, or dead-letter per policy—**no** silent partial acceptance.
- **MINOR** bump (e.g. **`1.0` → `1.1`**): **additive** only—new **optional** fields, new **`event_type`** registry rows,
  or documentation that tightens guidance **without** removing or retyping existing documented fields. Valid **`1.0`**
  payloads remain valid inputs for a **`1.1`** consumer when new fields are absent.

### Relationship to **`replayt-lifecycle-webhooks`** (package SemVer)

Public API and contracts follow [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html) as declared in
**CHANGELOG.md**. Maintainers SHOULD align bumps as follows (guidance, not a substitute for judgment):

| Payload / parser change | Typical package bump |
| ----------------------- | --------------------- |
| **Breaking** wire or **breaking** strictness in **`parse_lifecycle_webhook_event`** | **MAJOR** |
| **Additive** wire fields or new **`event_type`** support in models | **MINOR** |
| Doc-only clarification, same acceptance behavior | **PATCH** |

### Python implementation notes

The **`replayt_lifecycle_webhooks.events`** module MUST keep supported payload / **`schema_version`** expectations
visible in its module docstring and/or model field descriptions, per **T5** in acceptance criteria below.

## Breaking vs additive changes

Use this table when extending the contract or reviewing sender/receiver upgrades:

| Class | Examples (non-exhaustive) | Maintainer action |
| ----- | ------------------------- | ------------------- |
| **Breaking** | Removing a documented field; renaming an **`event_type`** string; changing a field’s JSON type; tightening **required** on **`detail`** or **`correlation`**; redefining the meaning of an existing value | Bump payload **`schema_version` MAJOR**; update **EVENTS.md**, **[schemas/lifecycle_webhook_payload-1-0.schema.json](schemas/lifecycle_webhook_payload-1-0.schema.json)** (or add a new schema file for the new major), Pydantic models, fixtures; **CHANGELOG.md** **Unreleased** with **migration** notes; plan package **MAJOR** if strict parsing rejects old payloads |
| **Additive** | New optional envelope or **`detail`** field; new **`event_type`** with its own **`detail`** shape; new optional **`correlation`** key | Bump payload **`schema_version` MINOR** (document in **CHANGELOG**); extend **Event registry**, examples, and schema; package **MINOR** when new types or parse paths ship |

**Integrator policy:** Unknown **`schema_version`** **MAJOR** (e.g. receiver knows only **`1.*`** and sees **`2.0`**) should be **rejected** or **quarantined** after verification—not partially parsed.

## Machine-readable JSON Schema (informative)

**[schemas/lifecycle_webhook_payload-1-0.schema.json](schemas/lifecycle_webhook_payload-1-0.schema.json)** is a
**Draft-07** JSON Schema **`oneOf`** over the six documented **`event_type`** values. It is intended for **non-Python**
tooling (OpenAPI generators, validators in other languages). **Normative** field rules remain the prose tables and
examples in **this document**; when the schema drifts, fix the schema or regenerate it from **EVENTS.md**.

## Typed Python representation (normative package API)

This section refines backlog **Define typed lifecycle event payloads (run + approval)**
(`0b929c17-525d-4ec7-b13c-a7b4f3f8ca10`): integrators get **editor assistance** and **runtime validation** instead of
ad hoc **`dict`** access after signature verification.

| Topic | Normative choice for this repository |
| ----- | ------------------------------------- |
| **Import surface** | **`replayt_lifecycle_webhooks.events`**: **`parse_lifecycle_webhook_event`**, **`LIFECYCLE_WEBHOOK_EVENT_TYPES`**, envelope and **`detail`** model types per **`event_type`**. |
| **Implementation technology** | **Pydantic v2** models (**`pydantic>=2.6.0`** per **`pyproject.toml`**). **TypedDict**-only or stdlib **dataclasses** are out of scope unless a future ADR replaces this row. |
| **Discrimination** | Union of event models discriminated by literal **`event_type`** (Pydantic discriminated union). |
| **Unknown `event_type`** | MUST fail validation (no silent default or partial parse). |
| **Minimum `event_type` coverage** | At least **two** distinct values with distinct **`detail`** shapes, including **one run-category** and **one approval-category** row from the **Event registry**. Claiming full compliance with **E1** requires covering **every** registry row with typed models and fixtures. |
| **Call order** | Call **`parse_lifecycle_webhook_event`** only **after** **`verify_lifecycle_webhook_signature`** (or equivalent) succeeds per **[SPEC_WEBHOOK_SIGNATURE.md](SPEC_WEBHOOK_SIGNATURE.md)**. |

## Acceptance criteria (for Builder / Tester)

Use with Spec gate and implementation phases. **JSON shape** rows **E1–E6**; **typed Python** rows **T1–T7**.

| # | Criterion | Verification |
|---|-----------|--------------|
| E1 | Docs list **every** `event_type` in the registry with field tables and **synthetic** JSON examples. | Review **this file**; examples must not contain real tokens or secrets. |
| E2 | Each event includes **`event_type`**, **`occurred_at`**, **`event_id`**, **`correlation`**, **`summary`**, and **`detail`** per the common envelope. | Schema review + sample payloads in tests or fixtures (phase 3+). |
| E3 | **`correlation`** carries **`run_id`** and **`workflow_id`**; approval events use **`approval_request_id`** when applicable. | Review payloads / tests. |
| E4 | **`summary`** is suitable for notifications (short, human-readable). | Review examples and any golden fixtures. |
| E5 | Spec states **verification-before-JSON** and **prohibited content** (no secrets, no full prompts in required fields). | Review **this file** and **SPEC_WEBHOOK_SIGNATURE.md**. |
| E6 | **replayt** core need not change for consumers to adopt this contract; drift from upstream product docs is called out in **CHANGELOG.md** when discovered. | Maintainer review alongside **SPEC_REPLAYT_DEPENDENCY.md**. |
| E7 | **`event_id`** semantics align with **[SPEC_DELIVERY_IDEMPOTENCY.md](SPEC_DELIVERY_IDEMPOTENCY.md)** (stable per logical emission, dedupe, TTL guidance). | Doc review; **pytest** **I3** / **I4** in **`tests/test_lifecycle_events.py`**. |

### Typed payloads (`0b929c17`)

| # | Criterion | Verification |
|---|-----------|--------------|
| T1 | Public **`parse_lifecycle_webhook_event`** validates a **`dict`**-like JSON object and returns a typed union discriminated by **`event_type`**. | Unit tests + **`__all__`** / import review. |
| T2 | Exported types cover at minimum **one run** and **one approval** **`event_type`**; **E1** compliance requires **all** registry rows. | Model/module review + fixtures. |
| T3 | **JSON fixtures** under **`tests/fixtures/events/`** (one file per documented **`event_type`** when **E1** is satisfied); tests parse each fixture through **`parse_lifecycle_webhook_event`** without error. | **pytest** |
| T4 | Invalid **`detail`** for a known **`event_type`**, unknown **`event_type`**, unsupported **`schema_version`** when present, or missing required **envelope** / **`correlation`** fields produce **`pydantic.ValidationError`** (or documented equivalent); covered by tests. | **pytest** |
| T5 | Supported payload / **`schema_version`** expectations are visible in **`events`** module docstrings and/or model fields. | Doc review |
| T6 | **[README.md](../README.md)** links to **replayt** upstream for **semantics** and states that **wire JSON** is normative in **EVENTS.md** until upstream publishes an official HTTP schema. | Doc review |
| T7 | User-visible parsing or shape changes appear under **CHANGELOG.md** **Unreleased** (or release section) with migration notes when shapes change. | Release hygiene |

## Related docs

- **[SPEC_DELIVERY_IDEMPOTENCY.md](SPEC_DELIVERY_IDEMPOTENCY.md)** — at-least-once expectations, **`event_id`** dedupe rules, consumer idempotency store TTL guidance.
- **[SPEC_AUTOMATED_TESTS.md](SPEC_AUTOMATED_TESTS.md)** — CI entrypoint; suite must exercise **`parse_lifecycle_webhook_event`**
  per **T3–T5** (not placeholder smoke tests).
- **[SPEC_WEBHOOK_SIGNATURE.md](SPEC_WEBHOOK_SIGNATURE.md)** — verify the raw body before parsing JSON.
- **[SPEC_MINIMAL_HTTP_HANDLER.md](SPEC_MINIMAL_HTTP_HANDLER.md)** — optional handler that verifies then parses JSON.
- **[MISSION.md](MISSION.md)** — run vs approval scope and consumer responsibilities.
- **[SPEC_REPLAYT_DEPENDENCY.md](SPEC_REPLAYT_DEPENDENCY.md)** — **replayt** version floor.
- **[schemas/lifecycle_webhook_payload-1-0.schema.json](schemas/lifecycle_webhook_payload-1-0.schema.json)** — informative Draft-07 schema.
