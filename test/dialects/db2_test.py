"""Db2 dialect-specific parser tests.

Positive SQL cases live in ``test/fixtures/dialects/db2/``. These tests pin
the shape of Db2-specific trailing clauses on ``CREATE TABLE`` so that they
are modelled as dedicated segments instead of generic keywords or aliases.
"""

import pytest

from sqlfluff.core import Linter

TRAILING_CLAUSE_CASES = [
    pytest.param(
        "CREATE TABLE t (a INT) ORGANIZE BY ROW;",
        "table_organization_clause",
        id="organize_by_row",
    ),
    pytest.param(
        "CREATE TABLE t (a INT) ORGANIZE BY COLUMN;",
        "table_organization_clause",
        id="organize_by_column",
    ),
    pytest.param(
        "CREATE TABLE t (a INT) DISTRIBUTE BY HASH (a);",
        "distribution_clause",
        id="distribute_by_hash",
    ),
    pytest.param(
        "CREATE TABLE t (a INT) DISTRIBUTE BY RANDOM;",
        "distribution_clause",
        id="distribute_by_random",
    ),
    pytest.param(
        "CREATE TABLE t (a INT) DISTRIBUTE BY REPLICATION;",
        "distribution_clause",
        id="distribute_by_replication",
    ),
    pytest.param(
        "CREATE TABLE t (a INT) IN ts;",
        "tablespace_clause",
        id="in_tablespace",
    ),
    pytest.param(
        "CREATE TABLE t (a INT) IN ts INDEX IN ts2 LONG IN ts3;",
        "tablespace_clause",
        id="in_tablespace_with_index_and_long",
    ),
    pytest.param(
        "CREATE TABLE t (a INT) WITH RESTRICT ON DROP;",
        "with_restrict_on_drop_clause",
        id="with_restrict_on_drop",
    ),
]


@pytest.mark.parametrize("sql,expected_type", TRAILING_CLAUSE_CASES)
def test_create_table_trailing_clause(sql: str, expected_type: str) -> None:
    """Db2 trailing clauses parse into their own segment types."""
    parsed = Linter(dialect="db2").parse_string(sql)
    assert parsed.tree is not None
    types = parsed.tree.type_set()
    assert "unparsable" not in types, f"Unparsable section in: {sql}"
    assert expected_type in types, f"Expected {expected_type} in {sorted(types)}"


def test_create_table_trailing_clauses_combined() -> None:
    """All Db2 trailing clauses can be combined on one table."""
    sql = (
        "CREATE TABLE t (a INT) "
        "ORGANIZE BY ROW "
        "DISTRIBUTE BY HASH (a) "
        "IN ts INDEX IN ts2 LONG IN ts3 "
        "WITH RESTRICT ON DROP;"
    )
    parsed = Linter(dialect="db2").parse_string(sql)
    assert parsed.tree is not None
    types = parsed.tree.type_set()
    assert "unparsable" not in types, f"Unparsable section in: {sql}"
    assert {
        "table_organization_clause",
        "distribution_clause",
        "tablespace_clause",
        "with_restrict_on_drop_clause",
    } <= types
