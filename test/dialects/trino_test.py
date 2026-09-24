"""Tests for the Trino dialect."""

import pytest

from sqlfluff.core import Linter


@pytest.mark.parametrize("prefix", ["EXPLAIN", "EXPLAIN (TYPE IO)", "EXPLAIN ANALYZE"])
def test_trino_explain_merge(prefix: str) -> None:
    """MERGE is an explainable statement, including with options or ANALYZE."""
    parsed = Linter(dialect="trino").parse_string(
        f"{prefix} MERGE INTO target USING source ON target.id = source.id "
        "WHEN MATCHED THEN DELETE;"
    )
    assert not parsed.violations


@pytest.mark.parametrize(
    "command", ["ROLES", "CURRENT ROLES", "ROLE GRANTS", "SCHEMAS"]
)
@pytest.mark.parametrize("preposition", ["FROM", "IN"])
@pytest.mark.parametrize("catalog", ["hive.sales", '"hive"."sales"'])
def test_trino_show_rejects_qualified_catalogs(
    command: str, preposition: str, catalog: str
) -> None:
    """SHOW catalog operands accept one identifier, not qualified names."""
    parsed = Linter(dialect="trino").parse_string(
        f"SHOW {command} {preposition} {catalog};"
    )
    assert parsed.violations


@pytest.mark.parametrize(
    "command", ["ROLES", "CURRENT ROLES", "ROLE GRANTS", "SCHEMAS"]
)
@pytest.mark.parametrize("preposition", ["FROM", "IN"])
@pytest.mark.parametrize("catalog", ["hive", '"hive.sales"'])
def test_trino_show_accepts_single_catalog_identifiers(
    command: str, preposition: str, catalog: str
) -> None:
    """A quoted identifier containing a dot is still one catalog name."""
    parsed = Linter(dialect="trino").parse_string(
        f"SHOW {command} {preposition} {catalog};"
    )
    assert not parsed.violations
