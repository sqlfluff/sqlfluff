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
        pytest.param("DROP CONNECTION;", id="drop_connection_without_name"),
        pytest.param("DROP CREDENTIAL;", id="drop_credential_without_name"),
        pytest.param("DROP EXTERNAL LOCATION;", id="drop_location_without_name"),
        pytest.param("DROP POLICY p;", id="drop_policy_without_target"),
        pytest.param("DROP PROCEDURE;", id="drop_procedure_without_name"),
        pytest.param("DROP PROVIDER;", id="drop_provider_without_name"),
        pytest.param("DROP RECIPIENT;", id="drop_recipient_without_name"),
        pytest.param("DROP SHARE;", id="drop_share_without_name"),
        pytest.param("DROP TEMPORARY VARIABLE;", id="drop_variable_without_name"),
        pytest.param("DROP TABLE;", id="drop_table_without_name"),
    ],
)
def test_drop_uc_rejections(sql: str) -> None:
    """Unity Catalog DROP statement boundaries."""
    assert _violations(sql), f"Expected violations but got none for:\n{sql}"
