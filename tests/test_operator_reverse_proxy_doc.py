"""SPEC_REVERSE_PROXY_REFERENCE_SERVER / SPEC_AUTOMATED_TESTS backlog dc212184 OG1–OG8."""

from __future__ import annotations

import pathlib
import re


def _repo_root() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parents[1]


def _operator_guide_text() -> str:
    return (_repo_root() / "docs" / "OPERATOR_REVERSE_PROXY.md").read_text(
        encoding="utf-8"
    )


def _readme_text() -> str:
    return (_repo_root() / "README.md").read_text(encoding="utf-8")


def _h2_section(text: str, title: str) -> str:
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


def _first_h1(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("# ") and not line.startswith("##"):
            return line
    return ""


def _nginx_fence_inner(text: str) -> str:
    m = re.search(r"```nginx\n(.*?)```", text, flags=re.DOTALL)
    return m.group(1) if m else ""


def test_og1_guide_exists_h1_reverse_proxy_tls_and_reference_command() -> None:
    guide = _operator_guide_text()
    h1 = _first_h1(guide).lower()
    assert "reverse proxy" in h1
    assert "tls" in h1
    assert "python -m replayt_lifecycle_webhooks" in h1


def test_og2_links_signature_spec_and_raw_body_discipline() -> None:
    guide = _operator_guide_text()
    assert "docs/SPEC_WEBHOOK_SIGNATURE.md" in guide
    assert "raw" in guide.lower() and "body" in guide.lower()


def test_og3_client_max_body_size_and_rationale() -> None:
    guide = _operator_guide_text()
    assert "client_max_body_size" in guide
    assert "413" in guide
    assert "truncat" in guide.lower()
    assert "signature" in guide.lower()


def test_og4_timeouts_and_delivery_idempotency_link() -> None:
    guide = _operator_guide_text()
    assert "timeout" in guide.lower()
    assert "docs/SPEC_DELIVERY_IDEMPOTENCY.md" in guide


def test_og5_transfer_encoding_chunked_byte_identical() -> None:
    guide = _operator_guide_text()
    assert "Transfer-Encoding" in guide or "transfer-encoding" in guide.lower()
    assert "chunked" in guide.lower()
    assert "byte-identical" in guide


def test_og6_nginx_fence_comment_points_at_signature_spec() -> None:
    guide = _operator_guide_text()
    inner = _nginx_fence_inner(guide)
    assert inner.strip() != ""
    assert "#" in inner
    assert (
        "docs/SPEC_WEBHOOK_SIGNATURE.md" in inner or "SPEC_WEBHOOK_SIGNATURE" in inner
    )


def test_og7_logging_callout_and_redaction_spec_link() -> None:
    guide = _operator_guide_text()
    assert "## Logging and secrets" in guide
    assert "full POST bodies" in guide or "full post bodies" in guide.lower()
    assert "shared webhook secret" in guide
    assert "Replayt-Signature" in guide
    assert "docs/SPEC_STRUCTURED_LOGGING_REDACTION.md" in guide


def test_og8_readme_links_operator_guide_under_troubleshooting_or_verifying() -> None:
    readme = _readme_text()
    needle = "docs/OPERATOR_REVERSE_PROXY.md"
    ts = _h2_section(readme, "Troubleshooting")
    vw = _h2_section(readme, "Verifying webhook signatures")
    assert needle in ts or needle in vw
