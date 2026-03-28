"""Local signed demo POST (SPEC_LOCAL_WEBHOOK_DEMO D3, D7, D8, D9)."""

from __future__ import annotations

import subprocess
import sys
import urllib.error
from importlib.resources import files
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from replayt_lifecycle_webhooks.demo_webhook import (
    DEFAULT_FIXTURE_PRESET,
    load_demo_fixture_bytes,
    main,
    post_signed_demo,
)
from replayt_lifecycle_webhooks.signature import (
    compute_lifecycle_webhook_signature_header,
    verify_lifecycle_webhook_signature,
)

_REPO_ROOT = Path(__file__).resolve().parents[1]
_TESTS_EVENTS = _REPO_ROOT / "tests" / "fixtures" / "events"
_PRESETS = [
    "approval_pending",
    "approval_resolved",
    "run_completed",
    "run_failed",
    "run_started",
]


@pytest.mark.parametrize("preset", _PRESETS)
def test_packaged_fixture_matches_repo_fixture(preset: str) -> None:
    """Packaged demo bodies stay aligned with tests/fixtures/events (D5)."""
    packaged = load_demo_fixture_bytes(preset)
    disk = (_TESTS_EVENTS / f"{preset}.json").read_bytes()
    assert packaged == disk


def test_packaged_run_started_redelivery_matches_repo_fixture() -> None:
    """Duplicate-delivery fixture (I3) stays byte-identical under src and tests trees."""
    root = files("replayt_lifecycle_webhooks")
    packaged = root.joinpath(
        "fixtures", "events", "run_started_redelivery.json"
    ).read_bytes()
    disk = (_TESTS_EVENTS / "run_started_redelivery.json").read_bytes()
    assert packaged == disk
    assert disk == (_TESTS_EVENTS / "run_started.json").read_bytes()


def test_d3_demo_signing_verify_agrees_on_run_completed() -> None:
    """D3: header from compute + fixture bytes passes verify_lifecycle_webhook_signature."""
    secret = "demo-test-secret-utf8"
    body = load_demo_fixture_bytes(DEFAULT_FIXTURE_PRESET)
    header = compute_lifecycle_webhook_signature_header(secret=secret, body=body)
    verify_lifecycle_webhook_signature(secret=secret, body=body, signature=header)


def test_d3_post_signed_demo_matches_verify() -> None:
    """Signing used for outbound POST matches the verifier (same code path as CLI)."""
    secret = b"byte-key-demo"
    body = load_demo_fixture_bytes("run_started")
    sig = compute_lifecycle_webhook_signature_header(secret=secret, body=body)

    def fake_urlopen(request, timeout=0):  # noqa: ANN001, ANN201
        hdrs = {k.lower(): v for k, v in request.header_items()}
        assert hdrs.get("replayt-signature") == sig
        assert request.data == body
        resp = MagicMock()
        resp.status = 204
        resp.__enter__ = lambda s: s
        resp.__exit__ = lambda *a: None
        return resp

    with patch(
        "replayt_lifecycle_webhooks.demo_webhook.urllib.request.urlopen", fake_urlopen
    ):
        code = post_signed_demo(
            url="http://127.0.0.1:9/webhook", secret=secret, body=body, timeout=1.0
        )
    assert code == 204
    verify_lifecycle_webhook_signature(secret=secret, body=body, signature=sig)


def test_d8_main_non_2xx_exit_code() -> None:
    """D8: non-2xx HTTP from the server yields a non-zero CLI exit."""

    def fake_urlopen(request, timeout=0):  # noqa: ANN001, ANN201
        raise urllib.error.HTTPError(
            url="http://example.invalid/webhook",
            code=500,
            msg="Internal Server Error",
            hdrs=None,
            fp=None,
        )

    with patch(
        "replayt_lifecycle_webhooks.demo_webhook.urllib.request.urlopen", fake_urlopen
    ):
        rc = main(
            [
                "--secret",
                "s",
                "--fixture",
                DEFAULT_FIXTURE_PRESET,
                "--url",
                "http://127.0.0.1:9/webhook",
            ]
        )
    assert rc == 1


def test_d9_main_does_not_print_secret_or_signature(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """D9: default output must not echo the secret or full signature header."""

    def fake_urlopen(request, timeout=0):  # noqa: ANN001, ANN201
        hdrs = {k.lower(): v for k, v in request.header_items()}
        got = hdrs.get("replayt-signature")
        assert got and got.startswith("sha256=")
        resp = MagicMock()
        resp.status = 204
        resp.__enter__ = lambda s: s
        resp.__exit__ = lambda *a: None
        return resp

    secret = "very-long-demo-secret-value-xyz"
    with patch(
        "replayt_lifecycle_webhooks.demo_webhook.urllib.request.urlopen", fake_urlopen
    ):
        rc = main(
            [
                "--secret",
                secret,
                "--fixture",
                DEFAULT_FIXTURE_PRESET,
                "--url",
                "http://127.0.0.1:9/webhook",
            ]
        )
    assert rc == 0
    out, err = capsys.readouterr()
    combined = f"{out}\n{err}"
    assert secret not in combined
    assert "sha256=" not in combined.lower()


def test_load_fixture_from_repo_path_matches_preset() -> None:
    path = str(_TESTS_EVENTS / "run_completed.json")
    assert load_demo_fixture_bytes(path) == load_demo_fixture_bytes("run_completed")


def test_help_documents_env_secret() -> None:
    """D4: --help names REPLAYT_LIFECYCLE_WEBHOOK_SECRET."""
    proc = subprocess.run(
        [sys.executable, "-m", "replayt_lifecycle_webhooks.demo_webhook", "--help"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "REPLAYT_LIFECYCLE_WEBHOOK_SECRET" in proc.stdout
