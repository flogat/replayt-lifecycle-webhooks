# Spec: public Python API surface and deprecation policy

**Backlog (normative traceability):** Define public API surface and deprecation policy before 1.0 (`30e133a5-78fa-4eee-ae56-56a1af4c9f73`).

**Audience:** Spec gate (2b), Builder (3), Tester (4), downstream library authors, maintainers.

## Purpose and normative status

This document is the **single integrator-facing contract** for which **imports** and **CLI entrypoints** of **`replayt-lifecycle-webhooks`** are **supported** for semantic-versioning and deprecation purposes. It aligns with **[Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html)** and **[CHANGELOG.md](../CHANGELOG.md)** practice (Keep a Changelog sections **Added** / **Changed** / **Deprecated** / **Removed**).

Until **1.0.0**, the project follows the **pre-1.0 stability** rules in **§ Pre-1.0 stability** below.

Other specs define **behavior** of named callables and types; this spec defines **whether** importing a name from a given path is a **supported** downstream dependency.

## Supported import paths

### Primary: package root

Integrators **SHOULD** import from the distribution package root:

```python
import replayt_lifecycle_webhooks as rlw
# or
from replayt_lifecycle_webhooks import verify_lifecycle_webhook_signature, parse_lifecycle_webhook_event
```

The authoritative list of **public** names is the package **`__all__`** in **`src/replayt_lifecycle_webhooks/__init__.py`**. The table below **must** stay in sync with that list and order (Builder + review: when you change `__all__`, update this spec **or** treat the omission as a spec bug). **`tests/test_public_api.py`** asserts the set matches this table.

| Category | Public names (package root) |
| -------- | --------------------------- |
| Version | `__version__` |
| Signature | `LIFECYCLE_WEBHOOK_SIGNATURE_HEADER`, `WebhookSignatureError`, `WebhookSignatureFormatError`, `WebhookSignatureMismatchError`, `WebhookSignatureMissingError`, `compute_lifecycle_webhook_signature_header`, `verify_lifecycle_webhook_signature` |
| Events / parsing | `SUPPORTED_LIFECYCLE_WEBHOOK_SCHEMA_VERSIONS`, `LIFECYCLE_WEBHOOK_EVENT_TYPES`, `LifecycleCorrelation`, `LifecycleWebhookEvent`, `ApprovalPendingDetail`, `ApprovalPendingEvent`, `ApprovalResolvedDetail`, `ApprovalResolvedEvent`, `RunCompletedDetail`, `RunCompletedEvent`, `RunFailedDetail`, `RunFailedEvent`, `RunStartedDetail`, `RunStartedEvent`, `parse_lifecycle_webhook_event`, `lifecycle_event_to_digest_text`, `lifecycle_event_to_digest_record` |
| HTTP handler (optional glue) | `LifecycleWebhookHttpResult`, `handle_lifecycle_webhook_post`, `make_lifecycle_webhook_wsgi_app` |
| Replay protection | `LifecycleWebhookDedupStore`, `InMemoryLifecycleWebhookDedupStore`, `LifecycleWebhookReplayPolicy`, `ReplayFreshnessRejected`, `ensure_occurred_at_within_replay_window` |
| Redaction / logging helpers | `DEFAULT_SENSITIVE_HEADER_NAMES`, `DEFAULT_SENSITIVE_MAPPING_KEYS`, `REDACTED_PLACEHOLDER`, `redact_headers`, `redact_mapping`, `format_safe_webhook_log_extra` |

**Acceptance (Builder / CI):** **`__all__`** lists **exactly** the names in the table above in **table order** (Version row, then Signature, Events / parsing, HTTP handler, Replay protection, Redaction / logging helpers). **`tests/test_public_api.py`** checks both the set and this order.

### Secondary: `replayt_lifecycle_webhooks.events`

**[EVENTS.md](EVENTS.md)** normatively places typed models and **`parse_lifecycle_webhook_event`** in this submodule. Integrators **MAY** import event types from:

```python
from replayt_lifecycle_webhooks.events import parse_lifecycle_webhook_event, LifecycleWebhookEvent
```

**Supported** names are those listed in **`__all__`** in **`src/replayt_lifecycle_webhooks/events.py`**. That set **must** match the **Events / parsing** row in the table above (same symbols as re-exported from the package root for events).

Deep imports of other submodules for **event** symbols (for example `from replayt_lifecycle_webhooks.events.models import ...` if such paths ever appear) are **not supported** unless this spec is updated.

## Unsupported imports (internal modules)

The following **import paths** are **internal implementation** until **1.0.0** (or until this spec explicitly promotes them):

