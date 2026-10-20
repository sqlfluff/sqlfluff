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


@pytest.mark.parametrize(
    "body",
    [
        # A branch must contain a statement (`sp_proc_stmts1`), wherever it is.
        "WHEN {a} THEN SET @x = 1; WHEN {b} THEN END CASE",
        "WHEN {a} THEN SET @x = 1; WHEN {b} THEN SET @x = 2; ELSE END CASE",
        # At least one WHEN is required.
        "ELSE SET @x = 1; END CASE",
        # The statement ends with END CASE; a plain END ends the expression.
        "WHEN {a} THEN SET @x = 1; WHEN {b} THEN SET @x = 2; END",
    ],
)
@pytest.mark.parametrize(
    "head, a, b",
    [
        # Simple form: a case value, then values.
        ("CASE @v", "1", "2"),
        # Searched form: conditions.
        ("CASE", "@v = 1", "@v = 2"),
    ],
)
def test_mysql_case_statement_does_not_match_invalid_syntax(
    body: str,
    head: str,
    a: str,
    b: str,
) -> None:
    """Test that invalid CASE statements are rejected, in both forms.

    Each of these is a syntax error on the server.
    """
    case = head + " " + body.format(a=a, b=b)
    raw = "CREATE PROCEDURE p() BEGIN " + case + "; END"
    parsed = Linter(dialect="mysql").parse_string(raw)
    parsing_errors = [v for v in parsed.violations if v.rule_code() == "PRS"]

    assert parsing_errors


@pytest.mark.parametrize(
    "raw",
    [
        "CREATE PROCEDURE p() @lbl: BEGIN END",
        "CREATE FUNCTION f() RETURNS VARCHAR(10) COLLATE @c RETURN 'x'",
        "CREATE TABLE t (a TEXT CHARACTER SET @cs)",
        "CREATE TABLE t (a TEXT COLLATE @c)",
        "CREATE PROCEDURE p() BEGIN DECLARE c CURSOR FOR SELECT 1; OPEN @c; END",
    ],
)
@pytest.mark.parametrize("dialect", ["mysql", "mariadb"])
def test_mysql_user_variable_is_not_a_name(raw: str, dialect: str) -> None:
    """Test that a user variable is not accepted where a name is required.

    Labels, collations, character sets and cursor names are names on the
    server; each of these is a syntax error there.
    """
    parsed = Linter(dialect=dialect).parse_string(raw)
    parsing_errors = [v for v in parsed.violations if v.rule_code() == "PRS"]

    assert parsing_errors


