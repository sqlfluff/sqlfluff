"""Tests the python routines within LT03."""

import sqlfluff
from sqlfluff.core import Linter
from sqlfluff.core.config import FluffConfig

EXPECTED_LEADING_MESSAGE = (
    "Found trailing binary operator. Expected only leading near line breaks."
)
EXPECTED_TRAILING_MESSAGE = (
    "Found leading binary operator. Expected only trailing near line breaks."
)


def test__rules__std_LT03_default():
    """Verify that LT03 returns the correct error message for default (trailing)."""
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
    assert "LT03" in [r["code"] for r in result]
    assert EXPECTED_LEADING_MESSAGE in [r["description"] for r in result]


def test__rules__std_LT03_leading():
    """Verify correct error message when leading is used."""
    sql = """
        SELECT
            a,
            b
        FROM foo
        WHERE
            a = 1 AND
            b = 2
    """
    config = FluffConfig(
        configs={"layout": {"type": {"binary_operator": {"line_position": "leading"}}}},
        overrides={"dialect": "ansi"},
    )
    # The sqlfluff.lint API doesn't allow us to pass config so need to do what it does
    linter = Linter(config=config)
    result_records = linter.lint_string_wrapped(sql).as_records()
    result = result_records[0]["violations"]
    assert "LT03" in [r["code"] for r in result]
    assert EXPECTED_LEADING_MESSAGE in [r["description"] for r in result]


def test__rules__std_LT03_trailing():
    """Verify correct error message when trailing is used."""
    sql = """
        SELECT
            a,
            b
        FROM foo
        WHERE
            a = 1
            AND b = 2
    """
    config = FluffConfig(
        configs={
            "layout": {"type": {"binary_operator": {"line_position": "trailing"}}}
        },
        overrides={"dialect": "ansi"},
    )
    # The sqlfluff.lint API doesn't allow us to pass config so need to do what it does
    linter = Linter(config=config)
    result_records = linter.lint_string_wrapped(sql).as_records()
    result = result_records[0]["violations"]
    assert "LT03" in [r["code"] for r in result]
    assert EXPECTED_TRAILING_MESSAGE in [r["description"] for r in result]
