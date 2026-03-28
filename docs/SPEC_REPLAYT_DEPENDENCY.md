# Spec: **replayt** dependency range and integrator compatibility

**Backlogs (normative traceability):**

- **Declare replayt dependency range and compatibility matrix** — `1a14a01a-e6be-4f3f-b270-68f57fbbe0e4` (range, matrix, upper-bound policy, justified floor, integrator reporting).
- **Pin replayt and document a minimum supported version** — `e65371ff-be0f-4dfb-ad57-9cdef4ecc8fc` (original pin / floor contract).

**Audience:** Spec gate (2b), Builder (3), integrators, maintainers.

## Problem

Without a declared, **justified** **replayt** dependency range and a **published compatibility matrix**, lifecycle event shapes and signing assumptions can drift silently between this package and the integrator’s environment. Upgrades stay unpredictable when the floor moves or when maintainers add an upper bound.

## Contract

### Dependency declaration

- **`[project.dependencies]`** in `pyproject.toml` **must** list **`replayt`** with a **minimum supported version** using a **lower bound** as the default policy, e.g. `replayt>=0.4.25`.
- **Canonical constraint shape for automation:** exactly **one** line in `[project.dependencies]` that matches `replayt>=<major>.<minor>.<patch>` (PEP 440 release segment; optional surrounding whitespace). Tests and tooling parse this line; do not split the lower bound across extras-only declarations without keeping this canonical line.
- **Justifying the floor (required for acceptance):** When setting or **raising** the minimum, **`CHANGELOG.md`** (Unreleased or the releasing section) **must** include a short **user-visible** note that states the new bound and **why** (for example: first PyPI version verified against this package’s tests; or a required **replayt** API or behavior). The same bump **must** be reflected in the **compatibility matrix** below and, if the numeric floor changes, in **`README.md`** where the minimum is stated.
- **Other runtime deps:** This package may list additional direct dependencies (for example **`pydantic`**) in `pyproject.toml`. Those are out of scope for the **replayt** matrix unless a maintainer explicitly documents cross-coupling; see **[DEPENDENCY_AUDIT.md](DEPENDENCY_AUDIT.md)** for CI and transitive-risk notes.

### Upper bound policy (optional but normative when used)

- **Default:** **No** upper bound on **replayt** in `pyproject.toml` unless maintainers deliberately cap compatibility (for example after an upstream **documented** breaking change that this package cannot absorb in the current major).
- **If an upper bound is added** (e.g. `replayt>=0.4.25,<0.5.0`): document it in this spec (matrix + one sentence of policy), in **`README.md`** if integrators must see it at a glance, and in **`CHANGELOG.md`** with rationale. Prefer resolving forward with a new **replayt** floor or a new **replayt-lifecycle-webhooks** major per SemVer rather than leaving a tight cap in place indefinitely.
- **Renovate / wide ranges:** Extra constraints (markers, duplicates) must **not** remove the single canonical `replayt>=M.m.p` line required above.

### Documentation (integrator-facing)

