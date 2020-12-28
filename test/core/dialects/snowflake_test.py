"""Tests specific to the snowflake dialect."""

import pytest

from sqlfluff.core import Linter
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
    """Test snowflake specific queries parse."""
    lnt = Linter(dialect="snowflake")
    parsed = lnt.parse_string(raw)
    assert len(parsed.violations) == 0

    # Find any unparsable statements
    typs = parsed.tree.type_set()
    assert "unparsable" not in typs

    # Find the expected type in the parsed segment
    child_segments = [seg for seg in parsed.tree.recursive_crawl(segment_cls.type)]
    assert len(child_segments) > 0
    # If we get here the raw statement was parsed as expected
