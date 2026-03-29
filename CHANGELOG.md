# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Tests

- **Subprocess reference server** (backlog **`83e07114`**, phase **3**): **`tests/test_reference_server_subprocess.py`**
  starts **`sys.executable -m replayt_lifecycle_webhooks`** on **`127.0.0.1`** with a parent-chosen free port and
  **`REPLAYT_LIFECYCLE_WEBHOOK_SECRET`** in the child environment, waits for **`GET /health`**, **POST**s
  **`tests/fixtures/events/run_started.json`** with **`compute_lifecycle_webhook_signature_header`**, and expects **204**.

### Documentation

- **Subprocess reference-server test contract** (backlog **`83e07114`**): **`docs/SPEC_AUTOMATED_TESTS.md`** adds **SUB1**–**SUB8**,
  **§ Minimum behavioral coverage** note, CI entrypoint allowance for **loopback** child HTTP, and topic-table traceability;
  **`docs/SPEC_HTTP_SERVER_ENTRYPOINT.md`** adds **S9** and links **SUB** rows to **`tests/test_reference_server_subprocess.py`**.

- **Reverse proxy operator guide** (phase **3**, backlog **`dc212184-8c0d-4ee6-90de-e0d50c370f6f`** /
  *Operator guide: reverse proxy in front of reference WSGI server*): new **`docs/OPERATOR_REVERSE_PROXY.md`** (raw POST body,
  **`client_max_body_size`** / limits, timeouts, **`Transfer-Encoding`** / buffering, **nginx** example with **SPEC_WEBHOOK_SIGNATURE**
  comment, logging callout). **`README.md`** **Troubleshooting** links the guide. **`docs/SPEC_HTTP_SERVER_ENTRYPOINT.md`**
  points at the shipped guide without a future-tense backlog clause. **`tests/test_operator_reverse_proxy_doc.py`**
  enforces **OG1**–**OG8**.

- **Reverse proxy docs** (phase **5** architecture review, same backlog): **`docs/MISSION.md`**, **`docs/SPEC_AUTOMATED_TESTS.md`**, **`README.md`**
  project layout, and **`docs/SPEC_REVERSE_PROXY_REFERENCE_SERVER.md`** now describe the shipped guide without “when shipped” /
  **Builder**-pending wording.

- **Reverse proxy in front of the reference HTTP server** (phase **2** spec, backlog **`dc212184-8c0d-4ee6-90de-e0d50c370f6f`** /
  *Operator guide: reverse proxy in front of reference WSGI server*): new **`docs/SPEC_REVERSE_PROXY_REFERENCE_SERVER.md`**
  (normative contract for the operator guide and **OG1**–**OG8**). Cross-links and traceability in
  **`docs/SPEC_HTTP_SERVER_ENTRYPOINT.md`**, **`docs/SPEC_README_OPERATOR_SECTIONS.md`** (README link rule),
  **`docs/SPEC_AUTOMATED_TESTS.md`**, **`docs/MISSION.md`**, **`docs/DESIGN_PRINCIPLES.md`**, and **`README.md`** project layout /
  overview.

- **Optional reference-documentation workflow** (backlog **`eb884da9`**, refinement **`2db687f4`**): new **`CONTRIBUTING.md`**
  entry; **`README.md`** and **`docs/reference-documentation/README.md`** describe when to refresh, small default clones, and
  gitignored **`_upstream_snapshot/`**. **`docs/SPEC_REFERENCE_DOCUMENTATION.md`** adds acceptance mapping, committed-path
  exclusivity (no alternate vendor roots), licensing rules, repeatable **`git`** / **`curl`** / **`rsync`** examples, and the
  optional **`scripts/`** helper contract. **`docs/reference-documentation/REPLAYT_WEBHOOK_SIGNING.md`** adds **Source and
  licensing**. **`docs/SPEC_AUTOMATED_TESTS.md`** and **`docs/DESIGN_PRINCIPLES.md`** reference **RD1**–**RD8**;
  **`tests/test_reference_documentation_workflow.py`** enforces them.

- **`scripts/sync_upstream_reference_docs.sh`**: optional maintainer helper copies a local upstream **`docs/`** tree into
  **`docs/reference-documentation/_upstream_snapshot/replayt-docs/`** (**`rsync`** when available, else **`cp -a`**). Not invoked
  by **CI** or the main **`pytest`** collection beyond syntax and path-contract checks in
  **`tests/test_reference_documentation_workflow.py`**.

- **`README.md`** (phase **3**, backlog **Expand README with operator troubleshooting and approval-flow walkthrough** /
  `23e2da29-8042-4721-a1eb-e44a2076273f`): operator block uses **`## Troubleshooting`**, **`## Approval webhook flow`**, and
  **`## Verifying webhook signatures`** (misconfiguration checklist, log pointers, **`event_type`** names and optional
  Mermaid sequence, copy-paste verification path). **`tests/test_readme_operator_sections.py`** covers **OP1**–**OP8** in
  **`docs/SPEC_AUTOMATED_TESTS.md`**.

- **`docs/SPEC_README_OPERATOR_SECTIONS.md`**, **`docs/SPEC_AUTOMATED_TESTS.md`**, **`docs/DESIGN_PRINCIPLES.md`**, **`docs/MISSION.md`**, **`README.md`** project layout (phase **2**, backlog **Expand README with operator troubleshooting and approval-flow walkthrough** /
  `23e2da29-8042-4721-a1eb-e44a2076273f`): normative contract for **`README.md`** headings (**Troubleshooting**, **Approval webhook flow**, **Verifying webhook signatures**), content bullets (misconfigs, logs, error-catalog links, approval **`event_type`** names, copy-paste verify path, secrets hygiene), and **pytest** checklist **OP1**–**OP8** for the Builder phase.

- **`docs/MISSION.md`**, **`docs/DESIGN_PRINCIPLES.md`**, **`docs/SPEC_AUTOMATED_TESTS.md`** (phase **5**, backlog **Expand README with operator troubleshooting and approval-flow walkthrough** /
  `23e2da29-8042-4721-a1eb-e44a2076273f`): **OP1**–**OP8** are described as enforced by **`tests/test_readme_operator_sections.py`** (removed stale “when implemented” wording after the README operator tests landed).

### Changed

