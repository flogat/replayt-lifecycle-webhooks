# Spec: structured logging helpers with default sensitive-key redaction

**Backlogs:**

- Establish structured logging and redaction for webhook handling (`6ea52b2b-ff96-4511-a9f8-d5d9ed6d3711`).
- Add structured logging helper that redacts sensitive keys by default (`fa75ecf3-a113-418e-99cc-aa0c31237eba`) — same
  implementation and **L1–L9** checklist; **`fa75ecf3`** remains the **SPEC_AUTOMATED_TESTS** anchor id.
- Optional structured diagnostics on the **reference server** and **HTTP handler** paths using the same redaction helpers
  (`0bab43f3-cb59-40ff-96c3-31fb2703cfb0`) — normative **§ Optional diagnostic logging (serve and handler paths)** and
  **pytest** rows **LG1–LG4** in **[SPEC_AUTOMATED_TESTS.md](SPEC_AUTOMATED_TESTS.md)** (backlog **`0bab43f3`**).

**Audience:** Spec gate (2b), Builder (3), Tester (4), operators, integrators.

## Backlog acceptance mapping (`6ea52b2b`)

Maps **Establish structured logging and redaction for webhook handling** to normative sections here and to **pytest**
proof (backlog **`fa75ecf3`**, rows **L1–L9** in **[SPEC_AUTOMATED_TESTS.md](SPEC_AUTOMATED_TESTS.md)**).

| Original backlog criterion | Normative location in this spec | Proof |
| -------------------------- | ------------------------------- | ----- |
| Logging **helper** or **convention** documented in **DESIGN_PRINCIPLES** or **MISSION** | **§ Public API** (symbols, **`format_safe_webhook_log_extra`**); **§ Recommended structured field names**; cross-links from **MISSION** (**Production logging**) and **DESIGN_PRINCIPLES** (**Observable automation**) | Doc review |
| Request logging **redacts** **`Authorization`** / **signature** headers and **omits full raw bodies** by default | **§ Request logging and raw body**; **§ Default sensitive header names**; **§ Default sensitive mapping keys** | **L2**, **L3**, **L8**; **L9** (no raw body substring) |
| At least one **test** or **doc example** for expected log shape on **successful** delivery | **§ Example: successful verified delivery** (normative documentation, always required) | **§ Example** (doc); **L9** in **pytest** (**`test_l9_success_verified_delivery_no_raw_body_in_logs`**) |

## Problem

Operators need **structured** log fields (HTTP method, path, status, stable **`error`** codes, correlation ids) to triage
webhook handling. Accidentally logging **raw headers** or **credential-like** fields leaks **signing material**, bearer
tokens, or cookies. Logging the **raw POST body** (even after verify) can leak **PII** and business data into aggregators.
Today **[SPEC_WEBHOOK_FAILURE_RESPONSES.md](SPEC_WEBHOOK_FAILURE_RESPONSES.md)** forbids certain outputs but does not, by
itself, define a **shared, tested** redaction primitive or a **normative request-logging** shape for this package or its
users.

## Goals

- Ship a **small**, **stdlib-only** (no new mandatory runtime dependencies) API to **redact** sensitive **HTTP header**
  names and **string-keyed mapping** entries before they are attached to **`logging`** records or serialized.
- **Normative default for request logging:** do **not** attach **full raw body** bytes or body text to log records or
  structured **`extra`** (see **§ Request logging and raw body**).
- Provide a **documented extension point** so integrators can add deployment-specific sensitive names (custom auth
  headers, internal tokens) without forking.
- Document **recommended correlation fields** aligned with **[EVENTS.md](EVENTS.md)** (**`event_id`**, **`correlation.*`**)
  so run/approval traffic is traceable without logging payload bodies.
- Ensure **package-owned** code paths that log header maps or similar metadata use the helper **once implemented** (see
  **§ Package-owned logging**).
- Add **pytest** coverage that fails if representative secrets reappear in formatted log output (see **§ Test
  acceptance** and **[SPEC_AUTOMATED_TESTS.md](SPEC_AUTOMATED_TESTS.md)** backlog **`fa75ecf3`**, rows **L1–L9**).

## Non-goals

