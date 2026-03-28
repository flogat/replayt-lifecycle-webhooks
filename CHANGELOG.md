# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Documentation

- **`docs/SPEC_WEBHOOK_SIGNATURE.md`:** explicit **signing scheme v1**, normative **consumer contract** (headers, raw
  body, header value shapes), **clock skew / replay policy** (N/A for v1; how to extend), **ordered verification steps**,
  acceptance rows **W1–W7** and **W3b**. **Backlog `35f984f8-67cc-48bf-9385-0ec73a054314`:** **single verification path**;
  **secret configuration** (recommended **`REPLAYT_LIFECYCLE_WEBHOOK_SECRET`**; library does not read env); **HTTP
  401/403** and **no leakage** of secret / full signature / MAC in responses or production logs; rows **W8–W10**;
  cryptographic hygiene for digest **byte** comparison.
- **`docs/reference-documentation/REPLAYT_WEBHOOK_SIGNING.md`:** scheme version, clock/replay summary, verification steps,
  recommended env var (see README).
- **README.md:** verification procedure link; **HTTP responses and logging** pointer; **`os.environ`** example for the
  recommended secret name.

### Added

- Webhook verification tests (phase **3**, backlog **Implement HMAC (or documented) request signing verification**):
  success path uses **`hmac.compare_digest`**; failure **`str(exception)`** omits the secret and the header digest hex;
  **verify-before-JSON** ordering covers **spec W8–W9** expectations in the suite.
- **`verify_lifecycle_webhook_signature`** with **`LIFECYCLE_WEBHOOK_SIGNATURE_HEADER`** (`Replayt-Signature`),
  HMAC-SHA256 over the raw body, and exceptions **`WebhookSignatureMissingError`**,
  **`WebhookSignatureFormatError`**, **`WebhookSignatureMismatchError`** (stdlib **`hmac`** / **`hashlib`**,
  **`hmac.compare_digest`** on digests).
- **`docs/reference-documentation/REPLAYT_WEBHOOK_SIGNING.md`:** consumer signing contract cited from the webhook
  signature spec when upstream HTTP delivery docs are absent.
- Unit tests for valid MAC, wrong secret, tampered body, and missing / malformed signature header (no network).
- Unit tests for uppercase hex signature values and for **secret** supplied as **bytes**.
- Runtime dependency on **replayt** `>=0.4.25` (lower bound only). The package does not import **replayt** yet; this
  floor matches the first integration surface and PyPI versions verified at pin time.
- Tests that assert the canonical **replayt** `>=M.m.p` line in `pyproject.toml` and README compatibility anchors from
  **SPEC_REPLAYT_DEPENDENCY.md**.

### Changed

- **CI:** the test job runs `pip install -e .` before `pip install -e ".[dev]"` so the minimal editable install is
  verified every run.
- **`LIFECYCLE_WEBHOOK_SIGNATURE_HEADER`:** annotated as `Final[str]` to match the spec.

### Documentation

- **`docs/SPEC_WEBHOOK_SIGNATURE.md`:** specification and acceptance checklist for incoming webhook signature
  verification (public API shape, test matrix, upstream alignment, non-goals); pointer to
  **`reference-documentation/REPLAYT_WEBHOOK_SIGNING.md`** as in-repo contract authority when upstream HTTP delivery
  docs are absent.
- **`docs/MISSION.md`:** phase **3** / backlog **Ship a one-page MISSION with scope and success criteria**—integrator skim
  paragraph, **replayt** capabilities consumed, explicit in/out scope bullets, success including **CI** and **automated
  tests** (**pytest**), short doc hygiene checklist; v0.x defers enterprise / extended LLM narrative to
  **DESIGN_PRINCIPLES.md**. Phase **5** (architecture review): minor prose tightening on **MISSION** (clearer consistency
  wording).
- **`README.md`:** **Overview** lists **MISSION** before **REPLAYT_ECOSYSTEM_IDEA** so scope and success are easy to find
  (phase **5**); link to the webhook signature spec, project layout row, reference-documentation note, and a
  copy-paste verification example using the public API; compatibility one-liner, how to check the installed **replayt**
  version, PyPI and release-history links, and [GitHub Issues](https://github.com/flogat/replayt-lifecycle-webhooks/issues)
  for breakage reports.
- **`pyproject.toml`:** `Homepage` and `Issues` URLs for this repository.
- **`docs/SPEC_REPLAYT_DEPENDENCY.md`:** formal spec for the **replayt** lower bound (acceptance criteria, bump policy,
  CI expectations); linked from README and design/dependency docs.

## [0.1.0] - 2026-03-27

### Added

- Initial scaffold and package layout.