- **CI / tooling** (phase **3**, backlog **Run ruff in CI for fast style and lint feedback** /
  `5a3f5a7f-d54a-4f8a-a446-e71b932d22c5`): **`.github/workflows/ci.yml`** runs a parallel **`lint`** job (**`ruff check`**
  and **`ruff format --check`** on **`src/`** and **`tests/`**, **`pip install "ruff>=0.6.0"`**) on the same triggers as
  **`test`** / **`supply-chain`**. **`pyproject.toml`** adds **`[tool.ruff]`** with **`target-version = "py311"`** (aligned
  with **`requires-python`**). **`README.md`** documents local **ruff** commands. **`tests/test_ci_ruff_wiring.py`**
  asserts the workflow and **`dev`** extra. **Ruff format** applied across **`src/`** and **`tests/`** so format check
  passes in CI.
  **`docs/SPEC_REPLAYT_DEPENDENCY.md`** compatibility matrix lists the **`lint`** job with **`test`** and **`supply-chain`**.

### Documentation

- **`docs/SPEC_AUTOMATED_TESTS.md`**, **`docs/DESIGN_PRINCIPLES.md`** (phase **2**, backlog **Run ruff in CI for fast style and lint feedback** /
  `5a3f5a7f-d54a-4f8a-a446-e71b932d22c5`): normative **ruff** CI acceptance (**RF1**–**RF5**)—workflow triggers (**`master`**, **`mc/**`**), **`ruff check`** required, optional **`ruff format --check`**, **`[tool.ruff]`** only when defaults are insufficient, **README.md** local command line, **CHANGELOG** when CI wires **ruff**; traceability bullet and **CI entrypoint** cross-links.

- **`docs/MISSION.md`**, **`docs/REPLAYT_ECOSYSTEM_IDEA.md`**, **`docs/SPEC_REPLAYT_DEPENDENCY.md`** (phase **5**, architecture review, backlog **Run ruff in CI for fast style and lint feedback** /
  `5a3f5a7f-d54a-4f8a-a446-e71b932d22c5`): **MISSION** success metrics and ecosystem pitch mention **ruff** with **pytest**; **SPEC_REPLAYT_DEPENDENCY** **CI** § states **`lint`**, **`test`**, and **`supply-chain`** share the pinned **Python** version.

- **`docs/SPEC_STRUCTURED_LOGGING_REDACTION.md`**, **`docs/MISSION.md`**, **`docs/DESIGN_PRINCIPLES.md`** (phase **2**, backlog **Establish structured logging and redaction for webhook handling** /
  `6ea52b2b-ff96-4511-a9f8-d5d9ed6d3711`): backlog **acceptance mapping** (`6ea52b2b`), operator **never-log checklist**,
  **G0**/**G5** spec acceptance rows, **`format_safe_webhook_log_extra`** / **`extra_sensitive_header_names`** clarity;
  **MISSION**/**DESIGN_PRINCIPLES** now point at the spec as the **normative** logging contract (symbols, example **`extra=`**,
  **L1–L9** traceability).

### Changed

- **`replayt_lifecycle_webhooks.redaction`** (phase **3**, backlog **Establish structured logging and redaction for webhook handling** /
  `6ea52b2b-ff96-4511-a9f8-d5d9ed6d3711`): **`format_safe_webhook_log_extra`** accepts **`webhook_body_bytes_len`** and
  optional **`lifecycle_*`** correlation kwargs (verified JSON only); **`None`** lifecycle values are omitted from the
  returned dict. **`DEFAULT_SENSITIVE_MAPPING_KEYS`** includes **`body`**, **`raw_body`**, **`payload`**, and
  **`request_body`** for shallow **`redact_mapping`** defaults. **L9** coverage in **`tests/test_redaction.py`**.

### Documentation

- **`docs/SPEC_STRUCTURED_LOGGING_REDACTION.md`**, **`docs/SPEC_AUTOMATED_TESTS.md`**, **`docs/MISSION.md`**, **`docs/DESIGN_PRINCIPLES.md`**, **`docs/SPEC_WEBHOOK_FAILURE_RESPONSES.md`**, **`README.md`** (phase **2**, backlog **Establish structured logging and redaction for webhook handling** /
  `6ea52b2b-ff96-4511-a9f8-d5d9ed6d3711`): normative **request logging** rules (**no default raw body**; length-only
  **`webhook_body_bytes_len`**); **recommended `extra=` field names** aligned with **[EVENTS.md](docs/EVENTS.md)** correlation ids;
  **§ Example: successful verified delivery** for operators; default **mapping** keys extended with **`body`** /
  **`raw_body`** / **`payload`** / **`request_body`**; **L9** test row (success-path log shape + absence of raw body
  substring); cross-links and **L1–L9** wording across specs and README.
- **`docs/SPEC_STRUCTURED_LOGGING_REDACTION.md`**, **`docs/SPEC_AUTOMATED_TESTS.md`**, **`docs/MISSION.md`**, **`README.md`**
  (phase **3**, same backlog **`6ea52b2b`**): **`format_safe_webhook_log_extra`** contract documents **`webhook_body_bytes_len`**
  and **`lifecycle_*`** kwargs; **L9** row points at **`test_l9_success_verified_delivery_no_raw_body_in_logs`**; normative
  success **`extra=`** example omits absent **`lifecycle_approval_request_id`**.
- **`CHANGELOG.md`** (phase **6**, security review, backlog **Establish structured logging and redaction for webhook handling** /
  `6ea52b2b-ff96-4511-a9f8-d5d9ed6d3711`): reviewed diff vs **`master`** (**`src/replayt_lifecycle_webhooks/redaction.py`**, **`tests/test_redaction.py`**, specs/README). **Checklist:** no default raw body or signature material in **`format_safe_webhook_log_extra`**; sensitive headers and common secret-like mapping keys redacted (**L1–L9** in CI); synthetic test tokens only; **`pyproject.toml`** / **`.github/workflows/ci.yml`** unchanged by this backlog; runtime pins remain **`pydantic>=2.6.0`** and **`replayt>=0.4.25`** per **SPEC_REPLAYT_DEPENDENCY**; **CI** still runs **`pytest tests`** and **`pip-audit`** (**`supply-chain`** job).
