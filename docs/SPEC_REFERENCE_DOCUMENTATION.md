# Spec: optional `docs/reference-documentation/` snapshot workflow

**Backlog (normative traceability):** Add optional reference-documentation snapshot workflow
(`eb884da9-5273-4ce0-b105-5130c6b1ac79`) — checklist **RD1**–**RD5** in **§ Acceptance** below and **§ Backlog `eb884da9`**
in **[SPEC_AUTOMATED_TESTS.md](SPEC_AUTOMATED_TESTS.md)**.

**Audience:** Spec gate (2b), Builder (3), Tester (4), contributors, agent workflows.

## Purpose and normative status

This document defines how **`docs/reference-documentation/`** may be used as an **optional**, **contributor-local** aid:
short **markdown** excerpts or **consumer contracts** that mirror or summarize **replayt** (or compatible) upstream prose
when it is not practical to rely on the network. Nothing here **requires** a full documentation mirror, a vendored
upstream tree, or **CI** steps that download upstream documentation.

**Default clone:** Fresh checkouts stay small. Integrators and **CI** **must not** depend on bulk material under
**`docs/reference-documentation/_upstream_snapshot/`** (that path is **gitignored** and may be absent).

## What belongs under `docs/reference-documentation/`

| Kind | Location | Tracked in git? |
| ---- | -------- | --------------- |
| **Consumer contract excerpts** — short, reviewed text this repo cites as authority (e.g. signing rules aligned with **SPEC_WEBHOOK_SIGNATURE**) | Root of **`docs/reference-documentation/`** (example: **`REPLAYT_WEBHOOK_SIGNING.md`**) | **Yes**, when maintainers intentionally commit them |
| **Folder README** — explains optional use, refresh hints, and points here | **`docs/reference-documentation/README.md`** | **Yes** |
| **Bulk / full-tree copies** — large mirrors, scraped docs, or arbitrary upstream markdown trees for offline browsing | **`docs/reference-documentation/_upstream_snapshot/`** only | **No** — directory is listed in **`.gitignore`** |

**Out of scope for this backlog:** automating upstream sync in **CI**, submodule pins, or mandatory scripts. A
maintainer **may** add an **optional** helper under **`scripts/`** (for example a shell script that copies from a local
**replayt** checkout into **`_upstream_snapshot/`**); if added, document the command in **`docs/reference-documentation/README.md`**
and/or root **README.md** (**Reference documentation** section). The script **must not** be required for **`pytest`** or
for publishing the package.

## How to refresh (contributors)

1. **Small contract updates** (edits to committed files such as **`REPLAYT_WEBHOOK_SIGNING.md`**) follow normal review:
   paste or summarize upstream accurately, cite sources in the file or in **CHANGELOG.md** when the contract changes.
2. **Personal or offline bulk snapshots:** create **`docs/reference-documentation/_upstream_snapshot/`** locally (ignored
   by git) and copy markdown from your local **replayt** checkout or docs site **manually**, or use an optional
   **`scripts/`** helper if the repository provides one. **Do not** `git add` that directory.
3. After refresh, if a **committed** excerpt changes verification or wire rules, update **[SPEC_WEBHOOK_SIGNATURE.md](SPEC_WEBHOOK_SIGNATURE.md)**,
   tests, and **CHANGELOG.md** per **[MISSION.md](MISSION.md)** doc hygiene.

## CI and repository hygiene

- **CI** **must not** add jobs whose **success** depends on downloading, cloning, or mirroring the full **replayt**
  documentation tree into this repository (no required **curl**/**git** doc mirror steps for merge gating).
- **`.gitignore`** **must** include **`docs/reference-documentation/_upstream_snapshot/`** (or an equivalent dedicated
  subtree documented here and in **README.md**) so accidental **`git add .`** does not pick up large trees.
- New **committed** markdown under **`docs/reference-documentation/`** (other than **`README.md`**) should be **short**
  excerpts or single-topic contracts; if a proposed addition is large, prefer **`_upstream_snapshot/`** locally or split
  into a focused excerpt.

## Acceptance (checklist)

Use for Spec gate, Builder, and Tester sign-off for backlog **`eb884da9`**.

| # | Criterion | Verification |
|---|-----------|--------------|
| **RD1** | **`docs/reference-documentation/README.md`** states that the tree is **optional**, what belongs in committed files vs **`_upstream_snapshot/`**, and links this spec. | **`pytest`** — **`tests/test_reference_documentation_workflow.py`** |
| **RD2** | Root **`README.md`** **Reference documentation (optional)** section links **`docs/reference-documentation/README.md`** and this spec; includes a **how to refresh** note (manual copy into **`_upstream_snapshot/`** and/or optional **`scripts/`** helper). | **`pytest`** (same module) |
| **RD3** | **`.gitignore`** ignores **`docs/reference-documentation/_upstream_snapshot/`** (entire subtree). | **`pytest`** (same module; **`git check-ignore -v`** on a path under that directory) |
| **RD4** | **CI** (e.g. **`.github/workflows/ci.yml`**) does **not** require fetching or generating a large upstream documentation mirror under **`docs/reference-documentation/`**. | **`pytest`** (same module) |
| **RD5** | **SPEC_AUTOMATED_TESTS.md** lists backlog **`eb884da9`** and **RD1**–**RD5** for traceability. | **`pytest`** (same module) |

## Related docs

- **[README.md](../README.md)** — contributor-facing summary (**Reference documentation**).
- **[docs/reference-documentation/README.md](reference-documentation/README.md)** — folder-level stub.
- **[SPEC_WEBHOOK_SIGNATURE.md](SPEC_WEBHOOK_SIGNATURE.md)** — cites **`REPLAYT_WEBHOOK_SIGNING.md`** as in-repo authority.
- **[MISSION.md](MISSION.md)** — optional material under **`docs/reference-documentation/`** in upstream alignment bullet.
- **[DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)** — explicit contracts index.
