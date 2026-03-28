# Dependency audit

## Direct runtime dependency: **replayt**

This package declares a **replayt** lower bound in `pyproject.toml`. Rationale, integrator-facing documentation expectations, and acceptance criteria are in **[SPEC_REPLAYT_DEPENDENCY.md](SPEC_REPLAYT_DEPENDENCY.md)**.

### Reference HTTP server (stdlib WSGI)

The documented **`python -m replayt_lifecycle_webhooks`** listener uses **stdlib** **`wsgiref.simple_server`** and the
same **`make_lifecycle_webhook_wsgi_app`** stack as **[SPEC_MINIMAL_HTTP_HANDLER.md](SPEC_MINIMAL_HTTP_HANDLER.md)**. No
**`serve`** extra or additional runtime packages were added for this backlog (**`2cf0f4fb-ef9a-40d4-b306-8a46d30f409e`**);
**`pip-audit`** surface for default **`pip install -e .`** is unchanged.

If a future optional **ASGI** stack ships under **`[project.optional-dependencies]`**, add a short justification here and
note any **pip-audit** delta for installs that include that extra.

---

CI **`supply-chain`** runs `pip-audit --ignore-vuln CVE-2026-4539 --desc` after `pip install -e ".[dev]"`. PyPA **pip-audit**
has no `--severity-high` flag; add further `--ignore-vuln` entries only with a short write-up under **Accepted risks**.

## Accepted risks

### CVE-2026-4539 (pygments)

Transitive **pygments** may report **CVE-2026-4539** (ReDoS in **AdlLexer**). This scaffold does not use that lexer; remove the
ignore from `.github/workflows/ci.yml` when your resolved dependency tree no longer needs it.
