# Spec: reference HTTP server route and status matrix

**Backlog:** Machine-readable route/status map for the reference HTTP server (`b4c68e50-04df-4149-b9b5-f5d6280b38cc`).  
**Audience:** Spec gate (2b), Builder (3), Tester (4), API gateway integrators, maintainers.

## Problem

**SPEC_HTTP_SERVER_ENTRYPOINT** and **SPEC_MINIMAL_HTTP_HANDLER** describe behavior across sections; operators and
**API gateways** need a **single compact matrix** of paths, methods, default bind values, success vs error **HTTP**
statuses, and **pointers to normative specs** (signing, stable JSON **`error`** codes) for policy, mocks, and allowlists.

## Normative status

- This document holds the **canonical Markdown table** for the **reference server** contract shipped under
  **[SPEC_HTTP_SERVER_ENTRYPOINT.md](SPEC_HTTP_SERVER_ENTRYPOINT.md)**.
- **`README.md`** **must** link to this file (see **§ Publication surfaces** and **[SPEC_README_OPERATOR_SECTIONS.md](SPEC_README_OPERATOR_SECTIONS.md)**).
- **No new runtime Python API** is required for this backlog—only documentation and cross-links.

## Non-goals

- **OpenAPI** / **JSON Schema** for the HTTP surface (this backlog is **Markdown-first**; maintainers may add a generated
  artifact later if they extend scope).
- Defining **replayt** upstream delivery URLs or product behavior beyond what existing specs already cover.

## Defaults (normative for the matrix)

These values **must** match **[SPEC_HTTP_SERVER_ENTRYPOINT.md](SPEC_HTTP_SERVER_ENTRYPOINT.md)** and the shipped
**`python -m replayt_lifecycle_webhooks`** implementation. If implementation or entrypoint docs change **host**, **port**,
or default **webhook path**, update **this table in the same change** as **SPEC_HTTP_SERVER_ENTRYPOINT** and
**CHANGELOG.md**.

| Item | Default | Notes |
| ---- | ------- | ----- |
| **Bind host** | **`127.0.0.1`** | Documented default for local use; production examples may use **`0.0.0.0`** behind a reverse proxy. |
| **Bind port** | **`8000`** | CLI **`--port`** (or equivalent) overrides must stay documented in **README** + **SPEC_HTTP_SERVER_ENTRYPOINT**. |
| **Webhook path** | **`/webhook`** | **POST** lifecycle deliveries; path overrides must remain documented if supported. |
| **Health path** | **`/health`** | **GET** liveness; **must not** require **`Replayt-Signature`** or the shared secret. |

## Canonical route / status table

**Integrators:** Use this table as the **single source of truth** for the reference listener’s **HTTP surface**. For
**JSON **`error`** codes** and response shapes on webhook failures, use
**[SPEC_WEBHOOK_FAILURE_RESPONSES.md](SPEC_WEBHOOK_FAILURE_RESPONSES.md)**. For **signature verification** rules,
**`Replayt-Signature`** format, and **401** / **403** policy,
**[SPEC_WEBHOOK_SIGNATURE.md](SPEC_WEBHOOK_SIGNATURE.md)**. For **handler ordering** (method → verify → JSON) and the full
status story including **422**, **[SPEC_MINIMAL_HTTP_HANDLER.md](SPEC_MINIMAL_HTTP_HANDLER.md)**.

| Path | Method | Success HTTP | Primary error / alternate HTTP | Normative specs |
| ---- | ------ | ------------ | ------------------------------ | --------------- |
| **`/webhook`** | **POST** | **204** (empty body on success; idempotent duplicate **`event_id`** ack per handler hooks) | **405** (non-POST; **`Allow: POST`** where applicable); **401** / **403** (signature); **400** (UTF-8 / JSON); **422** (unknown **`event_type`**, **`replay_rejected`**, etc. when replay/dedupe hooks apply) | [SPEC_MINIMAL_HTTP_HANDLER.md](SPEC_MINIMAL_HTTP_HANDLER.md) (**H1–H12**, status table); [SPEC_WEBHOOK_FAILURE_RESPONSES.md](SPEC_WEBHOOK_FAILURE_RESPONSES.md); [SPEC_WEBHOOK_SIGNATURE.md](SPEC_WEBHOOK_SIGNATURE.md) |
| **`/health`** | **GET** | **200** (small non-secret body, e.g. plain **`ok`** or minimal JSON) | *(none required for normal operation)* — wrong method or extra auth are **implementation-defined**; document behavior if non-**200** cases exist | [SPEC_HTTP_SERVER_ENTRYPOINT.md](SPEC_HTTP_SERVER_ENTRYPOINT.md) (**§ Health / readiness**) |

