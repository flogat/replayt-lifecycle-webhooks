# Spec: reverse proxy in front of the reference HTTP server

**Backlog:** Operator guide: reverse proxy in front of reference WSGI server  
**Workflow id:** `dc212184-8c0d-4ee6-90de-e0d50c370f6f` (phase **2** spec refinement; Builder authors **`docs/OPERATOR_REVERSE_PROXY.md`** and README cross-links in phase **3**).

**Audience:** Spec gate (2b), Builder (3), Tester (4), operators, integrators.

## Purpose and normative status

This document is the **contract** for a short **operator-facing** guide that explains how to place **nginx**, **Caddy**, or
another **reverse proxy / TLS terminator** in front of the **reference server** started with
**`python -m replayt_lifecycle_webhooks`** (see **[SPEC_HTTP_SERVER_ENTRYPOINT.md](SPEC_HTTP_SERVER_ENTRYPOINT.md)**)
without breaking **`Replayt-Signature`** verification (**HMAC over the raw POST body** per
**[SPEC_WEBHOOK_SIGNATURE.md](SPEC_WEBHOOK_SIGNATURE.md)**).

**Normative for Builder:** When this backlog is in scope, **`docs/OPERATOR_REVERSE_PROXY.md`** **must** satisfy **§
Deliverable** and **§ Acceptance criteria (OG1–OG8)** below. **§ Automated acceptance** maps to **pytest** rows **OG1**–**OG8**
in **[SPEC_AUTOMATED_TESTS.md](SPEC_AUTOMATED_TESTS.md)**.

**Non-goals:** Vendor-specific hardening beyond common proxy knobs (WAF rules, mTLS to upstream, Kubernetes Ingress
annotations) unless called out as optional notes; replacing **SPEC_WEBHOOK_SIGNATURE** or **SPEC_MINIMAL_HTTP_HANDLER**
with duplicated normative signing procedure.

## Problem

Production deployments almost always **terminate TLS** and **buffer** at an edge proxy. Misconfiguration can **truncate**,
**re-encode**, or **mutate** the request body before it reaches the WSGI stack, so the MAC computed over the bytes the app
sees no longer matches the sender’s signature.

## Deliverable

| Item | Requirement |
| ---- | ----------- |
| **Primary file** | **`docs/OPERATOR_REVERSE_PROXY.md`** (new file under **`docs/`**). |
| **Title** | Level-1 heading (**`# …`**) that clearly names **reverse proxy** (or **TLS termination**) and the **reference server** / **`python -m replayt_lifecycle_webhooks`** context. |
| **Tone** | Short operator runbook: bullets and one **copy-paste** proxy snippet; link out for signing and logging **norms**. |
| **Secrets hygiene** | No real shared secrets, bearer tokens, or live **`Replayt-Signature`** values—only placeholders. Snippets **must not** encourage **`access_log`** formats that echo full request bodies. |

## Required technical topics (prose)

The guide **must** explain, in operator-plain language:

1. **Raw body bytes** — Verification uses the **exact** octets the application reads as the POST body **after** any proxy
   buffering; integrators **must** not parse or modify JSON before MAC check (**[SPEC_WEBHOOK_SIGNATURE.md](SPEC_WEBHOOK_SIGNATURE.md)**).
2. **Client maximum body size** — Proxies should allow a **documented** upper bound large enough for expected lifecycle JSON
   (with headroom); operators should understand that **too-small** limits cause **413** / truncated bodies and **signature
   failures** that look like auth errors.
3. **Timeouts** — Proxy **read** / **send** timeouts (and upstream idle timeouts) should accommodate **slow clients** and
   **at-least-once** delivery retries without spurious **502**/disconnects that complicate operator debugging; link
   **[SPEC_DELIVERY_IDEMPOTENCY.md](SPEC_DELIVERY_IDEMPOTENCY.md)** for retry semantics (no need to copy the spec).
4. **`Transfer-Encoding` / buffering** — Why **chunked** vs **`Content-Length`** rewriting at the proxy matters: some stacks
   **buffer** or **normalize** bodies in ways that can affect what the upstream receives if misconfigured; the guide **must**
   state that the **signature is over the bytes the verifier sees**, so **transparent** forwarding of the **unchanged** body
   is the goal (without contradicting HTTP: do not claim impossible “never buffer” guarantees—focus on **avoiding
   transformation** and **truncation**).

## Config snippet

- **At least one** fenced **nginx** *or* **Caddy** example that **reverse-proxies** HTTP to the reference server’s listen
  address (placeholders for **`127.0.0.1:8000`** or documented defaults from **SPEC_HTTP_SERVER_ENTRYPOINT** are fine).
