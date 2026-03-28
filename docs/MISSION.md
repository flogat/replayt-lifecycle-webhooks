# Mission: Signed HTTP webhooks for replayt run and approval lifecycle events

This package provides **consumer-side** helpers for operators who receive **replayt** (or compatible) **run** and
**approval** lifecycle events over HTTP. It is **not** a fork of [replayt](https://pypi.org/project/replayt/); version
compatibility and signing rules are maintained **here** with tests and documentation.

## Users and problem

- **Integrators** need a **small, correct** way to confirm that a webhook POST actually came from their configured
  automation before updating internal state or triggering downstream jobs.
- **Maintainers** need an explicit contract for **replayt** versions (**[SPEC_REPLAYT_DEPENDENCY.md](SPEC_REPLAYT_DEPENDENCY.md)**)
  and for **signature verification** (**[SPEC_WEBHOOK_SIGNATURE.md](SPEC_WEBHOOK_SIGNATURE.md)**).

## Replayt’s role vs this repo

- **Replayt** (upstream) defines event semantics and how deliveries are **signed**; this repo **implements** verification
  and documents header/body expectations for Python integrators.
- Changes to signing algorithms or header names are **tracked upstream** and reflected here via tests, changelog notes,
  and optional snapshots under **`docs/reference-documentation/`**.

## Scope

| In scope | Out of scope |
| -------- | ------------ |
| Documented **replayt** minimum version in `pyproject.toml` | Patching replayt core |
| **Public** verification helper(s) with unit tests (no network in those tests) | Full HTTP frameworks as mandatory deps |
| README and spec docs integrators can copy from | Arbitrary third-party webhook providers unless aligned with replayt |

## Success

- **Automated tests** in CI cover claimed behavior (see specs for checklists).
- **CHANGELOG.md** records user-visible API and dependency changes.
- Operators can adopt verification using **README** + **SPEC_WEBHOOK_SIGNATURE.md** without reading the whole tree.
