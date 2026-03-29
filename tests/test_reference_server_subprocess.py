"""Subprocess + loopback HTTP against real ``python -m replayt_lifecycle_webhooks`` (SUB1–SUB6).

Normative checklist: **docs/SPEC_AUTOMATED_TESTS.md** backlog **83e07114** (**SUB1**–**SUB8**).
"""

from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from collections.abc import Generator
from pathlib import Path

import pytest

from replayt_lifecycle_webhooks.serve import DEFAULT_WEBHOOK_PATH
from replayt_lifecycle_webhooks.signature import (
    compute_lifecycle_webhook_signature_header,
)

_SECRET = "subprocess-ref-server-integration-secret"
_HEALTH_TIMEOUT_S = 20.0
_HEALTH_POLL_S = 0.05
_TEARDOWN_GRACE_S = 8.0

_REPO_ROOT = Path(__file__).resolve().parents[1]
_FIXTURE_BODY = (
    _REPO_ROOT / "tests" / "fixtures" / "events" / "run_started.json"
).read_bytes()


def _pick_free_loopback_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


def _wait_until_health_ok(
    base_url: str,
    proc: subprocess.Popen[bytes],
    *,
    timeout_s: float,
) -> None:
    """SUB2: bounded wait for GET /health → 200."""
    deadline = time.monotonic() + timeout_s
    health_url = f"{base_url}/health"
    while time.monotonic() < deadline:
        code = proc.poll()
        if code is not None:
            msg = f"reference server exited early with code {code}"
            raise AssertionError(msg)
        try:
            with urllib.request.urlopen(health_url, timeout=1.0) as resp:
                if resp.getcode() == 200:
                    return
        except urllib.error.HTTPError:
            pass
        except urllib.error.URLError:
            pass
        time.sleep(_HEALTH_POLL_S)
    raise TimeoutError(
        f"GET /health did not return 200 within {timeout_s}s ({health_url})"
    )


def _stop_server(proc: subprocess.Popen[bytes]) -> None:
    """SUB5: terminate, then kill if needed."""
    if proc.poll() is not None:
        return
    proc.terminate()
    try:
        proc.wait(timeout=_TEARDOWN_GRACE_S)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=_TEARDOWN_GRACE_S)


@pytest.fixture
def subprocess_reference_server_base_url() -> Generator[str, None, None]:
    """SUB1: spawn ``sys.executable -m replayt_lifecycle_webhooks`` with env secret and loopback port."""
    port = _pick_free_loopback_port()
    env = os.environ.copy()
    env["REPLAYT_LIFECYCLE_WEBHOOK_SECRET"] = _SECRET
    cmd = [
        sys.executable,
        "-m",
        "replayt_lifecycle_webhooks",
        "--host",
        "127.0.0.1",
        "--port",
        str(port),
    ]
    proc = subprocess.Popen(
        cmd,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    base = f"http://127.0.0.1:{port}"
    try:
        _wait_until_health_ok(base, proc, timeout_s=_HEALTH_TIMEOUT_S)
        yield base
    finally:
        _stop_server(proc)


def test_subprocess_signed_post_fixture_returns_204(
    subprocess_reference_server_base_url: str,
) -> None:
    """SUB3–SUB4: signed POST with committed fixture bytes; expect 204."""
    sig = compute_lifecycle_webhook_signature_header(secret=_SECRET, body=_FIXTURE_BODY)
    url = f"{subprocess_reference_server_base_url}{DEFAULT_WEBHOOK_PATH}"
    req = urllib.request.Request(
        url,
        data=_FIXTURE_BODY,
        method="POST",
        headers={"Replayt-Signature": sig},
    )
    with urllib.request.urlopen(req, timeout=15.0) as resp:
        assert resp.getcode() == 204
