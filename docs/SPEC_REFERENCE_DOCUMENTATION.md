# Spec: optional `docs/reference-documentation/` snapshot workflow

**Backlog (normative traceability):** Add optional reference-documentation snapshot workflow — Mission Control
**`2db687f4-23d2-4aff-8827-c3da11cdf283`** (this refinement). Earlier traceability id **`eb884da9-5273-4ce0-b105-5130c6b1ac79`**
names the same workflow where **pytest** rows **RD1**–**RD5** are defined.

**Audience:** Spec gate (2b), Builder (3), Tester (4), contributors, agent workflows.

## Purpose and normative status

This document defines how **`docs/reference-documentation/`** may be used as an **optional**, **maintainer-only** aid:
short **markdown** excerpts or **consumer contracts** that mirror or summarize **replayt** (or compatible) upstream prose
when it is not practical to rely on the network. Nothing here **requires** a full documentation mirror, a vendored
upstream tree, or **CI** steps that download upstream documentation.

**Default clone:** Fresh checkouts stay **small**. Integrators and **CI** **must not** depend on bulk material under
**`docs/reference-documentation/_upstream_snapshot/`** (that path is **gitignored** and may be absent).

**Optional task:** Refreshing snapshots or excerpts is **never** required to run **`pytest`**, install the package, or pass
merge gating.

## When to refresh

Maintain **committed** excerpts when:

- Upstream **replayt** (or your deployment’s doc source) changes **signing**, **headers**, or **delivery** rules that
  this repo’s verification contract should mirror — update the excerpt, then align **SPEC_WEBHOOK_SIGNATURE**, tests, and
  **CHANGELOG.md** per **[MISSION.md](MISSION.md)** doc hygiene.
- You are preparing a PR that **cites** new upstream prose and need a **stable, reviewable** quote in-tree.
- You work **offline** or in **locked-down CI** for analysis only: populate **`_upstream_snapshot/`** locally (see
  **§ Repeatable snapshot commands**) without committing.

**Do not** refresh bulk snapshots on a fixed schedule unless maintainers choose to; there is no automation requirement.

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

## Licensing and attribution

- **Committed excerpts** are part of this repository’s documentation. Each committed markdown file under
  **`docs/reference-documentation/`** (other than the folder **`README.md`**, which may stay purely structural) **must**
  include a short **“Source and licensing”** (or equivalent) subsection that states:
  - **Provenance** — e.g. maintainer-authored summary, **verbatim** excerpt with upstream URL and version/commit, or
    export from a named docs build.
  - **License / attribution** — how recipients may reuse the text (same license as this repo, upstream license for
    verbatim copies, or “internal reference only” if your org requires it). Do **not** imply this project owns upstream
    copyright on third-party prose.
- **`_upstream_snapshot/`** is **local-only** and **gitignored**. You are responsible for complying with **upstream**
  license terms when copying material there; nothing in this directory ships with **`pip install`**.
- **Bulk copies** must **not** be committed under a different path to evade **`.gitignore`** — if it is large or
  unmaintained, keep it under **`_upstream_snapshot/`** or outside the repo.

## Repeatable snapshot commands (no script required)

The following are **illustrative** patterns; adjust paths, branches, and URLs to your environment. They **do not** run
in **CI** and are **optional** for contributors.

**Layout:** create the snapshot root once (ignored by git):

```bash
mkdir -p docs/reference-documentation/_upstream_snapshot
```

**Git worktree or clone** (when upstream lives in a git repository you can access):

```bash
# Example: separate clone at a path you control
UPSTREAM_DIR="$HOME/src/replayt"
git -C "$UPSTREAM_DIR" pull
rsync -a --delete --exclude='.git' "$UPSTREAM_DIR/docs/" docs/reference-documentation/_upstream_snapshot/replayt-docs/
```

**curl** (when upstream publishes raw markdown or HTML you may archive locally):

```bash
# Example only — replace URL with the exact artifact you are allowed to mirror
curl -fsSL -o docs/reference-documentation/_upstream_snapshot/example.md 'https://example.invalid/path/to/doc.md'
```

**pip show / inspect** installed package paths (optional hint for finding upstream **Python**-packaged docs):

```bash
python -c "import replayt, pathlib; print(pathlib.Path(replayt.__file__).parent)"
# Copy selected files from the printed tree into _upstream_snapshot/ if license permits.
```

After any snapshot, **verify** `git status` does not list files under **`_upstream_snapshot/`** before committing.

## How to refresh (contributors)

1. **Small contract updates** (edits to committed files such as **`REPLAYT_WEBHOOK_SIGNING.md`**) follow normal review:
   paste or summarize upstream accurately, add **Source and licensing** per **§ Licensing and attribution**, cite
   sources in **CHANGELOG.md** when the contract changes.
