# Spec: **replayt** runtime pin and integrator compatibility

**Backlog:** Pin replayt and document a minimum supported version (`e65371ff-be0f-4dfb-ad57-9cdef4ecc8fc`).  
**Audience:** Spec gate (2b), Builder (3), integrators, maintainers.

## Problem

Without a declared **replayt** dependency, lifecycle event shapes and signing assumptions can drift silently between this package and the integrator’s environment.

## Contract

### Dependency declaration

- **`[project.dependencies]`** in `pyproject.toml` **must** list **`replayt`** with a **minimum supported version** using a **lower bound only** (pragmatic default), e.g. `replayt>=0.4.25`.
- **Canonical constraint shape for automation:** a single dependency line that matches `replayt>=<major>.<minor>.<patch>` (PEP 440 release segment; optional surrounding whitespace). If maintainers add multiple constraints or extras, they must preserve one line in this form for tooling that parses the lower bound.
- **Choosing the floor:** bump the lower bound when this package **requires** APIs or behavior introduced in a newer **replayt** release. Document the bump in **`CHANGELOG.md`** under **Unreleased** (or the releasing version section) with a short reason. Prefer verifying against PyPI and upstream release notes rather than guessing.

### Documentation (integrator-facing)

- **`README.md`** must state:
  - the **declared minimum** (or reference `pyproject.toml` explicitly alongside a one-line summary);
  - **how to check** the installed **replayt** version after install (e.g. `pip show replayt` and/or `importlib.metadata`);
  - **where to read upstream versions** — link to [replayt on PyPI](https://pypi.org/project/replayt/) and to [release history](https://pypi.org/project/replayt/#history);
  - **where to report incompatibility** — this repo’s Issues URL (also in `[project.urls]` when present).

### CI

- **`pip install -e .`** must succeed in CI (same standard as local editable install).
- Supply-chain / dev workflows that use **`pip install -e ".[dev]"`** remain valid; they must still resolve **replayt** from the declared dependency range.

## Acceptance criteria (checklist)

Use this list for Spec gate and Builder sign-off.

| # | Criterion | Verification |
|---|-----------|--------------|
| A1 | `replayt` appears in `[project.dependencies]` with a documented minimum (lower bound or exact pin). | Inspect `pyproject.toml`; matches contract above. |
| A2 | README gives integrators a clear **compatibility** story: declared floor, how to check installed version, PyPI/release-history link, and where to report breakage. | Manual review of `README.md`. |
| A3 | Editable install works in CI. | CI job that runs `pip install -e .` (or equivalent) exits 0. |
| A4 | User-visible dependency/documentation changes are reflected in **`CHANGELOG.md`** under **Unreleased** (or release section), per project convention. | Review `CHANGELOG.md`. |

## Non-goals (this backlog)

- Defining or implementing webhook payloads, signing, or HTTP handlers — only the **dependency and documentation contract**.
- Upstreaming changes inside **replayt** core.

## Related docs

- **[README.md](../README.md)** — integrator entry point.
- **[SPEC_WEBHOOK_SIGNATURE.md](SPEC_WEBHOOK_SIGNATURE.md)** — incoming webhook signature verification contract.
- **[DEPENDENCY_AUDIT.md](DEPENDENCY_AUDIT.md)** — CI and accepted transitive risks.
- **[DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)** — explicit contracts and consumer-side maintenance.
