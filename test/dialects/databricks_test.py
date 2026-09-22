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
        pytest.param("OPTIMIZE;", id="optimize_without_table"),
        pytest.param("OPTIMIZE events WHERE;", id="optimize_where_without_predicate"),
        pytest.param(
            "OPTIMIZE events FULL WHERE;", id="optimize_full_where_without_predicate"
        ),
        pytest.param("OPTIMIZE events ZORDER BY ();", id="optimize_empty_zorder_list"),
        pytest.param(
            "OPTIMIZE events ZORDER BY (a, );", id="optimize_zorder_trailing_comma"
        ),
        pytest.param("VACUUM;", id="vacuum_without_table"),
        pytest.param("VACUUM t FULL LITE;", id="vacuum_full_and_lite"),
        pytest.param("VACUUM t DRY RUN FULL;", id="vacuum_dry_run_and_full"),
    ],
)
def test_maintenance_full_mode_rejections(sql: str) -> None:
    """OPTIMIZE / VACUUM clause boundaries and exclusive FULL/LITE modes."""
    assert _violations(sql), f"Expected violations but got none for:\n{sql}"


@pytest.mark.parametrize(
    "sql",
    [
        pytest.param(
            "MERGE WITH SCHEMA EVOLUTION t USING s ON t.k = s.k WHEN MATCHED THEN UPDATE SET *;",
            id="schema_evolution_without_into",
        ),
    ],
)
def test_merge_schema_evolution_rejections(sql: str) -> None:
    """WITH SCHEMA EVOLUTION is only valid before INTO."""
    assert _violations(sql), f"Expected violations but got none for:\n{sql}"


@pytest.mark.parametrize(
    "sql",
    [
        pytest.param(
            "COPY INTO t () FROM 'p' FILEFORMAT = CSV;",
            id="empty_column_list",
        ),
        pytest.param(
            "COPY INTO t (a, ) FROM 'p' FILEFORMAT = CSV;",
            id="column_list_trailing_comma",
        ),
        pytest.param(
            "COPY INTO t FROM 'p' FILEFORMAT = CSV VALIDATE 10;",
            id="validate_without_unit",
        ),
        pytest.param(
            "COPY INTO t FROM 'p' FILEFORMAT = CSV VALIDATE ROWS;",
            id="validate_without_number",
        ),
        pytest.param(
            "COPY INTO t FROM 'p' FILEFORMAT = CSV FILES = ();",
            id="empty_files",
        ),
        pytest.param(
            "COPY INTO t FROM 'p' FILEFORMAT = CSV FILES = ('a.csv', );",
            id="file_list_trailing_comma",
        ),
        pytest.param(
            "COPY INTO t FROM 'p' FILEFORMAT = CSV FORMAT_OPTIONS ();",
            id="empty_format_options",
        ),
        pytest.param(
            "COPY INTO t FROM 'p' FILEFORMAT = CSV FORMAT_OPTIONS (header =);",
            id="format_option_without_value",
        ),
        pytest.param(
            "COPY INTO t FROM 'p' FILEFORMAT = CSV COPY_OPTIONS ();",
            id="empty_copy_options",
        ),
        pytest.param(
            "COPY INTO t FROM 'p' FILEFORMAT = CSV COPY_OPTIONS (force =);",
            id="copy_option_without_value",
        ),
        pytest.param(
            "COPY INTO t FROM 'p' FILEFORMAT =;",
            id="fileformat_without_source",
        ),
        pytest.param(
            "COPY INTO t FROM FILEFORMAT = CSV;",
            id="from_without_source",
        ),
        pytest.param(
            "COPY INTO t FROM 'p' WITH (CREDENTIAL) FILEFORMAT = CSV;",
            id="credential_without_name",
        ),
        pytest.param(
            "COPY INTO t FROM 'p' WITH (ENCRYPTION ()) FILEFORMAT = CSV;",
            id="empty_encryption",
        ),
        pytest.param(
            "COPY INTO t FROM 'p' FILEFORMAT = CSV FILES = ('a.csv') PATTERN = '*.csv';",
            id="files_and_pattern",
        ),
    ],
)
def test_copy_into_rejections(sql: str) -> None:
    """COPY INTO clause boundaries that a valid-parse fixture cannot express."""
    assert _violations(sql), f"Expected violations but got none for:\n{sql}"


@pytest.mark.parametrize(
    "sql",
    [
        pytest.param("FSCK REPAIR TABLE;", id="fsck_without_table"),
        pytest.param("FSCK REPAIR TABLE t METADATA;", id="fsck_metadata_without_only"),
        pytest.param("REORG TABLE events;", id="reorg_without_apply"),
        pytest.param("REORG TABLE events APPLY ();", id="reorg_empty_purge"),
        pytest.param("CACHE SELECT FROM boxes;", id="cache_select_without_column"),
        pytest.param("CACHE SELECT a, FROM boxes;", id="cache_select_trailing_comma"),
        pytest.param("DROP BLOOMFILTER INDEX;", id="bloom_without_table"),
        pytest.param(
            "DROP BLOOMFILTER INDEX ON TABLE t FOR COLUMNS ();",
            id="bloom_empty_columns",
        ),
        pytest.param("REPAIR TABLE;", id="repair_without_table"),
        pytest.param("REFRESH MATERIALIZED VIEW;", id="refresh_mv_without_table"),
        pytest.param("REFRESH FOREIGN;", id="refresh_foreign_without_type"),
        pytest.param("REFRESH FUNCTION;", id="refresh_function_without_name"),
        pytest.param("UNDROP TABLE;", id="undrop_without_name"),
        pytest.param("SYNC TABLE main.t FROM;", id="sync_without_source"),
        pytest.param("LIST;", id="list_without_url"),
        pytest.param("CALL (1);", id="call_without_name"),
        pytest.param("SET RECIPIENT;", id="set_recipient_without_name"),
        pytest.param(
            "ANALYZE TABLE COMPUTE STORAGE METRICS;", id="analyze_metrics_without_table"
        ),
        pytest.param("SET TAG ON TABLE t;", id="set_tag_without_key"),
        pytest.param("UNSET TAG ON TABLE t;", id="unset_tag_without_key"),
    ],
)
def test_maintenance_and_utility_rejections(sql: str) -> None:
    """Delta maintenance and auxiliary statement boundaries."""
    assert _violations(sql), f"Expected violations but got none for:\n{sql}"
