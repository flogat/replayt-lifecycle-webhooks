# Contributing

Development setup, tests, and coding expectations are summarized in **[README.md](README.md)** (**Quick start**,
**Running tests**, **Project layout**).

## Reference documentation snapshots (optional maintainer task)

This repository may include **small, committed** markdown excerpts under **`docs/reference-documentation/`** and a
**gitignored** directory **`docs/reference-documentation/_upstream_snapshot/`** for **local** bulk copies (offline or
locked-down environments).

- **When and how:** See **[docs/SPEC_REFERENCE_DOCUMENTATION.md](docs/SPEC_REFERENCE_DOCUMENTATION.md)** (**§ When to refresh**,
  **§ Repeatable snapshot commands**, **§ Licensing and attribution**).
- **Folder guide:** **[docs/reference-documentation/README.md](docs/reference-documentation/README.md)**.
- **Repo size:** Default clones stay **small**; do **not** commit **`_upstream_snapshot/`** or large mirrors elsewhere.
  **CI** does not download upstream documentation trees (see acceptance **RD1**–**RD5** in the spec).

You **do not** need to populate snapshots to build, test, or contribute code changes.
