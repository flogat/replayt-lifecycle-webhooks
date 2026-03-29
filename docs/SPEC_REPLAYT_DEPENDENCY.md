# Spec: **replayt** dependency range and integrator compatibility

**Backlogs (normative traceability):**

- **Add replayt dependency declaration and compatibility matrix stub** — `8b16060d-f6e6-4111-bed2-4978b965ff52` (matrix includes **Python** / **CI-tested** columns; **CHANGELOG** rule for dependency adds; optional **no runtime coupling yet** checklist).
- **Declare replayt dependency range and compatibility matrix** — `1a14a01a-e6be-4f3f-b270-68f57fbbe0e4` (range, matrix, upper-bound policy, justified floor, integrator reporting).
- **Pin replayt and document a minimum supported version** — `e65371ff-be0f-4dfb-ad57-9cdef4ecc8fc` (original pin / floor contract).
- **CI: run pytest and ruff on Python 3.11 (minimum supported)** — `6cd22a7b-72bc-4d34-ba7c-a6878b68907d` (matrix or equivalent for **`lint`** + **`test`**; matrix text in this spec; **§ Backlog `6cd22a7b`** in **[SPEC_AUTOMATED_TESTS.md](SPEC_AUTOMATED_TESTS.md)**).

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
- **Python version (normative for backlog `6cd22a7b`):**
  - **`lint`** and **`test`** **must** each run on **Python 3.11**, the **`requires-python` floor** in `pyproject.toml`, so **ruff** and the full **`pytest tests`** collection (same invocations as today: **`ruff check`**, **`ruff format --check`**, **`python -m pytest tests -q`**, plus existing **`test`** job steps such as **`pyproject.toml`** syntax validation and **`pip install -e .`** / **`-e ".[dev]"`**) execute at least once per workflow trigger on **3.11**.
  - **Recommended:** Keep **3.12** as an additional matrix axis (or equivalent second job) for **`lint`** and **`test`** so newer CPython behavior stays exercised. If maintainers drop **3.12** from those jobs, record the decision under **`CHANGELOG.md`**, update the **compatibility matrix** “CI-tested Python” text, and ensure **README** compatibility lines stay truthful.
  - **`package`** and **`supply-chain`** **should not** be matrixed across Python minors for this backlog (“without duplicating unrelated work”): use **one** interpreter per job (current tree: **3.12**) unless a future backlog requires otherwise. The **compatibility matrix** **Notes** column must state that packaging / **`pip-audit`** run on that single version.
  - **`[tool.ruff] target-version`** (currently **`py311`**) must stay aligned with the **lowest** supported minor; **ruff** running under **3.12** still targets **`py311`** syntax rules by configuration.

## When `replayt` is not listed in `pyproject.toml` yet (stub / pre-coupling)

Some trees may ship **documentation and tests** before the first **`import replayt`** or install-time coupling. If **`[project.dependencies]`** does **not** include **`replayt`**:

1. State **explicitly** in this spec (short **Status** paragraph under **Dependency declaration**) or in **`README.md`** that there is **no runtime dependency on replayt yet** and that the floor will appear in `pyproject.toml` when integration lands.
2. Keep the **compatibility matrix** with a **stub row** or a clear “N/A — dependency pending” note that links to this checklist.
3. Before merging the first change that adds **`replayt`** to **`[project.dependencies]`**, complete the **Builder checklist**:
   - Add **`replayt>=M.m.p`** with a justified floor (see **Justifying the floor** above).
   - Update the matrix row for the current package version line (replayt + Python columns).
   - Add **`CHANGELOG.md`** **Unreleased** **Added** (or **Changed**) text for the new dependency with rationale.
   - Align **`README.md`** compatibility lines with the new floor.
   - Ensure **replayt** boundary tests (**[SPEC_REPLAYT_BOUNDARY_TESTS.md](SPEC_REPLAYT_BOUNDARY_TESTS.md)**) match any new import surface.

Once **`replayt`** is declared, remove or rewrite the **no runtime coupling** wording so docs do not contradict the manifest.

## Compatibility matrix

**Purpose:** Give integrators a single table mapping **released `replayt-lifecycle-webhooks` versions** to **supported `replayt` install ranges**, **declared Python support**, and **what CI actually runs**. Extend the table on every release that changes declared bounds, Python support, or the CI interpreter.

**Maintainer rule:** When you cut a version or change `[project.dependencies]` for **replayt**, add or update the row for that package version and align **`CHANGELOG.md`**.

**CI note on replayt versions:** The test job does not pin a single **replayt** patch beyond the declared lower bound; **`pip`** resolves a version satisfying **`replayt>=M.m.p`**. The **matrix** documents the **declared range**; **`tests/test_replayt_dependency.py`** asserts the installed release is **≥** the canonical floor from `pyproject.toml`.

