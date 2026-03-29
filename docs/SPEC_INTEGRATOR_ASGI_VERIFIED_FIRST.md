# Spec: integrator recipe — ASGI (FastAPI / Starlette) verified-first handler

**Backlog:** Integrator recipe: FastAPI / Starlette verified-first handler  
**Workflow id:** `c631fe3f-8a66-4a9d-a900-bab855860c7b` (phase **2** spec refinement; Builder authors the prose and code blocks in phase **3**).

**Audience:** Spec gate (2b), Builder (3), Tester (4), integrators using **FastAPI**, **Starlette**, or other **ASGI** stacks.

## Purpose and normative status

This document is the **contract** for a **copy-paste friendly** integrator guide that shows how to obtain **raw request
body bytes** and run **replayt-lifecycle-webhooks** verification **before** JSON parsing in **ASGI** frameworks.

**Normative for Builder:** When this backlog is in scope, the repository **must** ship the **deliverable** in **§
Deliverable** and satisfy **§ Acceptance checklist (AF1–AF7)**. **§ Copy-paste examples (normative shape)** describes what
those examples **must** demonstrate; Builder fills in complete, runnable snippets (placeholders only for secrets).

**Non-goals:** This spec does **not** add **FastAPI** or **Starlette** as **mandatory** dependencies of the
distribution (**`pyproject.toml`**). Examples **assume** integrators already depend on their chosen framework. This
spec does **not** replace **SPEC_WEBHOOK_SIGNATURE** or **SPEC_MINIMAL_HTTP_HANDLER**—it **bridges** them for ASGI
users.

## Problem and context

**Raw body discipline** is a common failure mode: many framework tutorials show **`request.json()`**, **`Body(...)`**,
or Pydantic-typed bodies **before** integrity checks. That consumes or reformulates the stream so the **HMAC** over the
original octets no longer matches. Integrators need a **known-good** pattern aligned with **[SPEC_WEBHOOK_SIGNATURE.md](SPEC_WEBHOOK_SIGNATURE.md)**
(**verification procedure**) and, when using the optional glue API, **[SPEC_MINIMAL_HTTP_HANDLER.md](SPEC_MINIMAL_HTTP_HANDLER.md)**.

## Scope

- **Documentation only** in **`v0.x`** unless a **tiny shared helper** is justified; any new **public** symbol **must**
  be listed in **[SPEC_PUBLIC_API.md](SPEC_PUBLIC_API.md)**, exported from the package **`__all__`**, covered by tests in
  a later phase, and noted in **`CHANGELOG.md`**.
- Examples **must** use **only** **supported** imports from **`replayt_lifecycle_webhooks`** (package root and/or
  **`replayt_lifecycle_webhooks.events`**) per **SPEC_PUBLIC_API**—**no** deep imports from internal modules.

## Deliverable

1. **Primary guide file (this document):** **`docs/SPEC_INTEGRATOR_ASGI_VERIFIED_FIRST.md`** — after phase **3**, it
   **must** contain **at least one** complete minimal example under **§ Copy-paste examples** (see below) plus the
   checklist and cross-links in this spec. **Maintainers may** split a long appendix later; until then, **one file**
   stays the canonical URL.
2. **README operator cross-link:** Root **`README.md`**, section **`## Verifying webhook signatures`**, **must** include a
   markdown link to **`docs/SPEC_INTEGRATOR_ASGI_VERIFIED_FIRST.md`** (path as written from the repository root). Normative
   placement and posture: **[SPEC_README_OPERATOR_SECTIONS.md](SPEC_README_OPERATOR_SECTIONS.md)** (**§ Backlog acceptance
   mapping (`c631fe3f`)**).

## Supported integration patterns (choose one per example)

Builder **must** document **at least one** of the following; documenting **both** is **recommended** so integrators can
pick the least surprising path for their app.

### Pattern A — Primitive: `verify_lifecycle_webhook_signature`

1. Read **`bytes`** from the ASGI request **before** any JSON decode (**FastAPI:** `await request.body()` on
   **`Request`**; **Starlette:** same **`Request`** API).
2. Read **`Replayt-Signature`** (use **`LIFECYCLE_WEBHOOK_SIGNATURE_HEADER`** from the package for the header name).
3. Call **`verify_lifecycle_webhook_signature(secret=…, body=…, signature=…)`**.
4. On success, parse JSON (for example **`json.loads`** then **`parse_lifecycle_webhook_event`** for typed lifecycle
   events).

### Pattern B — Optional glue: `handle_lifecycle_webhook_post`

1. Collect **`method`** (**`POST`**), **raw body `bytes`**, and a **header mapping** (case-insensitive names; see
   **SPEC_MINIMAL_HTTP_HANDLER**).
2. Call **`handle_lifecycle_webhook_post`** with keyword-only arguments; map **`LifecycleWebhookHttpResult`** to the
   ASGI response (status, headers, body).

**Ordering invariant (both patterns):** Verification **must** run on the **exact** wire bytes; the guide **must** call
out that **`await request.json()`**, **`Body`**, or Pydantic **`BaseModel` body parameters** that run **before** reading
raw bytes are **incorrect** for this use case.

## Error mapping and hygiene (normative)

