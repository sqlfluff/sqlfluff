"""Tests for the reference/alias helpers in sqlfluff.core.dialects.common.

These helpers were extracted from methods on the dialect segment classes so
that they can dispatch on the dialect name + segment type (a prerequisite for
porting the rules that use them to Rust). The original segment methods are
retained as deprecated thin wrappers, which must:

1. emit a ``DeprecationWarning``, and
2. return exactly the same result as the replacement free function.

This module exercises every wrapper against its free function so the back-compat
surface stays covered and correct.
"""

import pytest

from sqlfluff.core.dialects.common import (
    ObjectReferenceLevel,
    extract_possible_multipart_references,
    extract_possible_references,
    get_from_clause_aliases,
    get_from_expression_element_alias,
    get_join_clause_aliases,
    is_qualified,
    iter_raw_references,
    qualification,
)
from sqlfluff.core.linter.linter import Linter


def _parse(sql: str, dialect: str = "ansi"):
    """Parse a SQL string and return its (fully parsable) root segment."""
    parsed = Linter(dialect=dialect).parse_string(sql)
    assert "unparsable" not in parsed.tree.descendant_type_set
    return parsed.tree


def _first(tree, seg_type):
    """Return the first descendant segment of the given type."""
    return next(tree.recursive_crawl(seg_type))


@pytest.mark.parametrize("dialect", ["ansi", "bigquery"])
def test_iter_raw_references_wrapper_matches_free_function(dialect):
    """``<ref>.iter_raw_references()`` warns and matches the free function.

    Covers the ANSI base, the BigQuery splittable-column and table overrides.
    """
    tree = _parse("SELECT a.b.c FROM x.y.z", dialect=dialect)
    for seg_type in ("column_reference", "table_reference"):
        ref = _first(tree, seg_type)
        expected = list(iter_raw_references(ref, dialect))
        with pytest.warns(DeprecationWarning):
            got = list(ref.iter_raw_references())
        assert got == expected


def test_wildcard_iter_raw_references_wrapper():
    """``WildcardIdentifierSegment.iter_raw_references()`` warns and matches."""
    tree = _parse("SELECT my_table.* FROM my_table")
    ref = _first(tree, "wildcard_identifier")
    expected = list(iter_raw_references(ref, "ansi"))
    with pytest.warns(DeprecationWarning):
        got = list(ref.iter_raw_references())
    assert got == expected


def test_is_qualified_and_qualification_wrappers():
    """``is_qualified()`` / ``qualification()`` warn and match the free funcs."""
    tree = _parse("SELECT a.b FROM t")
    ref = _first(tree, "column_reference")
    with pytest.warns(DeprecationWarning):
        assert ref.is_qualified() == is_qualified(ref, "ansi")
    with pytest.warns(DeprecationWarning):
        assert ref.qualification() == qualification(ref, "ansi")


@pytest.mark.parametrize("dialect", ["ansi", "bigquery"])
def test_extract_possible_references_wrapper(dialect):
    """``extract_possible_references()`` warns and matches the free function.

    Covers the ANSI base and the BigQuery column override.
    """
    ref = _first(_parse("SELECT s.t.c FROM s.t", dialect=dialect), "column_reference")
    expected = extract_possible_references(
        ref, level=ObjectReferenceLevel.TABLE, dialect_name=dialect
    )
    with pytest.warns(DeprecationWarning):
        got = ref.extract_possible_references(level=ObjectReferenceLevel.TABLE)
    assert got == expected


@pytest.mark.parametrize(
    "dialect, sql, seg_type",
    [
        # ANSI base: a 3-part table reference yields a schema.table pair.
        ("ansi", "SELECT c FROM d.s.t", "table_reference"),
        # BigQuery column override: schema-level multipart from a 3-part column.
        ("bigquery", "SELECT a.b.c FROM t", "column_reference"),
    ],
)
def test_extract_possible_multipart_references_wrapper(dialect, sql, seg_type):
    """``extract_possible_multipart_references()`` warns and matches."""
    ref = _first(_parse(sql, dialect=dialect), seg_type)
    levels = [ObjectReferenceLevel.SCHEMA, ObjectReferenceLevel.TABLE]
    expected = extract_possible_multipart_references(
        ref, levels=levels, dialect_name=dialect
    )
    with pytest.warns(DeprecationWarning):
        got = ref.extract_possible_multipart_references(levels=levels)
    assert got == expected


def test_eventual_alias_wrappers():
    """The ``get_eventual_alias(es)`` wrappers warn and match the free funcs."""
    tree = _parse("SELECT 1 FROM t AS a JOIN u AS b ON a.x = b.y")

    fee = _first(tree, "from_expression_element")
    with pytest.warns(DeprecationWarning):
        got_elem = list(fee.get_eventual_alias())
    assert got_elem == list(get_from_expression_element_alias(fee, "ansi"))

    jc = _first(tree, "join_clause")
    with pytest.warns(DeprecationWarning):
        got_join = jc.get_eventual_aliases()
    assert got_join == get_join_clause_aliases(jc, "ansi")

    fc = _first(tree, "from_clause")
    with pytest.warns(DeprecationWarning):
        got_from = fc.get_eventual_aliases()
    assert got_from == get_from_clause_aliases(fc, "ansi")
