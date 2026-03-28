# Positioning — Signed HTTP webhooks for replayt run and approval lifecycle events

This project **uses** [replayt](https://pypi.org/project/replayt/). It is **not** a fork of replayt. Compatibility,
version pins, and CI are **your** responsibility here.

**Test coverage (required):** ship automated tests for behavior you claim (unit, contract/integration at replayt
boundaries, smoke where useful). Document how to run them in the README and CI.

Pick **one primary** pattern below (you may blend—say which leads):

## 1) Core-gap

_Use when replayt core intentionally omits a capability._

For **this** repository:

- **Out of core (upstream):** Replayt defines lifecycle **semantics** and HTTP **signing** for run and approval moments; it
  does **not** ship this package’s **Python** verification surface, copy-paste **handler** contracts, or the **pytest** /
  **CI** proof integrators rely on to avoid reimplementing **HMAC-over-raw-body** edge cases.
- **This repo provides:** Consumer-side **`Replayt-Signature`** verification (stdlib **`hmac`** / **`hashlib`** where the
  contract allows), normative specs (**`SPEC_WEBHOOK_SIGNATURE`**, **`SPEC_REPLAYT_DEPENDENCY`**, and related docs),
  optional minimal HTTP glue, and automated tests—**without** forking or steering **replayt** core.
- **Release tracking:** See **Your choice** below (v0.x: one short bullet is enough).

## 2) LLM showcase

_Concrete demo that needs model calls._

- One-sentence use case; which replayt primitives you exercise
- LLM boundaries: secrets, cost, redaction
- What a reviewer runs to verify

## 3) Framework bridge

_Adapter to another framework or runtime._

- Target framework; public API of the bridge
- How **you** maintain consumer-side compatibility (pins, CI matrix)

## 4) Combinator

_Novel composition of replayt + other tools._

- What is stronger together; shared conventions; integration tests where feasible

## Your choice

- **Primary pattern:** **Core-gap** (taxonomy option 1 above) — normative statement and scope live in **[MISSION.md](MISSION.md)**.
- **One-paragraph pitch:** Replayt defines run and approval lifecycle **semantics** and HTTP **signing**; integrators still
  need a **small, tested** way to verify **`Replayt-Signature`** over the **raw body** before acting on JSON. This
  repository documents that consumer contract, ships verification (and optional minimal HTTP glue), and keeps **CI** and
  **pytest** aligned with **[SPEC_REPLAYT_DEPENDENCY.md](SPEC_REPLAYT_DEPENDENCY.md)** and **[SPEC_WEBHOOK_SIGNATURE.md](SPEC_WEBHOOK_SIGNATURE.md)**—without vendoring or steering **replayt** core.
- **Replayt release tracking (v0.x):** Keep the declared **`replayt`** **lower bound** in **`pyproject.toml`** in sync with
  **[SPEC_REPLAYT_DEPENDENCY.md](SPEC_REPLAYT_DEPENDENCY.md)** (bump policy, compatibility matrix, checklists). **CI** runs
  the **pytest** suite on every change workflow the repo uses, including **replayt** import-boundary coverage per
  **[SPEC_REPLAYT_BOUNDARY_TESTS.md](SPEC_REPLAYT_BOUNDARY_TESTS.md)**. Record user-visible dependency or verification
  contract shifts under **Unreleased** in **`CHANGELOG.md`**. For upstream cadence and prose per release, use
  **[PyPI release history](https://pypi.org/project/replayt/#history)** (and upstream changelog or GitHub Releases when you
  need more detail)—this package does not mirror upstream release notes (**README** **Upstream changes**).
