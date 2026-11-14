"""Regressions for CV06 semicolon diagnostics and placement."""

import sqlite3
from contextlib import closing

import pytest

from sqlfluff.core import FluffConfig, Linter


@pytest.mark.parametrize("multiline_newline", [False, True])
@pytest.mark.parametrize("require_final_semicolon", [False, True])
@pytest.mark.parametrize("comment", ["", " -- trailing comment"])
def test__rules__CV06_missing_intermediate_terminator(
    multiline_newline: bool, require_final_semicolon: bool, comment: str
) -> None:
    """Require intermediate terminators independently of the final-statement option."""
    config = FluffConfig(
        configs={
            "rules": {
                "convention.terminator": {
                    "multiline_newline": multiline_newline,
                    "require_final_semicolon": require_final_semicolon,
                }
            }
        },
        overrides={"dialect": "oracle", "rules": "CV06", "templater": "raw"},
    )
    linter = Linter(config=config)
    first = "DELETE\nFROM code_detail"
    second = "INSERT INTO code_head(code_type)\nVALUES('PLTQ')"
    sql = first + comment + "\n-- between statements\n" + second + "\n\n"
    terminator = "\n;" if multiline_newline else ";"
    fixed_first = (
        first + comment + terminator
        if multiline_newline
        else first + terminator + comment
    )
    expected = fixed_first + "\n-- between statements\n" + second
    expected += (terminator if require_final_semicolon else "") + "\n\n"

    assert not linter.parse_string(sql).violations
    violations = linter.lint_string(sql).violations
    assert [v.rule_code() for v in violations] == ["CV06"] * (
        2 if require_final_semicolon else 1
    )
    assert violations[0].line_no == 2
    fixed = linter.lint_string(sql, fix=True).fix_string()[0]
    assert fixed == expected
    assert not linter.parse_string(fixed).violations
    assert not linter.lint_string(fixed).violations
    assert linter.lint_string(fixed, fix=True).fix_string()[0] == fixed


@pytest.mark.parametrize("dialect", ["ansi", "oracle"])
@pytest.mark.parametrize(
    "sql,multiline_newline,description,fixed",
    [
        (
            "SELECT a FROM foo ;\n",
            False,
            "Semi-colon should be immediately after the statement.",
            "SELECT a FROM foo;\n",
        ),
        (
            "SELECT a\nFROM foo\n;\n",
            False,
            "Semi-colon should be immediately after the statement.",
            "SELECT a\nFROM foo;\n",
        ),
        (
            "SELECT a\nFROM foo;\n",
            True,
            "Semi-colon should be on a new line after a multi-line statement.",
            "SELECT a\nFROM foo\n;\n",
        ),
        (
            "SELECT a\nFROM foo\n",
            False,
            "Statements must end with a semi-colon.",
            "SELECT a\nFROM foo;\n",
        ),
        ("SELECT a FROM foo;\n", True, None, "SELECT a FROM foo;\n"),
        ("SELECT a\nFROM foo\n;\n", True, None, "SELECT a\nFROM foo\n;\n"),
    ],
    ids=["space", "newline", "own-line", "missing", "single-line", "correct"],
)
def test__rules__CV06_description(
    sql: str,
    multiline_newline: bool,
    description: str | None,
    fixed: str,
    dialect: str,
) -> None:
    """Distinguish misplaced terminators from missing ones without changing fixes."""
    config = FluffConfig(
        configs={
            "rules": {
                "convention.terminator": {
                    "multiline_newline": multiline_newline,
                    "require_final_semicolon": True,
                }
            }
        },
        overrides={"dialect": dialect, "rules": "CV06", "templater": "raw"},
    )
    linter = Linter(config=config)
    violations = linter.lint_string(sql).violations
    expected = [("CV06", description)] if description else []
    assert [(v.rule_code(), v.description) for v in violations] == expected
    assert linter.lint_string(sql, fix=True).fix_string()[0] == fixed
    assert not linter.lint_string(fixed).violations


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


@pytest.mark.parametrize("require_final_semicolon", [False, True])
@pytest.mark.parametrize("ending", [";\n", "\n", ";\nGO\n"])
@pytest.mark.parametrize(
    "elements",
    [
        "CREATE TABLE test (id INT)",
        "CREATE VIEW test AS SELECT 1 AS id",
        "GRANT SELECT ON SCHEMA::staging TO reader",
        "DENY SELECT ON SCHEMA::staging TO reader",
        "REVOKE SELECT ON SCHEMA::staging FROM reader",
        "CREATE TABLE first_table (id INT)\nCREATE TABLE second_table (id INT)",
        "CREATE TABLE staging.Person (id INT) AS NODE",
        "CREATE TABLE staging.Relation (id INT) AS EDGE",
        "CREATE TABLE likes AS EDGE",
        "CREATE TABLE staging.Person (id INT) AS NODE\n"
        "CREATE TABLE staging.likes AS EDGE\n"
        "CREATE TABLE test (id INT)",
        "GRANT SELECT ON SCHEMA::staging TO reader\n"
        "CREATE TABLE test (id INT)\n"
        "-- Keep the schema elements in one atomic statement.\n"
        "CREATE VIEW test_view AS SELECT id FROM test\n"
        "DENY UPDATE ON SCHEMA::staging TO reader\n"
        "REVOKE DELETE ON SCHEMA::staging FROM reader",
    ],
)
def test__rules__CV06_tsql_atomic_schema(
    elements: str, ending: str, require_final_semicolon: bool
) -> None:
    """CREATE SCHEMA elements belong to a single atomic T-SQL statement."""
    config = FluffConfig(
        configs={
            "rules": {
                "convention.terminator": {
                    "require_final_semicolon": require_final_semicolon
                }
            }
        },
        overrides={"dialect": "tsql", "rules": "CV06", "templater": "raw"},
    )
    linter = Linter(config=config)
    statement = "CREATE SCHEMA staging AUTHORIZATION dbo\n" + elements
    sql = statement + ending
    expected = statement + ";\n" if require_final_semicolon and ending == "\n" else sql
    assert linter.lint_string(sql, fix=True).fix_string()[0] == expected
    assert not linter.lint_string(expected).violations
    assert linter.lint_string(expected, fix=True).fix_string()[0] == expected
    parsed = linter.parse_string(sql)
    assert not parsed.violations
    assert parsed.tree is not None
    statements = list(parsed.tree.recursive_crawl("statement"))
    assert len(statements) == 1
    assert statements[0].get_child("create_schema_statement") is not None
