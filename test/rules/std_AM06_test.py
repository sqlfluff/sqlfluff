"""Tests the python routines within AM06."""

import sqlfluff


def test__rules__std_AM06_raised() -> None:
    """Test case for multiple AM06 errors raised with 'consistent' setting."""
    sql = """
    SELECT
        foo,
        bar,
        sum(baz) AS sum_value
    FROM (
        SELECT
            foo,
            bar,
            sum(baz) AS baz
        FROM fake_table
        GROUP BY
            foo, bar
    )
    GROUP BY
        1, 2
    ORDER BY
        1, 2;
    """
    result = sqlfluff.lint(sql)

    results_AM06 = [r for r in result if r["code"] == "AM06"]
    assert len(results_AM06) == 2
    assert (
        results_AM06[0]["description"]
        == "Inconsistent column references in 'GROUP BY/ORDER BY' clauses."
    )


def test__rules__std_AM06_unparsable() -> None:
    """Test unparsable group by doesn't result in bad rule AM06 error."""
    sql = """
    SELECT foo.set.barr
    FROM foo
    GROUP BY
      foo.set.barr
    """
    result = sqlfluff.lint(sql)

    results_AM06 = [r for r in result if r["code"] == "AM06"]
    results_prs = [r for r in result if r["code"] == "PRS"]
    assert len(results_AM06) == 0
    assert len(results_prs) > 0


def test__rules__std_AM06_noqa() -> None:
    """Test unparsable group by with no qa doesn't result in bad rule AM06 error."""
    sql = """
    SELECT foo.set.barr  --noqa: PRS
    FROM foo
    GROUP BY
      f@oo.set.bar.r --noqa: PRS
    """
    result = sqlfluff.lint(sql)

    results_AM06 = [r for r in result if r["code"] == "AM06"]
    results_prs = [r for r in result if r["code"] == "PRS"]
    assert len(results_AM06) == 0
    assert len(results_prs) == 0
