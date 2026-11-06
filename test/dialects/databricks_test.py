"""Databricks dialect-specific parser rejection tests."""

import pytest

from sqlfluff.core import Linter


@pytest.mark.parametrize("line_ending", ["\n", "\r\n"], ids=["lf", "crlf"])
@pytest.mark.parametrize(
    "magic_lines",
    [
        pytest.param(
            ["-- MAGIC %md", "-- MAGIC Some notebook prose"],
            id="magic_start_and_line",
        ),
        pytest.param(
            ["-- MAGIC %md # Title", "-- MAGIC", "-- MAGIC More prose"],
            id="single_line_directive_and_empty_line",
        ),
    ],
)
def test_magic_lines_do_not_trigger_lt01(
    line_ending: str, magic_lines: list[str]
) -> None:
    """Notebook magic lines remain separated for layout linting."""
    sql = line_ending.join(
        [
            "-- Databricks notebook source",
            *magic_lines,
            "",
            "-- COMMAND ----------",
            "",
            "SELECT 1;",
        ]
    )
    violations = Linter(dialect="databricks", rules=["LT01"]).lint_string(sql)
    assert not violations.violations


@pytest.mark.parametrize(
    "command",
    ["%tensorboard --logdir logs", "%%profile", "%uv pip install pandas"],
)
@pytest.mark.parametrize("line_ending", ["\n", "\r\n"], ids=["lf", "crlf"])
@pytest.mark.parametrize("first_cell", [True, False], ids=["first", "later"])
def test_bare_magic_commands_parse(
    command: str, line_ending: str, first_cell: bool
) -> None:
    """The shared bare magic pattern works at both cell positions."""
    notebook = "-- Databricks notebook source" + line_ending
    if not first_cell:
        notebook += line_ending.join(
            [
                "",
                "-- COMMAND ----------",
                "",
                "SELECT 1",
                "",
                "-- COMMAND ----------",
                "",
            ]
        )
    parsed = Linter(dialect="databricks").parse_string(notebook + command + line_ending)
    assert parsed.tree
    assert not parsed.violations
    assert not list(parsed.tree.recursive_crawl("unparsable"))


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
