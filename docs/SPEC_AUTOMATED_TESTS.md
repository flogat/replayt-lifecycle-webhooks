# Spec: automated tests and CI entrypoint

**Backlogs (normative traceability):**

- Replace smoke-only test with real package behavior assertions (`a91574f0-1e57-4b34-9922-763f92448a18`).
- Ship contract or integration tests at the replayt boundary (`d9d6b302-40c7-4e08-af2d-faabb923f2fe`) — see **[SPEC_REPLAYT_BOUNDARY_TESTS.md](SPEC_REPLAYT_BOUNDARY_TESTS.md)**.
- Replace scaffold smoke tests with unit and boundary coverage (`2b4c6927-573a-463c-b59f-f2f91dfb6381`) — rows **A6–A10** under **Backlog `2b4c6927`** below.

**Audience:** Spec gate (2b), Builder (3), Tester (4), maintainers, contributors.

## Purpose and normative status

This document defines what the **pytest** suite must prove so **CI** fails when signature verification or JSON parsing
regresses. It matches **[DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)** (**observable automation**, **explicit contracts**):
failures in those areas must **break** automated tests, not pass via **`assert True`**.

Detailed matrices for each surface live in the feature specs; this file ties them to **one** CI command and **minimum**
behavioral coverage.

| Topic | Where it lives |
| ----- | -------------- |
| Signature verification behavior and **W** rows | **[SPEC_WEBHOOK_SIGNATURE.md](SPEC_WEBHOOK_SIGNATURE.md)** |
| Optional HTTP handler status codes (**H1–H8**) | **[SPEC_MINIMAL_HTTP_HANDLER.md](SPEC_MINIMAL_HTTP_HANDLER.md)** |
| Reference HTTP server entrypoint (**S1–S8**), when implemented | **[SPEC_HTTP_SERVER_ENTRYPOINT.md](SPEC_HTTP_SERVER_ENTRYPOINT.md)** |
| Lifecycle JSON shapes and typed parsing (**E***, **T***) | **[EVENTS.md](EVENTS.md)** |
| **replayt** dependency / doc contract | **[SPEC_REPLAYT_DEPENDENCY.md](SPEC_REPLAYT_DEPENDENCY.md)** |
| **`replayt` import / API stability at the dependency seam** | **[SPEC_REPLAYT_BOUNDARY_TESTS.md](SPEC_REPLAYT_BOUNDARY_TESTS.md)** |

## CI entrypoint (invariant)

- **Project convention:** contributors and docs refer to:

  ```bash
  pytest tests -q
  ```

- **CI** (`.github/workflows/ci.yml`) may invoke the same suite as  
  `python -m pytest tests -q` plus optional flags (for example `--tb=short`). That is **equivalent** for acceptance as long
  as it collects **only** tests under **`tests/`** and does not require network I/O for the signing / parsing / handler
  unit tests mandated in the specs above.

- **Do not** change the workflow to a different test root or drop **`tests/`** without updating this document,
  **README.md**, and **CHANGELOG.md**.

## Prohibited patterns

- **No placeholder “smoke” module** whose **only** behavioral assertion is **`assert True`** (or an empty **`pass`**) while
  claiming the package is covered. If **`tests/test_smoke.py`** (or similar) still exists after focused modules cover
  **§ Minimum behavioral coverage** below, **delete** it or merge any unique scenario into a properly named test module.
- **Do not** rely on a single no-op test so **`pytest`** “passes” without exercising verification or parsing paths.

## Minimum behavioral coverage

The suite **must** include **network-free** **pytest** tests that fail when the following regress:

1. **Signature verification** — Exercises **`verify_lifecycle_webhook_signature`** (and, if the optional handler is in
   scope, the same rules through **`handle_lifecycle_webhook_post`** where **SPEC_MINIMAL_HTTP_HANDLER** already requires
   it). At minimum, outcomes aligned with **SPEC_WEBHOOK_SIGNATURE** checklist **W3** (valid MAC, wrong secret, tampered
   body, missing or malformed **`Replayt-Signature`**). Existing coverage is expected under **`tests/test_webhook_signature.py`**
   (and related handler tests per **H** rows).
2. **JSON parsing / lifecycle events** — Exercises **`parse_lifecycle_webhook_event`** on representative payloads and on
   invalid or unknown shapes so validation regressions fail. Align with **EVENTS.md** rows **T3–T5** (fixtures, invalid
   **`detail`**, unknown **`event_type`**, missing required envelope fields). Existing coverage is expected under
   **`tests/test_lifecycle_events.py`** and **`tests/fixtures/events/`**.

Other modules (**mission** doc anchors, **replayt** dependency doc checks, and so on) may coexist; they do **not** replace
items **1** and **2**.

