"""Tests for the Trino dialect."""

import pytest

from sqlfluff.core import Linter


@pytest.mark.parametrize(
    "sql",
    [
        "SHOW FUNCTIONS FROM;",
        "SHOW FUNCTIONS LIKE 123;",
        "SHOW FUNCTIONS ESCAPE '$';",
        "SHOW STATS motor;",
        "SHOW STATS FOR ();",
        "SHOW STATS FOR SELECT * FROM motor;",
        "DESCRIBE;",
        "DESCRIBE TABLE motor;",
        "DESC INPUT prepared_query;",
    ],
)
def test_trino_show_describe_invalid(sql):
    """Reject incomplete statements and invalid SHOW clause combinations."""
    parsed = Linter(dialect="trino").parse_string(sql)
    assert any(violation.rule_code() == "PRS" for violation in parsed.violations)