| Module path | Status |
| ----------- | ------ |
| `replayt_lifecycle_webhooks.signature` | **Internal** — use package root. |
| `replayt_lifecycle_webhooks.digest` | **Internal** — use package root (or `replayt_lifecycle_webhooks.events` re-exports). |
| `replayt_lifecycle_webhooks.handler` | **Internal** — use package root. |
| `replayt_lifecycle_webhooks.replay_protection` | **Internal** — use package root. |
| `replayt_lifecycle_webhooks.redaction` | **Internal** — use package root. |
| `replayt_lifecycle_webhooks.serve` | **Internal** — reference server implementation detail; behavior is described in **[SPEC_HTTP_SERVER_ENTRYPOINT.md](SPEC_HTTP_SERVER_ENTRYPOINT.md)**. |
| `replayt_lifecycle_webhooks.demo_webhook` | **Internal** — demo CLI is invoked via **`python -m replayt_lifecycle_webhooks.demo_webhook`** per **[SPEC_LOCAL_WEBHOOK_DEMO.md](SPEC_LOCAL_WEBHOOK_DEMO.md)**; do not import for library use. |
| `replayt_lifecycle_webhooks.__main__` | **Internal** — use **`python -m replayt_lifecycle_webhooks`**. |

**Rule:** Do **not** rely on symbols that appear in those modules but are **not** re-exported via the package root **`__all__`** (or **`events.__all__`** for the events submodule). They may change or move without a deprecation cycle.

## Documented CLI entrypoints

These **module** invocations are **supported** public **CLI** surfaces (behavior and flags live in their feature specs):

| Command | Spec |
| ------- | ---- |
| `python -m replayt_lifecycle_webhooks` | **[SPEC_HTTP_SERVER_ENTRYPOINT.md](SPEC_HTTP_SERVER_ENTRYPOINT.md)** |
| `python -m replayt_lifecycle_webhooks.demo_webhook` | **[SPEC_LOCAL_WEBHOOK_DEMO.md](SPEC_LOCAL_WEBHOOK_DEMO.md)** |

Adding or renaming a **`-m`** entrypoint requires updating this table, the relevant feature spec, **README.md**, and **CHANGELOG.md**.

## Semantic versioning and releases

- **API and CLI** changes to **supported** names (this document) follow **[Semantic Versioning](https://semver.org/spec/v2.0.0.html)** as recorded in **`CHANGELOG.md`** and **`pyproject.toml`**.
- **Dependency** contract changes (for example **`replayt`** lower bound) follow **[SPEC_REPLAYT_DEPENDENCY.md](SPEC_REPLAYT_DEPENDENCY.md)** and **CHANGELOG.md**.

## Deprecation policy

When a **supported** public name or behavior is to be **removed** or **incompatibly changed**:

1. **CHANGELOG** — Add a bullet under **`[Unreleased]` → Deprecated** (Keep a Changelog) describing what is deprecated, **what to use instead**, and the **planned removal target** (version or timeframe), in the **same release** that first advertises the deprecation.
2. **Notice period** — Maintain the deprecated surface for at least **one** subsequent **minor** **0.x** release published to PyPI after the deprecating release (for example deprecated in **0.4.0**, removal or breaking change no earlier than **0.5.0**). If the team ships **patch-only** releases, the **removal** release **must** still be a **new minor** (or major) **after** that waiting period.
3. **Runtime signal** — Where practical in Python, emit **`DeprecationWarning`** (subclass preferred) **once** per process or per clearly documented scope, with message pointing to the replacement API and **CHANGELOG** entry.
4. **Removal** — Move bullets from **Deprecated** to **Removed** (or **Changed** if behavior changes without removing the name) in the release that actually removes or breaks the old surface.

**Dependency-only** deprecations (for example raising the minimum **replayt** version) follow the same **CHANGELOG** visibility; the **notice period** aligns with **[SPEC_REPLAYT_DEPENDENCY.md](SPEC_REPLAYT_DEPENDENCY.md)** maintainer checklist when that spec is stricter.

## Pre-1.0 stability

For **`0.x`** releases:

- **Minor** bumps **may** add features and **may** deprecate; they **SHOULD NOT** remove or break **supported** APIs without the **deprecation policy** above unless **SECURITY** or **correctness** requires an urgent break (document under **CHANGELOG** **Security** or **Fixed** with explicit **Breaking** callout).
- **Patch** releases **SHOULD NOT** remove or break **supported** APIs.
- Promoting **internal** modules to **supported** paths is a **documentation + `__all__`** change and **CHANGELOG** **Added**.

At **1.0.0**, tighten policy as maintainers document (this spec should gain a **Post-1.0** subsection in a follow-up backlog).

## Acceptance criteria (backlog)

| ID | Criterion |
| -- | --------- |
| **API1** | **Supported public imports** are exactly those documented in **§ Supported import paths** (package root table + **`events`** submodule rule). |
| **API2** | **Internal** modules are listed in **§ Unsupported imports**; integrator docs and **README** do not encourage deep imports from them. |
| **API3** | **Deprecation policy** states **minimum** wait (**one minor 0.x** after deprecating release) and **CHANGELOG** requirements (**Deprecated** section + migration + removal tracking). |

## Related documentation

- **[DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)** — principles **explicit contracts**, **small public surfaces**, **consumer-side maintenance**.
- **[SPEC_REPLAYT_BOUNDARY_TESTS.md](SPEC_REPLAYT_BOUNDARY_TESTS.md)** — stability at the **`replayt`** dependency seam (orthogonal to *this* package’s export surface).
- **[SPEC_AUTOMATED_TESTS.md](SPEC_AUTOMATED_TESTS.md)** — CI bar; backlog **`30e133a5`** maps **API1**–**API3** to **`tests/test_public_api.py`**.
