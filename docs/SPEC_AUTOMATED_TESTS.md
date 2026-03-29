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
- Add replayt dependency declaration and compatibility matrix stub (`8b16060d-f6e6-4111-bed2-4978b965ff52`) — **SPEC_REPLAYT_DEPENDENCY** matrix (**Python** / CI-tested columns), **A8**, stub checklist when **`replayt`** is absent from **`pyproject.toml`**. Rows **A9**–**A10** (CI Python floor) are backlog **`6cd22a7b`**.

- Run **ruff** in CI for fast lint (and optionally format) feedback (`5a3f5a7f-d54a-4f8a-a446-e71b932d22c5`) — checklist **RF1**–**RF5** under **Backlog `5a3f5a7f`** below.
- Optional **pre-commit** mirroring CI **ruff** invocations (`c39b2a5f-a2f5-42a4-a5c2-a2b20989a31c`) — checklist **PC1**–**PC7** under **Backlog `c39b2a5f`** below.
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
- Optional structured diagnostics on **serve** / **handler** paths using **`redaction`** helpers
  (`0bab43f3-cb59-40ff-96c3-31fb2703cfb0`) — checklist **LG1–LG4** under **§ Backlog `0bab43f3`** below; normative
  contract **[SPEC_STRUCTURED_LOGGING_REDACTION.md](SPEC_STRUCTURED_LOGGING_REDACTION.md)** (**§ Optional diagnostic
  logging**); reference server rows **S10**–**S12** in **[SPEC_HTTP_SERVER_ENTRYPOINT.md](SPEC_HTTP_SERVER_ENTRYPOINT.md)**.
- **SDist / wheel build + `twine check`** in CI (`78e3554b-2b50-4918-9859-85642ac1a84a`) — checklist **PK1**–**PK7** under
  **§ Backlog `78e3554b`** below; normative **distribution contract** (package data; **`py.typed`** via **`78e3554b`** + **`2ec2c21c`**) in those
  sections.
- Property-based fuzzing for **`parse_lifecycle_webhook_event`** and signature verification
  (`dcffe5d5-7f7c-4585-aca0-a882653f20dd`) — checklist **PF1**–**PF10** under **§ Backlog `dcffe5d5`** below.
- **`pip-audit`** suppression alignment and review dates (`bea2900c-17e9-4bf8-9623-0830105386a2`) — checklist **PI1**–**PI7**
  under **§ Backlog `bea2900c`** below; normative parsing and governance rules in
  **[SPEC_PIP_AUDIT_SUPPRESSION_ALIGNMENT.md](SPEC_PIP_AUDIT_SUPPRESSION_ALIGNMENT.md)**.
- **CI: run pytest and ruff on Python 3.11 (minimum supported)** (`6cd22a7b-72bc-4d34-ba7c-a6878b68907d`) — checklist **CI1**–**CI6**
  under **§ Backlog `6cd22a7b`** below; compatibility matrix and **A9**–**A10** in **[SPEC_REPLAYT_DEPENDENCY.md](SPEC_REPLAYT_DEPENDENCY.md)**.
- **CI: expand Python interpreter matrix beyond 3.12** (`8e58aa9c-0d62-4649-852a-766babcd8218`) — checklist **PYM1**–**PYM7**
  under **§ Backlog `8e58aa9c`** below; **SPEC_REPLAYT_DEPENDENCY** **§ CI** ( **`8e58aa9c`** bullets) and checklist **A11**–**A14**.
- Reference HTTP server **route / HTTP status** matrix for gateways (`b4c68e50-04df-4149-b9b5-f5d6280b38cc`) —
  checklist **RM1**–**RM7** in **[SPEC_REFERENCE_HTTP_SERVER_ROUTE_MAP.md](SPEC_REFERENCE_HTTP_SERVER_ROUTE_MAP.md)** (**RM1**–**RM4**:
  **`tests/test_reference_http_server_route_map_doc.py`**);
  **README** link rule in **[SPEC_README_OPERATOR_SECTIONS.md](SPEC_README_OPERATOR_SECTIONS.md)**; **SPEC_HTTP_SERVER_ENTRYPOINT**
  **S13**.
