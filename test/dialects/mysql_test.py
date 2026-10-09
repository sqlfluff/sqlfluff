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
        "KILL HARD 5",
        "KILL SOFT CONNECTION 5",
        "KILL QUERY ID 5",
        "KILL USER 'u'@'h'",
    ],
)
def test_mysql_kill_rejects_mariadb_only_forms(raw: str) -> None:
    """Test that the MariaDB-only KILL forms do not parse as MySQL.

    MySQL has no HARD/SOFT, QUERY ID or USER forms. The MariaDB keyword is
    read as a variable holding the id, so it is the argument that follows
    it which fails to parse.
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


@pytest.mark.parametrize(
    "raw",
    [
        # In MySQL only procedure parameters take a direction; MariaDB also
        # allows one on function parameters.
        "CREATE FUNCTION f(IN a INT) RETURNS INT RETURN a",
        "CREATE FUNCTION f(OUT a INT) RETURNS INT RETURN 1",
        "CREATE FUNCTION f(INOUT a INT) RETURNS INT RETURN a",
        # A characteristic counts only when complete: READS SQL needs DATA,
        # SQL SECURITY needs DEFINER or INVOKER, NOT needs DETERMINISTIC.
        "CREATE FUNCTION f() RETURNS INT READS SQL RETURN 1",
        "CREATE FUNCTION f() RETURNS INT SQL SECURITY OWNER RETURN 1",
        "CREATE PROCEDURE p() NOT SELECT 1",
        # A character set is a name, not a variable.
        "CREATE FUNCTION f() RETURNS VARCHAR(10) CHARACTER SET @cs RETURN 'x'",
        # A parameter needs a name as well as a type.
        "CREATE PROCEDURE p(INT) SELECT 1",
        "CREATE FUNCTION f(INT) RETURNS INT RETURN 1",
        # A cursor is declared for a query, not any statement.
        "CREATE PROCEDURE p() BEGIN DECLARE c CURSOR FOR DELETE FROM t; END",
        # The brackets are required even when there are no parameters.
        "CREATE PROCEDURE p SELECT 1",
        "CREATE FUNCTION f RETURNS INT RETURN 1",
        # The header order is fixed: CREATE [DEFINER = user]
        # {FUNCTION | PROCEDURE} [IF NOT EXISTS] name (params)
        # [RETURNS type] [characteristics]. Each of these moves one part.
        "CREATE FUNCTION f() DETERMINISTIC RETURNS INT RETURN 1",
        "CREATE FUNCTION DEFINER = CURRENT_USER f() RETURNS INT RETURN 1",
        "CREATE IF NOT EXISTS FUNCTION f() RETURNS INT RETURN 1",
        # MariaDB only: OR REPLACE, parameter defaults, AGGREGATE and
        # CURRENT_ROLE. MySQL reads a bare CURRENT_ROLE as a user name, so only
        # CURRENT_ROLE() is an error.
        "CREATE OR REPLACE FUNCTION f() RETURNS INT RETURN 1",
        "CREATE FUNCTION f(a INT DEFAULT 1) RETURNS INT RETURN a",
        "CREATE AGGREGATE FUNCTION f(x INT) RETURNS INT RETURN x",
        "CREATE DEFINER = CURRENT_ROLE() PROCEDURE p() SELECT 1",
    ],
)
def test_mysql_routine_header_does_not_match_invalid_syntax(raw: str) -> None:
    """Test that invalid routine headers are rejected.

    Each of these is a syntax error on the server.
    """
    parsed = Linter(dialect="mysql").parse_string(raw)
    parsing_errors = [v for v in parsed.violations if v.rule_code() == "PRS"]

    assert parsing_errors
