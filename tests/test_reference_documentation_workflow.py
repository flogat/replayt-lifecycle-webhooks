"""SPEC_REFERENCE_DOCUMENTATION / SPEC_AUTOMATED_TESTS backlog eb884da9 RD1–RD5."""

from __future__ import annotations

import pathlib
import subprocess


def _repo_root() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parents[1]


def _read(rel: str) -> str:
    return (_repo_root() / rel).read_text(encoding="utf-8")


def _h2_section(text: str, title: str) -> str:
    """Return lines under ``## {title}`` until the next level-2 ``## `` heading."""
    lines = text.splitlines()
    heading = f"## {title}"
    start: int | None = None
    for i, line in enumerate(lines):
        if line == heading:
            start = i + 1
            break
    if start is None:
        return ""
    out: list[str] = []
    for line in lines[start:]:
        if line.startswith("## ") and not line.startswith("###"):
            break
        out.append(line)
    return "\n".join(out)


def test_rd1_folder_readme_optional_use_snapshot_and_spec_link() -> None:
    text = _read("docs/reference-documentation/README.md")
    assert "optional" in text.lower()
    assert "_upstream_snapshot/" in text
    assert "SPEC_REFERENCE_DOCUMENTATION.md" in text


def test_rd2_root_readme_reference_section_links_and_refresh() -> None:
    root_readme = _read("README.md")
    body = _h2_section(root_readme, "Reference documentation (optional)")
    assert body.strip() != ""
    assert "docs/reference-documentation/README.md" in body
    assert "docs/SPEC_REFERENCE_DOCUMENTATION.md" in body
    assert "How to refresh" in body
    assert "manually" in body.lower() or "manual" in body.lower()
    assert "scripts/" in body


def test_rd3_gitignore_lists_upstream_snapshot_and_git_honors_rule() -> None:
    gitignore = _read(".gitignore")
    assert "docs/reference-documentation/_upstream_snapshot/" in gitignore
    root = _repo_root()
    proc = subprocess.run(
        [
            "git",
            "check-ignore",
            "-v",
            "docs/reference-documentation/_upstream_snapshot/placeholder.md",
        ],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    assert "_upstream_snapshot" in proc.stdout


def test_rd4_ci_does_not_touch_reference_documentation_tree() -> None:
    """CI must not script downloads or mirrors into docs/reference-documentation/."""
    ci = _read(".github/workflows/ci.yml")
    assert "reference-documentation" not in ci.lower()


def test_rd5_spec_automated_tests_traces_backlog_and_rows() -> None:
    spec = _read("docs/SPEC_AUTOMATED_TESTS.md")
    assert "## Backlog `eb884da9`" in spec
    for n in range(1, 6):
        assert f"| **RD{n}** |" in spec
