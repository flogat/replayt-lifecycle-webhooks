# Spec: webhook failure responses for operators and runbooks

**Backlog:** Document webhook failure responses operators can act on (`5ec1325a-5b45-440f-b93f-28b711fa5482`).  
**Backlog (examples + cross-links):** Harden canonical HTTP + JSON examples (`70689a62-61d1-4f2a-9d32-e8e8eec27c88`).  
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

**Canonical examples:** One **normative** HTTP + JSON surface per stable **`error`** code lives in **§ Canonical
end-to-end examples** below (after the category tables). Use those blocks for **API gateways**, **contract tests**, and
**client mocks** so all languages share the same status, headers, and body bytes (modulo insignificant JSON whitespace).

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

<a id="canonical-end-to-end-examples"></a>

## Canonical end-to-end examples (HTTP + JSON)

These examples are **not** real traffic: they are **normative fixtures** for integrators. Bodies use the JSON envelope in
**§ JSON error envelope**; field order matches the reference handler’s compact encoding (**`separators=(",", ":")`** in
Python) so byte-for-byte checks are stable:

```json
{"error":"<code>","message":"<text>"}
```

**Response headers (when a body is present):** **`Content-Type: application/json; charset=utf-8`**. **405** responses from
the reference handler also include **`Allow: POST`**.

**Success (not an `error` code):** **`handle_lifecycle_webhook_post`** returns **204** with an **empty** body on success
(and for benign duplicate **`event_id`** acks when **`dedup_store`** is configured). No JSON object is returned on those
paths.

### `method_not_allowed` — **405**

| Item | Value |
| ---- | ----- |
| Recommended status | **405 Method Not Allowed** |
| Extra response headers | **`Allow: POST`** (reference handler and WSGI adapter) |
| `Content-Type` | **`application/json; charset=utf-8`** |

```json
{"error":"method_not_allowed","message":"Only POST is supported for this endpoint."}
```

### `signature_required` — **401**

| Item | Value |
| ---- | ----- |
| Recommended status | **401 Unauthorized** |
| `Content-Type` | **`application/json; charset=utf-8`** |

```json
{"error":"signature_required","message":"The Replayt-Signature header is missing or empty."}
```

### `signature_malformed` — **401**

| Item | Value |
| ---- | ----- |
| Recommended status | **401 Unauthorized** |
| `Content-Type` | **`application/json; charset=utf-8`** |

```json
{"error":"signature_malformed","message":"The signature header is not a valid v1 value."}
```

### `signature_mismatch` — **403**

| Item | Value |
| ---- | ----- |
| Recommended status | **403 Forbidden** |
| `Content-Type` | **`application/json; charset=utf-8`** |

```json
{"error":"signature_mismatch","message":"Signature does not match the request body."}
```

### `invalid_json` — **400**

| Item | Value |
| ---- | ----- |
| Recommended status | **400 Bad Request** |
| When | MAC verified; body is not valid UTF-8 and/or not JSON text (**`UnicodeDecodeError`** / **`json.JSONDecodeError`**). |
| `Content-Type` | **`application/json; charset=utf-8`** |

```json
{"error":"invalid_json","message":"Request body is not valid UTF-8 JSON."}
```

### `invalid_payload_shape` — **400** (post-verify; hooks enabled)

| Item | Value |
| ---- | ----- |
| Recommended status | **400 Bad Request** |
| When | MAC verified; JSON parses, but the top-level value is **not** a JSON **object** while **`dedup_store`** and/or
**`replay_policy`** is set on **`handle_lifecycle_webhook_post`** (reference handler path). Custom integrators without
those hooks may instead accept non-object JSON and enforce shape in **`on_success`**—this code applies when the reference
pipeline requires a lifecycle **object**. |
| `Content-Type` | **`application/json; charset=utf-8`** |

```json
{"error":"invalid_payload_shape","message":"Valid JSON but not the expected top-level object for lifecycle events."}
```

### `unknown_event_type` — **422** (post-verify)

| Item | Value |
| ---- | ----- |
| Recommended status | **422 Unprocessable Content** (formerly *Unprocessable Entity*); **400** is allowed if you document one policy per deployment. |
| When | MAC verified; JSON is an object but **`event_type`** / schema does not match **[EVENTS.md](EVENTS.md)** (e.g.
**`parse_lifecycle_webhook_event`** raises **`pydantic.ValidationError`**). |
| `Content-Type` | **`application/json; charset=utf-8`** |

```json
{"error":"unknown_event_type","message":"Event type is not supported by this integration."}
```

### `replay_rejected` — **422** or **409** (post-verify)

| Item | Value |
| ---- | ----- |
| Recommended status | **422** (preferred) or **409 Conflict**—pick one policy per deployment and document it. |
| When | MAC verified; parsed lifecycle object fails **application-level** replay, freshness, or duplicate policy (e.g.
**`occurred_at`** outside the configured window per **[SPEC_REPLAY_PROTECTION.md](SPEC_REPLAY_PROTECTION.md)**). **Not**
used for **benign** duplicate **`event_id`** acks that return **204** per **[SPEC_DELIVERY_IDEMPOTENCY.md](SPEC_DELIVERY_IDEMPOTENCY.md)**. |
| `Content-Type` | **`application/json; charset=utf-8`** |

```json
{"error":"replay_rejected","message":"Delivery is outside the accepted time window or was already processed."}
```

## Fuzz / property tests

Optional **Hypothesis** tests (**PF1**–**PF10**, backlog **`dcffe5d5`**, **[SPEC_AUTOMATED_TESTS.md](SPEC_AUTOMATED_TESTS.md)**) call
**`verify_lifecycle_webhook_signature`** and **`parse_lifecycle_webhook_event`** directly. They assert **Python** exception
types, not HTTP responses.

