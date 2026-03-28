"""Guard CI and packaging wiring for ruff (SPEC_AUTOMATED_TESTS RF1–RF2, backlog 5a3f5a7f)."""

from __future__ import annotations

import pathlib

import tomllib


def _repo_root() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parents[1]


def test_pyproject_dev_extra_includes_ruff() -> None:
    data = tomllib.loads((_repo_root() / "pyproject.toml").read_text(encoding="utf-8"))
    dev = data["project"]["optional-dependencies"]["dev"]
    assert any(str(line).strip().lower().startswith("ruff>=") for line in dev), (
        "expected ruff>=… in [project.optional-dependencies] dev"
    )


def test_ci_workflow_defines_lint_job_with_ruff() -> None:
    text = (_repo_root() / ".github" / "workflows" / "ci.yml").read_text(
        encoding="utf-8"
    )
    assert "jobs:" in text
    assert "  lint:" in text
    assert "ruff check src tests" in text
    assert "ruff format --check src tests" in text


def test_pyproject_has_tool_ruff_target_version() -> None:
    """RF3: target-version aligns with requires-python floor."""
    data = tomllib.loads((_repo_root() / "pyproject.toml").read_text(encoding="utf-8"))
    assert "tool" in data and "ruff" in data["tool"]
    assert data["tool"]["ruff"].get("target-version") == "py311"
