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


def test_replayt_installed_version_meets_pyproject_lower_bound() -> None:
    minimum = _replayt_lower_bound()
    installed = md.version("replayt")
    assert _version_tuple(installed) >= minimum
