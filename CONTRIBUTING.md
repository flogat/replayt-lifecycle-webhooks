# Contributing

Development setup, tests, and coding expectations are summarized in **[README.md](README.md)** (**Quick start**,
**Running tests**, **Project layout**).

## Reference documentation snapshots (optional maintainer task)

This repository may include **small, committed** markdown excerpts under **`docs/reference-documentation/`** and a
**gitignored** directory **`docs/reference-documentation/_upstream_snapshot/`** for **local** bulk copies (offline or
locked-down environments).

- **When and how:** See **[docs/SPEC_REFERENCE_DOCUMENTATION.md](docs/SPEC_REFERENCE_DOCUMENTATION.md)** (sections **When to refresh**,
  **Repeatable snapshot commands**, **Licensing and attribution**; optional **`scripts/`** helpers: **Optional maintainer automation (`scripts/`)**).
- **Folder guide:** **[docs/reference-documentation/README.md](docs/reference-documentation/README.md)**.
- **Repo size:** Default clones stay **small**; do **not** commit **`_upstream_snapshot/`** or large mirrors elsewhere.
  **CI** does not download upstream documentation trees (see acceptance **RD1**–**RD8** in the spec).

You **do not** need to populate snapshots to build, test, or contribute code changes.

## Packaging check (sdist and wheel)

CI runs **`python -m build`** and **`twine check`** on every change (job **`package`** in **`.github/workflows/ci.yml`**);
acceptance rows **PK1**–**PK7** live in **[docs/SPEC_AUTOMATED_TESTS.md](docs/SPEC_AUTOMATED_TESTS.md)** (**§ Backlog
`78e3554b`**). **PEP 561** **`py.typed`**, **sdist**/**wheel** layout for that marker, and an **optional** **pyright** /
**mypy** contributor or CI path are specified under **§ Backlog `2ec2c21c`** (**TP1**–**TP6**).

**Local (same lower bounds as CI):**

```bash
python -m pip install "build>=1.2.0" "twine>=5.0.0"
rm -rf dist
python -m build
twine check dist/*
```

Use a **venv** if you prefer. **`twine check`** **must** pass before a release. **PK5** and **`py.typed`** (**TP3**) are enforced by
**`tests/test_packaging_layout.py`** (wheel zip members, **`py.typed`**, and **sdist** tarball paths).

## Optional static typing (`pyright`)

Job **`typing`** in **`.github/workflows/ci.yml`** installs **`pyright`** from PyPI, **`pip install -e .`**, then type-checks
**`src/replayt_lifecycle_webhooks/__init__.py`** and **`src/replayt_lifecycle_webhooks/events.py`** (backlog **`2ec2c21c`**, **TP4**–**TP5**).
The job sets **`continue-on-error: true`** so it is informative only; **`lint`**, **`test`**, and **`package`** remain the merge bar.

Local check:

```bash
pip install -e . pyright
pyright src/replayt_lifecycle_webhooks/__init__.py src/replayt_lifecycle_webhooks/events.py
```

## Optional pre-commit (ruff)

**Source of truth:** **`.github/workflows/ci.yml`**, job **`lint`** (merge-blocking **ruff** steps run on **Python 3.11** and **3.12**
via the workflow matrix) — **`pip install "ruff>=0.6.0"`**, then **`ruff check src tests`**
and **`ruff format --check src tests`**. If those commands change in CI, update **`.pre-commit-config.yaml`** and this section so
local hooks stay aligned.

The repo root **`.pre-commit-config.yaml`** wires the same **ruff** targets via **astral-sh/ruff-pre-commit** (format is **check-only**,
not silent rewrite on commit). Install the **pre-commit** tool (for example **`pip install pre-commit`** in your venv; it is **not** a
package runtime dependency), then run **`pre-commit install`** so Git runs the hooks before each commit.

This setup is **optional**. Contributors can open drive-by patches without installing hooks; **GitHub Actions** still runs the **`lint`**
job on pushes and pull requests.

## Supply-chain audit (`pip-audit`)

In **`supply-chain`**, CI installs **`pip install -e ".[dev]"`**, runs **`python scripts/pip_audit_suppression_alignment.py`**, then
**`pip-audit`** (see **`.github/workflows/ci.yml`**).
Accepted **`--ignore-vuln`** CVEs and contributor steps for adding one live in **`docs/DEPENDENCY_AUDIT.md`**.

Normative alignment rules (workflow ignores ↔ doc headings, **`Next review (UTC)`** due dates) and automated test rows **PI1**–**PI7**
are in **`docs/SPEC_PIP_AUDIT_SUPPRESSION_ALIGNMENT.md`** and **`docs/SPEC_AUTOMATED_TESTS.md`** (**§ Backlog `bea2900c`**).

Local check (same logic as CI): from the repo root, **`pip install -e ".[dev]"`**, then **`python scripts/pip_audit_suppression_alignment.py`**
(or **`pytest tests/test_pip_audit_suppression_alignment.py -q`**). See **README.md** (**Running tests** → **Focused runs**).
