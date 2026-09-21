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
            "CREATE CONNECTION TYPE POSTGRESQL OPTIONS (host 'h');",
            id="connection_without_name",
        ),
        pytest.param(
            "CREATE CONNECTION c OPTIONS (host 'h');", id="connection_without_type"
        ),
        pytest.param(
            "CREATE CONNECTION c TYPE OPTIONS (host 'h');",
            id="connection_without_type_value",
        ),
        pytest.param(
            "CREATE CONNECTION c TYPE POSTGRESQL;", id="connection_without_options"
        ),
        pytest.param(
            "CREATE CONNECTION c TYPE POSTGRESQL OPTIONS ();",
            id="connection_empty_options",
        ),
        pytest.param(
            "CREATE CONNECTION c TYPE POSTGRESQL OPTIONS (host);",
            id="connection_without_option_value",
        ),
        pytest.param(
            "CREATE CONNECTION c TYPE POSTGRESQL OPTIONS (host 'h', );",
            id="connection_options_trailing_comma",
        ),
        pytest.param(
            "CREATE EXTERNAL LOCATION URL 'u' WITH (STORAGE CREDENTIAL c);",
            id="location_without_name",
        ),
        pytest.param(
            "CREATE EXTERNAL LOCATION l 'u' WITH (STORAGE CREDENTIAL c);",
            id="location_without_url_keyword",
        ),
        pytest.param(
            "CREATE EXTERNAL LOCATION l URL WITH (STORAGE CREDENTIAL c);",
            id="location_without_url_value",
        ),
        pytest.param("CREATE EXTERNAL LOCATION l URL 'u';", id="location_without_with"),
        pytest.param(
            "CREATE EXTERNAL LOCATION l URL 'u' WITH ();", id="location_empty_with"
        ),
        pytest.param(
            "CREATE EXTERNAL LOCATION l URL 'u' WITH (STORAGE CREDENTIAL);",
            id="location_without_credential_name",
        ),
        pytest.param(
            "CREATE EXTERNAL LOCATION l URL 'u' WITH (STORAGE CREDENTIAL c) COMMENT;",
            id="location_without_comment_value",
        ),
    ],
)
def test_create_connection_location_rejections(sql: str) -> None:
    """CREATE CONNECTION / EXTERNAL LOCATION boundaries."""
    assert _violations(sql), f"Expected violations but got none for:\n{sql}"


@pytest.mark.parametrize(
    "sql",
    [
        pytest.param(
            "CREATE FUNCTION f() RETURNS INT CONTAINS SQL READS SQL DATA RETURN 1;",
            id="contains_sql_and_reads_sql_data",
        ),
        pytest.param(
            "CREATE FUNCTION f() RETURNS INT RETURN 1 AS $$ return 1 $$;",
            id="body_return_and_as",
        ),
        pytest.param(
            "CREATE FUNCTION f() RETURNS INT LANGUAGE RETURN 1;",
            id="language_without_name",
        ),
        pytest.param(
            "CREATE FUNCTION f() RETURNS INT DEFAULT COLLATION RETURN 1;",
            id="default_collation_without_name",
        ),
        pytest.param(
            "CREATE FUNCTION f() RETURNS INT LANGUAGE PYTHON ENVIRONMENT () AS $$ return 1 $$;",
            id="empty_environment",
        ),
        pytest.param(
            "CREATE FUNCTION f() RETURNS INT LANGUAGE PYTHON ENVIRONMENT (dependencies =) AS $$ return 1 $$;",
            id="environment_without_value",
        ),
        pytest.param(
            "CREATE FUNCTION f() RETURNS INT;",
            id="without_body",
        ),
    ],
)
def test_create_function_characteristic_rejections(sql: str) -> None:
    """CREATE FUNCTION characteristic boundaries."""
    assert _violations(sql), f"Expected violations but got none for:\n{sql}"


