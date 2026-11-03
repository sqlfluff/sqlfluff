"""Pickle round-trip for the Rust file-slice classes.

Both rebuild from ``__getnewargs__`` alone, so every field must be in it.
"""

import copy
import pickle

import pytest

sqlfluffrs = pytest.importorskip("sqlfluffrs")


def _fields(o):
    if isinstance(o, sqlfluffrs.RsRawFileSlice):
        return (o.raw, o.slice_type, o.source_idx, o.block_idx, o.tag)
    return (o.slice_type, o.source_slice, o.templated_slice)


@pytest.mark.parametrize(
    "obj",
    [
        sqlfluffrs.RsRawFileSlice("select 1", "literal", 0),
        sqlfluffrs.RsRawFileSlice("{% if x %}", "block_start", 12, 3, "if"),
        sqlfluffrs.RsRawFileSlice("héllo ✓", "templated", 99, 7, None),
        sqlfluffrs.RsTemplatedFileSlice("templated", slice(10, 25), slice(10, 11)),
    ],
)
@pytest.mark.parametrize("protocol", range(2, pickle.HIGHEST_PROTOCOL + 1))
def test__rs_fileslice__pickle_roundtrip(obj, protocol):
    """Every field survives pickle and deepcopy."""
    back = pickle.loads(pickle.dumps(obj, protocol=protocol))
    assert type(back) is type(obj)
    assert _fields(back) == _fields(obj)
    assert _fields(copy.deepcopy(obj)) == _fields(obj)
