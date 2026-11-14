"""Pickle round-trip for the Rust file-slice classes.

Both rebuild from ``__getnewargs__`` alone, so every field must be in it.
"""

import copy
import pickle

import pytest

try:
    from sqlfluff.core.parser.rust_parser import _HAS_RUST_PARSER
    from sqlfluffrs import RsRawFileSlice, RsTemplatedFileSlice
except ImportError:  # pragma: no cover
    _HAS_RUST_PARSER = False


def _fields(o):
    if isinstance(o, RsRawFileSlice):
        return (o.raw, o.slice_type, o.source_idx, o.block_idx, o.tag)
    return (o.slice_type, o.source_slice, o.templated_slice)


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
@pytest.mark.parametrize(
    "make",
    [
        lambda: RsRawFileSlice("select 1", "literal", 0),
        lambda: RsRawFileSlice("{% if x %}", "block_start", 12, 3, "if"),
        lambda: RsRawFileSlice("héllo ✓", "templated", 99, 7, None),
        lambda: RsTemplatedFileSlice("templated", slice(10, 25), slice(10, 11)),
    ],
)
@pytest.mark.parametrize("protocol", range(2, pickle.HIGHEST_PROTOCOL + 1))
def test__rs_fileslice__pickle_roundtrip(make, protocol):
    """Every field survives pickle and deepcopy."""
    obj = make()
    back = pickle.loads(pickle.dumps(obj, protocol=protocol))
    assert type(back) is type(obj)
    assert _fields(back) == _fields(obj)
    assert _fields(copy.deepcopy(obj)) == _fields(obj)
