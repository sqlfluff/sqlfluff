"""Tests specific to the bigquery dialect."""

import hypothesis.strategies as st
import pytest
from hypothesis import example, given, note, settings

from sqlfluff.core import FluffConfig
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
    raw = f'SELECT * FROM t WHERE {"".join(filter)}'
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
    """Tests BigQuery override of TableReferenceSegment.iter_raw_references().

    The BigQuery implementation is more complex, handling:
    - hyphenated table references
    - quoted or not quoted table references
    """
    query = f"SELECT bar.user_id FROM {table_reference}"
    config = FluffConfig(overrides=dict(dialect="bigquery"))
    tokens, lex_vs = Lexer(config=config).lex(query)
    parsed = Parser(config=config).parse(tokens)
    for table_reference in parsed.recursive_crawl("table_reference"):
        actual_reference_parts = [
            orp.part for orp in table_reference.iter_raw_references()
        ]
        assert reference_parts == actual_reference_parts
