# Spec: incoming webhook signature verification

**Backlog:** Implement HMAC (or documented) request signing verification (`35f984f8-67cc-48bf-9385-0ec73a054314`).  
**Prior:** Define signed webhook verification API with explicit consumer contract (`3d375c9a-f0d6-42be-b88c-bb25d61f5c50`); copy-paste verification helper (`46f495d3-bf67-443b-859e-ebd9cb5ffbd6`).  
**Audience:** Spec gate (2b), Builder (3), Tester (4), integrators, maintainers.

## Problem

Operators need to **authenticate** HTTP payloads before handling replayt (or compatible automation) **run** and **approval** lifecycle events. The package name promises **signed** webhooks; verification must be **small**, **testable**, and safe to **copy into** a handler with minimal glue code.

## Goals

- Ship **one primary public helper** — **`verify_lifecycle_webhook_signature`** — plus minimal types and exceptions
  re-exported from the package, answering: “Does this raw request body match the signature, given the shared secret and
  relevant headers?”
- Enforce a **single verification path** for authentic traffic: every accepted webhook must pass through this helper
  (or logic that is **byte-for-byte equivalent** to this spec). Integrators must not add a parallel “trust JSON only”
  path for the same endpoint.
- Prefer **`hmac` / `hashlib` in the standard library** unless replayt’s documented algorithm requires otherwise.
- **No framework** in scope for this backlog: no Starlette/FastAPI/Flask middleware as the *required* delivery path—only the verification primitive. Integrators **should** wrap the primitive in their HTTP stack so failures map to **401/403**
  as below.
- Publish an **explicit consumer contract**: required headers, body rules, **signing scheme version**, **clock skew / replay policy**, **secret configuration convention**, **HTTP error expectations**, and **ordered verification steps** integrators can follow without reading implementation code.

## Signing scheme version

| Identifier | Meaning |
| ---------- | ------- |
| **v1** (`replayt-lifecycle-hmac-sha256-v1`) | HMAC-SHA256 over the **raw request body bytes**, MAC compared to the value in **`Replayt-Signature`** as specified below. |

**Wire format for v1**

- There is **no separate version header or JSON field** in v1. Compliance with v1 is: body + `Replayt-Signature` match this document and **[`REPLAYT_WEBHOOK_SIGNING.md`](reference-documentation/REPLAYT_WEBHOOK_SIGNING.md)**.
- **Future schemes** (e.g. JWS, v2 MAC): this repo will introduce a **discoverable version** (recommended: a dedicated header such as `Replayt-Signature-Version` and/or a structured signature string) and bump **CHANGELOG.md**, tests, and this spec. Integrators should **reject** unknown schemes unless they explicitly support them.

## Consumer contract (normative)

### Required inputs from the HTTP request

| Item | Requirement |
| ---- | ----------- |
| **Raw body** | **Bytes** exactly as read from the HTTP layer for the POST (or equivalent) **before** JSON parsing or other mutation. Any transformation (whitespace normalization, charset transcoding) **invalidates** the MAC unless upstream documents otherwise. |
| **Header `Replayt-Signature`** | **Required** for v1. HTTP header names are case-insensitive; use spelling **`Replayt-Signature`** in documentation and in the package constant **`LIFECYCLE_WEBHOOK_SIGNATURE_HEADER`**. |
| **Shared secret** | Configured out of band between sender and receiver. **UTF-8** encoding applies when the secret is provided as a Python `str` (see Python API below). **Recommended:** load from a process environment variable (see **Secret configuration**). |

**Secret configuration (operators / integrators)**

- The library accepts the secret only as an argument to **`verify_lifecycle_webhook_signature`**; it does **not** read
  environment variables itself.
- **Recommended environment variable name:** **`REPLAYT_LIFECYCLE_WEBHOOK_SECRET`** — shared secret as a string (UTF-8
  when encoded for HMAC). Document this name in **README.md** so operators and platforms align on one convention.
