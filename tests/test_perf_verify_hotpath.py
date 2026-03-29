"""Opt-in hot-path timing for ``verify_lifecycle_webhook_signature`` (backlog `1b3df584`).

Checklist **PG1**–**PG8** in ``docs/SPEC_AUTOMATED_TESTS.md`` § Backlog ``1b3df584``.

**PG6:** ``t_verify`` (median wall time of the success-path verifier) is compared to a
same-run **stdlib** control ``hmac.new(key, body, hashlib.sha256).digest()`` using the
UTF-8 key bytes for the fixed ``str`` secret.

**``K``:** ``256``. On reference runs the median ratio ``t_verify / t_hmac`` is near
``~1.3``; ``K`` leaves room for interpreter and VM variance while still failing if verify
balloons to hundreds of times the cost of a single bare HMAC (accidental quadratic work,
extra copies, etc.).
"""

from __future__ import annotations

import hashlib
import hmac
import statistics
import time

import pytest

from replayt_lifecycle_webhooks.signature import (
    compute_lifecycle_webhook_signature_header,
    verify_lifecycle_webhook_signature,
)

# PG3: fixed deterministic secret (UTF-8 str) and 4 KiB body (opaque stable octets).
_PERF_SECRET = "perf-hotpath-regression-guard-secret"
_PERF_BODY: bytes = (bytes(range(256)) * 16)[:4096]
_PERF_SIGNATURE = compute_lifecycle_webhook_signature_header(
    secret=_PERF_SECRET, body=_PERF_BODY
)
_HMAC_KEY = _PERF_SECRET.encode("utf-8")

# PG6: order-of-magnitude guard; generous for shared runners (see module docstring).
_PERF_VERIFY_VS_HMAC_K = 256

_WARMUP_UNTIMED = 5
_TIMED_SAMPLES = 50
_DISCARD_FIRST_TIMED = 10


def _time_call(fn) -> float:
    t0 = time.perf_counter()
    fn()
    return time.perf_counter() - t0


@pytest.mark.perf_hotpath
def test_verify_success_path_within_hmac_ratio() -> None:
    """PG4–PG6: success-path ``verify_lifecycle_webhook_signature`` vs stdlib HMAC."""

    def run_verify() -> None:
        verify_lifecycle_webhook_signature(
            secret=_PERF_SECRET,
            body=_PERF_BODY,
            signature=_PERF_SIGNATURE,
            metrics=None,
        )

    def run_hmac() -> None:
        hmac.new(_HMAC_KEY, _PERF_BODY, hashlib.sha256).digest()

    # PG5: untimed warm-up.
    for _ in range(_WARMUP_UNTIMED):
        run_verify()
        run_hmac()

    verify_samples: list[float] = []
    hmac_samples: list[float] = []
    for _ in range(_TIMED_SAMPLES):
        verify_samples.append(_time_call(run_verify))
        hmac_samples.append(_time_call(run_hmac))

    v_rest = verify_samples[_DISCARD_FIRST_TIMED:]
    h_rest = hmac_samples[_DISCARD_FIRST_TIMED:]
    t_verify = statistics.median(v_rest)
    t_hmac = statistics.median(h_rest)
    assert t_hmac > 0
    assert t_verify <= _PERF_VERIFY_VS_HMAC_K * t_hmac
