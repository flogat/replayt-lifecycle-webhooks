"""Align ``pip-audit --ignore-vuln`` in CI with ``docs/DEPENDENCY_AUDIT.md`` (backlog ``bea2900c``).

Normative rules: ``docs/SPEC_PIP_AUDIT_SUPPRESSION_ALIGNMENT.md``.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import re
import sys
from pathlib import Path
from typing import Final

try:
    import yaml
except ImportError as exc:  # pragma: no cover - exercised if dev deps missing
    raise SystemExit(
        'PyYAML is required. Install dev dependencies: pip install -e ".[dev]"'
    ) from exc

CVE_RE: Final[re.Pattern[str]] = re.compile(r"CVE-\d{4}-\d+")
IGNORE_FLAG_RE: Final[re.Pattern[str]] = re.compile(
    r"--ignore-vuln(?:=|\s+)(CVE-\d{4}-\d+)",
)
NEXT_REVIEW_RE: Final[re.Pattern[str]] = re.compile(
    r"Next\s+review\s*\(UTC\)\s*:\s*\**\s*(\d{4}-\d{2}-\d{2})",
    re.IGNORECASE | re.MULTILINE,
)
URL_RE: Final[re.Pattern[str]] = re.compile(r"https?://[^\s\]>]+", re.IGNORECASE)
SUPPLY_CHAIN_JOB: Final[str] = "supply-chain"
WORKFLOW_REL: Final[str] = ".github/workflows/ci.yml"
DOC_REL: Final[str] = "docs/DEPENDENCY_AUDIT.md"


def _utc_today() -> _dt.date:
    return _dt.datetime.now(_dt.timezone.utc).date()


def _strip_shell_comment(line: str) -> str:
    """Drop ``# ...`` suffix for typical CI shell lines (no quoted ``#`` on ``pip-audit`` lines)."""
    if "#" not in line:
        return line
    in_single = in_double = False
    escape = False
    for i, ch in enumerate(line):
        if escape:
            escape = False
            continue
        if ch == "\\" and (in_single or in_double):
            escape = True
            continue
        if ch == "'" and not in_double:
            in_single = not in_single
            continue
        if ch == '"' and not in_single:
            in_double = not in_double
            continue
        if ch == "#" and not in_single and not in_double:
            return line[:i].rstrip()
    return line


def extract_workflow_ignore_vulns(
    ci_yml_text: str, *, job_id: str = SUPPLY_CHAIN_JOB
) -> set[str]:
    """PI1: suppression ids from ``supply-chain`` ``pip-audit`` ``run`` scripts (SPEC workflow extraction)."""
    data = yaml.safe_load(ci_yml_text)
    if not isinstance(data, dict):
        msg = f"{WORKFLOW_REL}: root must be a mapping"
        raise ValueError(msg)
    jobs = data.get("jobs")
    if not isinstance(jobs, dict):
        msg = f"{WORKFLOW_REL}: missing or invalid `jobs`"
        raise ValueError(msg)
    job = jobs.get(job_id)
    if job is None:
        msg = f"{WORKFLOW_REL}: missing job `{job_id}`"
        raise ValueError(msg)
    if not isinstance(job, dict):
        msg = f"{WORKFLOW_REL}: job `{job_id}` must be a mapping"
        raise ValueError(msg)
    steps = job.get("steps")
    if not isinstance(steps, list):
        msg = f"{WORKFLOW_REL}: job `{job_id}` must have a `steps` list"
        raise ValueError(msg)

    found: set[str] = set()
    for step in steps:
        if not isinstance(step, dict):
            continue
        run = step.get("run")
        if not isinstance(run, str) or not run.strip():
            continue
        for line in run.splitlines():
            line = _strip_shell_comment(line).strip()
            if not line or line.lower().startswith("echo "):
                continue
            if not re.search(r"(?<![\w-])pip-audit(?![\w-])", line):
                continue
            for m in IGNORE_FLAG_RE.finditer(line):
                found.add(m.group(1))
    return found


def _accepted_risks_body(markdown: str) -> str:
    marker = "## Accepted risks"
    m_heading = re.search(rf"(?m)^{re.escape(marker)}\s*$", markdown)
    if not m_heading:
        msg = f"{DOC_REL}: missing top-level heading `{marker}` (must start a line)"
        raise ValueError(msg)
    idx = m_heading.end()
    after = markdown[idx:]
    # Next `## ` at column 0 ends the section (same level as Accepted risks).
    m = re.search(r"(?m)^## ", after)
    if m:
        return after[: m.start()]
    return after


