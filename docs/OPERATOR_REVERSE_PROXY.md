# Reverse proxy and TLS in front of `python -m replayt_lifecycle_webhooks`

Short runbook for placing **nginx**, **Caddy**, or another reverse proxy in front of the **reference HTTP server** started
with **`python -m replayt_lifecycle_webhooks`**. The server contract (paths, defaults) is in
**[SPEC_HTTP_SERVER_ENTRYPOINT.md](SPEC_HTTP_SERVER_ENTRYPOINT.md)**.

**`Replayt-Signature`** is an **HMAC over the raw POST body**. The verifier must see the **same bytes** the sender signed.
Anything that **truncates**, **re-encodes**, or **rewrites** the body before the WSGI app can break verification even when TLS
and routing are otherwise correct. Full signing rules: **[docs/SPEC_WEBHOOK_SIGNATURE.md](SPEC_WEBHOOK_SIGNATURE.md)**.

## Raw body discipline

- Read the POST body as **bytes** from the HTTP stack **before** JSON parsing or in-place edits.
- Do not normalize JSON, inject fields, or change encoding before **`verify_lifecycle_webhook_signature`** (or equivalent).
- The MAC is over the **octets** your application receives **after** the proxy; configure the edge so those octets match the
  sender’s payload.

## Client maximum body size

Set a **documented** upper bound large enough for expected lifecycle JSON plus headroom. In **nginx**, **`client_max_body_size`**
controls the maximum request body the proxy accepts; values that are **too small** yield **413** or truncated bodies. A
truncated body almost always produces a **signature mismatch** that looks like an auth problem. Size the limit from your
largest realistic payload and retry envelopes, not from the smallest happy path.

## Timeouts

Configure **proxy read / send timeouts** and **upstream** idle timeouts so slow clients and **at-least-once** retries do not
produce spurious **502** or dropped connections that are hard to distinguish from application bugs. Retry and dedupe
semantics: **[docs/SPEC_DELIVERY_IDEMPOTENCY.md](SPEC_DELIVERY_IDEMPOTENCY.md)**.

## `Transfer-Encoding`, buffering, and byte-identical verification

Some proxies **buffer** or **normalize** bodies when juggling **chunked** **`Transfer-Encoding`** vs **`Content-Length`**.
The signature is over **whatever bytes the verifier reads**; the goal is **transparent forwarding** without **transformation**
or **truncation**, not a promise that nothing buffers (HTTP stacks may buffer internally). Misconfiguration here can change
the byte stream the app sees. Prefer settings that forward the body **unchanged** to the upstream process.

## Example: nginx → reference server

Defaults in **[SPEC_HTTP_SERVER_ENTRYPOINT.md](SPEC_HTTP_SERVER_ENTRYPOINT.md)** use host **`127.0.0.1`** and port **`8000`**
for local examples. Adjust **`proxy_pass`** and **`location`** to match your **`/webhook`** (or overridden) path.

```nginx
# HMAC is over the raw POST body — see docs/SPEC_WEBHOOK_SIGNATURE.md (SPEC_WEBHOOK_SIGNATURE).
server {
    listen 443 ssl;
    server_name webhook.example;

    # Large enough for lifecycle JSON + headroom; too small → 413 / truncated body / false signature failures.
    client_max_body_size 1m;

    location /webhook {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 60s;
        proxy_send_timeout 60s;
    }
}
```

Do not add **`access_log`** formats or middleware that write **full request bodies** to disk or logs.

## Logging and secrets

Operators **must not** log **full POST bodies**, the **shared webhook secret**, or complete **`Replayt-Signature`** header
values. Use structured **`logging`** with the redaction defaults in
**[docs/SPEC_STRUCTURED_LOGGING_REDACTION.md](SPEC_STRUCTURED_LOGGING_REDACTION.md)**.

## Checklist

- Body bytes reaching the app match the signed payload (**[docs/SPEC_WEBHOOK_SIGNATURE.md](SPEC_WEBHOOK_SIGNATURE.md)**).
- **`client_max_body_size`** (or your proxy’s equivalent) is sized for real payloads.
- Timeouts cover slow clients and retries (**[docs/SPEC_DELIVERY_IDEMPOTENCY.md](SPEC_DELIVERY_IDEMPOTENCY.md)**).
- Avoid proxy settings that rewrite **`Transfer-Encoding`** or the body stream in ways that change upstream bytes.
- Logs follow **[docs/SPEC_STRUCTURED_LOGGING_REDACTION.md](SPEC_STRUCTURED_LOGGING_REDACTION.md)**.