- **PEP 561 `py.typed` in distributions + optional static typing gate** (`2ec2c21c-1107-4eb7-b5e4-b250f75cabeb`) —
  checklist **TP1**–**TP6** under **§ Backlog `2ec2c21c`** below; integrator expectations in
  **[SPEC_PUBLIC_API.md](SPEC_PUBLIC_API.md)** (**§ Static typing (PEP 561)**).

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
| Reference HTTP server entrypoint (**S1–S13**), when implemented | **[SPEC_HTTP_SERVER_ENTRYPOINT.md](SPEC_HTTP_SERVER_ENTRYPOINT.md)** |
| Reference server **HTTP surface** matrix for gateways (**RM1**–**RM7**), documentation | **[SPEC_REFERENCE_HTTP_SERVER_ROUTE_MAP.md](SPEC_REFERENCE_HTTP_SERVER_ROUTE_MAP.md)**; **§ Backlog `b4c68e50`** below |
| Operator reverse-proxy guide (**OG1–OG8**) | **[SPEC_REVERSE_PROXY_REFERENCE_SERVER.md](SPEC_REVERSE_PROXY_REFERENCE_SERVER.md)**; **§ Backlog `dc212184`** |
| Local signed demo POST (**D1–D9**), when implemented | **[SPEC_LOCAL_WEBHOOK_DEMO.md](SPEC_LOCAL_WEBHOOK_DEMO.md)** |
| Lifecycle JSON shapes and typed parsing (**E***, **T***) | **[EVENTS.md](EVENTS.md)** |
| Lifecycle event digest text and **`digest/1`** record (**DG1**–**DG6**) | **[SPEC_EVENT_DIGEST.md](SPEC_EVENT_DIGEST.md)** |
| **`event_id`** duplicate fixtures and handler dedupe patterns (**I3**, **I4**) | **[SPEC_DELIVERY_IDEMPOTENCY.md](SPEC_DELIVERY_IDEMPOTENCY.md)** |
| Replay / freshness vs duplicate delivery (**RP4**, **RP5**) | **[SPEC_REPLAY_PROTECTION.md](SPEC_REPLAY_PROTECTION.md)** |
| **replayt** dependency / doc contract (**A1**–**A10**, matrix **Python** + CI) | **[SPEC_REPLAYT_DEPENDENCY.md](SPEC_REPLAYT_DEPENDENCY.md)** |
| **`replayt` import / API stability at the dependency seam** | **[SPEC_REPLAYT_BOUNDARY_TESTS.md](SPEC_REPLAYT_BOUNDARY_TESTS.md)** |
| **This package’s supported exports** (`__all__`, import paths, CLI **`-m`**, deprecation) | **[SPEC_PUBLIC_API.md](SPEC_PUBLIC_API.md)** |
| Structured logging + redaction (**L1–L9**), when implemented | **[SPEC_STRUCTURED_LOGGING_REDACTION.md](SPEC_STRUCTURED_LOGGING_REDACTION.md)** |
| Optional **serve** / **handler** diagnostic logging + redaction (**LG1–LG4**), when implemented | **[SPEC_STRUCTURED_LOGGING_REDACTION.md](SPEC_STRUCTURED_LOGGING_REDACTION.md)** (**§ Optional diagnostic logging**); **[SPEC_HTTP_SERVER_ENTRYPOINT.md](SPEC_HTTP_SERVER_ENTRYPOINT.md)** (**S10**–**S12**) |
| **Ruff** lint (and optional format check) in CI | **§ Backlog `5a3f5a7f`** in this document |
| Optional **pre-commit** for local **ruff** (same argv / version floor as CI) | **§ Backlog `c39b2a5f`** in this document |
| README operator-facing sections (**Troubleshooting**, **Approval webhook flow**, **Verifying webhook signatures**) | **[SPEC_README_OPERATOR_SECTIONS.md](SPEC_README_OPERATOR_SECTIONS.md)**; **§ Backlog `23e2da29`** |
| Optional **`docs/reference-documentation/`** workflow (**RD1**–**RD8** pytest) | **[SPEC_REFERENCE_DOCUMENTATION.md](SPEC_REFERENCE_DOCUMENTATION.md)**; **§ Backlog `eb884da9`**; **`tests/test_reference_documentation_workflow.py`** |
| Subprocess **`python -m`** reference server + loopback POST (**SUB1**–**SUB8**) | **[SPEC_HTTP_SERVER_ENTRYPOINT.md](SPEC_HTTP_SERVER_ENTRYPOINT.md)** (**S9**); **§ Backlog `83e07114`** below |
| **SDist / wheel** build, **`twine check`**, declared package data, **`py.typed`** (**PEP 561**) | **§ Backlog `78e3554b`** (**PK1**–**PK7**) + **§ Backlog `2ec2c21c`** (**TP1**–**TP6**) |
| Optional **Hypothesis** fuzzing for verify + parse (no default install) | **§ Backlog `dcffe5d5`** below (**PF1**–**PF10**) |
| **`pip-audit --ignore-vuln`** alignment vs **`docs/DEPENDENCY_AUDIT.md`**, review due dates | **[SPEC_PIP_AUDIT_SUPPRESSION_ALIGNMENT.md](SPEC_PIP_AUDIT_SUPPRESSION_ALIGNMENT.md)**; **§ Backlog `bea2900c`** below (**PI1**–**PI7**) |

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

- **Python minors:** Merge-blocking **`test`** jobs **must** run that command (or equivalent) on **Python 3.11**, the
  **`requires-python` floor**, per **§ Backlog `6cd22a7b`** and **[SPEC_REPLAYT_DEPENDENCY.md](SPEC_REPLAYT_DEPENDENCY.md)** **§ CI** / **A9**.
  If the workflow uses a **matrix**, **every** leg that claims to satisfy **A9** must run the **full** **`test`** step list;
  optional **3.12** legs are **recommended** but not a substitute for **3.11**. Per **§ Backlog `8e58aa9c`**, merge-blocking
  **`lint`** and **`test`** **must** also include **3.13** so **`requires-python >=3.11`** is exercised above **3.12**—see
  **[SPEC_REPLAYT_DEPENDENCY.md](SPEC_REPLAYT_DEPENDENCY.md)** **§ CI** and checklist **PYM1**–**PYM2**.

- **Do not** change the workflow to a different test root or drop **`tests/`** without updating this document,
  **README.md**, and **CHANGELOG.md**.

- **Ruff** (**`ruff check`**, **`ruff format --check`**) is specified under **§ Backlog `5a3f5a7f`** and implemented in
  **`.github/workflows/ci.yml`** (**`lint`** job). **Removing** or **weakening** those steps requires updating this
  document, **README.md** (if contributor commands change), and **CHANGELOG.md** when the change is user-visible to
  contributors.

- **Optional pre-commit** (local only; **not** a merge gate) is specified under **§ Backlog `c39b2a5f`**. It must stay
  aligned with the **`lint`** job; it does **not** replace **RF1**/**RF2**.

- **`supply-chain`** (**`pip-audit`** after **`pip install -e ".[dev]"`**) is specified in **`.github/workflows/ci.yml`**.
  **§ Backlog `bea2900c`** is enforced by **`tests/test_pip_audit_suppression_alignment.py`** (**PI1**–**PI6**) and a
  **`supply-chain`** step that runs **`python scripts/pip_audit_suppression_alignment.py`** before **`pip-audit`** (**PI7**
  keeps the existing **`pip-audit`** invocation with **`--desc`**).

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

When backlog **`0bab43f3`** (optional **serve** / **handler** structured diagnostics) is implemented, the suite **must**
additionally include **network-free** tests that satisfy checklist **LG1–LG4** under **§ Backlog `0bab43f3`** below. Those
tests **must not** replace items **1**–**3**, **L1–L9**, or reference-server rows **S3**/**S4**/**S6**/**S9** where they
already apply.

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

**Optional** **Hypothesis**-backed tests (**PF1**–**PF10**) live under **§ Backlog `dcffe5d5`** below. They **complement**
**A2**, **A3**, and **§ Minimum behavioral coverage** items **1**–**2**; they **must not** replace them. Unless
**CHANGELOG.md** and this document record a deliberate policy change, **default** **`pytest tests -q`** and merge-blocking
**CI** **must** remain **green** on an install that does **not** include **Hypothesis** (skip, marker exclusion, or equivalent).

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

