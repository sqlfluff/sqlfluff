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


@pytest.mark.parametrize(
    "sql",
    [
        pytest.param(
            "CREATE FLOW f AS INSERT INTO t BY NAME "
            "REPLACE USING (a) SELECT * FROM STREAM s;",
            id="replace_using_without_sequence_by",
        ),
    ],
)
def test_replace_using_requires_sequence_by(sql: str) -> None:
    """replace_using_spec is REPLACE USING (...) SEQUENCE BY col, as documented."""
    assert _violations(sql), f"Expected violations but got none for:\n{sql}"


@pytest.mark.parametrize(
    "sql",
    [
        pytest.param("CREATE OR REFRESH VIEW v AS SELECT 1;\n", id="plain_view"),
        pytest.param("CREATE OR REFRESH LIVE VIEW v AS SELECT 1;\n", id="live_view"),
        pytest.param(
            "CREATE OR REFRESH TEMPORARY STREAMING LIVE VIEW v AS SELECT 1;\n",
            id="streaming_live_view",
        ),
    ],
)
def test_or_refresh_is_not_a_view_clause(sql: str) -> None:
    """OR REFRESH belongs to streaming tables and materialized views.

    The corpus of published Databricks SQL uses it with MATERIALIZED VIEW,
    STREAMING TABLE and LIVE TABLE, and with no VIEW form at all. Both of
    those statements have their own segments here, so CREATE VIEW does not
    need it.
    """
    assert _violations(sql), f"Expected a parse failure for:\n{sql}"


@pytest.mark.parametrize(
    "sql",
    [
        pytest.param(
            "CREATE TEMPORARY VIEW v USING;\n",
            id="using_without_data_source",
        ),
        pytest.param(
            "CREATE VIEW v USING csv OPTIONS (path '/data');\n",
            id="using_without_temporary",
        ),
        pytest.param(
            "CREATE TEMPORARY VIEW v USING csv OPTIONS ();\n",
            id="empty_options",
        ),
        pytest.param(
            "CREATE TEMPORARY VIEW v USING csv OPTIONS (path);\n",
            id="options_without_value",
        ),
        pytest.param(
            "CREATE VIEW v WITH AS SELECT a FROM t;\n",
            id="with_without_clause",
        ),
    ],
)
def test_view_requires_bound_clauses(sql: str) -> None:
    """The data-source production and the with_clause bind their tokens.

    `USING` needs a data source, the data-source production is only for a
    TEMPORARY view, `OPTIONS` needs at least one name-value pair, and `WITH`
    needs a clause.
    """
    assert _violations(sql), f"Expected violations but got none for:\n{sql}"
