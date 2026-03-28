# Spec: reference HTTP server entrypoint (lifecycle webhooks)

**Backlog:** Expose a minimal HTTP receiver (ASGI/WSGI) behind one entrypoint (`2cf0f4fb-ef9a-40d4-b306-8a46d30f409e`).  
**Audience:** Spec gate (2b), Builder (3), Tester (4), integrators, maintainers.

## Problem

Integrators need **one supported, documented** way to run an HTTP listener for signed lifecycle **POST**s locally and in
production-sized environments (behind a reverse proxy or tunnel). Today the package exposes **framework-agnostic** handler
APIs and a **stdlib WSGI** factory (**`make_lifecycle_webhook_wsgi_app`**) per
**[SPEC_MINIMAL_HTTP_HANDLER.md](SPEC_MINIMAL_HTTP_HANDLER.md)**; adopters must wire **`wsgiref`**, **gunicorn**, or
their own ASGI stack by hand. This spec defines the **reference server** contract so Builder and docs converge on a
single entrypoint without making a heavy web stack **mandatory** for consumers who only import verification helpers.

## Non-goals

- Replacing **`handle_lifecycle_webhook_post`** or **`make_lifecycle_webhook_wsgi_app`** as the **library** surface;
  the server is a **thin wrapper** around the same semantics (status table, JSON error bodies, verify-before-JSON).
- Defining replayt product URLs, tunneling, or TLS termination—operators use their platform’s edge.
- Request size limits, chunked upload handling, or rate limiting beyond a **short** note that production should enforce
  limits at the proxy or server (same posture as **SPEC_MINIMAL_HTTP_HANDLER** WSGI notes).

## Stack choice (normative for Builder)

The implementation **must** choose **one** primary serving model and document the rationale in **`pyproject.toml`**
(comments or dependency grouping) and **`CHANGELOG.md`** **Unreleased** when the feature lands:

| Option | When to prefer | Dependency posture |
| ------ | ---------------- | ------------------ |
| **ASGI** (e.g. **Starlette** + **uvicorn**, or equivalent thin ASGI app) | Production parity with async hosts, common integrator stacks, or clearer routing/middleware | Add **runtime** deps only under **`[project.optional-dependencies]`** (recommended extra name: **`serve`** or **`server`**) unless maintainers justify **core** deps in **`[project.dependencies]`** in **CHANGELOG** |
| **Stdlib WSGI** (**`wsgiref.simple_server`** + **`make_lifecycle_webhook_wsgi_app`**) | Zero new runtime dependencies; acceptable for local dev and simple mounts | **No** new packages required; document that the entrypoint wraps the existing WSGI app |

**Default recommendation:** Prefer an **optional extra** (e.g. **`pip install replayt-lifecycle-webhooks[serve]`**) for
any **third-party** HTTP server or framework so **`pip install replayt-lifecycle-webhooks`** remains aligned with
**[MISSION.md](MISSION.md)** (“no mandatory Starlette/FastAPI/Flask stack” for library consumers). A **stdlib-only**
entrypoint may ship **without** an extra if it adds only a **`__main__`** or console script around **`wsgiref`**.

## Entrypoint shape

Exactly **one** invocation is **canonical** in **README.md** (copy-paste block). The Builder **may** also register a
secondary alias (for example both **`python -m replayt_lifecycle_webhooks`** and a **`[project.scripts]`** console
script) if **README** labels one as **primary** and **`pyproject.toml`** lists both.

| Requirement | Detail |
| ----------- | ------ |
| **Documented command** | **`python -m <module>`** and/or **`console_scripts`** entry defined in **`pyproject.toml`**; README shows the **same** command operators should use in docs and runbooks. |
| **Bind address** | Configurable **host** and **port** with **documented defaults** (suggested defaults: host **`127.0.0.1`**, port **`8000`** for local use; production examples may show **`0.0.0.0`** behind a proxy). |
| **Webhook route** | **POST** requests that carry lifecycle deliveries **must** use a **single documented default path** (recommended: **`/`** or **`/webhook`**—pick one per implementation and do not change without **CHANGELOG** + spec update). If the CLI accepts a path override, defaults **must** remain stable. |
| **Handler semantics** | **POST** handling **must** match **SPEC_MINIMAL_HTTP_HANDLER** (statuses **405** / **401** / **403** / **400** / **204**, JSON error bodies per **[SPEC_WEBHOOK_FAILURE_RESPONSES.md](SPEC_WEBHOOK_FAILURE_RESPONSES.md)** where that spec applies). |

## Health / readiness

Platforms often require a **GET** probe that succeeds when the process is listening.

