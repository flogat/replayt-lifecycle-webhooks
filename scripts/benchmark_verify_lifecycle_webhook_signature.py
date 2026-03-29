#!/usr/bin/env python3
"""Stdlib timing harness for ``verify_lifecycle_webhook_signature`` (backlog `1b3df584`).

Mirrors ``tests/test_perf_verify_hotpath.py`` (fixed 4 KiB body, UTF-8 secret, PG7: no
network/subprocess/sleep). Exit code ``1`` if the median ratio exceeds ``K`` (same
default as the pytest module). For merge posture see **README.md** (**Running tests**).
"""

from __future__ import annotations

import argparse
import hashlib
import hmac
import statistics
import sys
import time

from replayt_lifecycle_webhooks.signature import (
    compute_lifecycle_webhook_signature_header,
    verify_lifecycle_webhook_signature,
)

_SECRET = "perf-hotpath-regression-guard-secret"
_BODY: bytes = (bytes(range(256)) * 16)[:4096]
_SIGNATURE = compute_lifecycle_webhook_signature_header(secret=_SECRET, body=_BODY)
_HMAC_KEY = _SECRET.encode("utf-8")
_DEFAULT_K = 256
_WARMUP = 5
_SAMPLES = 50
_DISCARD = 10


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--k",
        type=float,
        default=_DEFAULT_K,
        help=f"Maximum allowed median verify/hmac ratio (default {_DEFAULT_K})",
    )
    args = parser.parse_args(argv)

    def run_verify() -> None:
        verify_lifecycle_webhook_signature(
            secret=_SECRET, body=_BODY, signature=_SIGNATURE, metrics=None
        )

    def run_hmac() -> None:
        hmac.new(_HMAC_KEY, _BODY, hashlib.sha256).digest()

    for _ in range(_WARMUP):
        run_verify()
        run_hmac()

    v_times: list[float] = []
    h_times: list[float] = []
    for _ in range(_SAMPLES):
        t0 = time.perf_counter()
        run_verify()
        v_times.append(time.perf_counter() - t0)
        t0 = time.perf_counter()
        run_hmac()
        h_times.append(time.perf_counter() - t0)

    v_med = statistics.median(v_times[_DISCARD:])
    h_med = statistics.median(h_times[_DISCARD:])
    ratio = v_med / h_med if h_med else float("inf")
    print(f"median verify (s): {v_med:.6g}")
    print(f"median hmac (s):   {h_med:.6g}")
    print(f"ratio verify/hmac: {ratio:.3g} (limit K={args.k})")
    if ratio > args.k:
        print("benchmark: ratio exceeds K", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
