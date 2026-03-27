# Dependency audit

CI **`supply-chain`** runs `pip-audit --ignore-vuln CVE-2026-4539 --desc` after `pip install -e ".[dev]"`. PyPA **pip-audit**
has no `--severity-high` flag; add further `--ignore-vuln` entries only with a short write-up under **Accepted risks**.

## Accepted risks

### CVE-2026-4539 (pygments)

Transitive **pygments** may report **CVE-2026-4539** (ReDoS in **AdlLexer**). This scaffold does not use that lexer; remove the
ignore from `.github/workflows/ci.yml` when your resolved dependency tree no longer needs it.
