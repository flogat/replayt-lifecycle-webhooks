# Spec: structured logging helpers with default sensitive-key redaction

**Backlog:** Add structured logging helper that redacts sensitive keys by default (`fa75ecf3-a113-418e-99cc-aa0c31237eba`).  
**Audience:** Spec gate (2b), Builder (3), Tester (4), operators, integrators.

## Problem

Operators need **structured** log fields (HTTP method, path, status, stable **`error`** codes, correlation ids) to triage
webhook handling. Accidentally logging **raw headers** or **credential-like** fields leaks **signing material**, bearer
tokens, or cookies. Today **[SPEC_WEBHOOK_FAILURE_RESPONSES.md](SPEC_WEBHOOK_FAILURE_RESPONSES.md)** forbids certain
outputs but does not define a **shared, tested** redaction primitive for this package or its users.

## Goals

- Ship a **small**, **stdlib-only** (no new mandatory runtime dependencies) API to **redact** sensitive **HTTP header**
  names and **string-keyed mapping** entries before they are attached to **`logging`** records or serialized.
- Provide a **documented extension point** so integrators can add deployment-specific sensitive names (custom auth
  headers, internal tokens) without forking.
- Ensure **package-owned** code paths that log header maps or similar metadata use the helper **once implemented** (see
  **§ Package-owned logging**).
- Add **pytest** coverage that fails if representative secrets reappear in formatted log output (see **§ Test
  acceptance** and **[SPEC_AUTOMATED_TESTS.md](SPEC_AUTOMATED_TESTS.md)** backlog **`fa75ecf3`**).

## Non-goals

- **Deep JSON PII scrubbing** inside arbitrary webhook bodies (MISSION out-of-scope for payload secrets unless a spec
  explicitly adds it). Redaction here targets **headers** and **integrator-chosen structured fields** (dict-like
  **`extra`**), not full body content.
- **Mandatory** **structlog** / **JSON log** sinks; integrators may wrap stdlib **`logging`** as they prefer.
- Changing **HTTP response** bodies or stable **`error`** codes (remain **SPEC_WEBHOOK_FAILURE_RESPONSES**).

## Normative redacted placeholder

For every redacted **string value**, replace the entire value with exactly:

**`[REDACTED]`**

(ASCII brackets and word as shown.) Tests **must** assert this literal appears and that the **original secret substring**
does **not** appear in the captured log line or formatted message.

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

- **`format_safe_webhook_log_extra(...)`** — accepts optional **`headers`**, **`method`**, **`path`** or **`uri`**, **`status_code`**, **`error_code`**, and returns a **`dict`** suitable for **`extra=`** after passing nested header-like data through **`redact_headers`** / **`redact_mapping`**.

Exact parameter names are **Builder** choice; **README** and this spec **must** show one **copy-paste** example for
integrators.

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

**Integrators:** **README** **must** state that custom handlers should reuse the same helpers when logging request
metadata (see **README** **§ Production logging and redaction**).

## Relationship to **SPEC_WEBHOOK_FAILURE_RESPONSES**

This spec **implements** the “**what not to log**” table for **header-shaped** and **metadata** fields by providing
mechanisms and tests. It does **not** relax prohibitions on **raw body** excerpts, **computed MAC**, or **full**
**`Replayt-Signature`** in free-form strings — operators must still avoid logging those outside structured redacted
fields.

## Test acceptance (normative)

Detailed checklist rows **L1–L8** live under backlog **`fa75ecf3`** in **[SPEC_AUTOMATED_TESTS.md](SPEC_AUTOMATED_TESTS.md)**.
Summary:

- Capture output with **`caplog`**, a **`logging.Handler`**, or equivalent — **no** network.
- Prove **`Authorization`** (e.g. **`Bearer s3cr3t`**) and **`Replayt-Signature`** do not leak literal secrets.
- Prove **`extra_sensitive_*`** extensions redact custom keys.
- Prove shallow **`redact_mapping`** for at least one **`token`**, **`secret`**, or **`api_key`** key.

## Spec acceptance (checklist)

| # | Criterion | Verification |
|---|-----------|--------------|
| G1 | This file defines **placeholder**, **default header names**, **default mapping keys**, **public symbols**, and **package-owned logging** rules. | Review this file |
| G2 | **SPEC_AUTOMATED_TESTS** includes backlog **`fa75ecf3`** rows **L1–L8** pointing here. | Review **SPEC_AUTOMATED_TESTS** |
| G3 | **README** documents production logging expectations and links here. | Review **README.md** |
| G4 | **SPEC_WEBHOOK_FAILURE_RESPONSES** cross-links here from logging guidance. | Review **SPEC_WEBHOOK_FAILURE_RESPONSES** |

## Related docs

- **[SPEC_WEBHOOK_FAILURE_RESPONSES.md](SPEC_WEBHOOK_FAILURE_RESPONSES.md)** — HTTP JSON errors; what must not appear in
  logs or responses.
- **[SPEC_WEBHOOK_SIGNATURE.md](SPEC_WEBHOOK_SIGNATURE.md)** — **`Replayt-Signature`** verification; leakage rules.
- **[SPEC_MINIMAL_HTTP_HANDLER.md](SPEC_MINIMAL_HTTP_HANDLER.md)** — reference handler surface.
- **[SPEC_HTTP_SERVER_ENTRYPOINT.md](SPEC_HTTP_SERVER_ENTRYPOINT.md)** — reference server.
- **[README.md](../README.md)** — integrator copy-paste and operator expectations.
