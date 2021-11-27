"""Tests the python routines within L054."""
import sqlfluff


def test__rules__std_L054_raised() -> None:
    """Test case for multiple L054 errors raised with 'consistent' setting."""
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

    results_l054 = [r for r in result if r["code"] == "L054"]
    assert len(results_l054) == 2
    assert (
        results_l054[0]["description"]
        == "Inconsistent column references in GROUP BY/ORDER BY clauses."
    )


def test__rules__std_L054_unparsable() -> None:
    """Test unparsable group by doesn't result in bad rule L054 error."""
    sql = """
    SELECT foo.set.barr
    FROM foo
    GROUP BY
      foo.set.barr
    """
    result = sqlfluff.lint(sql)

    results_l054 = [r for r in result if r["code"] == "L054"]
    results_prs = [r for r in result if r["code"] == "PRS"]
    assert len(results_l054) == 0
    assert len(results_prs) > 0


def test__rules__std_L054_noqa() -> None:
    """Test unparsable group by with no qa doesn't result in bad rule L054 error."""
    sql = """
    SELECT foo.set.barr  --noqa: PRS
    FROM foo
    GROUP BY  --noqa: PRS
      foo.set.barr
    """
    result = sqlfluff.lint(sql)

    results_l054 = [r for r in result if r["code"] == "L054"]
    results_prs = [r for r in result if r["code"] == "PRS"]
    assert len(results_l054) == 0
    assert len(results_prs) == 0
