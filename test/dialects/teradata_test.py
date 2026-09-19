"""Tests specific to the Teradata dialect."""

import pytest

from sqlfluff.core import FluffConfig, Linter


@pytest.fixture(scope="module")
def teradata_linter() -> Linter:
    """A Linter configured for the Teradata dialect."""
    return Linter(config=FluffConfig(overrides={"dialect": "teradata"}))


@pytest.mark.parametrize(
    "raw,command",
    [
        # A dot-command terminated only by the end of its line (no semicolon)
        # followed by a semicolon-terminated SQL statement.
        (
            ".LOGON tdpid/username,password\nSELECT 1;\n",
            ".LOGON tdpid/username,password",
        ),
        # A no-argument dot-command followed by SQL.
        (".LOGOFF\nSELECT 1;\n", ".LOGOFF"),
        # A dot-command directly followed by another dot-command, both
        # newline-terminated.
        (".SET WIDTH 254\n.LOGOFF\nSELECT 1;\n", ".SET WIDTH 254"),
    ],
)
def test_bteq_command_is_newline_separated(
    teradata_linter: Linter, raw: str, command: str
) -> None:
    """BTEQ dot-commands are terminated by the end of their line.

    A dot-command needs no semicolon; the following statement parses
    independently rather than being absorbed or reported as unparsable
    (see #1673).
    """
    parsed = teradata_linter.parse_string(raw)

    # The whole script parses cleanly.
    assert not parsed.violations

    bteq_statements = list(parsed.tree.recursive_crawl("bteq_statement"))
    select_statements = list(parsed.tree.recursive_crawl("select_statement"))
    # The dot-command is bounded to its own line and the SELECT is a separate
    # statement (not swallowed by the command).
    assert bteq_statements[0].raw == command
    assert "SELECT" not in bteq_statements[0].raw
    assert len(select_statements) == 1


def test_sql_statements_still_require_a_semicolon(teradata_linter: Linter) -> None:
    """Newline separation does not relax semicolon termination for SQL.

    Only BTEQ dot-commands are newline-terminated; two SQL statements with no
    semicolon between them are still reported as unparsable.
    """
    parsed = teradata_linter.parse_string("SELECT 1 FROM t\nSELECT 2 FROM t\n")

    assert any(v.rule_code() == "PRS" for v in parsed.violations)
