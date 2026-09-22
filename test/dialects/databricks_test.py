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
        pytest.param("SHOW GRANTS;\n", id="no_securable"),
        pytest.param("SHOW GRANTS TABLE my_table;\n", id="missing_on"),
        pytest.param("SHOW GRANTS `alf` my_table;\n", id="principal_without_on"),
    ],
)
def test_show_grants_requires_a_securable(sql: str) -> None:
    """`SHOW GRANTS [ principal ] ON securable_object`.

    The securable and its `ON` are both required; only the principal is
    optional.
    """
    assert _violations(sql), f"Expected a parse failure for:\n{sql}"


@pytest.mark.parametrize(
    "sql",
    [
        pytest.param(
            "SHOW GRANTS ON STORAGE sc;\n",
            id="storage_without_credential",
        ),
        pytest.param(
            "SHOW GRANTS ON STORAGE CREDENTIAL;\n",
            id="credential_without_name",
        ),
        pytest.param(
            "SHOW GRANTS ON SERVICE sc;\n",
            id="service_without_credential",
        ),
        pytest.param(
            "GRANT ALL PRIVILEGES, SELECT ON TABLE t TO p;\n",
            id="all_privileges_in_list",
        ),
        pytest.param(
            "GRANT SELECT, ALL PRIVILEGES ON TABLE t TO p;\n",
            id="all_privileges_later_in_list",
        ),
        pytest.param(
            "GRANT ALL, SELECT ON TABLE t TO p;\n",
            id="bare_all_in_list",
        ),
    ],
)
def test_privileges_bind_their_clauses(sql: str) -> None:
    """Privilege forms bind, in both directions.

    A credential is `[ STORAGE | SERVICE ] CREDENTIAL name`, never the scope
    keyword alone or without a name, and `privilege_types` is
    `{ ALL PRIVILEGES | privilege_type [, ...] }`, so ALL PRIVILEGES cannot
    open or join a list.
    """
    assert _violations(sql), f"Expected violations but got none for:\n{sql}"


@pytest.mark.parametrize(
    "sql",
    [
        pytest.param("DESCRIBE CATALOG;", id="describe_catalog_without_name"),
        pytest.param("DESCRIBE CONNECTION;", id="describe_connection_without_name"),
        pytest.param("DESCRIBE CREDENTIAL;", id="describe_credential_without_name"),
        pytest.param(
            "DESCRIBE EXTERNAL LOCATION;", id="describe_location_without_name"
        ),
        pytest.param("DESCRIBE FUNCTION;", id="describe_function_without_name"),
        pytest.param("DESCRIBE POLICY p;", id="describe_policy_without_target"),
        pytest.param("DESCRIBE PROCEDURE;", id="describe_procedure_without_name"),
        pytest.param("DESCRIBE PROVIDER;", id="describe_provider_without_name"),
        pytest.param("DESCRIBE QUERY;", id="describe_query_without_statement"),
        pytest.param("DESCRIBE SCHEMA;", id="describe_schema_without_name"),
        pytest.param("DESCRIBE SHARE;", id="describe_share_without_name"),
        pytest.param("DESCRIBE VOLUME;", id="describe_volume_without_name"),
        pytest.param(
            "SHOW SHARES IN PROVIDER;", id="show_shares_in_provider_without_name"
        ),
        pytest.param("SHOW ALL IN SHARE;", id="show_all_in_share_without_name"),
        pytest.param("SHOW COLUMNS IN;", id="show_columns_without_table"),
        pytest.param(
            "SHOW GRANTS TO RECIPIENT;", id="show_grants_to_recipient_without_name"
        ),
        pytest.param("SHOW POLICIES ON;", id="show_policies_without_target"),
        pytest.param("DENY SELECT ON TABLE t;", id="deny_without_principal"),
        pytest.param("DROP GROUP;", id="drop_group_without_name"),
        pytest.param(
            "GRANT SELECT ON SHARE s TO RECIPIENT;", id="grant_share_without_recipient"
        ),
        pytest.param(
            "REVOKE SELECT ON SHARE FROM RECIPIENT r;", id="revoke_share_without_share"
        ),
        pytest.param("GRANT SELECT ON TABLE TO `u`;", id="grant_table_without_name"),
    ],
)
def test_uc_show_describe_security_rejections(sql: str) -> None:
    """Unity Catalog SHOW/DESCRIBE and security statement boundaries."""
    assert _violations(sql), f"Expected violations but got none for:\n{sql}"
