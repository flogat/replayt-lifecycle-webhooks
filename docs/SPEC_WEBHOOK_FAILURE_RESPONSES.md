# Spec: webhook failure responses for operators and runbooks

**Backlog:** Document webhook failure responses operators can act on (`5ec1325a-5b45-440f-b93f-28b711fa5482`).  
**Audience:** Spec gate (2b), Builder (3), Tester (4), operators, support, integrators.

## Problem

Operators triaging failed deliveries need **HTTP status codes** and **response body shapes** that explain **what failed**
(cryptography, syntax, routing, policy) **without** exposing signing material, secrets, or raw customer payloads in the
HTTP response or in default production logs.

## Goals

- Publish **stable machine-readable `error` codes** (string identifiers) plus **short human-readable `message`**
  strings for JSON error bodies where integrators return a body at all.
- Align **HTTP semantics** with **[SPEC_WEBHOOK_SIGNATURE.md](SPEC_WEBHOOK_SIGNATURE.md)** and the optional reference
  handler in **[SPEC_MINIMAL_HTTP_HANDLER.md](SPEC_MINIMAL_HTTP_HANDLER.md)** (**405** / **401** / **403** / **400** /
  **204** for that path).
- Document **post-verification** failures (**unknown `event_type`**, schema validation, optional **replay / freshness**
  policies) that integrators handle **after** **`json.loads`** or **`parse_lifecycle_webhook_event`**.
- State explicitly what **must not** appear in responses or production logs.

## HTTP stack alignment

| Surface | Role |
| ------- | ---- |
| **Any framework** | Map the same status codes and JSON shapes from this spec in FastAPI, Starlette, Flask, Django, etc. The package does **not** require a specific framework. |
| **`handle_lifecycle_webhook_post`** | Framework-agnostic request view → **`LifecycleWebhookHttpResult`**; see **SPEC_MINIMAL_HTTP_HANDLER** for ordering (**verify before JSON**). |
| **`make_lifecycle_webhook_wsgi_app`** | Stdlib **WSGI** adapter; same status mapping. |

**Content-Type:** For responses that include a JSON body, use **`Content-Type: application/json; charset=utf-8`**.

## JSON error envelope (normative for integrators)

When returning a **non-empty** error body, prefer a single JSON object with exactly these keys:

| Field | Type | Required | Description |
| ----- | ---- | -------- | ----------- |
| **`error`** | string | yes | Stable code from the tables below (**snake_case**). Do not rename per deployment. |
| **`message`** | string | yes | Short, operator-facing sentence. **No** stack traces, file paths, header values, or body excerpts. |

**Optional extension:** Integrators may add **`request_id`** (opaque id from their edge) for log correlation; it must not
reveal secrets or PII.

### Safe example bodies (redacted, illustrative)

These examples are **not** real traffic; digests and ids are placeholders.

**Missing signature (401):**

```json
{"error":"signature_required","message":"The Replayt-Signature header is missing or empty."}
```

**Malformed signature value (401):**

```json
{"error":"signature_malformed","message":"The signature header is not a valid v1 value."}
```

**MAC does not match body (403):**

```json
{"error":"signature_mismatch","message":"Signature does not match the request body."}
```

**Body not valid UTF-8 or not JSON text after verification (400):**

```json
{"error":"invalid_json","message":"Request body is not valid UTF-8 JSON."}
```

**Wrong HTTP method (405):** Custom integrators may use an empty body or minimal plain text (often with **`Allow: POST`**).
**`handle_lifecycle_webhook_post`** returns JSON for every client error on this path, including **405**, for a single
shape across statuses:

```json
{"error":"method_not_allowed","message":"Only POST is supported for this endpoint."}
```

**Unknown or unsupported `event_type` after verification (typical 422):**

```json
{"error":"unknown_event_type","message":"Event type is not supported by this integration."}
```

**Replay / freshness rejected by integrator policy (typical 422; see v1 note below):**

