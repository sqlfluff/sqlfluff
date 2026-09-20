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
            "-- Databricks notebook source\n"
            "-- MAGIC %md\n"
            "-- MAGIC Some prose quoting a command:\n"
            "-- MAGIC %fs ls /tmp/data \n"
            "\n"
            "-- COMMAND ----------\n"
            "\n"
            "SELECT a FROM b;",
            id="magic_line_with_trailing_space",
        ),
        pytest.param(
            "-- Databricks notebook source\n"
            "-- MAGIC %md\n"
            "-- MAGIC Some prose.\n"
            "-- MAGIC %fs\n"
            "\n"
            "-- COMMAND ----------\n"
            "\n"
            "SELECT a FROM b;",
            id="standalone_directive_ends_the_cell",
        ),
    ],
)
def test_magic_cell_boundaries(sql: str) -> None:
    """A magic cell ends at its separator, not at a directive-shaped line.

    A `-- MAGIC` body line may carry a trailing space, and a cell may end with
    a standalone directive; neither may swallow the blank line the command
    separator needs. These are whitespace-sensitive boundaries a `.sql` fixture
    cannot express, because trailing whitespace is stripped from fixtures.
    """
    assert not _violations(sql), f"Expected a clean parse for:\n{sql}"


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
