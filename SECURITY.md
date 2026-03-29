# Security policy

This document describes how to report security-sensitive findings about **this repository**:
**replayt-lifecycle-webhooks** (consumer-side signature verification and related docs). It does not replace
**replayt**’s own process for the upstream PyPI product, infrastructure, or core signing semantics.

Normative checklist and cross-links: **[docs/SPEC_SECURITY_DISCLOSURE.md](docs/SPEC_SECURITY_DISCLOSURE.md)**.

## Supported scope (in scope)

Report here when the issue touches **this package’s** Python surface, docs, or tests:

- **Signature verification** and **HMAC** handling shipped here (for example **`verify_lifecycle_webhook_signature`**
  and closely related verification helpers).
- **Optional HTTP surfaces** in this repo (reference server, minimal handler, WSGI factories) when they affect
  **authentication or integrity** of lifecycle webhooks **or** could leak webhook secrets, raw signing material, or full
  **`Replayt-Signature`** values through responses, logs, or error paths.
- **Documentation** that would systematically lead integrators to **skip** verification or **mishandle** secrets in a
  way that defeats the published contract. If exploitation is plausible, use the private channel below before
  broad public discussion.

## Out of scope (upstream and neighbors)

These belong outside this repository’s triage:

- **Upstream replayt** (the **PyPI** distribution **`replayt`**, core semantics, product signing behavior, or
  infrastructure). Use that project’s issue tracker, vendor contact, or security process for bugs and incidents there.
  This package tracks compatibility via **[docs/SPEC_REPLAYT_DEPENDENCY.md](docs/SPEC_REPLAYT_DEPENDENCY.md)** and tests;
  it does not patch **replayt** core.
- **Dependency CVEs** and third-party advisories are **usually** handled through public issues, version bumps, or
  **Dependabot**-style upgrades unless maintainers say otherwise.

## How to report

**Preferred:** Use **GitHub** private vulnerability reporting: open the repository **Security** tab and choose **Report a
vulnerability**. That path keeps details off public Issues and Discussions.

**Do not** open a **public** Issue, Discussion, or PR with **undisclosed exploit** details, live secrets, or production
payloads. Use the private channel first; maintainers will coordinate publication timing with you when appropriate.

## Response expectations

Maintainers will send a **best-effort initial acknowledgement within three business days** for well-formed reports.

**Severity**, **fix timelines**, and **release planning** depend on the report. While a report is **actively** under
investigation, expect **periodic updates**—**at least every 14 calendar days** when status is changing, or a short “no
update yet” note when work is still in progress.

## Disclosure hygiene (no secret leakage)

Do **not** paste **live** **HMAC** keys, **full** **`Replayt-Signature`** header values from real deployments, or **raw
webhook bodies** that contain production **PII** or secrets. Use redacted examples and describe behavior instead.

Verification and failure-handling norms: **[docs/SPEC_WEBHOOK_SIGNATURE.md](docs/SPEC_WEBHOOK_SIGNATURE.md)**. Logging and
redaction: **[docs/SPEC_STRUCTURED_LOGGING_REDACTION.md](docs/SPEC_STRUCTURED_LOGGING_REDACTION.md)**. **LLM** / demo
expectations: **[docs/DESIGN_PRINCIPLES.md](docs/DESIGN_PRINCIPLES.md)**.

## Test fixtures and CI

Security-sensitive **fixtures** under **`tests/`** and any **`src/…/fixtures/`** should avoid real shared secrets, live
full signatures presented as production truth, and raw production bodies. **CI** stays **network-free** for
cryptographic tests per **[docs/SPEC_AUTOMATED_TESTS.md](docs/SPEC_AUTOMATED_TESTS.md)**.