- **Operational hygiene:** inject the secret via your platform’s secret store or env; **do not** commit it, **do not**
  print it in startup banners, and **do not** log it when loading configuration.

**Header value format (v1)**

- Either `sha256=` followed by a **64-character** hexadecimal digest (HMAC-SHA256 of the raw body), **or** the same 64-character hex string **without** the `sha256=` prefix.
- Hex digits may be uppercase or lowercase; comparison must be **constant-time** on the decoded digest octets (see Cryptographic hygiene).

**Body “format”**

- Payload **may** be JSON or any other bytes; the verifier treats the body as **opaque octets**. Content-Type is **not** part of the MAC for v1.
- When the body is JSON consumed via **`replayt_lifecycle_webhooks.events`**, the **field contract** (envelope,
  **`schema_version`**, **`event_type`**, **`detail`**) is defined in **[EVENTS.md](EVENTS.md)**. That contract evolves
  independently of signing scheme **v1** (payload **SemVer-style** rules vs **HMAC v1** in this spec).

### Clock skew, timestamps, and replay

| Topic | Policy (v1) |
| ----- | ----------- |
| **Clock skew** | **Not applicable** to MAC verification alone: v1 does **not** include a normative timestamp in the signed material or required headers. |
| **Replay / freshness** | **Out of contract for v1.** Integrators who need bounded replay windows must enforce **application-level** controls (e.g. event IDs, idempotency stores, optional middleware that checks a future upstream timestamp if one is added to the contract). |
| **If upstream adds a timestamp later** | Update **[`REPLAYT_WEBHOOK_SIGNING.md`](reference-documentation/REPLAYT_WEBHOOK_SIGNING.md)**, this spec, and **CHANGELOG.md**; add **unit tests** for **acceptable skew** and **rejection of expired** (or stale) deliveries **without** real time/network (inject clock or fixed instants). Until then, acceptance criteria that mention “expired/skewed timestamp” are **N/A**.

### Verification procedure (integrators)

1. Read the **raw body** as `bytes` from the HTTP stack.
2. Read the **`Replayt-Signature`** header value as a string (your framework’s API may merge duplicates; if multiple values exist, behavior is **undefined** unless upstream specifies—prefer the single value replayt sends).
3. Call **`verify_lifecycle_webhook_signature(secret=…, body=…, signature=…)`** (or equivalent logic per this spec) **before** parsing the body as JSON or acting on the event.
4. On success, proceed; on failure, return **401** or **403** (or your policy) and **do not** treat the payload as authentic.

### HTTP responses and logging (normative for integrators)

Failures from verification are **authentication / integrity** failures. When exposing an HTTP webhook endpoint:

| Outcome | Suggested HTTP status | Notes |
| ------- | -------------------- | ----- |
| Missing or empty signature header | **401 Unauthorized** | Request did not present verifiable credentials. |
| Malformed signature value (not valid v1 hex / length) | **401 Unauthorized** | Treat as failed authentication; avoid distinguishing details that aid probing. |
| Well-formed signature that does not match body/secret | **403 Forbidden** (or **401**) | Either is acceptable; pick one policy per deployment and stay consistent. |

**Responses and logs must not leak secret material:**

- Do **not** include the **raw secret**, the **full `Replayt-Signature` header value**, or the **computed MAC** in HTTP
  response bodies, client-facing error JSON, or **production** logs at default levels.
- Exception messages raised by **`verify_lifecycle_webhook_signature`** are for **server-side** handling; map them to
  **generic** client responses (plain text, empty body, or the stable JSON envelope in
  **[SPEC_WEBHOOK_FAILURE_RESPONSES.md](SPEC_WEBHOOK_FAILURE_RESPONSES.md)**) rather than echoing internal exception text if
  that text could reveal header fragments or digests.

**Tests (phase 4):** where the suite asserts log or response behavior, use fixtures; no requirement to spin up a full HTTP server unless the project already does so for integration tests.

## Upstream alignment (required before calling the work “done”)

