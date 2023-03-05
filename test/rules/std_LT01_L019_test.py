"""Tests the python routines within LT01."""
import sqlfluff


def test__rules__std_LT01_single_raise() -> None:
    """Test case for multiple LT01 errors raised when no post comma whitespace."""
    # This query used to triple count LT01. Added memory to log previously fixed commas
    # (issue #2001).
    sql = """
    SELECT
        col_a AS a
        ,col_b AS b
    FROM foo;
    """
    result = sqlfluff.lint(sql, rules=["LT01", "L019"])

    results_LT01 = [r for r in result if r["code"] == "LT01"]
    results_L019 = [r for r in result if r["code"] == "L019"]
    assert len(results_LT01) == 1
    assert len(results_L019) == 1
