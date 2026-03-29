# Spec: automated tests and CI entrypoint

**Backlogs (normative traceability):**

- Replace smoke-only test with real package behavior assertions (`a91574f0-1e57-4b34-9922-763f92448a18`).
- Ship contract or integration tests at the replayt boundary (`d9d6b302-40c7-4e08-af2d-faabb923f2fe`) — see **[SPEC_REPLAYT_BOUNDARY_TESTS.md](SPEC_REPLAYT_BOUNDARY_TESTS.md)**.
- Replace scaffold smoke tests with unit and boundary coverage (`2b4c6927-573a-463c-b59f-f2f91dfb6381`) — rows **A6–A10** under **Backlog `2b4c6927`** below.
- Local demo webhook POST (`ab0bfe3c-a94c-4711-8a5b-eeb47c886d2c`) — checklist **D1–D9** in **[SPEC_LOCAL_WEBHOOK_DEMO.md](SPEC_LOCAL_WEBHOOK_DEMO.md)**.
- Structured logging with default sensitive-key redaction (`fa75ecf3-a113-418e-99cc-aa0c31237eba`; workflow
  **`6ea52b2b-ff96-4511-a9f8-d5d9ed6d3711`**) — checklist **L1–L9** in
  **[SPEC_STRUCTURED_LOGGING_REDACTION.md](SPEC_STRUCTURED_LOGGING_REDACTION.md)** and **Backlog `fa75ecf3`** below.
- Delivery idempotency and **`event_id`** (`4280c054-4193-4754-8e4c-1da320975fac`) — acceptance **I3**/**I4** in
  **[SPEC_DELIVERY_IDEMPOTENCY.md](SPEC_DELIVERY_IDEMPOTENCY.md)**; **`tests/test_lifecycle_events.py`** and packaged duplicate fixture under **Backlog `4280c054`** below.
- Replay protection and idempotency hooks (`f9677140-0803-41c7-9d1c-82fc85f25f8d`) — acceptance **RP4**/**RP5** in
  **[SPEC_REPLAY_PROTECTION.md](SPEC_REPLAY_PROTECTION.md)**; **Backlog `f9677140`** table below (**RP5** overlaps **I4**).
- PM/support lifecycle event digest format (`069e0240-54c5-44a9-bba3-ad0a80a52c60`) — acceptance **DG1**–**DG6** in
  **[SPEC_EVENT_DIGEST.md](SPEC_EVENT_DIGEST.md)**; **Backlog `069e0240`** table below.
- Add replayt dependency declaration and compatibility matrix stub (`8b16060d-f6e6-4111-bed2-4978b965ff52`) — **SPEC_REPLAYT_DEPENDENCY** matrix (**Python** / CI-tested columns), **A8**, stub checklist when **`replayt`** is absent from **`pyproject.toml`**.

- Run **ruff** in CI for fast lint (and optionally format) feedback (`5a3f5a7f-d54a-4f8a-a446-e71b932d22c5`) — checklist **RF1**–**RF5** under **Backlog `5a3f5a7f`** below.
- README operator sections: troubleshooting, approval flow, signature verification (`23e2da29-8042-4721-a1eb-e44a2076273f`) —
  checklist **OP1**–**OP8** under **Backlog `23e2da29`** below; normative contract
  **[SPEC_README_OPERATOR_SECTIONS.md](SPEC_README_OPERATOR_SECTIONS.md)**.
- Reverse proxy in front of the reference HTTP server (`dc212184-8c0d-4ee6-90de-e0d50c370f6f`) — checklist **OG1**–**OG8**
  under **Backlog `dc212184`** below; normative contract
  **[SPEC_REVERSE_PROXY_REFERENCE_SERVER.md](SPEC_REVERSE_PROXY_REFERENCE_SERVER.md)**; deliverable **`docs/OPERATOR_REVERSE_PROXY.md`**.
- Optional reference-documentation snapshot workflow (`eb884da9-5273-4ce0-b105-5130c6b1ac79`; Mission Control refinement
  **`2db687f4-23d2-4aff-8827-c3da11cdf283`**) — checklist **RD1**–**RD8** (pytest) in
  **[SPEC_REFERENCE_DOCUMENTATION.md](SPEC_REFERENCE_DOCUMENTATION.md)**; **§ Backlog `eb884da9`** below;
  **`tests/test_reference_documentation_workflow.py`**.
- Subprocess integration test against the real **`python -m replayt_lifecycle_webhooks`** entrypoint
  (`83e07114-fbec-46ab-9944-d2aa3bca0024`) — checklist **SUB1**–**SUB8** under **§ Backlog `83e07114`** below;
  normative server contract **[SPEC_HTTP_SERVER_ENTRYPOINT.md](SPEC_HTTP_SERVER_ENTRYPOINT.md)** (**S9**).

**Audience:** Spec gate (2b), Builder (3), Tester (4), maintainers, contributors.

## Purpose and normative status

This document defines what the **pytest** suite must prove so **CI** fails when signature verification or JSON parsing
regresses. It matches **[DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)** (**observable automation**, **explicit contracts**):
failures in those areas must **break** automated tests, not pass via **`assert True`**.

Detailed matrices for each surface live in the feature specs; this file ties them to **one** CI command and **minimum**
behavioral coverage.