- **Inside the snippet** (as `#` or `//` comments, depending on format), **must** reference
  **`docs/SPEC_WEBHOOK_SIGNATURE.md`** (path as in repo) **or** the title **SPEC_WEBHOOK_SIGNATURE** so operators tie
  proxy settings to **raw-body signing**.

## Logging and redaction callout

The guide **must** include a **visually distinct** callout (for example a short **`##`** subsection titled like **Logging and
secrets**, or a blockquote) that states operators **must not** log **full POST bodies**, the **shared secret**, or full
**`Replayt-Signature`** values, and **must** follow
**[SPEC_STRUCTURED_LOGGING_REDACTION.md](SPEC_STRUCTURED_LOGGING_REDACTION.md)** for structured **`logging`** defaults.

## README cross-link

**[SPEC_README_OPERATOR_SECTIONS.md](SPEC_README_OPERATOR_SECTIONS.md)** defines where **`README.md`** must link this guide
when the backlog is active (**Troubleshooting** or **Verifying webhook signatures**).

## Backlog acceptance mapping (`dc212184`)

| Source criterion | Where addressed in this spec |
| ---------------- | ---------------------------- |
| Preserve body bytes; signing | **§ Required technical topics** — raw body; **§ Config snippet** — comment → **SPEC_WEBHOOK_SIGNATURE** |
| Max body size, timeouts, `Transfer-Encoding` | **§ Required technical topics** |
| nginx or Caddy snippet | **§ Config snippet** |
| Do not log bodies/secrets | **§ Logging and redaction callout** |
| README cross-link | **§ README cross-link** + **SPEC_README_OPERATOR_SECTIONS** |

## Acceptance criteria (checklist for Builder / Tester)

| ID | Criterion | Verification |
| -- | --------- | ------------ |
| **OG1** | **`docs/OPERATOR_REVERSE_PROXY.md`** exists; level-1 heading covers **reverse proxy** / TLS edge and the **reference server** (**`python -m replayt_lifecycle_webhooks`** or equivalent pointer to **SPEC_HTTP_SERVER_ENTRYPOINT**). | **pytest** / doc review |
| **OG2** | Explains **raw body byte** discipline for **`Replayt-Signature`**; links **`docs/SPEC_WEBHOOK_SIGNATURE.md`**. | **pytest** |
| **OG3** | Documents **client max body size** (or equivalent directive name for the chosen proxy) with **operator rationale** (avoid truncation / false signature failures). | **pytest** |
| **OG4** | Documents **timeout** concerns (proxy and upstream) and links **`docs/SPEC_DELIVERY_IDEMPOTENCY.md`**. | **pytest** |
| **OG5** | Explains **`Transfer-Encoding` / buffering** risk to **byte-identical** verification in **plain language** (see **§ Required technical topics**). | **pytest** |
| **OG6** | Includes **one** **nginx** or **Caddy** fenced block; **comment inside the block** points to **`docs/SPEC_WEBHOOK_SIGNATURE.md`** and/or **SPEC_WEBHOOK_SIGNATURE**. | **pytest** |
| **OG7** | **Callout** forbids logging full bodies / secrets / full signatures; links **`docs/SPEC_STRUCTURED_LOGGING_REDACTION.md`**. | **pytest** |
| **OG8** | Root **`README.md`** links **`docs/OPERATOR_REVERSE_PROXY.md`** inside **`## Troubleshooting`** or **`## Verifying webhook signatures`** (per **SPEC_README_OPERATOR_SECTIONS**). | **pytest** |

## Related docs

- **[SPEC_HTTP_SERVER_ENTRYPOINT.md](SPEC_HTTP_SERVER_ENTRYPOINT.md)** — reference server command, **`/webhook`**, **`GET /health`**.
- **[SPEC_WEBHOOK_SIGNATURE.md](SPEC_WEBHOOK_SIGNATURE.md)** — HMAC over raw body; verification procedure.
- **[SPEC_STRUCTURED_LOGGING_REDACTION.md](SPEC_STRUCTURED_LOGGING_REDACTION.md)** — never-log rules and redaction helpers.
- **[SPEC_DELIVERY_IDEMPOTENCY.md](SPEC_DELIVERY_IDEMPOTENCY.md)** — retries and **`event_id`**.
- **[SPEC_MINIMAL_HTTP_HANDLER.md](SPEC_MINIMAL_HTTP_HANDLER.md)** — WSGI app semantics behind the server.
- **[SPEC_README_OPERATOR_SECTIONS.md](SPEC_README_OPERATOR_SECTIONS.md)** — README operator headings and reverse-proxy link rule.
- **[README.md](../README.md)** — project layout lists the guide; **Troubleshooting** links **`docs/OPERATOR_REVERSE_PROXY.md`** (**OG8**).
