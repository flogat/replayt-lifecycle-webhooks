"""PK5–PK6: built wheel and sdist contain declared package data (SPEC_AUTOMATED_TESTS § 78e3554b)."""

from __future__ import annotations

import glob
import pathlib
import subprocess
import sys
import tarfile
import zipfile

import pytest

pytest.importorskip(
    "build",
    reason="PK5–PK7 layout tests need [project.optional-dependencies] dev (build, twine)",
)

_WHEEL_FIXTURE_MEMBER = "replayt_lifecycle_webhooks/fixtures/events/run_started.json"
_SDIST_FIXTURE_SUFFIX = "replayt_lifecycle_webhooks/fixtures/events/run_started.json"


def _repo_root() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parents[1]


def _run_build(dist_dir: pathlib.Path) -> None:
    root = _repo_root()
    proc = subprocess.run(
        [sys.executable, "-m", "build", "--outdir", str(dist_dir)],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        pytest.fail(
            f"python -m build failed:\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
        )


def _run_twine_check(dist_dir: pathlib.Path) -> None:
    artifacts = sorted(glob.glob(str(dist_dir / "*")))
    assert artifacts, f"expected build artifacts under {dist_dir}"
    proc = subprocess.run(
        [sys.executable, "-m", "twine", "check", *artifacts],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        pytest.fail(
            f"twine check failed:\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
        )


def test_built_wheel_contains_declared_event_fixture(tmp_path: pathlib.Path) -> None:
    dist = tmp_path / "dist"
    dist.mkdir()
    _run_build(dist)
    _run_twine_check(dist)
    wheels = list(dist.glob("*.whl"))
    assert len(wheels) == 1, f"expected one wheel, got {[p.name for p in wheels]}"
    with zipfile.ZipFile(wheels[0]) as zf:
        names = zf.namelist()
    assert _WHEEL_FIXTURE_MEMBER in names, (
        f"missing {_WHEEL_FIXTURE_MEMBER!r} in wheel; sample names: {names[:20]!r}"
    )


def test_built_sdist_contains_declared_event_fixture(tmp_path: pathlib.Path) -> None:
    dist = tmp_path / "dist"
    dist.mkdir()
    _run_build(dist)
    sdists = list(dist.glob("*.tar.gz"))
    assert len(sdists) == 1, f"expected one sdist, got {[p.name for p in sdists]}"
    with tarfile.open(sdists[0], "r:gz") as tf:
        members = [m.name.replace("\\", "/") for m in tf.getmembers() if m.isfile()]
    assert any(m.endswith(_SDIST_FIXTURE_SUFFIX) for m in members), (
        f"no member ending with {_SDIST_FIXTURE_SUFFIX!r}; sample: {members[:25]!r}"
    )


def test_built_wheel_includes_py_typed_when_present_in_source(
    tmp_path: pathlib.Path,
) -> None:
    """PK6: only assert py.typed in the wheel when the marker exists under src/."""
    marker = _repo_root() / "src" / "replayt_lifecycle_webhooks" / "py.typed"
    dist = tmp_path / "dist"
    dist.mkdir()
    _run_build(dist)
    wheels = list(dist.glob("*.whl"))
    assert len(wheels) == 1
    with zipfile.ZipFile(wheels[0]) as zf:
        names = zf.namelist()
    wheel_typed = "replayt_lifecycle_webhooks/py.typed"
    if marker.is_file():
        assert wheel_typed in names, (
            f"expected {wheel_typed!r} in wheel when src marker exists"
        )
    else:
        assert wheel_typed not in names, (
            f"unexpected {wheel_typed!r} in wheel without src marker (PK6)"
        )