@pytest.mark.parametrize(
    "sql",
    [
        pytest.param("CREATE SCHEMA IF NOT s;", id="if_not_without_exists"),
        pytest.param("CREATE SCHEMA IF EXISTS s;", id="if_exists_without_not"),
        pytest.param("CREATE SCHEMA s COMMENT;", id="comment_without_text"),
        pytest.param(
            "CREATE SCHEMA s DEFAULT COLLATION;", id="default_collation_without_name"
        ),
        pytest.param("CREATE SCHEMA s LOCATION;", id="location_without_path"),
        pytest.param(
            "CREATE SCHEMA s MANAGED LOCATION;", id="managed_location_without_path"
        ),
        pytest.param(
            "CREATE SCHEMA s RETAIN DROPPED FOR 14;", id="retain_dropped_without_unit"
        ),
        pytest.param(
            "CREATE SCHEMA s RETAIN DROPPED FOR DAYS;",
            id="retain_dropped_without_number",
        ),
        pytest.param("CREATE SCHEMA s WITH DBPROPERTIES ();", id="empty_dbproperties"),
        pytest.param(
            "CREATE SCHEMA s WITH DBPROPERTIES (k =);", id="dbproperties_without_value"
        ),
    ],
)
def test_create_schema_rejections(sql: str) -> None:
    """CREATE SCHEMA clause boundaries."""
    assert _violations(sql), f"Expected violations but got none for:\n{sql}"


@pytest.mark.parametrize(
    "sql",
    [
        pytest.param("CREATE SHARE;", id="share_without_name"),
        pytest.param("CREATE SHARE COMMENT 'x';", id="share_without_name_with_comment"),
        pytest.param("CREATE SHARE s COMMENT;", id="share_without_comment_value"),
        pytest.param("CREATE RECIPIENT USING ID 'x';", id="recipient_without_name"),
        pytest.param("CREATE RECIPIENT r USING ID;", id="recipient_without_sharing_id"),
        pytest.param(
            "CREATE RECIPIENT r PROPERTIES ();", id="recipient_empty_properties"
        ),
        pytest.param(
            "CREATE RECIPIENT r PROPERTIES (k =);",
            id="recipient_without_property_value",
        ),
        pytest.param(
            "CREATE RECIPIENT r COMMENT;", id="recipient_without_comment_value"
        ),
    ],
)
def test_create_share_recipient_rejections(sql: str) -> None:
    """CREATE SHARE / RECIPIENT boundaries a valid-parse fixture cannot express."""
    assert _violations(sql), f"Expected violations but got none for:\n{sql}"


@pytest.mark.parametrize(
    "sql",
    [
        pytest.param(
            "CREATE TABLE t (a INT) DEFAULT COLLATION;",
            id="default_collation_without_name",
        ),
        pytest.param(
            "CREATE TABLE t (a INT) LOCATION 'x' WITH (CREDENTIAL);",
            id="location_without_credential_name",
        ),
    ],
)
def test_create_table_clause_rejections(sql: str) -> None:
    """CREATE TABLE clause boundaries."""
    assert _violations(sql), f"Expected violations but got none for:\n{sql}"


@pytest.mark.parametrize(
    "sql",
    [
        pytest.param(
            "CREATE CATALOG c USING SHARE provider;\n",
            id="share_without_share_name",
        ),
        pytest.param(
            "CREATE CATALOG c RETAIN DROPPED FOR 30;\n",
            id="retain_dropped_without_unit",
        ),
        pytest.param(
            "CREATE CATALOG c DEFAULT COLLATION;\n",
            id="default_collation_without_name",
        ),
        pytest.param(
            "CREATE CATALOG c OPTIONS ();\n",
            id="empty_options",
        ),
        pytest.param(
            "CREATE CATALOG c OPTIONS (k =);\n",
            id="options_without_value",
        ),
        pytest.param(
            "CREATE FOREIGN CATALOG fc OPTIONS (k = 'v');\n",
            id="foreign_without_connection",
        ),
        pytest.param(
            "CREATE FOREIGN CATALOG fc USING CONNECTION conn;\n",
            id="foreign_without_options",
        ),
    ],
)
def test_create_catalog_requires_bound_clauses(sql: str) -> None:
    """A clause's required tokens are all required.

    The reference gives the clause list as a bracketed alternation: a share
    needs both name parts, RETAIN DROPPED takes a number and a unit, a
    collation needs its name, OPTIONS needs at least one name-value pair, and
    the foreign form needs both USING CONNECTION and OPTIONS.
    """
    assert _violations(sql), f"Expected violations but got none for:\n{sql}"
