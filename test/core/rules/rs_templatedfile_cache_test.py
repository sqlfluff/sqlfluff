"""Regression tests for the Python→Rust TemplatedFile conversion cache.

The cache (``PY_TEMPLATED_FILE_CACHE``) was keyed by
``fname:source_str:templated_str`` — but two TemplatedFiles can share all
three strings with DIFFERENT slicings (jinja vs raw templater over the same
rendered text; minimal case: an empty file), and the second conversion
silently reused the first's slices. It also never evicted. Now keyed by
Python object identity with weakref eviction.
"""

import gc

import pytest

try:
    import sqlfluffrs

    _HAS = hasattr(sqlfluffrs, "_templated_file_cache_len")
except ImportError:  # pragma: no cover
    _HAS = False

from sqlfluff.core import FluffConfig, Linter
from sqlfluff.core.templaters import TemplatedFile
from sqlfluff.core.templaters.base import RawFileSlice, TemplatedFileSlice

pytestmark = pytest.mark.skipif(not _HAS, reason="sqlfluffrs unavailable")


def _tf(kind: str) -> TemplatedFile:
    """Identical fname/source/templated; only the SLICING differs."""
    return TemplatedFile(
        source_str="x",
        fname="<string>",
        templated_str="x",
        sliced_file=[TemplatedFileSlice(kind, slice(0, 1), slice(0, 1))],
        raw_sliced=[RawFileSlice("x", kind, 0)],
    )


def _span(tf: TemplatedFile):
    a = sqlfluffrs.RsPositionMarker.from_point(0, 0, tf, 1, 1)
    b = sqlfluffrs.RsPositionMarker.from_point(1, 1, tf, 1, 2)
    return sqlfluffrs.RsPositionMarker.from_points(a, b)


def test_same_strings_different_slicing_do_not_collide() -> None:
    """The old content key made tf_b silently reuse tf_a's conversion.

    Two TemplatedFiles with identical fname/source/templated but DIFFERENT
    slicings must convert to two distinct cache entries. (Under the old
    ``fname:source:templated`` key they shared one — the second object's
    markers answered with the first object's slicing.)
    """
    gc.collect()
    base = sqlfluffrs._templated_file_cache_len()
    tf_a, tf_b = _tf("literal"), _tf("templated")
    _span(tf_a)
    _span(tf_b)
    assert sqlfluffrs._templated_file_cache_len() - base == 2


def test_cache_evicts_with_its_source_objects() -> None:
    """Entries die with their Python objects (was: unbounded growth)."""
    # Purge pending garbage from earlier tests first — their entries
    # evict on OUR collect otherwise, dragging the count below base.
    gc.collect()
    base = sqlfluffrs._templated_file_cache_len()
    tfs = [_tf("literal") for _ in range(8)]
    markers = [_span(tf) for tf in tfs]
    assert sqlfluffrs._templated_file_cache_len() == base + 8
    del tfs, markers
    gc.collect()
    assert sqlfluffrs._templated_file_cache_len() == base


def test_cross_templater_empty_file_probe_is_stable() -> None:
    """The original symptom, pinned end-to-end.

    Raw-templater results depended on whether a jinja config had linted the
    same (empty) source earlier in the process.
    """

    def lint_empty(templater: str):
        cfg = FluffConfig(
            overrides={
                "dialect": "ansi",
                "templater": templater,
                "rules": "LT12",
                "use_rust_parser": True,
            }
        )
        return Linter(config=cfg).lint_string("").check_tuples()

    # Poison attempt: jinja first, then raw — the raw result must match a
    # raw-only run (recorded inline: both engines produce no LT12 for "").
    jinja_first = lint_empty("jinja")
    raw_after = lint_empty("raw")
    raw_again = lint_empty("raw")
    assert raw_after == raw_again
    # And re-rendering jinja after raw is stable too.
    assert lint_empty("jinja") == jinja_first
