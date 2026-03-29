"""Guard CI packaging job wiring (SPEC_AUTOMATED_TESTS PK1–PK4, backlog 78e3554b)."""

from __future__ import annotations

import pathlib

import tomllib


def _repo_root() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parents[1]


def test_pyproject_dev_extra_includes_build_and_twine() -> None:
    data = tomllib.loads((_repo_root() / "pyproject.toml").read_text(encoding="utf-8"))
    dev = data["project"]["optional-dependencies"]["dev"]
    lower = [str(line).strip().lower() for line in dev]
    assert any(line.startswith("build>=") for line in lower), (
        "expected build>=… in [project.optional-dependencies] dev (PK2/PK7 alignment)"
    )
    assert any(line.startswith("twine>=") for line in lower), (
        "expected twine>=… in [project.optional-dependencies] dev (PK2/PK7 alignment)"
    )


def test_ci_workflow_defines_package_job() -> None:
    text = (_repo_root() / ".github" / "workflows" / "ci.yml").read_text(
        encoding="utf-8"
    )
    assert "jobs:" in text
    assert "  package:" in text
    assert "build>=" in text
    assert "twine>=" in text
    assert "rm -rf dist" in text
    assert "python -m build" in text
    assert "twine check dist/*" in text
