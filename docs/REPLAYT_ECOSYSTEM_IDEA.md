# Positioning — Signed HTTP webhooks for replayt run and approval lifecycle events

This project **uses** [replayt](https://pypi.org/project/replayt/). It is **not** a fork of replayt. Compatibility,
version pins, and CI are **your** responsibility here.

**Test coverage (required):** ship automated tests for behavior you claim (unit, contract/integration at replayt
boundaries, smoke where useful). Document how to run them in the README and CI.

Pick **one primary** pattern below (you may blend—say which leads):

## 1) Core-gap

_Use when replayt core intentionally omits a capability._

- What is out of core and why?
- What does **this** repo provide instead?
- How do you track replayt releases?

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

- **Primary pattern:** **Core-gap** (§1) — normative statement and scope live in **[MISSION.md](MISSION.md)**.
- **One-paragraph pitch:** Replayt defines run and approval lifecycle **semantics** and HTTP **signing**; integrators still
  need a **small, tested** way to verify **`Replayt-Signature`** over the **raw body** before acting on JSON. This
  repository documents that consumer contract, ships verification (and optional minimal HTTP glue), and keeps **CI** and
  **pytest** aligned with **[SPEC_REPLAYT_DEPENDENCY.md](SPEC_REPLAYT_DEPENDENCY.md)** and **[SPEC_WEBHOOK_SIGNATURE.md](SPEC_WEBHOOK_SIGNATURE.md)**—without vendoring or steering **replayt** core.