| Topic | Where it lives |
| ----- | -------------- |
| Signature verification behavior and **W** rows | **[SPEC_WEBHOOK_SIGNATURE.md](SPEC_WEBHOOK_SIGNATURE.md)** |
| Optional HTTP handler status codes (**H1–H12**) | **[SPEC_MINIMAL_HTTP_HANDLER.md](SPEC_MINIMAL_HTTP_HANDLER.md)** |
| Reference HTTP server entrypoint (**S1–S9**), when implemented | **[SPEC_HTTP_SERVER_ENTRYPOINT.md](SPEC_HTTP_SERVER_ENTRYPOINT.md)** |
| Operator reverse-proxy guide (**OG1–OG8**) | **[SPEC_REVERSE_PROXY_REFERENCE_SERVER.md](SPEC_REVERSE_PROXY_REFERENCE_SERVER.md)**; **§ Backlog `dc212184`** |
| Local signed demo POST (**D1–D9**), when implemented | **[SPEC_LOCAL_WEBHOOK_DEMO.md](SPEC_LOCAL_WEBHOOK_DEMO.md)** |
| Lifecycle JSON shapes and typed parsing (**E***, **T***) | **[EVENTS.md](EVENTS.md)** |
| Lifecycle event digest text and **`digest/1`** record (**DG1**–**DG6**) | **[SPEC_EVENT_DIGEST.md](SPEC_EVENT_DIGEST.md)** |
| **`event_id`** duplicate fixtures and handler dedupe patterns (**I3**, **I4**) | **[SPEC_DELIVERY_IDEMPOTENCY.md](SPEC_DELIVERY_IDEMPOTENCY.md)** |
| Replay / freshness vs duplicate delivery (**RP4**, **RP5**) | **[SPEC_REPLAY_PROTECTION.md](SPEC_REPLAY_PROTECTION.md)** |
| **replayt** dependency / doc contract (**A1**–**A8**, matrix **Python** + CI) | **[SPEC_REPLAYT_DEPENDENCY.md](SPEC_REPLAYT_DEPENDENCY.md)** |
| **`replayt` import / API stability at the dependency seam** | **[SPEC_REPLAYT_BOUNDARY_TESTS.md](SPEC_REPLAYT_BOUNDARY_TESTS.md)** |
| **This package’s supported exports** (`__all__`, import paths, CLI **`-m`**, deprecation) | **[SPEC_PUBLIC_API.md](SPEC_PUBLIC_API.md)** |
| Structured logging + redaction (**L1–L9**), when implemented | **[SPEC_STRUCTURED_LOGGING_REDACTION.md](SPEC_STRUCTURED_LOGGING_REDACTION.md)** |
| **Ruff** lint (and optional format check) in CI | **§ Backlog `5a3f5a7f`** in this document |
| README operator-facing sections (**Troubleshooting**, **Approval webhook flow**, **Verifying webhook signatures**) | **[SPEC_README_OPERATOR_SECTIONS.md](SPEC_README_OPERATOR_SECTIONS.md)**; **§ Backlog `23e2da29`** |
| Optional **`docs/reference-documentation/`** workflow (**RD1**–**RD8** pytest) | **[SPEC_REFERENCE_DOCUMENTATION.md](SPEC_REFERENCE_DOCUMENTATION.md)**; **§ Backlog `eb884da9`**; **`tests/test_reference_documentation_workflow.py`** |
| Subprocess **`python -m`** reference server + loopback POST (**SUB1**–**SUB8**) | **[SPEC_HTTP_SERVER_ENTRYPOINT.md](SPEC_HTTP_SERVER_ENTRYPOINT.md)** (**S9**); **§ Backlog `83e07114`** below |

## CI entrypoint (invariant)

- **Project convention:** contributors and docs refer to:

  ```bash
  pytest tests -q
  ```

- **CI** (`.github/workflows/ci.yml`) may invoke the same suite as  
  `python -m pytest tests -q` plus optional flags (for example `--tb=short`). That is **equivalent** for acceptance as long
  as it collects **only** tests under **`tests/`** and does not require **outbound** or **public** network I/O for the
  signing / parsing / handler unit tests mandated in the specs above. **Loopback HTTP** to a **child process** started by
  the test suite (backlog **`83e07114`**, rows **SUB1**–**SUB8**) is **allowed** and is **not** an “extra service” as
  long as it uses **`127.0.0.1`** / **`localhost`** only and needs no Docker, databases, or remote endpoints.

- **Do not** change the workflow to a different test root or drop **`tests/`** without updating this document,
  **README.md**, and **CHANGELOG.md**.

- **Ruff** (**`ruff check`**, **`ruff format --check`**) is specified under **§ Backlog `5a3f5a7f`** and implemented in
  **`.github/workflows/ci.yml`** (**`lint`** job). **Removing** or **weakening** those steps requires updating this
  document, **README.md** (if contributor commands change), and **CHANGELOG.md** when the change is user-visible to
  contributors.

## Prohibited patterns

- **No placeholder “smoke” module** whose **only** behavioral assertion is **`assert True`** (or an empty **`pass`**) while
  claiming the package is covered. If **`tests/test_smoke.py`** (or similar) still exists after focused modules cover
  **§ Minimum behavioral coverage** below, **delete** it or merge any unique scenario into a properly named test module.
- **Do not** rely on a single no-op test so **`pytest`** “passes” without exercising verification or parsing paths.

## Minimum behavioral coverage

The suite **must** include **network-free** **pytest** tests that fail when the following regress:

1. **Signature verification** — Exercises **`verify_lifecycle_webhook_signature`** (and, if the optional handler is in
   scope, the same rules through **`handle_lifecycle_webhook_post`** where **SPEC_MINIMAL_HTTP_HANDLER** already requires
   it). At minimum, outcomes aligned with **SPEC_WEBHOOK_SIGNATURE** checklist **W3** (valid MAC, wrong secret, tampered
   body, missing or malformed **`Replayt-Signature`**). Existing coverage is expected under **`tests/test_webhook_signature.py`**
   (and related handler tests per **H** rows).
