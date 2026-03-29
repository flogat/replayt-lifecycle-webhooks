"""Guard CI and packaging wiring for ruff (SPEC_AUTOMATED_TESTS RF1–RF2, backlog 5a3f5a7f)."""

from __future__ import annotations

import pathlib

import pytest
import tomllib
import yaml


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


def _ci_workflow_dict() -> dict:
    path = _repo_root() / ".github" / "workflows" / "ci.yml"
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_ci_lint_job_matrix_includes_python_311_312_and_313() -> None:
    """CI1 + SPEC_REPLAYT_DEPENDENCY A9/A11: lint runs on floor, 3.12, and 3.13 (backlog 8e58aa9c)."""
    wf = _ci_workflow_dict()
    matrix = wf["jobs"]["lint"]["strategy"]["matrix"]
    versions = matrix["python-version"]
    assert "3.11" in versions
    assert "3.12" in versions
    assert "3.13" in versions
    text = (_repo_root() / ".github" / "workflows" / "ci.yml").read_text(
        encoding="utf-8"
    )
    assert "${{ matrix.python-version }}" in text


def test_ci_test_job_matrix_includes_python_311_312_and_313() -> None:
    """CI2 + SPEC_REPLAYT_DEPENDENCY A9/A11: test runs on 3.11, 3.12, and 3.13 (backlog 8e58aa9c)."""
    wf = _ci_workflow_dict()
    matrix = wf["jobs"]["test"]["strategy"]["matrix"]
    versions = matrix["python-version"]
    assert "3.11" in versions
    assert "3.12" in versions
    assert "3.13" in versions


@pytest.mark.parametrize("job", ("package", "supply-chain"))
def test_ci_package_and_supply_chain_stay_on_single_python_312(job: str) -> None:
    """A10: packaging and pip-audit jobs are not matrixed across Python minors (backlog 6cd22a7b)."""
    wf = _ci_workflow_dict()
    assert "strategy" not in wf["jobs"][job]
    steps = wf["jobs"][job]["steps"]
    setup = next(s for s in steps if s.get("uses") == "actions/setup-python@v5")
    assert setup["with"]["python-version"] == "3.12"