## Publication surfaces (Builder)

| Surface | Requirement |
| ------- | ----------- |
| **This spec** | Keep the **§ Canonical route / status table** present and aligned with **SPEC_HTTP_SERVER_ENTRYPOINT** / **SPEC_MINIMAL_HTTP_HANDLER**. |
| **`README.md`** | Include a **markdown link** to **`docs/SPEC_REFERENCE_HTTP_SERVER_ROUTE_MAP.md`** (path as written from repo root) in the **Overview** quick-link list **or** inside **`## Troubleshooting`** or **`## Verifying webhook signatures`** so operators and gateway owners can find the matrix without spelunking. |
| **CHANGELOG** | When the **user-visible** table or defaults change, add an **Unreleased** note per project convention. |

## Acceptance criteria (checklist for Builder / Tester)

| ID | Criterion | Verification |
| -- | --------- | ------------ |
| **RM1** | **§ Canonical route / status table** exists in this file and includes **`POST /webhook`** and **`GET /health`**. | Doc review |
| **RM2** | Table documents **default bind host**, **port**, and **`/webhook`** path (values consistent with **SPEC_HTTP_SERVER_ENTRYPOINT**). | Doc review |
| **RM3** | Table lists **primary success** statuses (**204** for webhook, **200** for health) and **primary error** statuses for the webhook path, with links to **SPEC_WEBHOOK_FAILURE_RESPONSES** and **SPEC_WEBHOOK_SIGNATURE**. | Doc review |
| **RM4** | **`README.md`** links to this spec (see **§ Publication surfaces**). | Doc review; **`pytest`** **`tests/test_reference_http_server_route_map_doc.py`** |
| **RM5** | **[SPEC_README_OPERATOR_SECTIONS.md](SPEC_README_OPERATOR_SECTIONS.md)** documents the README link requirement for this backlog (traceability for **OP** tests). | Doc review |
| **RM6** | **SPEC_HTTP_SERVER_ENTRYPOINT** and **SPEC_AUTOMATED_TESTS** reference this document for gateway / operator matrix discoverability. | Doc review |
| **RM7** | **No new integrator-facing runtime API**—docs, cross-links, and optional **pytest** doc guards only. | Doc / manifest review |

**Tester note:** **RM1**–**RM3** stay **doc review** unless extended with **pytest**; **RM4** includes **`tests/test_reference_http_server_route_map_doc.py`**; **RM5**–**RM7** stay **doc review**. Subprocess and handler behavior remain covered by **S3**/**S4**/**S6**/**S9**/**H1**–**H12**/**SUB1**–**SUB8** as applicable.

## Related docs

- **[SPEC_HTTP_SERVER_ENTRYPOINT.md](SPEC_HTTP_SERVER_ENTRYPOINT.md)** — entrypoint command, health contract, **S1–S13**.
- **[SPEC_MINIMAL_HTTP_HANDLER.md](SPEC_MINIMAL_HTTP_HANDLER.md)** — **`handle_lifecycle_webhook_post`** / WSGI status table **H1–H12**.
- **[SPEC_WEBHOOK_FAILURE_RESPONSES.md](SPEC_WEBHOOK_FAILURE_RESPONSES.md)** — stable JSON **`error`** codes and HTTP mapping.
- **[SPEC_WEBHOOK_SIGNATURE.md](SPEC_WEBHOOK_SIGNATURE.md)** — **`Replayt-Signature`**, verification procedure, leakage rules.
- **[SPEC_LOCAL_WEBHOOK_DEMO.md](SPEC_LOCAL_WEBHOOK_DEMO.md)** — local signed **POST**; defaults **must** stay aligned with **SPEC_HTTP_SERVER_ENTRYPOINT** (**D2**).
- **[SPEC_REVERSE_PROXY_REFERENCE_SERVER.md](SPEC_REVERSE_PROXY_REFERENCE_SERVER.md)** — edge proxy in front of the listener (**OG1**–**OG8**).
- **[README.md](../README.md)** — operator copy-paste and cross-links.