- **`docs/SPEC_REPLAYT_DEPENDENCY.md`**, **`README.md`**, **`docs/SPEC_AUTOMATED_TESTS.md`** (phase **2**, backlog **Add replayt dependency declaration and compatibility matrix stub** /
  `8b16060d-f6e6-4111-bed2-4978b965ff52`): **compatibility matrix** now lists **`requires-python`**, **CI-tested Python** (**3.12**, `.github/workflows/ci.yml`), and how **replayt** is resolved in CI vs the declared lower bound; **stub / pre-coupling** checklist when **`replayt`** is not yet in **`[project.dependencies]`**; acceptance **A8**; **A1**/**A2** cover the stub path. README states **Python** / **CI** expectations; **SPEC_AUTOMATED_TESTS** traceability points at **A1**–**A8**.
- **`docs/DESIGN_PRINCIPLES.md`**, **README** project layout table (phase **5**, architecture review, backlog **Add replayt dependency declaration and compatibility matrix stub** /
  `8b16060d-f6e6-4111-bed2-4978b965ff52`): **explicit contracts** bullet and **SPEC_REPLAYT_DEPENDENCY** row now name **Python** / **CI-tested** columns in the **compatibility matrix**, not only **replayt** ↔ package wording.
- **`CHANGELOG.md`** (phase **6**, security review, same backlog **`8b16060d`**): recorded security pass — `git diff master` is documentation and **`tests/test_replayt_dependency.py`** only (no **`src/`** or **`pyproject.toml`** changes in that diff); new tests read **`pyproject.toml`**, **`.github/workflows/ci.yml`**, and specs from disk only (no network/subprocess); no secrets or live credentials in added prose; runtime pins remain **`pydantic>=2.6.0`** and **`replayt>=0.4.25`** per existing policy; **CI** still runs **pytest** and the **supply-chain** **`pip-audit`** job (workflow unchanged there).

### Added

- **Lifecycle event digests** (phase **3**, backlog **Publish PM- and support-friendly event digest format** /
  `069e0240-54c5-44a9-bba3-ad0a80a52c60`): **`lifecycle_event_to_digest_text`** and **`lifecycle_event_to_digest_record`**
  per **`docs/SPEC_EVENT_DIGEST.md`** (**DG0** text layout and **`digest/1`** record). Re-exported from the
  package root and **`replayt_lifecycle_webhooks.events`**; implementation in **`replayt_lifecycle_webhooks.digest`**
  (internal). **`tests/test_event_digest.py`** covers **DG1–DG6**. **`docs/SPEC_PUBLIC_API.md`** and **`README.md`** /
  **`docs/EVENTS.md`** updated for exports and external-sharing guidance.

- **Public API contract tests** (phase **3**, backlog **Define public API surface and deprecation policy before 1.0** /
  `30e133a5-78fa-4eee-ae56-56a1af4c9f73`): **`tests/test_public_api.py`** asserts package root and **`events`** **`__all__`**
  match **`docs/SPEC_PUBLIC_API.md`**, documented internal modules import, and deprecation policy anchors in the spec.
  Package root **`__all__`** order aligned with that spec table.

- **SPEC_REPLAYT_DEPENDENCY acceptance A8** (phase **3**, backlog **Add replayt dependency declaration and compatibility matrix stub** /
  `8b16060d-f6e6-4111-bed2-4978b965ff52`): **`tests/test_replayt_dependency.py`** now checks **README**, the spec **compatibility matrix**,
  **`pyproject.toml`** **`requires-python`**, **`.github/workflows/ci.yml`** **`python-version`**, and the **CI note on replayt versions**
  stay aligned (single CI Python; matrix echoes declared and tested interpreters).

### Documentation

- **`docs/REPLAYT_ECOSYSTEM_IDEA.md`** and **README** Overview (phase **2**, backlog **Record primary ecosystem pattern in REPLAYT_ECOSYSTEM_IDEA** /
  `c70b89c2-7fd4-4733-b72d-23fd20279617`): **Core-gap** section filled for this repo (what stays upstream vs what ships
  here); **Your choice** adds a **replayt** release-tracking note (**`pyproject.toml`**, **SPEC_REPLAYT_DEPENDENCY**, **CI** /
  **pytest** + **SPEC_REPLAYT_BOUNDARY_TESTS**, **CHANGELOG**, PyPI / upstream monitoring). README explicitly cross-links
  **Core-gap** and the ecosystem doc.

- **`docs/SPEC_PUBLIC_API.md`** (phase **2**, backlog **Define public API surface and deprecation policy before 1.0** /
  `30e133a5-78fa-4eee-ae56-56a1af4c9f73`): normative **supported** imports (package root **`__all__`** and
  **`replayt_lifecycle_webhooks.events`**); **internal** submodule paths until **1.0**; documented **`python -m`**
  entrypoints; **semver**, **pre-1.0** stability, and **deprecation** rules (**CHANGELOG** **Deprecated**, minimum **one**
  **0.x minor** after the deprecating release, **`DeprecationWarning`** when practical). Acceptance **API1**–**API3**.
  Cross-links from **README**, **MISSION**, **DESIGN_PRINCIPLES** (new **Semantic versioning and deprecation** subsection),
  **SPEC_AUTOMATED_TESTS**.

- **`docs/SPEC_EVENT_DIGEST.md`** (phase **2**, backlog **Publish PM- and support-friendly event digest format** /
  `069e0240-54c5-44a9-bba3-ad0a80a52c60`): normative **deterministic** digest **text** (line templates for all six
  **`event_type`** values), **`digest/1`** JSON **record** shape, **DG0** determinism rules, **three** synthetic
  **worked examples**, external-sharing cautions, and acceptance **DG1–DG6** for Builder/Tester. Cross-links from **README**,
  **MISSION**, **EVENTS.md**, **DESIGN_PRINCIPLES**, and **SPEC_AUTOMATED_TESTS**.

- **Digest docs and test traceability** (phase **5**, same backlog): **`SPEC_EVENT_DIGEST.md`** updated for shipped
  **`lifecycle_event_to_digest_*`** helpers; **`SPEC_AUTOMATED_TESTS.md`** adds topic row and **Backlog `069e0240`** table
  (**DG1**–**DG6**); **`MISSION.md`** and **`DESIGN_PRINCIPLES.md`** link **SPEC_EVENT_DIGEST** (CHANGELOG cross-link list
  now matches the tree).

- **`CHANGELOG.md`** (phase **6**, security review, backlog **Publish PM- and support-friendly event digest format** /
  `069e0240-54c5-44a9-bba3-ad0a80a52c60`): recorded security pass — digest implementation does not log or expose signing
  material; digest text/record carries sender-controlled fields as documented (**SPEC_EVENT_DIGEST** external-sharing
  section + integrator docs); dependency manifest unchanged in this diff; **CI** still runs **pytest** and **`pip-audit`**.

- **`docs/SPEC_REPLAY_PROTECTION.md`** (phase **2**, backlog **Add replay protection and idempotency hooks for deliveries** /
  `f9677140-0803-41c7-9d1c-82fc85f25f8d`): normative contract for **stale capture** vs **benign duplicate** delivery;
  post-MAC processing order; **`occurred_at`** freshness with recommended **900s** max age and **300s** future skew;
  reserved optional **`Replayt-Delivery-Id`**, **`Replayt-Webhook-Timestamp`**, **`Replayt-Nonce`** headers;
  **`LifecycleWebhookDedupStore`** + **`InMemoryLifecycleWebhookDedupStore`** requirements; optional
  **`handle_lifecycle_webhook_post`** extension points; acceptance **RP0**–**RP5** (implementation and tests: phase **3**).
  Cross-links from **README**, **MISSION**, **DESIGN_PRINCIPLES**, **SPEC_DELIVERY_IDEMPOTENCY**, **SPEC_WEBHOOK_SIGNATURE**,
  **SPEC_MINIMAL_HTTP_HANDLER**, **SPEC_WEBHOOK_FAILURE_RESPONSES**, **SPEC_AUTOMATED_TESTS** (new **Backlog `f9677140`** table).

- **`docs/SPEC_MINIMAL_HTTP_HANDLER.md`**, **README** (spec index), **`docs/SPEC_AUTOMATED_TESTS.md`**, and **`tests/test_http_handler.py`**
  module docstring (phase **5** architecture review, backlog **`f9677140`**): acceptance rows **H9**–**H12** and **H1**–**H12**
  traceability; **`on_success`** / JSON rules when **`dedup_store`** or **`replay_policy`** is set; removed the obsolete
  “until implemented” note from **SPEC_MINIMAL_HTTP_HANDLER**.

### Added

- **Replay protection hooks** (phase **3**, backlog **Add replay protection and idempotency hooks for deliveries** /
  `f9677140-0803-41c7-9d1c-82fc85f25f8d`): **`LifecycleWebhookDedupStore`** protocol, **`InMemoryLifecycleWebhookDedupStore`**
  (TTL + injectable clock), **`LifecycleWebhookReplayPolicy`** and **`ensure_occurred_at_within_replay_window`** /
  **`ReplayFreshnessRejected`** for payload **`occurred_at`** freshness (defaults **900s** max age, **300s** future skew).
  **`handle_lifecycle_webhook_post`** and **`make_lifecycle_webhook_wsgi_app`** accept optional **`dedup_store`** and
  **`replay_policy`**: post-verify order is freshness then **`event_id`** claim; duplicate **`event_id`** returns **204**
  without **`on_success`**; stale **`occurred_at`** returns **422** **`replay_rejected`**. **`tests/test_replay_protection.py`**
  covers **RP4** / **RP5** and helpers. See **`docs/SPEC_REPLAY_PROTECTION.md`**.

- **Structured logging redaction** (phase **3**, backlog **Add structured logging helper that redacts sensitive keys by default** /
  `fa75ecf3-a113-418e-99cc-aa0c31237eba`): **`replayt_lifecycle_webhooks.redaction`** with **`REDACTED_PLACEHOLDER`**,
  **`redact_headers`** (case-insensitive defaults, **`X-Signature*`** prefix rule, **`extra_sensitive_names`**),
  **`redact_mapping`** (shallow defaults, **`extra_sensitive_keys`**), **`format_safe_webhook_log_extra`**, and documented
  **`DEFAULT_SENSITIVE_HEADER_NAMES`** / **`DEFAULT_SENSITIVE_MAPPING_KEYS`**. Re-exported from the package root **`__init__`**.
  **`tests/test_redaction.py`** covers **SPEC_AUTOMATED_TESTS** **L1–L9**. No new mandatory runtime dependencies.

### Fixed

- **Replay freshness helper** (phase **6** security review, backlog **Add replay protection and idempotency hooks for deliveries** /
  `f9677140-0803-41c7-9d1c-82fc85f25f8d`): **`ensure_occurred_at_within_replay_window`** now raises **`ReplayFreshnessRejected`**
  when **`occurred_at`** is not a parseable RFC 3339 instant, instead of letting **`ValueError`** escape (which could surface
  as an unhandled server error when **`replay_policy`** freshness checks are enabled on **`handle_lifecycle_webhook_post`**).

- **`format_safe_webhook_log_extra`** (phase **5** architecture review, same backlog **`fa75ecf3`**): removed an unused
  **`extra_sensitive_keys`** keyword argument (it was ignored). Use **`redact_mapping(..., extra_sensitive_keys=...)`** for
  non-header fields in **`Logger.*(..., extra={...})`**.

- **SPEC_PUBLIC_API** acceptance text and **API1** tests (phase **5** architecture review, backlog **Define public API surface and deprecation policy before 1.0** /
  `30e133a5-78fa-4eee-ae56-56a1af4c9f73`): **§ Primary: package root** now states **`__all__`** order matches the table; **`tests/test_public_api.py`** asserts list order for the package root and **`events`** **`__all__`**, not only set equality. **SPEC_AUTOMATED_TESTS** **API1** rows updated to match.

### Documentation

- **`docs/SPEC_LOCAL_WEBHOOK_DEMO.md`** (phase **3**, backlog **Specify idempotency and replay-safe delivery semantics** /
  `4280c054-4193-4754-8e4c-1da320975fac`): fixtures section notes reusing the same file bytes for dev HTTP retries (stable
  **`event_id`** and MAC) and links **`docs/SPEC_DELIVERY_IDEMPOTENCY.md`**.

- **`docs/SPEC_DELIVERY_IDEMPOTENCY.md`** (phase **2**, backlog **Specify idempotency and replay-safe delivery semantics** /
  `4280c054-4193-4754-8e4c-1da320975fac`): normative consumer contract for **at-least-once** HTTP delivery, **`event_id`**
  as primary dedupe key (senders **SHOULD** stabilize per logical emission), composite-key fallbacks, idempotency store
  **TTL** guidance, and acceptance rows **I1–I4**. **`docs/EVENTS.md`** **`event_id`** row and **E7** aligned; cross-links
  from **README** (**Troubleshooting**), **MISSION**, **DESIGN_PRINCIPLES**, **SPEC_WEBHOOK_SIGNATURE**,
  **SPEC_WEBHOOK_FAILURE_RESPONSES**, **REPLAYT_WEBHOOK_SIGNING**.

- **`docs/EVENTS.md`** (**E7** verification row) and **`docs/SPEC_AUTOMATED_TESTS.md`** (traceability table, minimum coverage
  item **2**, **Backlog `4280c054`** **I3**/**I4** table, **Related docs**): phase **5** architecture review so automated-test
  docs match implemented **SPEC_DELIVERY_IDEMPOTENCY** coverage.

