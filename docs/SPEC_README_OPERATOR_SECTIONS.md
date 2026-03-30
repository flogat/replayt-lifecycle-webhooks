# Spec: README operator sections (troubleshooting, approval path, signature checks)

**Backlog:** Expand README with operator troubleshooting and approval-flow walkthrough  
**Workflow id:** `23e2da29-8042-4721-a1eb-e44a2076273f` (phase **2** spec refinement; Builder implements **README.md** in phase **3**).

**Audience:** Spec gate (2b), Builder (3), Tester (4), operators, integrators.

## Purpose and normative status

This document is the **contract** for **integrator-facing** content in the repository root **`README.md`** that helps
**on-call operators** validate webhook configuration and understand **approval** lifecycle traffic at a high level.
It does **not** redefine **replayt** product semantics (when approvals fire upstream)—see **[EVENTS.md](EVENTS.md)** and
upstream documentation for payload meaning.

**Normative for Builder:** When this backlog is in scope, **`README.md`** **must** satisfy **§ Required sections** and
**§ Content requirements** below. **§ Automated acceptance** maps to **pytest** rows **OP1**–**OP9** in
**[SPEC_AUTOMATED_TESTS.md](SPEC_AUTOMATED_TESTS.md)** (**OP9** from backlog **`c631fe3f`**).

**Non-goals for README prose:** Full **generic** HTTP framework tutorials, enterprise runbooks, or copying entire normative specs into
the README—**link** to **[SPEC_WEBHOOK_SIGNATURE.md](SPEC_WEBHOOK_SIGNATURE.md)**,
**[SPEC_WEBHOOK_FAILURE_RESPONSES.md](SPEC_WEBHOOK_FAILURE_RESPONSES.md)**,
**[SPEC_STRUCTURED_LOGGING_REDACTION.md](SPEC_STRUCTURED_LOGGING_REDACTION.md)**,
**[SPEC_DELIVERY_IDEMPOTENCY.md](SPEC_DELIVERY_IDEMPOTENCY.md)**,
**[SPEC_REPLAY_PROTECTION.md](SPEC_REPLAY_PROTECTION.md)**,
**[SPEC_LOCAL_WEBHOOK_DEMO.md](SPEC_LOCAL_WEBHOOK_DEMO.md)**,
**[SPEC_REVERSE_PROXY_REFERENCE_SERVER.md](SPEC_REVERSE_PROXY_REFERENCE_SERVER.md)** / **`docs/OPERATOR_REVERSE_PROXY.md`**
instead of duplicating them verbatim. **Exception:** backlog **`c631fe3f`** requires a **short** pointer in **`## Verifying webhook signatures`** to the single normative ASGI recipe (**[SPEC_INTEGRATOR_ASGI_VERIFIED_FIRST.md](SPEC_INTEGRATOR_ASGI_VERIFIED_FIRST.md)**)—not a full tutorial in **`README.md`**.

## Backlog acceptance mapping (`23e2da29`)

| Source criterion | Where addressed in this spec |
| ---------------- | ---------------------------- |
| README **Troubleshooting** | **§ Required sections** — **Troubleshooting** |
| README **Approval flow** (high level) | **§ Required sections** — **Approval webhook flow** |
| README **Verify signatures** (copy-paste friendly) | **§ Required sections** — **Verifying webhook signatures** |
| No secrets in examples; placeholders | **§ Secrets and examples hygiene** |
| CHANGELOG **Unreleased** when user-visible README changes | **§ Release hygiene** |
| Verify signing locally; common misconfigurations; logs; error catalog | **§ Content requirements** |
| Optional sequence diagram (markdown) | **§ Content requirements** — **Approval webhook flow** |

## Backlog acceptance mapping (`dc212184`)

Cross-cutting README rule for **Operator guide: reverse proxy in front of reference WSGI server**
(`dc212184-8c0d-4ee6-90de-e0d50c370f6f`). Normative detail and **OG1**–**OG8** live in
**[SPEC_REVERSE_PROXY_REFERENCE_SERVER.md](SPEC_REVERSE_PROXY_REFERENCE_SERVER.md)**.

| Source criterion | Where addressed in this spec |
| ---------------- | ---------------------------- |
| README cross-link to operator reverse-proxy guide | **§ Content requirements** — **Reverse proxy operator guide link** |

## Backlog acceptance mapping (`b4c68e50`)

Cross-cutting README rule for **Docs: machine-readable route/status map for the reference HTTP server**
(`b4c68e50-04df-4149-b9b5-f5d6280b38cc`). Normative matrix and acceptance **RM1**–**RM7** live in
**[SPEC_REFERENCE_HTTP_SERVER_ROUTE_MAP.md](SPEC_REFERENCE_HTTP_SERVER_ROUTE_MAP.md)**.

