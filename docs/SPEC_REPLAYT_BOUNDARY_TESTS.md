# Spec: replayt boundary (contract / integration) tests

**Backlog:** Ship contract or integration tests at the replayt boundary — `d9d6b302-40c7-4e08-af2d-faabb923f2fe`.  
**Audience:** Spec gate (2b), Builder (3), Tester (4), maintainers.

## Purpose and normative status

This document defines **automated tests at the integration seam between this package and the installed `replayt`
distribution**. It complements **[SPEC_AUTOMATED_TESTS.md](SPEC_AUTOMATED_TESTS.md)** (signature verification, lifecycle JSON
parsing, handler rows), which can pass without importing **`replayt`** application code.

**Problem:** If **replayt** renames public types, changes `__all__`, or drifts from the concepts this repo documents in
**[EVENTS.md](EVENTS.md)**, maintainers should discover that **here**—not only after integrators report production breakage.

**Scope:** Consumer-side **compatibility** with the **declared** **replayt** lower bound and with **documented** upstream
symbols. This repo does **not** run **replayt**’s own test suite or require network access to upstream services.

## Definitions

| Term | Meaning |
| ---- | ------- |
| **Unit / contract suite** | Tests for **`verify_lifecycle_webhook_signature`**, **`parse_lifecycle_webhook_event`**, optional HTTP handler, fixtures under **`tests/fixtures/`**, and doc/syntax guards—**[SPEC_AUTOMATED_TESTS.md](SPEC_AUTOMATED_TESTS.md)** minimum items **1–2** and checklist **A1–A5**. |
| **Replayt boundary tests** | Tests that **import the `replayt` package** and assert **documented** public symbols or version behavior, **or** (secondary) stubbed golden payloads **explicitly tied** in comments to **EVENTS.md** / reference docs as upstream-shaped examples **plus** a **direct `replayt` import** elsewhere in the same module for API stability. **Stub-only** tests **without** any **`import replayt`** do **not** satisfy this spec by themselves. |
| **Default CI install** | **`pip install -e ".[dev]"`** then **`python -m pytest tests -q`** (or equivalent flags), same as **[SPEC_AUTOMATED_TESTS.md](SPEC_AUTOMATED_TESTS.md)**. |

## Documented replayt Python symbols (normative for boundary tests)

**[EVENTS.md](EVENTS.md)** (§ *Replayt concepts*, informative table) names these **replayt** types as parallel to webhook
notifications:

| Symbol | Package | Rationale |
| ------ | ------- | --------- |
| **`RunResult`** | `replayt` | Documented mapping from run lifecycle semantics. |
| **`RunFailed`** | `replayt` | Documented mapping for failed runs. |
| **`ApprovalPending`** | `replayt` | Documented mapping for approval gates. |

**Builder requirement:** Boundary tests **must** verify that each symbol above is **importable** from **`replayt`** on the
**minimum supported version** resolved by CI (and locally). Prefer **`from replayt import RunResult, RunFailed, ApprovalPending`**
(or equivalent **`import replayt`** + **`getattr`**) so renames fail loudly.

If upstream removes or renames a symbol, **do not** silence the failure: update **EVENTS.md**, **CHANGELOG.md**, and the
**replayt** floor or compatibility notes per **[SPEC_REPLAYT_DEPENDENCY.md](SPEC_REPLAYT_DEPENDENCY.md)**.

**Optional extensions** (not required for backlog closure but encouraged):

- Assert **`replayt.__version_tuple__`** (or **`importlib.metadata.version("replayt")`**) ordering against the canonical
  **`replayt>=M.m.p`** line—**[tests/test_replayt_dependency.py](../tests/test_replayt_dependency.py)** already covers part
  of this; **merge or co-locate** boundary assertions so one module clearly owns the **API + version** story, or keep
  dependency parsing in **`test_replayt_dependency.py`** and add **`test_replayt_boundary.py`** for **import** checks only—
  either layout is acceptable if **§ Module layout** below is satisfied.

## Relationship to existing tests

- **`tests/test_replayt_dependency.py`** — **pyproject.toml** canonical line, README strings, matrix alignment, installed
  version **≥** floor. **Counts** toward boundary coverage **only when** extended with **§ Documented replayt Python symbols**
  checks **or** paired with a sibling module that performs those imports in the same **pytest** run.
- **`tests/test_lifecycle_events.py`** + **`tests/fixtures/events/`** — Wire JSON and **`parse_lifecycle_webhook_event`**;
  they are **not** a substitute for **`import replayt`** boundary tests.

## Network and CI invariants

- **No undisclosed network I/O** in **`tests/`** on the default CI path. Boundary tests **must not** call remote services,
  download wheels beyond **`pip install`**, or open sockets.
- **Default CI** **must** collect and run boundary tests **without** extra extras beyond **`[dev]`** unless **CHANGELOG.md**
  and **README.md** document the new extra and CI is updated in the **same** change.

## Module layout and markers

- **At least one** test module under **`tests/`** must contain the **`replayt`** import checks in **§ Documented replayt Python
  symbols**. Suggested name: **`tests/test_replayt_boundary.py`**.
- Register a **pytest** marker, e.g. **`replayt_boundary`**, on those tests and declare it under **`[tool.pytest.ini_options]`**
  in **`pyproject.toml`** when implementing (**`markers = ["replayt_boundary: …"]`**), so contributors can run:

  ```bash
  pytest tests -m replayt_boundary -q
  ```

  The **full** suite (**`pytest tests -q`**) must still run them by default (do **not** exclude the marker in CI unless a
  documented optional job exists).

## Optional future tier (non-normative for this backlog)

Deeper scenarios (**`run_with_mock`**, **`assert_events`**, workflow graphs) may later use a separate marker (e.g.
**`replayt_workflow_sim`**) and **optional** CI job. Until documented, **do not** add network or flaky timing-dependent
tests to the default job.

## Acceptance criteria (checklist)

Use for Spec gate, Builder, and Tester sign-off for backlog **`d9d6b302`**.

| # | Criterion | Verification |
|---|-----------|--------------|
| R1 | **≥1** test module **imports `replayt`** and asserts **`RunResult`**, **`RunFailed`**, and **`ApprovalPending`** are available per **§ Documented replayt Python symbols**. | Code review; **`pytest tests -q`** |
| R2 | Default **`pip install -e ".[dev]"`** + **`pytest tests -q`** passes in CI with **no** extra undisclosed network. | **`.github/workflows/ci.yml`**; grep tests for **`httpx`**, **`urllib`**, sockets only where already justified |
| R3 | **README.md** or **MISSION.md** explains **default full suite** vs **focused** runs (path or **`-m replayt_boundary`**). | Manual doc review |
| R4 | **`replayt_boundary` marker** registered in **`pyproject.toml`** and used on boundary tests. | Inspect **`pyproject.toml`** + tests |
| R5 | Doc or CI changes to boundary policy appear under **CHANGELOG.md** **Unreleased** when contributor-visible. | Release hygiene |

## Related docs

- **[SPEC_AUTOMATED_TESTS.md](SPEC_AUTOMATED_TESTS.md)** — CI entrypoint and minimum verification / parsing coverage.
- **[SPEC_REPLAYT_DEPENDENCY.md](SPEC_REPLAYT_DEPENDENCY.md)** — Floor, matrix, bump policy.
- **[EVENTS.md](EVENTS.md)** — Lifecycle JSON and **replayt** concept mapping.
- **[README.md](../README.md)** — **Running tests** (full suite vs slices).
