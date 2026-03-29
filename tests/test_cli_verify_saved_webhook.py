"""Offline verify CLI (``python -m replayt_lifecycle_webhooks verify``) — VW1–VW8.

Normative: **docs/SPEC_CLI_VERIFY_SAVED_WEBHOOK.md**, **docs/SPEC_AUTOMATED_TESTS.md** backlog **845b4b11**.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

from replayt_lifecycle_webhooks.signature import (
    compute_lifecycle_webhook_signature_header,
)

_REPO_ROOT = Path(__file__).resolve().parents[1]
_RUN_STARTED = _REPO_ROOT / "tests" / "fixtures" / "events" / "run_started.json"
_SECRET_VW4 = "vw4-distinctive-cli-test-secret-not-in-stderr"


def _run_verify(
    *args: str,
    env: dict[str, str] | None = None,
    input_bytes: bytes | None = None,
) -> subprocess.CompletedProcess[str]:
    base = dict(os.environ)
    base.pop("REPLAYT_LIFECYCLE_WEBHOOK_SECRET", None)
    if env:
        base.update(env)
    cmd = [sys.executable, "-m", "replayt_lifecycle_webhooks", "verify", *args]
    if input_bytes is not None:
        proc = subprocess.run(
            cmd,
            cwd=str(_REPO_ROOT),
            env=base,
            input=input_bytes,
            capture_output=True,
            text=False,
            check=False,
        )
        return subprocess.CompletedProcess(
            proc.args,
            proc.returncode,
            proc.stdout.decode("utf-8", errors="replace"),
            proc.stderr.decode("utf-8", errors="replace"),
        )
    return subprocess.run(
        cmd,
        cwd=str(_REPO_ROOT),
        env=base,
        capture_output=True,
        text=True,
        check=False,
    )


def test_vw2_help_lists_raw_body_secret_and_exit_codes() -> None:
    """VW2: --help covers raw body discipline, env var, and exit 0/1/2."""
    proc = subprocess.run(
        [sys.executable, "-m", "replayt_lifecycle_webhooks", "verify", "--help"],
        cwd=str(_REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0
    out = proc.stdout
    assert "Re-serializing JSON" in out or "raw" in out.lower()
    assert "REPLAYT_LIFECYCLE_WEBHOOK_SECRET" in out
    assert "Exit codes:" in out
    assert " 0 " in out or out.count("0") >= 1
    assert " 1 " in out or "1 verification" in out
    assert " 2 " in out or "2 usage" in out


def test_vw3_fixture_file_valid_signature_ok_stdout() -> None:
    """VW3: fixture path + valid --signature → exit 0, stdout ok\\n."""
    body = _RUN_STARTED.read_bytes()
    secret = "vw3-fixture-secret"
    sig = compute_lifecycle_webhook_signature_header(secret=secret, body=body)
    proc = _run_verify(
        "--signature",
        sig,
        str(_RUN_STARTED),
        env={"REPLAYT_LIFECYCLE_WEBHOOK_SECRET": secret},
    )
    assert proc.returncode == 0
    assert proc.stdout == "ok\n"
    assert proc.stderr == ""


def test_vw4_wrong_signature_exit_one_no_secret_or_mac_leak() -> None:
    """VW4: MAC failure → 1; stderr must not contain secret or full expected digest hex."""
    body = _RUN_STARTED.read_bytes()
    good = compute_lifecycle_webhook_signature_header(secret=_SECRET_VW4, body=body)
    wrong = "sha256=" + "0" * 64
    assert wrong != good
    proc = _run_verify(
        "--signature",
        wrong,
        str(_RUN_STARTED),
        env={"REPLAYT_LIFECYCLE_WEBHOOK_SECRET": _SECRET_VW4},
    )
    assert proc.returncode == 1
    combined = proc.stdout + proc.stderr
    assert _SECRET_VW4 not in combined
    expected_hex = good.removeprefix("sha256=").lower()
    assert len(expected_hex) == 64
    assert expected_hex not in combined.lower()


def test_vw5_stdin_body_valid_signature_ok() -> None:
    """VW5: body from stdin (-) + valid signature → exit 0."""
    body = _RUN_STARTED.read_bytes()
    secret = "vw5-stdin-secret"
    sig = compute_lifecycle_webhook_signature_header(secret=secret, body=body)
    proc = _run_verify(
        "--signature",
        sig,
        "-",
        env={"REPLAYT_LIFECYCLE_WEBHOOK_SECRET": secret},
        input_bytes=body,
    )
    assert proc.returncode == 0
    assert proc.stdout == "ok\n"


def test_vw6_missing_secret_exit_two() -> None:
    """VW6: no env secret and no --secret → exit 2."""
    body = _RUN_STARTED.read_bytes()
    sig = compute_lifecycle_webhook_signature_header(secret="any", body=body)
    proc = _run_verify("--signature", sig, str(_RUN_STARTED))
    assert proc.returncode == 2
    assert "secret" in proc.stderr.lower()


def test_vw7_readme_links_cli_spec() -> None:
    """VW1/VW7 doc bar: README mentions canonical verify invocation and CLI spec."""
    readme = (_REPO_ROOT / "README.md").read_text(encoding="utf-8")
    assert "python -m replayt_lifecycle_webhooks verify" in readme
    assert "docs/SPEC_CLI_VERIFY_SAVED_WEBHOOK.md" in readme


def test_vw7_public_api_table_documents_verify() -> None:
    """VW7: SPEC_PUBLIC_API verify row documents shipped CLI (no 'when implemented' on that row)."""
    text = (_REPO_ROOT / "docs" / "SPEC_PUBLIC_API.md").read_text(encoding="utf-8")
    needle = "| `python -m replayt_lifecycle_webhooks verify` |"
    assert needle in text
    row_start = text.index(needle)
    row = text[row_start : text.index("\n", row_start)]
    assert "when implemented" not in row


@pytest.mark.parametrize(
    "extra_args,expect",
    [
        (["--signature", "sha256=ab"], 2),
        (["--signature", "sha256=" + "g" * 64, str(_RUN_STARTED)], 1),
    ],
)
def test_verify_argparse_or_format_errors(extra_args: list[str], expect: int) -> None:
    """Missing BODY → 2; invalid hex with body → 1."""
    env = {"REPLAYT_LIFECYCLE_WEBHOOK_SECRET": "x"}
    proc = _run_verify(*extra_args, env=env)
    assert proc.returncode == expect


def test_signature_file_trailing_newline_stripped() -> None:
    body = _RUN_STARTED.read_bytes()
    secret = "sigfile-secret"
    sig = compute_lifecycle_webhook_signature_header(secret=secret, body=body)
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        f.write(sig + "\n")
        sig_path = f.name
    try:
        proc = _run_verify(
            "--signature-file",
            sig_path,
            str(_RUN_STARTED),
            env={"REPLAYT_LIFECYCLE_WEBHOOK_SECRET": secret},
        )
    finally:
        os.unlink(sig_path)
    assert proc.returncode == 0
    assert proc.stdout == "ok\n"
