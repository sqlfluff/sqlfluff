"""Tests the python routines within L008."""
import sqlfluff


def test__rules__std_L008_single_raise() -> None:
    """Test case for multiple L008 errors raised when no post comma whitespace."""
    # This query used to triple count L008. Added memory to log previously fixed commas (issue #2001).
    sql = """
    SELECT
        col_a AS a
        ,col_b AS b
    FROM foo;
    """
    result = sqlfluff.lint(sql, rules=["L008", "L019"])

    results_L008 = [r for r in result if r["code"] == "L008"]
    results_L019 = [r for r in result if r["code"] == "L019"]
    assert len(results_L008) == 1
    assert len(results_L019) == 1
