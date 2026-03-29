# Spec: pip-audit suppression alignment and review hygiene

**Backlog (normative traceability):** `bea2900c-17e9-4bf8-9623-0830105386a2` — *Supply chain: automate pip-audit ignore review reminders*.

**Audience:** Spec gate (2b), Builder (3), Tester (4), maintainers.

## Purpose and normative status

This document defines **machine-checkable** rules so **`pip-audit --ignore-vuln`** flags in **CI** stay aligned with
**maintainer narrative** in **`docs/DEPENDENCY_AUDIT.md`**, and so each documented suppression carries **review metadata**.
It does **not** replace **[DEPENDENCY_AUDIT.md](DEPENDENCY_AUDIT.md)**; that file remains the human-facing register of
accepted transitive risk.

**Scope:** **CI** / **scripts** / **docs** only — **no** runtime package API.

## Canonical inputs

| Artifact | Role |
| -------- | ---- |
| **`.github/workflows/ci.yml`** | Source of **`pip-audit`** invocations for the merge gate (**`supply-chain`** job today). |
| **`docs/DEPENDENCY_AUDIT.md`** | Register of accepted **`--ignore-vuln`** IDs under **`## Accepted risks`**. |

If maintainers split workflows (for example separate scheduled audit), this spec **must** be updated to name the
**canonical** workflow file(s) and job id(s) that carry **`--ignore-vuln`** for the **default dev install** audit
(**`pip install -e ".[dev]"`** graph unless **DEPENDENCY_AUDIT** documents a different install posture for a given row).

## Identifier format

**Suppression IDs** are tokens matching **`CVE-YYYY-NNNN+`** (year **four** digits, trailing numeric suffix **one or more**
digits), consistent with **`pip-audit --ignore-vuln`** and common PyPI/OSV advisories. The checker **must** use a single
regex (for example **`CVE-\d{4}-\d+`**) for both workflow and markdown extraction so aliases do not diverge.

## Workflow extraction rules

1. Consider only steps in the **`supply-chain`** job (job id **`supply-chain`** in **`.github/workflows/ci.yml`**). If the
   job is renamed or split, update this spec and **§ Backlog `bea2900c`** in **[SPEC_AUTOMATED_TESTS.md](SPEC_AUTOMATED_TESTS.md)**
   in the same change.
2. From the **`run:`** block(s) that invoke **`pip-audit`**, collect **every** suppression id passed to **`--ignore-vuln`**.
   Support both **`--ignore-vuln CVE-…`** and **`--ignore-vuln=CVE-…`** spellings if present.
3. **Ignore** ids that appear only in **YAML comments** or in **`run:`** lines that do **not** execute **`pip-audit`**
   (for example echo-only documentation).
4. The **`pip-audit`** invocation **must** remain the **primary** dependency audit for that job (after the documented
   install). **Adding** an alignment script **must not** replace or skip this audit.

## Markdown extraction rules

1. Parse only the region at or after the heading **`## Accepted risks`** through the end of the file **or** through the next
   **`## `** heading of equal or higher level than **Accepted risks** if the doc gains additional top-level sections below it.
2. Every accepted suppression **must** be represented by an **`###`** (level-3) heading whose visible title contains **exactly
   one** suppression id matching **`CVE-\d{4}-\d+`**. Example: **`### CVE-2026-4539 (pygments)`**.
3. Under that heading, the body **must** include:
   - **Advisory link** — at least one HTTP(S) URL to a **PyPI advisory**, **GitHub Security Advisory**, **OSV**, or other
     **stable** public reference for the same CVE id.
   - **Rationale** — plain language on why the project accepts the risk (for example “unused code path”, “dev-only
     transitive”, “no fixed release compatible with our floor”).
   - **Next review (UTC):** **`YYYY-MM-DD`** — calendar date when a maintainer **must** re-read the advisory and either
     renew the date, remove the ignore, or bump dependencies. **Renewal** updates this line in the same PR as the
     decision (no silent extension).

## Alignment predicate

Let **\(W\)** be the set of ids from **Workflow extraction** and **\(D\)** the set from **Markdown extraction** (level-3
headings under **Accepted risks**).

The check **passes** only if **\(W = D\)** (set equality):

- **Undocumented ignore** — id in **\(W\)** not in **\(D\)** → **fail** (workflow flag without **Accepted risks** entry).
- **Orphan doc** — id in **\(D\)** not in **\(W\)** → **fail** (doc claims an acceptance CI does not implement).

Failure output **must** list symmetric differences (**workflow-only** vs **doc-only**) with file paths so contributors can
fix drift in one pass.

## Review due predicate

After alignment passes, compute **today UTC** as a date (no time-of-day).

For each accepted id, parse **`Next review (UTC): YYYY-MM-DD`** from its subsection body (case-insensitive label on the
label line is acceptable; the date **must** be ISO **8601** calendar).

- If the label or date is **missing** or **unparseable** → **fail** (incomplete register).
- If the date is **strictly before** today UTC → **fail** (review overdue; maintainer must renew or resolve in the same PR).

**Rationale:** This encodes “reminder” as a **hard** merge gate. A scheduled workflow that only opens issues **without** this
check would **not** satisfy the backlog on its own.

## Optional extensions (non-blocking unless promoted)

These are **documented** for maintainers who want stronger supply-chain signal; the Builder **may** implement **zero or one**
without blocking closure of **PI1**–**PI7**.

- **Scheduled strict audit** — A **`workflow_dispatch`** or **cron** job runs **`pip-audit`** **without** **`--ignore-vuln`**
  (same install line as **`supply-chain`**). Exit **non-zero** indicates at least one advisory is still present; compare
  output to **\(D\)** manually or with a follow-up backlog. This helps discover when an ignore can be **dropped** because
  upstream fixed the tree.
- **Duplicate workflow files** — If **`pip-audit`** is copied into another workflow, either keep **`--ignore-vuln`** lists
  **synchronized** (same set) or extend the checker to read **multiple** declared paths—**must** be specified in this spec
  when that happens.

## Strictness and governance

- **No silent weakening:** Removing **`--ignore-vuln`** from CI **without** removing the matching **Accepted risks** section
  (and vice versa) is **caught** by alignment. **Broadening** ignores (adding ids) **without** **DEPENDENCY_AUDIT** prose
  **fails** the same check.
- **Explicit maintainer decision:** Dropping an ignore because the vulnerability no longer applies **must** accompany
  dependency or lockfile changes (or upstream resolution) and **CHANGELOG.md** notes when the change is user-visible to
  integrators.

## Related docs

- **[DEPENDENCY_AUDIT.md](DEPENDENCY_AUDIT.md)** — narrative register; contributor checklist for new ignores.
- **[SPEC_AUTOMATED_TESTS.md](SPEC_AUTOMATED_TESTS.md)** — **§ Backlog `bea2900c`**, rows **PI1**–**PI7**.
- **`.github/workflows/ci.yml`** — **`supply-chain`** job.
