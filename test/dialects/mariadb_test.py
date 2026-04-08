"""Tests specific to the MariaDB dialect."""

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
