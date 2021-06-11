"""Tests specific to the snowflake dialect."""

import hypothesis.strategies as st
from hypothesis import example, given, note, settings

from sqlfluff.core.parser import Parser, Lexer
from sqlfluff.core import FluffConfig


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
    # specfic segment tests if we want to debug logs.
    parsed = Parser(config=config).parse(tokens)
    print(f"Post-parse structure: {parsed.to_tuple(show_raw=True)}")
    print(f"Post-parse structure: {parsed.stringify()}")
    # Check we're all there.
    assert parsed.raw == raw
    # Check that there's nothing un parsable
    typs = parsed.type_set()
    assert "unparsable" not in typs