2. **JSON parsing / lifecycle events** — Exercises **`parse_lifecycle_webhook_event`** on representative payloads and on
   invalid or unknown shapes so validation regressions fail. Align with **EVENTS.md** rows **T3–T5** (fixtures, invalid
   **`detail`**, unknown **`event_type`**, missing required envelope fields). When **SPEC_DELIVERY_IDEMPOTENCY** **I3**/**I4**
   apply, the same module also holds duplicate-delivery fixture checks and the signed duplicate-**POST** dedupe pattern.
   Existing coverage is expected under **`tests/test_lifecycle_events.py`** and **`tests/fixtures/events/`**.
3. **Replayt boundary (dependency seam)** — At least one module **imports `replayt`** and asserts **documented** public
   symbols (**`RunResult`**, **`RunFailed`**, **`ApprovalPending`**) per **[SPEC_REPLAYT_BOUNDARY_TESTS.md](SPEC_REPLAYT_BOUNDARY_TESTS.md)**.
   This is **in addition to** items **1** and **2**, not a substitute. Existing **`tests/test_replayt_dependency.py`** work
   counts toward the **version / pyproject** story only when combined with those **import** checks (same module or a
   dedicated **`tests/test_replayt_boundary.py`**).

Other modules (**mission** doc anchors, **replayt** dependency doc checks, and so on) may coexist; they do **not** replace
items **1**–**3**.

4. **Public export surface** — Package root **`replayt_lifecycle_webhooks.__all__`** and **`replayt_lifecycle_webhooks.events.__all__`**
   match **[SPEC_PUBLIC_API.md](SPEC_PUBLIC_API.md)** § **Supported import paths** (same names as the normative table);
   documented **internal** module paths in § **Unsupported imports** remain importable. See backlog **`30e133a5`** below.
   This item does **not** replace items **1**–**3**.

When **[SPEC_HTTP_SERVER_ENTRYPOINT.md](SPEC_HTTP_SERVER_ENTRYPOINT.md)** is implemented, the suite **must** additionally
include **network-free** tests that fail if the documented **POST** webhook path or **`GET /health`** (or the spec-chosen
health path) regresses per checklist **S3**, **S4**, and **S6** in that document. Those tests **must not** replace items
**1**–**3**.

When backlog **`83e07114`** is implemented, the suite **must** additionally include at least one test module satisfying
**SUB1**–**SUB8** below (**subprocess** + **loopback HTTP**). That harness **complements** **S3**/**S4**/**S6** (in-process
WSGI): it catches **argv**, **environment**, **`wsgiref`**, and **real `-m`** wiring regressions operators would see. It
**must not** replace items **1**–**3** or the in-process **S** rows.

When **[SPEC_LOCAL_WEBHOOK_DEMO.md](SPEC_LOCAL_WEBHOOK_DEMO.md)** is implemented, the suite **must** additionally include
**network-free** tests that satisfy checklist **D3**, **D7**, and **D8** in that document (signing agrees with
**`verify_lifecycle_webhook_signature`**; non-success HTTP maps to non-zero exit or equivalent tested behavior). Those
tests **must not** replace items **1**–**3**.

When **[SPEC_STRUCTURED_LOGGING_REDACTION.md](SPEC_STRUCTURED_LOGGING_REDACTION.md)** is implemented, the suite **must**
additionally include **network-free** tests that satisfy checklist **L1–L9** under **Backlog `fa75ecf3`** below. Those
tests **must not** replace items **1**–**3**.

When **[SPEC_REPLAY_PROTECTION.md](SPEC_REPLAY_PROTECTION.md)** is implemented, the suite **must** additionally include
**network-free** tests that satisfy **RP4** and **RP5** under **Backlog `f9677140`** below (**RP5** may alias **I4**).
Those tests **must not** replace items **1**–**3**.

When **[SPEC_EVENT_DIGEST.md](SPEC_EVENT_DIGEST.md)** ships formatters in-tree, the suite **must** additionally include
**network-free** tests that satisfy **DG1**–**DG6** under **Backlog `069e0240`** below. Those tests **must not** replace
items **1**–**3**.

Backlog **`23e2da29`** (**[SPEC_README_OPERATOR_SECTIONS.md](SPEC_README_OPERATOR_SECTIONS.md)**) is covered by **network-free**
**pytest** rows **OP1**–**OP8** under **Backlog `23e2da29`** below (**`tests/test_readme_operator_sections.py`**). Those
tests **must not** replace items **1**–**4** in **§ Minimum behavioral coverage**.

Backlog **`dc212184`** (**[SPEC_REVERSE_PROXY_REFERENCE_SERVER.md](SPEC_REVERSE_PROXY_REFERENCE_SERVER.md)**) is covered by **network-free**
**pytest** rows **OG1**–**OG8** under **Backlog `dc212184`** below (**`tests/test_operator_reverse_proxy_doc.py`**). Those
tests **must not** replace items **1**–**4** in **§ Minimum behavioral coverage**.

## Acceptance criteria (checklist)

Use for Spec gate, Builder, and Tester sign-off for backlog **`a91574f0`**. Rows **R1–R5** in
**[SPEC_REPLAYT_BOUNDARY_TESTS.md](SPEC_REPLAYT_BOUNDARY_TESTS.md)** cover backlog **`d9d6b302`**.

| # | Criterion | Verification |
|---|-----------|--------------|
| A1 | No **`tests/`** file is the **only** “package works” story via **`assert True`** / empty **`pass`** alone; remove or replace **`tests/test_smoke.py`** when redundant. | Code review; **`rg 'assert True' tests`** |
| A2 | **pytest** exercises **`verify_lifecycle_webhook_signature`** for success and representative failures (**W3** family). | **`pytest tests -q`**; review **`tests/test_webhook_signature.py`** |
| A3 | **pytest** exercises **`parse_lifecycle_webhook_event`** (or the handler’s verify-then-parse path) on valid and invalid lifecycle JSON per **EVENTS.md** **T3–T5**. | **`pytest tests -q`**; review **`tests/test_lifecycle_events.py`** / fixtures |
| A4 | CI runs **`pytest tests -q`** or **`python -m pytest tests -q`** (optional extra flags) against **`tests/`**. | Review **`.github/workflows/ci.yml`** |
| A5 | Doc or contract changes to the CI command or minimum coverage appear under **CHANGELOG.md** **Unreleased** when user-visible to contributors. | Release hygiene |

## Backlog `2b4c6927`: smoke replacement and module imports

Checklist rows for **Replace scaffold smoke test with real unit and boundary tests**
(`2b4c6927-573a-463c-b59f-f2f91dfb6381`). These extend **A1–A5**; they do not replace **A1–A5** or the **replayt**
boundary rows **R1–R5**.

| # | Criterion | Verification |
|---|-----------|--------------|
| A6 | At least one **golden vector**: fixed UTF-8 secret, fixed raw body bytes, and a **committed** `Replayt-Signature` value (`sha256=…`) checked by **`verify_lifecycle_webhook_signature`** without reusing ad-hoc signing helpers for that vector. | **`tests/test_webhook_signature.py`** — **`test_golden_vector_committed_replayt_signature`** |
| A7 | Invalid JSON after a good signature maps to the handler contract (**H4**). | **`tests/test_http_handler.py`** — **`test_h4_bad_json_400_after_good_signature`** |
| A8 | Unknown **`event_type`** is rejected during parsing (**T4** family). | **`tests/test_lifecycle_events.py`** — **`test_parse_rejects_unknown_event_type`** |
| A9 | After verify, the success path invokes the caller hook (**H7**). | **`tests/test_http_handler.py`** — **`test_on_success_called_after_verify`** |
| A10 | Tests **`import`** **`replayt_lifecycle_webhooks.signature`**, **`replayt_lifecycle_webhooks.handler`**, and **`replayt_lifecycle_webhooks.events`** directly (not only the package root), and exercise **`replayt_lifecycle_webhooks.serve`** where the reference server is in tree. | Search **`tests/`**; **`tests/test_reference_server.py`** for **serve** |

## Backlog `4280c054`: delivery idempotency (`event_id`)

Checklist rows for **Specify idempotency and replay-safe delivery semantics**
(`4280c054-4193-4754-8e4c-1da320975fac`). Normative contract: **[SPEC_DELIVERY_IDEMPOTENCY.md](SPEC_DELIVERY_IDEMPOTENCY.md)**.
These extend **A1–A5** and lifecycle coverage in **§ Minimum behavioral coverage** item **2**; they do not replace **R1–R5**.

| # | Criterion | Verification |
|---|-----------|--------------|
| I3 | Fixtures include a byte-identical duplicate-delivery pair with the same **`event_id`**; distinct logical emissions in fixtures use distinct **`event_id`** values. | **`tests/test_lifecycle_events.py`**; **`tests/fixtures/events/run_started.json`** and **`run_started_redelivery.json`** |
| I4 | Two **`handle_lifecycle_webhook_post`** calls with the same verified body and signature do not double integrator side effects when **`on_success`** dedupes on **`event_id`**. | **`tests/test_lifecycle_events.py`** — **`test_i4_duplicate_signed_post_idempotent_side_effects_pattern`** |

## Backlog `f9677140`: replay protection and idempotency hooks

Checklist rows for **Add replay protection and idempotency hooks for deliveries**
(`f9677140-0803-41c7-9d1c-82fc85f25f8d`). Normative contract: **[SPEC_REPLAY_PROTECTION.md](SPEC_REPLAY_PROTECTION.md)**.
These extend **A1–A5** and **§ Minimum behavioral coverage** item **2**; they do not replace **W** rows, **H1–H12**, or
**R1–R5**. **RP5** is satisfied by **I4** while that test remains the duplicate-delivery proof; **RP4** requires a
**distinct** stale-**`occurred_at`** / replay scenario once implemented.

| # | Criterion | Verification |
|---|-----------|--------------|
| RP4 | At least one **network-free** test: valid MAC, parsed payload, **`occurred_at`** outside configured freshness window → **`replay_rejected`** (or equivalent) and **no** spurious side effects. | **`tests/test_replay_protection.py`** — **`test_rp4_stale_occurred_at_valid_mac_replay_rejected_no_on_success`**; **`tests/test_http_handler.py`** — **`test_h8_error_messages_match_failure_response_spec`** (**`replay_rejected`** copy) |
| RP5 | At least one **network-free** test: same **`event_id`** delivered twice with valid MACs → idempotent side effects. | **`tests/test_lifecycle_events.py`** — **`test_i4_duplicate_signed_post_idempotent_side_effects_pattern`**; **`tests/test_replay_protection.py`** — **`test_rp5_dedup_store_second_post_204_without_on_success`** |

## Backlog `fa75ecf3`: structured logging and redaction

Checklist rows for **Add structured logging helper that redacts sensitive keys by default**
(`fa75ecf3-a113-418e-99cc-aa0c31237eba`) and **Establish structured logging and redaction for webhook handling**
(`6ea52b2b-ff96-4511-a9f8-d5d9ed6d3711`). Normative API and defaults: **[SPEC_STRUCTURED_LOGGING_REDACTION.md](SPEC_STRUCTURED_LOGGING_REDACTION.md)**.
These extend **A1–A5**; they do not replace **A1–A5** or **R1–R5**.

| # | Criterion | Verification |
|---|-----------|--------------|
| L1 | **`REDACTED_PLACEHOLDER`** is exactly **`[REDACTED]`** (ASCII) per spec. | Unit test asserts constant or equivalent public re-export. |
| L2 | **`redact_headers`** returns a **new** mapping; **`Authorization`** value (e.g. **`Bearer <secret>`**) is replaced and the **secret substring** does not appear in the redacted dict’s values. | Unit test |
| L3 | **`redact_headers`** redacts **`Replayt-Signature`** (case-insensitive name) to **`[REDACTED]`**. | Unit test |
| L4 | **`redact_headers`** redacts names matching the **`X-Signature`** **prefix** rule (e.g. **`X-Signature-Custom`**). | Unit test |
| L5 | **`extra_sensitive_names`** causes a **non-default** header (e.g. **`X-Internal-Token`**) to be redacted. | Unit test |
| L6 | **`redact_mapping`** performs **shallow** redaction for at least one default sensitive key (e.g. **`token`**, **`secret`**, or **`api_key`**) and preserves non-sensitive keys unchanged. | Unit test |
| L7 | **`extra_sensitive_keys`** causes a **non-default** mapping key to be redacted (lowercase comparison per spec). | Unit test |
| L8 | At least one test uses **`caplog`**, a **`logging.Handler`**, or equivalent to capture formatted log output showing **`[REDACTED]`** for sensitive fields and **asserting the absence** of a representative **high-entropy secret substring** (for example a fake bearer token) in the captured text. | Unit test (e.g. **`tests/test_redaction.py`** or module name aligned with implementation) |
| L9 | **Successful verified delivery** (**HTTP 204** path): captured log text **must not** contain a distinctive raw body substring from a request fixture (proving default logging does not echo the POST body). **`extra`** from **`format_safe_webhook_log_extra`** **must** include **`webhook_status_code`** **204**, **`webhook_headers`** with sensitive names redacted when headers were passed, **`webhook_body_bytes_len`**, and **`lifecycle_*`** keys per **§ Example: successful verified delivery** in **SPEC_STRUCTURED_LOGGING_REDACTION** (omit **`lifecycle_approval_request_id`** when absent). | **`tests/test_redaction.py`** — **`test_l9_success_verified_delivery_no_raw_body_in_logs`** |

## Backlog `069e0240`: PM/support event digest format

Checklist rows for **Publish PM- and support-friendly event digest format**
(`069e0240-54c5-44a9-bba3-ad0a80a52c60`). Normative contract: **[SPEC_EVENT_DIGEST.md](SPEC_EVENT_DIGEST.md)**.
These extend **§ Minimum behavioral coverage** item **2** (parse first, then digest); they do not replace **A1–A5**,
**A6–A10**, **R1–R5**, or items **1**–**3**.

| # | Criterion | Verification |
|---|-----------|--------------|
| **DG1** | Documented **text** line rules cover **all six** **`event_type`** values (**SPEC_EVENT_DIGEST** + **EVENTS.md** registry). | **`tests/test_event_digest.py`** — first-line parametrized cases |
| **DG2** | At least **two** worked **text** examples (**run** and **approval**) match **SPEC_EVENT_DIGEST** **Worked examples** exactly; third **run.failed** example matches. | **`tests/test_event_digest.py`** — golden string equality after **`parse_lifecycle_webhook_event`** |
| **DG3** | **Determinism:** fixed parsed model → stable digest text (no trailing **`\\n`**) and stable canonical JSON record bytes (**DG0**). | **`tests/test_event_digest.py`** — **`test_dg3_digest_text_and_record_are_deterministic`** |
| **DG4** | Optional fields omit lines / record keys when absent. | **`tests/test_event_digest.py`** — **`test_dg4_optional_lines_omitted_when_fields_absent`** |
| **DG5** | **`approval.resolved`** uses **Approval approved** vs **Approval rejected** first line per **`detail.decision`**. | **`tests/test_event_digest.py`** — **`test_dg5_approval_resolved_rejected_digest_line`** and parametrized **DG1** rows |
| **DG6** | External-sharing caution appears in integrator docs (**README** / **EVENTS.md**), as required by **SPEC_EVENT_DIGEST**. | **`tests/test_event_digest.py`** — **`test_dg6_integrator_docs_mention_external_sharing_caution`** |

## Backlog `30e133a5`: public API surface and deprecation policy

Checklist rows for **Define public API surface and deprecation policy before 1.0**
(`30e133a5-78fa-4eee-ae56-56a1af4c9f73`). Normative contract: **[SPEC_PUBLIC_API.md](SPEC_PUBLIC_API.md)**.
These extend **§ Minimum behavioral coverage** item **4**; they do not replace **A1–A5**, **A6–A10**, **R1–R5**, or items **1**–**3**.

| ID | Criterion | Verification |
| -- | --------- | ------------ |
| **API1** | Package root **`__all__`** is **exactly** the public names in **SPEC_PUBLIC_API** § **Primary: package root** (table), in **table order**. | **`tests/test_public_api.py`** — **`test_package_root___all___matches_spec_table`**; **`test_package_root___all___names_are_importable`** |
| **API1** (events) | **`replayt_lifecycle_webhooks.events`** **`__all__`** matches the **Events / parsing** row in **that row’s order** (same symbols as re-exported from the root). | **`tests/test_public_api.py`** — **`test_events___all___matches_spec_events_row`** |
| **API2** | **SPEC_PUBLIC_API** § **Unsupported imports** module paths exist (internal until **1.0**). | **`tests/test_public_api.py`** — **`test_spec_lists_documented_internal_modules_as_importable`** |
| **API3** | **SPEC_PUBLIC_API** § **Deprecation policy** documents **CHANGELOG** visibility (**Deprecated**), **minor** / **0.x** notice period, and related bullets. | **`tests/test_public_api.py`** — **`test_spec_public_api_deprecation_policy_mentions_changelog_and_notice`** |

## Backlog `5a3f5a7f`: **ruff** in CI (lint and optional format)

Checklist rows for **Run ruff in CI for fast style and lint feedback**
(`5a3f5a7f-d54a-4f8a-a446-e71b932d22c5`). These extend **A1–A5**; they do not replace **pytest** coverage, **R1–R5**, or
items **1**–**4** in **§ Minimum behavioral coverage**.

**Workflow surface:** The repository’s primary GitHub Actions workflow is **`.github/workflows/ci.yml`**, which already
runs on **push** and **pull_request** for **`master`** and **`mc/**`** (and **`workflow_dispatch`**). **RF1** applies to
that file unless the project adds another workflow that is also required for merges to **`master`** / **`mc/**`**—if so,
**every** such workflow must run the same **ruff** gates (or the spec and **CHANGELOG.md** must record a deliberate
exception).

**Scope on disk:** **`ruff check`** must cover Python sources the project maintains for this package—at minimum
**`src/`** and **`tests/`** (and any other tracked project Python at the repo root the maintainer group treats as
in-scope). Prefer repository-root discovery via **`pyproject.toml`** / Ruff defaults; use **`[tool.ruff]`**
**`extend-exclude`** only with a short comment or spec note when excluding generated or third-party trees.

**Install posture:** The workflow must use a **ruff** compatible with **`[project.optional-dependencies] dev`** (for
example after **`pip install -e ".[dev]"`**, or by installing **ruff** with a pin that satisfies the same lower bound).
Do **not** rely on a system **ruff** with an unknown version.

**Runtime / structure:** Keep wall-clock cost low—acceptable patterns include (a) a **dedicated parallel job** that only
installs **ruff** (or **dev** extras) and runs **ruff**, or (b) **steps** appended to the existing **`test`** job after
**dev** dependencies are installed. **Supply-chain-only** jobs do **not** need **ruff** if the **lint**/**test** job still
runs on the same triggers and fails the workflow.

