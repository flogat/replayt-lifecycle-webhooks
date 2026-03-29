# Spec: CLI — verify saved webhook (raw body + `Replayt-Signature`)

**Backlog:** Support CLI: verify saved webhook (body file + signature header)  
**Workflow id:** `845b4b11-847d-48cb-a9f3-e75f3e4862ef` (phase **2** spec refinement; Builder implements CLI + **pytest** in phase **3**).

**Audience:** Spec gate (2b), Builder (3), Tester (4), support, operators, integrators.

## Problem

During incidents, operators often **save** the HTTP **entity body** and the **`Replayt-Signature`** header from a captured
request. Ad-hoc scripts frequently mishandle **encoding**, **newlines**, or **secrets**. This package should expose a
**first-party**, **documented** **`python -m`** path that performs **offline** **v1** verification using the same rules as
**`verify_lifecycle_webhook_signature`**, without starting an HTTP server.

## Goals

- **One normative operator command** (primary UX) aligned with **[SPEC_PUBLIC_API.md](SPEC_PUBLIC_API.md)** **§ Documented
  CLI entrypoints** and the same **stable exit-code** discipline as **[SPEC_HTTP_SERVER_ENTRYPOINT.md](SPEC_HTTP_SERVER_ENTRYPOINT.md)**
  (reference server): predictable **0** / **1** / **2** mapping for automation and runbooks.
- Accept **raw body** input from a **file path** or **stdin**; accept the **header value** for **`Replayt-Signature`**
  (wire string, including optional **`sha256=`** prefix per **[SPEC_WEBHOOK_SIGNATURE.md](SPEC_WEBHOOK_SIGNATURE.md)**).
- Load the shared **secret** from **`REPLAYT_LIFECYCLE_WEBHOOK_SECRET`** by default (same name as **README** and the
  reference server), with an optional **`--secret`** override for local debugging and the **same shell-history warning** as
  **`python -m replayt_lifecycle_webhooks`**.
- **Never** echo the **secret**, the **full** signature header value, or the **computed MAC** / digest on **failure** (or on
  success unless this spec explicitly allows a success token—see **§ Output and logging**). Align with **SPEC_WEBHOOK_SIGNATURE**
  **§ HTTP responses and logging** for integrators; the CLI is an operator tool but must not become a secret or MAC oracle.

## Non-goals

- **JSON parsing**, **`event_id`** dedupe, or **replay / freshness** checks — verification **only** (MAC over octets).
  Operators who need digest or idempotency semantics use library APIs **after** they trust the body.
- **Network I/O** — the command **must not** require outbound HTTP for its **minimum** behavior.
- Replacing **`verify_lifecycle_webhook_signature`** for library use — the **library** remains explicit-injection for
  **`secret`**; only this **CLI process** reads the recommended env var by default (same posture as the reference server and
  **[SPEC_LOCAL_WEBHOOK_DEMO.md](SPEC_LOCAL_WEBHOOK_DEMO.md)**).

## Entrypoint shape (normative for Builder)

### Primary (recommended)

Extend the existing package **`__main__`** module (**`python -m replayt_lifecycle_webhooks`**) with an **`argparse`**
**subcommand** named **`verify`** so operators learn **one** module name:

| Requirement | Detail |
| ----------- | ------ |
| **Invocation** | **`python -m replayt_lifecycle_webhooks verify …`** |
| **Backward compatibility** | Invocations **without** the **`verify`** subcommand **must** keep the current behavior (start the reference **WSGI** server per **SPEC_HTTP_SERVER_ENTRYPOINT**). |
| **Help** | **`python -m replayt_lifecycle_webhooks verify --help`** documents flags, env var, exit codes, and **raw-body discipline** (see **§ Help text**). |

### Alternative (allowed if documented as primary in **README** + **CHANGELOG**)

A **dedicated** module **`python -m replayt_lifecycle_webhooks.<submodule>`** (for example **`verify_saved_webhook`**) **may**
be implemented **instead of** a subcommand **only if**:

- **SPEC_PUBLIC_API.md** **§ Documented CLI entrypoints** lists that **`-m`** module as the **supported** surface.
- **README.md** shows **one** canonical copy-paste command (same bar as **SPEC_HTTP_SERVER_ENTRYPOINT** **S1**).

The Builder **must not** ship both shapes as co-equal primaries; pick **one** canonical string for **README** and gate tests.

## Inputs (normative)

| Input | Requirement |
| ----- | ----------- |
| **Raw body** | **Exact octets** to verify. **Source A:** path to a file read in **binary** mode (`rb`). **Source B:** **stdin** when the body path is **`-`** (conventional “read from stdin”). The CLI **must not** interpret the bytes as UTF-8 text for signing purposes unless documenting a deliberate escape hatch (default: **opaque bytes**). |
| **`Replayt-Signature` value** | **Required.** Passed as a **CLI argument** (for example **`--signature`**). **Optional addition:** **`--signature-file PATH`** reading the value from a file (trim a single trailing newline only if documented; body is still binary). The string is the **header field-value** as received on the wire (after any HTTP stack unwrapping), not a path inside the JSON body. |
| **Shared secret** | **Preferred:** read from **`REPLAYT_LIFECYCLE_WEBHOOK_SECRET`** (string, UTF-8 when encoded for HMAC per **SPEC_WEBHOOK_SIGNATURE**). **Optional:** **`--secret`** with the same hygiene warning as the reference server’s **`--secret`**. If the secret is missing or empty after resolution, exit **2** with a **clear** stderr message that **does not** echo candidate values. |

## Verification behavior

