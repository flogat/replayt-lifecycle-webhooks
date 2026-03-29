# Dependency audit

**Alignment spec:** **[SPEC_PIP_AUDIT_SUPPRESSION_ALIGNMENT.md](SPEC_PIP_AUDIT_SUPPRESSION_ALIGNMENT.md)** defines how
**`pip-audit --ignore-vuln`** flags in **`.github/workflows/ci.yml`** must match the **`## Accepted risks`** section below,
how entries are parsed, and the **Next review (UTC)** rule enforced in CI (**`supply-chain`** job and **`pytest`**).

## Adding or updating a pip-audit ignore

Do **not** add **`--ignore-vuln`** in CI without prose in **`## Accepted risks`** (and the reverse). For each CVE:

1. Add an **`###`** heading that contains **exactly one** id of the form **`CVE-YYYY-NNNN`** (see the alignment spec).
2. Link the advisory (PyPI advisory page, **OSV**, **GitHub Security Advisory**, or equivalent).
3. Explain **rationale** (why this repository accepts the risk — unused code path, transitive dev-only exposure, etc.).
4. Set **`Next review (UTC): YYYY-MM-DD`** — when a maintainer must re-check the advisory and either renew the date,
   remove the ignore, or bump dependencies. Renew in the **same PR** as the decision.

Then mirror **`--ignore-vuln <id>`** on the **`pip-audit`** line in the **`supply-chain`** job so the documented set and
workflow set stay identical.

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

- **Advisory:** <https://osv.dev/vulnerability/CVE-2026-4539>
- **Rationale:** Transitive **pygments** may report **CVE-2026-4539** (ReDoS in **AdlLexer**). This package does not use that
  lexer path; risk is accepted until the resolved **dev** dependency tree no longer triggers the finding.
- **Next review (UTC):** 2026-12-01

Remove **`--ignore-vuln CVE-2026-4539`** from **`.github/workflows/ci.yml`** when **`pip-audit`** passes without it after
**`pip install -e ".[dev]"`**.
