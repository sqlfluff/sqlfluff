"""Tests for ST12 (structure.consecutive_semicolons)."""

import sqlfluff
from sqlfluff.core import Linter
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


def _databricks_config(ignore_command_cells: bool) -> FluffConfig:
    """Build a databricks FluffConfig with the ST12 command cell toggle set."""
    cfg = FluffConfig(overrides={"dialect": "databricks", "rules": "ST12"})
    cfg.set_value(
        [
            "rules",
            "structure.consecutive_semicolons",
            "ignore_databricks_command_cells",
        ],
        ignore_command_cells,
    )
    return cfg


def test__rules__std_ST12_databricks_command_cell_default_flags():
    """By default a semicolon followed by a command cell is a consecutive run.

    The databricks dialect lexes ``-- COMMAND ----------`` as a
    ``statement_terminator``. With the default configuration this delimiter is
    treated like any other terminator, so a trailing semicolon immediately
    before it is reported as a consecutive terminator run.
    """
    sql = (
        "-- Databricks notebook source\n\n"
        "SELECT COL1 FROM TABLE1;\n\n"
        "-- COMMAND ----------\n\n"
        "SELECT COL2 FROM TABLE2\n"
    )
    cfg = _databricks_config(ignore_command_cells=False)
    result = sqlfluff.lint(sql, config=cfg)
    violations = [r for r in result if r["code"] == "ST12"]
    assert len(violations) == 1


def test__rules__std_ST12_databricks_command_cell_ignored_when_enabled():
    """Enabling the toggle stops command cells from counting as terminators."""
    sql = (
        "-- Databricks notebook source\n\n"
        "SELECT COL1 FROM TABLE1;\n\n"
        "-- COMMAND ----------\n\n"
        "SELECT COL2 FROM TABLE2\n"
    )
    cfg = _databricks_config(ignore_command_cells=True)
    result = sqlfluff.lint(sql, config=cfg)
    violations = [r for r in result if r["code"] == "ST12"]
    assert violations == []


def test__rules__std_ST12_databricks_command_cell_is_still_terminator():
    """The command cell remains a statement_terminator even when ignored.

    Parsing must be unaffected by the rule configuration: each notebook cell is
    still parsed as a separate statement terminated by the command delimiter.
    """

    sql = (
        "-- Databricks notebook source\n\n"
        "SELECT COL1 FROM TABLE1\n\n"
        "-- COMMAND ----------\n\n"
        "SELECT COL2 FROM TABLE2\n"
    )
    cfg = _databricks_config(ignore_command_cells=True)
    parsed = Linter(config=cfg).parse_string(sql)
    terminators = [
        seg.raw for seg in parsed.tree.recursive_crawl("statement_terminator")
    ]
    assert any(raw.strip().startswith("-- COMMAND") for raw in terminators)


def test__rules__std_ST12_databricks_real_duplicates_still_flagged_when_ignored():
    """Genuine consecutive semicolons are still flagged when the toggle is on."""
    sql = (
        "-- Databricks notebook source\n\n"
        "SELECT COL1 FROM TABLE1;;\n\n"
        "-- COMMAND ----------\n\n"
        "SELECT COL2 FROM TABLE2\n"
    )
    cfg = _databricks_config(ignore_command_cells=True)
    result = sqlfluff.lint(sql, config=cfg)
    violations = [r for r in result if r["code"] == "ST12"]
    assert len(violations) == 1


def test__rules__std_ST12_databricks_consecutive_command_cells_ignored():
    """A pair of adjacent command cells (empty cell) is ignored when enabled."""
    sql = (
        "-- Databricks notebook source\n\n"
        "SELECT COL1 FROM TABLE1\n\n"
        "-- COMMAND ----------\n\n"
        "-- COMMAND ----------\n\n"
        "SELECT COL2 FROM TABLE2\n"
    )
    cfg = _databricks_config(ignore_command_cells=True)
    result = sqlfluff.lint(sql, config=cfg)
    violations = [r for r in result if r["code"] == "ST12"]
    assert violations == []
