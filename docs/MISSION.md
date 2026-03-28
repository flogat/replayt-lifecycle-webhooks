# Mission: Signed HTTP webhooks for replayt run and approval lifecycle events

**Skim (integrators).** This package is **consumer-side**: you get a **small, tested** primitive to confirm a webhook
POST matches **`Replayt-Signature`** (HMAC over the **raw body**) before you parse JSON or drive automation. It is
**not** a fork of [replayt](https://pypi.org/project/replayt/); the supported **replayt** floor and verification rules
live **here**—see **[SPEC_REPLAYT_DEPENDENCY.md](SPEC_REPLAYT_DEPENDENCY.md)**,
**[SPEC_WEBHOOK_SIGNATURE.md](SPEC_WEBHOOK_SIGNATURE.md)**, and the optional HTTP helper spec
**[SPEC_MINIMAL_HTTP_HANDLER.md](SPEC_MINIMAL_HTTP_HANDLER.md)**. Repository map and quick links:
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
  upstream are **tracked** here via tests, **CHANGELOG.md**, and optional material under **`docs/reference-documentation/`**.
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
- **Failure mapping** — Map verification failures to **401/403** (or your policy) and **avoid leaking** the secret,
  full signature header, or computed MAC in responses or logs, per **SPEC_WEBHOOK_SIGNATURE**. For stable JSON **`error`**
  codes, example bodies, and post-verify failures (**unknown `event_type`**, replay windows), see
  **[SPEC_WEBHOOK_FAILURE_RESPONSES.md](SPEC_WEBHOOK_FAILURE_RESPONSES.md)**.
- **Payload semantics and privacy** — After verification, **you** decide how to parse JSON, authorize actions, and handle
  **PII or business data** in the body. This package’s contract is **cryptographic integrity** of the octets, not
  redaction or validation of arbitrary JSON fields (unless a spec in this repo explicitly documents them).

## Scope

### In scope

- Documented **replayt** minimum version in `pyproject.toml` and **[SPEC_REPLAYT_DEPENDENCY.md](SPEC_REPLAYT_DEPENDENCY.md)**.
- **Public** verification helper(s) with **unit tests** that do **not** require the network.
- **[README.md](../README.md)** and spec docs integrators can copy from; **CHANGELOG.md** for user-visible changes.
- **CI** that installs the package and runs the **automated test suite** (see **Success metrics (v0.x)**).

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

- **Automated tests** (e.g. **pytest**) run in **CI** on every change workflow the project uses; they cover claimed
  verification behavior, dependency contract checks, and spec-driven acceptance where implemented—**green CI** is part
  of “done.” The suite must **not** rely on placeholder tests (e.g. bare **`assert True`**) as the only proof that
  verification or parsing works; see **[SPEC_AUTOMATED_TESTS.md](SPEC_AUTOMATED_TESTS.md)** for the CI entrypoint and
  minimum behavioral coverage.
- **Releases and versioning** — Public API and dependency contract changes are tracked under **[Semantic Versioning](https://semver.org/spec/v2.0.0.html)** as declared in **`CHANGELOG.md`**; cutting a release means updating the version in **`pyproject.toml`**, grouping **Unreleased** notes into a dated section, and publishing to PyPI (or the project’s canonical index) per maintainer practice. Integrators rely on the **replayt** lower bound and changelog for upgrade safety (**[SPEC_REPLAYT_DEPENDENCY.md](SPEC_REPLAYT_DEPENDENCY.md)**).
- **CHANGELOG.md** records user-visible API and dependency changes under **Unreleased** (or the releasing section) per
  project convention.
- Operators can adopt verification using **[README.md](../README.md)** + **SPEC_WEBHOOK_SIGNATURE.md** without reading the whole tree.

## Doc hygiene (checklist)

When you change behavior or contracts:

- [ ] Update the relevant **spec** and **[README.md](../README.md)** if integrator-facing text changes.
- [ ] Add **CHANGELOG.md** **Unreleased** notes for user-visible API, dependency, or notable doc contract changes.
- [ ] Keep **MISSION** scope/success consistent with **DESIGN_PRINCIPLES** and what **CI** actually runs.