- **Deep JSON PII scrubbing** inside arbitrary webhook bodies (MISSION out-of-scope for payload secrets unless a spec
  explicitly adds it). The **`redact_mapping`** / **`redact_headers`** helpers target **headers** and **integrator-chosen**
  structured fields (dict-like **`extra`**), **not** turning arbitrary JSON bodies into safe text. **Request logging**
  still **must omit** the raw body by default (**§ Request logging and raw body**).
- **Mandatory** **structlog** / **JSON log** sinks; integrators may wrap stdlib **`logging`** as they prefer.
- Changing **HTTP response** bodies or stable **`error`** codes (remain **SPEC_WEBHOOK_FAILURE_RESPONSES**).

## Normative redacted placeholder

For every redacted **string value**, replace the entire value with exactly:

**`[REDACTED]`**

(ASCII brackets and word as shown.) Tests **must** assert this literal appears and that the **original secret substring**
does **not** appear in the captured log line or formatted message.

## Request logging and raw body (normative)

For **inbound HTTP webhook** diagnostics (any code path that logs something about the request **before** or **after**
verification), **default** logging **must not** include:

| Prohibited in default request logs | Rationale |
| ---------------------------------- | --------- |
| Full **raw body** bytes or decoded body text | May contain **PII**, tokens, or business data — same class as **SPEC_WEBHOOK_FAILURE_RESPONSES** “raw request body”. |
| **`Authorization`**, **`Replayt-Signature`**, and other signing/token headers (unredacted) | Credential and digest leakage; use **`redact_headers`**. |

**Allowed without extra privacy review:** HTTP **method**, **path** (or a stable route template), response **`status_code`**,
stable **`error_code`** from **[SPEC_WEBHOOK_FAILURE_RESPONSES.md](SPEC_WEBHOOK_FAILURE_RESPONSES.md)** on failure paths,
**`webhook_body_bytes_len`** (integer octet count of the raw body the handler read from the wire), and **identifiers** copied **only**
from **verified** parsing (**`event_id`**, **`correlation.run_id`**, **`correlation.workflow_id`**, optional
**`correlation.approval_request_id`**) per **[EVENTS.md](EVENTS.md)**. **Do not** log arbitrary strings from **unverified**
JSON as if they were correlation ids.

**Integrators** who log header dicts without using **`format_safe_webhook_log_extra`** must still satisfy this section:
**`redact_headers`** alone does **not** absolve omitting the raw body from **`extra=`** and message templates.

### Never-log checklist (operators, default request logs)

Treat the following as **out of bounds** for **default** inbound-webhook request diagnostics (before or after verify)
unless a **separate**, privacy-reviewed logging path explicitly opts in:

- Full **raw body** octets, decoded body **text**, or a **JSON string snapshot** of the payload.
- **Unredacted** **`Authorization`**, **`Replayt-Signature`**, **`X-Signature*`** family, **`Cookie`** / **`Set-Cookie`**,
  **`X-Api-Key`**, and values for keys listed in **§ Default sensitive mapping keys**.
- **Shared HMAC secret**, **computed MAC**, full signature **digests** in free-form log messages, or anything that could
  reconstruct signing material (see **SPEC_WEBHOOK_SIGNATURE** / **SPEC_WEBHOOK_FAILURE_RESPONSES**).
- **Correlation identifiers** taken from **unverified** JSON; use **`event_id`** and **`correlation.*`** only **after**
  verify + parse per **[EVENTS.md](EVENTS.md)**.

## Default sensitive header names

Header name matching is **case-insensitive** (HTTP field names). If a name matches any row below, redact the **full**
header value.

| Name | Rationale |
| ---- | --------- |
| **`Authorization`** | Bearer / basic credentials. |
| **`Proxy-Authorization`** | Same class as **Authorization**. |
| **`Cookie`** | Session material. |
| **`Set-Cookie`** | Session material (if ever logged on responses). |
| **`Replayt-Signature`** | Aligns with **SPEC_WEBHOOK_FAILURE_RESPONSES** — never log full digest line. |
| **`X-Api-Key`**, **`X-API-Key`** | Common secret header shapes (match case-insensitively so one canonical check covers both). |
| **`X-Signature`**, **`X-Signature-*`** | Generic signature family; implement **prefix** match case-insensitively for names starting with **`X-Signature`** (including trailing token). |

**Builder note:** Implement as a normalized set plus optional **prefix** rules; document the exact matching algorithm in
docstrings so Tester can lock behavior with edge-case tests (e.g. **`x-signature-custom`** redacted).

## Default sensitive mapping keys (structured `extra` / metadata dicts)