## Backlog `0bab43f3`: optional serve / handler structured diagnostics

Checklist rows for **Serve path: optional structured logging hook using `redaction` helpers**
(`0bab43f3-cb59-40ff-96c3-31fb2703cfb0`). Normative contract: **[SPEC_STRUCTURED_LOGGING_REDACTION.md](SPEC_STRUCTURED_LOGGING_REDACTION.md)**
**§ Optional diagnostic logging (serve and handler paths)**; reference server rows **S10**–**S12** in
**[SPEC_HTTP_SERVER_ENTRYPOINT.md](SPEC_HTTP_SERVER_ENTRYPOINT.md)**.

These extend **A1–A5** and, when **L1–L9** are active, complement them; they do **not** replace **L1–L9**, **A1–A5**, or
**R1–R5**. Tests **must** remain **network-free** (in-process **WSGI** / **`handle_lifecycle_webhook_post`** and/or
**`caplog`** against the reference app factory).

| # | Criterion | Verification |
|---|-----------|--------------|
| **LG1** | **Default off:** With diagnostics **disabled**, the suite **must not** observe **new** request-scoped structured log records attributable to this feature compared to the documented baseline (for example **no** records from the documented diagnostic logger(s) at **INFO** or below during representative **POST**/**GET** handling, or equivalent assertion defined by the implementation’s logging levels). | **`pytest`** (module name aligned with implementation, e.g. **`tests/test_serve_handler_logging.py`** or extension of **`tests/test_reference_server.py`**) |
| **LG2** | **Opt-in:** With diagnostics **enabled**, at least one test captures log output (**`caplog`**, handler, or formatted line) showing **`[REDACTED]`** (or **`REDACTED_PLACEHOLDER`**) for **`Authorization`** and **`Replayt-Signature`** on a representative request that includes **`Bearer <high-entropy-secret>`** and a valid signature header; the **secret substring** and full signature digest **must not** appear in captured text. | **`pytest`** (same module family) |
| **LG3** | **Opt-in success path:** Captured log text for a **204** success scenario **must not** contain a **distinctive** raw body substring present in the request fixture (same bar as **L9**—prove the **serve** / **handler** path does not echo the POST body). | **`pytest`** |
| **LG4** | **Traceability:** The test module (or **pytest** **docstring** on the class/module enforcing **LG1**–**LG3**) **must** name **SPEC_STRUCTURED_LOGGING_REDACTION** and **§ Optional diagnostic logging** so reviewers link proof to the normative contract. | Code review |

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

## Backlog `6cd22a7b`: CI Python minimum (**pytest** + **ruff**)

Checklist rows for **CI: run pytest and ruff on Python 3.11 (minimum supported)**
(`6cd22a7b-72bc-4d34-ba7c-a6878b68907d`). Normative matrix and job split (**`package`** / **`supply-chain`** single version):
**[SPEC_REPLAYT_DEPENDENCY.md](SPEC_REPLAYT_DEPENDENCY.md)** (**§ CI**, **A9**–**A10**). These rows extend **A4**, **RF1**–**RF2**,
and **PI7**’s workflow expectations; they do **not** replace **pytest** behavioral minima or **ruff** path coverage.

| # | Criterion | Verification |
|---|-----------|--------------|
| **CI1** | **`.github/workflows/ci.yml`** runs the existing **`lint`** job’s **ruff** steps (**`ruff check src tests`**, **`ruff format --check src tests`**) on **Python 3.11** at least once per trigger (matrix value or dedicated job). | Workflow YAML + CI logs |
| **CI2** | The **`test`** job runs **`python -m pytest tests -q`** (or documented equivalent) on **3.11** with the same **`pip install`** / **`pyproject.toml`** validation steps as today, at least once per trigger. | Workflow YAML + CI logs |
| **CI3** | **`[tool.ruff] target-version`** in **`pyproject.toml`** remains **`py311`** (or the same minor as **`requires-python` floor** if the floor moves in a future change). | **`pyproject.toml`** review |
| **CI4** | **`docs/SPEC_REPLAYT_DEPENDENCY.md`** **compatibility matrix** “CI-tested Python” column and **Notes** match the workflow (including **`package`** / **`supply-chain`** single interpreter). | Doc diff vs **`ci.yml`** |
| **CI5** | Any **`skip`**, **`xfail`**, **`pytest.mark.skipif`**, or **`importorskip`** tied to **`sys.version_info`** / **`platform.python_version()`** is documented in this file (**§ Interpreter-conditioned skips**) **or** in a **`Reason:`** / adjacent comment that names the backlog and the interpreter rule. | Code + doc review |
| **CI6** | **README** compatibility / CI prose matches the matrix (minimum **3.11** exercised for **lint**/**test**). | **`README.md`** review |

**Builder note:** **`tests/test_ci_ruff_wiring.py`** asserts **`3.11`** under **`lint`** and **`test`** (and **`3.12`**, **`3.13`**) so CI cannot regress **CI1**/**PYM1**–**PYM2** silently. **`tests/test_replayt_dependency.py`** cross-checks the same matrix against **README** and **SPEC_REPLAYT_DEPENDENCY** (**A8**, **PYM4**–**PYM5**).

### Interpreter-conditioned skips

There are **no** interpreter-version **xfail**/**skip** markers in the suite at the time this section was added. If a
future test must diverge by CPython minor (for example a **stdlib** or **typing** difference), **prefer** fixing the
implementation for all supported minors. If a skip is unavoidable, add **CI5** documentation here (one row per marker or
group) and keep **[SPEC_REPLAYT_DEPENDENCY.md](SPEC_REPLAYT_DEPENDENCY.md)** truthful about what “full **pytest**” means.

## Backlog `8e58aa9c`: CI Python matrix beyond 3.12 (**ruff** + **pytest**)

