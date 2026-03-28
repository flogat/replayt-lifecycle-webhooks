# Signed HTTP webhooks for replayt run and approval lifecycle events

## Overview

This project builds on **[replayt](https://pypi.org/project/replayt/)**. It declares a runtime dependency on
**replayt `>=0.4.25`** (see `pyproject.toml`). Formal contract, bump policy, and acceptance criteria:
**[docs/SPEC_REPLAYT_DEPENDENCY.md](docs/SPEC_REPLAYT_DEPENDENCY.md)**. Webhook signature verification contract and
acceptance checklist: **[docs/SPEC_WEBHOOK_SIGNATURE.md](docs/SPEC_WEBHOOK_SIGNATURE.md)**. Read
**[docs/REPLAYT_ECOSYSTEM_IDEA.md](docs/REPLAYT_ECOSYSTEM_IDEA.md)** for positioning prompts, then
**[docs/MISSION.md](docs/MISSION.md)** for scope and goals.

**Compatibility:** After `pip install -e .` (or `pip install -e ".[dev]"` when you work in this repo), check the installed **replayt** with either:

```bash
pip show replayt
```

or:

```bash
python -c "import importlib.metadata as m; print(m.version('replayt'))"
```

**Upstream changes:** PyPI lists versions under [Release history](https://pypi.org/project/replayt/#history) on the
[replayt project page](https://pypi.org/project/replayt/). This package does not mirror upstream release notes; use
that history (and upstream’s own changelog or GitHub Releases when you need prose per release).

**Report breakage:** Open an issue on [GitHub Issues](https://github.com/flogat/replayt-lifecycle-webhooks/issues).

## Design principles

**[docs/DESIGN_PRINCIPLES.md](docs/DESIGN_PRINCIPLES.md)** covers **replayt** compatibility, versioning, and (for showcases)
**LLM** boundaries.


## Reference documentation (optional)

[`docs/reference-documentation/`](docs/reference-documentation/) holds short excerpts or consumer contracts when
upstream prose is not in this tree. See
[`REPLAYT_WEBHOOK_SIGNING.md`](docs/reference-documentation/REPLAYT_WEBHOOK_SIGNING.md) for the HMAC header and body
rules this package implements.

## Quick start

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
pip install -e ".[dev]"
```

## Verifying webhook signatures

Verify the **raw request body** with your shared secret and the **`Replayt-Signature`** header before parsing JSON or
running automation. Ordered steps for handlers:
**[Verification procedure](docs/SPEC_WEBHOOK_SIGNATURE.md#verification-procedure-integrators)** in
**[docs/SPEC_WEBHOOK_SIGNATURE.md](docs/SPEC_WEBHOOK_SIGNATURE.md)**. Full contract detail also in
**[docs/reference-documentation/REPLAYT_WEBHOOK_SIGNING.md](docs/reference-documentation/REPLAYT_WEBHOOK_SIGNING.md)**.

```python
from replayt_lifecycle_webhooks import (
    LIFECYCLE_WEBHOOK_SIGNATURE_HEADER,
    verify_lifecycle_webhook_signature,
)

# raw_body: bytes exactly as received from the HTTP layer
# header_value: request header LIFECYCLE_WEBHOOK_SIGNATURE_HEADER (e.g. "sha256=<hex>")
verify_lifecycle_webhook_signature(
    secret=your_secret,
    body=raw_body,
    signature=header_value,
)
```

## Optional agent workflows

This repo may include a [`.cursor/skills/`](.cursor/skills/) directory for Cursor-style agent skills. **`.gitignore`**
lists **`path/`** (so documentation-style placeholder paths are never committed), **`.cursor/skills/`**, and related
local tooling entries. Adapt or remove optional directories to match your team’s workflow.

## Project layout

| Path | Purpose |
| ---- | ------- |
| `docs/REPLAYT_ECOSYSTEM_IDEA.md` | Positioning (core-gap / showcase / bridge / combinator prompts) |
| `docs/MISSION.md` | Mission and scope |
| `docs/DESIGN_PRINCIPLES.md` | Design and integration principles |
| `docs/SPEC_REPLAYT_DEPENDENCY.md` | **replayt** pin: contract, checklist, CI expectations |
| `docs/SPEC_WEBHOOK_SIGNATURE.md` | Incoming webhook signature verification: API contract, tests, upstream alignment |
| `docs/reference-documentation/` | Optional markdown snapshot for contributors (e.g. `REPLAYT_WEBHOOK_SIGNING.md`) |
| `src/replayt_lifecycle_webhooks/` | Python package (import `replayt_lifecycle_webhooks`) |
| `pyproject.toml` | Package metadata |
| `CHANGELOG.md` | Release notes (Keep a Changelog); keep **Unreleased** updated |
| `.gitignore` | Ignores `path/` (doc placeholders), `.orchestrator/`, `.cursor/skills/`, and `AGENTS.md` (local tooling) |
