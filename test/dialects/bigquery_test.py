"""Tests specific to the bigquery dialect."""

import hypothesis.strategies as st
import pytest
from hypothesis import example, given, note, settings

from sqlfluff.core import FluffConfig, Linter
from sqlfluff.core.dialects.common import (
    get_from_clause_aliases,
    iter_raw_references,
)
from sqlfluff.core.parser import Lexer, Parser


@settings(max_examples=100, deadline=None)
@given(
    st.lists(
        st.tuples(st.sampled_from(["<", "=", ">"]), st.sampled_from(["AND", "OR"])),
        min_size=1,
        max_size=30,
    )
)
@example(data=[("<", "AND")])
@example(data=[(">", "AND")])
@example(data=[("<", "AND"), (">", "AND")])
@example(data=[("<", "AND"), ("=", "AND"), (">", "AND")])
@example(data=[(">", "AND"), ("<", "AND")])
@example(data=[("<", "AND"), ("<", "AND"), (">", "AND")])
@example(data=[(">", "AND"), (">", "AND"), ("<", "AND")])
def test_bigquery_relational_operator_parsing(data):
    """Tests queries with a diverse mixture of relational operators."""
    # Generate a simple SELECT query with relational operators and conjunctions
    # as specified in 'data'. Note the conjunctions are used as separators
    # between comparisons, sn the conjunction in the first item is not used.
    filter = []
    for i, (relation, conjunction) in enumerate(data):
        if i:
            filter.append(f" {conjunction} ")
        filter.append(f"a {relation} b")
    raw = f"SELECT * FROM t WHERE {''.join(filter)}"
    note(f"query: {raw}")
    # Load the right dialect
    config = FluffConfig(overrides=dict(dialect="bigquery"))
    tokens, lex_vs = Lexer(config=config).lex(raw)
    # From just the initial parse, check we're all there
    assert "".join(token.raw for token in tokens) == raw
    # Check we don't have lexing issues
    assert not lex_vs

    # Do the parse WITHOUT lots of logging
    # The logs get too long here to be useful. We should use
    # specific segment tests if we want to debug logs.
    parsed = Parser(config=config).parse(tokens)
    print(f"Post-parse structure: {parsed.to_tuple(show_raw=True)}")
    print(f"Post-parse structure: {parsed.stringify()}")
    # Check we're all there.
    assert parsed.raw == raw
    # Check that there's nothing un parsable
    typs = parsed.type_set()
    assert "unparsable" not in typs


@pytest.mark.parametrize(
    "table_reference, reference_parts",
    [
        (
            "bigquery-public-data.pypi.file_downloads",
            ["bigquery-public-data", "pypi", "file_downloads"],
        ),
        (
            "`bigquery-public-data.pypi.file_downloads`",
            ["bigquery-public-data", "pypi", "file_downloads"],
        ),
        ("foo.far.bar", ["foo", "far", "bar"]),
        ("`foo.far.bar`", ["foo", "far", "bar"]),
        ("a-b.c-d.e-f", ["a-b", "c-d", "e-f"]),
    ],
)
def test_bigquery_table_reference_segment_iter_raw_references(
    table_reference, reference_parts
):
    """Tests BigQuery handling of iter_raw_references() for table references.

    The BigQuery implementation is more complex, handling:
    - hyphenated table references
    - quoted or not quoted table references

    Exercises both the new free function (the recommended API) and the
    deprecated ``TableReferenceSegment.iter_raw_references()`` wrapper, which
    must still return the same result and emit a ``DeprecationWarning``.
    """
    query = f"SELECT bar.user_id FROM {table_reference}"
    config = FluffConfig(overrides=dict(dialect="bigquery"))
    tokens, lex_vs = Lexer(config=config).lex(query)
    parsed = Parser(config=config).parse(tokens)
    for table_reference in parsed.recursive_crawl("table_reference"):
        # Recommended API: the free function.
        actual_reference_parts = [
            orp.part for orp in iter_raw_references(table_reference, "bigquery")
        ]
        assert reference_parts == actual_reference_parts
        # Deprecated wrapper: still works, but warns.
        with pytest.warns(DeprecationWarning):
            deprecated_parts = [
                orp.part for orp in table_reference.iter_raw_references()
            ]
        assert reference_parts == deprecated_parts


@pytest.mark.parametrize(
    "from_clause, expected_ref_str",
    [
        # Unaliased, hyphenated, multi-part table name. The eventual alias is
        # the final part, which requires BigQuery's hyphen-aware handling
        # ("tbl-name", not "name").
        ("project.dataset.tbl-name", "tbl-name"),
        # Quoted multi-part name.
        ("`bigquery-public-data.pypi.file_downloads`", "file_downloads"),
        # Explicit alias is returned verbatim.
        ("foo.bar AS baz", "baz"),
    ],
)
def test_bigquery_from_clause_get_eventual_aliases_back_compat(
    from_clause, expected_ref_str
):
    """Back-compat for ``FromClauseSegment.get_eventual_aliases()`` on BigQuery.

    This is a behavior-parity check: the deprecated wrapper and the replacement
    free function ``get_from_clause_aliases`` must agree, and both must match
    the legacy (pre-refactor) implementation. It guards the back-compat path
    (``dialect_name=None``), which must dispatch via the segment's own class so
    the legacy behavior is unchanged.
    """
    query = f"SELECT 1 FROM {from_clause}"
    config = FluffConfig(overrides=dict(dialect="bigquery"))
    tokens, _ = Lexer(config=config).lex(query)
    parsed = Parser(config=config).parse(tokens)
    fc = next(parsed.recursive_crawl("from_clause"))

    # Recommended API: the free function with an explicit dialect.
    free_aliases = get_from_clause_aliases(fc, "bigquery")
    assert free_aliases[0][1].ref_str == expected_ref_str

    # Segment method must agree with the free function (and the legacy impl).
    wrapper_aliases = fc.get_eventual_aliases()
    assert wrapper_aliases[0][1].ref_str == expected_ref_str


def test_cast_as_float_fails():
    """CAST(... AS FLOAT) should fail for BigQuery (only FLOAT64 allowed)."""
    sql = "SELECT CAST('4.0' AS FLOAT)"
    parsed = Linter(dialect="bigquery").parse_string(sql)
    # Parsing produces a parse error for the unsupported `FLOAT` type.
    assert parsed.violations