def parse_accepted_risk_entries(
    markdown: str,
) -> tuple[dict[str, _dt.date], list[str]]:
    """PI2/PI5: ids from level-3 headings; map id -> next review date; collect errors."""
    region = _accepted_risks_body(markdown)
    errors: list[str] = []
    by_id: dict[str, _dt.date] = {}

    # Split on ### headings at line start.
    parts = re.split(r"(?m)^###\s+", region)
    # parts[0] is preamble after ## Accepted risks (often newlines only)
    for chunk in parts[1:]:
        lines = chunk.splitlines()
        if not lines:
            errors.append(f"{DOC_REL}: empty `###` subsection under Accepted risks")
            continue
        title_line = lines[0].strip()
        body = "\n".join(lines[1:])
        ids_in_title = CVE_RE.findall(title_line)
        if len(ids_in_title) != 1:
            errors.append(
                f"{DOC_REL}: `###` title must contain exactly one CVE id; got {len(ids_in_title)} "
                f"in `{title_line!r}`",
            )
            continue
        cid = ids_in_title[0]
        if cid in by_id:
            errors.append(f"{DOC_REL}: duplicate Accepted risks entry for `{cid}`")
            continue
        if not URL_RE.search(body):
            errors.append(
                f"{DOC_REL}: subsection `{cid}` must include at least one http(s) advisory URL",
            )
        m = NEXT_REVIEW_RE.search(body)
        if not m:
            errors.append(
                f"{DOC_REL}: subsection `{cid}` missing parseable `Next review (UTC): YYYY-MM-DD`",
            )
            continue
        raw = m.group(1)
        try:
            review = _dt.date.fromisoformat(raw)
        except ValueError:
            errors.append(
                f"{DOC_REL}: subsection `{cid}` has invalid `Next review (UTC)` date `{raw!r}`",
            )
            continue
        by_id[cid] = review

    if not by_id and not errors:
        errors.append(
            f"{DOC_REL}: no `###` Accepted risks subsections with a CVE id were found",
        )
    return by_id, errors


def alignment_errors(workflow_ids: set[str], doc_ids: set[str]) -> list[str]:
    """PI3: set equality messaging."""
    if workflow_ids == doc_ids:
        return []
    only_w = sorted(workflow_ids - doc_ids)
    only_d = sorted(doc_ids - workflow_ids)
    lines = [
        f"{WORKFLOW_REL} vs {DOC_REL}: `pip-audit --ignore-vuln` set mismatch "
        f"(expected set equality per SPEC_PIP_AUDIT_SUPPRESSION_ALIGNMENT).",
        f"  Workflow only ({WORKFLOW_REL}): {only_w if only_w else '[]'}",
        f"  Doc only ({DOC_REL}): {only_d if only_d else '[]'}",
    ]
    return lines


def review_due_errors(
    ids: set[str],
    by_id: dict[str, _dt.date],
    *,
    today: _dt.date,
) -> list[str]:
    """PI6: fail when Next review is strictly before today UTC."""
    overdue = sorted(cid for cid in ids if by_id.get(cid, today) < today)
    if not overdue:
        return []
    return [
        f"{DOC_REL}: Next review (UTC) is overdue (before {today.isoformat()} UTC) for: {overdue}",
    ]


def collect_errors(
    repo_root: Path,
    *,
    today: _dt.date | None = None,
) -> list[str]:
    """Run alignment + review checks; return human-readable error lines (empty => success)."""
    today = today or _utc_today()
    ci_path = repo_root / WORKFLOW_REL
    doc_path = repo_root / DOC_REL
    errors: list[str] = []

    if not ci_path.is_file():
        return [f"missing {ci_path}"]
    if not doc_path.is_file():
        return [f"missing {doc_path}"]

    try:
        wf_text = ci_path.read_text(encoding="utf-8")
        workflow_ids = extract_workflow_ignore_vulns(wf_text)
    except (yaml.YAMLError, ValueError) as exc:
        return [f"{WORKFLOW_REL}: {exc}"]

    try:
        doc_text = doc_path.read_text(encoding="utf-8")
        by_id, doc_errors = parse_accepted_risk_entries(doc_text)
    except ValueError as exc:
        return [str(exc)]

    errors.extend(doc_errors)
    doc_ids = set(by_id.keys())

    errors.extend(alignment_errors(workflow_ids, doc_ids))
    if workflow_ids != doc_ids:
        return errors

    errors.extend(review_due_errors(workflow_ids, by_id, today=today))
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check pip-audit suppressions vs docs/DEPENDENCY_AUDIT.md (bea2900c).",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="Repository root (default: current directory)",
    )
    args = parser.parse_args(argv)
    root = args.repo_root.resolve()
    errs = collect_errors(root)
    if errs:
        print("\n".join(errs), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