Exact **header names**, **signature encoding** (hex vs base64, with or without a `sha256=` prefix, etc.), and the **signed material** (typically the raw body bytes, but could be a concatenation with timestamp) **must match replayt’s published webhook delivery contract** when such a document exists.

| Builder responsibility | Details |
| ---------------------- | ------- |
| Confirm the algorithm | If replayt documents HMAC-SHA256 over the raw body, implement that. If it documents another MAC or a canonical string, follow upstream. |
| Name the headers in API docs | Module docstring + **README** snippet must list the **actual** header names operators configure their HTTP stack to forward. |
| Track drift | If upstream changes signing rules, bump tests and document in **CHANGELOG.md**; consider a short note in **docs/SPEC_REPLAYT_DEPENDENCY.md** if the change ties to a **replayt** version floor. |

If upstream prose is hard to find, capture the authoritative reference (URL, version, or a checked-in excerpt under **`docs/reference-documentation/`**) and cite it from this spec in a follow-up edit.

**Authority in this repo:** **[`docs/reference-documentation/REPLAYT_WEBHOOK_SIGNING.md`](reference-documentation/REPLAYT_WEBHOOK_SIGNING.md)** — v1: HMAC-SHA256 over the raw body; header **`Replayt-Signature`** with value **`sha256=<hex>`** or bare hex. Upstream **replayt** `0.4.25` does not ship HTTP webhook signing docs in the installed package; treat that file as the consumer contract until upstream publishes a delivery spec.

## Contract (package behavior)

### Public API (Python)

- **Module:** implementation lives under **`src/replayt_lifecycle_webhooks/`** (e.g. **`signature.py`**), with **stable names re-exported** from **`replayt_lifecycle_webhooks`** (`__init__.py`) and listed in **`__all__`**.
- **Callable:** **`verify_lifecycle_webhook_signature`** — keyword-only parameters **`secret: str | bytes`**, **`body: bytes`**, **`signature: str | None`** (header value passed in by the caller after reading from HTTP).
- **Callable (dev / tests):** **`compute_lifecycle_webhook_signature_header`** — returns the **`sha256=<hex>`** header value for **`body`** using the same **v1** HMAC as verification; used by the local demo (**[SPEC_LOCAL_WEBHOOK_DEMO.md](SPEC_LOCAL_WEBHOOK_DEMO.md)**) and is **not** a substitute for upstream replayt delivery semantics.
- **Constants:** at minimum **`LIFECYCLE_WEBHOOK_SIGNATURE_HEADER`** (`Final[str]`) for the wire name **`Replayt-Signature`**.
- **Exceptions:** distinct types subclassing a small base (e.g. **`WebhookSignatureError`**) for **missing/empty signature**, **malformed format**, and **MAC mismatch** — stable names exported publicly.
- **Type hints:** required on all **public** functions and constants above.
- **Docstrings:** required on the public callable and exception classes; document **parameters**, **raises**, **raw-body rule**, and **header value shapes** (align with this spec and README).

### Cryptographic hygiene

- Use **`hmac.compare_digest`** (or equivalent constant-time comparison) when comparing **equal-length** digest
  **bytes** (compare the decoded octets from the header to the HMAC output, not hex strings in a way that shortcuts
  constant-time properties).
- Do **not** log the **raw secret** or full **computed** MAC in production paths; tests may use fixed fixtures.
- Do **not** return secret or MAC material in HTTP responses; see **HTTP responses and logging** above.

### Dependencies

- Verification logic should rely on the **standard library** first. Add a third-party dependency **only** if replayt’s contract requires it; document the reason in **CHANGELOG.md** and this spec.

### Non-goals (this backlog)

- HTTP server, routing, retries, or replayt client calls.
- Mandatory **timestamp** validation for v1 — see **Clock skew, timestamps, and replay** above.

## Acceptance criteria (checklist)

Use this list for Spec gate, Builder, and Tester sign-off.

