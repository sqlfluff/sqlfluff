"""Tests the python routines within AM08."""
import sqlfluff


def test__rules__std_AM08_raised() -> None:
    """Test case for multiple AM08 errors raised with 'consistent' setting."""
    sql = """
    SELECT
        foo,
        bar,
    FROM foo
    ORDER BY 1, 2;
    """
    result = sqlfluff.lint(sql)
    print([r['code'] for r in result])
    results_AM08 = [r for r in result if r["code"] == "AM08"]
    print(results_AM08)
    # assert len(results_AM06) == 2
    # assert (
    #     results_AM06[0]["description"]
    #     == "Inconsistent column references in 'GROUP BY/ORDER BY' clauses."
    # )
