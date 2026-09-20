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
        pytest.param("ALTER CATALOG c DEFAULT COLLATION;", id="catalog_collation_without_value"),
        pytest.param("ALTER CATALOG c SET TAGS ();", id="catalog_empty_tags"),
        pytest.param("ALTER CATALOG c SET MANAGED LOCATION;", id="catalog_managed_location_without_path"),
        pytest.param("ALTER CATALOG c RETAIN DROPPED TO 1;", id="catalog_retain_dropped_without_unit"),
        pytest.param("ALTER SCHEMA s SET DBPROPERTIES ();", id="schema_empty_dbproperties"),
        pytest.param("ALTER SCHEMA s DEFAULT COLLATION;", id="schema_collation_without_value"),
    ],
)
def test_alter_catalog_schema_rejections(sql: str) -> None:
    """ALTER CATALOG / SCHEMA clause boundaries."""
    assert _violations(sql), f"Expected violations but got none for:\n{sql}"


@pytest.mark.parametrize(
    "sql",
    [
        pytest.param("ALTER CONNECTION c RENAME TO;", id="connection_rename_without_value"),
        pytest.param("ALTER CONNECTION c OPTIONS ();", id="connection_empty_options"),
        pytest.param("ALTER EXTERNAL LOCATION l SET URL;", id="location_set_url_without_value"),
        pytest.param("ALTER CREDENTIAL c RENAME TO;", id="credential_rename_without_value"),
    ],
)
def test_alter_connection_location_credential_rejections(sql: str) -> None:
    """ALTER CONNECTION / EXTERNAL LOCATION / CREDENTIAL boundaries."""
    assert _violations(sql), f"Expected violations but got none for:\n{sql}"


@pytest.mark.parametrize(
    "sql",
    [
        pytest.param("ALTER GROUP ADD GROUP h;", id="group_without_principal"),
        pytest.param("ALTER GROUP g ADD;", id="group_add_without_members"),
    ],
)
def test_alter_group_rejections(sql: str) -> None:
    """ALTER GROUP boundaries."""
    assert _violations(sql), f"Expected violations but got none for:\n{sql}"


@pytest.mark.parametrize(
    "sql",
    [
        pytest.param("ALTER MATERIALIZED VIEW v ALTER COLUMN c COMMENT;", id="mv_column_comment_without_value"),
        pytest.param("ALTER MATERIALIZED VIEW v ADD SCHEDULE;", id="mv_add_schedule_without_clause"),
        pytest.param("ALTER STREAMING TABLE t SET OWNER TO;", id="streaming_table_owner_without_value"),
    ],
)
def test_alter_materialized_view_streaming_table_rejections(sql: str) -> None:
    """ALTER MATERIALIZED VIEW / STREAMING TABLE boundaries."""
    assert _violations(sql), f"Expected violations but got none for:\n{sql}"


@pytest.mark.parametrize(
    "sql",
    [
        pytest.param("ALTER RECIPIENT r SET PROPERTIES ();", id="recipient_empty_properties"),
        pytest.param("ALTER RECIPIENT r UNSET PROPERTIES ();", id="recipient_empty_unset_properties"),
        pytest.param("ALTER PROVIDER p RENAME TO;", id="provider_rename_without_value"),
    ],
)
def test_alter_recipient_provider_rejections(sql: str) -> None:
    """ALTER RECIPIENT / PROVIDER boundaries."""
    assert _violations(sql), f"Expected violations but got none for:\n{sql}"


@pytest.mark.parametrize(
    "sql",
    [
        pytest.param("ALTER SHARE s ADD TABLE;", id="share_add_table_without_name"),
        pytest.param("ALTER SHARE s ADD;", id="share_add_without_object"),
        pytest.param("ALTER SHARE s RENAME TO;", id="share_rename_without_value"),
    ],
)
def test_alter_share_rejections(sql: str) -> None:
    """ALTER SHARE clause boundaries."""
    assert _violations(sql), f"Expected violations but got none for:\n{sql}"


@pytest.mark.parametrize(
    "sql",
    [
        pytest.param(
            "ALTER TABLE RENAME TO t2;",
            id="no_table_name",
        ),
        pytest.param(
            "ALTER TABLE t REPLACE PARTITIONED BY WITH;",
            id="replace_partitioned_without_cluster_by",
        ),
    ],
)
def test_alter_table_rejections(sql: str) -> None:
    """ALTER TABLE boundaries that a valid-parse fixture cannot express."""
    assert _violations(sql), f"Expected violations but got none for:\n{sql}"
