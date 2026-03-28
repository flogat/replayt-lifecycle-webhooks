# Dependency audit

## Direct runtime dependency: **replayt**

This package declares a **replayt** lower bound in `pyproject.toml`. Rationale, integrator-facing documentation expectations, and acceptance criteria are in **[SPEC_REPLAYT_DEPENDENCY.md](SPEC_REPLAYT_DEPENDENCY.md)**.

### Optional reference HTTP server (`serve` / similar extra)

When **[SPEC_HTTP_SERVER_ENTRYPOINT.md](SPEC_HTTP_SERVER_ENTRYPOINT.md)** adds a **`serve`** (or similarly named) extra or
new runtime packages for the documented **`python -m` / CLI** listener, extend this file with a short note on **why**
those packages are required and any **pip-audit** posture changes (for example dev-only vs default install).

---

CI **`supply-chain`** runs `pip-audit --ignore-vuln CVE-2026-4539 --desc` after `pip install -e ".[dev]"`. PyPA **pip-audit**
has no `--severity-high` flag; add further `--ignore-vuln` entries only with a short write-up under **Accepted risks**.

## Accepted risks

### CVE-2026-4539 (pygments)

Transitive **pygments** may report **CVE-2026-4539** (ReDoS in **AdlLexer**). This scaffold does not use that lexer; remove the
ignore from `.github/workflows/ci.yml` when your resolved dependency tree no longer needs it.
