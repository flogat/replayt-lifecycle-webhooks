"""Property fuzz: ``parse_lifecycle_webhook_event`` (**PF6**, **PF7**, **PF10**).

**PF9** is omitted; see :mod:`test_property_fuzz_signature` module docstring.

**Hypothesis:** ``max_examples`` set per test; ``deadline=None`` for CPU variance on CI.
"""

from __future__ import annotations

import pytest

pytest.importorskip("hypothesis")

from hypothesis import given, settings
from hypothesis import strategies as st
from pydantic import ValidationError

from replayt_lifecycle_webhooks.events import parse_lifecycle_webhook_event

_json_scalars = st.one_of(
    st.none(),
    st.booleans(),
    st.integers(min_value=-(10**6), max_value=10**6),
    st.floats(allow_nan=False, allow_infinity=False, width=32),
    st.text(max_size=64),
)

_json_values = st.recursive(
    _json_scalars,
    lambda children: st.one_of(
        st.lists(children, max_size=12),
        st.dictionaries(
            st.text(min_size=0, max_size=32),
            children,
            max_size=16,
        ),
    ),
    max_leaves=96,
)

_object_payloads = st.dictionaries(
    st.text(min_size=0, max_size=48),
    _json_values,
    max_size=24,
)

_non_dict_payload = st.one_of(
    st.none(),
    st.booleans(),
    st.integers(),
    st.floats(allow_nan=False, allow_infinity=False, width=32),
    st.text(),
    st.binary(max_size=64),
    st.lists(st.integers(), max_size=6),
    st.tuples(st.integers(), st.text(max_size=8)),
)


@pytest.mark.property_fuzz
@settings(max_examples=50, deadline=None)
@given(data=_object_payloads)
def test_parse_dict_only_validation_error_or_success(data: dict) -> None:
    """**PF6:** Random JSON-shaped dicts yield a model or ``ValidationError`` only."""
    try:
        parse_lifecycle_webhook_event(data)
    except ValidationError:
        return
    except BaseException as exc:  # pragma: no cover - property failure path
        pytest.fail(f"unexpected exception: {type(exc).__name__}: {exc}")


@pytest.mark.property_fuzz
@settings(max_examples=40, deadline=None)
@given(data=_non_dict_payload)
def test_parse_non_dict_raises_typeerror_only(data: object) -> None:
    """**PF7:** Non-``dict`` inputs raise ``TypeError`` only."""
    with pytest.raises(TypeError):
        parse_lifecycle_webhook_event(data)
