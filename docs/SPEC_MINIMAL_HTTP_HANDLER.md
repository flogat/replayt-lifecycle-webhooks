# Spec: minimal HTTP POST handler for lifecycle webhooks

**Backlog:** Expose one minimal HTTP handler for lifecycle POSTs (`6e1255ce-7dc2-42d8-b25b-135cf0534019`).  
**Audience:** Design gate (5b), integrators, maintainers.

## Problem

Integrators want a **small, copy-friendly** way to turn **method + raw body + headers** into stable HTTP outcomes for signed lifecycle POSTs, without pulling in a mandatory web framework from this package.

## Goals

- One **framework-agnostic** entry point that calls **`verify_lifecycle_webhook_signature`** on the raw body **before** **`json.loads`**.
- Optional **stdlib WSGI** adapter for local runs and simple mounts (**`wsgiref`**, reverse proxies, etc.).
- Status codes aligned with **[SPEC_WEBHOOK_SIGNATURE.md](SPEC_WEBHOOK_SIGNATURE.md)** (**401** / **403** table): missing or malformed header → **401**; well-formed MAC mismatch → **403**.
- Tests run **without network**; at least one path uses a fake request view and one uses an in-process WSGI call (see **H1**).

Signing rules, header shapes, and crypto hygiene remain defined in **SPEC_WEBHOOK_SIGNATURE.md** and **[reference-documentation/REPLAYT_WEBHOOK_SIGNING.md](reference-documentation/REPLAYT_WEBHOOK_SIGNING.md)**.

## Normative HTTP status table

Handled in order: method check → signature verification → UTF-8 decode → JSON parse → optional success hook.

| Status | When |
| ------ | ---- |
| **405** | Request method is not **POST**. Response includes **`Allow: POST`** where the API returns headers (callable result and WSGI). |
| **401** | **`Replayt-Signature`** missing, empty, or malformed (same classes as **`WebhookSignatureMissingError`** / **`WebhookSignatureFormatError`** from verification). |
| **403** | Header well-formed but MAC does not match body and secret (**`WebhookSignatureMismatchError`**). |
| **400** | Verification succeeded but body is not valid UTF-8 or not valid JSON text (**`UnicodeDecodeError`** / **`json.JSONDecodeError`**), or (when **`dedup_store`** / **`replay_policy`** is set) JSON is not a top-level object. |
| **422** | Unknown lifecycle **`event_type`** / validation failure (**`unknown_event_type`**), or **`occurred_at`** outside the replay window when **`replay_policy`** checks freshness (**`replay_rejected`**). |
| **204** | Success: verified, parsed JSON, empty response body; also when **`dedup_store`** treats a duplicate **`event_id`** as an idempotent ack (**`on_success`** not invoked again). |

**H5 (ordering):** If verification fails, the implementation must **not** return **400** for JSON errors. Garbage bodies with missing or wrong MAC must yield **401** or **403**, not **400**.

**Response bodies (4xx / 405):** **`handle_lifecycle_webhook_post`** returns JSON per
**[SPEC_WEBHOOK_FAILURE_RESPONSES.md](SPEC_WEBHOOK_FAILURE_RESPONSES.md)** with
**`Content-Type: application/json; charset=utf-8`**, **`error`**, and **`message`**. **204** success responses have an empty body.

## Public API (Python)

Stable names are re-exported from **`replayt_lifecycle_webhooks`** and listed in **`__all__`**.

| Symbol | Role |
| ------ | ---- |
| **`LifecycleWebhookHttpResult`** | Frozen dataclass: **`status`**, **`headers`** (tuple of pairs), **`body`** (bytes). |
| **`handle_lifecycle_webhook_post`** | Keyword-only: **`secret`**, **`method`**, **`body`** (bytes), **`headers`**, optional **`on_success`**, optional **`dedup_store`**, optional **`replay_policy`**. Returns **`LifecycleWebhookHttpResult`**; does not raise for client errors. |
| **`make_lifecycle_webhook_wsgi_app`** | Keyword-only: **`secret`**, optional **`on_success`**, optional **`dedup_store`**, optional **`replay_policy`**. Returns a WSGI **application** callable. |

**Secret:** Passed by the caller only (same rule as **`verify_lifecycle_webhook_signature`**). The library does not read the environment.

**Headers:** **`handle_lifecycle_webhook_post`** accepts a **`Mapping[str, str]`** or an iterable of **`(name, value)`** pairs. Names are compared case-insensitively after lowercasing. If the same header name appears more than once, the **last** value wins after normalization (match common single-header usage; duplicate **`Replayt-Signature`** values are otherwise undefined—see **SPEC_WEBHOOK_SIGNATURE**).

