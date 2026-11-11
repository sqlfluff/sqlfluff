"""Test that LT07 controls CTE closing bracket line breaks independently of LT02."""

import pytest

from sqlfluff.core import FluffConfig, Linter


@pytest.mark.parametrize("dialect", ["ansi", "bigquery", "postgres", "duckdb"])
@pytest.mark.parametrize("exclude_lt07", [True, False])
@pytest.mark.parametrize("indent", [2, 4])
def test_cte_closing_bracket_rule_ownership(dialect, exclude_lt07, indent):
    """Excluding LT07 preserves inline brackets; enabling it fixes them once."""
    sql = f"WITH zoo AS (\n{' ' * indent}SELECT a FROM foo)\n\nSELECT * FROM zoo\n"
    config = FluffConfig(
        overrides={
            "dialect": dialect,
            "exclude_rules": "layout.cte_bracket" if exclude_lt07 else "",
        }
    )
    linter = Linter(config=config)
    linted = linter.lint_string(sql, fix=True)
    expected_codes = [] if indent == 4 else ["LT02"]
    if not exclude_lt07:
        expected_codes.append("LT07")
    assert sorted(violation.rule_code() for violation in linted.get_violations()) == (
        expected_codes
    )
    fixed_sql, _ = linted.fix_string()
    expected_sql = "WITH zoo AS (\n    SELECT a FROM foo)\n\nSELECT * FROM zoo\n"
    if not exclude_lt07:
        expected_sql = expected_sql.replace("foo)", "foo\n)")
    assert fixed_sql == expected_sql
    assert not linter.lint_string(fixed_sql).get_violations()
    assert linter.lint_string(fixed_sql, fix=True).fix_string()[0] == fixed_sql
