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
`78e3554b`**).

**Local (same lower bounds as CI):**

```bash
python -m pip install "build>=1.2.0" "twine>=5.0.0"
rm -rf dist
python -m build
twine check dist/*
```

Use a **venv** if you prefer. **`twine check`** **must** pass before a release. **PK5** is enforced by
**`tests/test_packaging_layout.py`** (wheel zip members and **sdist** tarball paths).
