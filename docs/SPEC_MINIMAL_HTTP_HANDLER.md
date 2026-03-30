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

**Response bodies (4xx / 405 / 422):** **`handle_lifecycle_webhook_post`** returns JSON per
**[SPEC_WEBHOOK_FAILURE_RESPONSES.md](SPEC_WEBHOOK_FAILURE_RESPONSES.md)** with
**`Content-Type: application/json; charset=utf-8`**, **`error`**, and **`message`**. **204** success responses have an empty body.
Canonical status + body fixtures for each code: **SPEC_WEBHOOK_FAILURE_RESPONSES** **§ Canonical end-to-end examples**
(anchor **`#canonical-end-to-end-examples`**).

## Public API (Python)

Stable names are re-exported from **`replayt_lifecycle_webhooks`** and listed in **`__all__`**.

| Symbol | Role |
| ------ | ---- |
| **`LifecycleWebhookHttpResult`** | Frozen dataclass: **`status`**, **`headers`** (tuple of pairs), **`body`** (bytes). |
| **`handle_lifecycle_webhook_post`** | Keyword-only: **`secret`**, **`method`**, **`body`** (bytes), **`headers`**, optional **`on_success`**, optional **`dedup_store`**, optional **`replay_policy`**. Returns **`LifecycleWebhookHttpResult`**; does not raise for client errors. |
| **`make_lifecycle_webhook_wsgi_app`** | Keyword-only: **`secret`**, optional **`on_success`**, optional **`dedup_store`**, optional **`replay_policy`**, optional **`webhook_diagnostics`** (**`None`** reads **`REPLAYT_LIFECYCLE_WEBHOOK_DIAGNOSTICS`**; **`True`**/**`False`** override). When enabled, emits one **INFO** record per request via **`format_safe_webhook_log_extra`** (see **[SPEC_STRUCTURED_LOGGING_REDACTION.md](SPEC_STRUCTURED_LOGGING_REDACTION.md)** **§ Optional diagnostic logging**). Returns a WSGI **application** callable. |

**Secret:** Passed by the caller only (same rule as **`verify_lifecycle_webhook_signature`**). The library does not read the environment.

**Headers:** **`handle_lifecycle_webhook_post`** accepts a **`Mapping[str, str]`** or an iterable of **`(name, value)`** pairs. Names are compared case-insensitively after lowercasing. If the same header name appears more than once, the **last** value wins after normalization (match common single-header usage; duplicate **`Replayt-Signature`** values are otherwise undefined—see **SPEC_WEBHOOK_SIGNATURE**).

**JSON payload:** After verification, the body is decoded as UTF-8 and parsed with **`json.loads`**. If neither **`dedup_store`** nor **`replay_policy`** is set, the parsed value may be any JSON type and **`on_success`** receives it. If either hook is set, the payload must be a JSON object accepted by **`parse_lifecycle_webhook_event`** (non-object top-level JSON → **400** **`invalid_payload_shape`**; validation failure → **422** **`unknown_event_type`**), and **`on_success`** still receives the parsed **`dict`**. Callers without hooks who require an object should check **`isinstance(payload, dict)`** in **`on_success`**. For **run** / **approval** lifecycle objects, **[EVENTS.md](EVENTS.md)** and **`replayt_lifecycle_webhooks.events`** describe the normative shapes.

## WSGI adapter behavior

- Reads **`REQUEST_METHOD`**, **`wsgi.input`**, and **`CONTENT_LENGTH`** (missing or non-integer → length **0**; negative length is clamped to **0**).
- Builds header names from **`HTTP_*`** keys using the usual underscore-to-hyphen mapping (e.g. **`HTTP_REPLAYT_SIGNATURE`** → **`Replayt-Signature`**). Non-**`str`** header values are skipped.
- Does not implement chunked request bodies or request size limits; production deployments should enforce limits at the server or proxy.

## Acceptance tests (H1–H12)

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
| **H9** | With **`replay_policy`**, valid MAC and stale **`occurred_at`** → **422** **`replay_rejected`**; **`on_success`** not called. | **`tests/test_replay_protection.py`** — **`test_rp4_stale_occurred_at_valid_mac_replay_rejected_no_on_success`** |
| **H10** | With **`dedup_store`**, two POSTs with the same **`event_id`** and valid MACs → **204** both times; **`on_success`** runs once. | **`tests/test_replay_protection.py`** — **`test_rp5_dedup_store_second_post_204_without_on_success`** |
| **H11** | With replay/dedupe hooks enabled, verified body that is JSON but not a top-level object → **400** **`invalid_payload_shape`**. | **`tests/test_replay_protection.py`** — **`test_replay_hooks_reject_non_object_json`** |
| **H12** | With replay/dedupe hooks enabled, unknown **`event_type`** → **422** **`unknown_event_type`**. | **`tests/test_replay_protection.py`** — **`test_replay_hooks_unknown_event_type_422`** |

Rows **H9**–**H12** match **[SPEC_REPLAY_PROTECTION.md](SPEC_REPLAY_PROTECTION.md)** optional **`handle_lifecycle_webhook_post`** parameters (**backlog `f9677140`**). Integrators can still add policy in **`on_success`** or outer wrappers beyond these hooks.

## Related docs

- **[SPEC_HTTP_SERVER_ENTRYPOINT.md](SPEC_HTTP_SERVER_ENTRYPOINT.md)** — optional **reference server**: one documented
  **`python -m` / CLI** command, **POST** route, **`GET /health`**, optional-deps posture, acceptance **S1–S13**.
- **[SPEC_REFERENCE_HTTP_SERVER_ROUTE_MAP.md](SPEC_REFERENCE_HTTP_SERVER_ROUTE_MAP.md)** — compact **route / status** matrix for the reference listener (backlog **`b4c68e50`**).
- **[SPEC_AUTOMATED_TESTS.md](SPEC_AUTOMATED_TESTS.md)** — CI **`pytest`** entrypoint; suite must cover verification (and
  parsing where handler tests apply), not placeholder smoke tests.
- **[SPEC_WEBHOOK_SIGNATURE.md](SPEC_WEBHOOK_SIGNATURE.md)** — verification procedure, **401/403** guidance, v1 header format.
- **[EVENTS.md](EVENTS.md)** and **`replayt_lifecycle_webhooks.events`** — normative lifecycle JSON contract and typed parsing after a successful parse (see **README**).
- **[README.md](../README.md)** — copy-paste examples for **`handle_lifecycle_webhook_post`** and **`make_lifecycle_webhook_wsgi_app`**.
- **[SPEC_WEBHOOK_FAILURE_RESPONSES.md](SPEC_WEBHOOK_FAILURE_RESPONSES.md)** — stable JSON **`error`** codes, HTTP mapping, and logging boundaries for operators.
- **[SPEC_INTEGRATOR_ASGI_VERIFIED_FIRST.md](SPEC_INTEGRATOR_ASGI_VERIFIED_FIRST.md)** — **FastAPI** / **Starlette** verified-first pattern; bridges this handler spec to ASGI apps (**AF1**–**AF7**).
- **[SPEC_REPLAY_PROTECTION.md](SPEC_REPLAY_PROTECTION.md)** — post-verify freshness, dedupe store, handler hooks (**RP2**); traceability **H9**–**H12** above.
- **[SPEC_SQLITE_IDEMPOTENCY_STORE.md](SPEC_SQLITE_IDEMPOTENCY_STORE.md)** — optional **SQLite** **`dedup_store`** implementation (**SQ4**); wiring shape under **§ Wiring into the minimal HTTP handler**.
- **[SPEC_STRUCTURED_LOGGING_REDACTION.md](SPEC_STRUCTURED_LOGGING_REDACTION.md)** — redaction helpers when logging headers or structured metadata; optional **per-request** diagnostics on this handler and the reference **serve** path (**§ Optional diagnostic logging**, backlog **`0bab43f3`**, **pytest** **LG1–LG4**).
