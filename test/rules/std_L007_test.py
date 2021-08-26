"""Tests the python routines within L007."""

import sqlfluff
from sqlfluff.core.config import FluffConfig
from sqlfluff.core import Linter


def test__rules__std_L007_default():
    """Verify that L007 returns the correct error message for default (after)."""
    sql = """
        SELECT
            a,
            b
        FROM foo
        WHERE
            a = 1 AND
            b = 2
    """
    config = FluffConfig()
    result = sqlfluff.lint(sql)
    assert "L007" in [r["code"] for r in result]
    assert "Operators near newlines should be after, not before the newline" in [
        r["description"] for r in result
    ]


def test__rules__std_L007_after():
    """Verify that L007 returns the correct error message when after is explicitly used."""
    sql = """
        SELECT
            a,
            b
        FROM foo
        WHERE
            a = 1 AND
            b = 2
    """
    config = FluffConfig(configs={"rules": {"L007": {"operator_new_lines": "after"}}})
    linter = Linter(config=config)
    result_records = linter.lint_string_wrapped(sql).as_records()
    result = result_records[0]["violations"]
    assert "L007" in [r["code"] for r in result]
    assert "Operators near newlines should be after, not before the newline" in [
        r["description"] for r in result
    ]


def test__rules__std_L007_before():
    """Verify that L007 returns the correct error message when before is used."""
    sql = """
        SELECT
            a,
            b
        FROM foo
        WHERE
            a = 1
            AND b = 2
    """
    config = FluffConfig(configs={"rules": {"L007": {"operator_new_lines": "before"}}})
    linter = Linter(config=config)
    result_records = linter.lint_string_wrapped(sql).as_records()
    result = result_records[0]["violations"]
    assert "L007" in [r["code"] for r in result]
    assert "Operators near newlines should be before, not after the newline" in [
        r["description"] for r in result
    ]
