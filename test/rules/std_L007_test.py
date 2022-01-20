"""Tests the python routines within L007."""

import sqlfluff
from sqlfluff.core.config import FluffConfig
from sqlfluff.core import Linter

from sqlfluff.rules.L007 import after_description, before_description


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
    result = sqlfluff.lint(sql)
    assert "L007" in [r["code"] for r in result]
    assert after_description in [r["description"] for r in result]


def test__rules__std_L007_after():
    """Verify orrect error message when after is explicitly used."""
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
    # The sqlfluff.lint API doesn't allow us to pass config so need to do what it does
    linter = Linter(config=config)
    result_records = linter.lint_string_wrapped(sql).as_records()
    result = result_records[0]["violations"]
    assert "L007" in [r["code"] for r in result]
    assert after_description in [r["description"] for r in result]


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
    # The sqlfluff.lint API doesn't allow us to pass config so need to do what it does
    linter = Linter(config=config)
    result_records = linter.lint_string_wrapped(sql).as_records()
    result = result_records[0]["violations"]
    assert "L007" in [r["code"] for r in result]
    assert before_description in [r["description"] for r in result]
