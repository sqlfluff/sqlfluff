"""Focused Oracle parser regression tests."""

import pytest

from sqlfluff.core import Linter


@pytest.mark.xfail(
    strict=True,
    reason="Known Oracle CREATE VIEW division regression tracked in #8373",
)
def test_oracle_create_view_bare_division_parses() -> None:
    """Bare division in CREATE VIEW SELECT should not become a slash executor."""
    parsed = Linter(dialect="oracle").parse_string(
        "CREATE VIEW myview AS\nSELECT 1 / 100 AS z FROM dual;"
    )
    parsing_errors = [v for v in parsed.violations if v.rule_code() == "PRS"]

    assert not parsing_errors
