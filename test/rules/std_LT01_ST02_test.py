"""Tests the python routines within LT04 and ST06."""

import pytest

from sqlfluff.core import FluffConfig, Linter


@pytest.mark.parametrize(
    ["in_sql", "out_sql"],
    [
        (
            """
select
    case
        when ended_at is null or date(ended_at) > current_date()
        then true else false
    end as is_active
from foo
""",
            """
select
    coalesce(ended_at is null or date(ended_at) > current_date(), false) as is_active
from foo
""",
        ),
    ],
)
def test_rules_std_LT01_and_ST02_interaction(in_sql, out_sql) -> None:
    """Test interaction between LT04 and ST06.

    Test sql with two newlines with leading commas expecting trailing.
    """
    # Lint expected rules.
    cfg = FluffConfig.from_string(
        """[sqlfluff]
dialect = ansi
rules = LT01,ST02
"""
    )
    linter = Linter(config=cfg)

    # Return linted/fixed file.
    linted_file = linter.lint_string(in_sql, fix=True)

    # Check expected lint errors are raised.
    assert set([v.rule.code for v in linted_file.violations]) == {"ST02"}

    # Check file is fixed.
    assert linted_file.fix_string()[0] == out_sql
