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
            "CREATE PRIVATE TABLE t (a BIGINT);",
            id="private_without_streaming",
        ),
        pytest.param(
            "CREATE OR REFRESH PRIVATE TABLE t (a BIGINT);",
            id="private_refresh_without_streaming",
        ),
        pytest.param(
            "CREATE PRIVATE LIVE TABLE t (a BIGINT);",
            id="private_live_without_streaming",
        ),
    ],
)
def test_private_requires_a_streaming_table(sql: str) -> None:
    """`PRIVATE` qualifies a streaming table, so it cannot stand on its own.

    https://docs.databricks.com/aws/en/ldp/developer/ldp-sql-ref-create-streaming-table
    """
    assert _violations(sql), f"Expected violations but got none for:\n{sql}"


@pytest.mark.parametrize(
    "sql",
    [
        pytest.param(
            "CREATE FLOW f AS INSERT ONCE INTO ONCE t BY NAME SELECT * FROM src;",
            id="once_given_twice",
        ),
        pytest.param(
            "CREATE FLOW f AS INSERT INTO t SELECT * FROM src;",
            id="append_flow_without_by_name",
        ),
        pytest.param(
            "CREATE FLOW f INSERT INTO t BY NAME SELECT * FROM src;",
            id="append_flow_without_as",
        ),
    ],
)
def test_create_flow_rejects_invalid_append_flows(sql: str) -> None:
    """An append flow needs `AS`, `BY NAME`, and at most one `ONCE`.

    https://docs.databricks.com/aws/en/ldp/developer/ldp-sql-ref-create-flow
    """
    assert _violations(sql), f"Expected violations but got none for:\n{sql}"