- **`docs/SPEC_STRUCTURED_LOGGING_REDACTION.md`** (phase **2**, backlog **Add structured logging helper that redacts sensitive keys by default** /
  `fa75ecf3-a113-418e-99cc-aa0c31237eba`): normative contract for **stdlib** **`logging`**, **`[REDACTED]`** placeholder,
  default sensitive **HTTP header** names (incl. **`X-Signature*`** prefix rule) and **mapping** keys, public API surface
  (**`redact_headers`**, **`redact_mapping`**, structured **`extra`** helper), **package-owned** logging rules, and spec
  checklists **G0–G5** / test rows **L1–L9** in **SPEC_AUTOMATED_TESTS**. Cross-links from **SPEC_WEBHOOK_FAILURE_RESPONSES**
  (**F6**), **DESIGN_PRINCIPLES**, **MISSION**, **README** (**Production logging and redaction**), **SPEC_MINIMAL_HTTP_HANDLER**,
  **SPEC_HTTP_SERVER_ENTRYPOINT**.

- **`docs/SPEC_LOCAL_WEBHOOK_DEMO.md`** (phase **2**, backlog **Add a one-command local demo script for webhook delivery** /
  `ab0bfe3c-a94c-4711-8a5b-eeb47c886d2c`): normative contract for a **local** signed **POST** demo — primary
  **`python -m replayt_lifecycle_webhooks.demo_webhook`**, **v1** MAC alignment with **SPEC_WEBHOOK_SIGNATURE**, default
  **`http://127.0.0.1:8000/webhook`**, **`tests/fixtures/events/`** fixtures, CLI **`--help`** / env expectations, and
  acceptance **D1–D9**. Cross-links and **README** **Try it locally** subsection; **SPEC_AUTOMATED_TESTS** / **MISSION** /
  **DESIGN_PRINCIPLES** / **SPEC_HTTP_SERVER_ENTRYPOINT** / **SPEC_WEBHOOK_SIGNATURE** pointers updated.