| # | Criterion | Verification |
|---|-----------|--------------|
| **RF1** | CI runs **`ruff check`** (non-zero exit on violations) on pushes and pull requests targeting **`master`** or **`mc/**`**, using **`.github/workflows/ci.yml`** (and any other merge-blocking workflow on those branches, if added later). | **`tests/test_ci_ruff_wiring.py`**; review **`.github/workflows/ci.yml`**; optional CI log from a branch that violates **ruff** |
| **RF2** | Optional but **recommended:** CI also runs **`ruff format --check`** with the same install posture and trigger surface as **RF1**. If maintainers omit it initially, note that under **CHANGELOG.md** **Unreleased** (**Documentation** or **Changed**) so the gap is explicit. | **`tests/test_ci_ruff_wiring.py`**; review workflow + **CHANGELOG.md** |
| **RF3** | **`pyproject.toml`** contains a minimal **`[tool.ruff]`** section **when** Ruff defaults are insufficient for this tree (for example **`target-version`** alignment with **`requires-python`**, **`line-length`**, or **`extend-exclude`** for generated paths). If defaults are sufficient, the section may be absent; the **Builder** commit message or **CHANGELOG** should make that choice obvious to reviewers. | Review **`pyproject.toml`** |
| **RF4** | **README.md** documents local **`ruff check`** in at least one line (for example near **Running tests**). If **`ruff format --check`** is enabled in CI, mention **`ruff format`** for contributors too. There is no **CONTRIBUTING.md** today; adding one is optional as long as **README.md** satisfies this row. | Doc review |
| **RF5** | Wiring **ruff** into CI is recorded under **CHANGELOG.md** **Unreleased** when the change is user-visible to contributors (typical **Added** or **Changed**). | Release hygiene |

