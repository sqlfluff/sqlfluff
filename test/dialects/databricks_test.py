"""Databricks dialect-specific parser rejection tests."""

import pytest

from sqlfluff.core import Linter


def _violations(sql: str) -> list:
    """Return all parse errors, including unparsable nodes in the tree."""
    parsed = Linter(dialect="databricks").parse_string(sql)
    violations: list = list(parsed.violations)
    if parsed.tree:
        violations += list(parsed.tree.recursive_crawl("unparsable"))
    return violations


@pytest.mark.parametrize(
    "sql",
    [
        pytest.param(
            """CREATE MATERIALIZED VIEW bad_mv (
                CONSTRAINT c EXPECT (value > 0),
                value INT
            ) AS SELECT 1 AS value;""",
            id="expectation_before_column",
        ),
        pytest.param(
            """CREATE MATERIALIZED VIEW bad_mv (
                value INT,
                CONSTRAINT pk PRIMARY KEY (value),
                CONSTRAINT c EXPECT (value > 0)
            ) AS SELECT 1 AS value;""",
            id="expectation_after_table_constraint",
        ),
    ],
)
def test_materialized_view_constraints_reject_invalid_order(sql: str) -> None:
    """Materialized view constraints must follow columns and expectations."""
    assert _violations(sql), f"Expected violations but got none for:\n{sql}"


@pytest.mark.parametrize(
    "sql",
    [
        pytest.param(
            "CREATE PRIVATE TABLE t (a INT);",
            id="private_without_streaming",
        ),
        pytest.param(
            "CREATE OR REFRESH PRIVATE TABLE t (a INT);",
            id="private_refresh_without_streaming",
        ),
        pytest.param(
            "CREATE PRIVATE LIVE TABLE t (a INT);",
            id="private_live_without_streaming",
        ),
    ],
)
def test_private_requires_streaming_table(sql: str) -> None:
    """PRIVATE is only valid on a streaming table, not on a table."""
    assert _violations(sql), f"Expected violations but got none for:\n{sql}"


@pytest.mark.parametrize(
    "sql",
    [
        pytest.param("SELECT * FROM t OFFSET;", id="offset_without_expression"),
        pytest.param(
            "SELECT * FROM test TABLESAMPLE ();", id="tablesample_without_sample"
        ),
        pytest.param(
            "SELECT * FROM test TABLESAMPLE (30 PERCENT) REPEATABLE ();",
            id="repeatable_without_seed",
        ),
        pytest.param(
            "SELECT * FROM t MATCH_RECOGNIZE (DEFINE a AS TRUE);",
            id="match_recognize_without_pattern",
        ),
        pytest.param("SELECT * FROM t WITH();", id="table_options_empty"),
        pytest.param(
            "WITH RECURSIVE r(n) MAX RECURSION LEVEL AS (VALUES (1)) SELECT * FROM r;",
            id="cte_recursion_without_level",
        ),
    ],
)
def test_query_surface_rejections(sql: str) -> None:
    """Query-surface boundaries: OFFSET, sampling, MATCH_RECOGNIZE, and WITH."""
    assert _violations(sql), f"Expected violations but got none for:\n{sql}"