```json
{"error":"replay_rejected","message":"Delivery is outside the accepted time window or was already processed."}
```

**Success (204):** **No body** per **SPEC_MINIMAL_HTTP_HANDLER** for the reference handler; integrators using **200** may
return a minimal JSON ack—out of scope for this failure spec.

## Error categories and HTTP codes

### Cryptographic and transport (before trusting JSON)

Handled in **order**: method → signature verification → UTF-8 decode → JSON parse. See **SPEC_MINIMAL_HTTP_HANDLER**
(**H5**): if verification fails, do **not** return **400** for JSON parse errors.

| Category | Typical HTTP | Stable `error` | When |
| -------- | ------------ | -------------- | ---- |
| Wrong method | **405** | `method_not_allowed` | Not **POST** (include **`Allow: POST`** where headers are returned). |
| Missing / empty signature header | **401** | `signature_required` | No usable **`Replayt-Signature`** (same class as **`WebhookSignatureMissingError`**). |
| Malformed signature (not valid v1 hex / length) | **401** | `signature_malformed` | Header present but not a valid v1 encoding (**`WebhookSignatureFormatError`**). |
| Well-formed signature, MAC mismatch | **403** | `signature_mismatch` | **`WebhookSignatureMismatchError`**. |
| Invalid UTF-8 or **`json.JSONDecodeError`** **after** successful verification | **400** | `invalid_json` | Cryptographic check passed; body is not JSON text. |

### Semantics after verification (integrator / application layer)

These steps run **after** the raw body is authenticated. A forged request never reaches this branch if verification is
correct.

| Category | Typical HTTP | Stable `error` | When |
| -------- | ------------ | -------------- | ---- |
| Unknown **`event_type`** | **422** (recommended) or **400** | `unknown_event_type` | Parsed JSON does not match **[EVENTS.md](EVENTS.md)** registry (e.g. **`parse_lifecycle_webhook_event`** raises). Pick one policy per deployment; **422** signals “syntax OK, semantics not supported.” |
| JSON type wrong for pipeline (e.g. array instead of object) | **400** | `invalid_payload_shape` | Valid JSON but not the expected top-level object for lifecycle events. |
| Replay, duplicate **`event_id`**, or **freshness** outside integrator window | **422** (recommended) or **409** | `replay_rejected` | **Application-level** idempotency or time window (**not** part of v1 MAC); normative split between **benign duplicate** (**2xx**) vs **policy reject** documented in **[SPEC_REPLAY_PROTECTION.md](SPEC_REPLAY_PROTECTION.md)** and **[SPEC_DELIVERY_IDEMPOTENCY.md](SPEC_DELIVERY_IDEMPOTENCY.md)**. |

### Stale timestamp / replay (v1 MAC contract)

| Topic | Spec |
| ----- | ---- |
| **v1 signing (this repo today)** | **[SPEC_WEBHOOK_SIGNATURE.md](SPEC_WEBHOOK_SIGNATURE.md)** — there is **no** normative timestamp **inside** the signed material for v1. MAC verification alone does **not** prove freshness. |
| **Operator runbooks** | Still document **`replay_rejected`** (or **`stale_delivery`** as an alias code **only if** you document both as equivalent) for **your** deduplication store, **`event_id`** replay windows, **`occurred_at`** freshness, or **future** upstream timestamp headers. Dedupe keys and TTL: **[SPEC_DELIVERY_IDEMPOTENCY.md](SPEC_DELIVERY_IDEMPOTENCY.md)**; freshness parameters and hooks: **[SPEC_REPLAY_PROTECTION.md](SPEC_REPLAY_PROTECTION.md)**. |
| **If upstream adds a signed timestamp later** | Update **SPEC_WEBHOOK_SIGNATURE**, **REPLAYT_WEBHOOK_SIGNING.md**, and this file; add tests with injected clocks; map wire failures to **`replay_rejected`** or a dedicated stable code (e.g. **`timestamp_skew`**) in a minor release. |

## What not to log or return (normative)