### Tests

- **`event_id`** idempotency fixtures (**I3**, **I4**, **SPEC_DELIVERY_IDEMPOTENCY**; phase **3**, backlog **Specify
  idempotency and replay-safe delivery semantics** / `4280c054-4193-4754-8e4c-1da320975fac`): **`run_started_redelivery.json`**
  (byte-identical to **`run_started.json`**) under **`tests/fixtures/events/`** and **`replayt_lifecycle_webhooks/fixtures/events/`**;
  **`tests/test_lifecycle_events.py`** asserts same logical emission shares **`event_id`** and body octets, distinct fixtures
  differ, and a signed duplicate POST pattern dedupes side effects on **`event_id`**. **`tests/test_demo_webhook.py`** keeps
  packaged bytes aligned with the tests tree.

- **Golden-vector** **`Replayt-Signature`** case with committed expected MAC, and **explicit** imports of
  **`replayt_lifecycle_webhooks.signature`** / **`handler`** in **`tests/`** (phase **3**, backlog **Replace scaffold
  smoke test with real unit and boundary tests** / `2b4c6927-573a-463c-b59f-f2f91dfb6381`; **SPEC_AUTOMATED_TESTS** **A6**,
  **A10**).

### Documentation

- **`docs/SPEC_AUTOMATED_TESTS.md`** (phase **5**, backlog **Replace scaffold smoke test with real unit and boundary tests** /
  `2b4c6927-573a-463c-b59f-f2f91dfb6381`): **Backlog `2b4c6927`** checklist **A6–A10** so **CHANGELOG** and test
  comments that cite those rows match the spec.

### Added

- **Local demo webhook POST** (phase **3**, backlog **Add a one-command local demo script for webhook delivery** /
  `ab0bfe3c-a94c-4711-8a5b-eeb47c886d2c`): **`python -m replayt_lifecycle_webhooks.demo_webhook`** (primary) and
  **`replayt-lifecycle-webhooks-demo-post`**; stdlib **`urllib.request`** client; **`compute_lifecycle_webhook_signature_header`**
  (**v1** MAC aligned with **`verify_lifecycle_webhook_signature`**); packaged JSON under **`replayt_lifecycle_webhooks/fixtures/events/`**
  (same bytes as **`tests/fixtures/events/`**); **`tests/test_demo_webhook.py`** for **SPEC_LOCAL_WEBHOOK_DEMO** **D3** / **D7** / **D8** / **D9**.
  No new mandatory runtime dependencies.

- **Reference HTTP server** (phase **3**, backlog **Expose a minimal HTTP receiver (ASGI/WSGI) behind one entrypoint** /
  `2cf0f4fb-ef9a-40d4-b306-8a46d30f409e`): **`python -m replayt_lifecycle_webhooks`** (primary) and console script
  **`replayt-lifecycle-webhooks-serve`**; stdlib **WSGI** with **`GET /health`**, **`POST /webhook`** (default path;
  **`--host`**, **`--port`**, **`--webhook-path`**, optional **`--secret`**); **`replayt_lifecycle_webhooks.serve`**
  **`make_reference_lifecycle_webhook_wsgi_app`** for in-process mounts; **`tests/test_reference_server.py`** covers
  **S3**, **S4**, **S6** without binding public sockets. No new runtime dependencies (**`pip install`** unchanged).

### Documentation

- **`docs/SPEC_HTTP_SERVER_ENTRYPOINT.md`**, **`README.md`**, **`docs/MISSION.md`**, **`docs/DESIGN_PRINCIPLES.md`**,
  **`docs/SPEC_MINIMAL_HTTP_HANDLER.md`**, **`docs/SPEC_AUTOMATED_TESTS.md`**, **`docs/DEPENDENCY_AUDIT.md`**
  (phase **2**, backlog **Expose a minimal HTTP receiver (ASGI/WSGI) behind one entrypoint** / `2cf0f4fb-ef9a-40d4-b306-8a46d30f409e`):
  normative **reference server** contract — single canonical start command (**`python -m` and/or console script**), **POST**
  webhook path, **`GET /health`** (or spec-aligned alternative), host/port defaults, optional **ASGI** vs **stdlib WSGI**
  stack choice with **optional-dependencies** posture; **S1–S8** acceptance for Builder/Tester; **CHANGELOG** /
  **`pyproject.toml`** justification rule for new deps; CI tests **S6** (in-process, no network) when implemented.

### Changed

- **`parse_lifecycle_webhook_event`** (phase **3**, backlog **Define canonical webhook payload and event envelope schema** /
  `df51dbf9`): when **`schema_version`** is present it must be **`1.0`** (see **`SUPPORTED_LIFECYCLE_WEBHOOK_SCHEMA_VERSIONS`**);
  omitted remains valid per **EVENTS.md**. Informative **`docs/schemas/lifecycle_webhook_payload-1-0.schema.json`** constrains
  **`schema_version`** with **`enum`** when the key is sent.

### Added

