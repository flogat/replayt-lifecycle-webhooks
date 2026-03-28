"""Redact sensitive HTTP headers and mapping values before logging (stdlib only).

Normative defaults and matching rules: ``docs/SPEC_STRUCTURED_LOGGING_REDACTION.md``.

**Header matching:** names are compared case-insensitively. A name is sensitive if:

- its lowercased form equals one of the built-in exact names (see
  :data:`DEFAULT_SENSITIVE_HEADER_NAMES`), or
- its lowercased form starts with ``x-signature`` (``X-Signature*`` prefix rule).

**Integrator extensions:** :func:`redact_headers` ``extra_sensitive_names`` are matched
case-insensitively as **exact** names only (no prefix rule).

**Mapping keys:** compared after lowercasing the key string. Redaction replaces **str** or
**bytes** values with :data:`REDACTED_PLACEHOLDER`; other value types are copied unchanged
(shallow copy only for :func:`redact_mapping`).
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

REDACTED_PLACEHOLDER = "[REDACTED]"

# Lowercased exact header field-names (HTTP is case-insensitive on the wire).
_DEFAULT_HEADER_EXACT_LOWER: frozenset[str] = frozenset(
    {
        "authorization",
        "proxy-authorization",
        "cookie",
        "set-cookie",
        "replayt-signature",
        "x-api-key",
    }
)

_SIGNATURE_PREFIX_LOWER = "x-signature"

# Human-readable list for docs / introspection; ``X-Signature*`` is prefix-matched (see module docstring).
DEFAULT_SENSITIVE_HEADER_NAMES: tuple[str, ...] = (
    "Authorization",
    "Proxy-Authorization",
    "Cookie",
    "Set-Cookie",
    "Replayt-Signature",
    "X-Api-Key",
    "X-Signature*",
)

DEFAULT_SENSITIVE_MAPPING_KEYS: frozenset[str] = frozenset(
    {
        "authorization",
        "proxy-authorization",
        "cookie",
        "set-cookie",
        "replayt-signature",
        "signature",
        "x-api-key",
        "api-key",
        "api_key",
        "password",
        "secret",
        "token",
        "bearer",
        # Shallow redaction when integrators put request bodies in ``extra=``; prefer omission.
        "body",
        "raw_body",
        "payload",
        "request_body",
    }
)


def _is_sensitive_header_name(name: str, extra_lower_exact: frozenset[str]) -> bool:
    key = name.strip().lower()
    if key in _DEFAULT_HEADER_EXACT_LOWER or key in extra_lower_exact:
        return True
    return key.startswith(_SIGNATURE_PREFIX_LOWER)


def redact_headers(
    headers: Mapping[str, str] | Iterable[tuple[str, str]],
    *,
    extra_sensitive_names: Iterable[str] = (),
) -> dict[str, str]:
    """Copy ``headers`` into a new ``dict[str, str]``, redacting sensitive values.

    Original ``headers`` is not modified. Values for sensitive names are replaced with
    :data:`REDACTED_PLACEHOLDER`. Non-string values are coerced with ``str()`` for the
    returned mapping so the result is always ``dict[str, str]``.
    """
    extra_lower = frozenset(
        n.strip().lower() for n in extra_sensitive_names if n.strip()
    )
    out: dict[str, str] = {}
    items = headers.items() if isinstance(headers, Mapping) else headers
    for raw_name, raw_val in items:
        name = str(raw_name)
        val = (
            REDACTED_PLACEHOLDER
            if _is_sensitive_header_name(name, extra_lower)
            else str(raw_val)
        )
        out[name] = val
    return out


def _mapping_key_sensitive(key: str, extra_lower: frozenset[str]) -> bool:
    return (
        key.strip().lower() in DEFAULT_SENSITIVE_MAPPING_KEYS
        or key.strip().lower() in extra_lower
    )


def redact_mapping(
    mapping: Mapping[str, Any],
    *,
    extra_sensitive_keys: Iterable[str] = (),
) -> dict[str, Any]:
    """Shallow copy of ``mapping`` with sensitive **string** or **bytes** values redacted.

    Keys are sensitive if their lowercased form is in :data:`DEFAULT_SENSITIVE_MAPPING_KEYS`
    or in ``extra_sensitive_keys`` (compared lowercased). Nested dicts are not traversed.
    """
    extra_lower = frozenset(
        k.strip().lower() for k in extra_sensitive_keys if k.strip()
    )
    out: dict[str, Any] = {}
    for k, v in mapping.items():
        if _mapping_key_sensitive(str(k), extra_lower):
            if isinstance(v, str | bytes):
                out[k] = REDACTED_PLACEHOLDER
            else:
                out[k] = v
        else:
            out[k] = v
    return out


def format_safe_webhook_log_extra(
    *,
    headers: Mapping[str, str] | Iterable[tuple[str, str]] | None = None,
    method: str | None = None,
    path: str | None = None,
    uri: str | None = None,
    status_code: int | None = None,
    error_code: str | None = None,
    webhook_body_bytes_len: int | None = None,
    lifecycle_event_id: str | None = None,
    lifecycle_run_id: str | None = None,
    lifecycle_workflow_id: str | None = None,
    lifecycle_approval_request_id: str | None = None,
    extra_sensitive_header_names: Iterable[str] = (),
) -> dict[str, Any]:
    """Build a dict safe for ``Logger.*(..., extra={...})`` (no LogRecord name clashes).

    ``path`` wins over ``uri`` when both are set. Header names and values are copied through
    :func:`redact_headers` only (including ``extra_sensitive_header_names``). Other dict
    fields for ``extra=`` should use :func:`redact_mapping` separately. Keys use a ``webhook_``
    prefix so they avoid stdlib :class:`logging.LogRecord` attribute names.

    The returned mapping never includes raw body bytes or decoded body text. Optional
    ``webhook_body_bytes_len`` is a non-negative body length summary only. Correlation
    ``lifecycle_*`` fields should be taken from verified JSON only; keys whose values are
    ``None`` are omitted from the returned dict.
    """
    extra: dict[str, Any] = {}
    if method is not None:
        extra["webhook_method"] = method
    resolved_path = path if path is not None else uri
    if resolved_path is not None:
        extra["webhook_path"] = resolved_path
    if status_code is not None:
        extra["webhook_status_code"] = status_code
    if error_code is not None:
        extra["webhook_error_code"] = error_code
    if webhook_body_bytes_len is not None:
        if type(webhook_body_bytes_len) is not int:
            raise TypeError("webhook_body_bytes_len must be int or None")
        if webhook_body_bytes_len < 0:
            raise ValueError("webhook_body_bytes_len must be non-negative")
        extra["webhook_body_bytes_len"] = webhook_body_bytes_len
    if lifecycle_event_id is not None:
        extra["lifecycle_event_id"] = lifecycle_event_id
    if lifecycle_run_id is not None:
        extra["lifecycle_run_id"] = lifecycle_run_id
    if lifecycle_workflow_id is not None:
        extra["lifecycle_workflow_id"] = lifecycle_workflow_id
    if lifecycle_approval_request_id is not None:
        extra["lifecycle_approval_request_id"] = lifecycle_approval_request_id
    if headers is not None:
        extra["webhook_headers"] = redact_headers(
            headers,
            extra_sensitive_names=extra_sensitive_header_names,
        )
    return extra


__all__ = [
    "DEFAULT_SENSITIVE_HEADER_NAMES",
    "DEFAULT_SENSITIVE_MAPPING_KEYS",
    "REDACTED_PLACEHOLDER",
    "format_safe_webhook_log_extra",
    "redact_headers",
    "redact_mapping",
]
