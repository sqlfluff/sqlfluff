"""Tests interaction of ST01 with other rules (e.g. reflow rules)."""

import pytest

from sqlfluff.core import FluffConfig, Linter


@pytest.mark.parametrize(
    ["in_sql", "out_sql"],
    [
        (
            """SELECT
    CASE
        WHEN name = 'cat' THEN 'meow'
        WHEN name = 'dog' THEN 'woof'
        ELSE /* keep default */ NULL
    END
FROM x;
""",
            """SELECT
    CASE
        WHEN name = 'cat' THEN 'meow'
        WHEN name = 'dog' THEN 'woof'
        /* keep default */
    END
FROM x;
""",
        ),
        (
            """SELECT
    CASE
        WHEN name = 'cat' THEN 'meow'
        WHEN name = 'dog' THEN 'woof'
        ELSE -- keep default
            NULL
    END
FROM x;
""",
            """SELECT
    CASE
        WHEN name = 'cat' THEN 'meow'
        WHEN name = 'dog' THEN 'woof'
        -- keep default
    END
FROM x;
""",
        ),
    ],
)
def test_rules_std_ST01_preserve_comments_end_to_end(in_sql: str, out_sql: str) -> None:
    """Test ST01 comment preservation with all rules / reflow enabled.

    Ensures that when comments inside redundant ELSE NULL clauses are preserved,
    the subsequent reflow passes correctly indent and format the comment without
    causing parse errors or unexpected lint violations.
    """
    cfg = FluffConfig.from_string(
        """[sqlfluff]
dialect = ansi
"""
    )
    linter = Linter(config=cfg)

    # Return linted/fixed file.
    linted_file = linter.lint_string(in_sql, fix=True)

    # Check that ST01 violation is raised.
    assert "ST01" in [v.rule_code() for v in linted_file.violations]

    # Check file is fixed to expected SQL.
    assert linted_file.fix_string()[0] == out_sql

    # Check fixed output is clean and idempotent.
    recheck = linter.lint_string(out_sql)
    assert not [v for v in recheck.violations if v.rule_code() == "PRS"]
    assert len(recheck.violations) == 0
