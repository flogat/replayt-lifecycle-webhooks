"""SPEC_PIP_AUDIT_SUPPRESSION_ALIGNMENT / SPEC_AUTOMATED_TESTS § Backlog ``bea2900c`` (PI1–PI6)."""

from __future__ import annotations

import datetime as dt
import pathlib

from pip_audit_suppression_alignment import (
    alignment_errors,
    collect_errors,
    extract_workflow_ignore_vulns,
    parse_accepted_risk_entries,
    review_due_errors,
)


def _repo_root() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parents[1]


def _minimal_workflow(*, ignore: str, pip_audit_line: str | None = None) -> str:
    line = pip_audit_line or f"pip-audit --ignore-vuln {ignore} --desc"
    return f"""name: CI
on: push
jobs:
  supply-chain:
    runs-on: ubuntu-latest
    steps:
      - name: audit
        run: {line}
"""


def _minimal_doc(
    cve: str,
    *,
    review: str = "2099-01-01",
    with_url: bool = True,
    with_review: bool = True,
) -> str:
    url_line = (
        f"- **Advisory:** <https://osv.dev/vulnerability/{cve}>\n" if with_url else ""
    )
    review_line = (
        f"- **Next review (UTC):** {review}\n"
        if with_review
        else "- **Rationale:** x\n"
    )
    return f"""# Dependency audit

## Accepted risks

### {cve} (test)

{url_line}- **Rationale:** test fixture.
{review_line}
"""


def test_pi_alignment_succeeds_on_repository_tree() -> None:
    """PI3/PI5/PI6: current repo workflow and DEPENDENCY_AUDIT.md align and reviews are not overdue."""
    errs = collect_errors(_repo_root(), today=dt.date(2026, 3, 29))
    assert errs == []


def test_pi1_extract_ignore_vulns_equals_form() -> None:
    """PI1: ``--ignore-vuln=CVE-…`` spelling."""
    text = _minimal_workflow(
        ignore="CVE-2026-1000",
        pip_audit_line="pip-audit --ignore-vuln=CVE-2026-1000 --desc",
    )
    assert extract_workflow_ignore_vulns(text) == {"CVE-2026-1000"}


def test_pi1_extract_ignore_vulns_space_form() -> None:
    """PI1: ``--ignore-vuln CVE-…`` spelling."""
    assert extract_workflow_ignore_vulns(_minimal_workflow(ignore="CVE-2026-1001")) == {
        "CVE-2026-1001"
    }


def test_pi1_ignores_echo_and_non_pip_audit_lines() -> None:
    """PI1: echo lines and lines without ``pip-audit`` do not contribute ids."""
    yaml = """name: CI
on: push
jobs:
  supply-chain:
    runs-on: ubuntu-latest
    steps:
      - run: |
          echo "--ignore-vuln CVE-2026-9999"
          pip install x
          pip-audit --ignore-vuln CVE-2026-1002 --desc
"""
    assert extract_workflow_ignore_vulns(yaml) == {"CVE-2026-1002"}


def test_accepted_risks_heading_is_line_start_only() -> None:
    """Prose that mentions ``## Accepted risks`` must not delimit the parsed region (real heading below)."""
    md = """# Dependency audit

Intro mentions **`## Accepted risks`** in backticks before the real section.

## Accepted risks

### CVE-2026-8000

- **Advisory:** https://example.com/a
- **Rationale:** fixture
- **Next review (UTC):** 2099-01-01
"""
    by_id, errors = parse_accepted_risk_entries(md)
    assert errors == []
    assert by_id == {"CVE-2026-8000": dt.date(2099, 1, 1)}


def test_pi2_pi5_parse_accepted_risk_bullet_review() -> None:
    """PI2/PI5: level-3 heading + Next review line (markdown bullet)."""
    md = _minimal_doc("CVE-2026-2000")
    by_id, errors = parse_accepted_risk_entries(md)
    assert errors == []
    assert by_id == {"CVE-2026-2000": dt.date(2099, 1, 1)}


def test_pi2_title_must_have_exactly_one_cve() -> None:
    """Malformed ``###`` title is rejected."""
    md = """## Accepted risks

### CVE-2026-3000 and CVE-2026-3001

- **Advisory:** https://example.com/x
- **Rationale:** x
- **Next review (UTC):** 2099-01-01
"""
    _by_id, errors = parse_accepted_risk_entries(md)
    assert any("exactly one CVE" in e for e in errors)


def test_pi3_alignment_errors_list_symmetric_diff() -> None:
    """PI3: failure text names workflow-only and doc-only ids."""
    errs = alignment_errors({"CVE-2026-4000"}, {"CVE-2026-4001"})
    assert len(errs) == 3
    assert "Workflow only" in errs[1] and "CVE-2026-4000" in errs[1]
    assert "Doc only" in errs[2] and "CVE-2026-4001" in errs[2]


def test_collect_errors_reports_workflow_only(tmp_path: pathlib.Path) -> None:
    wf = tmp_path / ".github" / "workflows"
    wf.mkdir(parents=True)
    (wf / "ci.yml").write_text(
        _minimal_workflow(ignore="CVE-2026-5000"), encoding="utf-8"
    )
    doc = tmp_path / "docs"
    doc.mkdir(parents=True)
    (doc / "DEPENDENCY_AUDIT.md").write_text(
        _minimal_doc("CVE-2026-5001"), encoding="utf-8"
    )
    errs = collect_errors(tmp_path, today=dt.date(2099, 6, 1))
    assert any("Workflow only" in e for e in errs)
    assert any("Doc only" in e for e in errs)


def test_pi6_overdue_next_review(tmp_path: pathlib.Path) -> None:
    """PI6: strictly before today UTC fails."""
    wf = tmp_path / ".github" / "workflows"
    wf.mkdir(parents=True)
    (wf / "ci.yml").write_text(
        _minimal_workflow(ignore="CVE-2026-6000"), encoding="utf-8"
    )
    doc = tmp_path / "docs"
    doc.mkdir(parents=True)
    (doc / "DEPENDENCY_AUDIT.md").write_text(
        _minimal_doc("CVE-2026-6000", review="2020-01-01"), encoding="utf-8"
    )
    errs = collect_errors(tmp_path, today=dt.date(2026, 6, 15))
    assert any("overdue" in e.lower() for e in errs)
    assert "CVE-2026-6000" in "\n".join(errs)


def test_review_due_errors_empty_when_not_due() -> None:
    assert (
        review_due_errors(
            {"CVE-1"}, {"CVE-1": dt.date(2099, 1, 1)}, today=dt.date(2026, 1, 1)
        )
        == []
    )


def test_missing_supply_chain_job_errors(tmp_path: pathlib.Path) -> None:
    wf = tmp_path / ".github" / "workflows"
    wf.mkdir(parents=True)
    (wf / "ci.yml").write_text(
        "name: CI\non: push\njobs:\n  lint:\n    runs-on: ubuntu-latest\n    steps:\n      - run: echo hi\n",
        encoding="utf-8",
    )
    doc = tmp_path / "docs"
    doc.mkdir(parents=True)
    (doc / "DEPENDENCY_AUDIT.md").write_text(
        _minimal_doc("CVE-2026-7000"), encoding="utf-8"
    )
    errs = collect_errors(tmp_path)
    assert any("supply-chain" in e for e in errs)