Checklist rows for **CI: expand Python interpreter matrix beyond 3.12**
(`8e58aa9c-0d62-4649-852a-766babcd8218`). Normative workflow rules and matrix checklist **A11**–**A14**:
**[SPEC_REPLAYT_DEPENDENCY.md](SPEC_REPLAYT_DEPENDENCY.md)** (**§ CI**, **Compatibility matrix** **Notes**). These rows extend
**CI1**–**CI6**, **A4**, **RF1**–**RF2**, and **CI4**/**CI6**; they do **not** relax the **`requires-python` floor** requirement
from backlog **`6cd22a7b`**.

| # | Criterion | Verification |
|---|-----------|--------------|
| **PYM1** | **`lint`** job **`strategy.matrix.python-version`** includes **`3.13`** and still includes **`3.11`** and **`3.12`**. | **`.github/workflows/ci.yml`** + CI logs |
| **PYM2** | **`test`** job matrix includes the same three minors (**`3.11`**, **`3.12`**, **`3.13`**) with the same **`setup-python`** wiring pattern as today. | **`.github/workflows/ci.yml`** + CI logs |
| **PYM3** | Each **`lint`** matrix leg runs **`ruff check src tests`** and **`ruff format --check src tests`**; each **`test`** leg runs the full install + **`python -m pytest tests -q`** (or documented equivalent) + existing **`test`** prerequisites—**no** reduced “smoke only” subset on **3.13**. | Workflow YAML + CI logs |
| **PYM4** | **`docs/SPEC_REPLAYT_DEPENDENCY.md`** **compatibility matrix** **CI-tested Python** column lists **3.11**, **3.12**, and **3.13** for **`lint`** + **`test`**, and **Notes** stay consistent with **`package`** / **`supply-chain`** single-interpreter jobs. | Doc diff vs **`ci.yml`** |
| **PYM5** | **`README.md`** and **`CONTRIBUTING.md`** sentences that name CI Python matrix minors match **`.github/workflows/ci.yml`** (including **3.13**). | Doc review |
| **PYM6** | Any **`skip`**, **`xfail`**, **`pytest.mark.skipif`**, or **`importorskip`** that depends on **3.13** vs other minors satisfies **CI5** (this **§ Interpreter-conditioned skips** table or adjacent **`Reason:`** / workflow comment naming **`8e58aa9c`**). | Code + this document |
| **PYM7** | Contributor-visible CI matrix expansion is recorded under **`CHANGELOG.md`** **Unreleased** (**Changed** or **Documentation**). | **`CHANGELOG.md`** review |

**Builder note:** Phase **3** (backlog **`8e58aa9c`**) added **`3.13`** assertions alongside **`6cd22a7b`** guards in **`tests/test_ci_ruff_wiring.py`** and **`tests/test_replayt_dependency.py`**.

## Backlog `5a3f5a7f`: **ruff** in CI (lint and optional format)

Checklist rows for **Run ruff in CI for fast style and lint feedback**
(`5a3f5a7f-d54a-4f8a-a446-e71b932d22c5`). These extend **A1–A5**; they do not replace **pytest** coverage, **R1–R5**, or
items **1**–**4** in **§ Minimum behavioral coverage**.

**Workflow surface:** The repository’s primary GitHub Actions workflow is **`.github/workflows/ci.yml`**, which already
runs on **push** and **pull_request** for **`master`** and **`mc/**`** (and **`workflow_dispatch`**). **RF1** applies to
that file unless the project adds another workflow that is also required for merges to **`master`** / **`mc/**`**—if so,
**every** such workflow must run the same **ruff** gates (or the spec and **CHANGELOG.md** must record a deliberate
exception). When backlog **`6cd22a7b`** is implemented, **RF1**/**RF2** apply to **each** merge-blocking **`lint`** matrix
leg that satisfies **[SPEC_REPLAYT_DEPENDENCY.md](SPEC_REPLAYT_DEPENDENCY.md)** **A9** (including **3.11**). When backlog
**`8e58aa9c`** is implemented, **RF1**/**RF2** also apply to the **`3.13`** **`lint`** legs (**PYM1**, **PYM3**).

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
| **RF4** | **README.md** documents local **`ruff check`** in at least one line (for example near **Running tests**). If **`ruff format --check`** is enabled in CI, mention **`ruff format`** for contributors too. **CONTRIBUTING.md** may link or defer to **README.md** for **`ruff`** commands as long as contributors can discover them from the repo root docs. When backlog **`c39b2a5f`** ships, **CONTRIBUTING.md** must also meet **PC1**–**PC7** (**§ Backlog `c39b2a5f`**). | Doc review |
| **RF5** | Wiring **ruff** into CI is recorded under **CHANGELOG.md** **Unreleased** when the change is user-visible to contributors (typical **Added** or **Changed**). | Release hygiene |

## Backlog `c39b2a5f`: optional **pre-commit** mirroring CI **ruff**

Checklist rows for **CONTRIBUTING: optional pre-commit config mirroring Ruff CI commands**
(`c39b2a5f-a2f5-42a4-a5c2-a2b20989a31c`). These **extend** **RF1**–**RF5** (local ergonomics only); they do **not** add a
new CI gate or change the merge-blocking **ruff** story unless **maintainers** explicitly adopt **`pre-commit`** in
workflows (out of scope for this backlog).

**Authoritative invocation** (must stay in sync with **`.github/workflows/ci.yml`** **`lint`** job unless this spec and
**CHANGELOG.md** record a deliberate change):

1. **`pip install "ruff>=0.6.0"`** (CI install step; local **pre-commit** must use **ruff** satisfying the same lower
   bound—see **PC2**).
2. **`ruff check src tests`**
3. **`ruff format --check src tests`**

**Deliverable shape:** **Preferred:** committed **`.pre-commit-config.yaml`** at the repository root. **Acceptable
alternative:** **CONTRIBUTING.md** contains a **copy-paste** fenced **YAML** block under a dedicated heading so
contributors can create **`.pre-commit-config.yaml`** locally without committing it; prose must warn that the snippet
must stay aligned with **§ Authoritative invocation** above (same **`src` `tests`** path list and format **check**, not
auto-format-on-commit, unless maintainers later choose otherwise in **CI** first).

**Hook semantics:** Any **ruff format** step wired through **pre-commit** must be **check-only** (**`--check`** or
equivalent) so local hooks match CI (**`ruff format --check`**) and do not silently rewrite files unless the project
first changes CI to allow auto-format (which would require updating **RF2**, this section, and **CHANGELOG.md**).

| # | Criterion | Verification |
|---|-----------|--------------|
| **PC1** | **`.pre-commit-config.yaml`** exists at repo root **or** **CONTRIBUTING.md** provides an equivalent snippet (see **Deliverable shape**). The configured hooks, taken together, run the equivalent of **`ruff check src tests`** and **`ruff format --check src tests`** (same path arguments as the **`lint`** job **Ruff check** / **Ruff format** steps). | Doc review; optional **`pytest`** on YAML / **CONTRIBUTING** text (**Builder** / **Tester** discretion) |
| **PC2** | **Ruff** version policy matches CI and **`pyproject.toml`** **`[project.optional-dependencies] dev`**: the hook environment installs **ruff** satisfying **`ruff>=0.6.0`**. If using **`astral-sh/ruff-pre-commit`**, **`rev:`** must point to a tag whose bundled **ruff** meets that bound; **CONTRIBUTING** or a YAML comment must instruct maintainers to raise **`rev:`** when the CI/dev lower bound increases. | Doc review; compare **`rev:`** / **`additional_dependencies`** to **`ci.yml`** and **`pyproject.toml`** |
| **PC3** | **CONTRIBUTING.md** documents installing **`pre-commit`** (for example **`pip install pre-commit`** or **dev** extra if the project adds it—**do not** make **`pre-commit`** a runtime dependency of the package) and running **`pre-commit install`** so hooks run on commit. | Doc review |
| **PC4** | **CONTRIBUTING.md** states that **pre-commit** is **optional** and that contributors may submit changes without installing hooks (drive-by patches); **RF1**/**RF2** remain enforced by **GitHub Actions**. | Doc review |
| **PC5** | **CONTRIBUTING.md** names **`.github/workflows/ci.yml`** (**`lint`** job) as the **source of truth** for **ruff** commands and version floor, so prose does not drift from CI. Duplicating the exact shell lines is allowed **only** alongside that link or as a short quote labeled as mirroring CI. | Doc review |
| **PC6** | **CI invariant:** **`.github/workflows/ci.yml`** does **not** gain a required step that runs **`pre-commit run`** as a substitute for the existing **`ruff`** steps; the **`lint`** job keeps the **`pip install "ruff>=0.6.0"`** + **`ruff check`** + **`ruff format --check`** pattern (or its documented successor). | Review workflow diff |
| **PC7** | When the feature ships, **CHANGELOG.md** **Unreleased** notes the optional **pre-commit** path for contributors (**Added** or **Changed**, per project convention). | Release hygiene |

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