| Requirement | Detail |
| ----------- | ------ |
| **Path** | **`GET /health`** (recommended; Builder **may** choose **`/healthz`** or **`/ready`** instead only if **README** and this spec are updated together—prefer **`/health`** for simplicity). |
| **Status** | **200 OK** when the server process is accepting HTTP connections for the configured bind address. |
| **Body** | Small, stable response (for example plain text **`ok`** or minimal JSON **`{"status":"ok"}`**). **Must not** echo secrets or request headers. |
| **Secret** | The health endpoint **must not** require **`Replayt-Signature`** or the webhook shared secret; it **may** remain **200** even if the secret is missing or invalid (operators use separate config checks if they need “ready to verify”). |

If maintainers later split **liveness** vs **readiness**, document both paths in **README** and add a row to the
acceptance table below (**CHANGELOG** + **SPEC_AUTOMATED_TESTS** pointer).

## Configuration (reference server only)

- **Shared secret:** The **library** APIs **do not** read the environment (**[SPEC_WEBHOOK_SIGNATURE.md](SPEC_WEBHOOK_SIGNATURE.md)**).
  The **reference server process** **should** load the recommended secret from **`REPLAYT_LIFECYCLE_WEBHOOK_SECRET`**
  (see **README**) so operators have one name across docs; if the server cannot read the env, it **must** document the
  alternative (for example **`--secret`** with a strong warning against shell history). Failing fast with a clear exit
  code and message when no secret is configured is **recommended**.
- **Optional hooks:** If **`on_success`** is exposed for the server wrapper, behavior **must** match **SPEC_MINIMAL_HTTP_HANDLER**
  (callback runs only after verify + successful JSON parse).

## Dependencies and changelog

When this backlog is implemented:

- **`pyproject.toml`** **must** declare any **new** third-party packages needed to run the documented command (runtime
  or extra), with a **short justification** adjacent (comment) or in **README** / this spec’s **Stack choice** section.
- **`CHANGELOG.md`** **Unreleased** must list new extras, new console scripts / **`python -m`** modules, and
  user-visible flags (host, port, path) per project convention.
- **`docs/DEPENDENCY_AUDIT.md`** **should** gain a short subsection for the **serve** (or chosen) extra when it adds
  transitive surface area worth tracking for **pip-audit**.

## Acceptance criteria (checklist for Builder / Tester)

| ID | Criterion | Verification |
| -- | --------- | ------------ |
| **S1** | **README** documents **one** primary command that starts the server and listens for **POST** webhooks on the documented path. | Doc review; manual or scripted smoke optional |
| **S2** | **`pyproject.toml`** exposes that command via **`[project.scripts]`** and/or **`[tool.setuptools.packages]`** **`__main__`** (or documented **`python -m`** module). | Review manifest |
| **S3** | **`GET /health`** (or the spec-chosen single health path) returns **200** with a small, non-sensitive body and **no** webhook secret required. | **pytest** or in-process HTTP client |
| **S4** | **POST** behavior matches **SPEC_MINIMAL_HTTP_HANDLER** / **SPEC_WEBHOOK_FAILURE_RESPONSES** for method, signature, and JSON errors. | **pytest**; align with **H1–H8** where applicable |
| **S5** | New **runtime** dependencies are **justified** in **`pyproject.toml`** / spec and recorded under **CHANGELOG.md** **Unreleased**. | Review |
| **S6** | Automated tests exercise the server **without** binding public sockets or requiring network **CI** access (in-process ASGI client, **WSGI** **`EnvironBuilder`**, or equivalent). | **`pytest tests -q`**; see **SPEC_AUTOMATED_TESTS** |
| **S7** | Host, port, and (if supported) webhook path defaults are **documented** and stable; overrides are documented if present. | Doc review |
| **S8** | Documented secret configuration (**env** and/or flags) does **not** contradict **SPEC_WEBHOOK_SIGNATURE**’s rule that **library** calls remain explicit-injection. | Doc review |

## Related docs

- **[SPEC_MINIMAL_HTTP_HANDLER.md](SPEC_MINIMAL_HTTP_HANDLER.md)** — handler and WSGI factory; status table **H1–H8**.
- **[SPEC_WEBHOOK_FAILURE_RESPONSES.md](SPEC_WEBHOOK_FAILURE_RESPONSES.md)** — JSON **`error`** codes for client failures.
- **[SPEC_WEBHOOK_SIGNATURE.md](SPEC_WEBHOOK_SIGNATURE.md)** — verification and integrator logging rules.
- **[SPEC_AUTOMATED_TESTS.md](SPEC_AUTOMATED_TESTS.md)** — CI entrypoint; minimum coverage when **S** rows are active.
- **[SPEC_REPLAYT_DEPENDENCY.md](SPEC_REPLAYT_DEPENDENCY.md)** — declaring and justifying dependency changes.
- **[README.md](../README.md)** — operator copy-paste for the canonical start command (once implemented).
- **[MISSION.md](MISSION.md)** — optional HTTP glue scope; no mandatory framework for library-only installs.
