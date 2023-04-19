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
    results_AM08 = [r for r in result if r["code"] == "AM08"]
    assert len(results_AM08) == 1
    assert (
         results_AM08[0]["description"]
         == "Unnecessary 'ORDER BY' clauses."
    )
