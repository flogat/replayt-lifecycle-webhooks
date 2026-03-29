# Design principles

Revise as the project matures. Defaults below are minimal—expand with rules for **your** codebase.

1. **Explicit contracts** — Document supported **replayt** (and third-party framework) versions; test integration boundaries. The **replayt** lower bound, optional upper bound, **compatibility matrix** (package line ↔ **replayt** range, **`requires-python`**, **CI-tested** interpreter), README compatibility text, and checklist live in **[SPEC_REPLAYT_DEPENDENCY.md](SPEC_REPLAYT_DEPENDENCY.md)**. **Python API stability** at the **`replayt` import seam** (documented symbols vs installed **replayt**) lives in **[SPEC_REPLAYT_BOUNDARY_TESTS.md](SPEC_REPLAYT_BOUNDARY_TESTS.md)**. **This package’s supported import surface** (`__all__` at the package root, documented **`replayt_lifecycle_webhooks.events`** submodule, internal module paths, **`-m`** entrypoints, deprecation notice period, **pre-1.0** rules): **[SPEC_PUBLIC_API.md](SPEC_PUBLIC_API.md)**. Webhook signing and verification expectations live in **[SPEC_WEBHOOK_SIGNATURE.md](SPEC_WEBHOOK_SIGNATURE.md)**. **Delivery semantics**, **`event_id`** dedupe rules, at-least-once expectations, and consumer idempotency store TTL guidance: **[SPEC_DELIVERY_IDEMPOTENCY.md](SPEC_DELIVERY_IDEMPOTENCY.md)**. **Replay protection** (freshness on **`occurred_at`**, clock skew defaults, optional **`Replayt-*`** wire headers, **`LifecycleWebhookDedupStore`** protocol, in-memory reference store, **RP4**/**RP5** tests when implemented): **[SPEC_REPLAY_PROTECTION.md](SPEC_REPLAY_PROTECTION.md)**. **HTTP error categories**, stable JSON **`error`** codes, and logging boundaries for operators live in **[SPEC_WEBHOOK_FAILURE_RESPONSES.md](SPEC_WEBHOOK_FAILURE_RESPONSES.md)**. **Structured logging** with **default redaction** for sensitive headers and metadata dict keys (stdlib **`logging`**, extension points, **L1–L9** tests when implemented; optional **serve** / **handler** diagnostics and **LG1–LG4** when implemented, backlog **`0bab43f3`**, **§ Optional diagnostic logging**): **[SPEC_STRUCTURED_LOGGING_REDACTION.md](SPEC_STRUCTURED_LOGGING_REDACTION.md)**. Optional **reference HTTP server** (**`python -m` / CLI**, **POST** route, **`GET /health`**, optional-deps posture): **[SPEC_HTTP_SERVER_ENTRYPOINT.md](SPEC_HTTP_SERVER_ENTRYPOINT.md)**; gateway **HTTP surface** matrix (**RM1**–**RM7**): **[SPEC_REFERENCE_HTTP_SERVER_ROUTE_MAP.md](SPEC_REFERENCE_HTTP_SERVER_ROUTE_MAP.md)**. **Reverse proxy / TLS** in front of that server (preserve raw body, limits, timeouts, **`Transfer-Encoding`** pitfalls; **OG1**–**OG8**): **[SPEC_REVERSE_PROXY_REFERENCE_SERVER.md](SPEC_REVERSE_PROXY_REFERENCE_SERVER.md)**. Optional **local demo POST** (signed **dev** fixtures, one documented **`python -m`** command, defaults aligned with the reference server): **[SPEC_LOCAL_WEBHOOK_DEMO.md](SPEC_LOCAL_WEBHOOK_DEMO.md)**. Recommended **run** / **approval** JSON field shapes live in **[EVENTS.md](EVENTS.md)**; **typed** parsing and Pydantic models for those payloads live in **`replayt_lifecycle_webhooks.events`**, as specified in **EVENTS.md** (including **schema_version** and migration notes). **PM/support event digests** after parse (**DG0**–**DG6**, **`lifecycle_event_to_digest_text`** / **`lifecycle_event_to_digest_record`**): **[SPEC_EVENT_DIGEST.md](SPEC_EVENT_DIGEST.md)**. **README** operator-facing sections (**Troubleshooting**, **Approval webhook flow**, **Verifying webhook signatures**; **pytest** **OP1**–**OP8**): **[SPEC_README_OPERATOR_SECTIONS.md](SPEC_README_OPERATOR_SECTIONS.md)**. **Optional reference-documentation** snapshots under **`docs/reference-documentation/`** (committed excerpts vs gitignored **`_upstream_snapshot/`**, **CI** hygiene, licensing, documented snapshot commands, **RD1**–**RD8**): **[SPEC_REFERENCE_DOCUMENTATION.md](SPEC_REFERENCE_DOCUMENTATION.md)**.
2. **Small public surfaces** — Prefer narrow APIs and documented extension points.
3. **Observable automation** — Local scripts and CI produce clear logs and exit codes. The **pytest** suite and CI
   command are normative for regressions on public contracts; see **[SPEC_AUTOMATED_TESTS.md](SPEC_AUTOMATED_TESTS.md)**
   (no smoke-only **`assert True`** as substitute for verification / parsing coverage; **ruff** lint/format CI rows
   **RF1**–**RF5** under backlog **`5a3f5a7f`**; optional local **pre-commit** mirroring those **ruff** invocations
   **PC1**–**PC7** under backlog **`c39b2a5f`**; **sdist**/**wheel** **`python -m build`** + **`twine check`**, declared
   **package-data**, and conditional **`py.typed`** under backlog **`78e3554b`**, **PK1**–**PK7**; optional **Hypothesis**
   **`property_fuzz`** rows **PF1**–**PF10** under backlog **`dcffe5d5`**; **`pip-audit`** suppression alignment **PI1**–**PI7**
   under backlog **`bea2900c`** in **[SPEC_PIP_AUDIT_SUPPRESSION_ALIGNMENT.md](SPEC_PIP_AUDIT_SUPPRESSION_ALIGNMENT.md)**). **Webhook request logging**
   convention: **structured** **`logging`** with **`snake_case`** **`extra=`** keys (**`webhook_*`**, **`lifecycle_*`**),
   package **`redact_*`** helpers, and **no default raw POST body** in log records—see
   **[SPEC_STRUCTURED_LOGGING_REDACTION.md](SPEC_STRUCTURED_LOGGING_REDACTION.md)** (**§ Recommended structured field names**,
   **§ Example: successful verified delivery**, **L1–L9**, **LG1–LG4** for optional **serve** / **handler** diagnostics).
   Redact **`Authorization`** / **`Replayt-Signature`** (and
   related defaults); length-only **`webhook_body_bytes_len`** is allowed.
