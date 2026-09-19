"""Tests the python routines within AM12."""

import sqlfluff


def test__rules__std_AM12_forward_reference_reported() -> None:
    """A CTE may not reference a sibling defined later in the same block."""
    sql = "WITH first AS (SELECT * FROM later), later AS (SELECT 1 AS x) SELECT * FROM first;"
    result = sqlfluff.lint(sql)

    results_AM12 = [r for r in result if r["code"] == "AM12"]
    assert len(results_AM12) >= 1


def test__rules__std_AM12_earlier_sibling_no_violation() -> None:
    """Referencing an earlier sibling is exactly what CTEs are for."""
    sql = "WITH first AS (SELECT 1 AS x), later AS (SELECT * FROM first) SELECT * FROM later;"
    result = sqlfluff.lint(sql)

    results_AM12 = [r for r in result if r["code"] == "AM12"]
    assert len(results_AM12) == 0


def test__rules__std_AM12_self_reference_without_recursive_reported() -> None:
    """A CTE referencing itself needs WITH RECURSIVE."""
    sql = "WITH cte AS (SELECT * FROM cte) SELECT * FROM cte;"
    result = sqlfluff.lint(sql)

    results_AM12 = [r for r in result if r["code"] == "AM12"]
    assert len(results_AM12) >= 1


def test__rules__std_AM12_recursive_self_reference_no_violation() -> None:
    """WITH RECURSIVE legalizes a genuine self-reference.

    It does not, however, legalize a forward reference to a different,
    later sibling.
    """
    legal = sqlfluff.lint(
        "WITH RECURSIVE cte AS (SELECT 1 AS n UNION ALL SELECT n + 1 FROM cte "
        "WHERE n < 3) SELECT * FROM cte;"
    )
    assert len([r for r in legal if r["code"] == "AM12"]) == 0

    still_illegal = sqlfluff.lint(
        "WITH RECURSIVE first AS (SELECT * FROM later), later AS (SELECT 1 AS x) "
        "SELECT * FROM first;"
    )
    assert len([r for r in still_illegal if r["code"] == "AM12"]) >= 1


def test__rules__std_AM12_nested_with_shadows_outer_scope_no_violation() -> None:
    """A nested WITH block starts its own scope and may reuse an outer name."""
    sql = (
        "WITH outer_cte AS (WITH outer_cte AS (SELECT 1 AS x) "
        "SELECT * FROM outer_cte) SELECT * FROM outer_cte;"
    )
    result = sqlfluff.lint(sql)

    results_AM12 = [r for r in result if r["code"] == "AM12"]
    assert len(results_AM12) == 0


def test__rules__std_AM12_non_select_statement_integration() -> None:
    """Non-SELECT statements should never trigger AM12."""
    sql = "CREATE TABLE foo (id INT, name TEXT);"
    result = sqlfluff.lint(sql)

    results_AM12 = [r for r in result if r["code"] == "AM12"]
    assert len(results_AM12) == 0
