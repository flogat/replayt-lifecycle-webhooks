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

CI **must** run **`python -m build`** and **`twine check`** on the artifacts once backlog **`78e3554b`** is implemented;
acceptance rows **PK1**–**PK7** live in **[docs/SPEC_AUTOMATED_TESTS.md](docs/SPEC_AUTOMATED_TESTS.md)** (**§ Backlog
`78e3554b`**).

**Local (matches the intended CI shape):**

```bash
python -m pip install "build" "twine"
rm -rf dist
python -m build
twine check dist/*
```

Use a **venv** if you prefer; versions need not match CI exactly, but **`twine check`** **must** pass before a release.
Inspecting the **wheel** (zip) for **`replayt_lifecycle_webhooks/fixtures/events/*.json`** is part of **PK5**—automate in CI
as specified in **SPEC_AUTOMATED_TESTS**.
