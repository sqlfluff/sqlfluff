"""Tests specific to the MySQL dialect."""

from typing import Callable

import pytest
from _pytest.logging import LogCaptureFixture


@pytest.mark.parametrize(
    "raw",
    [
        "ELSEIF x = 1 THEN SELECT 1; END IF",
        "ELSE SELECT 1; END IF",
        "x = 0 THEN SELECT 1; END IF",
        "IF x = 0 THEN SELECT 1;",
        "IF x = 0 THEN SELECT 1; ELSE SELECT 2; ELSEIF x = 1 THEN SELECT 3; END IF",
        "IF x = 0 THEN SELECT 1; ELSE SELECT 2; ELSE SELECT 3; END IF",
    ],
)
def test_mysql_if_statement_does_not_match_invalid_clause_order(
    raw: str,
    caplog: LogCaptureFixture,
    dialect_specific_segment_not_match: Callable,
) -> None:
    """Test that invalid IF statement forms do not match."""
    dialect_specific_segment_not_match("mysql", "IfExpressionStatement", raw, caplog)
