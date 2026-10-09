"""Tests specific to the MySQL dialect."""

from typing import Callable

import pytest
from _pytest.logging import LogCaptureFixture

from sqlfluff.core import FluffConfig, Linter


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


@pytest.mark.parametrize("dialect", ["mysql", "mariadb"])
def test_mysql_source_ends_at_end_of_line(dialect: str) -> None:
    """Test that a SOURCE file name doesn't run on to the next line."""
    parsed = Linter(dialect=dialect).parse_string(
        "SOURCE a.sql\nSELECT 1;\n\\. b.sql\nSELECT 2;\n"
    )

    assert not parsed.violations
    assert parsed.tree
    sources = list(parsed.tree.recursive_crawl("source_statement"))
    assert [s.raw for s in sources] == ["SOURCE a.sql", "\\. b.sql"]
    assert len(list(parsed.tree.recursive_crawl("select_statement"))) == 2


@pytest.mark.parametrize(
    "raw",
    [
        # Only SOURCE may omit the delimiter. Other statements still need one.
        "SELECT 1\nSELECT 2;\n",
        "DELETE FROM t\nSELECT 1;\n",
        # The file name is required, and must be on the same line.
        "SOURCE\na.sql\n",
        # The command and file name must be separated by whitespace.
        "\\.a.sql\n",
    ],
)
def test_mysql_source_invalid_syntax(raw: str) -> None:
    """Test that invalid uses of SOURCE, or missing delimiters, don't parse."""
    parsed = Linter(dialect="mysql").parse_string(raw)
    parsing_errors = [v for v in parsed.violations if v.rule_code() == "PRS"]

    assert parsing_errors


@pytest.mark.parametrize("dialect", ["mysql", "mariadb"])
def test_mysql_source_is_an_identifier_mid_statement(dialect: str) -> None:
    """Test that SOURCE starting a line within a statement is an identifier.

    SOURCE is only a client command at the start of a statement.
    """
    parsed = Linter(dialect=dialect).parse_string(
        "SELECT a\nFROM t\nWHERE\nsource = 'web';\n"
    )

    assert not parsed.violations
    assert parsed.tree
    assert not list(parsed.tree.recursive_crawl("source_statement"))
    assert not list(parsed.tree.recursive_crawl("unparsable"))
    assert len(list(parsed.tree.recursive_crawl("select_statement"))) == 1


def test_mysql_source_file_name_is_not_respaced() -> None:
    """Test that layout rules leave the spacing inside a SOURCE file name alone.

    The client reads the file name verbatim, so respacing it would change it.
    """
    sql = "SOURCE ../my-dir/v1.2/file  name.sql\n\\. C:/db/a+b.sql\n"
    linted = Linter(dialect="mysql", rules=["LT01"]).lint_string(sql)

    assert not linted.violations

    # It's the `spacing_within = any` default that leaves it alone.
    config = FluffConfig(
        configs={
            "layout": {"type": {"source_file_name": {"spacing_within": "single"}}}
        },
        overrides={"dialect": "mysql", "rules": "LT01"},
    )
    linted = Linter(config=config).lint_string(sql)

    assert linted.violations
