# Spec: local demo webhook POST (signed fixture sender)

**Backlog:** Add a one-command local demo script for webhook delivery (`ab0bfe3c-a94c-4711-8a5b-eeb47c886d2c`).  
**Audience:** Spec gate (2b), Builder (3), Tester (4), contributors, maintainers.

## Problem

New contributors and integrators want to **exercise the reference HTTP server** (or any compatible listener) with a
**realistic, signed** lifecycle POST **without** deploying replayt or external infrastructure. Today they must craft
**`Replayt-Signature`** by hand or copy snippets; that is error-prone and drifts from **v1** rules in
**[SPEC_WEBHOOK_SIGNATURE.md](SPEC_WEBHOOK_SIGNATURE.md)**.

## Goals

- Provide **one primary, documented** invocation (same posture as **S1** in
  **[SPEC_HTTP_SERVER_ENTRYPOINT.md](SPEC_HTTP_SERVER_ENTRYPOINT.md)**) that **reads a dev fixture**, **computes v1
  HMAC-SHA256** over the **exact body octets** sent on the wire, sets **`Replayt-Signature`**, and **POST**s to a
  configurable URL.
- Align **defaults** with the reference server documented in **README.md** so a **two-terminal** “start server → send
  demo” flow works **copy-paste**.
- Document **required configuration** (**shared secret**, URL overrides) in **`--help`** and/or **README** so operators
  match **[SPEC_WEBHOOK_SIGNATURE.md](SPEC_WEBHOOK_SIGNATURE.md)**’s recommended env var
  **`REPLAYT_LIFECYCLE_WEBHOOK_SECRET`**.

## Non-goals

- **Not** a supported “replayt sender” or production integration path; **dev / docs / CI fixtures only**.
- **Not** extending the **library** contract: the **library** still does **not** read the environment for
  **`verify_lifecycle_webhook_signature`** (**[SPEC_WEBHOOK_SIGNATURE.md](SPEC_WEBHOOK_SIGNATURE.md)**). Only this **demo
  process** may read **`REPLAYT_LIFECYCLE_WEBHOOK_SECRET`** by default, mirroring the reference server entrypoint.
- **Not** requiring network access from **pytest** for the **minimum** acceptance bar (**D7** allows **network-free**
  tests that prove signing + verifier agreement without a real socket).

## Signing and body bytes (normative)

| Requirement | Detail |
| ----------- | ------ |
| **Algorithm** | **v1** only: **HMAC-SHA256** over the **raw POST body bytes**, header **`Replayt-Signature`**, value
  **`sha256=<64 hex>`** (or bare hex per **v1**), same rules as **[SPEC_WEBHOOK_SIGNATURE.md](SPEC_WEBHOOK_SIGNATURE.md)**
  and **[`reference-documentation/REPLAYT_WEBHOOK_SIGNING.md`](reference-documentation/REPLAYT_WEBHOOK_SIGNING.md)**. |
| **Verifier agreement** | For the chosen body bytes and secret, the computed header **must** be accepted by
  **`verify_lifecycle_webhook_signature`** (or be **byte-for-byte equivalent** to that implementation’s checks). **Do
  not** invent a parallel MAC format for the demo. |
| **Body octets** | The bytes signed **must** be **identical** to the bytes sent in the HTTP entity-body. **Recommended
  approach:** read a committed fixture file under **`tests/fixtures/events/`** as **binary** (`rb`) and POST those
  octets unchanged—avoids JSON re-serialization (**key order**, whitespace) changing the MAC. If the implementation
  builds JSON in memory instead, it **must** document a **stable** encoding and add tests that catch drift. |

## Default URL and reference server alignment

| Item | Default | Notes |
| ---- | ------- | ----- |
| **Target URL** | **`http://127.0.0.1:8000/webhook`** | Must match **README** defaults for **`python -m
  replayt_lifecycle_webhooks`** (**host** **`127.0.0.1`**, port **`8000`**, path **`/webhook`**) per
  **[SPEC_HTTP_SERVER_ENTRYPOINT.md](SPEC_HTTP_SERVER_ENTRYPOINT.md)**. |
| **Method** | **`POST`** | |
| **Overrides** | **Optional** **`--url`** (or split **host** / **port** / **path** flags) | If present, **document** in
  **README** and **`--help`**; defaults **must** stay stable unless **CHANGELOG** + this spec update. |

## Fixtures (normative)

- **Source directory:** **`tests/fixtures/events/`** (existing **`run_started.json`**, **`run_completed.json`**, etc.).
- **Dev-only:** Fixtures are **test and demo** inputs; they may contain **synthetic** ids and **no** real secrets.
- **Retries:** To mimic an HTTP retry of one logical emission, POST the **same** file bytes again (same **`event_id`**, same MAC). **`run_started_redelivery.json`** matches **`run_started.json`** for that pattern in tests; see **[SPEC_DELIVERY_IDEMPOTENCY.md](SPEC_DELIVERY_IDEMPOTENCY.md)**.
- **Default fixture** (if the CLI supports a named default): **`run_completed.json`** unless maintainers choose another
  single default and update this spec + **README** together.

## Entrypoint shape

Exactly **one** invocation is **canonical** in **README.md** (copy-paste block in **Quick start** or **Try it
locally**), matching **SPEC_HTTP_SERVER_ENTRYPOINT**’s “one primary command” pattern:

