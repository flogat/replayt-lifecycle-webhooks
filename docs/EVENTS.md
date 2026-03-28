# Spec: lifecycle webhook JSON payload shapes (run and approval)

**Backlog:** Map replayt run and approval events to webhook payload shapes (`076a56b7-afd9-4778-b46a-4dc8875a431f`).  
**Audience:** Spec gate (2b), Builder (3), Tester (4), integrators, operators.

## Purpose and normative status

This document defines a **recommended JSON object model** for HTTP POST bodies that carry **run** and **approval**
lifecycle notifications, after **`Replayt-Signature`** verification succeeds. It exists so downstream systems get
**predictable fields** for routing, idempotency, dashboards, and **human-readable digests** (Slack, email, PM tools).

| Topic | Where it lives |
| ----- | -------------- |
| **Integrity of the HTTP payload** (raw body + `Replayt-Signature`) | **[SPEC_WEBHOOK_SIGNATURE.md](SPEC_WEBHOOK_SIGNATURE.md)**, **[reference-documentation/REPLAYT_WEBHOOK_SIGNING.md](reference-documentation/REPLAYT_WEBHOOK_SIGNING.md)** |
| **When events fire in the product** (workflow semantics) | **replayt** upstream documentation and runtime behavior — this repo **does not** redefine those moments |
| **Field names and examples below** | **Normative for integrators** who adopt this package’s documented payload contract; senders (automation or bridges) should emit compatible JSON when claiming compatibility with this spec |

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

## Common envelope (all events)

Every supported event is a single JSON **object** that **includes** the common fields below. Event-specific fields live
under **`detail`** (or top-level only when noted).

| Field | Type | Required | Description |
| ----- | ---- | -------- | ----------- |
| **`event_type`** | string | yes | Stable, namespaced identifier (see **Event registry**). Treat as an opaque enum in consumers; unknown values should be logged and ignored or dead-lettered per your policy. |
| **`occurred_at`** | string | yes | Timestamp when the sending system **emitted** the event, in **RFC 3339** form with explicit offset (prefer **UTC**, e.g. `2026-03-28T14:32:01Z`). Used for ordering and dashboards, **not** for MAC verification in v1. |
| **`event_id`** | string | yes | Unique id for **this delivery** (UUID string recommended). Use for idempotency and deduplication keys in workers. |
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

## Acceptance criteria (for Builder / Tester)

Use with Spec gate and implementation phases.

| # | Criterion | Verification |
|---|-----------|--------------|
| E1 | Docs list **every** `event_type` in the registry with field tables and **synthetic** JSON examples. | Review **this file**; examples must not contain real tokens or secrets. |
| E2 | Each event includes **`event_type`**, **`occurred_at`**, **`event_id`**, **`correlation`**, **`summary`**, and **`detail`** per the common envelope. | Schema review + sample payloads in tests or fixtures (phase 3+). |
| E3 | **`correlation`** carries **`run_id`** and **`workflow_id`**; approval events use **`approval_request_id`** when applicable. | Review payloads / tests. |
| E4 | **`summary`** is suitable for notifications (short, human-readable). | Review examples and any golden fixtures. |
| E5 | Spec states **verification-before-JSON** and **prohibited content** (no secrets, no full prompts in required fields). | Review **this file** and **SPEC_WEBHOOK_SIGNATURE.md**. |
| E6 | **replayt** core need not change for consumers to adopt this contract; drift from upstream product docs is called out in **CHANGELOG.md** when discovered. | Maintainer review alongside **SPEC_REPLAYT_DEPENDENCY.md**. |

## Related docs

- **[SPEC_WEBHOOK_SIGNATURE.md](SPEC_WEBHOOK_SIGNATURE.md)** — verify the raw body before parsing JSON.
- **[SPEC_MINIMAL_HTTP_HANDLER.md](SPEC_MINIMAL_HTTP_HANDLER.md)** — optional handler that verifies then parses JSON.
- **[MISSION.md](MISSION.md)** — run vs approval scope and consumer responsibilities.
- **[SPEC_REPLAYT_DEPENDENCY.md](SPEC_REPLAYT_DEPENDENCY.md)** — **replayt** version floor.