## Backlog `23e2da29`: README operator sections

Checklist rows for **Expand README with operator troubleshooting and approval-flow walkthrough**
(`23e2da29-8042-4721-a1eb-e44a2076273f`). Normative contract:
**[SPEC_README_OPERATOR_SECTIONS.md](SPEC_README_OPERATOR_SECTIONS.md)**. These extend **A1**–**A5**; they do not replace
signature, parsing, boundary, or public-API coverage.

Implement **network-free** **`README.md`** text assertions (read from repo root). Prefer small helpers that slice the file
between consecutive **`## `** headings so each row scopes content to the right section.

| # | Criterion | Verification |
|---|-----------|--------------|
| **OP1** | **`README.md`** contains heading **`## Troubleshooting`** (exact line). | **`pytest`** — e.g. **`tests/test_readme_operator_sections.py`** |
| **OP2** | **`README.md`** contains heading **`## Approval webhook flow`** (exact line). | **`pytest`** (same module) |
| **OP3** | **`README.md`** contains heading **`## Verifying webhook signatures`** (exact line). | **`pytest`** (same module) |
| **OP4** | Under **Troubleshooting**, prose links **`docs/SPEC_WEBHOOK_FAILURE_RESPONSES.md`** (error catalog). | **`pytest`** |
| **OP5** | Under **Approval webhook flow**, prose mentions both **`replayt.lifecycle.approval.pending`** and **`replayt.lifecycle.approval.resolved`**. | **`pytest`** |
| **OP6** | Under **Approval webhook flow**, prose links **`docs/EVENTS.md`**. | **`pytest`** |
| **OP7** | Under **Verifying webhook signatures**, prose links **`docs/SPEC_WEBHOOK_SIGNATURE.md`** with fragment **`#verification-procedure-integrators`** (substring match). | **`pytest`** |
| **OP8** | Under **Verifying webhook signatures**, prose mentions **`verify_lifecycle_webhook_signature`** **or** **`replayt_lifecycle_webhooks.demo_webhook`** / **`python -m replayt_lifecycle_webhooks.demo_webhook`** (local verify path). | **`pytest`** |

