"""Tests the python routines within L048."""
import pytest

import sqlfluff


def test__rules__std_L048() -> None:
    """L0048 is not raised for quoted literals surrounded by a single whitespace."""
    sql = "SELECT a + 'b' + 'c' FROM tbl;"
    result = sqlfluff.lint(sql)

    assert len(result) == 1

    results_l048 = [r for r in result if r["code"] == "L048"]
    assert not len(results_l048)


def test__rules__std_L048_raised() -> None:
    """L0048 is raised for quoted literals not surrounded by a single whitespace."""
    sql = "SELECT a +'b'+'c' FROM tbl;"
    result = sqlfluff.lint(sql)

    assert len(result) == 7

    results_l048 = [r for r in result if r["code"] == "L048"]
    assert len(results_l048) == 3
    assert results_l048[0]["description"] == "Missing whitespace before 'b'"
    assert results_l048[1]["description"] == "Missing whitespace after 'b'"
    assert results_l048[2]["description"] == "Missing whitespace before 'c'"


def test__rules__std_L048_unicode_tsql() -> None:
    """L0048 is not raised for unicode quoted literals when T-SQL."""
    sql = "SELECT a + N'b' + N'c' FROM tbl;"
    result = sqlfluff.lint(sql, dialect="tsql")

    assert len(result) == 1

    results_l048 = [r for r in result if r["code"] == "L048"]
    assert not len(results_l048)


@pytest.mark.parametrize("dialect", ["ansi", "mysql", "postgres", "sqlite", "bigquery"])
def test__rules__std_L048_unicode_other_dialects(dialect: str) -> None:
    """L0048 is raised for unicode quoted literals when some other dialects."""
    sql = "SELECT a + N'b' + N'c' FROM tbl;"
    result = sqlfluff.lint(sql, dialect=dialect)

    assert len(result) == 3

    results_l048 = [r for r in result if r["code"] == "L048"]
    assert len(results_l048) == 2
    assert results_l048[0]["description"] == "Missing whitespace before 'b'"
    assert results_l048[1]["description"] == "Missing whitespace before 'c'"


def test__rules__std_L048_unicode_tsql_small_n() -> None:
    """L0048 when there is `n` instead of `N` in a T-SQL."""
    sql = "SELECT a + N'b' + n'c' FROM tbl;"
    result = sqlfluff.lint(sql, dialect="tsql")

    assert len(result) == 2
    results_l048 = [r for r in result if r["code"] == "L048"]

    assert len(results_l048) == 1
    assert results_l048[0]["description"] == "Missing whitespace before 'c'"