Do **not** include any of the following in **HTTP response bodies**, **client-facing error JSON**, or **production**
logs at default verbosity:

| Prohibited | Why |
| ---------- | --- |
| **Shared secret** or **HMAC key** material | Full compromise if leaked. |
| **Full `Replayt-Signature` header value** | Reveals the digest line; aids forgery attempts and cross-request correlation. |
| **Computed MAC** or partial digests from your verifier | Same as above. |
| **Raw request body** or large excerpts | May contain **PII**, tokens, or business data. |
| **Stack traces**, internal file paths, or dependency versions | Operational noise; can aid attackers. |

**Server-side:** Exception messages from **`verify_lifecycle_webhook_signature`** are for **internal** handling only; map
them to **generic** client responses per **SPEC_WEBHOOK_SIGNATURE** (**W9**).

**Logging:** Log **stable `error` codes**, **HTTP status**, and opaque **request / correlation ids** you already use.
Optional: first **8** characters of **`event_id`** from **verified** payloads for support—**never** log unverified JSON.
When emitting **header maps** or **structured** metadata, use the package **redaction** helpers described in
**[SPEC_STRUCTURED_LOGGING_REDACTION.md](SPEC_STRUCTURED_LOGGING_REDACTION.md)** (or equivalent integrator-side
redaction) so **defaults** mask **`Authorization`**, **`Replayt-Signature`**, **`X-Signature*`**-family headers, and
related keys.

## Reference handler vs this spec

**`handle_lifecycle_webhook_post`** (**SPEC_MINIMAL_HTTP_HANDLER**) returns the JSON envelope above for **405** / **401**
/ **403** / **400** (with **`Content-Type: application/json; charset=utf-8`**). **204** success has **no** body. Custom
wrappers may still extend responses (for example **`request_id`**) per the optional extension rule.

## Acceptance criteria (checklist)

| # | Criterion | Verification |
|---|-----------|--------------|
| F1 | **README** links this spec and summarizes operator-facing failure categories. | Review **README.md**. |
| F2 | This spec lists **categories**, **typical HTTP codes**, **stable `error` codes**, and **redacted** example JSON bodies. | Review this file. |
| F3 | Guidance forbids returning or logging **secrets**, **full signature header**, **computed MAC**, and **raw payload** excerpts. | Review **§ What not to log or return** and **SPEC_WEBHOOK_SIGNATURE**. |
| F4 | Semantics align with **SPEC_MINIMAL_HTTP_HANDLER** status table and **verify-before-JSON** ordering. | Cross-check both specs. |
| F5 | **Unknown `event_type`** and **replay / freshness** are documented with v1 **MAC** limitations and application-layer responsibility. | Review **§ Stale timestamp / replay** and post-verification table. |
| F6 | **Structured logging / redaction** defaults and test rows **L1–L8** are specified for header- and metadata-shaped fields. | Review **SPEC_STRUCTURED_LOGGING_REDACTION**; **SPEC_AUTOMATED_TESTS** backlog **`fa75ecf3`**. |

## Related docs

- **[SPEC_WEBHOOK_SIGNATURE.md](SPEC_WEBHOOK_SIGNATURE.md)** — **401** / **403** policy, leakage rules, v1 MAC scope.
- **[SPEC_MINIMAL_HTTP_HANDLER.md](SPEC_MINIMAL_HTTP_HANDLER.md)** — reference handler, **H1–H8**, status table.
- **[EVENTS.md](EVENTS.md)** — supported **`event_type`** values; unknown types after verify.
- **[README.md](../README.md)** — integrator entry and operator runbook pointer.
- **[SPEC_STRUCTURED_LOGGING_REDACTION.md](SPEC_STRUCTURED_LOGGING_REDACTION.md)** — tested redaction helpers and integrator extension points.
- **[SPEC_REPLAY_PROTECTION.md](SPEC_REPLAY_PROTECTION.md)** — when to use **`replay_rejected`** vs idempotent **2xx** for duplicates.
