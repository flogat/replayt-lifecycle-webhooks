# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
  acceptance (ecosystem section, **Core-gap** named once in **MISSION**, link targets, success metrics, README avoids
  repeating the taxonomy token).
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
- **`README.md`:** **Overview** lists **MISSION** before **REPLAYT_ECOSYSTEM_IDEA** so scope and success are easy to find
  (phase **5**); link to the webhook signature spec, project layout row, reference-documentation note, and a
  copy-paste verification example using the public API; compatibility one-liner, how to check the installed **replayt**
  version, PyPI and release-history links, and [GitHub Issues](https://github.com/flogat/replayt-lifecycle-webhooks/issues)
  for breakage reports.
- **`pyproject.toml`:** `Homepage` and `Issues` URLs for this repository.
- **`docs/SPEC_REPLAYT_DEPENDENCY.md`:** formal spec for the **replayt** dependency range (lower bound, optional upper
  bound, **compatibility matrix**, acceptance criteria, bump policy, CI expectations); linked from README and design/dependency docs.

## [0.1.0] - 2026-03-27

### Added

- Initial scaffold and package layout.
