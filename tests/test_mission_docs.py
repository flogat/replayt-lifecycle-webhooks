"""Backlog acceptance: MISSION, ecosystem idea, and README positioning (no network)."""

from __future__ import annotations

import pathlib
import re


def _repo_root() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parents[1]


def _read(rel: str) -> str:
    return (_repo_root() / rel).read_text(encoding="utf-8")


def test_mission_has_ecosystem_positioning_and_core_gap_named_once() -> None:
    """Primary pattern token appears in MISSION only under ecosystem positioning (named once in doc body)."""
    text = _read("docs/MISSION.md")
    assert "## Ecosystem positioning" in text
    assert "**Primary pattern:** **Core-gap**" in text
    assert text.count("Core-gap") == 1


def test_mission_links_readme_and_design_principles() -> None:
    """Integrator links use correct relative paths from docs/."""
    text = _read("docs/MISSION.md")
    assert "[DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)" in text
    assert "[README.md](../README.md)" in text


def test_mission_success_covers_tests_and_releases() -> None:
    """Success metrics mention CI/pytest and SemVer / release mechanics."""
    text = _read("docs/MISSION.md")
    assert "## Success metrics (v0.x)" in text
    assert "pytest" in text
    assert "Semantic Versioning" in text
    assert "pyproject.toml" in text


def test_mission_has_no_ecosystem_draft_placeholder() -> None:
    """Filled mission: no taxonomy choice stub left in MISSION."""
    text = _read("docs/MISSION.md")
    assert "_(1–4" not in text
    assert "**Primary pattern:** _" not in text


def test_replayt_ecosystem_idea_your_choice_is_filled() -> None:
    """REPLAYT_ECOSYSTEM_IDEA 'Your choice' records Core-gap, pitch, and release tracking."""
    text = _read("docs/REPLAYT_ECOSYSTEM_IDEA.md")
    assert "## Your choice" in text
    assert "**Primary pattern:** **Core-gap**" in text
    assert "[MISSION.md](MISSION.md)" in text
    assert "_(1–4 or short name)_" not in text
    assert "**Replayt release tracking" in text
    assert "SPEC_REPLAYT_BOUNDARY_TESTS.md" in text
    assert "CHANGELOG.md" in text


def test_readme_overview_cross_links_ecosystem_idea_and_core_gap() -> None:
    """README Overview names Core-gap and links REPLAYT_ECOSYSTEM_IDEA before MISSION."""
    text = _read("README.md")
    assert "docs/MISSION.md" in text
    assert "docs/REPLAYT_ECOSYSTEM_IDEA.md" in text
    overview, _, _ = text.partition("## Design principles")
    assert "## Overview" in overview
    assert "docs/REPLAYT_ECOSYSTEM_IDEA.md" in overview
    assert re.search(r"core[- ]?gap", overview, re.IGNORECASE)
    assert "Primary ecosystem pattern" in overview