- The CLI **must** call **`verify_lifecycle_webhook_signature`** (or logic **byte-for-byte equivalent** to it and **SPEC_WEBHOOK_SIGNATURE** **v1**) with **`secret`**, **`body`**, and **`signature`** derived from the inputs above.
- **No** JSON parsing, **no** **`parse_lifecycle_webhook_event`**, **no** metrics hooks required for the **minimum** backlog
  (Builder **may** wire **`metrics=None`** only).

## Exit codes (stable)

| Code | Meaning |
| ---- | ------- |
| **0** | Verification **succeeded** (MAC valid for **v1**). |
| **1** | Verification **failed** — missing/empty signature, malformed header value, MAC mismatch, or any **`WebhookSignature*`** failure from the verifier. **Stderr** **must** use **generic** wording (for example **“verification failed”** / **“signature verification failed”**) **without** printing the **secret**, the **full** **`Replayt-Signature`** value, or **computed** digest hex. |
| **2** | **Usage or configuration** — unknown flags, missing required arguments, missing/empty secret, unreadable body path, I/O errors reading body or signature file. |

**Note:** Distinguish **1** vs **2** so scripts can treat **1** as “untrusted payload” and **2** as “fix the command / env”.

## Output and logging

- **Stdout (success):** **Exactly one** stable line **`ok`** (ASCII, lowercase, trailing newline) **unless** this spec is
  amended with **CHANGELOG** + **README** — default is **`ok\n`** for grep-friendly automation.
- **Stdout (failure):** **Empty** preferred; messages belong on **stderr**.
- **Stderr:** Error text only; **must not** include secret material, full signature header, or computed MAC (same bar as
  **SPEC_WEBHOOK_SIGNATURE** for client-facing leakage).
- **Verbose / debug** flags are **optional**; if added later, **default off** and **must not** print secrets or full MACs at
  default verbosity.

## Help text (minimum)

**`--help`** for the **`verify`** subcommand (or dedicated module) **must** state explicitly:

1. The MAC is over the **raw POST body bytes**; **re-serializing JSON** (pretty-print, key order) **breaks** verification.
2. The recommended secret env var is **`REPLAYT_LIFECYCLE_WEBHOOK_SECRET`**.
3. Point to **SPEC_WEBHOOK_SIGNATURE** **§ Verification procedure (integrators)** (or the **README** anchor that links to
   it).

## Fixtures and golden vectors (normative for tests)

- **Body bytes:** Use committed files under **`tests/fixtures/events/`** (same directory as the local demo and lifecycle
  tests) — at minimum **`run_started.json`** for one **success** subprocess case.
- **Signature construction in tests:** Tests **may** use **`compute_lifecycle_webhook_signature_header`** to derive the
  **`--signature`** string for a fixture (same approach as **SPEC_LOCAL_WEBHOOK_DEMO** and **§ Backlog `2b4c6927`** **A6**
  golden-vector policy: the **CLI** under test is exercised end-to-end; the **test** computes the expected header).
- **Failure cases:** Include at least **wrong MAC** (exit **1**, no leak) and **missing secret** (exit **2**).

## Related documentation

- **[SPEC_WEBHOOK_SIGNATURE.md](SPEC_WEBHOOK_SIGNATURE.md)** — **v1** rules, header format, secret hygiene.
- **[SPEC_PUBLIC_API.md](SPEC_PUBLIC_API.md)** — supported **`-m`** / CLI table.
- **[SPEC_HTTP_SERVER_ENTRYPOINT.md](SPEC_HTTP_SERVER_ENTRYPOINT.md)** — reference server; shared module name **`python -m
  replayt_lifecycle_webhooks`** when using the **subcommand** design.
- **[SPEC_LOCAL_WEBHOOK_DEMO.md](SPEC_LOCAL_WEBHOOK_DEMO.md)** — complementary “send signed POST” demo; same fixtures and
  env var story.
- **[SPEC_AUTOMATED_TESTS.md](SPEC_AUTOMATED_TESTS.md)** — **§ Backlog `845b4b11`** (**VW1**–**VW8**).

## Acceptance criteria (checklist for Builder / Tester)

| ID | Criterion | Verification |
| -- | --------- | ------------ |
| **VW1** | **README.md** documents the **canonical** **`python -m …`** invocation (subcommand or dedicated module per **§ Entrypoint shape**) and points at this spec. | Doc review; **OP**-style tests if **SPEC_README_OPERATOR_SECTIONS** maps a row |
| **VW2** | **`--help`** mentions **raw body discipline**, **`REPLAYT_LIFECYCLE_WEBHOOK_SECRET`**, and exit codes **0** / **1** / **2**. | Subprocess **`--help`** capture; or **pytest** string assertions |
| **VW3** | Subprocess: fixture body file + valid **`--signature`** → exit **0**, stdout **`ok\n`**. | **`pytest`** |
| **VW4** | Subprocess: valid body + **wrong** signature (or tampered body) → exit **1**; captured **stderr** **must not** contain a distinctive **high-entropy secret** substring or **full 64-hex** MAC used in the test. | **`pytest`** |
| **VW5** | Subprocess: body from **stdin** (`-`) with valid signature → exit **0**. | **`pytest`** |
| **VW6** | Missing or empty secret (no env, no **`--secret`**) → exit **2**. | **`pytest`** |
| **VW7** | **`SPEC_PUBLIC_API.md`** CLI table and **`CHANGELOG.md`** **Unreleased** include the new entrypoint when implemented. | Doc review |
| **VW8** | **`pytest tests -q`** remains **network-free** for these cases (no outbound HTTP). | CI / local **pytest** |

**CHANGELOG:** When the CLI ships, record the entrypoint, exit codes, and env var under **`[Unreleased]`** per project
convention.
