"""PK5–PK7, TP3: wheel/sdist contain fixtures and PEP 561 ``py.typed`` (78e3554b, 2ec2c21c)."""

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
_SDIST_PY_TYPED_SUFFIX = "replayt_lifecycle_webhooks/py.typed"
_WHEEL_PY_TYPED = "replayt_lifecycle_webhooks/py.typed"


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
    assert _WHEEL_PY_TYPED in names, (
        f"missing {_WHEEL_PY_TYPED!r} in wheel (TP3); sample names: {names[:20]!r}"
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
    assert any(m.endswith(_SDIST_PY_TYPED_SUFFIX) for m in members), (
        f"no member ending with {_SDIST_PY_TYPED_SUFFIX!r}; sample: {members[:25]!r}"
    )
