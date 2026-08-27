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
        # Opaque arguments.
        (
            ".LOGON tdpid/username,password;\nSELECT 1;\n",
            ".LOGON tdpid/username,password",
        ),
        # No arguments.
        (".LOGOFF;\nSELECT 1;\n", ".LOGOFF"),
        # Structured `.RUN FILE=` argument.
        (".RUN FILE=POSTING;\nSELECT 1;\n", ".RUN FILE=POSTING"),
    ],
)
def test_bteq_command_and_sql_parse_as_separate_statements(
    teradata_linter: Linter, raw: str, command: str
) -> None:
    """A semicolon-terminated BTEQ command followed by SQL parses cleanly.

    Both the ``bteq_statement`` and the following ``select_statement`` are
    parsed as independent statements with no unparsable sections (see #1673).
    """
    parsed = teradata_linter.parse_string(raw)

    assert not parsed.violations
    statement_types = {
        seg.get_type()
        for seg in parsed.tree.recursive_crawl("bteq_statement", "select_statement")
    }
    assert statement_types == {"bteq_statement", "select_statement"}

    bteq_statements = list(parsed.tree.recursive_crawl("bteq_statement"))
    assert len(bteq_statements) == 1
    assert bteq_statements[0].raw == command


@pytest.mark.parametrize("command", [".LOGON tdpid/username,password", ".LOGOFF"])
def test_bteq_command_does_not_absorb_the_next_line(
    teradata_linter: Linter, command: str
) -> None:
    """A BTEQ dot-command is confined to its own line.

    Regression guard for the newline boundary: a command's opaque arguments must
    stop at the end of its line and never bleed into the following statement,
    whether or not the command has arguments. Without the newline terminator the
    following ``SELECT`` would be silently absorbed into the ``bteq_statement``.
    """
    parsed = teradata_linter.parse_string(f"{command}\nSELECT 1;\n")

    bteq_statements = list(parsed.tree.recursive_crawl("bteq_statement"))
    assert len(bteq_statements) == 1
    # The command stops at the newline; the following line is not part of it.
    assert bteq_statements[0].raw == command
    assert "SELECT" not in bteq_statements[0].raw
