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


def test_merge_insert_requires_values_clause() -> None:
    """Oracle MERGE insert clauses cannot omit VALUES before WHERE."""
    assert _violations(
        "MERGE INTO target t USING source s ON (t.id = s.id) "
        "WHEN NOT MATCHED THEN INSERT (id) WHERE s.id > 0;"
    )


def test_merge_delete_requires_where_clause() -> None:
    """Oracle MERGE delete clauses cannot omit WHERE."""
    assert _violations(
        "MERGE INTO target t USING source s ON (t.id = s.id) "
        "WHEN MATCHED THEN UPDATE SET t.value = s.value DELETE;"
    )


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


# `slash_buffer_executor` lexer matcher: SQL*Plus runs the SQL buffer when a
# `/` sits alone on its own line. The Oracle lexer emits that form of `/`
# as a distinct `slash_buffer_executor` token, so the parser never has to
# disambiguate it from the arithmetic division operator. These tests lock
# in that lexer decision across the shapes of context the matcher is meant
# to handle, per the review on PR #8483.


def _slash_tokens(sql: str) -> list:
    """Return the raw `/` segments produced by lexing `sql` under Oracle."""
    parsed = Linter(dialect="oracle").parse_string(sql)
    assert parsed.tree is not None, sql
    return [seg for seg in parsed.tree.raw_segments if seg.raw == "/"]


def _standalone_slash_count(sql: str) -> int:
    """How many `/` tokens carry the `slash_buffer_executor` instance type."""
    return sum(
        1 for seg in _slash_tokens(sql) if "slash_buffer_executor" in seg.class_types
    )


def _division_slash_count(sql: str) -> int:
    """How many `/` tokens are the ordinary division operator (not standalone)."""
    return sum(
        1
        for seg in _slash_tokens(sql)
        if "slash_buffer_executor" not in seg.class_types
    )


@pytest.mark.parametrize(
    "sql, expected_standalone, expected_division",
    [
        # Division operator never becomes a slash_buffer_executor.
        pytest.param("SELECT 1 / 100 FROM DUAL;", 0, 1, id="division_inline"),
        pytest.param(
            "SELECT NVL(X, 0) / 1024 / 1024 FROM T;", 0, 2, id="division_chained"
        ),
        pytest.param("SELECT SYSDATE - 1 / 24 FROM DUAL;", 0, 1, id="division_sysdate"),
        # A `/` alone on its own line is the buffer-executor.
        # LF and CRLF forms both match.
        pytest.param("SELECT 1 FROM DUAL;\n/\n", 1, 0, id="standalone_lf"),
        pytest.param("SELECT 1 FROM DUAL;\r\n/\r\n", 1, 0, id="standalone_crlf"),
        # EOF (no trailing newline) also qualifies.
        pytest.param(
            "SELECT 1 FROM DUAL;\n/", 1, 0, id="standalone_eof_no_trailing_newline"
        ),
        # Leading / trailing inline whitespace on the slash's own line is ok.
        pytest.param(
            "SELECT 1 FROM DUAL;\n   /\n", 1, 0, id="standalone_leading_whitespace"
        ),
        pytest.param(
            "SELECT 1 FROM DUAL;\n/   \n", 1, 0, id="standalone_trailing_whitespace"
        ),
        # A `/` followed by a comment on the same line is NOT standalone
        # (SQL*Plus requires the line to carry only the slash).
        pytest.param(
            "SELECT 1 FROM DUAL;\n/ -- end\n",
            0,
            1,
            id="slash_with_trailing_comment_is_division",
        ),
        # A leading `/` at the very start of input is also the buffer-executor:
        # SQL*Plus documents a script-opening `/` as running whatever is
        # already in the buffer from the surrounding session.
        pytest.param("/\nSELECT 1 FROM DUAL;\n", 1, 0, id="start_of_input_slash"),
        pytest.param("/", 1, 0, id="start_of_input_slash_only"),
        # Several batches separated by standalone slashes.
        pytest.param(
            "BEGIN NULL; END;\n/\nBEGIN NULL; END;\n/\n",
            2,
            0,
            id="multiple_plsql_batches",
        ),
        # Division across a line continuation stays as division (the `/`
        # does not sit on its own line).
        pytest.param(
            "SELECT 1 /\n100 FROM DUAL;", 0, 1, id="division_newline_continuation"
        ),
    ],
)
def test_slash_buffer_executor_lexer(
    sql: str, expected_standalone: int, expected_division: int
) -> None:
    """The lexer distinguishes a standalone-line `/` from the division operator."""
    assert _standalone_slash_count(sql) == expected_standalone, sql
    assert _division_slash_count(sql) == expected_division, sql


@pytest.mark.parametrize(
    "sql",
    [
        # CREATE VIEW ... SELECT with a bare `/` arithmetic operator.
        pytest.param(
            "CREATE VIEW V AS SELECT 1 / 100 AS R FROM DUAL;",
            id="create_view_inline_division",
        ),
        pytest.param(
            "CREATE VIEW V AS SELECT NVL(X, 0) / 1024 / 1024 AS R FROM T;",
            id="create_view_chained_division",
        ),
        pytest.param(
            "CREATE VIEW V AS SELECT SYSDATE - 1 / 24 FROM DUAL;",
            id="create_view_sysdate_minus_fraction",
        ),
        # Batch delimiter must still parse at the end of a CREATE VIEW body.
        pytest.param(
            "CREATE VIEW V AS SELECT 1 FROM DUAL\n/\n",
            id="create_view_batch_delimiter",
        ),
        # Standalone PL/SQL block and procedure terminated by `/`.
        pytest.param(
            "BEGIN NULL; END;\n/\n",
            id="plsql_anonymous_block_batch_delimiter",
        ),
        pytest.param(
            "CREATE OR REPLACE PROCEDURE p AS BEGIN NULL; END;\n/\n",
            id="plsql_procedure_batch_delimiter",
        ),
    ],
)
def test_slash_contexts_parse_clean(sql: str) -> None:
    """Each bare-slash context parses with no unparsable nodes."""
    assert _violations(sql) == [], f"Expected no violations, got some for:\n{sql}"
