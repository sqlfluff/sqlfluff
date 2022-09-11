"""Tests the python routines within L009 and L052."""
from textwrap import dedent

from sqlfluff.core import FluffConfig
from sqlfluff.core import Linter


def test__rules__std_L014_leading_non_capitalizable_characters() -> None:
    """Test the capitalisation_policy is correctly inferred when string starts with non-capitalizable characters """
    # Test sql file where first column has leading underscore
    sql = dedent("""
    select
        _a,
        b
    from foo
    """)

    cfg = FluffConfig(overrides={"dialect": "ansi"})
    linter = Linter(config=cfg)

    # Return linted/fixed file.
    linted_file = linter.lint_string(sql)

    # Check expected lint errors are raised.
    assert "L014" not in [v.rule.code for v in linted_file.violations]