For **dict-like** structures intended for **`Logger.*(..., extra={...})`** or JSON log fields, treat a key as sensitive
if its **lowercased** form **equals** any of:

- **`authorization`**
- **`proxy-authorization`**
- **`cookie`**
- **`set-cookie`**
- **`replayt-signature`**
- **`signature`**
- **`x-api-key`**
- **`api-key`**, **`api_key`**
- **`password`**
- **`secret`**
- **`token`**
- **`bearer`**
- **`body`**, **`raw_body`**, **`payload`**, **`request_body`** — if present in **`extra=`**, redact string-like values;
  **prefer omitting** these keys entirely per **§ Request logging and raw body**.

**Depth:** For the **minimum** contract (**L6** in **SPEC_AUTOMATED_TESTS**), **shallow** redaction only: top-level keys
of the provided mapping. **Optional extension (documented):** a **`max_depth`** (or equivalent) parameter **may** recurse
into nested **`dict`** values; if implemented, defaults **must** preserve **shallow** behavior and tests **must** cover
at least one nested case.

**Values:** Redact when the value is **`str`** or **`bytes`** (for **`bytes`**, replace with **`[REDACTED]`** as **`str`**
or document a single consistent encoding for tests). Non-string scalar values **may** be left unchanged unless the key
matches; **do not** stringify arbitrary objects solely to redact (avoid leaking **`__repr__`** surprises).

## Bearer and token-shaped values (optional hardening)

If **`Authorization`** (or **`authorization`** in a mapping) is present and the value **case-insensitively** starts with
**`Bearer `** followed by non-empty token material, the **entire** value **must** be replaced with **`[REDACTED]`** (same
as other sensitive keys — no need to preserve the **`Bearer`** prefix in output).

**Optional:** If the Builder implements **heuristic** redaction for **non-header** string values that look like
**`Bearer <token>`** inside generic messages, document it as **best-effort** and **do not** mark it normative unless a
checklist row is added in a follow-up backlog.

## Public API (contract for Builder)

**Module:** Prefer a dedicated submodule **`replayt_lifecycle_webhooks.redaction`** (or a name documented here if
renamed in **CHANGELOG**). **No** new mandatory dependencies.

**Required symbols (minimum):**

| Symbol | Role |
| ------ | ---- |
| **`REDACTED_PLACEHOLDER`** | Constant **`str`**, value **`[REDACTED]`**. |
| **`DEFAULT_SENSITIVE_HEADER_NAMES`** | Documented iterable of default header names / prefix rules (frozen or tuple) for transparency. |
| **`DEFAULT_SENSITIVE_MAPPING_KEYS`** | Documented iterable of default dict keys (lowercase forms). |
| **`redact_headers(headers, *, extra_sensitive_names=(), ...)`** | Returns a **new** **`dict[str, str]`** (or **`Mapping`** copy) with sensitive header **values** replaced; original mapping **unmodified**. Accept **`extra_sensitive_names`** for integrator extensions (**case-insensitive** names, same rules as defaults). |
| **`redact_mapping(mapping, *, extra_sensitive_keys=(), ...)`** | Returns a **new** shallow **`dict`** with sensitive **values** replaced per **§ Default sensitive mapping keys**; supports **`extra_sensitive_keys`** (**lowercase** comparison per key). |

**Structured logging helper (required):** At least one documented entry point that combines common operator fields, for
example:

- **`format_safe_webhook_log_extra(...)`** — accepts optional **`headers`**, **`method`**, **`path`** or **`uri`**, **`status_code`**, **`error_code`**, optional **`webhook_body_bytes_len`** (non-negative **`int`**, body length only), optional correlation kwargs **`lifecycle_event_id`**, **`lifecycle_run_id`**, **`lifecycle_workflow_id`**, **`lifecycle_approval_request_id`** (from verified JSON only), optional **`extra_sensitive_header_names`** for integrator-specific header names (passed through to **`redact_headers`**), and returns a **`dict`** suitable for **`extra=`**. Emitted keys use the **`webhook_*`** / **`lifecycle_*`** names in **§ Recommended structured field names** (call-site kwargs **`status_code`** / **`error_code`** map to **`webhook_status_code`** / **`webhook_error_code`** in the returned dict). Keys whose values are **`None`** (**`lifecycle_approval_request_id`** when absent) **may** be omitted from the returned dict.

