# Reference documentation (optional)

This directory is **optional**. **Default repository clones stay small** — only small **committed** excerpts ship with
git; large trees are **local-only** under **`_upstream_snapshot/`** (gitignored).

Clones work without extra work beyond any **committed** excerpts the maintainers already ship (for example
**`REPLAYT_WEBHOOK_SIGNING.md`** as the in-repo signing contract cited from **SPEC_WEBHOOK_SIGNATURE**).

## When to refresh

- Upstream **signing** or **delivery** documentation changes materially — update committed excerpts and align specs /
  **CHANGELOG** (see **[SPEC_REFERENCE_DOCUMENTATION.md](../SPEC_REFERENCE_DOCUMENTATION.md)**).
- You need **offline** or **bulk** upstream prose for yourself — populate **`_upstream_snapshot/`** only; never commit
  it.

## What to put here

- **Committed (git):** Short markdown **excerpts** or **consumer contracts** the project reviews and cites from specs—
  not whole upstream documentation trees. Include **source and licensing** prose per the spec (**RD6**).
- **Local only:** Large copies of **replayt** (or related) docs for offline or agent context go under
  **`_upstream_snapshot/`**. That subdirectory is **gitignored**; do not commit it.

## How to refresh

1. **Update a committed excerpt:** edit the relevant **`.md`** file and follow normal PR review; if wire or verification
   rules change, update **[SPEC_WEBHOOK_SIGNATURE.md](../SPEC_WEBHOOK_SIGNATURE.md)** (and tests) as usual.
2. **Bulk local snapshot:** create **`_upstream_snapshot/`** and copy markdown from your local upstream checkout or
   exported docs **manually**, use the **git** / **curl** / **rsync** patterns in the spec, or run
   **`scripts/sync_upstream_reference_docs.sh /path/to/replayt/docs`** from the repository root (output lands under
   **`_upstream_snapshot/replayt-docs/`** only). See root **README.md** (**Reference documentation (optional)**).

Normative contract: **[SPEC_REFERENCE_DOCUMENTATION.md](../SPEC_REFERENCE_DOCUMENTATION.md)**. Contributor summary:
**[CONTRIBUTING.md](../../CONTRIBUTING.md)**.
