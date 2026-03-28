# Signed HTTP webhooks for replayt run and approval lifecycle events

## Overview

This project builds on **[replayt](https://pypi.org/project/replayt/)** as a **consumer-side** satellite: upstream owns
lifecycle **semantics** and **signing**; this repo supplies the tested verification primitive, normative specs, and **CI**
coverage integrators would otherwise reimplement (ecosystem pattern and scope: **[docs/MISSION.md](docs/MISSION.md)**,
**[docs/REPLAYT_ECOSYSTEM_IDEA.md](docs/REPLAYT_ECOSYSTEM_IDEA.md)**). It declares a runtime dependency on
**replayt `>=0.4.25`** (see `pyproject.toml`). Formal contract, bump policy, and acceptance criteria:
**[docs/SPEC_REPLAYT_DEPENDENCY.md](docs/SPEC_REPLAYT_DEPENDENCY.md)**. Webhook signature verification contract and
acceptance checklist: **[docs/SPEC_WEBHOOK_SIGNATURE.md](docs/SPEC_WEBHOOK_SIGNATURE.md)**. **Optional minimal HTTP POST
handler** (mounting, status codes, test bar): **[docs/SPEC_MINIMAL_HTTP_HANDLER.md](docs/SPEC_MINIMAL_HTTP_HANDLER.md)**. **Run / approval JSON envelope** (field
definitions and examples): **[docs/EVENTS.md](docs/EVENTS.md)**.
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

**WSGI (stdlib server):** **`make_lifecycle_webhook_wsgi_app`** returns an app you can mount or run with
**`wsgiref.simple_server`** (no extra install beyond this package):

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

Optional **`on_success`** on both APIs runs only after verification and successful JSON parse.

**Run / approval payload shape:** after verification, pass the parsed JSON object to
**`parse_lifecycle_webhook_event`** to validate against **[docs/EVENTS.md](docs/EVENTS.md)** (discriminated by
**`event_type`**). Combine with **`on_success`** when using **`handle_lifecycle_webhook_post`**.

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
| `docs/SPEC_WEBHOOK_FAILURE_RESPONSES.md` | Operator-facing HTTP + JSON failure contract; safe examples; logging boundaries |
| `docs/EVENTS.md` | Lifecycle webhook JSON: **`event_type`**, **`occurred_at`**, correlation ids, **`summary`**, synthetic examples |
| `docs/reference-documentation/` | Optional markdown snapshot for contributors (e.g. `REPLAYT_WEBHOOK_SIGNING.md`) |
| `src/replayt_lifecycle_webhooks/` | Python package: `signature`, `handler`, `events` (`parse_lifecycle_webhook_event`, models) |
| `pyproject.toml` | Package metadata |
| `CHANGELOG.md` | Release notes (Keep a Changelog); keep **Unreleased** updated |
| `.gitignore` | Ignores `path/` (doc placeholders), `.orchestrator/`, `.cursor/skills/`, and `AGENTS.md` (local tooling) |
