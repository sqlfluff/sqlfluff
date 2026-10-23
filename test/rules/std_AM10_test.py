"""Integration tests for INSERT/SELECT column counts."""

import pytest

from sqlfluff.core import Linter


@pytest.mark.parametrize(
    "dialect",
    [
        "ansi",
        "bigquery",
        "clickhouse",
        "duckdb",
        "hive",
        "mysql",
        "oracle",
        "postgres",
        "redshift",
        "snowflake",
        "sparksql",
        "sqlite",
        "tsql",
    ],
)
@pytest.mark.parametrize(
    "columns,select_list,expected",
    [
        ("a", "x, y", 1),
        ("a, b", "x", 1),
        ("a, b", "x, y", 0),
        ("a, b", "*", 0),
    ],
)
def test__rules__std_AM10_dialects(dialect, columns, select_list, expected):
    """Check the common positional form across dialects without modifying SQL."""
    sql = f"INSERT INTO dst ({columns}) SELECT {select_list} FROM src;"
    linter = Linter(dialect=dialect, rules=["AM10"])
    result = linter.lint_string(sql, fix=True)
    violations = result.get_violations()
    assert [violation.rule_code() for violation in violations] == ["AM10"] * expected
    if expected:
        assert violations[0].line_no == 1
        assert violations[0].line_pos == sql.index("SELECT") + 1
        assert not violations[0].fixable
    assert result.fix_string()[0] == sql


def test__rules__std_AM10_reports_each_insert():
    """Keep independent INSERT statements separate and report both counts."""
    result = Linter(dialect="ansi", rules=["AM10"]).lint_string(
        "INSERT INTO dst (a) SELECT x, y FROM src;\n"
        "INSERT INTO dst (a, b) SELECT x FROM src;\n"
    )
    violations = result.get_violations()
    assert [violation.rule_code() for violation in violations] == ["AM10", "AM10"]
    assert [violation.line_no for violation in violations] == [1, 2]
    assert violations[0].desc() == (
        "INSERT target column count (1) does not match SELECT column count (2)."
    )
    assert violations[1].desc() == (
        "INSERT target column count (2) does not match SELECT column count (1)."
    )


def test__rules__std_AM10_incomplete_source():
    """Do not infer column counts from a partially parsed SELECT source."""
    result = Linter(dialect="ansi", rules=["AM10"]).lint_string(
        "INSERT INTO dst (a) SELECT x, y FROM src WHERE x +;"
    )
    assert not any(
        violation.rule_code() == "AM10" for violation in result.get_violations()
    )