## Backlog `b4c68e50`: reference HTTP server route / status matrix (documentation)

Checklist rows for **Docs: machine-readable route/status map for the reference HTTP server**
(`b4c68e50-04df-4149-b9b5-f5d6280b38cc`). **Normative contract:**
**[SPEC_REFERENCE_HTTP_SERVER_ROUTE_MAP.md](SPEC_REFERENCE_HTTP_SERVER_ROUTE_MAP.md)**. **README** placement rule:
**[SPEC_README_OPERATOR_SECTIONS.md](SPEC_README_OPERATOR_SECTIONS.md)** (**§ Reference server route map link**). **Traceability**
on the entrypoint spec: **S13** in **[SPEC_HTTP_SERVER_ENTRYPOINT.md](SPEC_HTTP_SERVER_ENTRYPOINT.md)**.

**Scope:** **Documentation only**—no new Python runtime API. **Verification:** **RM5**–**RM7** remain **documentation review**.
**RM1**–**RM4** are also enforced by **`tests/test_reference_http_server_route_map_doc.py`** (phase **3** builder).

| # | Criterion | Verification |
|---|-----------|--------------|
| **RM1** | Canonical **Markdown** table includes **`POST /webhook`** and **`GET /health`**. | **`pytest`** **`tests/test_reference_http_server_route_map_doc.py`**; doc review |
| **RM2** | Table documents default **bind host**, **port**, and **`/webhook`** path consistent with **SPEC_HTTP_SERVER_ENTRYPOINT** and **`replayt_lifecycle_webhooks.serve`** defaults. | **`pytest`** (same module); doc review |
| **RM3** | Table links **SPEC_WEBHOOK_FAILURE_RESPONSES** and **SPEC_WEBHOOK_SIGNATURE** for webhook errors and signing policy. | **`pytest`** (same module); doc review |
| **RM4** | **`README.md`** links **`docs/SPEC_REFERENCE_HTTP_SERVER_ROUTE_MAP.md`**. | **`pytest`** (same module); doc review |
| **RM5** | **SPEC_README_OPERATOR_SECTIONS** records the backlog mapping and README requirement. | Doc review |
| **RM6** | **SPEC_HTTP_SERVER_ENTRYPOINT** and **SPEC_AUTOMATED_TESTS** (this section) reference the route map for discoverability. | Doc review |
| **RM7** | **No new runtime API** beyond documentation and cross-links. | Doc review |

## Backlog `78e3554b`: sdist / wheel build and `twine check` (CI)

Checklist rows for **CI: `python -m build` + `twine check` on sdist/wheel**
(`78e3554b-2b50-4918-9859-85642ac1a84a`). **Scope:** CI wiring + verification steps + contributor docs; **no** change to
runtime library behavior except what packaging already implies. **`py.typed`** was **optional** under **PK6** alone until backlog
**`2ec2c21c`** shipped; that backlog makes the marker **mandatory** and extends verification (**TP1**–**TP3**).

**Normative distribution contract (this repository today):**

- **`[tool.setuptools.package-data]`** in **`pyproject.toml`** declares JSON under
  **`replayt_lifecycle_webhooks/fixtures/events/*.json`**. Those files **must** ship inside both the **wheel** and the
  **sdist** produced by **`python -m build`**. **PK5** enforces at least one representative file.
- **`py.typed`:** **TP1**–**TP3** require the committed marker under **`src/replayt_lifecycle_webhooks/`**, **`pyproject.toml`**
  package-data, and **pytest** proof in **both** **wheel** and **sdist** (**`tests/test_packaging_layout.py`**). **PK6** described
  the pre-**`2ec2c21c`** conditional rule; enforcement is **TP3** today.

