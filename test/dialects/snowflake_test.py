"""Tests specific to the snowflake dialect."""

import pytest

from sqlfluff.core import Linter
from sqlfluff.core.dialects import dialect_selector


# Deprecated: All new tests should be added as .sql and .yml files under
# `test/fixtures/dialects/snowflake`.
# See test/fixtures/dialects/README.md for more details.
@pytest.mark.parametrize(
    "segment_cls,raw",
    [
        (
            "CreateCloneStatementSegment",
            "create table orders_clone_restore clone orders at (timestamp => "
            "to_timestamp_tz('04/05/2013 01:02:03', 'mm/dd/yyyy hh24:mi:ss'));",
        ),
        ("ShowStatementSegment", "SHOW GRANTS ON ACCOUNT;"),
        ("ShowStatementSegment", "show tables history in tpch.public;"),
        ("ShowStatementSegment", "show future grants in schema sales.public;"),
        (
            "ShowStatementSegment",
            "show replication databases with primary aws_us_west_2.myaccount1.mydb1;",
        ),
        (
            "ShowStatementSegment",
            "SHOW TERSE SCHEMAS HISTORY LIKE '%META%' IN DATABASE MYDB STARTS WITH "
            "'INT' LIMIT 10 FROM 'LAST_SCHEMA';",
        ),
        ("ShowStatementSegment", "SHOW GRANTS TO ROLE SECURITYADMIN;"),
        ("ShowStatementSegment", "SHOW GRANTS OF SHARE MY_SHARE;"),
        # Testing https://github.com/sqlfluff/sqlfluff/issues/634
        (
            "SemiStructuredAccessorSegment",
            "SELECT ID :: VARCHAR as id, OBJ : userId :: VARCHAR as user_id from x",
        ),
        ("DropUserStatementSegment", "DROP USER my_user;"),
        ("AlterSessionStatementSegment", "ALTER SESSION SET TIMEZONE = 'UTC'"),
        (
            "AlterSessionStatementSegment",
            "ALTER SESSION SET ABORT_DETACHED_QUERY = FALSE",
        ),
        ("AlterSessionStatementSegment", "ALTER SESSION SET JSON_INDENT = 5"),
        (
            "AlterSessionStatementSegment",
            "ALTER SESSION UNSET ERROR_ON_NONDETERMINISTIC_MERGE;",
        ),
        (
            "AlterSessionStatementSegment",
            "ALTER SESSION UNSET TIME_OUTPUT_FORMAT, TWO_DIGIT_CENTURY_START;",
        ),
    ],
)
def test_snowflake_queries(segment_cls, raw, caplog):
    """Test snowflake specific queries parse."""
    lnt = Linter(dialect="snowflake")
    parsed = lnt.parse_string(raw)
    print(parsed.violations())
    assert len(parsed.violations()) == 0
    tree = parsed.root_variant().tree

    # Find any unparsable statements
    typs = tree.type_set()
    assert "unparsable" not in typs

    # Find the expected type in the parsed segment
    seg_type = dialect_selector("snowflake").get_segment(segment_cls).type
    child_segments = [seg for seg in tree.recursive_crawl(seg_type)]
    assert len(child_segments) > 0
    # If we get here the raw statement was parsed as expected