4. **Consumer-side maintenance** — Compatibility shims and pins live **here**; upstream changes are tracked with tests
   and changelog notes.
5. **Not a lever on core** — This repo does not exist to steer replayt core; propose upstream changes through normal
   channels.

## Semantic versioning and deprecation

Published releases follow **[Semantic Versioning](https://semver.org/spec/v2.0.0.html)**. **User-visible** API, CLI, and dependency contract changes belong in **`CHANGELOG.md`** (Keep a Changelog: **Added**, **Changed**, **Deprecated**, **Removed**, and so on). **Supported imports**, **documented `python -m` entrypoints**, the **minimum deprecation window** (at least **one** subsequent **0.x minor** after the release that announces a deprecation), and **pre-1.0** stability expectations are normative in **[SPEC_PUBLIC_API.md](SPEC_PUBLIC_API.md)**—keep that spec, package **`__all__`**, and **CHANGELOG** aligned when the export surface changes.

## LLM / demos (if applicable)

Document models, secrets handling, cost and redaction expectations here or in MISSION. **Outputs must not** include raw
webhook bodies, **HMAC** secrets, or full **`Replayt-Signature`** lines; treat **SPEC_WEBHOOK_FAILURE_RESPONSES** and
**SPEC_STRUCTURED_LOGGING_REDACTION** as the **minimum** redaction bar for anything that looks like production logs or
support dumps.

## Audience (extend)

| Audience | Needs |
| -------- | ----- |
| **Maintainers** | Mission, scripts, pinned versions, release notes |
| **Integrators** | Stable adapter surface, compatibility matrix |
| **Contributors** | README, tests, coding expectations |