| # | Criterion | Verification |
|---|-----------|--------------|
| W1 | Public API documents **expected headers** and **raw body** usage at a high level (docstring + README pointer). | Review `src/…` and **README.md**. |
| W2 | README includes a **short, copy-paste-oriented** example (imports + one call) and links to this spec. | Review **README.md**. |
| W3 | Unit tests cover **valid signature**, **wrong secret**, **tampered body** (body bytes changed after signing), and **missing required header(s)** / malformed header value. | `pytest`; no network/socket use in these tests. |
| W3b | **Expired / skewed timestamp:** **N/A for v1** — spec and reference doc state there is no timestamp in the v1 contract. If a timestamp is added later, tests must cover **tolerance** and **rejection** without real time/network. | Review this spec + tests when contract changes. |
| W4 | No **network I/O** in the test suite for this feature (fixtures only). | Grep/review tests; CI must not require connectivity for them. |
| W5 | Implementation matches **replayt’s documented** signing rules; reference cited in docs or **reference-documentation**. | Maintainer review. |
| W6 | User-visible API or behavior change reflected in **CHANGELOG.md** under **Unreleased** when implemented. | Review **CHANGELOG.md** at release. |
| W7 | **Signing scheme v1** and **clock skew / replay policy** are documented in this spec and summarized in **REPLAYT_WEBHOOK_SIGNING.md**. | Review both files. |
| W8 | **Single path:** Handlers do not accept the same URL with “unsigned JSON” as an alternate success path; verification runs before trusting payload. | Code review of example / integrator glue; optional test if the repo ships a sample handler. |
| W9 | **HTTP safety:** On verification failure, integrator guidance documents **401** and/or **403** (per spec table) and **forbids** echoing secret, full signature header, or computed MAC in responses or production logs. | Review **README.md** + this spec; Tester may add a focused test if the repo exposes a reference HTTP wrapper. |
| W10 | **Secret configuration:** **README.md** documents the recommended env var **`REPLAYT_LIFECYCLE_WEBHOOK_SECRET`** (and that the library receives the secret only via the API). | Review **README.md**. |

## Suggested test fixtures (for Builder / Tester)

- **Secret:** fixed byte/string values only (no env var reads in unit tests).
- **Body:** small JSON or arbitrary bytes; **tampered** case = same body with one octet flipped.
- **Signature:** precomputed using the **same** algorithm the implementation uses, so tests remain deterministic.
- **Wrong secret:** MAC computed with a different secret than passed to `verify_lifecycle_webhook_signature`.

## Related docs

- **[SPEC_AUTOMATED_TESTS.md](SPEC_AUTOMATED_TESTS.md)** — CI **`pytest tests -q`** invariant; minimum suite coverage
  including **W3** verification paths; placeholder smoke tests forbidden.
- **[README.md](../README.md)** — integrator entry and quick example.
- **[EVENTS.md](EVENTS.md)** and **`replayt_lifecycle_webhooks.events`** — normative lifecycle JSON field contract and **`parse_lifecycle_webhook_event`** after verification (see **README** overview).
- **[SPEC_MINIMAL_HTTP_HANDLER.md](SPEC_MINIMAL_HTTP_HANDLER.md)** — optional **`handle_lifecycle_webhook_post`** and WSGI factory, status table, **H1–H8**.
- **[SPEC_LOCAL_WEBHOOK_DEMO.md](SPEC_LOCAL_WEBHOOK_DEMO.md)** — dev **sender** contract; signing **must** stay **v1**-compatible with this spec.
- **[SPEC_WEBHOOK_FAILURE_RESPONSES.md](SPEC_WEBHOOK_FAILURE_RESPONSES.md)** — operator-facing JSON error envelope, **`error`** codes, post-verify failures, replay/freshness notes for v1.
- **[SPEC_REPLAYT_DEPENDENCY.md](SPEC_REPLAYT_DEPENDENCY.md)** — **replayt** version floor and bump policy.
- **[DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)** — small public surfaces and explicit contracts.
