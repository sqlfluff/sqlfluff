"""Tests specific to the T-SQL dialect."""

import pytest

from sqlfluff.core import Linter


@pytest.mark.parametrize(
    "sql",
    [
        pytest.param(
            "SELECT * FROM CONTAINSTABLE ([Table], [Column], 'Search')",
            id="containstable_table_function",
        ),
        pytest.param(
            "SELECT * FROM FREETEXTTABLE ([Table], [Column], 'Search')",
            id="freetexttable_table_function",
        ),
    ],
)
def test_tsql_full_text_table_functions_parse(sql: str) -> None:
    """Full-text table-valued functions should parse in FROM clauses."""
    parsed = Linter(dialect="tsql").parse_string(sql)
    assert not parsed.violations
    assert parsed.tree
    assert "unparsable" not in parsed.tree.type_set()
