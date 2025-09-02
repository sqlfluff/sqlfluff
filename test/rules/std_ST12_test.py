"""Tests for ST12 (structure.consecutive_semicolons)."""

import pytest

from sqlfluff.core import FluffConfig, Linter

SQL_SIMPLE = "SELECT 1;;\nSELECT 2;\n;;SELECT 3;"
SQL_ONLY_SEMICOLONS = ";;;;\n; ; ;\n;\n"


CASES = [
    ("SELECT 1;", 0),
    (";SELECT 1;", 0),  # single leading
    (";;SELECT 1;", 1),
    ("SELECT 1;;;", 1),
    ("SELECT 1; ; ;", 1),
    (";;;;", 1),  # one run
    ("; ; ;", 1),  # spaced run
]


@pytest.mark.parametrize(
    "dialect",
    [
        "ansi",
        "postgres",
        "snowflake",
        "bigquery",
        "tsql",
        "mysql",
        "vertica",
        "databricks",
    ],
)
def test_st12_basic_counts(dialect):
    """Parameterized simple patterns produce expected violation counts."""
    for sql, expected in CASES:
        cfg = FluffConfig(overrides={"dialect": dialect, "rules": "ST12"})
        lnt = Linter(config=cfg)
        res = lnt.lint_string(sql)
        assert (
            res.num_violations() == expected
        ), f"Dialect {dialect} SQL {sql!r}"  # noqa: PT009


@pytest.mark.parametrize(
    "dialect",
    [
        "ansi",
        "postgres",
        "snowflake",
        "bigquery",
        "tsql",
        "mysql",
        "vertica",
        "databricks",
    ],
)
def test_st12_runs_and_positions_complex(dialect):
    """Complex sample: parses cleanly, groups detected once each, no fixes."""
    complex_sql = (
        ";;SELECT col1 FROM tbl1;\n"
        "SELECT col2 FROM tbl2;;\n"
        "SELECT col3 FROM tbl3;;;;SELECT col4 FROM tbl4;\n"
        "; ; ;SELECT col5 FROM tbl5;   ;  ;\n"
        "SELECT col6 FROM tbl6;;;;;;\n"
        "SELECT col6 FROM tbl6;;;\n"
    )
    cfg = FluffConfig(overrides={"dialect": dialect, "rules": "ST12"})
    lnt = Linter(config=cfg)
    parsed = lnt.parse_string(complex_sql)
    assert not list(parsed.tree.recursive_crawl("unparsable"))
    linted = lnt.lint_string(complex_sql)
    violations = [v for v in linted.get_violations() if v.rule_code() == "ST12"]
    # Expected groups (7) mirroring original logic.
    assert len(violations) == 7
    assert len({(v.line_no, v.line_pos) for v in violations}) == 7
    fixed_str, changed = linted.fix_string()
    assert fixed_str == complex_sql and changed is False


def test_st12_invocation_canonical():
    """Invoking ST12 directly works and yields expected violations."""
    sql = SQL_SIMPLE
    cfg = FluffConfig(overrides={"dialect": "tsql", "rules": "ST12"})
    lnt = Linter(config=cfg)
    res = lnt.lint_string(sql)
    codes = {v.rule_code() for v in res.get_violations()}
    assert codes == {"ST12"}
    assert res.num_violations() == 2
