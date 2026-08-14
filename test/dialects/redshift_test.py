"""Redshift dialect-specific parser rejection tests.

Positive/valid-SQL cases belong in the SQL/YAML parse fixtures under
test/fixtures/dialects/redshift/ per project convention.
"""

import pytest

from sqlfluff.core import Linter


def _violations(sql: str) -> list:
    """Return all parse errors, including unparsable nodes in the tree."""
    parsed = Linter(dialect="redshift").parse_string(sql)
    violations: list = list(parsed.violations)
    if parsed.tree:
        violations += list(parsed.tree.recursive_crawl("unparsable"))
    return violations


@pytest.mark.parametrize(
    "sql",
    [
        pytest.param(
            "SELECT *, a, EXCLUDE x FROM tbl;",
            id="comma_before_unbracketed_exclude",
        ),
        pytest.param(
            "SELECT col1, EXCLUDE col2 FROM tbl;",
            id="comma_before_unbracketed_exclude_no_star",
        ),
    ],
)
def test_select_exclude_rejects_comma_before_clause(sql: str) -> None:
    """A comma before SELECT EXCLUDE must not parse as a select item."""
    assert _violations(sql), f"Expected violations but got none for:\n{sql}"
