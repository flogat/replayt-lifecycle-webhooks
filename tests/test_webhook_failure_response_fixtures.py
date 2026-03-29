"""FR5: canonical webhook error JSON fixtures match the reference handler (SPEC_WEBHOOK_FAILURE_RESPONSES)."""

from __future__ import annotations

import hashlib
import hmac
import json
from datetime import datetime, timezone
from pathlib import Path

from replayt_lifecycle_webhooks.handler import handle_lifecycle_webhook_post
from replayt_lifecycle_webhooks.replay_protection import LifecycleWebhookReplayPolicy
from replayt_lifecycle_webhooks.signature import LIFECYCLE_WEBHOOK_SIGNATURE_HEADER

_FIXTURE_DIR = (
    Path(__file__).resolve().parent / "fixtures" / "webhook_failure_responses"
)
_SECRET = "handler-test-secret"
_GOOD_BODY = b'{"event":"run_finished","run_id":"r1"}'
_EVENTS_FIXTURE = (
    Path(__file__).resolve().parent / "fixtures" / "events" / "run_started.json"
)


def _sign(body: bytes, secret: str | bytes = _SECRET) -> str:
    key = secret.encode("utf-8") if isinstance(secret, str) else secret
    mac = hmac.new(key, body, hashlib.sha256)
    return f"sha256={mac.hexdigest()}"


def _fake_headers(signature: str | None) -> dict[str, str]:
    h: dict[str, str] = {}
    if signature is not None:
        h[LIFECYCLE_WEBHOOK_SIGNATURE_HEADER] = signature
    return h


def _fixture_bytes(code: str) -> bytes:
    return (_FIXTURE_DIR / f"{code}.json").read_bytes()


def test_fr5_canonical_fixtures_match_reference_handler_bodies() -> None:
    """Each committed fixture equals ``handle_lifecycle_webhook_post`` body for that ``error`` code."""
    raw = b"not-json"
    stale_event = json.loads(_EVENTS_FIXTURE.read_bytes())
    stale_event["occurred_at"] = "2020-01-01T00:00:00Z"
    stale_body = json.dumps(
        stale_event, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    cases: list[tuple[object, str]] = [
        (
            handle_lifecycle_webhook_post(
                secret=_SECRET,
                method="GET",
                body=_GOOD_BODY,
                headers=_fake_headers(_sign(_GOOD_BODY)),
            ),
            "method_not_allowed",
        ),
        (
            handle_lifecycle_webhook_post(
                secret=_SECRET, method="POST", body=_GOOD_BODY, headers={}
            ),
            "signature_required",
        ),
        (
            handle_lifecycle_webhook_post(
                secret=_SECRET,
                method="POST",
                body=_GOOD_BODY,
                headers=_fake_headers("nope"),
            ),
            "signature_malformed",
        ),
        (
            handle_lifecycle_webhook_post(
                secret=_SECRET,
                method="POST",
                body=_GOOD_BODY,
                headers=_fake_headers(_sign(_GOOD_BODY, secret="x")),
            ),
            "signature_mismatch",
        ),
        (
            handle_lifecycle_webhook_post(
                secret=_SECRET,
                method="POST",
                body=raw,
                headers=_fake_headers(_sign(raw)),
            ),
            "invalid_json",
        ),
        (
            handle_lifecycle_webhook_post(
                secret=_SECRET,
                method="POST",
                body=b"[1]",
                headers=_fake_headers(_sign(b"[1]")),
                replay_policy=LifecycleWebhookReplayPolicy(check_occurred_at=False),
            ),
            "invalid_payload_shape",
        ),
        (
            handle_lifecycle_webhook_post(
                secret=_SECRET,
                method="POST",
                body=_GOOD_BODY,
                headers=_fake_headers(_sign(_GOOD_BODY)),
                replay_policy=LifecycleWebhookReplayPolicy(check_occurred_at=False),
            ),
            "unknown_event_type",
        ),
        (
            handle_lifecycle_webhook_post(
                secret=_SECRET,
                method="POST",
                body=stale_body,
                headers=_fake_headers(_sign(stale_body)),
                replay_policy=LifecycleWebhookReplayPolicy(
                    now=lambda: datetime(2026, 3, 28, 15, 0, 0, tzinfo=timezone.utc),
                ),
            ),
            "replay_rejected",
        ),
    ]
    for result, code in cases:
        assert result.body == _fixture_bytes(code), code


def test_fr5_fixture_dir_covers_all_stable_error_codes() -> None:
    """Every ``*.json`` in the fixture dir is listed in the handler/spec stable set."""
    expected_codes = {
        "method_not_allowed",
        "signature_required",
        "signature_malformed",
        "signature_mismatch",
        "invalid_json",
        "invalid_payload_shape",
        "unknown_event_type",
        "replay_rejected",
    }
    json_files = {p.stem for p in _FIXTURE_DIR.glob("*.json")}
    assert json_files == expected_codes
