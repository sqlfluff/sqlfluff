"""Tests for TQ02 (tsql.consecutive_semicolons).

Coverage aims:
* Parsing: complex semicolon patterns produce no unparsables.
* Detection: each adjacent run (len >=2) is a violation; spaced singles aren't.
* Positioning: each group is reported once; rule provides no fixes.
* Context: detection also works inside a stored procedure body.
"""

import pytest

from sqlfluff.core import FluffConfig, Linter

# Shared SQL Fixtures
SIMPLE = "SELECT 1;;\nSELECT 2;\n;;SELECT 3;"  # multiple double-semicolon patterns
COMPLEX = (
    ";;SELECT col1 FROM tbl1;\n"
    "SELECT col2 FROM tbl2;;\n"
    "SELECT col3 FROM tbl3;;;;SELECT col4 FROM tbl4;\n"
    "; ; ;SELECT col5 FROM tbl5;   ;  ;\n"
    "SELECT col6 FROM tbl6;;;;;;\n"
    "SELECT col6 FROM tbl6;GO;GO;;\n"
)


def lint(raw: str, rules="tsql.consecutive_semicolons"):
    """Helper to lint a raw SQL string with the TSQL dialect and given rules."""
    cfg = FluffConfig(overrides={"dialect": "tsql", "rules": rules})
    lnt = Linter(config=cfg)
    return lnt.lint_string(raw)


def test_tsql_tq02_basic():
    """Two separate double-semicolon groups detected in simple sample."""
    res = lint(SIMPLE)
    assert res.num_violations() == 2
    descs = [v.desc() for v in res.get_violations()]
    assert all("Consecutive semicolons detected" in d for d in descs)


@pytest.mark.parametrize(
    "sql,expected",
    [
        ("SELECT 1;", 0),
        (";SELECT 1;", 0),  # single leading semicolon not a violation
        (";;SELECT 1;", 1),
        ("SELECT 1;;;", 1),
        ("SELECT 1; ; ;", 1),  # whitespace-separated run now considered a violation
    ],
)
def test_tsql_tq02_param(sql, expected):
    """Parameterized counts for various adjacent/non-adjacent semicolon patterns."""
    res = lint(sql)
    assert res.num_violations() == expected


def test_tsql_tq02_positions_parse_and_no_fix():
    """Complex sample: parses cleanly, groups detected, distinct positions, no fixes."""
    # Parse to assert there are no unparsables in complex semicolon scenarios.
    cfg = FluffConfig(overrides={"dialect": "tsql", "rules": "TQ02"})
    lnt = Linter(config=cfg)
    parsed = lnt.parse_string(COMPLEX)
    unparsables = list(parsed.tree.recursive_crawl("unparsable"))
    assert not unparsables, f"Unexpected unparsables: {unparsables}"
    linted = lnt.lint_string(COMPLEX)
    violations = [v for v in linted.get_violations() if v.rule_code() == "TQ02"]
    # Expected groups (whitespace-only separators also count now):
    # line1 leading ';;'
    # line2 trailing ';;'
    # line3 middle ';;;;'
    # line4 spaced singles before SELECT col5: '; ; ;'
    # line4 spaced singles after col5 stmt before final semicolon: ';  ;'
    # line5 trailing ';;;;;;'
    # line6 ';;' after second GO
    assert len(violations) == 7
    assert len({(v.line_no, v.line_pos) for v in violations}) == 7
    fixed_str, changed = linted.fix_string()
    assert fixed_str == COMPLEX and changed is False


def test_tsql_tq02_inside_procedure():
    """Consecutive semicolons are detected inside a stored procedure body.

    Ensures the rule still fires correctly within procedural T-SQL blocks and
    that parsing produces no unparsable segments.
    """
    sql = (
        "CREATE PROCEDURE dbo.MyProc AS\n"
        "BEGIN\n"
        "    SELECT 1;;\n"  # one double-semicolon group
        "    SELECT 2;\n"
        "    ;;SELECT 3;\n"  # second group: leading ;; before a statement
        "END;"
    )
    cfg = FluffConfig(overrides={"dialect": "tsql", "rules": "TQ02"})
    lnt = Linter(config=cfg)
    parsed = lnt.parse_string(sql)
    unparsables = list(parsed.tree.recursive_crawl("unparsable"))
    assert not unparsables, f"Unexpected unparsables in procedure: {unparsables}"
    linted = lnt.lint_string(sql)
    violations = [v for v in linted.get_violations() if v.rule_code() == "TQ02"]
    assert len(violations) == 2
