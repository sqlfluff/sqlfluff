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


@pytest.mark.parametrize("dialect", ["ansi", "bigquery", "postgres", "duckdb"])
@pytest.mark.parametrize("rules", ["LT07", "LT02,LT07", "all"])
@pytest.mark.parametrize("indent", [2, 4])
def test_many_cte_closing_brackets_fixed(dialect, rules, indent):
    """Fix all CTE brackets without exhausting the default fix-loop limit."""
    queries = ["SELECT a FROM foo"] + [f"SELECT a FROM cte_{idx}" for idx in range(11)]
    ctes = ",\n".join(
        f"cte_{idx} AS (\n{' ' * indent}{query})" for idx, query in enumerate(queries)
    )
    sql = f"WITH {ctes}\n\nSELECT * FROM cte_11\n"
    linter = Linter(config=FluffConfig(overrides={"dialect": dialect, "rules": rules}))
    linted = linter.lint_string(sql, fix=True)
    expected_indent = indent if rules == "LT07" else 4
    expected_ctes = (",\n\n" if rules == "all" else ",\n").join(
        f"cte_{idx} AS (\n{' ' * expected_indent}{query}\n)"
        for idx, query in enumerate(queries)
    )
    expected_sql = f"WITH {expected_ctes}\n\nSELECT * FROM cte_11\n"
    fixed_sql, _ = linted.fix_string()
    assert fixed_sql == expected_sql
    assert len(linted.get_violations(rules="LT07")) == 12
    assert not linter.lint_string(fixed_sql).get_violations()
    assert linter.lint_string(fixed_sql, fix=True).fix_string()[0] == fixed_sql


@pytest.mark.parametrize("exclude_lt07", [True, False])
@pytest.mark.parametrize("nested_cte", [True, False])
@pytest.mark.parametrize("indent", [6, 8])
def test_pipe_cte_closing_bracket_rule_ownership(exclude_lt07, nested_cte, indent):
    """LT02 retains pipe CTE brackets, including around an ordinary nested CTE."""
    body = "WITH u AS (\n            SELECT 2)\n\n" if nested_cte else ""
    query = "SELECT * FROM u" if nested_cte else "SELECT 2"
    sql = (
        "SELECT 1\n|> WITH\n    t AS (\n"
        + ("        " + body if body else "")
        + " " * indent
        + query
        + ")\n|> SELECT * FROM t\n"
    )
    linter = Linter(
        config=FluffConfig(
            overrides={
                "dialect": "bigquery",
                "rules": "LT02,LT07",
                "exclude_rules": "LT07" if exclude_lt07 else "",
            }
        )
    )
    linted = linter.lint_string(sql, fix=True)
    codes = {violation.rule_code() for violation in linted.get_violations()}
    assert "LT02" in codes
    assert ("LT07" in codes) == (nested_cte and not exclude_lt07)
    expected_body = "        " + body if body else ""
    if nested_cte and not exclude_lt07:
        expected_body = expected_body.replace("SELECT 2)", "SELECT 2\n        )")
    expected_sql = (
        "SELECT 1\n|> WITH\n    t AS (\n"
        + expected_body
        + "        "
        + query
        + "\n    )\n|> SELECT * FROM t\n"
    )
    fixed_sql, _ = linted.fix_string()
    assert fixed_sql == expected_sql
    assert not linter.lint_string(fixed_sql).get_violations()
    assert linter.lint_string(fixed_sql, fix=True).fix_string()[0] == fixed_sql
