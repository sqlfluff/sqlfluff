"""Tests for the Teradata dialect."""

from sqlfluff.core import Linter


def test_teradata_bteq_command_with_arguments_parses():
    """BTEQ dot commands may have arguments after the command keyword."""
    parsed = Linter(dialect="teradata").parse_string(".RUN FILE=POSTING\n")

    assert not [violation for violation in parsed.violations if violation.rule_code() == "PRS"]