**Verifier (`verify_lifecycle_webhook_signature`):** For bounded generated **`secret`**, **`body`**, and **`signature`**, the
function returns **`None`** or raises **only** **`WebhookSignatureMissingError`**, **`WebhookSignatureFormatError`**, or
**`WebhookSignatureMismatchError`**. Map those to **`signature_required`**, **`signature_malformed`**, and
**`signature_mismatch`** (and **401** / **403**) per the tables above when you build HTTP responses.

**Parser (`parse_lifecycle_webhook_event`):** For bounded JSON-shaped **`dict`** inputs, the function returns a supported
lifecycle model or raises **only** **`pydantic.ValidationError`**. For **non-**`dict` **`data`**, it raises **`TypeError`**
only (see the function docstring). Map validation failures to **`unknown_event_type`**, **`invalid_payload_shape`**, or
your chosen **400** / **422** policy per **§ Semantics after verification**.

**Handler fuzzing (**PF9**):** If property tests exercise **`handle_lifecycle_webhook_post`** or
**`make_lifecycle_webhook_wsgi_app`**, outcomes **must** match **[SPEC_MINIMAL_HTTP_HANDLER.md](SPEC_MINIMAL_HTTP_HANDLER.md)**
ordering and the stable **`error`** codes in this spec for the branches under test. The current optional suite omits **PF9**
and stays on verify + parse only.

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
/ **403** / **400** / **422** (with **`Content-Type: application/json; charset=utf-8`**). **204** success has **no** body.
Custom wrappers may still extend responses (for example **`request_id`**) per the optional extension rule. Copy-paste
status + body fixtures: **§ Canonical end-to-end examples**.

## Acceptance criteria (checklist)

| # | Criterion | Verification |
|---|-----------|--------------|
| F1 | **README** links this spec and summarizes operator-facing failure categories. | Review **README.md**. |
| F2 | This spec lists **categories**, **typical HTTP codes**, **stable `error` codes**, and **§ Canonical end-to-end examples** with one **normative** HTTP + JSON fixture per documented **`error`** code (plus **204** success called out as non-JSON). | Review this file. |
| F3 | Guidance forbids returning or logging **secrets**, **full signature header**, **computed MAC**, and **raw payload** excerpts. | Review **§ What not to log or return** and **SPEC_WEBHOOK_SIGNATURE**. |
| F4 | Semantics align with **SPEC_MINIMAL_HTTP_HANDLER** status table and **verify-before-JSON** ordering. | Cross-check both specs. |
| F5 | **Unknown `event_type`**, **`invalid_payload_shape`**, and **replay / freshness** are documented with v1 **MAC** limitations and application-layer responsibility. | Review **§ Stale timestamp / replay**, post-verification table, and canonical **`replay_rejected`** / **`unknown_event_type`** examples. |
| F6 | **Structured logging / redaction** defaults and test rows **L1–L9** are specified for header- and metadata-shaped fields (including **no raw body** in default request logs). | Review **SPEC_STRUCTURED_LOGGING_REDACTION**; **SPEC_AUTOMATED_TESTS** backlog **`fa75ecf3`**. |

### Backlog `70689a62` — canonical examples and cross-links (documentation)

| # | Criterion | Verification |
|---|-----------|--------------|
| FR1 | Each stable **`error`** in the **§ Error categories** tables appears in **§ Canonical end-to-end examples** with **recommended HTTP status**, optional extra headers (**`Allow`** for **405**), and exact **`message`** text aligned with **`test_h8_error_messages_match_failure_response_spec`** when the reference handler emits that code. | Review this file; **`tests/test_http_handler.py`** (**H8**). |
| FR2 | **`README.md`** **§ Troubleshooting** links **`docs/SPEC_WEBHOOK_FAILURE_RESPONSES.md`** and calls out **§ Canonical end-to-end examples** (anchor **`#canonical-end-to-end-examples`**) for gateway / mock fixtures. | Review **README.md**; **SPEC_README_OPERATOR_SECTIONS** **OP4**. |
| FR3 | **`src/replayt_lifecycle_webhooks/handler.py`** module docstring points to **§ Canonical end-to-end examples** in this spec (same anchor or explicit section name). | Review **handler.py** docstring. |
| FR4 | **SPEC_MINIMAL_HTTP_HANDLER** links **§ Canonical end-to-end examples** from the JSON response-body paragraph. | Review **SPEC_MINIMAL_HTTP_HANDLER.md**. |
| FR5 | Optional **JSON fixtures** under **`tests/fixtures/`** (or similar), if added for contract tests, **must** match canonical bodies byte-for-byte (compact JSON) and cite this spec in a comment or **README** under that folder—**no** drift between doc and files. | Review fixtures when present; otherwise **N/A**. |

## Related docs

- **[SPEC_WEBHOOK_SIGNATURE.md](SPEC_WEBHOOK_SIGNATURE.md)** — **401** / **403** policy, leakage rules, v1 MAC scope.
- **[SPEC_MINIMAL_HTTP_HANDLER.md](SPEC_MINIMAL_HTTP_HANDLER.md)** — reference handler, **H1–H8**, status table.
- **[EVENTS.md](EVENTS.md)** — supported **`event_type`** values; unknown types after verify.
- **[README.md](../README.md)** — integrator entry and operator runbook pointer.
- **[SPEC_STRUCTURED_LOGGING_REDACTION.md](SPEC_STRUCTURED_LOGGING_REDACTION.md)** — tested redaction helpers and integrator extension points.
- **[SPEC_REPLAY_PROTECTION.md](SPEC_REPLAY_PROTECTION.md)** — when to use **`replay_rejected`** vs idempotent **2xx** for duplicates.
