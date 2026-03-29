# Mission: Signed HTTP webhooks for replayt run and approval lifecycle events

**Skim (integrators).** This package is **consumer-side**: you get a **small, tested** primitive to confirm a webhook
POST matches **`Replayt-Signature`** (HMAC over the **raw body**) before you parse JSON or drive automation. It is
**not** a fork of [replayt](https://pypi.org/project/replayt/); the supported **replayt** floor and verification rules
live **here**—see **[SPEC_REPLAYT_DEPENDENCY.md](SPEC_REPLAYT_DEPENDENCY.md)**,
**[SPEC_WEBHOOK_SIGNATURE.md](SPEC_WEBHOOK_SIGNATURE.md)**, the optional HTTP helper spec
**[SPEC_MINIMAL_HTTP_HANDLER.md](SPEC_MINIMAL_HTTP_HANDLER.md)**, and the optional **reference server** contract
**[SPEC_HTTP_SERVER_ENTRYPOINT.md](SPEC_HTTP_SERVER_ENTRYPOINT.md)** (one documented start command when implemented);
**path / method / status** matrix for gateways:
**[SPEC_REFERENCE_HTTP_SERVER_ROUTE_MAP.md](SPEC_REFERENCE_HTTP_SERVER_ROUTE_MAP.md)**.
**Reverse proxy / TLS** in front of the reference server (raw body, limits, timeouts): **[SPEC_REVERSE_PROXY_REFERENCE_SERVER.md](SPEC_REVERSE_PROXY_REFERENCE_SERVER.md)**; operator guide **[OPERATOR_REVERSE_PROXY.md](OPERATOR_REVERSE_PROXY.md)**.
Local **signed demo POST** contract (contributor try-it flow): **[SPEC_LOCAL_WEBHOOK_DEMO.md](SPEC_LOCAL_WEBHOOK_DEMO.md)**.
**Structured logging** with default **redaction** for sensitive headers and metadata:
**[SPEC_STRUCTURED_LOGGING_REDACTION.md](SPEC_STRUCTURED_LOGGING_REDACTION.md)**.
**Delivery retries and `event_id` idempotency:**
**[SPEC_DELIVERY_IDEMPOTENCY.md](SPEC_DELIVERY_IDEMPOTENCY.md)**.
**Replay protection** (freshness, optional wire headers, dedupe store hooks):
**[SPEC_REPLAY_PROTECTION.md](SPEC_REPLAY_PROTECTION.md)**.
**Public Python import surface** and **deprecation** policy (**`__all__`**, internal modules, **CHANGELOG** alignment):
**[SPEC_PUBLIC_API.md](SPEC_PUBLIC_API.md)**.
**PM/support lifecycle digests** (fixed English lines and **`digest/1`** record from parsed events; **DG0**–**DG6**):
**[SPEC_EVENT_DIGEST.md](SPEC_EVENT_DIGEST.md)**.
Repository map and quick links:
**[README.md](../README.md)**.

## Ecosystem positioning

**Primary pattern:** **Core-gap** (see taxonomy in **[REPLAYT_ECOSYSTEM_IDEA.md](REPLAYT_ECOSYSTEM_IDEA.md)**). Replayt
upstream defines lifecycle **semantics** and **signing** on the wire; it does not ship this repository’s **Python**
verification surface, tests, and copy-paste handler contracts. This package fills that gap **on the consumer side**
without forking or steering core.

## Users and problem

**Operators and integrators** need to trust that an HTTP callback really came from their **replayt** (or compatible)
automation before they record outcomes, notify users, or trigger downstream systems. **Run** lifecycle deliveries tell
you how a workflow progressed (for example completion or failure). **Approval** deliveries tell you when a human or
policy gate must be satisfied before work continues. Without a shared contract for **signing** and **verification**,
teams either skip checks (risky) or reimplement crypto and HTTP edge cases inconsistently.

This repository’s job is to narrow that gap: document the wire rules, ship a **verified-first** verification helper and
optional HTTP glue, and keep **CI** and tests aligned so adopters can copy a **known-good** path.

| Audience | What they need from this repo |
| -------- | ------------------------------ |
| **Integrators** | A **correct, copy-friendly** verification path and normative handler steps without mandatory full HTTP-framework dependencies from this package. |
| **Maintainers** | Explicit contracts for **replayt** versions and **signature verification**, consistent with **[DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)**. |
| **Contributors** | Clear **scope**, **success bar**, and pointers to specs and **CI** expectations. |

## Replayt’s role vs this repository

- **Replayt** (upstream) defines **event semantics**—what “run” and “approval” mean on the wire, when deliveries fire,
  and how payloads are **signed**. This repository **does not** redefine those product moments; it **documents and tests**
  **consumer-side verification** so your endpoint can authenticate the **bytes** replayt (or a compatible sender) POSTs.
- **Version alignment** — A declared **`replayt`** minimum in `pyproject.toml` (lower bound) so installs and docs agree;
  bump policy and checklists: **[SPEC_REPLAYT_DEPENDENCY.md](SPEC_REPLAYT_DEPENDENCY.md)**.
- **Lifecycle delivery contract** — Run and approval events are delivered over HTTP with signing as upstream documents;
  this repo implements **verification** and documents headers/body rules for Python handlers. Algorithm or header changes
  upstream are **tracked** here via tests, **CHANGELOG.md**, and optional material under **`docs/reference-documentation/`**
  (layout and contributor workflow: **[SPEC_REFERENCE_DOCUMENTATION.md](SPEC_REFERENCE_DOCUMENTATION.md)**).
- **Standard-library crypto** — Verification uses **stdlib** **`hmac` / `hashlib`** where the published contract allows;
  no requirement to patch **replayt** core from this repository.
- This repository does **not** exist to steer replayt core; propose upstream changes through normal channels (see
  **[DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)**).

## Lifecycle moments: run vs approval

For **scope and stakeholder clarity**, distinguish two kinds of **lifecycle** traffic this package is built to **authenticate**
(not to fully interpret):

| Moment | Plain language | Consumer takeaway |
| ------ | ---------------- | ----------------- |
| **Run** | The automation **executed** (or reported) a workflow step—progress, completion, failure, or similar **run-time** outcomes. | Your webhook handler may update run state, metrics, or notifications **after** verification. Event **meaning** lives in upstream docs and JSON fields; **integrity** is **`Replayt-Signature` + raw body**. |
| **Approval** | Work is **blocked** until a person or rule **approves** (or rejects) a pending step—e.g. “pending approval” and follow-up resolution. | Same verification bar as run deliveries: **verify first**, then parse JSON and drive **your** approval UX, ticketing, or policy engine. This package does not implement approval workflows; it helps you **trust the POST**. |

**For PM, support, and program stakeholders (approval).** When a workflow hits an **approval** gate, replayt (or your
deployment) may send a **signed** webhook so your systems know an approval is **pending** or has been **resolved**
without polling the core product. This repository does **not** replace your approval UI or identity model—it gives
engineering a **small, testable** way to prove the callback was **not** forged before you file tickets, send customer
emails, or unlock the next automation step. If verification fails, treat the delivery as **untrusted** and use your
normal incident or retry paths; do not act on the JSON as if it were authentic.

## Consumer responsibilities

Integrators and operators are responsible for:

- **Shared secret** — Configure one secret out of band and pass it into **`verify_lifecycle_webhook_signature`** (or
  equivalent). This library does **not** read the environment for you; see **[README.md](../README.md)** and **SPEC_WEBHOOK_SIGNATURE** for
  the recommended env var name and hygiene.
- **Raw body discipline** — Provide the **exact** request body **bytes** from the HTTP layer **before** JSON parsing or
  mutation; otherwise the MAC will not match.
- **Idempotent handling** — Assume **at-least-once** delivery; after verification, dedupe with **`event_id`** (and an
  idempotency store with an appropriate **TTL**) per **[SPEC_DELIVERY_IDEMPOTENCY.md](SPEC_DELIVERY_IDEMPOTENCY.md)** so
  retries do not double-charge approvals, tickets, or metrics.
- **Replay and freshness** — After verification, constrain **stale** or **replayed** captures (payload **`occurred_at`**
  vs receiver time, optional headers, pluggable store) per **[SPEC_REPLAY_PROTECTION.md](SPEC_REPLAY_PROTECTION.md)** in
  addition to **`event_id`** dedupe.
- **Failure mapping** — Map verification failures to **401/403** (or your policy) and **avoid leaking** the secret,
  full signature header, or computed MAC in responses or logs, per **SPEC_WEBHOOK_SIGNATURE**. For stable JSON **`error`**
  codes, example bodies, and post-verify failures (**unknown `event_type`**, replay windows), see
  **[SPEC_WEBHOOK_FAILURE_RESPONSES.md](SPEC_WEBHOOK_FAILURE_RESPONSES.md)**.
- **Production logging** — Use **[SPEC_STRUCTURED_LOGGING_REDACTION.md](SPEC_STRUCTURED_LOGGING_REDACTION.md)** as the
  **normative** contract for **stdlib** **`logging`**: default sensitive **header** and **`extra=`** key lists,
  **`[REDACTED]`** placeholder, **`redact_headers`** / **`redact_mapping`** / **`format_safe_webhook_log_extra`**, the
  **never-log** rules (no full raw body; redact **`Authorization`**, **`Replayt-Signature`**, and related defaults), and the
  **§ Example: successful verified delivery** shape. **`pytest`** rows **L1–L9** (backlog **`fa75ecf3`**) prove the
  behavior once implemented. For correlation, prefer **`event_id`** and **`correlation.run_id`**,
  **`correlation.workflow_id`**, and **`correlation.approval_request_id`** from **verified** payloads per
  **[EVENTS.md](EVENTS.md)** — not unverified JSON strings.
- **Payload semantics and privacy** — After verification, **you** decide how to parse JSON, authorize actions, and handle
  **PII or business data** in the body. This package’s contract is **cryptographic integrity** of the octets, not
  redaction or validation of arbitrary JSON fields (unless a spec in this repo explicitly documents them).

## Scope

### In scope

- Documented **replayt** minimum version in `pyproject.toml` and **[SPEC_REPLAYT_DEPENDENCY.md](SPEC_REPLAYT_DEPENDENCY.md)**.
- **Public** verification helper(s) with **unit tests** that do **not** require the network.
- **[README.md](../README.md)** and spec docs integrators can copy from; **CHANGELOG.md** for user-visible changes.
- **CI** that installs the package and runs the **automated test suite** (see **Success metrics (v0.x)**).
- **Structured logging** helpers with **default redaction** for sensitive headers and metadata dict keys, per
  **[SPEC_STRUCTURED_LOGGING_REDACTION.md](SPEC_STRUCTURED_LOGGING_REDACTION.md)** (**stdlib** **`logging`**; **no** new
  mandatory dependencies; **L1–L9** in **SPEC_AUTOMATED_TESTS** when implemented).

### Out of scope

- Patching or vendoring **replayt** core.
- Shipping a **mandatory** Starlette/FastAPI/Flask (or similar) stack as part of this package’s required surface—integrators
  wrap the primitive in their own HTTP layer.
- Arbitrary third-party webhook providers unless their contract **matches** the replayt-compatible signing rules
  documented here.
- **Secret handling inside JSON payloads** beyond what integrator-facing specs explicitly document (e.g. recommended env
  var for the **HMAC key**). This repo does **not** define a standard for embedding, rotating, or scrubbing secrets **inside**
  webhook JSON; operators must follow upstream replayt documentation and their own security policies for payload contents.
- **Enterprise** positioning narratives and extended **LLM**/demo policy on this page for **v0.x**—defer those to
  **[DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)** (and extend MISSION when the project needs them).

## Success metrics (v0.x)

- **Automated tests** (e.g. **pytest**) and **ruff** lint/format checks (**`src/`**, **`tests/`**, see **[SPEC_AUTOMATED_TESTS.md](SPEC_AUTOMATED_TESTS.md)** **RF1**–**RF5**) run in **CI** on every change workflow the project uses; merge-blocking **`lint`** and **`test`** jobs **must** exercise the **`requires-python` floor (3.11)** per **[SPEC_REPLAYT_DEPENDENCY.md](SPEC_REPLAYT_DEPENDENCY.md)** and **SPEC_AUTOMATED_TESTS** **§ Backlog `6cd22a7b`**. The suite **must** cover
  claimed verification behavior, dependency contract checks, and spec-driven acceptance where implemented—**green CI** is part
  of “done.” It **must** also include **replayt** boundary coverage (**`import replayt`**, documented symbols **R1–R5**) per
  **[SPEC_REPLAYT_BOUNDARY_TESTS.md](SPEC_REPLAYT_BOUNDARY_TESTS.md)** in addition to **[SPEC_AUTOMATED_TESTS.md](SPEC_AUTOMATED_TESTS.md)**
  (signature / parsing minima). When **SPEC_STRUCTURED_LOGGING_REDACTION** is implemented, the suite **must** also satisfy
  checklist **L1–L9** for that backlog. The suite must **not** rely on placeholder tests (e.g. bare **`assert True`**) as the only
  proof that verification or parsing works. Contributors run **`pytest tests -q`** for the full collection; **[README.md](../README.md)**
  (**Running tests**) lists optional focused commands.
- **Packaging gate (PyPI readiness)** — **CI** runs **`python -m build`** and **`twine check`** on the **sdist** and **wheel**
  (**job `package`** in **`.github/workflows/ci.yml`**; backlog **`78e3554b`**). The **pytest** suite checks **declared package data**
  per **[SPEC_AUTOMATED_TESTS.md](SPEC_AUTOMATED_TESTS.md)** **§ Backlog `78e3554b`** (**PK1**–**PK7**). **PEP 561** marker
  **`py.typed`** and optional static typing expectations are specified under **§ Backlog `2ec2c21c`** (**TP1**–**TP6**);
  integrator summary: **SPEC_PUBLIC_API.md**, **§ Static typing (PEP 561)**. This catches broken metadata or missing
  distribution files **before** a release tag.
- **Releases and versioning** — Public API and dependency contract changes are tracked under **[Semantic Versioning](https://semver.org/spec/v2.0.0.html)** as declared in **`CHANGELOG.md`**; cutting a release means updating the version in **`pyproject.toml`**, grouping **Unreleased** notes into a dated section, and publishing to PyPI (or the project’s canonical index) per maintainer practice. Integrators rely on the **replayt** lower bound and changelog for upgrade safety (**[SPEC_REPLAYT_DEPENDENCY.md](SPEC_REPLAYT_DEPENDENCY.md)**).
- **CHANGELOG.md** records user-visible API and dependency changes under **Unreleased** (or the releasing section) per
  project convention.
- Operators can adopt verification using **[README.md](../README.md)** + **SPEC_WEBHOOK_SIGNATURE.md** without reading the whole tree. Operator-focused **README** structure (troubleshooting, high-level **approval** path, copy-paste signature checks) is specified in **[SPEC_README_OPERATOR_SECTIONS.md](SPEC_README_OPERATOR_SECTIONS.md)**; **pytest** rows **OP1**–**OP8** in **SPEC_AUTOMATED_TESTS** are enforced by **`tests/test_readme_operator_sections.py`**.

## Doc hygiene (checklist)

When you change behavior or contracts:

- [ ] Update the relevant **spec** and **[README.md](../README.md)** if integrator-facing text changes.
- [ ] Add **CHANGELOG.md** **Unreleased** notes for user-visible API, dependency, or notable doc contract changes.
- [ ] Keep **MISSION** scope/success consistent with **DESIGN_PRINCIPLES** and what **CI** actually runs.
