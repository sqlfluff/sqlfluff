"""Tests for ST12 (structure.consecutive_semicolons)."""

import sqlfluff
from sqlfluff.core.config import FluffConfig


def test__rules__std_ST12_basic_patterns():
    """Test basic consecutive semicolon patterns."""
    # Test cases: (SQL, expected_violation_count)
    cases = [
        ("SELECT 1;", 0),  # Single semicolon - no violation
        (";SELECT 1;", 0),  # Leading semicolon - no violation
        (";;SELECT 1;", 1),  # Double leading - violation
        ("SELECT 1;;;", 1),  # Triple trailing - violation
        ("SELECT 1; ; ;", 1),  # Spaced consecutive - violation
        ("SELECT 1;;;;", 1),  # Many consecutive - violation
    ]

    for sql, expected_count in cases:
        result = sqlfluff.lint(sql, rules=["ST12"])
        actual_count = len([r for r in result if r["code"] == "ST12"])
        assert actual_count == expected_count, f"SQL: {sql!r}"


def test__rules__std_ST12_complex_multistatement():
    """Test complex multi-statement scenarios."""
    sql = (
        ";;SELECT col1 FROM tbl1;\n"
        "SELECT col2 FROM tbl2;;\n"
        "SELECT col3 FROM tbl3;;;;SELECT col4 FROM tbl4;\n"
        "; ; ;SELECT col5 FROM tbl5;   ;  ;\n"
        "SELECT col6 FROM tbl6;;;;;;\n"
        "SELECT col6 FROM tbl6;;;\n"
    )

    result = sqlfluff.lint(sql, rules=["ST12"])
    violations = [r for r in result if r["code"] == "ST12"]

    # Should detect 7 distinct runs of consecutive semicolons
    assert len(violations) == 7
    # Each violation should be at a unique position
    positions = {(v["start_line_no"], v["start_line_pos"]) for v in violations}
    assert len(positions) == 7


def test__rules__std_ST12_fix_functionality():
    """Test that ST12 fixes work correctly."""
    sql = "SELECT 1;; SELECT 2;;; SELECT 3;"

    result = sqlfluff.fix(sql, rules=["ST12"])

    # Should have made changes
    assert result != sql
    # Should have fewer semicolons
    assert result.count(";") < sql.count(";")
    # Should have no violations after fixing
    fixed_violations = sqlfluff.lint(result, rules=["ST12"])
    assert len(fixed_violations) == 0


def test__rules__std_ST12_whitespace_handling():
    """Test that whitespace between semicolons is handled correctly."""
    sql = "SELECT 1;\n\n;SELECT 2;"
    result = sqlfluff.lint(sql, rules=["ST12"])
    violations = [r for r in result if r["code"] == "ST12"]

    # Semicolons separated by newlines should still be flagged
    assert len(violations) == 1


def test__rules__std_ST12_no_semicolon():
    """Test that no semicolon results in no violations."""
    sql = "SELECT 1"
    result = sqlfluff.lint(sql, rules=["ST12"])
    violations = [r for r in result if r["code"] == "ST12"]

    # No semicolons means no violations
    assert len(violations) == 0


def test__rules__std_ST12_comments_break_runs():
    """Test that comments between semicolons break consecutive runs."""
    sql = "SELECT 1; /* comment */ ; SELECT 2;"
    result = sqlfluff.lint(sql, rules=["ST12"])
    violations = [r for r in result if r["code"] == "ST12"]

    # Comments should break the run, so no violations
    assert len(violations) == 0


def test__rules__std_ST12_templated_loop_no_false_positive():
    """Templated loops rendering full statements should not trigger ST12."""
    sql = """
    {% for i in range(3) %}
    SELECT {{ i }};
    {% endfor %}
    """
    cfg = FluffConfig(overrides={"dialect": "ansi", "templater": "jinja"})
    result = sqlfluff.lint(sql, rules=["ST12"], config=cfg)
    violations = [r for r in result if r["code"] == "ST12"]
    assert violations == []


def test__rules__std_ST12_templated_consecutive_semicolons_detected():
    """Actual consecutive semicolons in templated output must still be flagged."""
    sql = """
    {% for _ in range(2) %}
    ;SELECT 1;;
    {% endfor %}
    """
    cfg = FluffConfig(overrides={"dialect": "ansi", "templater": "jinja"})
    result = sqlfluff.lint(sql, rules=["ST12"], config=cfg)
    violations = [r for r in result if r["code"] == "ST12"]
    assert len(violations) == 1
