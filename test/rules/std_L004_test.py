"""Tests the python routines within L004."""
from sqlfluff.testing.rules import assert_rule_fail_in_sql, dedent, lint

RULE = "L004"


def test_indented_comments_default_config() -> None:
    """It's not visible to bare eye, but here tab indent is replaced with spaces.

    Lint fails after fixing due to the tabs that come before the comments.
    That is left unfixable for now, as explained in:
    https://github.com/sqlfluff/sqlfluff/pull/590#issuecomment-739484190
    """
    fail_str = dedent(
        """
        SELECT
            a,\t\t\t-- Some comment
            longer_col\t-- A lined up comment
        FROM spam
    """
    )
    fix_str = dedent(
        """
        SELECT
            a,\t\t\t-- Some comment
            longer_col\t-- A lined up comment
        FROM spam
    """
    )
    configs = {}
    res = assert_rule_fail_in_sql(RULE, fail_str, configs)
    assert res == fix_str
    assert lint(res, configs) == 2 * [
        "Incorrect indentation type found in file. "
        "The indent occurs after other text, so a manual fix is needed."
    ]


def test_indented_comments_tab_config_fails() -> None:
    """It's not visible to bare eye, but here spaces indent is replaced with tab.

    Lint fails after fixing due to the spaces that come before the comments.
    That is left unfixable for now, as explained in:
    https://github.com/sqlfluff/sqlfluff/pull/590#issuecomment-739484190
    """
    fail_str = dedent(
        """
        SELECT
            a,         -- Some comment
            longer_col -- A lined up comment
        FROM spam
    """
    )
    fix_str = dedent(
        """
        SELECT
        \ta,         -- Some comment
        \tlonger_col -- A lined up comment
        FROM spam
    """
    )
    configs = {"rules": {"indent_unit": "tab"}}
    res = assert_rule_fail_in_sql(RULE, fail_str, configs)
    assert res == fix_str
    assert lint(res, configs) == [
        "Incorrect indentation type found in file. "
        "The indent occurs after other text, so a manual fix is needed."
    ]
