"""Tests issue #1373 doesn't reoccur.

The combination of L003 (incorrect indentation), L036 (select targets),
and L039 (unnecessary white space) can result in incorrect indentation.
"""

import textwrap

import sqlfluff


def test__rules__std_L003_L036_L039():
    """Verify that double indents don't flag L039."""
    sql = """\
    WITH example AS (
        SELECT my_id,
            other_thing,
            one_more
        FROM
            my_table
    )

    SELECT *
    FROM example\n"""
    sql = textwrap.dedent(sql)

    fixed_sql = """\
    WITH example AS (
        SELECT
            my_id,
            other_thing,
            one_more
        FROM
            my_table
    )

    SELECT *
    FROM example\n"""
    fixed_sql = textwrap.dedent(fixed_sql)

    result = sqlfluff.fix(sql)
    assert result == fixed_sql
