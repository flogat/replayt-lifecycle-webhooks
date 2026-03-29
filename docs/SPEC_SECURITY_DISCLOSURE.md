# Spec: coordinated security disclosure (`SECURITY.md`)

**Backlog:** SECURITY.md and coordinated disclosure process  
**Workflow id:** `87e7edae-033d-45af-87fc-066fca51db96` (phase **2** spec; phase **3** shipped root **`SECURITY.md`**, **`README.md`** / **`CONTRIBUTING.md`** links, and **`tests/test_security_disclosure_doc.py`** for **SEC1**–**SEC9**).

**Audience:** Spec gate (2b), Builder (3), Tester (4), Architect / Design gate (5 / 5b), security researchers, enterprise adopters, maintainers.

## Purpose and normative status

This document is the **contract** for a **repository root** **[`SECURITY.md`](../SECURITY.md)** that explains **how to report
security-sensitive findings** about **this package’s consumer-side verification surface** and related documentation. It
**does not** replace upstream **replayt**’s own security process for the core product or its infrastructure.

**Normative for Builder:** When this backlog is in scope, **`SECURITY.md`** **must** satisfy **§ Required contents** and
**§ Disclosure hygiene (no secret leakage)**. **`README.md`** and **`CONTRIBUTING.md`** **must** satisfy **§ Repository
cross-links**. **§ Optional CI and test-vector hygiene** is **recommended** but not merge-blocking unless the **Spec gate**
elevates it.

**Non-goals:** Legal advice, a bug bounty program, or guarantees about disclosure embargoes beyond what maintainers can
credibly commit to in an OSS policy.

## Backlog acceptance mapping (`87e7edae`)

| Source criterion | Where addressed in this spec |
| ---------------- | ---------------------------- |
| Root **SECURITY.md** with **scope** (this repo vs upstream **replayt**) | **§ Required contents** — **Supported scope** |
| **Expected response cadence** | **§ Required contents** — **Response expectations** |
| **Contact / reporting method** | **§ Required contents** — **How to report** |
| Link from **README** and **GitHub** security policy | **§ Repository cross-links**; file location **§ Deliverable location** |
| Align with **no secret leakage** / existing specs | **§ Disclosure hygiene (no secret leakage)** |
| Optional: **CI** / security-sensitive **test vectors** | **§ Optional CI and test-vector hygiene** |

## Deliverable location

