"""Tests specific to the MariaDB dialect."""

import pytest

from sqlfluff.core import Linter


def _prs_violations(result):
    """Extract parse violations from a lint result."""
    return [v for v in result.violations if v.rule_code() == "PRS"]


def test_mariadb_inline_comment_without_space_is_valid() -> None:
    """MariaDB should accept --comment without a following space (permissive like MySQL)."""
    linter = Linter(dialect="mariadb")
    result = linter.lint_string("--comment\nSELECT 1;\n")

    assert not _prs_violations(result)


def test_mariadb_inline_comment_with_space_is_valid() -> None:
    """MariaDB should accept -- comment with a space."""
    linter = Linter(dialect="mariadb")
    result = linter.lint_string("-- comment\nSELECT 1;\n")

    assert not _prs_violations(result)


def test_mysql_inline_comment_without_space_still_valid() -> None:
    """MySQL behavior is unchanged: --comment without space is valid."""
    linter = Linter(dialect="mysql")
    result = linter.lint_string("--comment\nSELECT 1;\n")

    assert not _prs_violations(result)


@pytest.mark.parametrize(
    "sql",
    [
        "SELECT 1; --trailing comment without space\n",
        "SELECT 1; -- trailing comment with space\n",
        "--comment before statement\nSELECT 1;\n",
        "-- comment before statement\nSELECT 1;\n",
        "SELECT\n--mid-query comment\n1;\n",
    ],
)
def test_mariadb_inline_comment_variants(sql: str) -> None:
    """MariaDB permits -- comments with and without a trailing space in all positions."""
    linter = Linter(dialect="mariadb")
    result = linter.lint_string(sql)

    assert not _prs_violations(result), f"Unexpected parse error for: {sql!r}"
