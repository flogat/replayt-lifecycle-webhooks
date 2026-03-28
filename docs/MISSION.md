# Mission: Signed HTTP webhooks for replayt run and approval lifecycle events

**Skim (integrators).** This package is **consumer-side**: you get a **small, tested** primitive to confirm a webhook
POST matches **`Replayt-Signature`** (HMAC over the **raw body**) before you parse JSON or drive automation. It is
**not** a fork of [replayt](https://pypi.org/project/replayt/); the supported **replayt** floor and verification rules
live **here**—see **[SPEC_REPLAYT_DEPENDENCY.md](SPEC_REPLAYT_DEPENDENCY.md)**,
**[SPEC_WEBHOOK_SIGNATURE.md](SPEC_WEBHOOK_SIGNATURE.md)**, and the optional HTTP helper spec
**[SPEC_MINIMAL_HTTP_HANDLER.md](SPEC_MINIMAL_HTTP_HANDLER.md)**.

## Who benefits

- **Integrators** — A **correct, copy-friendly** verification path and normative handler steps without mandatory full
  HTTP-framework dependencies from this package.
- **Maintainers** — Explicit contracts for **replayt** versions and **signature verification**, consistent with
  **[DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)**.
- **Contributors** — Clear **scope**, **success bar**, and pointers to specs and **CI** expectations.

## Replayt capabilities this repo consumes

- **Version alignment** — A declared **`replayt`** minimum in `pyproject.toml` (lower bound) so installs and docs agree;
  bump policy and checklists: **[SPEC_REPLAYT_DEPENDENCY.md](SPEC_REPLAYT_DEPENDENCY.md)**.
- **Lifecycle delivery contract** — Run and approval events delivered over HTTP with signing as **replayt** (or
  compatible senders) documents; this repo **implements verification** and documents headers/body rules for Python
  handlers. Upstream algorithm or header changes are **tracked** and reflected via tests, **CHANGELOG.md**, and optional
  material under **`docs/reference-documentation/`**.
- **Standard-library crypto** — Verification uses **stdlib** **`hmac` / `hashlib`** where the published contract allows;
  no requirement to patch **replayt** core from this repository.

## Replayt’s role vs this repo

- **Replayt** (upstream) defines event semantics and how deliveries are **signed**; this repo **documents and tests**
  consumer-side verification for integrators.
- This repository does **not** exist to steer replayt core; propose upstream changes through normal channels (see
  **DESIGN_PRINCIPLES**).

## Scope

### In scope

- Documented **replayt** minimum version in `pyproject.toml` and **[SPEC_REPLAYT_DEPENDENCY.md](SPEC_REPLAYT_DEPENDENCY.md)**.
- **Public** verification helper(s) with **unit tests** that do **not** require the network.
- **README** and spec docs integrators can copy from; **CHANGELOG.md** for user-visible changes.
- **CI** that installs the package and runs the **automated test suite** (see Success).

### Out of scope

- Patching or vendoring **replayt** core.
- Shipping a **mandatory** Starlette/FastAPI/Flask (or similar) stack as part of this package’s required surface—integrators
  wrap the primitive in their own HTTP layer.
- Arbitrary third-party webhook providers unless their contract **matches** the replayt-compatible signing rules
  documented here.
- **Enterprise** positioning narratives and extended **LLM**/demo policy on this page for **v0.x**—defer those to
  **[DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)** (and extend MISSION when the project needs them).

## Success (v0.x)

- **Automated tests** (e.g. **pytest**) run in **CI** on every change workflow the project uses; they cover claimed
  verification behavior, dependency contract checks, and spec-driven acceptance where implemented—**green CI** is part
  of “done.”
- **CHANGELOG.md** records user-visible API and dependency changes under **Unreleased** (or the releasing section) per
  project convention.
- Operators can adopt verification using **README** + **SPEC_WEBHOOK_SIGNATURE.md** without reading the whole tree.

## Doc hygiene (checklist)

When you change behavior or contracts:

- [ ] Update the relevant **spec** and **README** if integrator-facing text changes.
- [ ] Add **CHANGELOG.md** **Unreleased** notes for user-visible API, dependency, or notable doc contract changes.
- [ ] Keep **MISSION** scope/success consistent with **DESIGN_PRINCIPLES** and what **CI** actually runs.