## Backlog `dc212184`: operator reverse-proxy guide

Checklist rows for **Operator guide: reverse proxy in front of reference WSGI server**
(`dc212184-8c0d-4ee6-90de-e0d50c370f6f`). Normative contract:
**[SPEC_REVERSE_PROXY_REFERENCE_SERVER.md](SPEC_REVERSE_PROXY_REFERENCE_SERVER.md)**. These extend **A1**–**A5**; they do not
replace signature, parsing, boundary, or public-API coverage.

Implement **network-free** assertions by reading **`docs/OPERATOR_REVERSE_PROXY.md`** and **`README.md`** from disk (same
pattern as **OP1**–**OP8**). **Builder** may use a dedicated module (for example **`tests/test_operator_reverse_proxy_doc.py`**)
or extend an existing README doc-guard module if maintainers prefer one file—**Tester** ensures all **OG** rows are covered.

| # | Criterion | Verification |
|---|-----------|--------------|
| **OG1** | **`docs/OPERATOR_REVERSE_PROXY.md`** exists; level-1 heading matches **SPEC_REVERSE_PROXY_REFERENCE_SERVER** **§ Deliverable** intent (reverse proxy / TLS + reference server context). | **`pytest`** |
| **OG2** | Prose links **`docs/SPEC_WEBHOOK_SIGNATURE.md`** and addresses **raw body** / signature discipline. | **`pytest`** |
| **OG3** | Documents **client max body size** (or the chosen proxy’s equivalent directive name) with operator-facing rationale. | **`pytest`** |
| **OG4** | Documents **timeouts** and links **`docs/SPEC_DELIVERY_IDEMPOTENCY.md`**. | **`pytest`** |
| **OG5** | Mentions **`Transfer-Encoding`** and/or **chunked** buffering risk to **byte-identical** verification (per spec wording). | **`pytest`** |
| **OG6** | Contains a fenced **nginx** or **Caddy** block; a **comment inside that block** references **`docs/SPEC_WEBHOOK_SIGNATURE.md`** and/or **`SPEC_WEBHOOK_SIGNATURE`**. | **`pytest`** |
| **OG7** | Callout against logging full bodies / secrets / full signatures; links **`docs/SPEC_STRUCTURED_LOGGING_REDACTION.md`**. | **`pytest`** |
| **OG8** | Root **`README.md`** links **`docs/OPERATOR_REVERSE_PROXY.md`** under **`## Troubleshooting`** or **`## Verifying webhook signatures`** (per **SPEC_README_OPERATOR_SECTIONS**). | **`pytest`** |

