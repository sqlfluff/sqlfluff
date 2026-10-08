"""Tests specific to the MySQL dialect."""

from typing import Callable

import pytest
from _pytest.logging import LogCaptureFixture

from sqlfluff.core import Linter


@pytest.mark.parametrize(
    "raw",
    [
        "ELSEIF x = 1 THEN SELECT 1; END IF",
        "ELSE SELECT 1; END IF",
        "x = 0 THEN SELECT 1; END IF",
        "IF x = 0 THEN SELECT 1;",
        "IF x = 0 THEN SELECT 1; ELSE SELECT 2; ELSEIF x = 1 THEN SELECT 3; END IF",
        "IF x = 0 THEN SELECT 1; ELSE SELECT 2; ELSE SELECT 3; END IF",
        "IF x = 0 THEN END IF",
        "IF x = 0 THEN SELECT 1; ELSEIF x = 1 THEN END IF",
        "IF x = 0 THEN SELECT 1; ELSE END IF",
        "IF x = 0 THEN SELECT 1 END IF",
    ],
)
def test_mysql_if_statement_does_not_match_invalid_syntax(
    raw: str,
    caplog: LogCaptureFixture,
    dialect_specific_segment_not_match: Callable,
) -> None:
    """Test that invalid IF statements do not match."""
    dialect_specific_segment_not_match("mysql", "IfExpressionStatement", raw, caplog)


@pytest.mark.parametrize(
    "raw",
    [
        "SELECT HARD 5",
        "SELECT foo 5 FROM t",
        "SELECT INT 5",
    ],
)
def test_mysql_word_then_literal_is_not_a_typed_literal(raw: str) -> None:
    """Test that a word followed by a literal does not parse as a typed literal.

    MySQL only has `DATE`, `TIME` and `TIMESTAMP` literals of this shape. A
    word followed by a string is a column and its alias, and a word followed
    by a number is a syntax error.
    """
    parsed = Linter(dialect="mysql").parse_string(raw)
    parsing_errors = [v for v in parsed.violations if v.rule_code() == "PRS"]

    assert parsing_errors


@pytest.mark.parametrize(
    "dialect,raw",
    [
        # SEPARATOR must follow ORDER BY.
        ("mysql", "SELECT GROUP_CONCAT(v SEPARATOR '|' ORDER BY v) FROM t"),
        # The separator is one string token, or a hexadecimal or bit literal.
        ("mysql", "SELECT GROUP_CONCAT(v SEPARATOR 5) FROM t"),
        ("mysql", "SELECT GROUP_CONCAT(v SEPARATOR 'a' 'b') FROM t"),
        ("mysql", "SELECT GROUP_CONCAT(v SEPARATOR CONCAT('|')) FROM t"),
        # LIMIT is MariaDB only, and must come last.
        ("mysql", "SELECT GROUP_CONCAT(v LIMIT 2) FROM t"),
        ("mariadb", "SELECT GROUP_CONCAT(v LIMIT 1 SEPARATOR '|') FROM t"),
        # JSON_ARRAYAGG has no SEPARATOR.
        ("mariadb", "SELECT JSON_ARRAYAGG(v SEPARATOR ',') FROM t"),
        # The LIMIT values are numbers, placeholders or routine variables only.
        ("mariadb", "SELECT GROUP_CONCAT(v LIMIT ALL) FROM t"),
        ("mariadb", "SELECT GROUP_CONCAT(v LIMIT 1 + 1) FROM t"),
        ("mariadb", "SELECT GROUP_CONCAT(v LIMIT @x) FROM t"),
    ],
)
def test_mysql_group_concat_rejects_invalid_forms(dialect: str, raw: str) -> None:
    """Test that GROUP_CONCAT and JSON_ARRAYAGG only accept the server's syntax.

    Each of these is a syntax error on the server.
    """
    parsed = Linter(dialect=dialect).parse_string(raw)
    parsing_errors = [v for v in parsed.violations if v.rule_code() == "PRS"]

    assert parsing_errors


@pytest.mark.parametrize(
    "raw",
    [
        "KILL HARD 5",
        "KILL SOFT CONNECTION 5",
        "KILL QUERY ID 5",
        "KILL USER 'u'@'h'",
    ],
)
def test_mysql_kill_rejects_mariadb_only_forms(raw: str) -> None:
    """Test that the MariaDB-only KILL forms do not parse as MySQL.

    MySQL has no HARD/SOFT, QUERY ID or USER forms. The MariaDB keyword is
    read as the id expression (a column name), so it is the argument that
    follows it which fails to parse.
    """
    parsed = Linter(dialect="mysql").parse_string(raw)
    parsing_errors = [v for v in parsed.violations if v.rule_code() == "PRS"]

    assert parsing_errors


@pytest.mark.parametrize(
    "raw",
    [
        "CREATE PROCEDURE p() BEGIN WHILE 0 DO END WHILE; END",
        "CREATE PROCEDURE p() BEGIN LOOP END LOOP; END",
        "CREATE PROCEDURE p() BEGIN REPEAT UNTIL 1 END REPEAT; END",
        "CREATE PROCEDURE p() BEGIN IF 1 THEN END IF; END",
    ],
)
def test_mysql_loop_and_if_bodies_are_not_empty(raw: str) -> None:
    """Test that a loop body or IF branch must contain a statement.

    The server's grammar uses `sp_proc_stmts1` (one or more) for these, and
    `sp_proc_stmts` (zero or more) only for `BEGIN ... END`. Each of these is
    a syntax error on the server.
    """
    parsed = Linter(dialect="mysql").parse_string(raw)
    parsing_errors = [v for v in parsed.violations if v.rule_code() == "PRS"]

    assert parsing_errors
