# Replayt-compatible lifecycle webhook signing (consumer contract)

This file records the **verification contract** implemented in `replayt_lifecycle_webhooks`
as of the phase-3 backlog work. It is the authority cited from
`docs/SPEC_WEBHOOK_SIGNATURE.md` until replayt publishes a dedicated HTTP delivery document.

## Algorithm and material

- **MAC:** HMAC-SHA256.
- **Signed input:** the **raw HTTP request body** (bytes exactly as received).
- **Key:** the shared secret. In this package, a Python `str` secret is encoded as **UTF-8** for the HMAC key.

## Header

- **Name:** `Replayt-Signature` (HTTP headers are case-insensitive).
- **Value:** either
  - `sha256=` followed by a 64-character hexadecimal encoding of the HMAC digest, or
  - the same 64-character hex string without the `sha256=` prefix.

## Upstream note

The **replayt** PyPI package (checked at `0.4.25`) does not ship HTTP webhook client code or
header names in the installed tree. Automation that POSTs lifecycle events should match this
contract or document any intentional difference; this repo bumps tests and changelog when the
contract changes.
