"""Send a signed lifecycle webhook POST using dev fixtures (SPEC_LOCAL_WEBHOOK_DEMO)."""

from __future__ import annotations

import argparse
import os
import sys
import urllib.error
import urllib.request
from importlib.resources import files
from pathlib import Path
from typing import Final, Sequence

from .signature import (
    LIFECYCLE_WEBHOOK_SIGNATURE_HEADER,
    compute_lifecycle_webhook_signature_header,
)

DEFAULT_DEMO_POST_URL: Final[str] = "http://127.0.0.1:8000/webhook"
DEFAULT_FIXTURE_PRESET: Final[str] = "run_completed"
_ENV_SECRET: Final[str] = "REPLAYT_LIFECYCLE_WEBHOOK_SECRET"

_BUILTIN_PRESETS: Final[frozenset[str]] = frozenset(
    {
        "run_completed",
        "run_started",
        "run_failed",
        "approval_pending",
        "approval_resolved",
    }
)


def load_demo_fixture_bytes(fixture: str) -> bytes:
    """Load raw POST body bytes from a filesystem path or a built-in preset name."""
    raw = fixture.strip()
    path = Path(raw).expanduser()
    if path.is_file():
        return path.read_bytes()

    name = raw.removesuffix(".json")
    if name not in _BUILTIN_PRESETS:
        names = ", ".join(sorted(_BUILTIN_PRESETS))
        raise ValueError(
            f"unknown fixture preset {name!r}; use a path to a JSON file or one of: {names}"
        )
    root = files("replayt_lifecycle_webhooks")
    rel = root.joinpath("fixtures", "events", f"{name}.json")
    if not rel.is_file():
        raise FileNotFoundError(f"missing packaged fixture: {name}.json")
    return rel.read_bytes()


def post_signed_demo(
    *,
    url: str,
    secret: str | bytes,
    body: bytes,
    timeout: float,
) -> int:
    """POST body with v1 Replayt-Signature. Returns HTTP status code (may be non-2xx)."""
    sig = compute_lifecycle_webhook_signature_header(secret=secret, body=body)
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/json; charset=utf-8")
    req.add_header(LIFECYCLE_WEBHOOK_SIGNATURE_HEADER, sig)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return int(resp.status)
    except urllib.error.HTTPError as exc:
        return int(exc.code)
    except urllib.error.URLError:
        raise


def _parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    env_secret = os.environ.get(_ENV_SECRET)
    p = argparse.ArgumentParser(
        description=(
            "POST a signed lifecycle webhook body to a local listener. "
            f"Reads the shared secret from {_ENV_SECRET} or --secret (prefer the env var in runbooks). "
            "Does not print the secret, full signature header, or MAC on success paths."
        ),
        epilog=(
            f"Exit codes: 0 if HTTP 2xx; 2 if the secret is missing; 1 for transport errors, "
            f"unknown fixtures, or non-2xx HTTP responses. Default URL: {DEFAULT_DEMO_POST_URL}. "
            "Built-in --fixture presets ship inside the package (same bytes as tests/fixtures/events/ in "
            "the source tree). You may also pass a path to any JSON file to send those octets unchanged."
        ),
    )
    p.add_argument(
        "--url",
        default=DEFAULT_DEMO_POST_URL,
        help=f"Target URL for the POST (default: {DEFAULT_DEMO_POST_URL}).",
    )
    p.add_argument(
        "--fixture",
        default=DEFAULT_FIXTURE_PRESET,
        metavar="PATH_OR_PRESET",
        help=(
            f"Fixture: path to a JSON file (read as binary), or a packaged preset name "
            f"(default: {DEFAULT_FIXTURE_PRESET}). Presets: {', '.join(sorted(_BUILTIN_PRESETS))}."
        ),
    )
    p.add_argument(
        "--secret",
        default=env_secret,
        help=(
            "Webhook HMAC secret. Prefer "
            f"{_ENV_SECRET} so the value is not passed on the shell; this flag is for local debugging only."
        ),
    )
    p.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="HTTP timeout in seconds (default: 30).",
    )
    return p.parse_args(list(argv) if argv is not None else None)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    secret = args.secret
    if secret is None or (isinstance(secret, str) and not secret.strip()):
        print(
            f"error: no webhook secret configured. Set {_ENV_SECRET} or pass --secret "
            "(avoid --secret in production shell history).",
            file=sys.stderr,
        )
        return 2

    try:
        body = load_demo_fixture_bytes(str(args.fixture))
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    try:
        code = post_signed_demo(
            url=str(args.url),
            secret=secret,
            body=body,
            timeout=float(args.timeout),
        )
    except urllib.error.URLError as exc:
        print(f"error: request failed ({exc.reason!r})", file=sys.stderr)
        return 1

    if 200 <= code < 300:
        print(f"HTTP {code}")
        return 0

    print(f"error: HTTP {code} (expected 2xx)", file=sys.stderr)
    return 1


def _cli_main() -> None:
    raise SystemExit(main())


if __name__ == "__main__":
    _cli_main()
