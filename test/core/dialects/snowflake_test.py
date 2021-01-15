"""Tests specific to the snowflake dialect."""

import pytest

from sqlfluff.core import Linter
from sqlfluff.core.dialects.dialect_snowflake import (
    UseStatementSegment,
    SemiStructuredAccessorSegment,
    CreateStatementSegment,
    CreateCloneStatementSegment,
    ShowStatementSegment,
)


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
        (CreateStatementSegment, "CREATE ROLE MY_ROLE;"),
        (CreateStatementSegment, 'CREATE ROLE "my_role";'),
        (CreateStatementSegment, "CREATE DATABASE MY_DATABASE;"),
        (CreateStatementSegment, "CREATE DATABASE IF NOT EXISTS MY_DATABASE;"),
        (
            CreateCloneStatementSegment,
            "create schema mytestschema_clone_restore clone testschema;",
        ),
        (
            CreateCloneStatementSegment,
            "create schema mytestschema_clone_restore clone testschema before (timestamp => to_timestamp(40*365*86400));",
        ),
        (
            CreateCloneStatementSegment,
            "create table orders_clone_restore clone orders at (timestamp => to_timestamp_tz('04/05/2013 01:02:03', 'mm/dd/yyyy hh24:mi:ss'));",
        ),
        (ShowStatementSegment, "SHOW GRANTS ON ACCOUNT;"),
        (ShowStatementSegment, "show tables history in tpch.public;"),
        (ShowStatementSegment, "show future grants in schema sales.public;"),
        # Testing https://github.com/sqlfluff/sqlfluff/issues/634
        (
            SemiStructuredAccessorSegment,
            "SELECT ID :: VARCHAR as id, OBJ : userId :: VARCHAR as user_id from x",
        ),
    ],
)
def test_snowflake_queries(segment_cls, raw, caplog):
    """Test snowflake specific queries parse."""
    lnt = Linter(dialect="snowflake")
    parsed = lnt.parse_string(raw)
    print(parsed.violations)
    assert len(parsed.violations) == 0

    # Find any unparsable statements
    typs = parsed.tree.type_set()
    assert "unparsable" not in typs

    # Find the expected type in the parsed segment
    child_segments = [seg for seg in parsed.tree.recursive_crawl(segment_cls.type)]
    assert len(child_segments) > 0
    # If we get here the raw statement was parsed as expected
