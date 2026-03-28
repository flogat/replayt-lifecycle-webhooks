"""SPEC_README_OPERATOR_SECTIONS / SPEC_AUTOMATED_TESTS backlog 23e2da29 OP1–OP8."""

from __future__ import annotations

import pathlib


def _repo_root() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parents[1]


def _readme_text() -> str:
    return (_repo_root() / "README.md").read_text(encoding="utf-8")


def _h2_section(text: str, title: str) -> str:
    """Return lines under ``## {title}`` until the next level-2 ``## `` heading."""
    lines = text.splitlines()
    heading = f"## {title}"
    start: int | None = None
    for i, line in enumerate(lines):
        if line == heading:
            start = i + 1
            break
    if start is None:
        return ""
    out: list[str] = []
    for line in lines[start:]:
        if line.startswith("## ") and not line.startswith("###"):
            break
        out.append(line)
    return "\n".join(out)


def test_op1_troubleshooting_heading_exact_line() -> None:
    assert any(line == "## Troubleshooting" for line in _readme_text().splitlines())


def test_op2_approval_webhook_flow_heading_exact_line() -> None:
    assert any(
        line == "## Approval webhook flow" for line in _readme_text().splitlines()
    )


def test_op3_verifying_webhook_signatures_heading_exact_line() -> None:
    assert any(
        line == "## Verifying webhook signatures"
        for line in _readme_text().splitlines()
    )


def test_op4_troubleshooting_links_webhook_failure_responses() -> None:
    body = _h2_section(_readme_text(), "Troubleshooting")
    assert "docs/SPEC_WEBHOOK_FAILURE_RESPONSES.md" in body


def test_op5_approval_mentions_both_approval_event_types() -> None:
    body = _h2_section(_readme_text(), "Approval webhook flow")
    assert "replayt.lifecycle.approval.pending" in body
    assert "replayt.lifecycle.approval.resolved" in body


def test_op6_approval_links_events_md() -> None:
    body = _h2_section(_readme_text(), "Approval webhook flow")
    assert "docs/EVENTS.md" in body


def test_op7_verifying_links_signature_spec_verification_procedure() -> None:
    body = _h2_section(_readme_text(), "Verifying webhook signatures")
    assert "docs/SPEC_WEBHOOK_SIGNATURE.md" in body
    assert "#verification-procedure-integrators" in body


def test_op8_verifying_mentions_signature_check_path() -> None:
    body = _h2_section(_readme_text(), "Verifying webhook signatures")
    assert (
        "verify_lifecycle_webhook_signature" in body
        or "replayt_lifecycle_webhooks.demo_webhook" in body
        or "python -m replayt_lifecycle_webhooks.demo_webhook" in body
    )