@pytest.mark.parametrize(
    "raw",
    [
        # DELIMITER needs an argument, and refuses an empty one or one with a
        # backslash left in it after unescaping.
        "DELIMITER\nSELECT 1;\n",
        "DELIMITER ''\nSELECT 1;\n",
        "DELIMITER \\\\\nSELECT 1;\n",
        # A command only counts at the start of a statement, and only the active
        # delimiter ends one: here `;` doesn't, so DELIMITER is part of it.
        "SELECT 1; DELIMITER $$\nSELECT 2 $$\n",
        "SELECT 1\nDELIMITER $$\nSELECT 2 $$\n",
        "DELIMITER ;;\nSELECT 1;\nDELIMITER ;\nSELECT 2;\n",
        # The delimiter is found inside words, and is cut to 15 bytes.
        "DELIMITER go\nSELECT 1 AS good go\n",
        "DELIMITER abcdefghijklmnopqrstuvwxyz\nSELECT 1 abcdefghijklmnopqrstuvwxyz\n",
        # `\d` skips its argument up to the new delimiter, which here is inside
        # the quotes, so the rest of the line is read as SQL.
        "\\d '$$' rest\nSELECT 1 $$\n",
        # SOURCE needs a space before its file name.
        "SOURCE\tt.sql\n",
        "\\.a.sql\n",
        # With the delimiter or `\g` on its line, SOURCE is collected as a
        # statement first, so its backslashes run as client commands.
        "SOURCE C:\\db\\x.sql;\n",
        "SOURCE C:\\games\\x.sql\n",
        "SOURCE \\\\gitserver\\share\\x.sql\n",
        "SOURCE \\g\n",
        # A delimiter can't start with whitespace.
        "SELECT 1 \\d  \\ \nSELECT 2;\n",
        "DELIMITER ' x'\nSELECT 1 x\n",
        "DELIMITER '$$ '\nSELECT 1 $$ \n",
        # An unclosed quote in a delimiter argument is a typo.
        "DELIMITER '$$\nSELECT 1 $$\n",
        "\\d '$$\nSELECT 1 $$\n",
        # A line that holds `\g` is collected as a statement, even DELIMITER's.
        "DELIMITER // \\g\nSELECT 1 //\n",
        # SOURCE after a delimiter runs to the next one, past its line.
        "SELECT 1; SOURCE a.sql\nSELECT 2;\n",
    ],
)
@pytest.mark.parametrize("dialect", ["mysql", "mariadb"])
def test_mysql_client_commands_the_client_rejects(raw: str, dialect: str) -> None:
    """Test that client commands the client refuses or misreads don't parse.

    The mysql and mariadb clients report each of these as an error, or send
    the server something other than what is written.
    """
    parsed = Linter(dialect=dialect).parse_string(raw)
    parsing_errors = [v for v in parsed.violations if v.rule_code() == "PRS"]

    assert parsing_errors


@pytest.mark.parametrize(
    "raw",
    [
        # MySQL needs whitespace after `--` for a comment, even at the start
        # of a statement.
        "--Hello\nSELECT 1;\n",
        "SELECT 1; --inline\n",
    ],
)
def test_mysql_dash_dash_needs_whitespace(raw: str) -> None:
    """Test that `--` without whitespace after it isn't a MySQL comment.

    MySQL 8.4 and 9.7 report each of these as a syntax error. (The mariadb
    client takes them as comments; see the mariadb `line_comment` fixture.)
    """
    parsed = Linter(dialect="mysql").parse_string(raw)
    parsing_errors = [v for v in parsed.violations if v.rule_code() == "PRS"]

    assert parsing_errors


@pytest.mark.parametrize(
    "raw",
    [
        "/* comment */ DELIMITER $$\nSELECT 1 $$\n",
        "/* comment */ SOURCE after_comment.sql\n",
    ],
)
def test_mariadb_no_comment_before_a_client_command(raw: str) -> None:
    """Test that the mariadb client doesn't take a command after a comment.

    The mysql client does; see the mysql `client_command_after_comment` fixture.
    """
    parsed = Linter(dialect="mariadb").parse_string(raw)
    parsing_errors = [v for v in parsed.violations if v.rule_code() == "PRS"]

    assert parsing_errors


@pytest.mark.parametrize(
    "raw",
    [
        "SELECT 1 AS $$;\n",
        "SELECT 1 AS $a$;\n",
        "SELECT 1 AS $1$;\n",
        "SELECT 1 AS $$a;\n",
        "SELECT 1 AS $a$b;\n",
        # The client opens the quote before it finds the delimiter `$$`.
        "DELIMITER $$\nSELECT $a$$\n",
    ],
)
def test_mysql_dollar_quote_opener_is_not_a_name(raw: str) -> None:
    """Test that `$tag$` at the start of a token is not a MySQL name.

    MySQL reads it as the start of a dollar-quoted string, which never ends:
    MySQL 8.4 and 9.7 report each of these as a syntax error. (MariaDB has no
    dollar-quoted strings and takes them as names; see its `identifier_dollar`
    fixture.)
    """
    parsed = Linter(dialect="mysql").parse_string(raw)
    lexing_errors = [v for v in parsed.violations if v.rule_code() == "LXR"]

    assert lexing_errors
