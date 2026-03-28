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

This checkout does not yet include [`docs/reference-documentation/`](docs/reference-documentation/). You can add markdown
copies of upstream replayt documentation there for offline review or agent context.

## Quick start

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
pip install -e ".[dev]"
```

## Verifying webhook signatures (planned API)

Operators should verify the **raw request body** with the shared secret and the **signature headers replayt sends**
before parsing JSON or running automation. Exact header names and MAC details are defined in
**[docs/SPEC_WEBHOOK_SIGNATURE.md](docs/SPEC_WEBHOOK_SIGNATURE.md)**; the Builder phase will add the public helper and
unit tests. Intended usage (illustrative—names may differ once implemented):

```python
from replayt_lifecycle_webhooks import verify_lifecycle_webhook_signature  # name TBD

# raw_body: bytes exactly as received from the HTTP layer
# headers: signature (and any other required) values from the incoming request
verify_lifecycle_webhook_signature(secret=..., body=raw_body, signature=..., ...)
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
| `docs/reference-documentation/` | Optional markdown snapshot for contributors (when present) |
| `src/replayt_lifecycle_webhooks/` | Python package (import `replayt_lifecycle_webhooks`) |
| `pyproject.toml` | Package metadata |
| `CHANGELOG.md` | Release notes (Keep a Changelog); keep **Unreleased** updated |
| `.gitignore` | Ignores `path/` (doc placeholders), `.orchestrator/`, `.cursor/skills/`, and `AGENTS.md` (local tooling) |
