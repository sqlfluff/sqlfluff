"""Tests the python routines within AM11."""

import sqlfluff


def test__rules__std_AM11_window_in_where_reported() -> None:
    """A window function may not be evaluated inside a row filter."""
    sql = "SELECT a FROM foo WHERE ROW_NUMBER() OVER (ORDER BY a) = 1;"
    result = sqlfluff.lint(sql)

    results_AM11 = [r for r in result if r["code"] == "AM11"]
    assert len(results_AM11) >= 1


def test__rules__std_AM11_aggregate_in_where_reported() -> None:
    """A non-window aggregate may not be evaluated inside a row filter."""
    sql = "SELECT a FROM foo WHERE COUNT(*) > 1;"
    result = sqlfluff.lint(sql)

    results_AM11 = [r for r in result if r["code"] == "AM11"]
    assert len(results_AM11) >= 1


def test__rules__std_AM11_aggregate_in_having_no_violation() -> None:
    """Aggregates remain legal in HAVING, unlike WHERE."""
    sql = "SELECT a, COUNT(*) FROM foo GROUP BY a HAVING COUNT(*) > 1;"
    result = sqlfluff.lint(sql)

    results_AM11 = [r for r in result if r["code"] == "AM11"]
    assert len(results_AM11) == 0


def test__rules__std_AM11_window_in_select_no_violation() -> None:
    """Window functions remain legal in SELECT and ORDER BY."""
    sql = "SELECT a, SUM(x) OVER (PARTITION BY a) AS r FROM foo;"
    result = sqlfluff.lint(sql)

    results_AM11 = [r for r in result if r["code"] == "AM11"]
    assert len(results_AM11) == 0


def test__rules__std_AM11_window_inside_aggregate_reported() -> None:
    """A window function nested inside a non-window aggregate is illegal.

    The reverse nesting, an aggregate inside a window, remains fine.
    """
    illegal = sqlfluff.lint("SELECT SUM(ROW_NUMBER() OVER (ORDER BY a)) FROM foo;")
    assert len([r for r in illegal if r["code"] == "AM11"]) >= 1

    legal = sqlfluff.lint("SELECT SUM(COUNT(*)) OVER () FROM foo;")
    assert len([r for r in legal if r["code"] == "AM11"]) == 0


def test__rules__std_AM11_non_select_statement_integration() -> None:
    """Non-SELECT statements should never trigger AM11."""
    sql = "CREATE TABLE foo (id INT, name TEXT);"
    result = sqlfluff.lint(sql)

    results_AM11 = [r for r in result if r["code"] == "AM11"]
    assert len(results_AM11) == 0