- **`jsonschema`** in **`[project.optional-dependencies].dev`** and **pytest** checks that **`docs/schemas/lifecycle_webhook_payload-1-0.schema.json`**
  parses and that **`tests/fixtures/events/*.json`** validate under Draft-07 (phase **3**, backlog **Define canonical webhook payload and event envelope schema** / `df51dbf9`).

### Documentation

- **`README.md`** (phase **5**, architecture review, backlog **Define canonical webhook payload and event envelope schema** /
  `df51dbf9`): **Run / approval payload** paragraph notes **`parse_lifecycle_webhook_event`** and present **`schema_version`**
  against **`SUPPORTED_LIFECYCLE_WEBHOOK_SCHEMA_VERSIONS`**.
- **`docs/EVENTS.md`** (phase **3**, backlog **Define canonical webhook payload and event envelope schema** / `df51dbf9`): **T4**
  documents unsupported **`schema_version`** as a validation failure.
- **`docs/EVENTS.md`**, **`docs/schemas/lifecycle_webhook_payload-1-0.schema.json`**, **`README.md`**, **`docs/SPEC_WEBHOOK_SIGNATURE.md`**
  (phase **2**, same backlog): canonical **envelope** definition; **`schema_version`** **`MAJOR.MINOR`** rules; **breaking vs additive**
  maintainer table; package SemVer alignment; informative JSON Schema for **`1.0`**-family payloads; cross-link from signing spec
  (payload contract orthogonal to HMAC **v1**).

### Added

- **`tests/test_replayt_boundary.py`**, **`replayt_boundary`** pytest marker in **`pyproject.toml`** (phase **3**, backlog **Ship
  contract or integration tests at the replayt boundary** / `d9d6b302-40c7-4e08-af2d-faabb923f2fe`): **`import replayt`** and
  **EVENTS.md** symbols **`RunResult`**, **`RunFailed`**, **`ApprovalPending`** per **SPEC_REPLAYT_BOUNDARY_TESTS**.

### Documentation

- **`docs/SPEC_REPLAYT_BOUNDARY_TESTS.md`**, **`docs/SPEC_AUTOMATED_TESTS.md`**, **`README.md`**, **`docs/MISSION.md`**,
  **`docs/SPEC_REPLAYT_DEPENDENCY.md`**, **`docs/DESIGN_PRINCIPLES.md`**, **`docs/EVENTS.md`** (phase **2**, backlog **Ship
  contract or integration tests at the replayt boundary** / `d9d6b302-40c7-4e08-af2d-faabb923f2fe`): normative **replayt**
  boundary bar (**R1–R5** checklist); default **`pytest tests -q`** vs focused runs; CI remains **no undisclosed network**
  on **`pip install -e ".[dev]"`**.

### Changed

- **`handle_lifecycle_webhook_post`** / **`make_lifecycle_webhook_wsgi_app`** (phase **3**, backlog **Document webhook
  failure responses operators can act on** / `5ec1325a-5b45-440f-b93f-28b711fa5482`): **405** / **401** / **403** /
  **400** responses now include **`application/json; charset=utf-8`** bodies with stable **`error`** codes
  (**`method_not_allowed`**, **`signature_required`**, **`signature_malformed`**, **`signature_mismatch`**,
  **`invalid_json`**) and operator-facing **`message`** text per **`docs/SPEC_WEBHOOK_FAILURE_RESPONSES.md`**. **204**
  remains empty.

### Documentation

- **`docs/SPEC_WEBHOOK_FAILURE_RESPONSES.md`**, **`README.md`**, **`docs/MISSION.md`**, **`docs/SPEC_WEBHOOK_SIGNATURE.md`**,
  **`docs/SPEC_MINIMAL_HTTP_HANDLER.md`**, **`docs/DESIGN_PRINCIPLES.md`** (phase **2**, backlog **Document webhook
  failure responses operators can act on** / `5ec1325a-5b45-440f-b93f-28b711fa5482`): normative JSON error envelope
  (**`error`** + **`message`**), stable codes (**`signature_required`**, **`signature_mismatch`**, **`invalid_json`**,
  **`unknown_event_type`**, **`replay_rejected`**, etc.), typical HTTP statuses, redacted examples, **v1** replay/timestamp
  scope, **what not to log or return**; README runbook table; cross-links from signature / minimal-handler / design
  principles; acceptance **F1–F5**; **Builder (phase 3)** aligned the reference handler JSON bodies with this spec.
- Phase **5** architecture review (same backlog): **H1–H8** labels in **README**, **SPEC_MINIMAL_HTTP_HANDLER**,
  **SPEC_AUTOMATED_TESTS**, **SPEC_WEBHOOK_SIGNATURE** (related docs + exception-to-response mapping), and
  **SPEC_WEBHOOK_FAILURE_RESPONSES** (**405**: custom handlers may use empty/plain text; reference handler uses JSON for
  all client errors); **`tests/test_http_handler.py`** module docstring; historical **CHANGELOG** rows under **0.1.0**
  that listed **H1–H7** for the handler suite.
- **`docs/SPEC_AUTOMATED_TESTS.md`**, **`README.md`**, **`docs/MISSION.md`**, **`docs/DESIGN_PRINCIPLES.md`**,
  **`docs/SPEC_WEBHOOK_SIGNATURE.md`**, **`docs/SPEC_MINIMAL_HTTP_HANDLER.md`**, **`docs/EVENTS.md`** (phase **2**,
  backlog **Replace smoke-only test with real
  package behavior assertions** / `a91574f0-1e57-4b34-9922-763f92448a18`): normative **pytest** / CI entrypoint
  (**`pytest tests -q`**, equivalent **`python -m pytest tests -q`** in CI); minimum behavioral coverage for
  **`verify_lifecycle_webhook_signature`** and **`parse_lifecycle_webhook_event`**; checklist **A1–A5**; forbid
  smoke-only **`assert True`**; remove redundant **`tests/test_smoke.py`** when covered elsewhere.
- **`docs/SPEC_REPLAYT_DEPENDENCY.md`**, **`docs/SPEC_AUTOMATED_TESTS.md`** (phase **5**, architecture review, backlog
  **Replace smoke-only test with real package behavior assertions** / `a91574f0-1e57-4b34-9922-763f92448a18`):
  **SPEC_REPLAYT_DEPENDENCY** **Related docs** links **SPEC_AUTOMATED_TESTS**; **SPEC_AUTOMATED_TESTS** purpose paragraph
  tightened for contributor-facing clarity.

### Removed

- **`tests/test_smoke.py`** (phase **3**, backlog **Replace smoke-only test with real package behavior assertions** /
  `a91574f0-1e57-4b34-9922-763f92448a18`): dropped the placeholder-only test; **`tests/test_webhook_signature.py`**,
  **`tests/test_lifecycle_events.py`**, **`tests/test_http_handler.py`**, and related modules already cover verification
  and JSON parsing.

