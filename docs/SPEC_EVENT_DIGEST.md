# Spec: PM- and support-friendly lifecycle event digest

**Backlog:** Publish PM- and support-friendly event digest format (`069e0240-54c5-44a9-bba3-ad0a80a52c60`).

**Audience:** Spec gate (2b), Builder (3), Tester (4), integrators, PM/support stakeholders.

## Purpose and normative status

This document defines a **stable, deterministic** **text digest** and an optional **JSON-serializable record** derived from a
**typed** lifecycle webhook event (**`LifecycleWebhookEvent`** union in **`replayt_lifecycle_webhooks.events`**) **after**
signature verification and successful parsing per **[EVENTS.md](EVENTS.md)**.

It answers: *“What short, consistent string or structured blob can we put in tickets, email, or dashboards without
re-exposing raw webhook bytes or crypto material?”*

**Non-goals:**

- Replacing or redefining the wire **`summary`** field on the envelope (**[EVENTS.md](EVENTS.md)** **Common envelope**).
  That string is **sender-authored**; the digest defined **here** is **receiver-computed** from the typed model and
  follows **fixed English templates** in this spec.
- Adding a new **required** top-level wire field (for example **`digest`**) to HTTP JSON bodies. Doing so would be an
  **EVENTS.md** / payload **MINOR** (or **MAJOR**) change with **CHANGELOG.md** and schema updates. This backlog’s
  **default delivery** is a **library function** (and optional record helper), not a change to the POST body contract.

## Relationship to **`summary`** vs digest

| Artifact | Who controls it | Use |
| -------- | ---------------- | --- |
| **`summary`** (envelope) | Sender | Human-readable hint on the wire; may vary by deployment or locale. |
| **Digest text** (this spec) | This package’s documented formatter | Stable English lines for reports and automation **given the same parsed model**. |
| **Digest record** (optional JSON) | Same | Machine columns / ETL without parsing free-form **`summary`**. |

Integrators may show **`summary`**, digest text, both, or neither depending on audience and redaction policy.

## Input and call order

1. Verify the HTTP body per **[SPEC_WEBHOOK_SIGNATURE.md](SPEC_WEBHOOK_SIGNATURE.md)**.
2. Parse JSON and validate with **`parse_lifecycle_webhook_event`** (**[EVENTS.md](EVENTS.md)** **T1**).
3. Pass the resulting **`LifecycleWebhookEvent`** instance to the digest helpers (when implemented).

**Do not** compute digests from unverified or unparsed **`dict`** data in security-sensitive paths unless you have an
explicit, reviewed reason (for example offline fixture replay in tests).

## Determinism and locale

**DG0 (normative):**

- **Locale:** Fixed **ASCII-safe English** labels and punctuation as specified below. Implementations **must not** depend
  on **`locale`** or system timezone for formatting.
- **Text digest:** Output is a single **`str`**. Lines are separated by **exactly one** **`\n`** (**LF**). The final line
  **must not** be followed by a trailing **`\\n`** unless a future spec revision explicitly changes this rule (tests
  should lock the chosen convention).
- **Optional fields:** If a value is **`None`** or missing on the model, **omit** the entire corresponding line from the
  **text** digest (do not emit empty values or placeholder words).
- **Strings from the payload** (**`occurred_at`**, **`workflow_name`**, **`error_message`**, etc.) are copied **verbatim**
  from the model (no case folding, no trimming) so **byte-identical** inputs produce **byte-identical** digests.
- **JSON record:** If implemented, **`json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=True)`** on
  the documented key set **must** be identical for two equal models. (Tests may assert on either the **dict** equality
  or these canonical bytes.)

## Text digest: line templates

Each **`event_type`** uses a **fixed first line** (**`Digest:`** …) followed by **context lines** in the **exact order**
listed. Only lines whose values are present (non-**`None`**) are emitted, except the **`Digest:`** line and lines marked
**always**.

**Shared lines** (after the initial **`Digest:`** line, when values exist):

| Line prefix | Source | When |
| ----------- | ------ | ---- |
| **`Workflow:`** | **`detail.workflow_name`** | Run events only (all run **`detail`** types expose **`workflow_name`**). |
| **`Step:`** | **`detail.step_name`** | Approval events only. |
| **`Run:`** | **`correlation.run_id`** | Always for all six registry types. |
| **`Workflow ID:`** | **`correlation.workflow_id`** | Always. |
| **`When:`** | **`occurred_at`** | Always. |
| **`Event ID:`** | **`event_id`** | Always (support correlation; integrators may strip for external channels). |
| **`Deployment:`** | **`correlation.deployment_id`** | If not **`None`**. |
| **`Approval request:`** | **`correlation.approval_request_id`** | If not **`None`**. |

### `replayt.lifecycle.run.started`

