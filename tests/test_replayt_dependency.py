"""Integration boundary: installed replayt matches the declared lower bound in pyproject.toml."""

from __future__ import annotations

import pathlib
import re
import tomllib

import importlib.metadata as md


def _repo_root() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parents[1]


def _replayt_lower_bound() -> tuple[int, ...]:
    data = tomllib.loads((_repo_root() / "pyproject.toml").read_text(encoding="utf-8"))
    for raw in data["project"]["dependencies"]:
        dep = raw.strip()
        m = re.fullmatch(r"replayt>=(\d+)\.(\d+)\.(\d+)", dep)
        if m:
            return tuple(int(g) for g in m.groups())
    raise AssertionError("expected replayt>=X.Y.Z in [project.dependencies]")


def _version_tuple(version: str) -> tuple[int, ...]:
    # PEP 440 allows suffixes; compare only the release segment.
    release = version.split("+", 1)[0].split("-", 1)[0]
    parts = release.split(".")
    if len(parts) < 3:
        raise AssertionError(f"unexpected replayt version shape: {version!r}")
    return tuple(int(p) for p in parts[:3])


def _requires_python_from_pyproject() -> str:
    data = tomllib.loads((_repo_root() / "pyproject.toml").read_text(encoding="utf-8"))
    return str(data["project"]["requires-python"])


def _workflow_python_versions() -> list[str]:
    text = (_repo_root() / ".github" / "workflows" / "ci.yml").read_text(
        encoding="utf-8"
    )
    return re.findall(r'python-version:\s*["\']([\d.]+)["\']', text)


def _compatibility_matrix_doc_section(spec_text: str) -> str:
    start = spec_text.index("## Compatibility matrix")
    end = spec_text.index("## Reporting breakage", start)
    return spec_text[start:end]


def test_pyproject_has_single_canonical_replayt_lower_bound() -> None:
    """SPEC: one `replayt>=M.m.p` line in [project.dependencies] for parsers and installs."""
    data = tomllib.loads((_repo_root() / "pyproject.toml").read_text(encoding="utf-8"))
    matches: list[str] = []
    for raw in data["project"]["dependencies"]:
        dep = raw.strip()
        if re.fullmatch(r"replayt>=\d+\.\d+\.\d+", dep):
            matches.append(dep)
    assert len(matches) == 1, (
        f"expected exactly one replayt>=M.m.p line, got {matches!r}"
    )


def test_readme_documents_integrator_compatibility() -> None:
    """SPEC A2 (+ A8): floor check commands, PyPI/history links, matrix pointer, CI-tested Python, report path."""
    text = (_repo_root() / "README.md").read_text(encoding="utf-8")
    required = (
        "docs/SPEC_REPLAYT_DEPENDENCY.md",
        "https://pypi.org/project/replayt/",
        "https://pypi.org/project/replayt/#history",
        "https://github.com/flogat/replayt-lifecycle-webhooks/issues",
        "pip show replayt",
        "importlib.metadata",
        "Compatibility matrix",
        "replayt-lifecycle-webhooks",
        ".github/workflows/ci.yml",
    )
    missing = [s for s in required if s not in text]
    assert not missing, f"README missing expected integrator strings: {missing}"
    versions = _workflow_python_versions()
    assert versions, "expected python-version in .github/workflows/ci.yml"
    assert len(set(versions)) == 1, (
        f"CI must pin one Python version for README alignment, got {versions!r}"
    )
    assert f"Python {versions[0]}" in text, (
        "README must state the same Python minor CI uses (see SPEC A8)"
    )


def test_replayt_installed_version_meets_pyproject_lower_bound() -> None:
    minimum = _replayt_lower_bound()
    installed = md.version("replayt")
    assert _version_tuple(installed) >= minimum


def test_design_principles_points_at_replayt_dependency_spec() -> None:
    """SPEC: DESIGN_PRINCIPLES names the matrix and SPEC_REPLAYT_DEPENDENCY."""
    text = (_repo_root() / "docs" / "DESIGN_PRINCIPLES.md").read_text(encoding="utf-8")
    assert "SPEC_REPLAYT_DEPENDENCY.md" in text
    assert "compatibility matrix" in text.lower()


def test_spec_compatibility_matrix_matches_pyproject_replayt_floor() -> None:
    """SPEC A5: matrix documents the same lower bound as [project.dependencies]."""
    minimum = _replayt_lower_bound()
    floor = f">={minimum[0]}.{minimum[1]}.{minimum[2]}"
    spec = (_repo_root() / "docs" / "SPEC_REPLAYT_DEPENDENCY.md").read_text(
        encoding="utf-8"
    )
    assert "## Compatibility matrix" in spec
    assert floor in spec
    assert "no upper bound" in spec.lower() or "upper bound" in spec.lower()


def test_a8_workflow_pins_single_python_minor() -> None:
    """SPEC A8: one interpreter version across CI jobs that set python-version."""
    versions = _workflow_python_versions()
    assert versions, "expected python-version entries in .github/workflows/ci.yml"
    assert len(set(versions)) == 1, (
        f"all CI jobs must use the same python-version, got {versions!r}"
    )


def test_a8_spec_matrix_aligns_requires_python_ci_and_workflow_path() -> None:
    """SPEC A8: matrix lists requires-python, CI-tested Python, workflow path, and replayt resolution note."""
    root = _repo_root()
    req_py = _requires_python_from_pyproject()
    spec = (root / "docs" / "SPEC_REPLAYT_DEPENDENCY.md").read_text(encoding="utf-8")
    matrix = _compatibility_matrix_doc_section(spec)
    ci_versions = _workflow_python_versions()
    assert len(set(ci_versions)) == 1
    ci_py = ci_versions[0]

    assert "`requires-python`" in matrix or "requires-python" in matrix
    assert "CI-tested Python" in matrix
    assert req_py in matrix, (
        f"compatibility matrix must echo pyproject requires-python {req_py!r} "
        "(SPEC_REPLAYT_DEPENDENCY.md ## Compatibility matrix)"
    )
    assert ci_py in matrix, f"compatibility matrix must list CI-tested Python {ci_py!r}"
    assert ".github/workflows/ci.yml" in matrix

    assert "A8 |" in spec
    assert "**CI note on replayt versions:**" in spec
    note_start = spec.index("**CI note on replayt versions:**")
    note_snippet = spec[note_start : note_start + 450].lower()
    assert "pip" in note_snippet and "resolves" in note_snippet