**Normative:** The returned mapping **must not** include raw body bytes, decoded body text, or JSON string snapshots of the
payload **by default**. Optional **`webhook_body_bytes_len`** is the **only** body-related field the contract guarantees for
request summaries; integrators who need more must **opt in** explicitly in their own code (out of this helper’s defaults)
and accept privacy review.

Exact parameter names are **Builder** choice; **README** and this spec **must** show one **copy-paste** example for
integrators. **§ Example: successful verified delivery** is the reference shape for a **204** success path.

**Exports:** **`replayt_lifecycle_webhooks.__all__`** (if used) **may** re-export redaction symbols; re-export is
**optional** as long as **README** documents the canonical import path.

## Package-owned logging

After implementation, **any** **`logging`** call in this repository that emits **HTTP header** names/values or **structured**
copies of header maps **must** use **`redact_headers`** (or a helper built on it) before emission. Applies at minimum to:

- **`replayt_lifecycle_webhooks.handler`**
- **`replayt_lifecycle_webhooks.serve`**
- **`replayt_lifecycle_webhooks.demo_webhook`**
- **`replayt_lifecycle_webhooks.__main__`**

If a file has **no** logging today, **do not** add noisy logs solely to satisfy this spec; when logging is added for
diagnostics, it **must** follow this section.

## Optional diagnostic logging (serve and handler paths)

**Backlog:** **`0bab43f3-cb59-40ff-96c3-31fb2703cfb0`** (*Serve path: optional structured logging hook using `redaction`
helpers*). **Audience:** operators running **`python -m replayt_lifecycle_webhooks`**, integrators wrapping the WSGI stack,
Builder (3), Tester (4).

### Problem

The reference server (**`replayt_lifecycle_webhooks.serve`**, **`__main__`**) and the minimal HTTP handler
(**`replayt_lifecycle_webhooks.handler`**) are natural places to add request-scoped diagnostics. Without an explicit
contract, ad-hoc **`print`** or **`logging`** can leak **raw bodies**, **signing material**, or **bearer** tokens. This
section defines an **opt-in** path that **reuses** **`format_safe_webhook_log_extra`**, **`redact_headers`**, and
**`redact_mapping`** so server and handler logs stay aligned with **§ Request logging and raw body** and **§ Example:
successful verified delivery**.

### Goals (normative)

- **Default off:** With diagnostics **disabled**, behavior and observable output **must** match the pre-feature baseline
  for webhook handling (no **new** request-scoped **`logging`** records; existing **startup** **`print`** in **`__main__`**
  **may** remain). Operators who do not enable the feature see **no** extra log volume from per-request hooks.
- **No new mandatory logging dependencies:** Use **stdlib** **`logging`** only; **do not** add third-party logging
  libraries for this backlog.
- **Redaction at the source:** Every **opt-in** diagnostic record **must** be built with **`format_safe_webhook_log_extra`**
  and/or **`redact_headers`** / **`redact_mapping`** so sensitive header names and **`extra=`** keys follow **§ Default
  sensitive header names** and **§ Default sensitive mapping keys**. **Do not** hand-assemble header dicts for log **`extra`**
  without redaction.
- **Documented configuration:** **README.md** (reference-server / operator section) **must** document **how** to enable
  diagnostics (**environment variable** and/or **`python -m`** flag and/or keyword-only parameters on factories, at least
  one combination that operators can discover without reading source). When multiple switches exist, document **precedence**
  (for example flag overrides env).
- **Optional narrow callback (Builder choice):** The implementation **may** expose an optional callable (for example
  **`on_request_log: Callable[..., None] | None`**) that receives **only** data already safe per this spec (for example a
  **`Mapping[str, Any]`** shaped like **`Logger.debug(..., extra=…)`** kwargs, **after** redaction). The callback **must
  not** receive the raw POST body, unredacted signing headers, or the shared secret. If no callback is documented, **stdlib**
  **`logging`** alone satisfies the backlog.
- **Logger naming:** If using **`logging`**, use a **documented** logger name (recommended: child loggers under
  **`replayt_lifecycle_webhooks`**, e.g. **`replayt_lifecycle_webhooks.serve`** / **`replayt_lifecycle_webhooks.handler`**)
  so operators can attach handlers and levels without guessing.
- **Correlation fields:** **`lifecycle_*`** keys in diagnostic **`extra`** **must** come **only** from **verified** parsed
  payloads per **§ Request logging and raw body** (same rule as **§ Recommended structured field names**).

