"""Replayt Python seam: EVENTS.md symbols and __all__ guardrails (SPEC_REPLAYT_BOUNDARY_TESTS R1, G1–G7)."""

from __future__ import annotations

import pytest
import replayt
from replayt import ApprovalPending, RunFailed, RunResult

# Normative maintainer hint (SPEC_REPLAYT_BOUNDARY_TESTS § Failure messages): primary links + boundary spec.
_REPLAYT_BOUNDARY_ACTION = (
    "replayt boundary mismatch: update EVENTS.md and docs/SPEC_REPLAYT_BOUNDARY_TESTS.md expectations, "
    "then follow bump policy in docs/SPEC_REPLAYT_DEPENDENCY.md and record user-visible changes in CHANGELOG.md."
)

_REQUIRED_EVENTS_MD_NAMES = frozenset({"RunResult", "RunFailed", "ApprovalPending"})


@pytest.mark.replayt_boundary
def test_replayt_exports_events_md_symbols() -> None:
    """RunResult, RunFailed, ApprovalPending must remain public on the installed replayt (EVENTS.md)."""
    assert getattr(replayt, "RunResult") is RunResult, _REPLAYT_BOUNDARY_ACTION
    assert getattr(replayt, "RunFailed") is RunFailed, _REPLAYT_BOUNDARY_ACTION
    assert getattr(replayt, "ApprovalPending") is ApprovalPending, (
        _REPLAYT_BOUNDARY_ACTION
    )


@pytest.mark.replayt_boundary
def test_replayt_all_superset_of_required_symbols() -> None:
    """Required public names must stay listed in replayt.__all__; upstream may add names (superset semantics)."""
    names = set(getattr(replayt, "__all__", ()))
    missing = sorted(_REQUIRED_EVENTS_MD_NAMES - names)
    assert not missing, (
        f"{_REPLAYT_BOUNDARY_ACTION} "
        f"Required names missing from replayt.__all__ (expected superset of {_REQUIRED_EVENTS_MD_NAMES!r}): {missing!r}."
    )