**Workflow surface:** Prefer a **dedicated** job in **`.github/workflows/ci.yml`** (for example **`package`**) so **lint** /
**test** failures stay visually distinct from packaging failures. The job **must** use the same **push** / **pull_request**
branch filters as the existing **`lint`** and **`test`** jobs (**`master`**, **`mc/**`**), unless **CHANGELOG.md** and this
section document a deliberate exception.

**Install posture:** Use **`pip install build twine`** (or equivalent) with versions **pinned or lower-bounded** in the
workflow **or** documented in **`CONTRIBUTING.md`** so CI does not float on unpinned **`pip`** resolution. Adding
**`build`** / **`twine`** to **`[project.optional-dependencies] dev`** is **optional**; CI **must not** assume they are
already installed from **`pip install -e ".[dev]"`** unless **`pyproject.toml`** is updated accordingly.

| # | Criterion | Verification |
|---|-----------|--------------|
| **PK1** | CI runs a **packaging** job (or equivalent documented workflow) on **push** and **pull_request** for **`master`** and **`mc/**`**, consistent with **RF1**’s trigger story. | Review **`.github/workflows/ci.yml`** |
| **PK2** | The job installs **`build`** and **`twine`** before building. | Review workflow logs |
| **PK3** | The job runs **`python -m build`** from the **repository root** on a **clean** **`dist/`** directory (for example **`rm -rf dist`** immediately before the build step) so each run’s artifacts correspond only to the current tree. | Review workflow |
| **PK4** | The job runs **`twine check dist/*`** (or an equivalent that checks **every** artifact in **`dist/`** from that build). **Non-zero** exit on long-description / README / metadata issues **must** fail the workflow. | Review workflow; optional negative PR |
| **PK5** | **Package data:** After build, at least one **committed** JSON fixture that **`pyproject.toml`** claims under **`fixtures/events/`** (for example **`run_started.json`**) **must** be present inside the **wheel** at path prefix **`replayt_lifecycle_webhooks/fixtures/events/`** (wheels are zips—inspect members). The same file **must** appear inside the **sdist** archive under the setuptools layout (for example **`replayt_lifecycle_webhooks-*/src/replayt_lifecycle_webhooks/fixtures/events/`** or the layout **`build`** emits for this backend—assert by **`tar`**/path list, not by guessing intermediate temp dirs). | Workflow step **or** **`pytest`** module dedicated to packaging layout |
| **PK6** | **`py.typed`:** Historical **conditional** rule before **`2ec2c21c`**. With **TP1**–**TP3** implemented, the marker **must** exist and the **wheel** and **sdist** **must** include **`replayt_lifecycle_webhooks/py.typed`**—see **TP3** for the normative **pytest** bar. | Source tree + **`tests/test_packaging_layout.py`** |
| **PK7** | **`CONTRIBUTING.md`** documents the **same** local commands (clean **`dist/`**, **`python -m build`**, **`twine check dist/*`**) **or** explicitly points to this section as the canonical copy-paste block. | Doc review |

**Equivalence:** **`python -m build`** (no extra flags) is the **default** normative command. **`python -m build --sdist --wheel`** is an acceptable **documented** equivalent if maintainers prefer explicit formats.

## Backlog `2ec2c21c`: PEP 561 `py.typed` and optional static typing gate

Checklist rows for **Packaging: ship `py.typed` and optional static typing gate**
(`2ec2c21c-1107-4eb7-b5e4-b250f75cabeb`). **Scope:** packaging metadata + CI/docs verification; **no** runtime semantic
changes to verification or HTTP behavior. **Normative integrator contract:** **[SPEC_PUBLIC_API.md](SPEC_PUBLIC_API.md)**
(**§ Static typing (PEP 561)**).

**Relationship to `78e3554b`:** **PK1**–**PK5** and **PK7** unchanged. **PK6**’s conditional story is **closed** (**TP1** requires
the marker). **TP3** extends **`tests/test_packaging_layout.py`** so **`py.typed`** is proven in **both** wheel and **sdist**, not only the wheel.

| # | Criterion | Verification |
|---|-----------|--------------|
| **TP1** | An **empty** **PEP 561** marker file **`src/replayt_lifecycle_webhooks/py.typed`** is committed (zero-byte file is valid). | Source tree review |
| **TP2** | **`pyproject.toml`** declares the marker as **package data** for **`replayt_lifecycle_webhooks`** (extend **`[tool.setuptools.package-data]`** or use a **setuptools**-equivalent hook documented in the PR) so **`python -m build`** includes **`py.typed`** in the **wheel** and **sdist** layouts—same posture as **`fixtures/events/*.json`**. | **`pyproject.toml`** + build inspection |
| **TP3** | **`pytest`** asserts **`replayt_lifecycle_webhooks/py.typed`** is a member of the built **wheel** (zip) **and** that the **sdist** tarball contains a file path ending with **`replayt_lifecycle_webhooks/py.typed`** (same listing style as **PK5**, tolerant of intermediate directory prefixes). Update or replace **`test_built_wheel_includes_py_typed_when_present_in_source`** so the marker is **required**, not conditional. | **`tests/test_packaging_layout.py`** (or agreed module); **`pip install -e ".[dev]"`** |
| **TP4** | **Optional** static typing gate: implement **at least one** of: (a) a **non-merge-blocking** GitHub Actions workflow (for example **`workflow_dispatch`** only, or a job that is **not** a **required** check on **`master`** PRs); (b) a **CONTRIBUTING.md** copy-paste block only (no CI). **Default `lint` / `test` / `package` jobs must not** start failing on **pyright** / **mypy** unless a **later** backlog promotes that. If the optional workflow is omitted, record the choice in the PR / **handoff**—no silent requirement. | Workflow review + **CONTRIBUTING.md** |
| **TP5** | When **TP4**(a) or **TP4**(b) runs a checker, use **pyright** **or** **mypy** (one tool per implementation—document which). Check an **allowlisted** small set of **`src/`** modules that cover the **supported public** import surface—**minimum:** **`replayt_lifecycle_webhooks/__init__.py`** and **`replayt_lifecycle_webhooks/events.py`**. **Internal** modules **may** stay out of the allowlist initially. Configuration **should** target **clear public API** issues (exported callables and types integrators use); suppressions for third-party / **replayt** seams are acceptable when documented next to the command. | Config file + doc snippet or workflow logs |
| **TP6** | **`CHANGELOG.md`** **Unreleased** gains an **Added** (preferred) or **Documentation** bullet stating **PEP 561** / **`py.typed`** shipment and the **typing posture** (what is type-checked vs best-effort—align with **SPEC_PUBLIC_API**). | Doc review |

