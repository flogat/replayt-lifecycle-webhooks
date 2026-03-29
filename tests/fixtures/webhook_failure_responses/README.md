# Webhook failure response fixtures

Each `*.json` file is one line of compact UTF-8 JSON, matching **§ Canonical end-to-end examples** in
[`docs/SPEC_WEBHOOK_FAILURE_RESPONSES.md`](../../docs/SPEC_WEBHOOK_FAILURE_RESPONSES.md) (anchor
`#canonical-end-to-end-examples`). Field order is `error` then `message`, same as
`handle_lifecycle_webhook_post` (`json.dumps(..., separators=(",", ":"), ensure_ascii=True)`).

Files have **no trailing newline** so bytes match the handler body exactly.

Verified by **`tests/test_webhook_failure_response_fixtures.py`**.