1. **`Digest: Run started`**
2. **`Workflow:`** …
3. **`Run:`** …
4. **`Workflow ID:`** …
5. **`When:`** …
6. **`Event ID:`** …
7. **`Deployment:`** … (optional)
8. **`Approval request:`** … (optional; normally absent)
9. **`Trigger:`** **`detail.trigger`** (optional)

### `replayt.lifecycle.run.completed`

1. **`Digest: Run completed (success)`**
2. **`Workflow:`** …
3. **`Run:`** …
4. **`Workflow ID:`** …
5. **`When:`** …
6. **`Event ID:`** …
7. **`Deployment:`** … (optional)
8. **`Approval request:`** … (optional)
9. **`Duration (ms):`** **`detail.duration_ms`** as decimal integer string (optional)

### `replayt.lifecycle.run.failed`

1. **`Digest: Run failed`**
2. **`Workflow:`** …
3. **`Run:`** …
4. **`Workflow ID:`** …
5. **`When:`** …
6. **`Event ID:`** …
7. **`Deployment:`** … (optional)
8. **`Approval request:`** … (optional)
9. **`Error code:`** **`detail.error_code`**
10. **`Error:`** **`detail.error_message`**

### `replayt.lifecycle.approval.pending`

1. **`Digest: Approval requested`**
2. **`Step:`** …
3. **`Run:`** …
4. **`Workflow ID:`** …
5. **`When:`** …
6. **`Event ID:`** …
7. **`Deployment:`** … (optional)
8. **`Approval request:`** … (optional but **should** be present for this moment per **EVENTS.md**)
9. **`Policy hint:`** **`detail.policy_hint`** (optional)

### `replayt.lifecycle.approval.resolved`

1. **`Digest: Approval approved`** if **`detail.decision == "approved"`**; **`Digest: Approval rejected`** if **`"rejected"`**.
2. **`Step:`** …
3. **`Run:`** …
4. **`Workflow ID:`** …
5. **`When:`** …
6. **`Event ID:`** …
7. **`Deployment:`** … (optional)
8. **`Approval request:`** … (optional but **should** be present)
9. **`Resolved by role:`** **`detail.resolved_by_role`** (optional)

## Optional JSON digest record

When implemented, **`lifecycle_event_to_digest_record`** (name indicative; final name in **SPEC_PUBLIC_API.md** when
exported) **must** return a plain `dict` with **only** JSON-friendly scalars (`str`, `int`, `bool`, or JSON **`null`**) and
the following **minimum keys** (additional keys are **not allowed** unless **EVENTS.md** / this spec is bumped):

| Key | Value |
| --- | ----- |
| **`schema_version`** | **`"digest/1"`** — labels this record shape for consumers. |
| **`event_type`** | Same string as **`event.event_type`**. |
| **`digest_kind`** | One of **`run_started`**, **`run_completed`**, **`run_failed`**, **`approval_pending`**, **`approval_resolved`**. |
| **`occurred_at`** | Envelope **`occurred_at`**. |
| **`event_id`** | Envelope **`event_id`**. |
| **`run_id`** | **`correlation.run_id`**. |
| **`workflow_id`** | **`correlation.workflow_id`**. |

**Optional keys** (include when the model has a non-**`None`** value; omit the key entirely when absent):

- **`deployment_id`**, **`approval_request_id`**
- Run: **`workflow_name`**, **`trigger`**, **`duration_ms`**, **`outcome`** (literal **`success`** for completed), **`error_code`**, **`error_message`**
- Approval: **`step_name`**, **`policy_hint`**, **`decision`** (**`approved` | `rejected`**), **`resolved_by_role`**

**Sorting:** Canonical JSON tests use **`sort_keys=True`** as in **DG0**.

## Worked examples (synthetic)

The JSON below matches the fabrications in **[EVENTS.md](EVENTS.md)** **Synthetic examples**. **Normative expected digest
text** for Builder **golden tests** is the string shown in each **“Expected digest text”** fenced block.

### Run completed (`replayt.lifecycle.run.completed`)

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

**Expected digest text:**

```text
Digest: Run completed (success)
Workflow: Invoice automation v3
Run: run_01jqexampleabcd
Workflow ID: wf_invoice_automation_v3
When: 2026-03-28T14:31:12Z
Event ID: 8c3d5g9f-1e12-5b6c-0d4e-222222222222
Deployment: dep_staging_west
Duration (ms): 72000
```

### Approval resolved — approved (`replayt.lifecycle.approval.resolved`)

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

**Expected digest text:**

```text
Digest: Approval approved
Step: production_deploy
Run: run_01jqapprovaldemo
Workflow ID: wf_release_train
When: 2026-03-28T15:45:22Z
Event ID: 1f6g8j2i-4h45-8e9f-3g7h-555555555555
Deployment: dep_prod_eu
Approval request: apr_01jqexamplegate
Resolved by role: approver
```

### Run failed (`replayt.lifecycle.run.failed`) — third lifecycle example

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

**Expected digest text:**