**CI packaging job:** The existing **`package`** job (**PK3**) already runs **`python -m build`**. **TP3** remains **pytest**-driven so local contributors catch missing **`py.typed`** without relying on workflow log archaeology.

## Backlog `dcffe5d5`: property-based fuzzing (parse + signature)

Checklist rows for **Tests: property-based fuzzing for event parse and signature edge cases**
(`dcffe5d5-7f7c-4585-aca0-a882653f20dd`). **Scope:** tests + optional dependency metadata; **minimal** production code
changes only for **demonstrated** defects (crashes, unintended exception types). **Normative mapping** from verifier /
parser signals to HTTP JSON **`error`** codes (when the reference handler is in play): **[SPEC_WEBHOOK_FAILURE_RESPONSES.md](SPEC_WEBHOOK_FAILURE_RESPONSES.md)**
(**§ Fuzz / property tests**).

These extend **A2** / **A3** and **§ Minimum behavioral coverage** items **1**–**2**; they do **not** replace **A1**–**A5**,
**A6**–**A10**, **R1**–**R5**, or explicit fixture-driven cases under **EVENTS.md** **T3**–**T5**.

### Dependency and collection posture

| # | Criterion | Verification |
|---|-----------|--------------|
| **PF1** | **`pyproject.toml`** declares **Hypothesis** only under **`[project.optional-dependencies]`** (preferred: a dedicated extra, e.g. **`property`**, listing **`hypothesis>=6.0`** or a maintainer-chosen floor). **`pip install -e .`** **must not** install it. Bundling into **`dev`** is **acceptable** only if **PF3** still guarantees a **Hypothesis-free** default **CI** graph **or** CI uses an explicit **`-m`** / path filter that **never** collects these tests without the extra—**prefer** a dedicated extra so **`pip install -e ".[dev]"`** stays aligned with **ruff** / **pytest** without forcing fuzz deps. | **`pyproject.toml`**; **`pip install -e .`** dependency tree review |
| **PF2** | Register a **`pytest` marker** (name **`property_fuzz`**) in **`pyproject.toml`** **`[tool.pytest.ini_options] markers`** with a one-line description pointing to this section. **Every** Hypothesis-backed test in this backlog uses **`@pytest.mark.property_fuzz`**. | **`pytest --markers`**; code review |
| **PF3** | **Default** **`pytest tests -q`** passes **without** **Hypothesis** installed: use **`pytest.importorskip("hypothesis")`** (module or test scope), **`@pytest.mark.skipif`**, or CI **`addopts`** / workflow **`pytest -m "not property_fuzz"`**—**pick one** strategy, document it here and in **README.md** (**Running tests** → **Focused runs**). | Local **`pytest`** in a clean env; CI workflow review |
| **PF4** | **Documented opt-in command** for maintainers (copy-paste in this section **and** **README.md**): install the extra, then run **only** the marked suite, e.g. **`pip install -e ".[property]"`** (if the extra is named **`property`**) then **`pytest tests -m property_fuzz -q`**. | Doc review |

**PF3 implementation:** **`tests/test_property_fuzz_signature.py`** and **`tests/test_property_fuzz_parse.py`** call **`pytest.importorskip("hypothesis")`** at **module** import time so the whole module is skipped when **Hypothesis** is absent. **CI** installs **`[dev]`** only (not **`[property]`**), so the default graph stays **Hypothesis-free** while **`pytest tests -q`** remains green.

### Behavioral contracts (Hypothesis on)

Strategies **must** stay **finite** and **size-bounded** (depth, string length, collection sizes) so CI / local runs complete
predictably. Prefer **`hypothesis.strategies.recursive`** / **`dictionaries`** with **`max_size`** and **`text`**
**`max_size`** aligned with realistic POST bodies (tens of KiB at most unless a documented stress mode is separate).

| # | Criterion | Verification |
|---|-----------|--------------|
| **PF5** | **Signature:** For generated **`secret`** (**`text` / `binary`**, bounded), **`body: bytes`** (bounded length), and **`signature: str \| None`** (bounded string including empty / whitespace / random ASCII), **`verify_lifecycle_webhook_signature`** either returns **`None`** or raises **only** **`WebhookSignatureMissingError`**, **`WebhookSignatureFormatError`**, or **`WebhookSignatureMismatchError`** (from **`replayt_lifecycle_webhooks.signature`**). **No** other **`BaseException`** may propagate. | **`pytest`** — e.g. **`tests/test_property_fuzz_signature.py`** or agreed module name |
| **PF6** | **Parse:** For generated **`dict`** objects (JSON-object-shaped, bounded), **`parse_lifecycle_webhook_event`** either returns a **`LifecycleWebhookEvent`** union member per **EVENTS.md** or raises **only** **`pydantic.ValidationError`**. **No** other **`BaseException`** may propagate. | **`pytest`** (same module family or split file) |
| **PF7** | **Parse type guard:** At least one property or example table covers **`parse_lifecycle_webhook_event`** with **non-**`dict` **`data`** (**`TypeError`** only, per public docstring). | **`pytest`** |
| **PF8** | **Signing interop:** Whenever the strategy builds **`signature`** with **`compute_lifecycle_webhook_signature_header`** for the same **`secret`** and **`body`**, **`verify_lifecycle_webhook_signature`** **succeeds** (nested **`given`** / **`data.draw`** composite is fine). | **`pytest`** |
| **PF9** | **Handler (optional):** If tests call **`handle_lifecycle_webhook_post`** (or **`make_lifecycle_webhook_wsgi_app`**
  adapter) with generated wire inputs, outcomes **must** match **[SPEC_MINIMAL_HTTP_HANDLER.md](SPEC_MINIMAL_HTTP_HANDLER.md)**
  ordering and **[SPEC_WEBHOOK_FAILURE_RESPONSES.md](SPEC_WEBHOOK_FAILURE_RESPONSES.md)** stable **`error`** codes for the
  branches exercised (**no** **5xx** from malformed client data alone). This row is **optional** if the Builder limits fuzzing
  to **PF5**–**PF8** only—state the choice in the test module docstring. | **`pytest`**; code review |