| Source criterion | Where addressed in this spec |
| ---------------- | ---------------------------- |
| README cross-link to the route / status matrix | **§ Content requirements** — **Reference server route map link** |

## Backlog acceptance mapping (`87e7edae`)

Cross-cutting README rule for **SECURITY.md and coordinated disclosure process**
(`87e7edae-033d-45af-87fc-066fca51db96`). Normative policy and checklist **SC1**–**SC11** live in
**[SPEC_SECURITY_DISCLOSURE.md](SPEC_SECURITY_DISCLOSURE.md)**.

| Source criterion | Where addressed in this spec |
| ---------------- | ---------------------------- |
| README link to root **`SECURITY.md`** (GitHub security policy surface) | **§ Content requirements** — **Security reporting link** |

## Backlog acceptance mapping (`c631fe3f`)

Cross-cutting README rule for **Integrator recipe: FastAPI / Starlette verified-first handler**
(`c631fe3f-8a66-4a9d-a900-bab855860c7b`). Normative guide and checklist **AF1**–**AF7** live in
**[SPEC_INTEGRATOR_ASGI_VERIFIED_FIRST.md](SPEC_INTEGRATOR_ASGI_VERIFIED_FIRST.md)**.

| Source criterion | Where addressed in this spec |
| ---------------- | ---------------------------- |
| README cross-link to the ASGI verified-first recipe | **§ Content requirements** — **`## Verifying webhook signatures`** — **ASGI / FastAPI / Starlette recipe link** |

## Backlog acceptance mapping (`845b4b11`)

Cross-cutting README rule for **Support CLI: verify saved webhook (body file + signature header)**
(`845b4b11-847d-48cb-a9f3-e75f3e4862ef`). Normative CLI contract and checklist **VW1**–**VW8** live in
**[SPEC_CLI_VERIFY_SAVED_WEBHOOK.md](SPEC_CLI_VERIFY_SAVED_WEBHOOK.md)**.

| Source criterion | Where addressed in this spec |
| ---------------- | ---------------------------- |
| README documents the canonical **`python -m`** verify invocation and links **SPEC_CLI_VERIFY_SAVED_WEBHOOK** | **§ Content requirements** — **`## Verifying webhook signatures`** — include a **short** pointer (one command + link); **VW1** in **SPEC_AUTOMATED_TESTS** |

## Required sections (`README.md`)

Use these **exact markdown headings** (level-2 `## …`) so doc-guard tests and readers can rely on stable anchors:

| # | Heading | Role |
| - | ------- | ---- |
| 1 | `## Troubleshooting` | Fast diagnosis: misconfigurations, retries, replay vs duplicate, signature failures, pointers to logs and specs. |
| 2 | `## Approval webhook flow` | Short narrative of how **approval**-category deliveries fit consumer handling (verify-first, then parse); optional diagram. |
| 3 | `## Verifying webhook signatures` | Copy-paste friendly steps: local verification loop (env placeholder + library API and/or documented **`python -m`** demo), links to normative signing procedure. |

**Ordering:** **Troubleshooting** may appear **before** or **after** **Verifying webhook signatures** as long as all three
headings exist and **Approval webhook flow** is **adjacent** to the other operator-focused blocks (recommended order:
**Troubleshooting** → **Approval webhook flow** → **Verifying webhook signatures**, or **Verifying** first if the README
already groups “how to verify” near quick start—**Builder** chooses one contiguous operator block).

**Note:** If **`README.md`** already contains material under different headings (for example a combined section), **merge**
content and **rename** headings to match this spec in the **Builder** commit—doc guards (**OP1**–**OP3**) require the exact
strings above.

## Content requirements

### `## Troubleshooting`

The section **must**:

1. Call out **at least three** common misconfigurations from this list (paraphrase is fine):  
   **wrong or rotated shared secret**; **body not raw bytes** (parsed/mutated JSON before MAC); **header name or**
   **`Replayt-Signature`** format mistakes; **assuming exactly-once delivery** without **`event_id`** dedupe; **treating**
   **stale** payloads as safe because the MAC is valid.
2. Tell operators **where to look in logs**: structured **`extra=`** fields (**`webhook_*`**, **`lifecycle_*`**,
   **`error_code`**) and **redaction** expectations, with a link to
   **[SPEC_STRUCTURED_LOGGING_REDACTION.md](SPEC_STRUCTURED_LOGGING_REDACTION.md)** (not a dump of the full spec).
3. Link **[SPEC_WEBHOOK_FAILURE_RESPONSES.md](SPEC_WEBHOOK_FAILURE_RESPONSES.md)** as the **stable `error` code catalog**
   (HTTP + JSON) for verification and post-verify failures. When backlog **`70689a62`** (canonical examples) is in scope,
   **§ Troubleshooting** **should** also link anchor **`#canonical-end-to-end-examples`** on that file for copy-paste
   gateway / mock fixtures.
