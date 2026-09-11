"""Tests the python routines within AM10."""

import sqlfluff


def test__rules__std_AM10_invalid_projection() -> None:
    """A bare column outside an aggregate, not a grouping key, is flagged."""
    sql = """
    SELECT a, b, COUNT(*) AS c
    FROM foo
    GROUP BY b;
    """
    result = sqlfluff.lint(sql)

    results_AM10 = [r for r in result if r["code"] == "AM10"]
    assert len(results_AM10) >= 1


def test__rules__std_AM10_grouped_column_no_violation() -> None:
    """A column that is itself a plain grouping key is fine."""
    sql = """
    SELECT b, COUNT(*) AS c
    FROM foo
    GROUP BY b;
    """
    result = sqlfluff.lint(sql)

    results_AM10 = [r for r in result if r["code"] == "AM10"]
    assert len(results_AM10) == 0


def test__rules__std_AM10_computed_key_reuse_no_violation() -> None:
    """The full computed grouping expression may be reused in the projection.

    This holds through cosmetic parenthesis or whitespace differences, but
    that does not make an additional bare component column valid on its own.
    """
    reused = sqlfluff.lint("SELECT a + b AS key, COUNT(*) FROM foo GROUP BY a + b;")
    assert len([r for r in reused if r["code"] == "AM10"]) == 0

    parenthesized = sqlfluff.lint("SELECT (a + b), COUNT(*) FROM foo GROUP BY a + b;")
    assert len([r for r in parenthesized if r["code"] == "AM10"]) == 0

    extra_column = sqlfluff.lint("SELECT a + b + c, COUNT(*) FROM foo GROUP BY a + b;")
    assert len([r for r in extra_column if r["code"] == "AM10"]) >= 1


def test__rules__std_AM10_quoted_identifier_case_sensitivity() -> None:
    """Quoted identifiers are compared case-sensitively, unlike bare ones."""
    result = sqlfluff.lint('SELECT "A", COUNT(*) AS c FROM foo GROUP BY "a";')

    results_AM10 = [r for r in result if r["code"] == "AM10"]
    assert len(results_AM10) >= 1


def test__rules__std_AM10_window_function_no_violation() -> None:
    """A windowed aggregate does not collapse rows, so it is exempt."""
    sql = """
    SELECT a, SUM(x) OVER (PARTITION BY a) AS running
    FROM foo;
    """
    result = sqlfluff.lint(sql)

    results_AM10 = [r for r in result if r["code"] == "AM10"]
    assert len(results_AM10) == 0


def test__rules__std_AM10_non_select_statement_integration() -> None:
    """Non-SELECT statements should never trigger AM10."""
    sql = """
    CREATE TABLE foo (id INT, name TEXT);
    """
    result = sqlfluff.lint(sql)

    results_AM10 = [r for r in result if r["code"] == "AM10"]
    assert len(results_AM10) == 0
