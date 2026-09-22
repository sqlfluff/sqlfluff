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
            "CREATE TABLE t FLOW INSERT BY NAME SELECT * FROM STREAM s;",
            id="flow_without_streaming",
        ),
        pytest.param(
            "CREATE PRIVATE TABLE t FLOW INSERT BY NAME SELECT * FROM STREAM s;",
            id="flow_with_private_without_streaming",
        ),
    ],
)
def test_inline_flow_requires_streaming_and_a_bound_spec(sql: str) -> None:
    """An inline FLOW is only valid on a streaming table, and its spec binds.

    `REPLACE USING (...)` and `SEQUENCE BY` are required together, and the
    append form takes `BY NAME`. These are the boundaries #8509 missed for the
    standalone statement, so they are asserted here rather than left to the
    fixture, which cannot express a rejection.
    """
    assert _violations(sql), f"Expected violations but got none for:\n{sql}"