### Non-goals

- **Mandatory** request logging for all installs.
- **Changing** HTTP status codes, JSON error bodies, or **SPEC_WEBHOOK_FAILURE_RESPONSES** mappings.
- **Deep** JSON scrubbing of arbitrary payload fields (remains **§ Non-goals** for this package).

### Documentation and examples (normative)

- Any **README** or spec **example** that shows **enabled** diagnostics **must** use **synthetic** correlation ids, **fake**
  **`[REDACTED]`** header values, and **must not** show real **HMAC** secrets, full **`Replayt-Signature`** digests, or raw
  POST bodies. Prefer the same field names as **§ Example: successful verified delivery** where applicable.
- **CHANGELOG.md** **Unreleased** **must** note the new opt-in switches and logger names when the feature ships.

### Backlog acceptance mapping (`0bab43f3`)

| Original backlog criterion | Normative location | Proof |
| -------------------------- | ------------------- | ----- |
| Documented optional logging configuration (**stdlib** **`logging`** or narrow callback) routing selected fields through existing redaction utilities | **§ Optional diagnostic logging (serve and handler paths)**; **SPEC_HTTP_SERVER_ENTRYPOINT** configuration; **README** | Doc review; **S10** |
| Default behavior unchanged when disabled; no secret or raw body values in default log examples | **§ Optional diagnostic logging** (default off, example rules); **§ Request logging and raw body** | Doc review; **LG1**; example review |
| Tests prove redaction on representative messages; references **SPEC_STRUCTURED_LOGGING_REDACTION** | **SPEC_AUTOMATED_TESTS** backlog **`0bab43f3`**, rows **LG1–LG4** | **`pytest`**; module docstring or comments cite this spec |

**Integrators:** **README** **must** state that custom handlers should reuse the same helpers when logging request
metadata (see **README** **§ Production logging and redaction**).

Package-owned code **must** also follow **§ Request logging and raw body** (no default raw body logging).

## Recommended structured field names (`logging` `extra=`)

Use **snake_case** keys in **`Logger.*(..., extra={...})`** so fields are unlikely to clash with **`LogRecord`**
attributes. Recommended names (subset; **`format_safe_webhook_log_extra`** should document the exact keys it emits):

| Key | When | Notes |
| --- | ---- | ----- |
| **`webhook_method`** | Request handled | Shipped today by **`format_safe_webhook_log_extra`**; e.g. **`POST`**. |
| **`webhook_path`** | Request handled | Path or route template; avoid query strings that carry PII. |
| **`webhook_status_code`** | Response decided | e.g. **204**, **403**. |
| **`webhook_error_code`** | Failure responses | Stable code from **SPEC_WEBHOOK_FAILURE_RESPONSES**; omit on success (or set **`None`** only if the helper documents that). |
| **`webhook_headers`** | When logging headers | Redacted copy from **`redact_headers`** (shipped key name). |
| **`webhook_body_bytes_len`** | After body read | Non-negative **`int`** only; **Builder** extends **`format_safe_webhook_log_extra`**. |
| **`lifecycle_event_id`** | After verify + parse | From payload **`event_id`**. |
| **`lifecycle_run_id`** | After verify + parse | From **`correlation.run_id`**. |
| **`lifecycle_workflow_id`** | After verify + parse | From **`correlation.workflow_id`**. |
| **`lifecycle_approval_request_id`** | After verify + parse | From **`correlation.approval_request_id`** when present. |

Correlation fields **must** come **only** from **verified** JSON (see **§ Request logging and raw body**).

## Example: successful verified delivery (normative documentation)

Expected **`extra=`** shape after a **successful** path (**HTTP 204**, signature verified, application hook completed).
**`webhook_method`**, **`webhook_path`**, **`webhook_status_code`**, **`webhook_body_bytes_len`**, **`webhook_headers`**, and
present **`lifecycle_*`** fields match **`format_safe_webhook_log_extra`** (omit **`lifecycle_approval_request_id`** when
there is no approval correlation id).

```python
{
    "webhook_method": "POST",
    "webhook_path": "/webhook",
    "webhook_status_code": 204,
    "webhook_body_bytes_len": 642,
    "webhook_headers": {
        "content-type": "application/json; charset=utf-8",
        "replayt-signature": "[REDACTED]",
        "authorization": "[REDACTED]",
    },
    "lifecycle_event_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "lifecycle_run_id": "01JHBDUMMYRUNID000000000000",
    "lifecycle_workflow_id": "wf-email-triage",
}
```