4. Cross-link **at least two** of: **[SPEC_DELIVERY_IDEMPOTENCY.md](SPEC_DELIVERY_IDEMPOTENCY.md)**,
   **[SPEC_REPLAY_PROTECTION.md](SPEC_REPLAY_PROTECTION.md)**,
   **[SPEC_WEBHOOK_SIGNATURE.md](SPEC_WEBHOOK_SIGNATURE.md)** for the matching symptom (duplicate delivery, replay policy,
   raw body discipline).

### Reverse proxy operator guide link (backlog `dc212184`)

When **[SPEC_REVERSE_PROXY_REFERENCE_SERVER.md](SPEC_REVERSE_PROXY_REFERENCE_SERVER.md)** is in scope (operator reverse
proxy guide backlog **`dc212184-8c0d-4ee6-90de-e0d50c370f6f`**), **`README.md`** **must** include a markdown link to
**`docs/OPERATOR_REVERSE_PROXY.md`** (path as written from the repository root) inside **`## Troubleshooting`** **or**
**`## Verifying webhook signatures`**. **Do not** paste full proxy configs into **`README.md`**—the guide file holds the
snippet.

### Reference server route map link (backlog `b4c68e50`)

When **[SPEC_REFERENCE_HTTP_SERVER_ROUTE_MAP.md](SPEC_REFERENCE_HTTP_SERVER_ROUTE_MAP.md)** is in scope (backlog
**`b4c68e50-04df-4149-b9b5-f5d6280b38cc`**), **`README.md`** **must** include a markdown link to
**`docs/SPEC_REFERENCE_HTTP_SERVER_ROUTE_MAP.md`** (path as written from the repository root) in the **Overview** quick-link
paragraph **or** inside **`## Troubleshooting`** or **`## Verifying webhook signatures`**. The linked spec holds the
canonical **path / method / HTTP status** table for the **`python -m replayt_lifecycle_webhooks`** listener; use it for
gateway policy, mocks, and allowlists instead of duplicating the full matrix in **`README.md`**.

### Security reporting link (backlog `87e7edae`)

When **[SPEC_SECURITY_DISCLOSURE.md](SPEC_SECURITY_DISCLOSURE.md)** is in scope (backlog
**`87e7edae-033d-45af-87fc-066fca51db96`**), **`README.md`** **must** include a markdown link to **`SECURITY.md`**
(repository root; target written as **`SECURITY.md`** or **`./SECURITY.md`** in the link) in the **Overview** paragraph
**or** inside **`## Troubleshooting`** **or** **`## Verifying webhook signatures`**, so **GitHub** readers and operators can
find the coordinated disclosure channel without opening **CONTRIBUTING.md**. Full policy text lives in **`SECURITY.md`**;
**do not** paste the entire reporting procedure into **`README.md`**.

### `## Approval webhook flow`

The section **must**:

1. State that **approval** and **run** deliveries share the same **verify-then-parse** bar (**`Replayt-Signature`** over
   **raw body** per **SPEC_WEBHOOK_SIGNATURE**).
2. Name the two approval **`event_type`** values from **[EVENTS.md](EVENTS.md)** (**`replayt.lifecycle.approval.pending`**
   and **`replayt.lifecycle.approval.resolved`**) and explain in plain language: **pending** = work blocked waiting for a
   decision; **resolved** = decision recorded (approved/rejected per payload **`detail`**—point at **EVENTS.md** for
   fields, without duplicating full tables).
3. Mention **`correlation.approval_request_id`** when discussing routing or support correlation (optional in envelope per
   **EVENTS.md**).
4. Clarify this package **does not** implement approval UI or policy—consumers act **after** verification.

**Optional (recommended):** A **Mermaid** or ASCII **sequence diagram** in markdown showing: **sender** → **HTTPS POST** →
**receiver verifies** → **parse JSON** → **idempotent handler** (and optionally **downstream ticket/notification**). Keep
diagrams **free of secrets** and **free of real signature hex** (use placeholders like `sha256=<redacted>` or omit the
value line).

### `## Verifying webhook signatures`

The section **must**:

1. Link the **Verification procedure (integrators)** subsection in
   **`docs/SPEC_WEBHOOK_SIGNATURE.md`** (anchor **`#verification-procedure-integrators`**), matching how other
   **`docs/…`** links are written from **`README.md`**.
2. Include a markdown link to **`docs/SPEC_CLI_VERIFY_SAVED_WEBHOOK.md`** and the **canonical** offline verify command
   (placeholders only for secrets and signature material) so operators can triage captured POSTs without ad-hoc scripts
   (**VW1**).