| **PF10** | **Hypothesis settings:** Use explicit **`@settings`** (**`max_examples`** documented, **`deadline=None`** or a generous bound for CI CPU variance) so flakes are rare; avoid **`HealthCheck.all()`** suppression unless justified in a comment. | Code review |

### Contributor commands (normative examples)

Adjust the extra name if **`pyproject.toml`** uses something other than **`property`**:

```bash
pip install -e ".[property]"
pytest tests -m property_fuzz -q
```

Optional: run a single module while iterating:

```bash
pytest tests/test_property_fuzz_signature.py -q
pytest tests/test_property_fuzz_parse.py -q
```

## Backlog `bea2900c`: pip-audit suppression alignment and review reminders

Checklist rows for **Supply chain: automate pip-audit ignore review reminders**
(`bea2900c-17e9-4bf8-9623-0830105386a2`). **Normative contract:**
**[SPEC_PIP_AUDIT_SUPPRESSION_ALIGNMENT.md](SPEC_PIP_AUDIT_SUPPRESSION_ALIGNMENT.md)**. **Scope:** **CI** step(s), optional
**`scripts/`** helper, and **docs** only — **no** runtime **`src/`** API.

**Install graph:** The audited environment remains **`pip install -e ".[dev]"`** in the **`supply-chain`** job unless
**DEPENDENCY_AUDIT** documents a deliberate change; alignment checks read **disk** only (workflow + markdown), **no** network.

| # | Criterion | Verification |
|---|-----------|--------------|
| **PI1** | Extract suppression ids from the **`supply-chain`** job’s **`pip-audit`** **`run:`** per **SPEC_PIP_AUDIT_SUPPRESSION_ALIGNMENT** (**workflow extraction**). | **`pytest`** (preferred) or **CI** step with **non-zero** exit on parse errors |
| **PI2** | Extract suppression ids from **`docs/DEPENDENCY_AUDIT.md`** level-3 headings under **`## Accepted risks`** per **SPEC_PIP_AUDIT_SUPPRESSION_ALIGNMENT** (**markdown extraction**). | **`pytest`** or **CI** step |
| **PI3** | **Set equality:** workflow ids and documented ids match exactly; failures print **workflow-only** and **doc-only** lists. | **`pytest`** or **CI** step |
| **PI4** | **`docs/DEPENDENCY_AUDIT.md`** includes contributor steps for a new ignore (heading shape, link, rationale, **Next review**, CI flag). | Doc review |
| **PI5** | Each **Accepted risks** subsection includes **`Next review (UTC): YYYY-MM-DD`** (parseable). Missing or invalid dates **fail** the check. | **`pytest`** or **CI** step |
| **PI6** | If **Next review** is **strictly before** today’s UTC date, the check **fails** with the overdue CVE ids (maintainer renews or resolves in the same PR). | **`pytest`** or **CI** step |
| **PI7** | Default **`pip-audit`** invocation in **`supply-chain`** remains present with **`--desc`** (or a documented superset); alignment automation **must not** replace or skip it. | Workflow review |

**Implementation hints (non-normative):** a small **stdlib** Python module under **`scripts/`** invoked from **CI** and
**`pytest`** via **`subprocess`** keeps argv parsing consistent; alternatively **`pytest`** may parse files directly without
shelling out.

## Related docs

- **[README.md](../README.md)** — quick start; see **Running tests** for the canonical command.
- **[MISSION.md](MISSION.md)** — success metrics and alignment with what CI runs.
- **[DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)** — observable automation and explicit contracts.
- **[SPEC_REPLAYT_BOUNDARY_TESTS.md](SPEC_REPLAYT_BOUNDARY_TESTS.md)** — **`replayt`** import and documented symbol checks.
- **[SPEC_DELIVERY_IDEMPOTENCY.md](SPEC_DELIVERY_IDEMPOTENCY.md)** — at-least-once delivery, **`event_id`** dedupe, **I3**/**I4** tests.
- **[SPEC_REPLAY_PROTECTION.md](SPEC_REPLAY_PROTECTION.md)** — freshness, dedupe store, **RP4**/**RP5** (overlaps **I4** for duplicates).
- **[SPEC_STRUCTURED_LOGGING_REDACTION.md](SPEC_STRUCTURED_LOGGING_REDACTION.md)** — redaction defaults, public API, **L1–L9**;
  optional **serve** / **handler** diagnostics, **LG1–LG4** (**§ Optional diagnostic logging**).
- **[SPEC_EVENT_DIGEST.md](SPEC_EVENT_DIGEST.md)** — digest text, **`digest/1`** record, **DG1**–**DG6**.
- **[SPEC_README_OPERATOR_SECTIONS.md](SPEC_README_OPERATOR_SECTIONS.md)** — README operator sections, **OP1**–**OP8**.
- **[SPEC_REVERSE_PROXY_REFERENCE_SERVER.md](SPEC_REVERSE_PROXY_REFERENCE_SERVER.md)** — operator reverse-proxy guide, **OG1**–**OG8**.
- **[SPEC_REFERENCE_DOCUMENTATION.md](SPEC_REFERENCE_DOCUMENTATION.md)** — optional **`docs/reference-documentation/`** workflow, **RD1**–**RD8**.
- **`CONTRIBUTING.md`** — local **sdist** / **wheel** + **`twine check`** commands (**PK7**); **§ Backlog `78e3554b`** above is normative for CI acceptance; **§ Backlog `2ec2c21c`** for **`py.typed`** + optional typing commands.
- **[SPEC_PIP_AUDIT_SUPPRESSION_ALIGNMENT.md](SPEC_PIP_AUDIT_SUPPRESSION_ALIGNMENT.md)** — **`pip-audit`** ignore alignment and **Next review** rules (**PI1**–**PI7**).
