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
        pytest.param(
            "CREATE OR REFRESH STREAMING TABLE t FLOW INSERT SELECT * FROM STREAM s;",
            id="flow_insert_without_by_name",
        ),
        pytest.param(
            "CREATE OR REFRESH STREAMING TABLE t "
            "FLOW REPLACE USING (c) BY NAME SELECT * FROM STREAM s;",
            id="flow_replace_using_without_sequence_by",
        ),
        pytest.param(
            "CREATE OR REFRESH STREAMING TABLE t "
            "FLOW REPLACE USING (c) SEQUENCE BY d SELECT * FROM STREAM s;",
            id="flow_replace_using_without_by_name",
        ),
        pytest.param(
            "CREATE OR REFRESH STREAMING TABLE t "
            "FLOW SEQUENCE BY d BY NAME SELECT * FROM STREAM s;",
            id="flow_sequence_by_without_replace_using",
        ),
        pytest.param(
            "CREATE PRIVATE TABLE t FLOW INSERT BY NAME SELECT * FROM STREAM s;",
            id="flow_with_private_without_streaming",
        ),
        pytest.param(
            "CREATE TABLE t FLOW INSERT BY NAME;",
            id="table_flow_without_query",
        ),
    ],
)
def test_inline_flow_spec_binds(sql: str) -> None:
    """An inline FLOW's spec binds, and PRIVATE still requires STREAMING.

    `REPLACE USING (...)` and `SEQUENCE BY` are required together, and the
    append form takes `BY NAME`. These are the boundaries #8509 missed for the
    standalone statement, so they are asserted here rather than left to the
    fixture, which cannot express a rejection.
    """
    assert _violations(sql), f"Expected violations but got none for:\n{sql}"


@pytest.mark.parametrize(
    "sql",
    [
        pytest.param(
            "CREATE FLOW append_flow AS INSERT INTO target BY NAME "
            "REPLACE USING (event_date) SELECT * FROM STREAM source;",
            id="replace_using_without_sequence_by",
        ),
        pytest.param(
            "CREATE FLOW append_flow AS INSERT INTO target BY NAME "
            "SEQUENCE BY event_date SELECT * FROM STREAM source;",
            id="sequence_by_without_replace_using",
        ),
    ],
)
def test_replace_using_spec_binds_sequence_by(sql: str) -> None:
    """`REPLACE USING (...)` and `SEQUENCE BY` are required together."""
    assert _violations(sql), f"Expected violations but got none for:\n{sql}"


@pytest.mark.parametrize(
    "sql",
    [
        pytest.param(
            "INSERT INTO t REPLACE ON SELECT a FROM s;",
            id="insert_replace_on_without_expression",
        ),
        pytest.param("RESTORE TABLE employee;", id="restore_without_version"),
        pytest.param("RESTORE TABLE employee TO;", id="restore_without_time_travel"),
        pytest.param(
            "RESTORE TABLE employee TO TIMESTAMP AS OF;",
            id="restore_timestamp_without_expression",
        ),
        pytest.param("RESTORE TO VERSION AS OF 1;", id="restore_without_table_name"),
    ],
)
def test_insert_and_restore_rejections(sql: str) -> None:
    """INSERT/REPLACE ON and RESTORE boundaries."""
    assert _violations(sql), f"Expected violations but got none for:\n{sql}"