3. Include **copy-paste ready** examples that use **placeholders only** for secrets, for example
   **`your-shared-secret`** or **`REPLAYT_LIFECYCLE_WEBHOOK_SECRET`**—see **§ Secrets and examples hygiene**.
4. Show **at least one** of:  
   (a) a **minimal** **`verify_lifecycle_webhook_signature`** snippet (secret + raw **`bytes`** + header value variable), or  
   (b) the **documented local loop**: reference server + **`python -m replayt_lifecycle_webhooks.demo_webhook`** per
   **[SPEC_LOCAL_WEBHOOK_DEMO.md](SPEC_LOCAL_WEBHOOK_DEMO.md)** with env-based secret (no literal secret strings).

**Must not** include complete **`Replayt-Signature`** header values tied to real fixtures (no committed **64-char hex**
example posing as a live MAC) or **base64/raw key** material.

### ASGI / FastAPI / Starlette recipe link (backlog `c631fe3f`)

When **[SPEC_INTEGRATOR_ASGI_VERIFIED_FIRST.md](SPEC_INTEGRATOR_ASGI_VERIFIED_FIRST.md)** is in scope (backlog
**`c631fe3f-8a66-4a9d-a900-bab855860c7b`**), **`README.md`** **must** include a markdown link to
**`docs/SPEC_INTEGRATOR_ASGI_VERIFIED_FIRST.md`** (path as written from the repository root) inside **`## Verifying webhook signatures`**.
Use **one or two sentences** of context (raw body before JSON; FastAPI / Starlette)—the linked spec holds the copy-paste
examples.

## Secrets and examples hygiene

- **Never** document real shared secrets, bearer tokens, or live **`Replayt-Signature`** values. Use obvious placeholders
  (**`your-shared-secret`**, **`<signature-header-value>`**).
- Code blocks **must not** echo **SPEC_WEBHOOK_FAILURE_RESPONSES** example **`Replayt-Signature`** values when those examples use
  distinctive hex patterns—prefer ellipses or generic placeholders in README-only snippets.
- Align with **[DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)** **LLM / demos** and **MISSION** redaction expectations for
  anything resembling production logs.

## Release hygiene

When **Builder** changes **`README.md`** to satisfy this spec (user-visible operator guidance):

- Add a bullet under **`CHANGELOG.md`** **Unreleased** (**Documentation** or **Changed**) referencing this backlog and the
  new/expanded sections.

**Phase 2 (spec-only):** No **CHANGELOG** entry is **required** until **README** text ships; this spec file alone is
maintainer-facing contract.

## Automated acceptance

See **Backlog `23e2da29`** in **[SPEC_AUTOMATED_TESTS.md](SPEC_AUTOMATED_TESTS.md)** (**OP1**–**OP9**; **OP9** is the
**`docs/SPEC_INTEGRATOR_ASGI_VERIFIED_FIRST.md`** link under **Verifying**, backlog **`c631fe3f`**) and **Backlog
`87e7edae`** (**SEC8** — **`SECURITY.md`** link from **`README.md`**). Implementations **must** use **network-free** tests
that read **`README.md`** from disk (same pattern as **DG6**, **A2**/README checks).

## Related docs

- **[SPEC_REFERENCE_HTTP_SERVER_ROUTE_MAP.md](SPEC_REFERENCE_HTTP_SERVER_ROUTE_MAP.md)** — canonical reference-server **HTTP**
  matrix (**RM1**–**RM7**); README link requirement **§ Reference server route map link**.
- **[README.md](../README.md)** — target document for Builder.
- **[EVENTS.md](EVENTS.md)** — approval and run **`event_type`** registry and **`correlation`** fields.
- **[SPEC_WEBHOOK_SIGNATURE.md](SPEC_WEBHOOK_SIGNATURE.md)** — signing and verification procedure.
- **[SPEC_WEBHOOK_FAILURE_RESPONSES.md](SPEC_WEBHOOK_FAILURE_RESPONSES.md)** — operator error catalog.
- **[SPEC_LOCAL_WEBHOOK_DEMO.md](SPEC_LOCAL_WEBHOOK_DEMO.md)** — local signed POST command (**D1**–**D9**).
- **[SPEC_REVERSE_PROXY_REFERENCE_SERVER.md](SPEC_REVERSE_PROXY_REFERENCE_SERVER.md)** — reverse proxy guide contract (**OG1**–**OG8**).
- **[SPEC_SECURITY_DISCLOSURE.md](SPEC_SECURITY_DISCLOSURE.md)** — root **`SECURITY.md`** disclosure policy (**SC1**–**SC11**); **README** link **SEC8**.
