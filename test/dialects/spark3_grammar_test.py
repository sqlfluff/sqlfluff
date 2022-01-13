"""Test some specific spark3 grammars."""
import logging
from typing import List, Callable, Any

import pytest

from sqlfluff.core import FluffConfig, dialect_selector
from sqlfluff.core.dialects import Dialect
from sqlfluff.core.parser import Lexer, RawSegment
from sqlfluff.core.parser.context import RootParseContext


@pytest.fixture(scope="function")
def fresh_spark3_dialect() -> Dialect:
    """Expand the spark3 dialect for use."""
    return dialect_selector("spark3")


def lex_segments(fragment: str):
    """For given test examples, check successful parsing."""
    config = FluffConfig(overrides=dict(dialect="spark3"))
    tokens, lex_vs = Lexer(config=config).lex(fragment)
    # From just the initial parse, check we're all there
    assert "".join(token.raw for token in tokens) == fragment
    # Check we don't have lexing issues
    assert not lex_vs
    return tokens


@pytest.mark.parametrize(
    ["segment_class", "match_or_parse", "fragment"],
    [
        (t[1], b, t[0])
        for t in [
            ("as t ( col1 , col2 )", "AliasExpressionSegment"),
            ("as t \t ( col1 , col2 )", "AliasExpressionSegment"),
            ("from t", "FromClauseSegment"),
            ("from t as u", "FromClauseSegment"),
            ("from values ( 1 , 2 )", "FromClauseSegment"),
            ("from values 1", "FromClauseSegment"),
            ("from values 1 , 2 ", "FromClauseSegment"),
            ("1 , 2 , 3", "DelimitedValues"),
            ("values 1 , 2 , 3", "ValuesClauseSegment"),
            ("values ( 1 , 2 , 3 )", "ValuesClauseSegment"),
            ("values ( 1 , 2 ) , ( 3 , 4 )", "ValuesClauseSegment"),
            ("values ( 1 , 2 )", "TableExpressionSegment"),
            ("values ( 1 , 2 ) , ( 3 , 4 )", "TableExpressionSegment"),
            ("values ( 1 , 2 )", "FromExpressionElementSegment"),
            ("values ( 1 , 2 ) , ( 3 , 4 )", "FromExpressionElementSegment"),
            ("values ( 1 , 2 ) , ( 3 , 4 )", "FromExpressionSegment"),
            ("from values ( 1 , 2 )", "FromClauseSegment"),
            ("from values 1 , 2", "FromClauseSegment"),
            ("from values ( 1 , 2 ) , ( 3 , 4 )", "FromClauseSegment"),
            ("select * from t", "SelectStatementSegment"),
            ("select * from values ( 1 , 2 ) , ( 3 , 4 ) ;", "SelectStatementSegment"),
        ]
        for b in ["match", "parse"]
    ],
)
def test__dialect__spark3__grammars(
    segment_class: str,
    match_or_parse: str,
    fragment: str,
    generate_test_segments: Callable[[List[str]], List[RawSegment]],
    fresh_spark3_dialect: Dialect,
    caplog: Any,
):
    """Test that some grammars match as expected.

    When the fixtured tests fail to parse some particular query, it can be difficult to tell where things went wrong.
    For instance, "values (1, 2)" is a `ValuesClauseSegment` but also a `TableExpressionSegment`. If this fails to be
    recognized, is it because `ValuesClauseSegment` is wrong, or because a `ValuesClauseSegment` is not recognized as
    a `TableExpressionSegment`?

    This test can help us diagnose that, since we pick both the sequence of segments _and_ the grammar we think it
    should match.
    """
    lexed_seg_list = lex_segments(fragment)
    segment = fresh_spark3_dialect._library[segment_class]
    grammar = (
        segment.parse_grammar
        if (match_or_parse == "parse" and segment.parse_grammar)
        else segment.match_grammar
    )

    with RootParseContext(dialect=fresh_spark3_dialect) as ctx:
        ctx.logger.setLevel(logging.DEBUG)
        with caplog.at_level(logging.DEBUG):
            p = grammar.match(lexed_seg_list, parse_context=ctx)

    if p.unmatched_segments:
        logger = logging.getLogger()
        logger.addHandler(logging.StreamHandler())
        for _, _, message in caplog.record_tuples:
            logger.warning(message)

    assert not p.unmatched_segments
