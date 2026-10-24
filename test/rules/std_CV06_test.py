"""Execution-level regressions for CV06 semicolon placement."""

import sqlite3
from contextlib import closing

import pytest

from sqlfluff.core import FluffConfig, Linter


@pytest.mark.parametrize("dialect", ["ansi", "sqlite"])
@pytest.mark.parametrize(
    "sql,expected",
    [
        ("SELECT\n17\n-- comment\n;SELECT 29;", [[(17,)], [(29,)]]),
        (
            "CREATE TABLE t (v INTEGER);\n"
            "INSERT INTO t\nVALUES (17)\n-- comment\n;"
            "INSERT INTO t VALUES (29);SELECT v FROM t ORDER BY v;",
            [[], [], [], [(17,), (29,)]],
        ),
        (
            "CREATE TABLE t (v INTEGER);INSERT INTO t VALUES (17), (29);\n"
            "DELETE FROM t\nWHERE v = 17\n-- comment\n;"
            "DELETE FROM t WHERE v = 29;SELECT v FROM t;",
            [[], [], [], [], []],
        ),
    ],
    ids=["select", "insert", "delete"],
)
def test__rules__CV06_newline_preserves_execution(
    sql: str, expected: list[list[tuple[int, ...]]], dialect: str
) -> None:
    """Moving a terminator must not extend a line comment over the next SQL."""
    config = FluffConfig(
        configs={"rules": {"convention.terminator": {"multiline_newline": True}}},
        overrides={"dialect": dialect, "rules": "CV06", "templater": "raw"},
    )
    linter = Linter(config=config)
    fixed = linter.lint_string(sql, fix=True).fix_string()[0]

    assert not linter.parse_string(fixed).violations
    assert not linter.lint_string(fixed).violations
    assert linter.lint_string(fixed, fix=True).fix_string()[0] == fixed

    # Both dialect configurations use the same SQLite engine. These flat,
    # trigger-free statements need no external database or real data.
    for script in (sql, fixed):
        with closing(sqlite3.connect(":memory:")) as connection:
            results = []
            statement = ""
            for char in script:
                statement += char
                if sqlite3.complete_statement(statement):
                    results.append(connection.execute(statement).fetchall())
                    statement = ""
            assert results == expected