2. **Personal or offline bulk snapshots:** create **`docs/reference-documentation/_upstream_snapshot/`** locally (ignored
   by git) and copy markdown from your local **replayt** checkout or docs site **manually**, use **§ Repeatable snapshot
   commands**, or use an optional **`scripts/`** helper if the repository provides one. **Do not** `git add` that directory.
3. After refresh, if a **committed** excerpt changes verification or wire rules, update **[SPEC_WEBHOOK_SIGNATURE.md](SPEC_WEBHOOK_SIGNATURE.md)**,
   tests, and **CHANGELOG.md** per **[MISSION.md](MISSION.md)** doc hygiene.

## Repository size expectations

- **Default clone** — Should remain **light**: only **small** committed files under **`docs/reference-documentation/`**
  (plus folder **README**) ship with the repo. Avoid committing generated sites, PDFs, or full upstream trees.
- **Growth policy** — If an excerpt grows beyond a few screens, split into a focused contract file or move narrative
  detail to **`_upstream_snapshot/`** locally.
- **`.gitignore`** — **must** list **`docs/reference-documentation/_upstream_snapshot/`** (or an equivalent dedicated
  subtree documented here and in **README.md**) so **`git add .`** does not pick up large trees.

## CI and repository hygiene

- **CI** **must not** add jobs whose **success** depends on downloading, cloning, or mirroring the full **replayt**
  documentation tree into this repository (no required **curl**/**git** doc mirror steps for merge gating).
- **`.gitignore`** **must** include **`docs/reference-documentation/_upstream_snapshot/`** (or an equivalent dedicated
  subtree documented here and in **README.md**) so accidental **`git add .`** does not pick up large trees.
- New **committed** markdown under **`docs/reference-documentation/`** (other than **`README.md`**) should be **short**
  excerpts or single-topic contracts; if a proposed addition is large, prefer **`_upstream_snapshot/`** locally or split
  into a focused excerpt.

## Acceptance (checklist)

Use for Spec gate, Builder, and Tester sign-off. Rows **RD1**–**RD5** are enforced by **`pytest`** today; **RD6**–**RD8**
are **spec / maintainer-review** until optional **pytest** extension lands.

| # | Criterion | Verification |
|---|-----------|--------------|
| **RD1** | **`docs/reference-documentation/README.md`** states that the tree is **optional**, what belongs in committed files vs **`_upstream_snapshot/`**, and links this spec. | **`pytest`** — **`tests/test_reference_documentation_workflow.py`** |
| **RD2** | Root **`README.md`** **Reference documentation (optional)** section links **`docs/reference-documentation/README.md`** and this spec; includes a **how to refresh** note (manual copy into **`_upstream_snapshot/`** and/or optional **`scripts/`** helper). | **`pytest`** (same module) |
| **RD3** | **`.gitignore`** ignores **`docs/reference-documentation/_upstream_snapshot/`** (entire subtree). | **`pytest`** (same module; **`git check-ignore -v`** on a path under that directory) |
| **RD4** | **CI** (e.g. **`.github/workflows/ci.yml`**) does **not** require fetching or generating a large upstream documentation mirror under **`docs/reference-documentation/`**. | **`pytest`** (same module) |
| **RD5** | **SPEC_AUTOMATED_TESTS.md** lists backlog **`eb884da9`** and **RD1**–**RD5** for traceability. | **`pytest`** (same module) |
| **RD6** | Each committed excerpt under **`docs/reference-documentation/`** (except the folder **`README.md`**) includes **provenance** and **license/attribution** per **§ Licensing and attribution** (see **`REPLAYT_WEBHOOK_SIGNING.md`** as the reference shape). | Maintainer review / optional future **`pytest`** |
| **RD7** | This spec documents **repeatable** manual **git** / **curl** / **rsync** (or equivalent) patterns for **`_upstream_snapshot/`** without requiring a repository script. | Maintainer review (**§ Repeatable snapshot commands**) |
| **RD8** | **CONTRIBUTING.md** or root **README.md** states **when** to refresh, **default clone stays small**, and that bulk material belongs under the gitignored subtree — consistent with **§ Repository size expectations**. | Maintainer review |

## Related docs

- **[README.md](../README.md)** — contributor-facing summary (**Reference documentation**).
- **[CONTRIBUTING.md](../CONTRIBUTING.md)** — optional maintainer task; when/how to refresh; links here.
- **[docs/reference-documentation/README.md](reference-documentation/README.md)** — folder-level guide.
- **[SPEC_WEBHOOK_SIGNATURE.md](SPEC_WEBHOOK_SIGNATURE.md)** — cites **`REPLAYT_WEBHOOK_SIGNING.md`** as in-repo authority.
- **[MISSION.md](MISSION.md)** — optional material under **`docs/reference-documentation/`** in upstream alignment bullet.
- **[DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)** — explicit contracts index.