**Must not appear:** raw body bytes/text, JSON snapshot of the payload, unredacted **`Replayt-Signature`** or
**`Authorization`**, **`webhook_hmac`**, or computed MAC material. Implementations **may** omit keys whose values are
**`None`** if documented.

## Relationship to **SPEC_WEBHOOK_FAILURE_RESPONSES**

This spec **implements** the “**what not to log**” table for **header-shaped** and **metadata** fields by providing
mechanisms and tests, and **§ Request logging and raw body** makes the **no raw body** rule explicit for **request**
logging. It does **not** relax prohibitions on **raw body** excerpts, **computed MAC**, or **full**
**`Replayt-Signature`** in free-form strings — operators must still avoid logging those outside structured redacted
fields.

## Test acceptance (normative)

Detailed checklist rows **L1–L9** live under backlog **`fa75ecf3`** in **[SPEC_AUTOMATED_TESTS.md](SPEC_AUTOMATED_TESTS.md)**.
Rows **LG1–LG4** (optional **serve** / **handler** diagnostics, backlog **`0bab43f3`**) live in the same file and **must**
cite this spec in test module docstrings or comments. Summary:

- Capture output with **`caplog`**, a **`logging.Handler`**, or equivalent — **no** network.
- Prove **`Authorization`** (e.g. **`Bearer s3cr3t`**) and **`Replayt-Signature`** do not leak literal secrets.
- Prove **`extra_sensitive_*`** extensions redact custom keys.
- Prove shallow **`redact_mapping`** for at least one **`token`**, **`secret`**, or **`api_key`** key.
- Prove **L9**: success-path **`extra`** (or formatted log line) matches **§ Example: successful verified delivery** for
  required keys and **excludes** raw body substrings.
- Prove **LG1–LG4**: opt-out baseline, opt-in redaction, no raw body echo, traceability to this document (**§ Optional
  diagnostic logging**).

## Spec acceptance (checklist)

| # | Criterion | Verification |
|---|-----------|--------------|
| G0 | **§ Backlog acceptance mapping (`6ea52b2b`)** ties story criteria to sections and **L*** proof. | Review this file |
| G1 | This file defines **placeholder**, **default header names**, **default mapping keys**, **public symbols**, **package-owned logging**, **request body omission**, **recommended field names**, **never-log checklist**, and the **success-path example**. | Review this file |
| G2 | **SPEC_AUTOMATED_TESTS** includes backlog **`fa75ecf3`** rows **L1–L9** pointing here. | Review **SPEC_AUTOMATED_TESTS** |
| G3 | **README** documents production logging expectations and links here. | Review **README.md** |
| G4 | **SPEC_WEBHOOK_FAILURE_RESPONSES** cross-links here from logging guidance. | Review **SPEC_WEBHOOK_FAILURE_RESPONSES** |
| G5 | **MISSION** and **DESIGN_PRINCIPLES** state the logging convention and link here (story AC: helper or convention in mission/design docs). | Review **MISSION.md**, **DESIGN_PRINCIPLES.md** |
| G6 | Backlog **`0bab43f3`**: **§ Optional diagnostic logging (serve and handler paths)** and **SPEC_AUTOMATED_TESTS** **LG1–LG4** trace optional **serve** / **handler** diagnostics to this spec. | Review this file and **SPEC_AUTOMATED_TESTS** |

## Related docs

- **[SPEC_WEBHOOK_FAILURE_RESPONSES.md](SPEC_WEBHOOK_FAILURE_RESPONSES.md)** — HTTP JSON errors; what must not appear in
  logs or responses.
- **[SPEC_WEBHOOK_SIGNATURE.md](SPEC_WEBHOOK_SIGNATURE.md)** — **`Replayt-Signature`** verification; leakage rules.
- **[SPEC_MINIMAL_HTTP_HANDLER.md](SPEC_MINIMAL_HTTP_HANDLER.md)** — reference handler surface.
- **[SPEC_HTTP_SERVER_ENTRYPOINT.md](SPEC_HTTP_SERVER_ENTRYPOINT.md)** — reference server.
- **[README.md](../README.md)** — integrator copy-paste and operator expectations.
