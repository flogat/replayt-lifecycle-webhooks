# Spec: automated tests and CI entrypoint

**Backlog:** Replace smoke-only test with real package behavior assertions (`a91574f0-1e57-4b34-9922-763f92448a18`).  
**Audience:** Spec gate (2b), Builder (3), Tester (4), maintainers, contributors.

## Purpose and normative status

This document defines what the **pytest** suite must prove so **CI** is a **regression signal**, not a presence check. It
implements **[DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)** (**observable automation**, **explicit contracts**): failures
in signature verification or JSON parsing must **break** automated tests, not pass via **`assert True`**.

Detailed matrices for each surface live in the feature specs; this file ties them to **one** CI command and **minimum**
behavioral coverage.

| Topic | Where it lives |
| ----- | -------------- |
| Signature verification behavior and **W** rows | **[SPEC_WEBHOOK_SIGNATURE.md](SPEC_WEBHOOK_SIGNATURE.md)** |
| Optional HTTP handler status codes (**H1–H7**) | **[SPEC_MINIMAL_HTTP_HANDLER.md](SPEC_MINIMAL_HTTP_HANDLER.md)** |
| Lifecycle JSON shapes and typed parsing (**E***, **T***) | **[EVENTS.md](EVENTS.md)** |
| **replayt** dependency / doc contract | **[SPEC_REPLAYT_DEPENDENCY.md](SPEC_REPLAYT_DEPENDENCY.md)** |

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

## Acceptance criteria (checklist)

Use for Spec gate, Builder, and Tester sign-off for backlog **`a91574f0`**.

| # | Criterion | Verification |
|---|-----------|--------------|
| A1 | No **`tests/`** file is the **only** “package works” story via **`assert True`** / empty **`pass`** alone; remove or replace **`tests/test_smoke.py`** when redundant. | Code review; **`rg 'assert True' tests`** |
| A2 | **pytest** exercises **`verify_lifecycle_webhook_signature`** for success and representative failures (**W3** family). | **`pytest tests -q`**; review **`tests/test_webhook_signature.py`** |
| A3 | **pytest** exercises **`parse_lifecycle_webhook_event`** (or the handler’s verify-then-parse path) on valid and invalid lifecycle JSON per **EVENTS.md** **T3–T5**. | **`pytest tests -q`**; review **`tests/test_lifecycle_events.py`** / fixtures |
| A4 | CI runs **`pytest tests -q`** or **`python -m pytest tests -q`** (optional extra flags) against **`tests/`**. | Review **`.github/workflows/ci.yml`** |
| A5 | Doc or contract changes to the CI command or minimum coverage appear under **CHANGELOG.md** **Unreleased** when user-visible to contributors. | Release hygiene |

## Related docs

- **[README.md](../README.md)** — quick start; see **Running tests** for the canonical command.
- **[MISSION.md](MISSION.md)** — success metrics and alignment with what CI runs.
- **[DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)** — observable automation and explicit contracts.
