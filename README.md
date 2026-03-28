# Signed HTTP webhooks for replayt run and approval lifecycle events

## Overview

This project builds on **[replayt](https://pypi.org/project/replayt/)** as a **consumer-side** satellite: upstream owns
lifecycle **semantics** and **signing**; this repo supplies the tested verification primitive, normative specs, and **CI**
coverage integrators would otherwise reimplement (ecosystem pattern and scope: **[docs/MISSION.md](docs/MISSION.md)**,
**[docs/REPLAYT_ECOSYSTEM_IDEA.md](docs/REPLAYT_ECOSYSTEM_IDEA.md)**). It declares a runtime dependency on
**replayt `>=0.4.25`** (see `pyproject.toml`). Formal contract, bump policy, and acceptance criteria:
**[docs/SPEC_REPLAYT_DEPENDENCY.md](docs/SPEC_REPLAYT_DEPENDENCY.md)**. Webhook signature verification contract and
acceptance checklist: **[docs/SPEC_WEBHOOK_SIGNATURE.md](docs/SPEC_WEBHOOK_SIGNATURE.md)**. **Optional minimal HTTP POST
handler** (mounting, status codes, test bar): **[docs/SPEC_MINIMAL_HTTP_HANDLER.md](docs/SPEC_MINIMAL_HTTP_HANDLER.md)**.
**Reference HTTP server** (stdlib **WSGI**, no extra install): primary command **`python -m replayt_lifecycle_webhooks`**,
**POST** on **`/webhook`** by default, **`GET /health`**. Details and acceptance **S1–S8**:
**[docs/SPEC_HTTP_SERVER_ENTRYPOINT.md](docs/SPEC_HTTP_SERVER_ENTRYPOINT.md)**. **Local signed demo POST** (one command,
dev fixtures, same **v1** signing as verification): **[docs/SPEC_LOCAL_WEBHOOK_DEMO.md](docs/SPEC_LOCAL_WEBHOOK_DEMO.md)**
(checklist **D1–D9**). **Run / approval JSON envelope** (field
definitions and examples): **[docs/EVENTS.md](docs/EVENTS.md)**. **Delivery retries, duplicate POSTs, and `event_id`
idempotency:** **[docs/SPEC_DELIVERY_IDEMPOTENCY.md](docs/SPEC_DELIVERY_IDEMPOTENCY.md)**. **Replay protection** (freshness
on **`occurred_at`**, clock skew, optional wire headers, pluggable dedupe store contract, test rows **RP4**/**RP5**):
**[docs/SPEC_REPLAY_PROTECTION.md](docs/SPEC_REPLAY_PROTECTION.md)**. Informative **JSON Schema** mirror (**Draft-07**):
**[docs/schemas/lifecycle_webhook_payload-1-0.schema.json](docs/schemas/lifecycle_webhook_payload-1-0.schema.json)**.
**Scope, success, and release expectations:** **[docs/MISSION.md](docs/MISSION.md)**. **Automated test bar and CI
entrypoint:** **[docs/SPEC_AUTOMATED_TESTS.md](docs/SPEC_AUTOMATED_TESTS.md)**.

**Lifecycle semantics (upstream) vs wire JSON (this repo):** Replayt’s product and library semantics are described on
**[replayt (PyPI)](https://pypi.org/project/replayt/)** (project description, release history, and links from that
page). The **replayt** distribution does not currently ship a single canonical HTTP webhook JSON schema; after you
verify **`Replayt-Signature`**, treat **`docs/EVENTS.md`** and **`replayt_lifecycle_webhooks.events`** (**`parse_lifecycle_webhook_event`**
and model types) as the **normative wire contract** for lifecycle POST bodies in this package. When replayt publishes an
authoritative schema, align **EVENTS.md**, models, fixtures, and **CHANGELOG.md** with it.

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

**Report breakage:** Open an issue on [GitHub Issues](https://github.com/flogat/replayt-lifecycle-webhooks/issues). Include both the installed **replayt** version and **replayt-lifecycle-webhooks** version.

**Compatibility matrix** (**replayt** ↔ this package version line, bump policy, optional upper bound): **[docs/SPEC_REPLAYT_DEPENDENCY.md](docs/SPEC_REPLAYT_DEPENDENCY.md)** (section **Compatibility matrix**).

## Design principles

**[docs/DESIGN_PRINCIPLES.md](docs/DESIGN_PRINCIPLES.md)** covers **replayt** compatibility, versioning, and (for showcases)
**LLM** boundaries.


## Reference documentation (optional)

[`docs/reference-documentation/`](docs/reference-documentation/) holds short excerpts or consumer contracts when
upstream prose is not in this tree. See
[`REPLAYT_WEBHOOK_SIGNING.md`](docs/reference-documentation/REPLAYT_WEBHOOK_SIGNING.md) for the HMAC header and body
rules this package implements.

## Quick start

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
pip install -e ".[dev]"
```

## Try it locally

1. Start the **reference server** (see **Reference HTTP server** below) with **`REPLAYT_LIFECYCLE_WEBHOOK_SECRET`** set.
2. In a second terminal, POST a **signed** sample lifecycle body (default **`run_completed`**) to the same secret and
   default URL **`http://127.0.0.1:8000/webhook`**:

```bash
export REPLAYT_LIFECYCLE_WEBHOOK_SECRET='your-shared-secret'
python -m replayt_lifecycle_webhooks.demo_webhook
```

Optional flags: **`--url`**, **`--fixture PATH_OR_PRESET`** (packaged presets match **`tests/fixtures/events/*.json`** in
the repo; **`pip install`** users rely on the copies shipped under **`replayt_lifecycle_webhooks/fixtures/events/`**), or
**`--secret`** for local debugging only (prefer the env var). Console script alias: **`replayt-lifecycle-webhooks-demo-post`**.

Full contract, exit codes, and checklist **D1–D9**: **[docs/SPEC_LOCAL_WEBHOOK_DEMO.md](docs/SPEC_LOCAL_WEBHOOK_DEMO.md)**.
Signing rules match **[docs/SPEC_WEBHOOK_SIGNATURE.md](docs/SPEC_WEBHOOK_SIGNATURE.md)** (**v1** **`Replayt-Signature`**).

## Reference HTTP server

Primary start command (same handler semantics as **`make_lifecycle_webhook_wsgi_app`**; see
**[docs/SPEC_HTTP_SERVER_ENTRYPOINT.md](docs/SPEC_HTTP_SERVER_ENTRYPOINT.md)**):

```bash
export REPLAYT_LIFECYCLE_WEBHOOK_SECRET='your-shared-secret'
python -m replayt_lifecycle_webhooks
```

Defaults: bind **`127.0.0.1`:**`8000`, webhook **POST** URL path **`/webhook`**, probe **`GET /health`** (body **`ok`**,
plain text). Override with **`--host`**, **`--port`**, **`--webhook-path`**; optional **`--secret`** for local debugging
(prefer the environment variable in runbooks so the shell does not retain the value).

The **library** still does not read the environment for **`verify_lifecycle_webhook_signature`** or
**`handle_lifecycle_webhook_post`**; only this **process** entrypoint loads **`REPLAYT_LIFECYCLE_WEBHOOK_SECRET`** by
default (**[docs/SPEC_WEBHOOK_SIGNATURE.md](docs/SPEC_WEBHOOK_SIGNATURE.md)**).

Secondary console scripts (equivalent): **`replayt-lifecycle-webhooks-serve`** (reference server),
**`replayt-lifecycle-webhooks-demo-post`** (signed demo POST).

## Running tests

From the repository root after a dev install:

```bash
pytest tests -q
```

The **normative** full suite is defined in **[docs/SPEC_AUTOMATED_TESTS.md](docs/SPEC_AUTOMATED_TESTS.md)** and
**[docs/SPEC_REPLAYT_BOUNDARY_TESTS.md](docs/SPEC_REPLAYT_BOUNDARY_TESTS.md)**: **unit / contract** tests (signature
verification, lifecycle JSON parsing, handler behavior, doc guards) and **replayt boundary** tests that **`import replayt`**
and lock **EVENTS.md**-listed symbols (**R1–R5**). **`pytest tests -q`** is the contributor and **CI** entrypoint (see
**`.github/workflows/ci.yml`**). There is **no** separate network-backed “integration” job unless **CHANGELOG.md** and those
specs add one.

**Focused runs (optional):**

```bash
pytest tests/test_webhook_signature.py tests/test_lifecycle_events.py -q   # crypto + parsing only (example)
pytest tests -m replayt_boundary -q                                         # replayt import + symbol checks only
```

Checklist rows **A1–A5** (minimum verification / parsing) and **R1–R5** (replayt boundary): **SPEC_AUTOMATED_TESTS** and
**SPEC_REPLAYT_BOUNDARY_TESTS**.

## Troubleshooting

**Duplicate deliveries (retries, redelivery of the same event):** Treat lifecycle webhooks as **at-least-once** on the
wire. After **`Replayt-Signature`** verification succeeds, dedupe using **`event_id`** from the JSON envelope (see
**[docs/EVENTS.md](docs/EVENTS.md)**). Compatible senders should reuse the **same** **`event_id`** and body for every HTTP
retry of one logical emission. Use an **application idempotency store** with a **TTL** sized to your longest retry and
approval windows; if you evict keys too early, a late duplicate may run side effects twice. Full contract, composite-key
fallbacks for legacy senders, and TTL guidance: **[docs/SPEC_DELIVERY_IDEMPOTENCY.md](docs/SPEC_DELIVERY_IDEMPOTENCY.md)**.

**Replayed captures (valid MAC, stale or disallowed delivery):** Signing does not prove freshness. After verification,
enforce **payload `occurred_at`** windows (and optionally reserved **`Replayt-*`** headers or a **nonce**) per
**[docs/SPEC_REPLAY_PROTECTION.md](docs/SPEC_REPLAY_PROTECTION.md)**; map rejections to **`replay_rejected`** in
**[docs/SPEC_WEBHOOK_FAILURE_RESPONSES.md](docs/SPEC_WEBHOOK_FAILURE_RESPONSES.md)**. Do not confuse **benign
duplicates** (idempotent **2xx**) with **policy rejects** (**422** / **`replay_rejected`**).

**Signature verification failures:** See **[docs/SPEC_WEBHOOK_SIGNATURE.md](docs/SPEC_WEBHOOK_SIGNATURE.md)** (raw body
discipline, header format) and **[docs/SPEC_WEBHOOK_FAILURE_RESPONSES.md](docs/SPEC_WEBHOOK_FAILURE_RESPONSES.md)** (stable
**`error`** codes for operators).

## Verifying webhook signatures

Verify the **raw request body** with your shared secret and the **`Replayt-Signature`** header before parsing JSON or
running automation. Ordered steps for handlers:
**[Verification procedure](docs/SPEC_WEBHOOK_SIGNATURE.md#verification-procedure-integrators)** in
**[docs/SPEC_WEBHOOK_SIGNATURE.md](docs/SPEC_WEBHOOK_SIGNATURE.md)**. Full contract detail also in
**[docs/reference-documentation/REPLAYT_WEBHOOK_SIGNING.md](docs/reference-documentation/REPLAYT_WEBHOOK_SIGNING.md)**.

**Signing secret configuration:** this package does **not** read the environment for you. Operators should configure one
shared secret out of band and pass it into **`verify_lifecycle_webhook_signature`**. **Recommended environment variable
name:** **`REPLAYT_LIFECYCLE_WEBHOOK_SECRET`** (string secret; UTF-8 when used as the HMAC key via a `str` argument).
Load it with your framework or `os.environ`, inject via a secret manager in production, and **never** log the raw value.

**HTTP failures:** on missing, malformed, or non-matching signatures, respond with **401 Unauthorized** and/or **403
Forbidden** as described in
**[HTTP responses and logging](docs/SPEC_WEBHOOK_SIGNATURE.md#http-responses-and-logging-normative-for-integrators)**.
Use **generic** client-facing error bodies; do not echo the secret, the full signature header, or a computed MAC.

**Operator runbooks (status + JSON):** stable **`error` codes**, typical HTTP statuses, redacted example bodies, and
rules for **what not to log or return** live in
**[docs/SPEC_WEBHOOK_FAILURE_RESPONSES.md](docs/SPEC_WEBHOOK_FAILURE_RESPONSES.md)**. That spec also covers
**post-verification** failures (**unknown `event_type`**, invalid JSON shape, **application-level replay / freshness**)
and notes that **v1** MAC verification does **not** include a wire timestamp.

| Situation | Typical HTTP | Stable `error` (JSON) |
| --------- | ------------ | ----------------------- |
| Not POST | **405** | `method_not_allowed` |
| Missing / empty `Replayt-Signature` | **401** | `signature_required` |
| Malformed signature header (v1) | **401** | `signature_malformed` |
| MAC mismatch | **403** | `signature_mismatch` |
| Invalid UTF-8 or JSON **after** verify | **400** | `invalid_json` |
| Unknown `event_type` **after** verify | **422** (recommended) | `unknown_event_type` |
| Replay / duplicate / freshness policy | **422** or **409** | `replay_rejected` |

See the spec for full tables and examples. **`handle_lifecycle_webhook_post`** returns **`application/json`** bodies
(**`error`** + **`message`**) for **405** / **401** / **403** / **400** per that spec; **204** stays empty.

**Production logging and redaction:** use stdlib **`logging`** (or your stack’s structured wrapper) with **stable**
**`error`** codes, HTTP status, and correlation ids—**not** raw secrets. When you log **HTTP headers** or **dict-like**
metadata, pass them through **`replayt_lifecycle_webhooks.redaction`** first
(**[docs/SPEC_STRUCTURED_LOGGING_REDACTION.md](docs/SPEC_STRUCTURED_LOGGING_REDACTION.md)**): defaults mask
**`Authorization`**, **`Replayt-Signature`**, **`X-Signature*`**-family headers, cookies, and common token-like mapping
keys; use **`extra_sensitive_names`** / **`extra_sensitive_keys`** for deployment-specific names. **Do not** log the
**raw body**, **full** signature header, **computed MAC**, or **HMAC secret** (same boundaries as
**[docs/SPEC_WEBHOOK_FAILURE_RESPONSES.md](docs/SPEC_WEBHOOK_FAILURE_RESPONSES.md)**).

```python
import logging

from replayt_lifecycle_webhooks.redaction import format_safe_webhook_log_extra, redact_headers

log = logging.getLogger(__name__)

# Structured fields for LogRecord.extra (keys avoid stdlib attribute clashes):
extra = format_safe_webhook_log_extra(
    method="POST",
    path="/webhook",
    status_code=403,
    error_code="signature_mismatch",
    headers=request_headers,  # mapping or (name, value) pairs
)
log.info("handled webhook", extra=extra)

# Or redact a header map before formatting your own message:
log.debug("headers=%s", redact_headers(request_headers))
```

**Drop-in HTTP handler:** **`handle_lifecycle_webhook_post`** maps a POST, raw body, and header map to status **405** /
**401** / **403** / **400** / **204** as in **[docs/SPEC_MINIMAL_HTTP_HANDLER.md](docs/SPEC_MINIMAL_HTTP_HANDLER.md)**.
**MAC mismatch** uses **403**; missing or malformed **`Replayt-Signature`** uses **401**. Verification runs before
**`json.loads`**.

**Callable (any framework):** pass method, raw body bytes, and headers (names are matched case-insensitively):

```python
import os

from replayt_lifecycle_webhooks import handle_lifecycle_webhook_post

secret = os.environ["REPLAYT_LIFECYCLE_WEBHOOK_SECRET"]
result = handle_lifecycle_webhook_post(
    secret=secret,
    method=request_method,  # e.g. "POST"
    body=raw_body,  # bytes from the HTTP layer, unchanged
    headers=request_headers,  # mapping or (name, value) pairs including Replayt-Signature
)
# result.status, result.headers, result.body — e.g. 204 with empty body on success
```

**WSGI (stdlib server):** use **`python -m replayt_lifecycle_webhooks`** for routing (**`GET /health`**, **`POST /webhook`**
by default), or build your own server from **`make_lifecycle_webhook_wsgi_app`** (single-path app, no health route) with
**`wsgiref.simple_server`**:

```python
import os

from wsgiref.simple_server import make_server

from replayt_lifecycle_webhooks import make_lifecycle_webhook_wsgi_app

app = make_lifecycle_webhook_wsgi_app(secret=os.environ["REPLAYT_LIFECYCLE_WEBHOOK_SECRET"])

if __name__ == "__main__":
    with make_server("", 8000, app) as httpd:
        print("Listening on http://127.0.0.1:8000")
        httpd.serve_forever()
```

For a composite app in code (health + webhook path), use **`replayt_lifecycle_webhooks.serve.make_reference_lifecycle_webhook_wsgi_app`**.

Optional **`on_success`** on both APIs runs only after verification and successful JSON parse.

**Run / approval payload shape:** after verification, pass the parsed JSON object to
**`parse_lifecycle_webhook_event`** to validate against **[docs/EVENTS.md](docs/EVENTS.md)** (discriminated by
**`event_type`**; if **`schema_version`** is present it must match **`SUPPORTED_LIFECYCLE_WEBHOOK_SCHEMA_VERSIONS`**).
Combine with **`on_success`** when using **`handle_lifecycle_webhook_post`**.

**Lower-level verification only:**

```python
import os

from replayt_lifecycle_webhooks import (
    LIFECYCLE_WEBHOOK_SIGNATURE_HEADER,
    verify_lifecycle_webhook_signature,
)

# raw_body: bytes exactly as received from the HTTP layer
# header_value: request header LIFECYCLE_WEBHOOK_SIGNATURE_HEADER (e.g. "sha256=<hex>")
verify_lifecycle_webhook_signature(
    secret=os.environ["REPLAYT_LIFECYCLE_WEBHOOK_SECRET"],
    body=raw_body,
    signature=header_value,
)
```

## Optional agent workflows

This repo may include a [`.cursor/skills/`](.cursor/skills/) directory for Cursor-style agent skills. **`.gitignore`**
lists **`path/`** (so documentation-style placeholder paths are never committed), **`.cursor/skills/`**, and related
local tooling entries. Adapt or remove optional directories to match your team’s workflow.

## Project layout

| Path | Purpose |
| ---- | ------- |
| `docs/REPLAYT_ECOSYSTEM_IDEA.md` | Ecosystem taxonomy; primary pattern recorded and aligned with **MISSION** |
| `docs/MISSION.md` | Mission and scope |
| `docs/DESIGN_PRINCIPLES.md` | Design and integration principles |
| `docs/SPEC_REPLAYT_DEPENDENCY.md` | **replayt** range: contract, **compatibility matrix**, upper-bound policy, checklist, CI expectations |
| `docs/SPEC_AUTOMATED_TESTS.md` | **pytest** / CI entrypoint, minimum verification + parsing coverage, no smoke-only **`assert True`** |
| `docs/SPEC_WEBHOOK_SIGNATURE.md` | Incoming webhook signature verification: API contract, tests, upstream alignment |
| `docs/SPEC_MINIMAL_HTTP_HANDLER.md` | Optional minimal HTTP POST handler: mounting, status codes, acceptance **H1–H8** |
| `docs/SPEC_HTTP_SERVER_ENTRYPOINT.md` | Reference HTTP server: one start command, **POST** route, **`GET /health`**, acceptance **S1–S8** |
| `docs/SPEC_LOCAL_WEBHOOK_DEMO.md` | Local demo: one command POSTs signed fixtures to default listener; acceptance **D1–D9** |
| `replayt_lifecycle_webhooks.demo_webhook` | **`python -m replayt_lifecycle_webhooks.demo_webhook`**: signed POST to default **`/webhook`** URL |
| `replayt_lifecycle_webhooks/fixtures/events/` | Packaged JSON presets aligned with **`tests/fixtures/events/`** for **`pip install`** demos |
| `docs/SPEC_WEBHOOK_FAILURE_RESPONSES.md` | Operator-facing HTTP + JSON failure contract; safe examples; logging boundaries |
| `docs/SPEC_STRUCTURED_LOGGING_REDACTION.md` | Structured **`logging`** helpers; default sensitive-key redaction; tests **L1–L8** |
| `docs/EVENTS.md` | Lifecycle webhook JSON: **`event_type`**, **`occurred_at`**, **`event_id`**, correlation ids, **`summary`**, **`schema_version`**, synthetic examples |
| `docs/SPEC_DELIVERY_IDEMPOTENCY.md` | At-least-once delivery assumptions, **`event_id`** dedupe rules, idempotency store TTL guidance |
| `docs/SPEC_REPLAY_PROTECTION.md` | Stale capture replay vs duplicates; **`occurred_at`** freshness; optional headers; dedupe store protocol; **RP4**/**RP5** |
| `docs/schemas/lifecycle_webhook_payload-1-0.schema.json` | Informative JSON Schema for **`1.0`**-family payloads (non-Python integrators) |
| `docs/reference-documentation/` | Optional markdown snapshot for contributors (e.g. `REPLAYT_WEBHOOK_SIGNING.md`) |
| `src/replayt_lifecycle_webhooks/` | Python package: `signature`, `handler`, `events`, `redaction`, `serve`; **`__main__`** for **`python -m`** |
| `pyproject.toml` | Package metadata |
| `CHANGELOG.md` | Release notes (Keep a Changelog); keep **Unreleased** updated |
| `.gitignore` | Ignores `path/` (doc placeholders), `.orchestrator/`, `.cursor/skills/`, and `AGENTS.md` (local tooling) |
