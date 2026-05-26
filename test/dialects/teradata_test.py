"""Tests for the Teradata dialect."""

import pytest

from sqlfluff.core import Linter


@pytest.mark.parametrize(
    "sql",
    [
        ".RUN FILE=POSTING.SQL\n",
        ".RUN FILE=../posting-file.sql\n",
        '.RUN FILE="reports/out summary.txt"\n',
        ".RUN FILE=C:\\reports\\out-summary.txt\n",
        ".EXPORT REPORT FILE=reports/out,summary.txt\n",
    ],
)
def test_teradata_bteq_command_with_arguments_parses(sql):
    """BTEQ dot commands may have arguments after the command keyword."""
    parsed = Linter(dialect="teradata").parse_string(sql)

    assert not [
        violation for violation in parsed.violations if violation.rule_code() == "PRS"
    ]
