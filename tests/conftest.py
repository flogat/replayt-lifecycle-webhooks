"""Pytest hooks for this package's test suite.

Backlog `1b3df584` (PG1): ``perf_hotpath`` timing tests are opt-in so
``pytest tests -q`` and merge-blocking CI stay free of wall-clock flakes.
"""

from __future__ import annotations

import os


def _perf_hotpath_opted_in(config) -> bool:
    if os.environ.get("RUN_PERF_HOTPATH") == "1":
        return True
    markexpr = (getattr(config.option, "markexpr", None) or "").strip()
    if not markexpr:
        return False
    compact = markexpr.replace(" ", "")
    if "notperf_hotpath" in compact:
        return False
    return "perf_hotpath" in markexpr


def pytest_collection_modifyitems(config, items):  # type: ignore[no-untyped-def]
    if _perf_hotpath_opted_in(config):
        return
    items[:] = [i for i in items if not i.get_closest_marker("perf_hotpath")]
