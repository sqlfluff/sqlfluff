"""Tests the python routines within AM08."""
import sqlfluff


def test__rules__std_AM08_raised() -> None:
    """Test case for AM08 errors raised"""
    sql = """
    SELECT
        LAST_VALUE(foo) OVER (PARTITION BY bar ORDER BY baz) as boo,
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

def test__rules__std_AM08_fix() -> None:
    """Test case for AM08 errors fixed."""
    sql = """
    SELECT
        foo,
        bar,
    FROM foo
    ORDER BY 1, 2;
    """

    result = sqlfluff.fix(sql)
    assert result == 'SELECT\n    foo,\n    bar\nFROM foo;\n'
