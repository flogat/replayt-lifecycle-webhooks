# Reference documentation (optional)

This directory is **optional**. Clones work without it beyond any small **committed** excerpts the maintainers already
ship (for example **`REPLAYT_WEBHOOK_SIGNING.md`** as the in-repo signing contract cited from **SPEC_WEBHOOK_SIGNATURE**).

## What to put here

- **Committed (git):** Short markdown **excerpts** or **consumer contracts** the project reviews and cites from specs—
  not whole upstream documentation trees.
- **Local only:** Large copies of **replayt** (or related) docs for offline or agent context go under
  **`_upstream_snapshot/`**. That subdirectory is **gitignored**; do not commit it.

## How to refresh

1. **Update a committed excerpt:** edit the relevant **`.md`** file and follow normal PR review; if wire or verification
   rules change, update **[SPEC_WEBHOOK_SIGNATURE.md](../SPEC_WEBHOOK_SIGNATURE.md)** (and tests) as usual.
2. **Bulk local snapshot:** create **`_upstream_snapshot/`** and copy markdown from your local upstream checkout or
   exported docs manually. Optional: use a maintainer-provided script under **`scripts/`** if one exists (see root
   **README.md**, **Reference documentation**).

Normative contract: **[SPEC_REFERENCE_DOCUMENTATION.md](../SPEC_REFERENCE_DOCUMENTATION.md)**.
