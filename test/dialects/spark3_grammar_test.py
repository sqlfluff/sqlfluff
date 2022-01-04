import logging
from typing import List, Callable, Generator, Any

import pytest

from sqlfluff.core import FluffConfig, dialect_selector
from sqlfluff.core.dialects import Dialect
from sqlfluff.core.parser import Parser, Lexer, RawSegment, OptionallyBracketed
from sqlfluff.core.parser.context import RootParseContext
from ..conftest import (
    compute_parse_tree_hash,
    parse_example_file,
    load_file,
    make_dialect_path,
    get_parse_fixtures,
)


@pytest.fixture(scope="function")
def fresh_spark3_dialect() -> Dialect:
    """Expand the ansi dialect for use."""
    return dialect_selector("spark3")




@pytest.mark.parametrize(
    ["token_list", "matching_segment"],
    [
        ("as t ( col1 , col2 )".split(), "AliasExpressionSegment"),
        ("as t \t ( col1 , col2 )".split(), "AliasExpressionSegment"),
        ("from t".split(), "FromClauseSegment"),
        ("from t as u".split(), "FromClauseSegment"),
        ("from values ( 1 , 2 )".split(), "FromClauseSegment"),
        ("values ( 1 , 2 ) , ( 3 , 4 )".split(), "ValuesClauseSegment"),
        ("values ( 1 , 2 )".split(), "TableExpressionSegment"),
        ("values ( 1 , 2 ) , ( 3 , 4 )".split(), "TableExpressionSegment"),
        ("values ( 1 , 2 )".split(), "FromExpressionElementSegment"),
        ("values ( 1 , 2 ) , ( 3 , 4 )".split(), "FromExpressionElementSegment"),
        ("values ( 1 , 2 ) , ( 3 , 4 )".split(), "FromExpressionSegment"),
        ("from values ( 1 , 2 ) , ( 3 , 4 )".split(), "FromClauseSegment"),
        ("select * from t".split(), "SelectStatementSegment"),
        ("select * from values ( 1 , 2 ) , ( 3 , 4 ) ;".split(), "SelectStatementSegment"),
    ],
)
def test__dialect__spark3__grammars(token_list: List[str], matching_segment:str,
                                         generate_test_segments: Callable[[List[str]], List[RawSegment]],
                                         caplog:Any,
                                         fresh_spark3_dialect: Dialect):
    """Test that some grammars match as expected

    When the fixtured tests fail to parse some particular query, it can be difficult to tell where things went wrong.
    For instance, "values (1, 2)" is a `ValuesClauseSegment` but also a `TableExpressionSegment`. If this fails to be
    recognized, is it because `ValuesClauseSegment` is wrong, or because a `ValuesClauseSegment` is not recognized as
    a `TableExpressionSegment`?

    This test can help us diagnose that, since we pick both the sequence of segments _and_ the grammar we think it
    should match.
    """
    seg_list = generate_test_segments(token_list)
    g = fresh_spark3_dialect._library[matching_segment].match_grammar
    maybe_bracketed_g = OptionallyBracketed(g)
    with RootParseContext(dialect=fresh_spark3_dialect) as ctx:
        with caplog.at_level(logging.DEBUG, logger="sqlfluff.parser"):
            # Matching with whitespace shouldn't match if we need at least one delimiter
            m = g.match(seg_list, parse_context=ctx)
            assert not m.unmatched_segments

            mb = maybe_bracketed_g.match(seg_list, parse_context=ctx)
            assert not mb.unmatched_segments
