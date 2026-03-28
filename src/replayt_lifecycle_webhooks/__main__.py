"""Run the reference lifecycle webhook server (``python -m replayt_lifecycle_webhooks``)."""

from __future__ import annotations

import argparse
import os
import sys
from typing import Sequence

from wsgiref.simple_server import make_server

from .serve import (
    DEFAULT_HOST,
    DEFAULT_PORT,
    DEFAULT_WEBHOOK_PATH,
    make_reference_lifecycle_webhook_wsgi_app,
)


def _parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    env_secret = os.environ.get("REPLAYT_LIFECYCLE_WEBHOOK_SECRET")
    p = argparse.ArgumentParser(
        description=(
            "Listen for signed lifecycle webhook POSTs and serve GET /health. "
            "Load the shared secret from REPLAYT_LIFECYCLE_WEBHOOK_SECRET or --secret."
        ),
    )
    p.add_argument(
        "--host",
        default=DEFAULT_HOST,
        help=f"Bind address (default: {DEFAULT_HOST}).",
    )
    p.add_argument(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help=f"TCP port (default: {DEFAULT_PORT}).",
    )
    p.add_argument(
        "--webhook-path",
        default=DEFAULT_WEBHOOK_PATH,
        metavar="PATH",
        help=f"URL path for webhook POST (default: {DEFAULT_WEBHOOK_PATH}).",
    )
    p.add_argument(
        "--secret",
        default=env_secret,
        help=(
            "Webhook HMAC secret. Prefer REPLAYT_LIFECYCLE_WEBHOOK_SECRET so the value "
            "is not passed on the shell; this flag is intended for local debugging only."
        ),
    )
    return p.parse_args(list(argv) if argv is not None else None)


def main(argv: Sequence[str] | None = None) -> None:
    args = _parse_args(argv)
    secret = args.secret
    if secret is None or (isinstance(secret, str) and not secret.strip()):
        print(
            "error: no webhook secret configured. Set REPLAYT_LIFECYCLE_WEBHOOK_SECRET "
            "or pass --secret (avoid --secret in production shell history).",
            file=sys.stderr,
        )
        sys.exit(2)

    app = make_reference_lifecycle_webhook_wsgi_app(
        secret=secret,
        webhook_path=args.webhook_path,
    )
    with make_server(args.host, args.port, app) as httpd:
        base = f"http://{args.host}:{args.port}"
        print(f"Listening on {base}{args.webhook_path} (POST); {base}/health (GET)")
        httpd.serve_forever()


if __name__ == "__main__":
    main()
