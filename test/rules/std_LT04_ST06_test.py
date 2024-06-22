"""Tests the python routines within LT04 and ST06."""

import pytest

from sqlfluff.core import FluffConfig, Linter


@pytest.mark.parametrize(
    ["in_sql", "out_sql"],
    [
        (
            """SELECT COALESCE(a, 0) AS b

    , COALESCE(c, 0) AS d
    , e
FROM t""",
            """SELECT e,

    COALESCE(a, 0) AS b,
    COALESCE(c, 0) AS d
FROM t""",
        ),
        (
            """SELECT COALESCE(a, 0) AS b--comment

    , COALESCE(c, 0) AS d
    , e
FROM t""",
            """SELECT e,--comment

    COALESCE(a, 0) AS b,
    COALESCE(c, 0) AS d
FROM t""",
        ),
        (
            """with cte1 as (
select "a"
      ,"b"
      ,coalesce("g1"
               ,"g2"
               ,"g3"
       ) as "g_combined"

      ,"i"
      ,"j"
  from test
),

cte2 as (
select "col1"

      ,'start: ' + "col2" as "new_col2"

      ,'start2: ' + "col3" as "new_col3"

      ,"col4"
      ,"col5"
from cte1
),

select * from cte2""",
            """with cte1 as (
select "a",
      "b",
      "i",

      "j",
      coalesce("g1",
               "g2",
               "g3"
       ) as "g_combined"
  from test
),

cte2 as (
select "col1",

      "col4",

      "col5",

      'start: ' + "col2" as "new_col2",
      'start2: ' + "col3" as "new_col3"
from cte1
),

select * from cte2""",
        ),
    ],
)
def test_rules_std_LT04_and_ST06_interaction_trailing(in_sql, out_sql) -> None:
    """Test interaction between LT04 and ST06.

    Test sql with two newlines with leading commas expecting trailing.
    """
    # Lint expected rules.
    cfg = FluffConfig.from_string(
        """[sqlfluff]
dialect = ansi
rules = LT04, ST06
"""
    )
    linter = Linter(config=cfg)

    # Return linted/fixed file.
    linted_file = linter.lint_string(in_sql, fix=True)

    # Check expected lint errors are raised.
    assert set([v.rule.code for v in linted_file.violations]) == {"LT04", "ST06"}

    # Check file is fixed.
    assert linted_file.fix_string()[0] == out_sql