### Added

- **`src/replayt_lifecycle_webhooks/events.py`**, **`tests/test_lifecycle_events.py`** (phase **3**, backlog **Define typed lifecycle event payloads (run + approval)** /
  `0b929c17-525d-4ec7-b13c-a7b4f3f8ca10`): **`events`** module docstring documents **``schema_version``** and **1.0** payload semantics per **EVENTS.md**; **pytest** covers a missing required **`detail`** envelope field (**T4** / **T5**).
- **`tests/test_replayt_dependency.py`** (phase **3**, backlog **Declare replayt dependency range and compatibility matrix** /
  `1a14a01a-e6be-4f3f-b270-68f57fbbe0e4`): asserts README **Compatibility matrix** pointer and dual-version issue reporting,
  **DESIGN_PRINCIPLES** link to **SPEC_REPLAYT_DEPENDENCY**, and the spec **Compatibility matrix** section includes the
  same **`replayt`** floor as **`pyproject.toml`**.

### Documentation

- **`docs/EVENTS.md`**, **`README.md`**, **`docs/DESIGN_PRINCIPLES.md`** (phase **2**, backlog **Define typed lifecycle event payloads (run + approval)** /
  `0b929c17-525d-4ec7-b13c-a7b4f3f8ca10`): **T1–T7** acceptance criteria for typed parsing; **upstream vs wire JSON** authority; **schema versioning and migration**; normative **Pydantic v2** / **`events`** module table; README links **replayt (PyPI)** for semantics and states **EVENTS.md** + **`parse_lifecycle_webhook_event`** as the package wire contract until upstream publishes an HTTP schema; design principles reference **`events`** and **schema_version** discipline.
- **`docs/SPEC_WEBHOOK_SIGNATURE.md`**, **`docs/SPEC_MINIMAL_HTTP_HANDLER.md`** (phase **5**, architecture review, backlog **Define typed lifecycle event payloads (run + approval)** /
  `0b929c17-525d-4ec7-b13c-a7b4f3f8ca10`): **Related docs** / **JSON payload** text names **EVENTS.md** and **`replayt_lifecycle_webhooks.events`** as the normative lifecycle JSON contract, consistent with **README** and **EVENTS.md**.
- **`docs/SPEC_REPLAYT_DEPENDENCY.md`**, **`README.md`**, **`docs/DESIGN_PRINCIPLES.md`** (phase **3**, backlog **Declare replayt dependency range and compatibility matrix** /
  `1a14a01a-e6be-4f3f-b270-68f57fbbe0e4`): **compatibility matrix**, upper-bound policy, dual-backlog traceability, reporting breakage (**both** package versions), acceptance **A5–A7**; README **Compatibility matrix** pointer and layout row; design principles name matrix and optional upper bound.
- **`docs/SPEC_REPLAYT_DEPENDENCY.md`**, **`CHANGELOG.md`** (phase **5**, architecture review, same backlog /
  `1a14a01a-e6be-4f3f-b270-68f57fbbe0e4`): spec title uses **dependency range** (replacing **runtime pin**); older **SPEC_REPLAYT_DEPENDENCY** changelog summary lists **compatibility matrix** and optional upper bound.
- **`CHANGELOG.md`** (phase **6**, security review, same backlog /
  `1a14a01a-e6be-4f3f-b270-68f57fbbe0e4`): recorded security pass — diff vs **master** is docs + **`tests/test_replayt_dependency.py`** only; no **`src/`** or manifest changes; checklist items **1–6** satisfied (no secrets in new prose, dependency posture matches spec, **CI** still runs **pytest** and **`pip-audit`**).
- **`docs/MISSION.md`** (phase **2**, backlog **Finalize docs/MISSION.md and primary ecosystem pattern** /
  `3f27ad86-ef1f-4883-8cc2-cee94ba301cb`): **Ecosystem positioning** — primary pattern **Core-gap**; skim links to
  **README**; success metrics add **releases and versioning** (SemVer, `pyproject.toml`, changelog
  sections, PyPI); **DESIGN_PRINCIPLES** cross-reference uses a proper in-tree link.
- **`docs/REPLAYT_ECOSYSTEM_IDEA.md`:** completed **Your choice** (core-gap pitch; pointers to **MISSION** and key specs).
  Phase **5** (architecture review): **Your choice** references **taxonomy option 1 above** in plain text (section sign removed).
- **`README.md`:** **Overview** reflects the **MISSION** ecosystem framing (consumer-side gap-fill) and points there for
  scope, success, and release expectations; project layout row updated.

### Added

- **`tests/test_mission_docs.py`** (phase **3**, backlog **Finalize docs/MISSION.md and primary ecosystem pattern** /
  `3f27ad86-ef1f-4883-8cc2-cee94ba301cb`): regression tests for **MISSION** / **REPLAYT_ECOSYSTEM_IDEA** / **README**
  acceptance (ecosystem section, **Core-gap** named once in **MISSION**, link targets, success metrics). Phase **3** /
  backlog **`c70b89c2-7fd4-4733-b72d-23fd20279617`**: **Overview** asserts **Primary ecosystem pattern**, **Core-gap** token,
  **REPLAYT_ECOSYSTEM_IDEA** link before **## Design principles**, plus release-tracking anchors in **REPLAYT_ECOSYSTEM_IDEA**.
- **Lifecycle JSON validation** (phase 3, backlog **Map replayt run and approval events to webhook payload shapes** /
  `076a56b7-afd9-4778-b46a-4dc8875a431f`): **`parse_lifecycle_webhook_event`**, **`LIFECYCLE_WEBHOOK_EVENT_TYPES`**,
  and Pydantic models for the envelope and each **`event_type`** in **`docs/EVENTS.md`**. Golden fixtures live under
  **`tests/fixtures/events/`**; tests cover fixtures (**E2–E4**), invalid **`detail`** / unknown **`event_type`**, missing
  **`correlation.run_id`**, and verify-then-parse ordering with **`handle_lifecycle_webhook_post`**. Runtime dependency
  **`pydantic>=2.6.0`** added (explicit; also required by **replayt**).
- **Minimal HTTP POST handler (phase 3, backlog `6e1255ce`):** **`handle_lifecycle_webhook_post`** (framework-agnostic
  request view → **405** / **401** / **403** / **400** / **204**), **`LifecycleWebhookHttpResult`**, and
  **`make_lifecycle_webhook_wsgi_app`** (stdlib WSGI). **401** for missing or malformed **`Replayt-Signature`**;
  **403** for well-formed MAC mismatch; verify-before-JSON ordering per **`docs/SPEC_MINIMAL_HTTP_HANDLER.md`**.
  Tests cover **H1–H8** (including invalid signature with invalid JSON → **401/403**, not **400**).