| Requirement | Detail |
| ----------- | ------ |
| **Primary command** | **`python -m replayt_lifecycle_webhooks.demo_webhook`** — implemented as a **`demo_webhook.py`**
  (or package submodule) with **`if __name__ == "__main__"`** / **`runpy`** equivalent so **`-m`** works after install. |
| **Secondary alias** | Builder **may** add a **`[project.scripts]`** console script (e.g. **`replayt-lifecycle-webhooks-demo-post`**)
  if **README** still labels **`python -m …`** as **primary**. |
| **`scripts/`** | A repository **`scripts/`** file is **optional**; the **normative** operator path is **`python -m`**
  (or the documented console script), not an uninstalled path-only script. |

## CLI configuration (normative minimum)

- **`--help`**: **must** mention **`REPLAYT_LIFECYCLE_WEBHOOK_SECRET`** (and that the demo **process** reads it by
  default, like the reference server).
- **`--secret`**: optional override for local debugging **with** the same hygiene warning as the server’s **`--secret`**
  (shell history); prefer env in runbooks.
- **`--url`**: optional; default **see table above**.
- **`--fixture`**: path **or** preset name mapping to **`tests/fixtures/events/*.json`** when run from a **dev** checkout;
  for **`pip install`** users, either ship fixtures as **package data** or document that presets require the **source
  tree** / a documented install extra—**Builder** must pick one and document it (**README** + **`--help`**).

## HTTP client and dependencies

- **Prefer** **`urllib.request`** (stdlib) for the POST so **`pip install replayt-lifecycle-webhooks`** does **not** gain a
  **new mandatory** HTTP dependency for this tool.
- If Builder uses **httpx** or another third-party client, they **must** justify it in **`pyproject.toml`** / **README**,
  follow **[MISSION.md](MISSION.md)** optional-deps posture, and record **CHANGELOG.md** **Unreleased** per
  **[SPEC_HTTP_SERVER_ENTRYPOINT.md](SPEC_HTTP_SERVER_ENTRYPOINT.md)** dependency rules.

## Observability and safety

- **Exit codes:** **`0`** when the HTTP response status is **2xx** (typically **204** from the reference handler);
  **non-zero** on transport failure, missing secret, or **non-2xx** response—document in **`--help`**.
- **Logging:** **do not** print the raw secret, full **`Replayt-Signature`** value, or computed MAC in default output
  (same spirit as **[SPEC_WEBHOOK_SIGNATURE.md](SPEC_WEBHOOK_SIGNATURE.md)** logging rules).

## Acceptance criteria (checklist for Builder / Tester)

| ID | Criterion | Verification |
| -- | --------- | ------------ |
| **D1** | **README.md** includes **one** copy-paste **primary** command for the demo (**`python -m …`** and/or the chosen console script) in **Quick start** or **Try it locally**, with default URL implied or explicit. | Doc review |
| **D2** | Documented **default URL** matches **reference server** defaults (**`http://127.0.0.1:8000/webhook`** unless server defaults change in lockstep). | Doc review + **SPEC_HTTP_SERVER_ENTRYPOINT** |
| **D3** | Demo signing is **v1** and **verifier-compatible**: for at least one committed fixture, **`verify_lifecycle_webhook_signature`** succeeds on **`(secret, body_bytes, signature_header)`** produced by the demo’s signing logic. | **`pytest`** (network-free helper test acceptable) |
| **D4** | **`--help`** documents **`REPLAYT_LIFECYCLE_WEBHOOK_SECRET`** (and optional **`--secret`** hazards if implemented). | CLI / doc review |
| **D5** | Default or documented fixtures live under **`tests/fixtures/events/`** (or packaged equivalents); **no** one-off undocumented JSON blobs in prose only. | Tree / package review |
| **D6** | New **runtime** dependencies (if any) are declared, justified, and noted under **CHANGELOG.md** **Unreleased**. | **`pyproject.toml`** + **CHANGELOG** |
| **D7** | Automated tests cover **D3** **without** requiring outbound network or binding public interfaces in CI (in-process HTTP optional). | **`pytest tests -q`**; see **SPEC_AUTOMATED_TESTS** |
| **D8** | Non-2xx HTTP responses yield **non-zero** exit from the demo CLI (documented). | **`pytest`** or scripted check |
| **D9** | Default **stdout/stderr** does **not** echo the raw secret or full signature header value. | Code review / test |

## Related docs

- **[SPEC_WEBHOOK_SIGNATURE.md](SPEC_WEBHOOK_SIGNATURE.md)** — **v1** MAC and header rules.
- **[SPEC_HTTP_SERVER_ENTRYPOINT.md](SPEC_HTTP_SERVER_ENTRYPOINT.md)** — reference server defaults and **S1–S8**.
- **[SPEC_MINIMAL_HTTP_HANDLER.md](SPEC_MINIMAL_HTTP_HANDLER.md)** — **POST** behavior expected at the default path.
- **[SPEC_AUTOMATED_TESTS.md](SPEC_AUTOMATED_TESTS.md)** — CI entrypoint; **D7** coverage expectations.
- **[EVENTS.md](EVENTS.md)** — payload field semantics (informative for fixture choice).
- **[README.md](../README.md)** — operator copy-paste for server + demo.
