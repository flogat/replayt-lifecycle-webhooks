"""Run the reference lifecycle webhook server (``python -m replayt_lifecycle_webhooks``)."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Sequence

from wsgiref.simple_server import make_server

from .serve import (
    DEFAULT_HOST,
    DEFAULT_PORT,
    DEFAULT_WEBHOOK_PATH,
    make_reference_lifecycle_webhook_wsgi_app,
)
from .signature import WebhookSignatureError, verify_lifecycle_webhook_signature


def _parse_serve_args(argv: Sequence[str] | None) -> argparse.Namespace:
    env_secret = os.environ.get("REPLAYT_LIFECYCLE_WEBHOOK_SECRET")
    p = argparse.ArgumentParser(
        description=(
            "Listen for signed lifecycle webhook POSTs and serve GET /health. "
            "Load the shared secret from REPLAYT_LIFECYCLE_WEBHOOK_SECRET or --secret. "
            "Offline MAC check for a saved body: "
            "python -m replayt_lifecycle_webhooks verify --help"
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
    p.add_argument(
        "--webhook-diagnostics",
        action="store_true",
        help=(
            "Emit one structured INFO log per webhook request (redacted headers, no raw body). "
            "Overrides REPLAYT_LIFECYCLE_WEBHOOK_DIAGNOSTICS when set."
        ),
    )
    p.add_argument(
        "--no-webhook-diagnostics",
        action="store_true",
        help="Disable webhook diagnostic logs even if REPLAYT_LIFECYCLE_WEBHOOK_DIAGNOSTICS is set.",
    )
    return p.parse_args(list(argv) if argv is not None else None)


def _parse_verify_args(argv: Sequence[str] | None) -> argparse.Namespace:
    env_secret = os.environ.get("REPLAYT_LIFECYCLE_WEBHOOK_SECRET")
    p = argparse.ArgumentParser(
        prog="python -m replayt_lifecycle_webhooks verify",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=(
            "Verify an offline copy of the raw POST body against Replayt-Signature using "
            "the same v1 HMAC-SHA256 rules as verify_lifecycle_webhook_signature."
        ),
        epilog=(
            "Raw body discipline: the MAC is over the exact bytes the HTTP layer received. "
            "Re-serializing JSON (pretty-print, key reordering) breaks verification.\n\n"
            "Secret: prefer REPLAYT_LIFECYCLE_WEBHOOK_SECRET so the value is not passed on "
            "the shell; --secret is for local debugging only.\n\n"
            "Exit codes: 0 verification succeeded (stdout prints ok); 1 verification failed "
            "(generic message on stderr); 2 usage, missing or empty secret, or I/O error.\n\n"
            "Handler-oriented steps: docs/SPEC_WEBHOOK_SIGNATURE.md"
            "#verification-procedure-integrators"
        ),
    )
    p.add_argument(
        "body",
        metavar="BODY",
        help="Path to the raw POST body file, or '-' to read body bytes from stdin.",
    )
    sig = p.add_mutually_exclusive_group(required=True)
    sig.add_argument(
        "--signature",
        metavar="VALUE",
        help="Replayt-Signature header field-value (sha256=<hex> or bare 64-char hex).",
    )
    sig.add_argument(
        "--signature-file",
        metavar="PATH",
        help=(
            "File containing the Replayt-Signature value. One trailing newline is stripped "
            "from the file contents."
        ),
    )
    p.add_argument(
        "--secret",
        default=env_secret,
        help=(
            "Webhook HMAC secret. Prefer REPLAYT_LIFECYCLE_WEBHOOK_SECRET; this flag is for "
            "local debugging only."
        ),
    )
    return p.parse_args(list(argv) if argv is not None else None)


def _read_signature_file(path: str) -> str:
    try:
        raw = Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        print(f"error: cannot read signature file: {exc}", file=sys.stderr)
        sys.exit(2)
    if raw.endswith("\r\n"):
        return raw[:-2]
    if raw.endswith("\n"):
        return raw[:-1]
    return raw


def main_verify(argv: Sequence[str] | None) -> None:
    args = _parse_verify_args(argv)
    secret = args.secret
    if secret is None or (isinstance(secret, str) and not secret.strip()):
        print(
            "error: no webhook secret configured. Set REPLAYT_LIFECYCLE_WEBHOOK_SECRET "
            "or pass --secret (avoid --secret in production shell history).",
            file=sys.stderr,
        )
        sys.exit(2)

    body_path = args.body
    if body_path == "-":
        try:
            body = sys.stdin.buffer.read()
        except OSError as exc:
            print(f"error: cannot read body from stdin: {exc}", file=sys.stderr)
            sys.exit(2)
    else:
        try:
            body = Path(body_path).read_bytes()
        except OSError as exc:
            print(f"error: cannot read body file: {exc}", file=sys.stderr)
            sys.exit(2)

    if args.signature is not None:
        signature = args.signature
    else:
        signature = _read_signature_file(args.signature_file)

    try:
        verify_lifecycle_webhook_signature(
            secret=secret, body=body, signature=signature
        )
    except WebhookSignatureError:
        print("signature verification failed", file=sys.stderr)
        sys.exit(1)

    sys.stdout.write("ok\n")


def main_serve(argv: Sequence[str] | None) -> None:
    args = _parse_serve_args(argv)
    secret = args.secret
    if secret is None or (isinstance(secret, str) and not secret.strip()):
        print(
            "error: no webhook secret configured. Set REPLAYT_LIFECYCLE_WEBHOOK_SECRET "
            "or pass --secret (avoid --secret in production shell history).",
            file=sys.stderr,
        )
        sys.exit(2)

    if args.webhook_diagnostics and args.no_webhook_diagnostics:
        print(
            "error: --webhook-diagnostics and --no-webhook-diagnostics cannot be used together.",
            file=sys.stderr,
        )
        sys.exit(2)
    if args.webhook_diagnostics:
        webhook_diagnostics = True
    elif args.no_webhook_diagnostics:
        webhook_diagnostics = False
    else:
        webhook_diagnostics = None

    app = make_reference_lifecycle_webhook_wsgi_app(
        secret=secret,
        webhook_path=args.webhook_path,
        webhook_diagnostics=webhook_diagnostics,
    )
    with make_server(args.host, args.port, app) as httpd:
        base = f"http://{args.host}:{args.port}"
        print(f"Listening on {base}{args.webhook_path} (POST); {base}/health (GET)")
        httpd.serve_forever()


def main(argv: Sequence[str] | None = None) -> None:
    argv_list = list(sys.argv[1:] if argv is None else argv)
    if argv_list and argv_list[0] == "verify":
        main_verify(argv_list[1:])
    else:
        main_serve(argv_list)


if __name__ == "__main__":
    main()
