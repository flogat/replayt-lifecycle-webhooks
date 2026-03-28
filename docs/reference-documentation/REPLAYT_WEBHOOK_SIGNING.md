# Replayt-compatible lifecycle webhook signing (consumer contract)

This file records the **verification contract** implemented in `replayt_lifecycle_webhooks`.
It is the authority cited from `docs/SPEC_WEBHOOK_SIGNATURE.md` until replayt publishes a
dedicated HTTP delivery document.

## Signing scheme version

- **v1** (document name: `replayt-lifecycle-hmac-sha256-v1`): rules in this file. No separate version header in v1; see **`docs/SPEC_WEBHOOK_SIGNATURE.md`** for how future versions will be introduced.

## Algorithm and material

- **MAC:** HMAC-SHA256.
- **Signed input:** the **raw HTTP request body** (bytes exactly as received).
- **Key:** the shared secret. In this package, a Python `str` secret is encoded as **UTF-8** for the HMAC key.

## Header

- **Name:** `Replayt-Signature` (HTTP headers are case-insensitive).
- **Value:** either
  - `sha256=` followed by a 64-character hexadecimal encoding of the HMAC digest, or
  - the same 64-character hex string without the `sha256=` prefix.

## Clock skew and replay (v1)

- **Clock skew:** not part of v1 — there is no required timestamp in the signed material or headers.
- **Replay protection:** not specified in v1; use application-level idempotency or freshness controls if needed.

## Verification steps (summary)

1. Capture the raw body as bytes.
2. Read the `Replayt-Signature` header value.
3. Verify the MAC against the body and secret (e.g. `verify_lifecycle_webhook_signature`) before parsing JSON.

## Upstream note

The **replayt** PyPI package (checked at `0.4.25`) does not ship HTTP webhook client code or
header names in the installed tree. Automation that POSTs lifecycle events should match this
contract or document any intentional difference; this repo bumps tests and changelog when the
contract changes.
