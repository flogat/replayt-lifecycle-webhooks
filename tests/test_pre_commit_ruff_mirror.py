"""Guard optional pre-commit wiring for ruff (SPEC_AUTOMATED_TESTS PC1–PC2, backlog c39b2a5f)."""

from __future__ import annotations

import pathlib


def _repo_root() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parents[1]


def test_pre_commit_config_exists() -> None:
    assert (_repo_root() / ".pre-commit-config.yaml").is_file()


def test_pre_commit_config_mirrors_ci_lint_ruff() -> None:
    text = (_repo_root() / ".pre-commit-config.yaml").read_text(encoding="utf-8")
    assert "astral-sh/ruff-pre-commit" in text
    assert "ruff-check" in text
    assert "ruff-format" in text
    assert "--check" in text
    assert "pass_filenames: false" in text
    assert "args:" in text
    # Same path arguments as `.github/workflows/ci.yml` lint job.
    assert "src" in text
    assert "tests" in text
    assert "rev:" in text
    assert (
        "bundled ruff" in text.lower()
        or "ruff>=" in text.lower()
        or "lower bound" in text.lower()
    )


def test_contributing_documents_pre_commit_optional_and_ci_truth() -> None:
    md = (_repo_root() / "CONTRIBUTING.md").read_text(encoding="utf-8")
    assert "pre-commit" in md.lower()
    assert "pre-commit install" in md
    assert ".github/workflows/ci.yml" in md
    assert "lint" in md.lower()
    assert "optional" in md.lower()
    assert "drive-by" in md.lower() or "without installing" in md.lower()
