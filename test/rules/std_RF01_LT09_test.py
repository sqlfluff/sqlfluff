"""Tests observed conflict between RF01 & LT09.

Root cause was BaseSegment.copy().
"""

from sqlfluff.core import FluffConfig, Linter


def test__rules__std_RF01_LT09_copy() -> None:
    """Tests observed conflict between RF01 & LT09.

    https://github.com/sqlfluff/sqlfluff/issues/5203
    """
    sql = """
SELECT
    DISTINCT `FIELD`
FROM `TABLE`;
"""
    cfg = FluffConfig.from_kwargs(
        dialect="mysql",
        rules=["RF01", "LT09"],
    )
    result = Linter(config=cfg).lint_string(sql)
    for violation in result.violations:
        assert "Unexpected exception" not in violation.description
    assert len(result.violations) == 1
    only_violation = result.violations[0]
    assert only_violation.rule_code() == "LT09"
