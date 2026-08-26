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
        # A dot-command with opaque arguments must not consume the following
        # statement: its arguments are bounded by the end of its own line.
        (
            ".LOGON tdpid/username,password\nSELECT 1;\n",
            ".LOGON tdpid/username,password",
        ),
        # A dot-command with no arguments must likewise stop at the newline
        # rather than absorbing the next line.
        (".LOGOFF\nSELECT 1;\n", ".LOGOFF"),
    ],
)
def test_bteq_command_is_bounded_to_its_line(
    teradata_linter: Linter, raw: str, command: str
) -> None:
    """BTEQ dot-commands are confined to a single line.

    Regression test for the newline boundary: opaque command arguments must not
    bleed across the end of the line into the following statement (see #1673).
    """
    parsed = teradata_linter.parse_string(raw)
    bteq_statements = list(parsed.tree.recursive_crawl("bteq_statement"))

    assert len(bteq_statements) == 1
    assert bteq_statements[0].raw == command
    # The following statement is not absorbed into the BTEQ command.
    assert "SELECT" not in bteq_statements[0].raw