- **`README.md`** must state:
  - the **declared minimum** (or reference `pyproject.toml` explicitly alongside a one-line summary);
  - **how to check** the installed **replayt** version after install (e.g. `pip show replayt` and/or `importlib.metadata`);
  - **where to read upstream versions** — link to [replayt on PyPI](https://pypi.org/project/replayt/) and to [release history](https://pypi.org/project/replayt/#history);
  - **where to report incompatibility** — this repo’s Issues URL (also in `[project.urls]` when present);
  - a **pointer** to this spec’s **compatibility matrix** (see README “Compatibility matrix” line).
- **`DESIGN_PRINCIPLES.md`** must point maintainers and integrators at this spec for the **matrix** and bump policy (one sentence or bullet is enough).

### CI

- **`pip install -e .`** must succeed in CI (same standard as local editable install).
- Supply-chain / dev workflows that use **`pip install -e ".[dev]"`** remain valid; they must still resolve **replayt** from the declared dependency range.

## Compatibility matrix

**Purpose:** Give integrators a single table mapping **released `replayt-lifecycle-webhooks` versions** to **supported `replayt` install ranges** and short notes. Extend the table on every release that changes declared bounds or compatibility story.

**Maintainer rule:** When you cut a version or change `[project.dependencies]` for **replayt**, add or update the row for that package version and align **`CHANGELOG.md`**.

| replayt-lifecycle-webhooks | Supported replayt (declared in `pyproject.toml` for that release) | Notes |
| -------------------------- | ----------------------------------------------------------------- | ----- |
| 0.1.x (current tree)       | `>=0.4.25` (lower bound only; no upper bound)                     | Floor chosen as the first PyPI **replayt** version verified with this package’s CI at pin time; bump when tests or product contract require newer **replayt** APIs or behavior. |

**Integrator expectation:** Install this package from PyPI (or a fork) and let the resolver pick **replayt** consistent with the row for your **replayt-lifecycle-webhooks** version. If you pin **replayt** independently, ensure it still satisfies the declared range; otherwise signature or payload assumptions may not match what this repo tests.

## Reporting breakage

- **In-repo channel:** [GitHub Issues](https://github.com/flogat/replayt-lifecycle-webhooks/issues) for this repository — use for verification failures, resolver errors, or **replayt** upgrades that behave differently from this spec.
- **Upstream product / signing semantics:** Follow **replayt**’s own support and documentation channels for core behavior; this repo does not steer **replayt** (see **[DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)**). Include **both** installed **`replayt`** version and **`replayt-lifecycle-webhooks`** version in issue text.

## Acceptance criteria (checklist)

Use this list for Spec gate and Builder sign-off. Rows **A5–A7** map to backlog **Declare replayt dependency range and compatibility matrix** (`1a14a01a-e6be-4f3f-b270-68f57fbbe0e4`).

| # | Criterion | Verification |
|---|-----------|--------------|
| A1 | `replayt` appears in `[project.dependencies]` with a documented minimum (lower bound or exact pin). | Inspect `pyproject.toml`; matches contract above. |
| A2 | README gives integrators a clear **compatibility** story: declared floor, how to check installed version, PyPI/release-history link, where to report breakage, and pointer to this spec’s **compatibility matrix**. | Manual review of `README.md`. |
| A3 | Editable install works in CI. | CI job that runs `pip install -e .` (or equivalent) exits 0. |
| A4 | User-visible dependency/documentation changes are reflected in **`CHANGELOG.md`** under **Unreleased** (or release section), per project convention — including **dependency adds/changes** and **floor/upper-bound** moves with brief rationale. | Review `CHANGELOG.md`. |
| A5 | **Compatibility matrix** in this spec includes a row for the current package version line and matches `pyproject.toml`. | Diff `pyproject.toml` vs matrix; README links here. |
| A6 | **Floor justification** is present in **CHANGELOG** whenever the **replayt** minimum is introduced or raised (not required for doc-only matrix wording if bounds unchanged). | Review **CHANGELOG** history for bound changes. |
| A7 | **Upper bound policy** is explicit: either no cap (default) or cap documented in spec + README (if integrator-visible) + **CHANGELOG** with rationale. | This section + matrix + `pyproject.toml`. |

## Non-goals (this backlog)

- Defining or implementing webhook payloads, signing, or HTTP handlers — only the **dependency and documentation contract**.
- Upstreaming changes inside **replayt** core.

## Related docs

- **[README.md](../README.md)** — integrator entry point.
- **[SPEC_AUTOMATED_TESTS.md](SPEC_AUTOMATED_TESTS.md)** — **pytest** / CI entrypoint and minimum behavioral coverage for
  verification and parsing (see matrix row notes on CI at pin time).
- **[SPEC_WEBHOOK_SIGNATURE.md](SPEC_WEBHOOK_SIGNATURE.md)** — incoming webhook signature verification contract.
- **[DEPENDENCY_AUDIT.md](DEPENDENCY_AUDIT.md)** — CI and accepted transitive risks.
- **[DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)** — explicit contracts and consumer-side maintenance.
