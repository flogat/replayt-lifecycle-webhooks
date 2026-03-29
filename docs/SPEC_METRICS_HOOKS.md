# Spec: optional metrics hooks for verify and handler outcomes

**Backlog:** `42b8d5a9-a246-4c47-b167-f39ac371789e` (*Optional metrics hooks for verify / handler outcomes*).

**Audience:** Spec gate (2b), Builder (3), Tester (4), operators, integrators.

## Purpose and normative status

This document defines an **optional**, **stdlib-only** extension point for recording **coarse** signature-verification outcomes and **HTTP-level** handler outcomes. Integrators **may** pass a **`LifecycleWebhookMetrics`** implementation; the package **must not** require **Prometheus**, **OpenTelemetry**, or other metrics backends.

Implementation reference: **`src/replayt_lifecycle_webhooks/metrics.py`**. Supported public names live in the package root **`__all__`** per **[SPEC_PUBLIC_API.md](SPEC_PUBLIC_API.md)**.

Related: **[SPEC_WEBHOOK_SIGNATURE.md](SPEC_WEBHOOK_SIGNATURE.md)** (verification behavior), **[SPEC_MINIMAL_HTTP_HANDLER.md](SPEC_MINIMAL_HTTP_HANDLER.md)** (handler), **[SPEC_HTTP_SERVER_ENTRYPOINT.md](SPEC_HTTP_SERVER_ENTRYPOINT.md)** (reference server). **pytest** rows **M1**–**M8**: **[SPEC_AUTOMATED_TESTS.md](SPEC_AUTOMATED_TESTS.md)** **§ Backlog `42b8d5a9`**.

## Protocol: `LifecycleWebhookMetrics`

A narrow **`typing.Protocol`** (or equivalent structural type) with **two** methods. All parameters are **keyword-only** except **`self`**.

### `record_verify_outcome`

- **`outcome`:** one of **`LifecycleWebhookVerifyOutcome`** (see below).
- **`duration_sec`:** **float**, **non-negative**, measuring **verify-only** work (**HMAC** parse + compare), using **`time.monotonic()`** **only** when metrics are enabled (see **§ Disabled-path performance contract**).

**Not passed:** raw body **bytes** or body **text**, shared **secret** material, the full **`Replayt-Signature`** header value, or a computed **MAC** digest string.

### `record_handler_outcome`

- **`http_status`:** final HTTP status code the handler returns for this invocation (for example **204**, **403**).
- **`error_code`:** the JSON **`error`** string when the handler returns a structured **4xx** body; **`None`** for **2xx** and for responses **without** that field.
- **`duration_sec`:** **float**, **non-negative**, **wall** time from handler **entry** to **exit**, **including** verification and JSON parsing/business logic. For a single request where both methods run, this value **is greater than or equal to** the verify-only **`duration_sec`** reported by **`record_verify_outcome`**.

**Not passed:** same prohibitions as **`record_verify_outcome`** (no body, secret, full signature, MAC).

## `LifecycleWebhookVerifyOutcome`

Stable **string literal** values (for adapter mapping to counters or labels):

| Value | Meaning |
| ----- | ------- |
| **`success`** | Signature verified successfully. |
| **`missing_signature`** | **`Replayt-Signature`** absent or empty ( **`WebhookSignatureMissingError`** ). |
| **`format_error`** | Header present but not parseable per wire rules ( **`WebhookSignatureFormatError`** ). |
| **`mismatch`** | Parsed MAC does not match computed MAC ( **`WebhookSignatureMismatchError`** ). |

## Wire API: `metrics=` keyword

Integrators pass **`metrics: LifecycleWebhookMetrics | None = None`** (keyword-only) on:

- **`verify_lifecycle_webhook_signature`**
- **`handle_lifecycle_webhook_post`**
- **`make_lifecycle_webhook_wsgi_app`**
- **`make_reference_lifecycle_webhook_wsgi_app`** (forwards to the inner WSGI factory)

Default **`None`:** no user-defined metrics object; see **§ Disabled-path performance contract**.

## Disabled-path performance contract

When **`metrics is None`**:

- The implementation **must not** call **`record_verify_outcome`** or **`record_handler_outcome`**.
- The implementation **must not** call **`time.monotonic()`** **solely** to populate metrics **`duration_sec`** values. (Verification and handling may still use monotonic or other clocks for **non-metrics** reasons if introduced elsewhere; the **metrics-disabled** path adds **no** timer **only** for metrics.)

## Safety, redaction, and cardinality

Align with **[SPEC_STRUCTURED_LOGGING_REDACTION.md](SPEC_STRUCTURED_LOGGING_REDACTION.md)** **§ Metrics and observability callbacks**: callbacks **must not** receive material that logging would treat as sensitive (raw body, secret, full signing header). Prefer **coarse** outcomes and **stable** **`error_code`** strings from **[SPEC_WEBHOOK_FAILURE_RESPONSES.md](SPEC_WEBHOOK_FAILURE_RESPONSES.md)**; **do not** pass unbounded or high-cardinality strings derived from arbitrary JSON fields as **metric labels** in your own backends.

### Checklist (**MH1**–**MH5**)

| ID | Criterion |
| -- | --------- |
| **MH1** | Callback kwargs **never** include raw POST body **bytes** or decoded body **text**. |
| **MH2** | Callback kwargs **never** include the shared **HMAC** secret. |
| **MH3** | Callback kwargs **never** include the full **`Replayt-Signature`** value or computed **MAC** digest. |
| **MH4** | **`LifecycleWebhookVerifyOutcome`** and handler **`error_code`** use **bounded**, **documented** strings (no arbitrary JSON blobs as protocol fields). |
| **MH5** | Integrator adapters that copy values into **logs** reuse the same hygiene as **SPEC_STRUCTURED_LOGGING_REDACTION** (no raw body or signing material in log fields). |

## Reference implementations (stdlib-only)

Shipped in **`metrics.py`** (import from package root per **SPEC_PUBLIC_API**):

- **`NullLifecycleWebhookMetrics`** — explicit no-op for wiring tests.
- **`InMemoryLifecycleWebhookMetrics`** — in-process counters and last durations (**tests** and **local debugging** only; **not** a production backend).

Optional distribution **extras** for third-party adapters (**Prometheus**, **OTel**) are **out of scope** for the default install graph; if added later, they **must** remain **optional** and **must not** become mandatory dependencies of the core package.

## Test traceability

See **[SPEC_AUTOMATED_TESTS.md](SPEC_AUTOMATED_TESTS.md)** **§ Backlog `42b8d5a9`** (**M1**–**M8**). Primary module: **`tests/test_metrics_hooks.py`**. **M8** (export / spec alignment) is satisfied together with **`tests/test_public_api.py`** (**API1**).

## Related documentation

- **[SPEC_STRUCTURED_LOGGING_REDACTION.md](SPEC_STRUCTURED_LOGGING_REDACTION.md)** — logging redaction; **§ Metrics and observability callbacks**.
- **[SPEC_PUBLIC_API.md](SPEC_PUBLIC_API.md)** — **`__all__`** and supported imports.
- **[CHANGELOG.md](../CHANGELOG.md)** — user-visible API notes.
