"""SPEC_REFERENCE_HTTP_SERVER_ROUTE_MAP — pytest doc guards (backlog ``b4c68e50``, RM1–RM4)."""

from __future__ import annotations

import pathlib

from replayt_lifecycle_webhooks.serve import (
    DEFAULT_HOST,
    DEFAULT_PORT,
    DEFAULT_WEBHOOK_PATH,
    HEALTH_PATH,
)


def _repo_root() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parents[1]


def _route_map_text() -> str:
    path = _repo_root() / "docs" / "SPEC_REFERENCE_HTTP_SERVER_ROUTE_MAP.md"
    assert path.is_file(), "docs/SPEC_REFERENCE_HTTP_SERVER_ROUTE_MAP.md must exist"
    return path.read_text(encoding="utf-8")


def test_rm1_canonical_table_includes_webhook_post_and_health_get() -> None:
    """RM1: canonical table documents POST /webhook and GET /health."""
    text = _route_map_text()
    assert "## Canonical route / status table" in text
    assert "**`/webhook`**" in text
    assert "**POST**" in text
    assert "**`/health`**" in text
    assert "**GET**" in text


def test_rm2_defaults_match_shipped_serve_constants() -> None:
    """RM2: defaults section documents the same host, port, and path as ``serve``."""
    text = _route_map_text()
    assert DEFAULT_HOST in text
    assert str(DEFAULT_PORT) in text
    assert DEFAULT_WEBHOOK_PATH in text
    assert HEALTH_PATH in text


def test_rm3_canonical_table_links_failure_responses_and_signature_specs() -> None:
    """RM3: matrix points at SPEC_WEBHOOK_FAILURE_RESPONSES and SPEC_WEBHOOK_SIGNATURE."""
    text = _route_map_text()
    assert "SPEC_WEBHOOK_FAILURE_RESPONSES.md" in text
    assert "SPEC_WEBHOOK_SIGNATURE.md" in text


def test_rm4_readme_links_route_map_spec() -> None:
    """RM4: README includes the repo-relative path to the route map spec."""
    readme = (_repo_root() / "README.md").read_text(encoding="utf-8")
    assert "docs/SPEC_REFERENCE_HTTP_SERVER_ROUTE_MAP.md" in readme