## Backlog `eb884da9`: optional reference-documentation snapshot workflow

Checklist rows for **Add optional reference-documentation snapshot workflow**
(`eb884da9-5273-4ce0-b105-5130c6b1ac79`). The same workflow is refined under Mission Control backlog
**`2db687f4-23d2-4aff-8827-c3da11cdf283`** (refinement: licensing, documented snapshot commands, repo-size prose in
**SPEC_REFERENCE_DOCUMENTATION**; **§ Backlog acceptance mapping** maps Mission Control acceptance bullets to **RD1**–**RD8**).
Normative contract:
**[SPEC_REFERENCE_DOCUMENTATION.md](SPEC_REFERENCE_DOCUMENTATION.md)**. Rows **RD1**–**RD8** below are **documentation /
workflow** acceptance enforced by **`pytest`** (not a substitute for signature, parsing, boundary, or **pytest** minima in
**§ Minimum behavioral coverage**).

| # | Criterion | Verification |
|---|-----------|--------------|
| **RD1** | **`docs/reference-documentation/README.md`** explains optional use, committed vs **`_upstream_snapshot/`** content, and links **SPEC_REFERENCE_DOCUMENTATION**. | **`pytest`** — **`tests/test_reference_documentation_workflow.py`** |
| **RD2** | Root **`README.md`** **Reference documentation (optional)** links the folder **README**, **SPEC_REFERENCE_DOCUMENTATION**, and describes refresh (manual **and/or** optional **`scripts/`**). | **`pytest`** (same module) |
| **RD3** | **`.gitignore`** contains **`docs/reference-documentation/_upstream_snapshot/`**; **`git check-ignore`** honors the rule. | **`pytest`** (same module) |
| **RD4** | **CI** does not require downloading or mirroring a large upstream documentation tree into **`docs/reference-documentation/`**. | **`pytest`** (same module; **`.github/workflows/ci.yml`** must not mention **`reference-documentation`**) |
| **RD5** | This file (**SPEC_AUTOMATED_TESTS**) traces backlog **`eb884da9`** and **RD1**–**RD8** (this table). | **`pytest`** (same module) |
| **RD6** | Each committed **`docs/reference-documentation/*.md`** except **`README.md`** includes **`## Source and licensing`** with **provenance** and **license** or **attribution** language. | **`pytest`** (same module) |
| **RD7** | **SPEC_REFERENCE_DOCUMENTATION** **§ Repeatable snapshot commands** documents **git**, **curl**, and **rsync** (or equivalent) toward **`_upstream_snapshot/`**. | **`pytest`** (same module) |
| **RD8** | Root **`README.md`** **Reference documentation (optional)** and/or **`CONTRIBUTING.md`** **Reference documentation snapshots** states **when** to refresh, **small** default clone expectations, and **`_upstream_snapshot/`** as **gitignore**/**gitignored** bulk storage. | **`pytest`** (same module) |

## Backlog `83e07114`: subprocess reference server integration (`python -m`)

Checklist rows for **Integration test: subprocess POST against `python -m` reference server**
(`83e07114-fbec-46ab-9944-d2aa3bca0024`). Normative server CLI and routes:
**[SPEC_HTTP_SERVER_ENTRYPOINT.md](SPEC_HTTP_SERVER_ENTRYPOINT.md)**. These **complement** in-process **S3**/**S4**/**S6**
in **`tests/test_reference_server.py`**; they do **not** replace **A1**–**A5**, **R1**–**R5**, or **§ Minimum behavioral
coverage** items **1**–**4**.

**Scope:** **Tests only**; production code changes are **out of scope** unless minimally required for testability (for
example a bug that prevents binding or health checks). Prefer **no** server changes: the parent test process **should**
choose a free TCP port (for example bind **`127.0.0.1:0`** in the parent, read the assigned port, pass **`--port`** to the
child) so the child does not need to print an OS-assigned port when **`--port 0`** is used.

| # | Criterion | Verification |
|---|-----------|--------------|
| **SUB1** | Starts the **real** package entrypoint with **`sys.executable -m replayt_lifecycle_webhooks`** (no importing **`__main__`** as a shortcut for the spawn alone—may import helpers for assertions). Passes **`--host 127.0.0.1`** (or the spec default host if it remains loopback-only) and **`--port <chosen>`** where **`<chosen>`** is a free port on the runner. Sets **`REPLAYT_LIFECYCLE_WEBHOOK_SECRET`** in the **child** environment to a **non-empty** test secret (fixed string is fine). | **`pytest`**; module e.g. **`tests/test_reference_server_subprocess.py`** or an agreed split under **`tests/`** |
| **SUB2** | Waits until **`GET /health`** on the child’s base URL returns **HTTP 200** within a **bounded** timeout (poll loop or equivalent); treats non-200 or connection errors as failure after the timeout. | **`pytest`** (same module) |
| **SUB3** | Sends **POST** to the configured webhook path (default **`/webhook`** per **SPEC_HTTP_SERVER_ENTRYPOINT**) with **raw body bytes** from a **committed** lifecycle fixture under **`tests/fixtures/events/`** (or the same JSON bytes as an existing golden test) and a correct **`Replayt-Signature`** header (**`sha256=…`**) computed with **`compute_lifecycle_webhook_signature_header`** or the same HMAC rule as **`verify_lifecycle_webhook_signature`**. | **`pytest`** (same module) |
| **SUB4** | Asserts the webhook **POST** response is **2xx** on the success path (expected **`204 No Content`** per **SPEC_MINIMAL_HTTP_HANDLER** / reference wiring). | **`pytest`** (same module) |
| **SUB5** | **Teardown** is reliable on **Linux CI**: terminate the child (for example **`terminate()`** then **`kill()`** / **`wait()`** with timeouts), close any client connections, and avoid leaving a listening socket behind across tests (flaky follow-on tests are a failure). | Code review; repeated **`pytest`** runs locally optional |
| **SUB6** | **CI posture:** passes on **`ubuntu-latest`** (or the project’s canonical Linux CI image) **without** Docker, systemd user services, or other **extra** daemons—only the spawned **`python`** process and loopback HTTP. | **`.github/workflows/ci.yml`** + green run |
| **SUB7** | If the test is marked **`@pytest.mark.slow`** or conditionally skipped, **this document** states the fact under this table (reason: wall-clock, platform, and so on) and **either** (a) default **`pytest tests -q`** / CI still collects it, **or** (b) CI runs an explicit command that includes the marker (for example **`pytest tests -q -m slow`**) so the subprocess harness is **not** silently dropped. **Preferred default:** keep it in the main collection if runtime stays small. | Doc + workflow review |
| **SUB8** | **`README.md`** (**Running tests**) **or** this section names the module (or marker) contributors use to run only this integration test when debugging (**`pytest … <path> -q`** or **`-k`** / **`-m`** as implemented). | **`README.md`** **Running tests** → **`pytest tests/test_reference_server_subprocess.py -q`** |

## Related docs

- **[README.md](../README.md)** — quick start; see **Running tests** for the canonical command.
- **[MISSION.md](MISSION.md)** — success metrics and alignment with what CI runs.
- **[DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)** — observable automation and explicit contracts.
- **[SPEC_REPLAYT_BOUNDARY_TESTS.md](SPEC_REPLAYT_BOUNDARY_TESTS.md)** — **`replayt`** import and documented symbol checks.
- **[SPEC_DELIVERY_IDEMPOTENCY.md](SPEC_DELIVERY_IDEMPOTENCY.md)** — at-least-once delivery, **`event_id`** dedupe, **I3**/**I4** tests.
- **[SPEC_REPLAY_PROTECTION.md](SPEC_REPLAY_PROTECTION.md)** — freshness, dedupe store, **RP4**/**RP5** (overlaps **I4** for duplicates).
- **[SPEC_STRUCTURED_LOGGING_REDACTION.md](SPEC_STRUCTURED_LOGGING_REDACTION.md)** — redaction defaults, public API, **L1–L9**.
- **[SPEC_EVENT_DIGEST.md](SPEC_EVENT_DIGEST.md)** — digest text, **`digest/1`** record, **DG1**–**DG6**.
- **[SPEC_README_OPERATOR_SECTIONS.md](SPEC_README_OPERATOR_SECTIONS.md)** — README operator sections, **OP1**–**OP8**.
- **[SPEC_REVERSE_PROXY_REFERENCE_SERVER.md](SPEC_REVERSE_PROXY_REFERENCE_SERVER.md)** — operator reverse-proxy guide, **OG1**–**OG8**.
- **[SPEC_REFERENCE_DOCUMENTATION.md](SPEC_REFERENCE_DOCUMENTATION.md)** — optional **`docs/reference-documentation/`** workflow, **RD1**–**RD8**.
