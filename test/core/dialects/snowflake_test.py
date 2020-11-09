"""Tests specific to the ansi dialect."""

import pytest
import logging

from sqlfluff.core import FluffConfig, Linter
from sqlfluff.core.parser import (
    Lexer,
    BaseSegment,
    RawSegment,
)
from sqlfluff.core.parser.context import RootParseContext
from sqlfluff.core.parser.match_result import MatchResult
from sqlfluff.core.dialects import snowflake_dialect
from sqlfluff.core.dialects.dialect_snowflake import UseStatementSegment


@pytest.mark.parametrize(
    "segment_cls,raw",
    [
        (UseStatementSegment, 'USE ROLE "MY_ROLE";'),
        (UseStatementSegment, 'USE WAREHOUSE "MY_WAREHOUSE";'),
        (UseStatementSegment, 'USE DATABASE "MY_DATABASE";'),
        (UseStatementSegment, 'USE "MY_DATABASE";'),
        (UseStatementSegment, 'USE SCHEMA "MY_DATABASE"."MY_SCHEMA";'),
        (UseStatementSegment, 'USE SCHEMA "MY_SCHEMA";'),
        (UseStatementSegment, 'USE "MY_DATABASE"."MY_SCHEMA";'),
    ],
)
def test_snowflake_queries(segment_cls, raw, caplog):
    """Test queries parse"""
    lnt = Linter(dialect="snowflake")
    parsed, vs, _ = lnt.parse_string(raw)
    assert len(vs) == 0

    ## Find any unparsable statements
    typs = parsed.type_set()
    assert "unparsable" not in typs

    ## Find the expected type in the parsed segment
    child_segments = [seg for seg in parsed.recursive_crawl(segment_cls.type)]
    assert len(child_segments) > 0
    ## If we get here the raw statement was parsed as expected