When **[SPEC_HTTP_SERVER_ENTRYPOINT.md](SPEC_HTTP_SERVER_ENTRYPOINT.md)** is implemented, the suite **must** additionally
include **network-free** tests that fail if the documented **POST** webhook path or **`GET /health`** (or the spec-chosen
health path) regresses per checklist **S3**, **S4**, and **S6** in that document. Those tests **must not** replace items
**1**–**3** above.

3. **Replayt boundary (dependency seam)** — At least one module **imports `replayt`** and asserts **documented** public
   symbols (**`RunResult`**, **`RunFailed`**, **`ApprovalPending`**) per **[SPEC_REPLAYT_BOUNDARY_TESTS.md](SPEC_REPLAYT_BOUNDARY_TESTS.md)**.
   This is **in addition to** items **1** and **2**, not a substitute. Existing **`tests/test_replayt_dependency.py`** work
   counts toward the **version / pyproject** story only when combined with those **import** checks (same module or a
   dedicated **`tests/test_replayt_boundary.py`**).

## Acceptance criteria (checklist)

Use for Spec gate, Builder, and Tester sign-off for backlog **`a91574f0`**. Rows **R1–R5** in
**[SPEC_REPLAYT_BOUNDARY_TESTS.md](SPEC_REPLAYT_BOUNDARY_TESTS.md)** cover backlog **`d9d6b302`**.

| # | Criterion | Verification |
|---|-----------|--------------|
| A1 | No **`tests/`** file is the **only** “package works” story via **`assert True`** / empty **`pass`** alone; remove or replace **`tests/test_smoke.py`** when redundant. | Code review; **`rg 'assert True' tests`** |
| A2 | **pytest** exercises **`verify_lifecycle_webhook_signature`** for success and representative failures (**W3** family). | **`pytest tests -q`**; review **`tests/test_webhook_signature.py`** |
| A3 | **pytest** exercises **`parse_lifecycle_webhook_event`** (or the handler’s verify-then-parse path) on valid and invalid lifecycle JSON per **EVENTS.md** **T3–T5**. | **`pytest tests -q`**; review **`tests/test_lifecycle_events.py`** / fixtures |
| A4 | CI runs **`pytest tests -q`** or **`python -m pytest tests -q`** (optional extra flags) against **`tests/`**. | Review **`.github/workflows/ci.yml`** |
| A5 | Doc or contract changes to the CI command or minimum coverage appear under **CHANGELOG.md** **Unreleased** when user-visible to contributors. | Release hygiene |

## Backlog `2b4c6927`: smoke replacement and module imports

Checklist rows for **Replace scaffold smoke test with real unit and boundary tests**
(`2b4c6927-573a-463c-b59f-f2f91dfb6381`). These extend **A1–A5**; they do not replace **A1–A5** or the **replayt**
boundary rows **R1–R5**.

| # | Criterion | Verification |
|---|-----------|--------------|
| A6 | At least one **golden vector**: fixed UTF-8 secret, fixed raw body bytes, and a **committed** `Replayt-Signature` value (`sha256=…`) checked by **`verify_lifecycle_webhook_signature`** without reusing ad-hoc signing helpers for that vector. | **`tests/test_webhook_signature.py`** — **`test_golden_vector_committed_replayt_signature`** |
| A7 | Invalid JSON after a good signature maps to the handler contract (**H4**). | **`tests/test_http_handler.py`** — **`test_h4_bad_json_400_after_good_signature`** |
| A8 | Unknown **`event_type`** is rejected during parsing (**T4** family). | **`tests/test_lifecycle_events.py`** — **`test_parse_rejects_unknown_event_type`** |
| A9 | After verify, the success path invokes the caller hook (**H7**). | **`tests/test_http_handler.py`** — **`test_on_success_called_after_verify`** |
| A10 | Tests **`import`** **`replayt_lifecycle_webhooks.signature`**, **`replayt_lifecycle_webhooks.handler`**, and **`replayt_lifecycle_webhooks.events`** directly (not only the package root), and exercise **`replayt_lifecycle_webhooks.serve`** where the reference server is in tree. | Search **`tests/`**; **`tests/test_reference_server.py`** for **serve** |

## Related docs

- **[README.md](../README.md)** — quick start; see **Running tests** for the canonical command.
- **[MISSION.md](MISSION.md)** — success metrics and alignment with what CI runs.
- **[DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)** — observable automation and explicit contracts.
- **[SPEC_REPLAYT_BOUNDARY_TESTS.md](SPEC_REPLAYT_BOUNDARY_TESTS.md)** — **`replayt`** import and documented symbol checks.
