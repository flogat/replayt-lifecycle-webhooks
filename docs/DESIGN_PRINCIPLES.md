# Design principles

Revise as the project matures. Defaults below are minimal—expand with rules for **your** codebase.

1. **Explicit contracts** — Document supported **replayt** (and third-party framework) versions; test integration boundaries. The **replayt** lower bound, optional upper bound, **compatibility matrix** (**replayt** ↔ this package), README compatibility text, and checklist live in **[SPEC_REPLAYT_DEPENDENCY.md](SPEC_REPLAYT_DEPENDENCY.md)**. Webhook signing and verification expectations live in **[SPEC_WEBHOOK_SIGNATURE.md](SPEC_WEBHOOK_SIGNATURE.md)**. Recommended **run** / **approval** JSON field shapes live in **[EVENTS.md](EVENTS.md)**; **typed** parsing and Pydantic models for those payloads live in **`replayt_lifecycle_webhooks.events`**, as specified in **EVENTS.md** (including **schema_version** and migration notes).
2. **Small public surfaces** — Prefer narrow APIs and documented extension points.
3. **Observable automation** — Local scripts and CI produce clear logs and exit codes.
4. **Consumer-side maintenance** — Compatibility shims and pins live **here**; upstream changes are tracked with tests
   and changelog notes.
5. **Not a lever on core** — This repo does not exist to steer replayt core; propose upstream changes through normal
   channels.

## LLM / demos (if applicable)

Document models, secrets handling, cost and redaction expectations here or in MISSION.

## Audience (extend)

| Audience | Needs |
| -------- | ----- |
| **Maintainers** | Mission, scripts, pinned versions, release notes |
| **Integrators** | Stable adapter surface, compatibility matrix |
| **Contributors** | README, tests, coding expectations |
