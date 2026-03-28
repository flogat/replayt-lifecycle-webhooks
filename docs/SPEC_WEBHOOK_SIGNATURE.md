# Spec: incoming webhook signature verification

**Backlog:** Add copy-paste signature verification for incoming webhooks (`46f495d3-bf67-443b-859e-ebd9cb5ffbd6`).  
**Audience:** Spec gate (2b), Builder (3), Tester (4), integrators, maintainers.

## Problem

Operators need to **authenticate** HTTP payloads before handling replayt (or compatible automation) **run** and **approval** lifecycle events. The package name promises **signed** webhooks; verification must be **small**, **testable**, and safe to **copy into** a handler with minimal glue code.

## Goals

- Ship **one primary public helper** — **`verify_lifecycle_webhook_signature`** — plus minimal types and exceptions
  re-exported from the package, answering: “Does this raw request body match the signature, given the shared secret and
  relevant headers?”
- Prefer **`hmac` / `hashlib` in the standard library** unless replayt’s documented algorithm requires otherwise.
- **No framework** in scope for this backlog: no Starlette/FastAPI/Flask middleware as the *required* delivery path—only the verification primitive.

## Upstream alignment (required before calling the work “done”)

Exact **header names**, **signature encoding** (hex vs base64, with or without a `sha256=` prefix, etc.), and the **signed material** (typically the raw body bytes, but could be a concatenation with timestamp) **must match replayt’s published webhook delivery contract**.

| Builder responsibility | Details |
| ---------------------- | ------- |
| Confirm the algorithm | If replayt documents HMAC-SHA256 over the raw body, implement that. If it documents another MAC or a canonical string, follow upstream. |
| Name the headers in API docs | Module docstring + **README** snippet must list the **actual** header names operators configure their HTTP stack to forward. |
| Track drift | If upstream changes signing rules, bump tests and document in **CHANGELOG.md**; consider a short note in **docs/SPEC_REPLAYT_DEPENDENCY.md** if the change ties to a **replayt** version floor. |

If upstream prose is hard to find, capture the authoritative reference (URL, version, or a checked-in excerpt under **`docs/reference-documentation/`**) and cite it from this spec in a follow-up edit.

**Authority in this repo:** **[`docs/reference-documentation/REPLAYT_WEBHOOK_SIGNING.md`](reference-documentation/REPLAYT_WEBHOOK_SIGNING.md)** — HMAC-SHA256 over the raw body; header **`Replayt-Signature`** with value **`sha256=<hex>`** or bare hex. Upstream **replayt** `0.4.25` does not ship HTTP webhook signing docs in the installed package; treat that file as the consumer contract until upstream publishes a delivery spec.

## Contract (package behavior)

### Public API

- **Callable** **`verify_lifecycle_webhook_signature`** exported from the installable package (`replayt_lifecycle_webhooks`).
- **Document in the docstring** (and README):
  - **Parameters:** signing secret (type: `str` or `bytes`—pick one documented convention), **raw body** (`bytes`; callers must not pre-parse JSON before verification unless upstream signs a derived string), and **header values** (either explicit parameters or a small mapping type—document which headers are required vs optional).
  - **Expected headers / body shape** at a **high level** (e.g. “raw POST body as received; signature in header X”).
  - **Success vs failure:** either raise **distinct, documented exceptions** for “missing header”, “malformed header”, and “signature mismatch”, or return a **small result type**—choose one style and stick to it across tests and README.

### Cryptographic hygiene

- Use **`hmac.compare_digest`** (or equivalent constant-time comparison) when comparing computed vs provided signatures.
- Do **not** log the **raw secret** or full **computed** MAC in production paths; tests may use fixed fixtures.

### Dependencies

- Verification logic should rely on the **standard library** first. Add a third-party dependency **only** if replayt’s contract requires it; document the reason in **CHANGELOG.md** and this spec.

### Non-goals (this backlog)

- HTTP server, routing, retries, or replayt client calls.
- **Timestamp / replay-window** validation: **optional** follow-up unless replayt’s contract requires it for this backlog; if implemented, document tolerance and test it without real time/network.

## Acceptance criteria (checklist)

Use this list for Spec gate, Builder, and Tester sign-off.

| # | Criterion | Verification |
|---|-----------|--------------|
| W1 | Public API documents **expected headers** and **raw body** usage at a high level (docstring + README pointer). | Review `src/…` and **README.md**. |
| W2 | README includes a **short, copy-paste-oriented** example (imports + one call) and links to this spec. | Review **README.md**. |
| W3 | Unit tests cover **valid signature**, **wrong secret**, **tampered body** (body bytes changed after signing), and **missing required header(s)**. | `pytest`; no network/socket use in these tests. |
| W4 | No **network I/O** in the test suite for this feature (fixtures only). | Grep/review tests; CI must not require connectivity for them. |
| W5 | Implementation matches **replayt’s documented** signing rules; reference cited in docs or **reference-documentation**. | Maintainer review. |
| W6 | User-visible API or behavior change reflected in **CHANGELOG.md** under **Unreleased** when implemented. | Review **CHANGELOG.md** at release. |

## Suggested test fixtures (for Builder / Tester)

- **Secret:** fixed byte/string values only (no env var reads in unit tests).
- **Body:** small JSON or arbitrary bytes; **tampered** case = same body with one octet flipped.
- **Signature:** precomputed using the **same** algorithm the implementation uses, so tests remain deterministic.

## Related docs

- **[README.md](../README.md)** — integrator entry and quick example.
- **[SPEC_REPLAYT_DEPENDENCY.md](SPEC_REPLAYT_DEPENDENCY.md)** — **replayt** version floor and bump policy.
- **[DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)** — small public surfaces and explicit contracts.
