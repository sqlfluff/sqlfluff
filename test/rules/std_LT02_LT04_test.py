"""Tests the python routines within LT02 and LT04."""

import pytest

from sqlfluff.core import FluffConfig, Linter


@pytest.mark.parametrize(
    ["in_sql", "out_sql"],
    [
        (
            """SELECT
    acct_id,
    date_x,
    't' AS test,

    CASE
        WHEN condition_1 = '1' THEN ''
        ELSE condition_1
    END AS case_1,

    CASE
        WHEN condition_2 = '2' THEN ''
        ELSE condition_2
    END AS case_2,
    dollar_amt,
FROM
    table_x""",
            """SELECT
    acct_id
    , date_x
    , 't' AS test

    , CASE
        WHEN condition_1 = '1' THEN ''
        ELSE condition_1
    END AS case_1

    , CASE
        WHEN condition_2 = '2' THEN ''
        ELSE condition_2
    END AS case_2
    , dollar_amt,
FROM
    table_x""",
        ),
    ],
)
def test_rules_std_LT02_LT04_interaction_indentation_leading(in_sql, out_sql) -> None:
    """Test interaction between LT02 and LT04.

    Test sql with two newlines with trailing commas expecting leading.
    """
    # Lint expected rules.
    cfg = FluffConfig.from_string("""[sqlfluff]
dialect = snowflake
rules = LT02, LT04

[sqlfluff:layout:type:comma]
spacing_before = touch
line_position = leading
""")
    linter = Linter(config=cfg)

    # Return linted/fixed file.
    linted_file = linter.lint_string(in_sql, fix=True)

    # Check expected lint errors are raised.
    assert set([v.rule.code for v in linted_file.violations]) == {"LT04"}

    # Check file is fixed.
    assert linted_file.fix_string()[0] == out_sql
