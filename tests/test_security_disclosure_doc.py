"""SPEC_SECURITY_DISCLOSURE / SPEC_AUTOMATED_TESTS backlog 87e7edae SEC1–SEC9."""

from __future__ import annotations

import pathlib


def _repo_root() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parents[1]


def _security_text() -> str:
    return (_repo_root() / "SECURITY.md").read_text(encoding="utf-8")


def _readme_text() -> str:
    return (_repo_root() / "README.md").read_text(encoding="utf-8")


def _contributing_text() -> str:
    return (_repo_root() / "CONTRIBUTING.md").read_text(encoding="utf-8")


def test_sec1_security_md_exists_next_to_readme() -> None:
    root = _repo_root()
    assert (root / "SECURITY.md").is_file()
    assert (root / "README.md").is_file()
    assert (root / "SECURITY.md").resolve() == (
        root / "README.md"
    ).parent / "SECURITY.md"


def test_sec2_security_has_level1_heading_with_security() -> None:
    for line in _security_text().splitlines():
        if line.startswith("# "):
            assert "security" in line.lower()
            return
    raise AssertionError("no level-1 heading in SECURITY.md")


def test_sec3_security_has_in_scope_h2() -> None:
    assert any(
        line.startswith("## ") and "in scope" in line.lower()
        for line in _security_text().splitlines()
    )


def test_sec4_security_has_out_of_scope_h2_and_mentions_replayt() -> None:
    lines = _security_text().splitlines()
    assert any(
        line.startswith("## ") and "out of scope" in line.lower() for line in lines
    )
    assert "replayt" in _security_text().lower()


def test_sec5_security_response_expectations_prose() -> None:
    t = _security_text().lower()
    assert "acknowledg" in t or "business day" in t or "72" in t, (
        "expected acknowledgement / business-day / 72h style prose per SC6"
    )


def test_sec6_security_reporting_channel() -> None:
    t = _security_text().lower()
    assert "mailto:" in t or ("github" in t and "security" in t)


def test_sec7_security_links_normative_doc_paths() -> None:
    s = _security_text()
    assert (
        "docs/SPEC_WEBHOOK_SIGNATURE.md" in s
        or "docs/SPEC_STRUCTURED_LOGGING_REDACTION.md" in s
        or "docs/DESIGN_PRINCIPLES.md" in s
    )


def test_sec8_readme_links_security_md() -> None:
    r = _readme_text()
    assert "](SECURITY.md)" in r or "](./SECURITY.md)" in r


def test_sec9_contributing_links_spec_and_names_security_policy() -> None:
    c = _contributing_text()
    assert "](docs/SPEC_SECURITY_DISCLOSURE.md)" in c
    assert "SECURITY.md" in c