- **Primary file:** **`SECURITY.md`** at the **repository root** (same directory as **`README.md`**).  
  **GitHub** surfaces this path as the repository **Security policy** when present ([GitHub docs: Adding a security policy](https://docs.github.com/code-security/getting-started/adding-a-security-policy-to-your-repository)).
- **Do not** replace the root file with **only** **`.github/SECURITY.md`** for this backlog—the acceptance criteria call for
  **root** **`SECURITY.md`**. (A duplicate under **`.github/`** is **optional** if maintainers want symmetry with other
  templates; **pytest** rows **SEC1**–**SEC9** target the **root** file unless a future backlog says otherwise.)

## Required contents (`SECURITY.md`)

Use clear **markdown headings** so readers and doc-guard tests can rely on stable sections. The exact heading text may vary
slightly, but **Builder** **must** cover every bullet below with a dedicated subsection (level-2 **`## …`** recommended).

### Title

- **SC1:** First visible heading **should** be level-1 **`# …`** whose title includes **Security** (for example **`# Security policy`**).

### Supported scope

- **SC2 — In scope (this repository):** Explicit **in-scope** list **must** include at least:
  - **Signature verification** and **HMAC** handling implemented **in this package** (for example
    **`verify_lifecycle_webhook_signature`** and closely related verification helpers).
  - **Optional HTTP surfaces shipped here** (reference server, minimal handler, **WSGI** app factories) **when** they
    affect **authentication or integrity** of lifecycle webhooks **or** could **leak** webhook secrets, raw signing
    material, or full **`Replayt-Signature`** values through responses, logs, or error paths.
  - **Documentation bugs** that would **systematically** cause integrators to **skip** verification or **mis-handle** secrets
    in a way that defeats the stated contract—**coordinate** before public issue discussion when exploitation is plausible.
- **SC3 — Out of scope (upstream and neighbors):** Explicit **out-of-scope** list **must** name **upstream replayt** (the
  **PyPI** distribution and its core semantics / signing **product** behavior) and **must** tell reporters to use **that
  project’s** (or vendor’s) **own** reporting channels for issues **outside** this repository’s **Python verification**
  surface. It **should** mention **dependency CVEs** (for example **PyPI** advisories) as **usually** handled via **public**
  issues or **Dependabot**-style upgrades unless maintainers declare otherwise.

### How to report

- **SC4:** **Primary channel** **must** be documented using **at least one** of:
  - **GitHub** private vulnerability reporting (**Security** tab → **Report a vulnerability**), **or**
  - A **mailto:** address **or** stable contact URL **owned by maintainers**, **or**
  - **Both**, with guidance on which to prefer.
- **SC5:** **Must** ask reporters **not** to file **public** issues (or **public** discussions) with **undisclosed exploit**
  details; point them at the **private** channel first.

### Response expectations

- **SC6:** **Must** state a **best-effort** **initial acknowledgement** window (recommended text: **within three business
  days** for well-formed reports).
- **SC7:** **Must** state that **severity assessment** and **fix timelines** vary, and **should** promise **periodic updates**
  while the report is **actively** under investigation (recommended: **at least every 14 calendar days** when status
  changes are expected, or a single honest “no update yet” ping).

### Disclosure hygiene (no secret leakage)

- **SC8:** **Must** explicitly ask reporters **not** to paste **live** **HMAC** keys, **full** **`Replayt-Signature`**
  header values tied to real deployments, or **raw webhook bodies** that contain **production** **PII** or secrets.
- **SC9:** **Must** link **at least one** of:
  - **[SPEC_WEBHOOK_SIGNATURE.md](SPEC_WEBHOOK_SIGNATURE.md)** (verification contract and failure-handling boundaries), **or**
  - **[SPEC_STRUCTURED_LOGGING_REDACTION.md](SPEC_STRUCTURED_LOGGING_REDACTION.md)** (logging redaction expectations), **or**
  - **[DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)** (**LLM / demos** redaction expectations).  
  **Prefer two** when space allows so researchers see both **crypto** and **logging** norms.

## Repository cross-links

- **SC10 — README:** Root **`README.md`** **must** include a **markdown link** whose target is **`SECURITY.md`** (relative
  form **`[…](SECURITY.md)`** or **`./SECURITY.md`** is fine). **Recommended placement:** the **Overview** bullet list (near
  **Report breakage**) **or** **`## Troubleshooting`** so operators and researchers see it without hunting.
- **SC11 — CONTRIBUTING:** **`CONTRIBUTING.md`** **must** include a short **Security** note: for **undisclosed**
  **security-sensitive** issues, follow **`SECURITY.md`** at the repository root (name it explicitly, with a **markdown
  link** **`[SECURITY.md](SECURITY.md)`** once the file exists in **git**) and link **`docs/SPEC_SECURITY_DISCLOSURE.md`**
  for the normative contract. **Do not** paste exploit-ready payloads or secrets into **Issues** / **PR** comments.  
  **Phase 2 / spec-only PRs** may use plain monospace **`SECURITY.md`** (no hyperlink) until **Builder** adds the file; the
  **SEC9** **pytest** row still passes when **CONTRIBUTING** links **SPEC_SECURITY_DISCLOSURE** and names **`SECURITY.md`**.

## Optional CI and test-vector hygiene

**Recommended** subsection in **`SECURITY.md`** **or** **`CONTRIBUTING.md`** (either is acceptable for this optional bullet):

- Security-sensitive **fixtures** and **test vectors** in **`tests/`** and **`src/…/fixtures/`** **should** follow the same
  **redaction** mindset as **[DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)** (**LLM / demos**) and
  **[SPEC_STRUCTURED_LOGGING_REDACTION.md](SPEC_STRUCTURED_LOGGING_REDACTION.md)**—**no** real shared secrets, **no** live
  **full** signatures presented as production truth, and **no** raw production bodies in committed files.
- **CI** **should** remain **network-free** for cryptographic tests per **[SPEC_AUTOMATED_TESTS.md](SPEC_AUTOMATED_TESTS.md)**;
  do not add “phone home” secret exfiltration checks without a separate backlog.

This subsection is **not** part of **SEC1**–**SEC9** **pytest** acceptance unless the project promotes it to merge-blocking in
a later backlog.

## Release hygiene

When **Builder** adds or materially changes **`SECURITY.md`** or the **README** / **CONTRIBUTING** cross-links:

- Add a bullet under **`CHANGELOG.md`** **Unreleased** (**Documentation** or **Security**, per project convention)
  referencing this backlog.

**Phase 2 (spec-only):** No **`CHANGELOG`** entry is **required** until **`SECURITY.md`** ships; this spec file is the
maintainer-facing contract.

## Automated acceptance

See **§ Backlog `87e7edae`** in **[SPEC_AUTOMATED_TESTS.md](SPEC_AUTOMATED_TESTS.md)** (**SEC1**–**SEC9**). Implementations
**must** use **network-free** tests that read **`SECURITY.md`**, **`README.md`**, and **`CONTRIBUTING.md`** from disk (same
pattern as **OP1**–**OP9**).

## Related docs

- **[SPEC_WEBHOOK_SIGNATURE.md](SPEC_WEBHOOK_SIGNATURE.md)** — verification procedure; failure mapping; secret hygiene.
- **[SPEC_STRUCTURED_LOGGING_REDACTION.md](SPEC_STRUCTURED_LOGGING_REDACTION.md)** — structured logging and redaction.
- **[SPEC_WEBHOOK_FAILURE_RESPONSES.md](SPEC_WEBHOOK_FAILURE_RESPONSES.md)** — stable **`error`** codes; response bodies.
- **[DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)** — **LLM / demos** and **explicit contracts** index.
- **[MISSION.md](MISSION.md)** — scope split between this package and **replayt** upstream.
