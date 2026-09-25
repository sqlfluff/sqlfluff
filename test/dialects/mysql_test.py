"""Tests specific to the MySQL dialect."""

from typing import Callable

import pytest
from _pytest.logging import LogCaptureFixture

from sqlfluff.core import Linter
from sqlfluff.core.errors import SQLParseError


@pytest.mark.parametrize(
    "raw",
    [
        "ELSEIF x = 1 THEN SELECT 1; END IF",
        "ELSE SELECT 1; END IF",
        "x = 0 THEN SELECT 1; END IF",
        "IF x = 0 THEN SELECT 1;",
        "IF x = 0 THEN SELECT 1; ELSE SELECT 2; ELSEIF x = 1 THEN SELECT 3; END IF",
        "IF x = 0 THEN SELECT 1; ELSE SELECT 2; ELSE SELECT 3; END IF",
        "IF x = 0 THEN END IF",
        "IF x = 0 THEN SELECT 1; ELSEIF x = 1 THEN END IF",
        "IF x = 0 THEN SELECT 1; ELSE END IF",
        "IF x = 0 THEN SELECT 1 END IF",
    ],
)
def test_mysql_if_statement_does_not_match_invalid_syntax(
    raw: str,
    caplog: LogCaptureFixture,
    dialect_specific_segment_not_match: Callable,
) -> None:
    """Test that invalid IF statements do not match."""
    dialect_specific_segment_not_match("mysql", "IfExpressionStatement", raw, caplog)


@pytest.mark.parametrize(
    "raw",
    [
        "KILL HARD 5\n",
        "KILL SOFT CONNECTION 5\n",
        "KILL QUERY ID 5\n",
        "KILL USER 'u'@'h'\n",
    ],
)
def test_mysql_kill_rejects_mariadb_only_forms(raw: str) -> None:
    """Test that the MariaDB-only KILL forms do not parse as MySQL."""
    parsed = Linter(dialect="mysql").parse_string(raw)
    assert len(parsed.violations) == 1
    assert isinstance(parsed.violations[0], SQLParseError)