```text
Digest: Run failed
Workflow: Invoice automation v3
Run: run_01jqexamplefail1
Workflow ID: wf_invoice_automation_v3
When: 2026-03-28T14:31:05Z
Event ID: 9d4e6h0g-2f23-6c7d-1e5f-333333333333
Deployment: dep_staging_west
Error code: STEP_FAILED
Error: Upstream payment API did not respond within the configured timeout.
```

## Fields and artifacts **not** suitable for external sharing

Digest output is **safer** than dumping raw HTTP, but integrators remain responsible for **policy** and **redaction**.

**Do not** publish or ship to untrusted parties without review:

- **Raw HTTP body bytes**, full JSON webhook payloads, or **structured logs** that contain them.
- **`Replayt-Signature`**, computed MACs, or the **HMAC secret** (see **[SPEC_WEBHOOK_SIGNATURE.md](SPEC_WEBHOOK_SIGNATURE.md)**).
- **Verbose failure text** (**`error_message`**, **`summary`**, or digests derived from them) if it may contain **internal
  hostnames**, file paths, **secrets**, or **customer PII** slipped in by a sender—**EVENTS.md** discourages this in
  required fields, but **malicious or misconfigured senders** can still emit unsafe strings **after** verification.
- **Correlation identifiers** (**`run_id`**, **`event_id`**, **`approval_request_id`**, **`deployment_id`**) when your
  support policy treats opaque ids as **tenant-identifying** or **competitive** information in a given channel.

**PM/support-safe default:** Prefer the **digest text** (or a **redacted** subset of the **digest record**) over raw JSON.
When in doubt, strip **`Event ID:`** / **`event_id`** for customer-visible copy while retaining it in internal ticketing.

## Implementation shape (Builder)

**Preferred public API** (names indicative until **SPEC_PUBLIC_API.md** is updated in phase **3**):

- **`lifecycle_event_to_digest_text(event: LifecycleWebhookEvent) -> str`**
- **`lifecycle_event_to_digest_record(event: LifecycleWebhookEvent) -> dict[str, Any]`** (optional but recommended for
  JSON pipelines)

Placement options documented here for Builder alignment:

- **`replayt_lifecycle_webhooks.digest`** module (narrow surface), re-exported from the package root **`__all__`** when
  stable; **or**
- Adjacent helpers under **`replayt_lifecycle_webhooks.events`** if maintainers prefer a single import path (must still
  update **SPEC_PUBLIC_API.md** and root **`__all__`** explicitly).

**Stub phase:** A **`NotImplementedError`** stub is **not** sufficient for “done” on this backlog—ship **working**
formatters or defer the backlog. If a **skeleton** is needed temporarily, it **must** be clearly marked **private**
(**`_…`**) and **omitted** from **`__all__`** until behavior matches this spec.

## Acceptance criteria (Builder / Tester)

| # | Criterion | Verification |
|---|-----------|--------------|
| **DG1** | Documented **text** line rules cover **all six** **`event_type`** values in **[EVENTS.md](EVENTS.md)** **Event registry**. | Review **this spec**; **pytest** golden strings per type. |
| **DG2** | At least **two** worked **text** examples from distinct lifecycle **categories** (**run** and **approval**) match the blocks in **Worked examples** above **exactly**. | **pytest** (parse fixture → digest → `==` expected multiline string) |
| **DG3** | **Determinism:** for a fixed parsed model, digest text and canonical JSON record bytes are stable across runs and platforms (**DG0**). | **pytest** |
| **DG4** | Optional fields (**`trigger`**, **`duration_ms`**, **`policy_hint`**, **`resolved_by_role`**, **`deployment_id`**, **`approval_request_id`**) **omit** lines / keys when absent. | **pytest** cases or parametrized fixtures |
| **DG5** | **`approval.resolved`** uses **`Digest: Approval approved`** vs **`Digest: Approval rejected`** per **`detail.decision`**. | **pytest** |
| **DG6** | **This section** (**Fields and artifacts not suitable for external sharing**) is reflected in integrator docs (**README** or **EVENTS.md** pointer) so PM/support readers see the warning without reading crypto specs. | Doc review |

## Related docs

- **[EVENTS.md](EVENTS.md)** — wire envelope, **`summary`**, **`detail`** shapes, synthetic JSON fixtures.
- **[SPEC_WEBHOOK_SIGNATURE.md](SPEC_WEBHOOK_SIGNATURE.md)** — verify before parse.
- **[SPEC_STRUCTURED_LOGGING_REDACTION.md](SPEC_STRUCTURED_LOGGING_REDACTION.md)** — logging redaction vs human-facing digest.
- **[SPEC_PUBLIC_API.md](SPEC_PUBLIC_API.md)** — export surface when functions ship.
- **[SPEC_AUTOMATED_TESTS.md](SPEC_AUTOMATED_TESTS.md)** — **DG1–DG6** checklist row **Backlog `069e0240`**.
