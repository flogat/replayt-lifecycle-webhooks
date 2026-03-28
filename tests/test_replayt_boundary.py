"""Replayt Python seam: EVENTS.md-listed symbols stay importable (SPEC_REPLAYT_BOUNDARY_TESTS R1)."""

from __future__ import annotations

import pytest
import replayt
from replayt import ApprovalPending, RunFailed, RunResult


@pytest.mark.replayt_boundary
def test_replayt_exports_events_md_symbols() -> None:
    """RunResult, RunFailed, ApprovalPending must remain public on the installed replayt (EVENTS.md)."""
    assert getattr(replayt, "RunResult") is RunResult
    assert getattr(replayt, "RunFailed") is RunFailed
    assert getattr(replayt, "ApprovalPending") is ApprovalPending
