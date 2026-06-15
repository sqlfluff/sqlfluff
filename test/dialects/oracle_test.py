"""Oracle dialect specific parser rejection tests.

Verifies that duplicate attributes and mutually-exclusive pairs in Oracle
physical-attribute segments are rejected at parse time (AnySetOf semantics).

Positive/valid-SQL cases belong in the SQL/YAML parse fixtures under
test/fixtures/dialects/oracle/ per project convention.
"""

import pytest

from sqlfluff.core import Linter


def _violations(sql: str) -> list:
    """Return all parse errors, including unparsable nodes anywhere in the tree.

    Top-level parse failures surface in parsed.violations, but content that
    cannot be matched inside a Bracketed clause is silently wrapped in an
    unparsable tree node without raising a SQLParseError. We collect both so
    that rejection tests for STORAGE(...) sub-parameters work correctly.
    """
    parsed = Linter(dialect="oracle").parse_string(sql)
    violations: list = list(parsed.violations)
    if parsed.tree:
        violations += list(parsed.tree.recursive_crawl("unparsable"))
    return violations


# OraclePhysicalAttributesSegment - table-level attributes
@pytest.mark.parametrize(
    "sql",
    [
        # Duplicate scalar attributes
        pytest.param(
            "CREATE TABLE t (c NUMBER) PCTFREE 10 PCTFREE 20;",
            id="dup_pctfree",
        ),
        pytest.param(
            "CREATE TABLE t (c NUMBER) PCTUSED 40 PCTUSED 60;",
            id="dup_pctused",
        ),
        pytest.param(
            "CREATE TABLE t (c NUMBER) INITRANS 2 INITRANS 4;",
            id="dup_initrans",
        ),
        pytest.param(
            "CREATE TABLE t (c NUMBER) MAXTRANS 255 MAXTRANS 100;",
            id="dup_maxtrans",
        ),
        # Mutually exclusive pairs
        pytest.param(
            "CREATE TABLE t (c NUMBER) LOGGING NOLOGGING;",
            id="logging_nologging",
        ),
        pytest.param(
            "CREATE TABLE t (c NUMBER) MONITORING NOMONITORING;",
            id="monitoring_nomonitoring",
        ),
        pytest.param(
            "CREATE TABLE t (c NUMBER) ROWDEPENDENCIES NOROWDEPENDENCIES;",
            id="rowdep_norowdep",
        ),
        pytest.param(
            "CREATE TABLE t (c NUMBER) CACHE NOCACHE;",
            id="cache_nocache",
        ),
    ],
)
def test_table_physical_attrs_rejected(sql: str) -> None:
    """Duplicate or mutually-exclusive table physical attributes must produce a parse violation."""
    assert _violations(sql) != [], f"Expected violations but got none for:\n{sql}"


# StorageClauseSegment - STORAGE(...) sub-parameters
@pytest.mark.parametrize(
    "sql",
    [
        pytest.param(
            "CREATE TABLE t (c NUMBER) STORAGE (INITIAL 256K INITIAL 512K);",
            id="storage_dup_initial",
        ),
        pytest.param(
            "CREATE TABLE t (c NUMBER) STORAGE (NEXT 64K NEXT 128K);",
            id="storage_dup_next",
        ),
        pytest.param(
            "CREATE TABLE t (c NUMBER) STORAGE (MAXEXTENTS 100 MAXEXTENTS 200);",
            id="storage_dup_maxextents",
        ),
        pytest.param(
            "CREATE TABLE t (c NUMBER) STORAGE (PCTINCREASE 0 PCTINCREASE 10);",
            id="storage_dup_pctincrease",
        ),
        pytest.param(
            "CREATE TABLE t (c NUMBER) STORAGE (BUFFER_POOL DEFAULT BUFFER_POOL KEEP);",
            id="storage_dup_buffer_pool",
        ),
    ],
)
def test_storage_clause_rejected(sql: str) -> None:
    """Duplicate STORAGE sub-parameters must produce a parse violation."""
    assert _violations(sql) != [], f"Expected violations but got none for:\n{sql}"


# INMEMORY subclause AnySetOf enforcement
@pytest.mark.parametrize(
    "sql",
    [
        pytest.param(
            "CREATE TABLE t (c NUMBER) INMEMORY PRIORITY LOW PRIORITY HIGH;",
            id="inmemory_dup_priority",
        ),
    ],
)
def test_inmemory_subclauses_rejected(sql: str) -> None:
    """Duplicate INMEMORY subclauses must produce a parse violation."""
    assert _violations(sql) != [], f"Expected violations but got none for:\n{sql}"


# OracleIndexPhysicalAttributesSegment - index-level attributes
@pytest.mark.parametrize(
    "sql",
    [
        # Duplicate scalar attributes
        pytest.param(
            "CREATE INDEX i ON t (c) PCTFREE 10 PCTFREE 20;",
            id="index_dup_pctfree",
        ),
        # Mutually exclusive pairs
        pytest.param(
            "CREATE INDEX i ON t (c) LOGGING NOLOGGING;",
            id="index_logging_nologging",
        ),
        pytest.param(
            "CREATE INDEX i ON t (c) NOSORT REVERSE;",
            id="index_nosort_reverse",
        ),
        pytest.param(
            "CREATE INDEX i ON t (c) VISIBLE INVISIBLE;",
            id="index_visible_invisible",
        ),
    ],
)
def test_index_physical_attrs_rejected(sql: str) -> None:
    """Duplicate or mutually-exclusive index physical attributes must produce a parse violation."""
    assert _violations(sql) != [], f"Expected violations but got none for:\n{sql}"
