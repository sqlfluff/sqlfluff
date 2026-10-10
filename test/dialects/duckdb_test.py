"""Tests for the DuckDB dialect."""

import pytest

from sqlfluff.core import Linter


@pytest.mark.parametrize("kind", ["MACRO", "FUNCTION"])
@pytest.mark.parametrize("temporary", ["", "TEMP ", "TEMPORARY "])
@pytest.mark.parametrize("body", ["a + 1", "TABLE SELECT a AS value"])
def test_create_macro_rejects_replace_if_not_exists(
    kind: str, temporary: str, body: str
) -> None:
    """OR REPLACE and IF NOT EXISTS are mutually exclusive for macros."""
    sql = f"CREATE OR REPLACE {temporary}{kind} IF NOT EXISTS m(a) AS {body};"
    parsed = Linter(dialect="duckdb").parse_string(sql)
    assert parsed.violations