| replayt-lifecycle-webhooks | Supported replayt (declared in `pyproject.toml` for that release) | Python (`requires-python`) | CI-tested Python | Notes |
| -------------------------- | ----------------------------------------------------------------- | -------------------------- | ---------------- | ----- |
| 0.1.x (current tree)       | `>=0.4.25` (lower bound only; no upper bound)                     | `>=3.11` (see `pyproject.toml`) | **3.11** and **3.12** for **`lint`** + **`test`** (matrix or equivalent; see **§ CI**); **`package`** + **`supply-chain`** on **3.12** only (single interpreter; not matrixed per backlog `6cd22a7b`) | **Target state** after backlog **`6cd22a7b`** ships: minimum minor is always exercised in merge-blocking **ruff**/**pytest** jobs. Until the workflow is updated, treat the matrix row as the contract and align `.github/workflows/ci.yml` in phase **3**. Floor chosen as the first PyPI **replayt** version verified with this package’s CI at pin time; bump when tests or product contract require newer **replayt** APIs or behavior. |

**Integrator expectation:** Install this package from PyPI (or a fork) and let the resolver pick **replayt** consistent with the row for your **replayt-lifecycle-webhooks** version. If you pin **replayt** independently, ensure it still satisfies the declared range; otherwise signature or payload assumptions may not match what this repo tests.

## Reporting breakage

- **In-repo channel:** [GitHub Issues](https://github.com/flogat/replayt-lifecycle-webhooks/issues) for this repository — use for verification failures, resolver errors, or **replayt** upgrades that behave differently from this spec.
- **Upstream product / signing semantics:** Follow **replayt**’s own support and documentation channels for core behavior; this repo does not steer **replayt** (see **[DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)**). Include **both** installed **`replayt`** version and **`replayt-lifecycle-webhooks`** version in issue text.

## Acceptance criteria (checklist)

Use this list for Spec gate and Builder sign-off. Rows **A5–A7** map to backlog **Declare replayt dependency range and compatibility matrix** (`1a14a01a-e6be-4f3f-b270-68f57fbbe0e4`). Row **A8** maps to backlog **Add replayt dependency declaration and compatibility matrix stub** (`8b16060d-f6e6-4111-bed2-4978b965ff52`). Rows **A9–A10** map to backlog **CI: run pytest and ruff on Python 3.11** (`6cd22a7b-72bc-4d34-ba7c-a6878b68907d`).

| # | Criterion | Verification |
|---|-----------|--------------|
| A1 | `replayt` appears in `[project.dependencies]` with a documented minimum (lower bound or exact pin), **or** the **stub / pre-coupling** section above is satisfied until integration lands. | Inspect `pyproject.toml` and this spec / README for the active branch. |
| A2 | README gives integrators a clear **compatibility** story: declared floor (when present), how to check installed version, PyPI/release-history link, where to report breakage, pointer to this spec’s **compatibility matrix**, and **CI-tested Python** (see **A8**, **A9**). | Manual review of `README.md`. |
| A3 | Editable install works in CI. | CI job that runs `pip install -e .` (or equivalent) exits 0. |
| A4 | User-visible dependency/documentation changes are reflected in **`CHANGELOG.md`** under **Unreleased** (or release section), per project convention — including **dependency adds/changes** and **floor/upper-bound** moves with brief rationale. | Review `CHANGELOG.md`. |
| A5 | **Compatibility matrix** in this spec includes a row for the current package version line and matches `pyproject.toml` **replayt** bound when declared. | Diff `pyproject.toml` vs matrix; README links here. |
| A6 | **Floor justification** is present in **CHANGELOG** whenever the **replayt** minimum is introduced or raised (not required for doc-only matrix wording if bounds unchanged). | Review **CHANGELOG** history for bound changes. |
| A7 | **Upper bound policy** is explicit: either no cap (default) or cap documented in spec + README (if integrator-visible) + **CHANGELOG** with rationale. | This section + matrix + `pyproject.toml`. |
| A8 | **Compatibility matrix** lists **declared Python** (`requires-python`) and **CI-tested Python** (workflow file), and the Notes (or CI note) explain **replayt** resolution vs the lower bound. | Matrix + `.github/workflows/ci.yml` + `pyproject.toml`. |
| A9 | **`lint`** and **`test`** jobs in **`.github/workflows/ci.yml`** run on **Python 3.11** (numeric **`3.11`** in **`actions/setup-python`** or equivalent). Each job’s full step list (ruff + pytest + existing **`test`** prerequisites) runs on that interpreter. | Workflow review; CI logs for a **`mc/**` or **`master`** PR. |
| A10 | **`package`** and **`supply-chain`** remain **single-interpreter** jobs unless a separate backlog matrixes them; the matrix **Notes** name which minors **packaging** / **`pip-audit`** use. **A8** stays consistent with the workflow. | Workflow + matrix **Notes**. |

## Non-goals (this backlog)

- Defining or implementing webhook payloads, signing, or HTTP handlers — only the **dependency and documentation contract**.
- Upstreaming changes inside **replayt** core.

## Related docs

- **[README.md](../README.md)** — integrator entry point.
- **[SPEC_AUTOMATED_TESTS.md](SPEC_AUTOMATED_TESTS.md)** — **pytest** / CI entrypoint and minimum behavioral coverage for
  verification and parsing (see matrix row notes on CI at pin time).
- **[SPEC_REPLAYT_BOUNDARY_TESTS.md](SPEC_REPLAYT_BOUNDARY_TESTS.md)** — **`import replayt`** checks for **EVENTS.md**-listed
  symbols (**`RunResult`**, **`RunFailed`**, **`ApprovalPending`**) so renames break CI **here**.
- **[SPEC_WEBHOOK_SIGNATURE.md](SPEC_WEBHOOK_SIGNATURE.md)** — incoming webhook signature verification contract.
- **[DEPENDENCY_AUDIT.md](DEPENDENCY_AUDIT.md)** — CI and accepted transitive risks.
- **[SPEC_PIP_AUDIT_SUPPRESSION_ALIGNMENT.md](SPEC_PIP_AUDIT_SUPPRESSION_ALIGNMENT.md)** — **`pip-audit --ignore-vuln`**
  alignment with **DEPENDENCY_AUDIT** and **Next review** due dates (backlog **`bea2900c`**).
- **[DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)** — explicit contracts and consumer-side maintenance.