Examples **must** demonstrate mapping signature failures to HTTP **401** / **403** consistent with
**[SPEC_WEBHOOK_SIGNATURE.md](SPEC_WEBHOOK_SIGNATURE.md)** (**HTTP responses and logging**) and
**[SPEC_MINIMAL_HTTP_HANDLER.md](SPEC_MINIMAL_HTTP_HANDLER.md)** when using **`handle_lifecycle_webhook_post`**:

| Failure class | Typical HTTP | Notes for examples |
| ------------- | ------------ | ------------------ |
| Missing / empty / malformed **`Replayt-Signature`** | **401** | Map **`WebhookSignatureMissingError`** / **`WebhookSignatureFormatError`** (or equivalent **`handle_lifecycle_webhook_post`** outcome). |
| Well-formed MAC mismatch | **403** (or **401** if policy chooses; stay consistent in the snippet) | Map **`WebhookSignatureMismatchError`** / **`403`** from handler glue. |

**Must not (examples and prose):**

- Echo the **shared secret**, the **full** **`Replayt-Signature`** value, or a **computed MAC** in HTTP responses, client
  JSON, or example logs.
- Use **realistic long hex** substrings that look like live MACs; use placeholders such as **`<signature-header-value>`**
  or **`sha256=<redacted>`** in narrative.

**Should:** Point readers to **[SPEC_WEBHOOK_FAILURE_RESPONSES.md](SPEC_WEBHOOK_FAILURE_RESPONSES.md)** for stable
**`error`** codes and safe JSON bodies, and to **[SPEC_STRUCTURED_LOGGING_REDACTION.md](SPEC_STRUCTURED_LOGGING_REDACTION.md)**
for logging header dicts.

## Copy-paste examples (normative shape)

Until Builder phase **3** lands, this section is a **placeholder**. When complete, it **must** include:

1. **Framework:** **FastAPI** **or** **Starlette** (at least one; both preferred if maintainers agree on length).
2. **Single POST route** (e.g. **`/webhook`**) that accepts **`application/json`** lifecycle payloads.
3. **Explicit step:** `await request.body()` (or equivalent) **before** **`json.loads`** / **`parse_lifecycle_webhook_event`**.
4. **Secret:** Load from **`REPLAYT_LIFECYCLE_WEBHOOK_SECRET`** (or placeholder **`your-shared-secret`**) per **README** /
   **SPEC_WEBHOOK_SIGNATURE**—**not** hard-coded real secrets.
5. **401/403 mapping** with **generic** client bodies (link or abbreviated JSON per **SPEC_WEBHOOK_FAILURE_RESPONSES**).
6. **Imports:** Only **public** API names (**`verify_lifecycle_webhook_signature`**, **`LIFECYCLE_WEBHOOK_SIGNATURE_HEADER`**,
   **`parse_lifecycle_webhook_event`**, optional **`handle_lifecycle_webhook_post`**, **`LifecycleWebhookHttpResult`**).

## Acceptance checklist (AF1–AF7)

| ID | Criterion |
| -- | --------- |
| **AF1** | **`docs/SPEC_INTEGRATOR_ASGI_VERIFIED_FIRST.md`** exists and replaces **§ Copy-paste examples** placeholder with at least one **minimal**, **runnable** ASGI-oriented example (FastAPI and/or Starlette). |
| **AF2** | Example(s) obtain **raw body `bytes`** and verify **before** JSON parsing; anti-pattern (**`request.json()`** / body params first) is **named** in prose. |
| **AF3** | Example(s) use **only** **SPEC_PUBLIC_API** import paths for this package. |
| **AF4** | Example(s) show **401** / **403** mapping for signature failures without leaking secret, full signature, or MAC. |
| **AF5** | Prose links **SPEC_WEBHOOK_SIGNATURE** (verification procedure) and **SPEC_WEBHOOK_FAILURE_RESPONSES**. |
| **AF6** | Root **`README.md`** **`## Verifying webhook signatures`** links **`docs/SPEC_INTEGRATOR_ASGI_VERIFIED_FIRST.md`**. |
| **AF7** | **`CHANGELOG.md`** **Unreleased** notes the new integrator guide when user-visible doc ships (Builder commit). |

## Related docs

- **[SPEC_WEBHOOK_SIGNATURE.md](SPEC_WEBHOOK_SIGNATURE.md)** — raw body, **`Replayt-Signature`**, **`verify_lifecycle_webhook_signature`**.
- **[SPEC_MINIMAL_HTTP_HANDLER.md](SPEC_MINIMAL_HTTP_HANDLER.md)** — **`handle_lifecycle_webhook_post`**, status table **H5** (verify before JSON on bad MAC).
- **[SPEC_WEBHOOK_FAILURE_RESPONSES.md](SPEC_WEBHOOK_FAILURE_RESPONSES.md)** — stable **`error`** codes and safe bodies.
- **[SPEC_STRUCTURED_LOGGING_REDACTION.md](SPEC_STRUCTURED_LOGGING_REDACTION.md)** — redacting **`Replayt-Signature`** in logs.
- **[SPEC_PUBLIC_API.md](SPEC_PUBLIC_API.md)** — supported imports; no internal modules in examples.
- **[SPEC_README_OPERATOR_SECTIONS.md](SPEC_README_OPERATOR_SECTIONS.md)** — README **`## Verifying webhook signatures`** link requirement.
- **[README.md](../README.md)** — operator entry; must cross-link this guide when backlog is implemented.
