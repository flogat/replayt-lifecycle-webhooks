# Signed HTTP webhooks for replayt run and approval lifecycle events

## Overview

This project builds on **[replayt](https://pypi.org/project/replayt/)** as a **consumer-side** satellite: upstream owns
lifecycle **semantics** and **signing**; this repo supplies the tested verification primitive, normative specs, and **CI**
coverage integrators would otherwise reimplement. **Primary ecosystem pattern — Core-gap** (taxonomy, pitch, and how we
track **replayt** releases): **[docs/REPLAYT_ECOSYSTEM_IDEA.md](docs/REPLAYT_ECOSYSTEM_IDEA.md)**. Broader scope and success
expectations: **[docs/MISSION.md](docs/MISSION.md)**. It declares a runtime dependency on
**replayt `>=0.4.25`** (see `pyproject.toml`). Formal contract, bump policy, and acceptance criteria:
**[docs/SPEC_REPLAYT_DEPENDENCY.md](docs/SPEC_REPLAYT_DEPENDENCY.md)**. Webhook signature verification contract and
acceptance checklist: **[docs/SPEC_WEBHOOK_SIGNATURE.md](docs/SPEC_WEBHOOK_SIGNATURE.md)**. **Optional minimal HTTP POST
handler** (mounting, status codes, test bar): **[docs/SPEC_MINIMAL_HTTP_HANDLER.md](docs/SPEC_MINIMAL_HTTP_HANDLER.md)**.
**Optional metrics hooks** (keyword-only **`metrics=`**, stdlib reference types; no mandatory **Prometheus** / **OTel**):
**[docs/SPEC_METRICS_HOOKS.md](docs/SPEC_METRICS_HOOKS.md)** (**M1**–**M8**).
**Reference HTTP server** (stdlib **WSGI**, no extra install): primary command **`python -m replayt_lifecycle_webhooks`**,
**POST** on **`/webhook`** by default, **`GET /health`**. Compact **path / method / status** matrix for gateways and mocks:
**[docs/SPEC_REFERENCE_HTTP_SERVER_ROUTE_MAP.md](docs/SPEC_REFERENCE_HTTP_SERVER_ROUTE_MAP.md)**. Details and acceptance **S1–S13**:
**[docs/SPEC_HTTP_SERVER_ENTRYPOINT.md](docs/SPEC_HTTP_SERVER_ENTRYPOINT.md)**. **Reverse proxy / TLS** in front of that
listener (raw POST body, limits, timeouts): contract **[docs/SPEC_REVERSE_PROXY_REFERENCE_SERVER.md](docs/SPEC_REVERSE_PROXY_REFERENCE_SERVER.md)**;
operator guide **[docs/OPERATOR_REVERSE_PROXY.md](docs/OPERATOR_REVERSE_PROXY.md)** (**OG1**–**OG8**). **Local signed demo POST** (one command,
dev fixtures, same **v1** signing as verification): **[docs/SPEC_LOCAL_WEBHOOK_DEMO.md](docs/SPEC_LOCAL_WEBHOOK_DEMO.md)**
(checklist **D1–D9**). **Offline verify CLI** (saved raw body + **`Replayt-Signature`**; spec **VW1**–**VW8**, backlog **`845b4b11`**):
**[docs/SPEC_CLI_VERIFY_SAVED_WEBHOOK.md](docs/SPEC_CLI_VERIFY_SAVED_WEBHOOK.md)**. **Run / approval JSON envelope** (field
definitions and examples): **[docs/EVENTS.md](docs/EVENTS.md)**. **PM/support digest** (deterministic text + optional JSON
record after parse; **DG1–DG6**): **[docs/SPEC_EVENT_DIGEST.md](docs/SPEC_EVENT_DIGEST.md)** — digest output can still include
identifiers or sender-controlled text that is **not suitable for external sharing**; read **SPEC_EVENT_DIGEST** section
**Fields and artifacts not suitable for external sharing** before publishing to untrusted channels. **Delivery retries, duplicate POSTs, and `event_id`**
idempotency:** **[docs/SPEC_DELIVERY_IDEMPOTENCY.md](docs/SPEC_DELIVERY_IDEMPOTENCY.md)**. **Replay protection** (freshness
on **`occurred_at`**, clock skew, optional wire headers, pluggable dedupe store contract, test rows **RP4**/**RP5**):
**[docs/SPEC_REPLAY_PROTECTION.md](docs/SPEC_REPLAY_PROTECTION.md)**. Informative **JSON Schema** mirror (**Draft-07**):
**[docs/schemas/lifecycle_webhook_payload-1-0.schema.json](docs/schemas/lifecycle_webhook_payload-1-0.schema.json)**.
**Scope, success, and release expectations:** **[docs/MISSION.md](docs/MISSION.md)**. **Automated test bar and CI
entrypoint:** **[docs/SPEC_AUTOMATED_TESTS.md](docs/SPEC_AUTOMATED_TESTS.md)**. **Public Python API** (`__all__`, supported
vs internal import paths, **`python -m`** entrypoints, deprecation / **pre-1.0** policy):
**[docs/SPEC_PUBLIC_API.md](docs/SPEC_PUBLIC_API.md)**. **Optional contributor reference snapshots**
(**`docs/reference-documentation/`**): **[docs/SPEC_REFERENCE_DOCUMENTATION.md](docs/SPEC_REFERENCE_DOCUMENTATION.md)**.

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

**Compatibility matrix** (**replayt** and **Python** support, CI-tested interpreter, bump policy, optional upper bound): **[docs/SPEC_REPLAYT_DEPENDENCY.md](docs/SPEC_REPLAYT_DEPENDENCY.md)** (section **Compatibility matrix**).

**Python:** `pyproject.toml` sets **`requires-python`** (minimum installers must satisfy). Merge-blocking **`lint`** and **`test`** jobs run **`ruff check`** / **`ruff format --check`** on **`src/`** and **`tests/`** and the full **`pytest`** suite on **Python 3.11**, **Python 3.12**, and **Python 3.13** (matrix in **`.github/workflows/ci.yml`**). See **`docs/SPEC_REPLAYT_DEPENDENCY.md`** (**§ CI**, compatibility matrix) and **`docs/SPEC_AUTOMATED_TESTS.md`** (**§ Backlog `6cd22a7b`**, **§ Backlog `8e58aa9c`**). The **`package`** (**`python -m build`**, **`twine check`**) and **`supply-chain`** (**`pip-audit`**) jobs use **Python 3.12** only (single interpreter per job; matrix **Notes**). See **`.github/workflows/ci.yml`** for the live wiring.

## Design principles

**[docs/DESIGN_PRINCIPLES.md](docs/DESIGN_PRINCIPLES.md)** covers **replayt** compatibility, versioning, and (for showcases)
**LLM** boundaries.


## Reference documentation (optional)

[`docs/reference-documentation/`](docs/reference-documentation/) holds **optional** short markdown excerpts or consumer
contracts when upstream prose is not in this tree. You **do not** need to populate it to build or test this package;
**CI** does not download upstream documentation trees. **Default clone stays small:** only reviewed excerpts are
committed; large mirrors belong under a **local-only**, **gitignored** tree (see below). Maintainer-oriented **when to
refresh**, **licensing/attribution** rules for committed prose, and **git** / **curl** / **rsync** patterns for snapshots:
**[docs/SPEC_REFERENCE_DOCUMENTATION.md](docs/SPEC_REFERENCE_DOCUMENTATION.md)**. Contributor entry point:
**[CONTRIBUTING.md](CONTRIBUTING.md)** (**Reference documentation snapshots**).

See
[`REPLAYT_WEBHOOK_SIGNING.md`](docs/reference-documentation/REPLAYT_WEBHOOK_SIGNING.md) for the HMAC header and body rules
this package implements, and [`docs/reference-documentation/README.md`](docs/reference-documentation/README.md) for what
belongs in git vs a **local-only** tree.

**When to refresh (summary)**

- Upstream **signing** or **delivery** docs change in a way that affects this repo’s contract — update committed
  excerpts and follow **[docs/SPEC_WEBHOOK_SIGNATURE.md](docs/SPEC_WEBHOOK_SIGNATURE.md)** / **CHANGELOG.md** hygiene.
- You need a **stable in-tree citation** for review, or you are working **offline** — use a **local** snapshot under
  [`docs/reference-documentation/_upstream_snapshot/`](docs/reference-documentation/_upstream_snapshot/) (do not commit).

**Licensing:** Committed excerpts must carry clear **provenance** and **license/attribution** (see the spec). Local
**`_upstream_snapshot/`** copies are your responsibility to keep license-compliant; they are **not** shipped with the
package.

**How to refresh**

- **Committed excerpts:** edit the relevant file(s) under [`docs/reference-documentation/`](docs/reference-documentation/)
  in a PR when the consumer contract changes.
- **Bulk / offline copies:** use a **gitignored** directory
  [`docs/reference-documentation/_upstream_snapshot/`](docs/reference-documentation/_upstream_snapshot/) (create it
  locally) and copy markdown from your local **replayt** checkout or docs export **manually**, follow the **git** /
  **curl** / **rsync** examples in
  [`docs/SPEC_REFERENCE_DOCUMENTATION.md`](docs/SPEC_REFERENCE_DOCUMENTATION.md), or run the optional helper
  **`scripts/sync_upstream_reference_docs.sh`** with the path to upstream’s **`docs/`** directory (writes under
  **`_upstream_snapshot/replayt-docs/`** only). Do not `git add` **`_upstream_snapshot/`**. The script is optional and
  never required for **CI** or `pytest`.

Normative layout and acceptance checklist **RD1**–**RD8** (pytest enforces the full set via **`tests/test_reference_documentation_workflow.py`**):
**[docs/SPEC_REFERENCE_DOCUMENTATION.md](docs/SPEC_REFERENCE_DOCUMENTATION.md)**.

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

**Optional webhook diagnostics:** Default is **off** (no extra per-request **`logging`** records on the webhook path).
Enable structured **INFO** lines with redacted headers, response status, body length, and (when the POST parses as a
supported lifecycle event) correlation ids from **verified** JSON—**never** the raw POST body or full signature values.
Normative rules: **[docs/SPEC_STRUCTURED_LOGGING_REDACTION.md](docs/SPEC_STRUCTURED_LOGGING_REDACTION.md)** (**§ Optional
diagnostic logging**).

| Switch | Effect |
| ------ | ------ |
| **`REPLAYT_LIFECYCLE_WEBHOOK_DIAGNOSTICS`** | If set to **`1`**, **`true`**, **`yes`**, or **`on`** (case-insensitive), enables diagnostics for WSGI apps that use the default **`webhook_diagnostics=None`**. |
| **`python -m replayt_lifecycle_webhooks --webhook-diagnostics`** | Forces diagnostics **on** for that process. |
| **`python -m replayt_lifecycle_webhooks --no-webhook-diagnostics`** | Forces diagnostics **off**, even when the environment variable is set. |
| **`make_lifecycle_webhook_wsgi_app(..., webhook_diagnostics=…)`** / **`make_reference_lifecycle_webhook_wsgi_app`** | **`True`** or **`False`** overrides the environment variable; **`None`** reads **`REPLAYT_LIFECYCLE_WEBHOOK_DIAGNOSTICS`**. |

Configure the stdlib logger **`replayt_lifecycle_webhooks.handler`** (for example level **INFO** and your handler of
choice). With logging enabled, a representative record’s **`extra`** fields resemble:

```python
{
    "webhook_method": "POST",
    "webhook_path": "/webhook",
    "webhook_status_code": 204,
    "webhook_body_bytes_len": 120,
    "webhook_headers": {
        "Content-Type": "application/json; charset=utf-8",
        "Replayt-Signature": "[REDACTED]",
        "Authorization": "[REDACTED]",
    },
    "lifecycle_event_id": "00000000-0000-4000-8000-000000000001",
    "lifecycle_run_id": "run_example_id",
    "lifecycle_workflow_id": "wf_example",
}
```

Secondary console scripts (equivalent): **`replayt-lifecycle-webhooks-serve`** (reference server),
**`replayt-lifecycle-webhooks-demo-post`** (signed demo POST).

## Running tests

From the repository root after a dev install:

```bash
pytest tests -q
```

Lint and format (same paths as CI; **`ruff`** is in **`[project.optional-dependencies] dev`**):

```bash
ruff check src tests
ruff format --check src tests
```

The same checks can run as optional **Git** hooks via **`.pre-commit-config.yaml`**; see **[CONTRIBUTING.md](CONTRIBUTING.md)**
(**Optional pre-commit (ruff)**).

The **normative** full suite is defined in **[docs/SPEC_AUTOMATED_TESTS.md](docs/SPEC_AUTOMATED_TESTS.md)** and
**[docs/SPEC_REPLAYT_BOUNDARY_TESTS.md](docs/SPEC_REPLAYT_BOUNDARY_TESTS.md)**: **unit / contract** tests (signature
verification, lifecycle JSON parsing, handler behavior, doc guards) and **replayt boundary** tests that **`import replayt`**
and lock **EVENTS.md**-listed symbols (**R1–R5**). **`pytest tests -q`** is the contributor **test** entrypoint; **CI**
also runs **ruff** on **`src/`** and **`tests/`** (see **`.github/workflows/ci.yml`**). The same command includes a
**loopback-only** subprocess check (**`tests/test_reference_server_subprocess.py`**, backlog **`83e07114`**) that starts
**`python -m replayt_lifecycle_webhooks`** with no outbound or public network I/O.

**Focused runs (optional):**

```bash
pytest tests/test_webhook_signature.py tests/test_lifecycle_events.py -q   # crypto + parsing only (example)
pytest tests -m replayt_boundary -q                                         # replayt import + symbol checks only
pytest tests/test_reference_server_subprocess.py -q                         # reference server via python -m; loopback POST
pytest tests/test_reference_http_server_route_map_doc.py -q                 # route map spec + README link (backlog b4c68e50)
pytest tests/test_pip_audit_suppression_alignment.py -q                     # pip-audit ignores vs DEPENDENCY_AUDIT.md (bea2900c)
python scripts/pip_audit_suppression_alignment.py                           # same check without pytest (needs dev install for PyYAML)
```

**Property / fuzz tests (optional, backlog `dcffe5d5`):** install **`[property]`** (adds **Hypothesis**), then run
**`pytest tests -m property_fuzz -q`**. Without that extra, **`tests/test_property_fuzz_signature.py`** and
**`tests/test_property_fuzz_parse.py`** skip at import (**`pytest.importorskip`**), so the default suite stays lean.
Normative rows **PF1**–**PF10**: **[docs/SPEC_AUTOMATED_TESTS.md](docs/SPEC_AUTOMATED_TESTS.md)** (**§ Backlog `dcffe5d5`**).

Checklist rows **A1–A5** (minimum verification / parsing), **R1–R5**, and **G1–G7** (version bump guardrails): **SPEC_AUTOMATED_TESTS** and
**SPEC_REPLAYT_BOUNDARY_TESTS**.

**Upstream / network checks:** There is no opt-in **pytest** marker for live PyPI or other outbound **replayt** probes in this tree. Merge-blocking **pytest** stays network-free per **SPEC_REPLAYT_BOUNDARY_TESTS** **G3**; optional cron workflows would be documented here if added (**G4** / **G5**).

## Troubleshooting

**Stable response fixtures (gateways / contract tests):** Copy **HTTP status**, **`Content-Type`**, and compact JSON bodies
from **[docs/SPEC_WEBHOOK_FAILURE_RESPONSES.md § Canonical end-to-end examples](docs/SPEC_WEBHOOK_FAILURE_RESPONSES.md#canonical-end-to-end-examples)**
— one normative example per stable **`error`** code (and **204** success described there as an empty body).

**Wrong or rotated shared secret:** If the HMAC key on the receiver does not match the sender, verification fails with
**`signature_mismatch`**. Use one secret out of band on both sides and roll receivers before retiring an old key.

**Body not raw bytes:** JSON parsing, whitespace edits, or re-encoding before verification breaks the MAC. Feed the
**exact** POST **bytes** from the HTTP layer into verification; raw-body rules live in
**[docs/SPEC_WEBHOOK_SIGNATURE.md](docs/SPEC_WEBHOOK_SIGNATURE.md)**.

**`Replayt-Signature` header mistakes:** The header must follow the **v1** **`sha256=<hex>`** shape. Wrong names,
truncated values, or missing headers surface **`signature_required`**, **`signature_malformed`**, or **`signature_mismatch`**
per **[docs/SPEC_WEBHOOK_FAILURE_RESPONSES.md](docs/SPEC_WEBHOOK_FAILURE_RESPONSES.md)**.

**Treating delivery as exactly-once:** Assume **at-least-once** on the wire. After a good MAC, dedupe with **`event_id`**
and an idempotency store whose **TTL** covers retries and approval windows. Full rules and legacy fallbacks:
**[docs/SPEC_DELIVERY_IDEMPOTENCY.md](docs/SPEC_DELIVERY_IDEMPOTENCY.md)**.

**Stale or replayed captures with a valid MAC:** Signing does not prove freshness. Constrain **`occurred_at`** (and
optional **`Replayt-*`** headers or a nonce) per **[docs/SPEC_REPLAY_PROTECTION.md](docs/SPEC_REPLAY_PROTECTION.md)**.
**Benign duplicates** (same **`event_id`**, idempotent **2xx**) differ from **policy rejects** (**422** /
**`replay_rejected`**); map the latter using **[docs/SPEC_WEBHOOK_FAILURE_RESPONSES.md](docs/SPEC_WEBHOOK_FAILURE_RESPONSES.md)**.

**Reverse proxy / TLS in front of the reference server:** Preserve the raw POST body, set sane body limits and timeouts,
and avoid **`Transfer-Encoding`** pitfalls. Copy-paste **nginx** (or adapt for **Caddy**) patterns in
**[docs/OPERATOR_REVERSE_PROXY.md](docs/OPERATOR_REVERSE_PROXY.md)**.

**Where to look in logs:** Prefer structured **`extra=`** keys such as **`webhook_*`**, **`lifecycle_*`**, and
**`error_code`**, with headers and dict values passed through **`replayt_lifecycle_webhooks.redaction`** as in
**[docs/SPEC_STRUCTURED_LOGGING_REDACTION.md](docs/SPEC_STRUCTURED_LOGGING_REDACTION.md)**. That spec lists defaults
(**`Authorization`**, **`Replayt-Signature`**, and related) and what must never appear in log records.

## Approval webhook flow

**Approval** and **run** deliveries share the same bar: verify **`Replayt-Signature`** on the **raw body**, then parse JSON
(**[docs/SPEC_WEBHOOK_SIGNATURE.md](docs/SPEC_WEBHOOK_SIGNATURE.md)**).

Approval-related **`event_type`** values are defined in **[docs/EVENTS.md](docs/EVENTS.md)**:

- **`replayt.lifecycle.approval.pending`** — automation is blocked until a decision exists.
- **`replayt.lifecycle.approval.resolved`** — a decision was recorded (approved or rejected; see **`detail`** in **EVENTS.md**).

When **`correlation.approval_request_id`** is present, use it to tie deliveries to tickets or support notes. This package
does **not** implement approval UIs or policy; your handler runs **after** verification and owns UX and automation.

```mermaid
sequenceDiagram
  participant Sender as Sender
  participant Post as HTTPS POST
  participant Rx as Receiver
  participant H as Idempotent handler
  Sender->>Post: Lifecycle body + Replayt-Signature
  Post->>Rx: Raw bytes + headers
  Rx->>Rx: Verify MAC
  Rx->>H: Parsed JSON (after verify)
  Note over H: Dedupe on event_id; optional ticket or notify
```

## Verifying webhook signatures

Verify the **raw request body** with your shared secret and the **`Replayt-Signature`** header before parsing JSON or
running automation. For **FastAPI**, **Starlette**, or other **ASGI** apps, read **`await request.body()`** (or equivalent)
before **`json.loads`** or typed body parsing—copy-paste patterns and **401**/**403** mapping are in
**[docs/SPEC_INTEGRATOR_ASGI_VERIFIED_FIRST.md](docs/SPEC_INTEGRATOR_ASGI_VERIFIED_FIRST.md)**. Ordered steps for handlers:
**[Verification procedure](docs/SPEC_WEBHOOK_SIGNATURE.md#verification-procedure-integrators)** in
**[docs/SPEC_WEBHOOK_SIGNATURE.md](docs/SPEC_WEBHOOK_SIGNATURE.md)**. Full contract detail also in
**[docs/reference-documentation/REPLAYT_WEBHOOK_SIGNING.md](docs/reference-documentation/REPLAYT_WEBHOOK_SIGNING.md)**.

**Signing secret configuration:** this package does **not** read the environment for you. Operators should configure one
shared secret out of band and pass it into **`verify_lifecycle_webhook_signature`**. **Recommended environment variable
name:** **`REPLAYT_LIFECYCLE_WEBHOOK_SECRET`** (string secret; UTF-8 when used as the HMAC key via a `str` argument).
Load it with your framework or `os.environ`, inject via a secret manager in production, and **never** log the raw value.

**Offline CLI (saved captures):** **`python -m replayt_lifecycle_webhooks verify`** checks a file of raw POST bytes (or stdin
when **`BODY`** is **`-`**) against a captured **`Replayt-Signature`** value using the same **v1** rules as the library.
Set **`REPLAYT_LIFECYCLE_WEBHOOK_SECRET`** (or pass **`--secret`** only for local debugging). Exit **0** prints **`ok`**;
**1** means the MAC did not verify; **2** means fix usage, secret, or I/O.

```bash
export REPLAYT_LIFECYCLE_WEBHOOK_SECRET='your-shared-secret'
python -m replayt_lifecycle_webhooks verify --signature "$REPLAYT_SIGNATURE" /path/to/captured_body.bin
```

Full contract: **[docs/SPEC_CLI_VERIFY_SAVED_WEBHOOK.md](docs/SPEC_CLI_VERIFY_SAVED_WEBHOOK.md)**.

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
keys; use **`extra_sensitive_names`** / **`extra_sensitive_keys`** for deployment-specific names. **`format_safe_webhook_log_extra`**
**must not** put raw body text or JSON snapshots into **`extra=`** by default—only safe summaries such as
**`webhook_body_bytes_len`** (see the spec’s **successful delivery** example). **Do not** log the **raw body**, **full**
signature header, **computed MAC**, or **HMAC secret** (same boundaries as
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

# After verify: ``raw_body`` is the POST bytes; ``parsed`` is the verified JSON object.
# Never pass raw body text into ``extra=`` — only ``webhook_body_bytes_len`` and safe fields.
extra_ok = format_safe_webhook_log_extra(
    method="POST",
    path="/webhook",
    status_code=204,
    headers=request_headers,
    webhook_body_bytes_len=len(raw_body),
    lifecycle_event_id=parsed["event_id"],
    lifecycle_run_id=parsed["correlation"]["run_id"],
    lifecycle_workflow_id=parsed["correlation"]["workflow_id"],
)
log.info("webhook accepted", extra=extra_ok)

# Or redact a header map before formatting your own message:
log.debug("headers=%s", redact_headers(request_headers))
```

**Drop-in HTTP handler:** **`handle_lifecycle_webhook_post`** maps a POST, raw body, and header map to status **405** /
**401** / **403** / **400** / **422** / **204** as in **[docs/SPEC_MINIMAL_HTTP_HANDLER.md](docs/SPEC_MINIMAL_HTTP_HANDLER.md)**.
**MAC mismatch** uses **403**; missing or malformed **`Replayt-Signature`** uses **401**. Verification runs before
**`json.loads`**. Optional **`dedup_store`** and **`replay_policy`** implement **`event_id`** dedupe and **`occurred_at`**
freshness after verify (**[docs/SPEC_REPLAY_PROTECTION.md](docs/SPEC_REPLAY_PROTECTION.md)**).

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
| `docs/SPEC_PUBLIC_API.md` | Supported public imports (`__all__`), internal modules until 1.0, semver + deprecation + **CHANGELOG** rules |
| `docs/SPEC_REPLAYT_DEPENDENCY.md` | **replayt** range: contract, **compatibility matrix** (**replayt**, **`requires-python`**, CI-tested Python), upper-bound policy, checklist, CI expectations |
| `docs/SPEC_AUTOMATED_TESTS.md` | **pytest** / **ruff** / CI entrypoint, minimum verification + parsing coverage, no smoke-only **`assert True`** |
| `docs/SPEC_WEBHOOK_SIGNATURE.md` | Incoming webhook signature verification: API contract, tests, upstream alignment |
| `docs/SPEC_MINIMAL_HTTP_HANDLER.md` | Optional minimal HTTP POST handler: mounting, status codes, acceptance **H1–H12** |
| `docs/SPEC_INTEGRATOR_ASGI_VERIFIED_FIRST.md` | Integrator recipe: raw body + verify-before-JSON for **FastAPI** / **Starlette** (**AF1**–**AF7**; backlog **`c631fe3f`**) |
| `docs/SPEC_HTTP_SERVER_ENTRYPOINT.md` | Reference HTTP server: one start command, **POST** route, **`GET /health`**, acceptance **S1–S13** |
| `docs/SPEC_REFERENCE_HTTP_SERVER_ROUTE_MAP.md` | Gateway-oriented **path / method / HTTP status** matrix; backlog **`b4c68e50`**, acceptance **RM1**–**RM7** |
| `docs/SPEC_REVERSE_PROXY_REFERENCE_SERVER.md` | Normative contract for **`docs/OPERATOR_REVERSE_PROXY.md`**: nginx/Caddy-style proxy, raw body, limits, timeouts; **pytest** **OG1**–**OG8** |
| `docs/OPERATOR_REVERSE_PROXY.md` | Operator guide: reverse proxy in front of **`python -m replayt_lifecycle_webhooks`** (**OG1**–**OG8**; backlog **`dc212184`**) |
| `docs/SPEC_LOCAL_WEBHOOK_DEMO.md` | Local demo: one command POSTs signed fixtures to default listener; acceptance **D1–D9** |
| `replayt_lifecycle_webhooks.demo_webhook` | **`python -m replayt_lifecycle_webhooks.demo_webhook`**: signed POST to default **`/webhook`** URL |
| `replayt_lifecycle_webhooks/fixtures/events/` | Packaged JSON presets aligned with **`tests/fixtures/events/`** for **`pip install`** demos |
| `docs/SPEC_WEBHOOK_FAILURE_RESPONSES.md` | Operator-facing HTTP + JSON failure contract; canonical end-to-end examples; logging boundaries |
| `docs/SPEC_STRUCTURED_LOGGING_REDACTION.md` | Structured **`logging`** helpers; default sensitive-key redaction; tests **L1–L9** |
| `docs/SPEC_METRICS_HOOKS.md` | Optional **`LifecycleWebhookMetrics`** / **`metrics=`** contract; verify vs handler timing; tests **M1**–**M8** (backlog **`42b8d5a9`**) |
| `docs/SPEC_README_OPERATOR_SECTIONS.md` | Normative **README** operator sections (**Troubleshooting**, **Approval webhook flow**, **Verifying**); tests **OP1–OP9** |
| `docs/EVENTS.md` | Lifecycle webhook JSON: **`event_type`**, **`occurred_at`**, **`event_id`**, correlation ids, **`summary`**, **`schema_version`**, synthetic examples |
| `docs/SPEC_DELIVERY_IDEMPOTENCY.md` | At-least-once delivery assumptions, **`event_id`** dedupe rules, idempotency store TTL guidance |
| `docs/SPEC_REPLAY_PROTECTION.md` | Stale capture replay vs duplicates; **`occurred_at`** freshness; optional headers; dedupe store protocol; **RP4**/**RP5** |
| `docs/schemas/lifecycle_webhook_payload-1-0.schema.json` | Informative JSON Schema for **`1.0`**-family payloads (non-Python integrators) |
| `docs/SPEC_REFERENCE_DOCUMENTATION.md` | Optional **`docs/reference-documentation/`** workflow: what to commit, local `_upstream_snapshot/`, CI hygiene, licensing, snapshot commands; **RD1**–**RD8** |
| `CONTRIBUTING.md` | Contributor entry; optional reference-documentation snapshot task (links **SPEC_REFERENCE_DOCUMENTATION**) |
| `docs/reference-documentation/README.md` | Folder guide: optional use, refresh hints, link to spec |
| `docs/reference-documentation/` | Optional markdown for contributors; committed excerpts (e.g. `REPLAYT_WEBHOOK_SIGNING.md`); bulk copies local-only under `_upstream_snapshot/` (gitignored) |
| `src/replayt_lifecycle_webhooks/` | Python package: `signature`, `handler`, `events`, `redaction`, `serve`; **`__main__`** for **`python -m`** |
| `pyproject.toml` | Package metadata |
| `CHANGELOG.md` | Release notes (Keep a Changelog); keep **Unreleased** updated |
| `.gitignore` | Ignores `path/` (doc placeholders), `docs/reference-documentation/_upstream_snapshot/`, `.orchestrator/`, `.cursor/skills/`, and `AGENTS.md` (local tooling) |
