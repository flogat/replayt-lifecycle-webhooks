"""SPEC_INTEGRATOR_ASGI_VERIFIED_FIRST — pytest doc guards (backlog ``c631fe3f``, AF1–AF5)."""

from __future__ import annotations

import pathlib


def _repo_root() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parents[1]


def _integrator_spec_text() -> str:
    path = _repo_root() / "docs" / "SPEC_INTEGRATOR_ASGI_VERIFIED_FIRST.md"
    assert path.is_file(), "docs/SPEC_INTEGRATOR_ASGI_VERIFIED_FIRST.md must exist"
    return path.read_text(encoding="utf-8")


def _copy_paste_section(text: str) -> str:
    start = "## Copy-paste examples (normative shape)"
    end = "## Acceptance checklist (AF1–AF7)"
    i = text.index(start) + len(start)
    j = text.index(end, i)
    return text[i:j]


def test_af1_copy_paste_section_not_placeholder() -> None:
    """AF1: copy-paste section has concrete framework examples, not the phase-2 placeholder."""
    section = _copy_paste_section(_integrator_spec_text())
    assert "Until Builder phase" not in section
    assert "await request.body()" in section
    assert "from fastapi import" in section
    assert "starlette.applications" in section


def test_af2_verify_before_json_named() -> None:
    """AF2: raw bytes before parse; anti-pattern named."""
    section = _copy_paste_section(_integrator_spec_text())
    assert "await request.json()" in section or "request.json()" in section
    assert "json.loads" in section


def test_af3_public_import_paths_only_in_examples() -> None:
    """AF3: examples avoid deep/internal imports from this package."""
    section = _copy_paste_section(_integrator_spec_text())
    assert "from replayt_lifecycle_webhooks import" in section
    assert "replayt_lifecycle_webhooks.signature" not in section
    assert "replayt_lifecycle_webhooks.handler" not in section


def test_af4_status_mapping_without_leakage_hints() -> None:
    """AF4: 401/403 mapping with stable JSON error codes (no MAC/secret in response bodies)."""
    section = _copy_paste_section(_integrator_spec_text())
    assert "401" in section
    assert "403" in section
    assert "signature_mismatch" in section
    assert "signature_required" in section
    assert "do not echo secrets" in section.lower() or "do not echo" in section.lower()


def test_af5_links_signature_and_failure_specs_in_copy_paste_scope() -> None:
    """AF5: prose in copy-paste scope links SPEC_WEBHOOK_SIGNATURE and SPEC_WEBHOOK_FAILURE_RESPONSES."""
    section = _copy_paste_section(_integrator_spec_text())
    assert "SPEC_WEBHOOK_SIGNATURE.md" in section
    assert "SPEC_WEBHOOK_FAILURE_RESPONSES.md" in section