**JSON payload:** After verification, the body is decoded as UTF-8 and parsed with **`json.loads`**. The parsed value may be any JSON type; **`on_success`**, if provided, receives that value. Callers who require a JSON object should check **`isinstance(payload, dict)`** in **`on_success`** or in surrounding code. For **run** / **approval** lifecycle objects, **[EVENTS.md](EVENTS.md)** and **`replayt_lifecycle_webhooks.events`** describe the normative shapes; use **`parse_lifecycle_webhook_event`** when you need validation.

## WSGI adapter behavior

- Reads **`REQUEST_METHOD`**, **`wsgi.input`**, and **`CONTENT_LENGTH`** (missing or non-integer → length **0**; negative length is clamped to **0**).
- Builds header names from **`HTTP_*`** keys using the usual underscore-to-hyphen mapping (e.g. **`HTTP_REPLAYT_SIGNATURE`** → **`Replayt-Signature`**). Non-**`str`** header values are skipped.
- Does not implement chunked request bodies or request size limits; production deployments should enforce limits at the server or proxy.

## Acceptance tests (H1–H8)

| ID | Criterion | Checked by |
| -- | --------- | ---------- |
| **H1** | At least one test uses a **fake request** view (method, body, headers); at least one test exercises the **WSGI** path **in process** without sockets. | **`tests/test_http_handler.py`** (`test_h1_fake_request_object_end_to_end`, `test_wsgi_path_in_process`) |
| **H2** | Valid signature and valid JSON → **2xx** (**204**). | **`test_h2_success_2xx`** |
| **H3** | Missing, malformed, or mismatching MAC → **401** or **403** per table. | **`test_h3_bad_signature_4xx`** |
| **H4** | Valid signature, invalid JSON → **400**. | **`test_h4_bad_json_400_after_good_signature`** |
| **H5** | Invalid signature with invalid JSON → **401** or **403**, never **400**. | **`test_h5_verify_before_json_invalid_signature_bad_json_is_401_not_400`** |
| **H6** | Non-POST → **405** with **`Allow: POST`**. | **`test_method_not_allowed_405`**, **`test_wsgi_wrong_method_405`** |
| **H7** | **`on_success`** runs only after verification and successful JSON parse. | **`test_on_success_called_after_verify`** |
| **H8** | Client error bodies match **SPEC_WEBHOOK_FAILURE_RESPONSES** stable codes and operator-facing **`message`** strings. | **`test_h8_error_messages_match_failure_response_spec`** |

When **[SPEC_REPLAY_PROTECTION.md](SPEC_REPLAY_PROTECTION.md)** is implemented, optional handler parameters (**dedupe
store**, **replay policy**, injectable **`now`**) **may** extend this table with additional rows (e.g. **H9**–**H11**)
for **422** **`replay_rejected`** on stale **`occurred_at`** and **204** on idempotent duplicate **`event_id`** hits;
until then, integrators apply replay/idempotency logic inside **`on_success`** or outer wrappers per that spec.

## Related docs

- **[SPEC_HTTP_SERVER_ENTRYPOINT.md](SPEC_HTTP_SERVER_ENTRYPOINT.md)** — optional **reference server**: one documented
  **`python -m` / CLI** command, **POST** route, **`GET /health`**, optional-deps posture, acceptance **S1–S8**.
- **[SPEC_AUTOMATED_TESTS.md](SPEC_AUTOMATED_TESTS.md)** — CI **`pytest`** entrypoint; suite must cover verification (and
  parsing where handler tests apply), not placeholder smoke tests.
- **[SPEC_WEBHOOK_SIGNATURE.md](SPEC_WEBHOOK_SIGNATURE.md)** — verification procedure, **401/403** guidance, v1 header format.
- **[EVENTS.md](EVENTS.md)** and **`replayt_lifecycle_webhooks.events`** — normative lifecycle JSON contract and typed parsing after a successful parse (see **README**).
- **[README.md](../README.md)** — copy-paste examples for **`handle_lifecycle_webhook_post`** and **`make_lifecycle_webhook_wsgi_app`**.
- **[SPEC_WEBHOOK_FAILURE_RESPONSES.md](SPEC_WEBHOOK_FAILURE_RESPONSES.md)** — stable JSON **`error`** codes, HTTP mapping, and logging boundaries for operators.
- **[SPEC_REPLAY_PROTECTION.md](SPEC_REPLAY_PROTECTION.md)** — optional post-verify freshness, dedupe store, handler hooks (**RP2**, future **H9+**).
- **[SPEC_STRUCTURED_LOGGING_REDACTION.md](SPEC_STRUCTURED_LOGGING_REDACTION.md)** — redaction helpers when logging headers or structured metadata.