### Documentation

- **`docs/EVENTS.md`:** lifecycle webhook JSON spec (phase **2**, backlog **Map replayt run and approval events to webhook payload shapes** / `076a56b7-afd9-4778-b46a-4dc8875a431f`) — common envelope (`event_type`, `occurred_at`, `event_id`, `correlation`, `summary`, `detail`), **run** and **approval** event registry, prohibited content, synthetic examples, acceptance rows **E1–E6**; cross-links **replayt** concepts without requiring core changes.
- **README.md:** pointer to **`parse_lifecycle_webhook_event`** and **`docs/EVENTS.md`** after verification.
- **`docs/MISSION.md`:** phase **2** / backlog **Complete MISSION.md with approval and run-boundary narrative**
  (`83e47fd6-14c7-4a13-9688-56a1b5bb2e06`)—finalized sections **Users and problem**, **Replayt’s role vs this repository**,
  **Lifecycle moments: run vs approval** (table + stakeholder paragraph for PM/support), **Consumer responsibilities**,
  **Success metrics (v0.x)**; **out of scope** clarified for **secrets inside JSON payloads** (HMAC key via documented
  config only; no payload secret contract beyond upstream/spec). Phase **5** (architecture review): **MISSION** in-scope
  bullet now references **Success metrics (v0.x)**; removed a premature **CHANGELOG** note that claimed phase **5** prose
  tightening under the older phase **3** **MISSION** entry.
- **`docs/SPEC_WEBHOOK_SIGNATURE.md`:** explicit **signing scheme v1**, normative **consumer contract** (headers, raw
  body, header value shapes), **clock skew / replay policy** (N/A for v1; how to extend), **ordered verification steps**,
  acceptance rows **W1–W7** and **W3b**. **Backlog `35f984f8-67cc-48bf-9385-0ec73a054314`:** **single verification path**;
  **secret configuration** (recommended **`REPLAYT_LIFECYCLE_WEBHOOK_SECRET`**; library does not read env); **HTTP
  401/403** and **no leakage** of secret / full signature / MAC in responses or production logs; rows **W8–W10**;
  cryptographic hygiene for digest **byte** comparison.
- **`docs/reference-documentation/REPLAYT_WEBHOOK_SIGNING.md`:** scheme version, clock/replay summary, verification steps,
  recommended env var (see README).
- **README.md:** verification procedure link; **HTTP responses and logging** pointer; **`os.environ`** example for the
  recommended secret name.
- **`docs/SPEC_MINIMAL_HTTP_HANDLER.md`:** normative status table, public handler API, WSGI notes, acceptance rows **H1–H8**;
  cross-links to the webhook signature spec.
- **`docs/SPEC_WEBHOOK_SIGNATURE.md`:** **Related docs** link to the minimal HTTP handler spec.
- **`docs/MISSION.md`:** skim pointer to **SPEC_MINIMAL_HTTP_HANDLER**.

### Added

- Webhook verification tests (phase **3**, backlog **Implement HMAC (or documented) request signing verification**):
  success path uses **`hmac.compare_digest`**; failure **`str(exception)`** omits the secret and the header digest hex;
  **verify-before-JSON** ordering covers **spec W8–W9** expectations in the suite.
- **`verify_lifecycle_webhook_signature`** with **`LIFECYCLE_WEBHOOK_SIGNATURE_HEADER`** (`Replayt-Signature`),
  HMAC-SHA256 over the raw body, and exceptions **`WebhookSignatureMissingError`**,
  **`WebhookSignatureFormatError`**, **`WebhookSignatureMismatchError`** (stdlib **`hmac`** / **`hashlib`**,
  **`hmac.compare_digest`** on digests).
- **`docs/reference-documentation/REPLAYT_WEBHOOK_SIGNING.md`:** consumer signing contract cited from the webhook
  signature spec when upstream HTTP delivery docs are absent.
- Unit tests for valid MAC, wrong secret, tampered body, and missing / malformed signature header (no network).
- Unit tests for uppercase hex signature values and for **secret** supplied as **bytes**.
- Runtime dependency on **replayt** `>=0.4.25` (lower bound only). The package does not import **replayt** yet; this
  floor matches the first integration surface and PyPI versions verified at pin time.
- Tests that assert the canonical **replayt** `>=M.m.p` line in `pyproject.toml` and README compatibility anchors from
  **SPEC_REPLAYT_DEPENDENCY.md**.

### Changed

- **CI:** the test job runs `pip install -e .` before `pip install -e ".[dev]"` so the minimal editable install is
  verified every run.
- **`LIFECYCLE_WEBHOOK_SIGNATURE_HEADER`:** annotated as `Final[str]` to match the spec.

### Documentation

- **`docs/SPEC_WEBHOOK_SIGNATURE.md`:** specification and acceptance checklist for incoming webhook signature
  verification (public API shape, test matrix, upstream alignment, non-goals); pointer to
  **`reference-documentation/REPLAYT_WEBHOOK_SIGNING.md`** as in-repo contract authority when upstream HTTP delivery
  docs are absent.
- **`docs/MISSION.md`:** phase **3** / backlog **Ship a one-page MISSION with scope and success criteria**—integrator skim
  paragraph, **replayt** capabilities consumed, explicit in/out scope bullets, success including **CI** and **automated
  tests** (**pytest**), short doc hygiene checklist; v0.x defers enterprise / extended LLM narrative to
  **DESIGN_PRINCIPLES.md**.
- **`README.md`:** **Overview** links **docs/REPLAYT_ECOSYSTEM_IDEA.md** and **docs/MISSION.md** (ecosystem taxonomy and scope
  / success); link to the webhook signature spec, project layout row, reference-documentation note, and a
  copy-paste verification example using the public API; compatibility one-liner, how to check the installed **replayt**
  version, PyPI and release-history links, and [GitHub Issues](https://github.com/flogat/replayt-lifecycle-webhooks/issues)
  for breakage reports.
- **`pyproject.toml`:** `Homepage` and `Issues` URLs for this repository.
- **`docs/SPEC_REPLAYT_DEPENDENCY.md`:** formal spec for the **replayt** dependency range (lower bound, optional upper
  bound, **compatibility matrix**, acceptance criteria, bump policy, CI expectations); linked from README and design/dependency docs.

## [0.1.0] - 2026-03-27

### Added

- Initial scaffold and package layout.
