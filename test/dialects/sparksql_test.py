"""Tests specific to the SparkSQL dialect."""

import pytest

from sqlfluff.core import FluffConfig, Linter


@pytest.mark.parametrize(
    "sql,should_parse",
    [
        # VARCHAR requires mandatory length
        ("CREATE TABLE t (col VARCHAR(100))", True),
        ("CREATE TABLE t (col VARCHAR)", False),
        # CHAR requires mandatory length
        ("CREATE TABLE t (col CHAR(10))", True),
        ("CREATE TABLE t (col CHAR)", False),
        # CHARACTER requires mandatory length
        ("CREATE TABLE t (col CHARACTER(20))", True),
        ("CREATE TABLE t (col CHARACTER)", False),
        # DECIMAL has optional precision/scale
        ("CREATE TABLE t (col DECIMAL)", True),
        ("CREATE TABLE t (col DECIMAL(10))", True),
        ("CREATE TABLE t (col DECIMAL(10, 2))", True),
        # NUMERIC has optional precision/scale
        ("CREATE TABLE t (col NUMERIC)", True),
        ("CREATE TABLE t (col NUMERIC(10))", True),
        ("CREATE TABLE t (col NUMERIC(10, 2))", True),
        # DEC has optional precision/scale
        ("CREATE TABLE t (col DEC)", True),
        ("CREATE TABLE t (col DEC(10))", True),
        ("CREATE TABLE t (col DEC(10, 2))", True),
    ],
)
def test_sparksql_char_varchar_mandatory_length(sql: str, should_parse: bool):
    """Test that CHAR/VARCHAR require mandatory length but DECIMAL/NUMERIC don't."""
    config = FluffConfig.from_root(overrides={"dialect": "sparksql"})
    linter = Linter(config=config)
    result = linter.lint_string(sql)
    
    has_parsing_errors = any(v.rule_code() == "PRS" for v in result.violations)
    
    if should_parse:
        assert not has_parsing_errors, (
            f"Expected SQL to parse successfully but got parsing errors: {sql}"
        )
    else:
        assert has_parsing_errors, (
            f"Expected SQL to fail parsing but it parsed successfully: {sql}"
        )
