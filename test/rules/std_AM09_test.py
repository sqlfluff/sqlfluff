"""Tests the python routines within AM09."""

from types import SimpleNamespace

import sqlfluff
from sqlfluff.rules.ambiguous.AM09 import Rule_AM09


def test__rules__std_AM09_missing_order_by() -> None:
    """Test case for LIMIT and OFFSET without ORDER BY."""
    sql = """
    SELECT *
    FROM foo
    LIMIT 10 OFFSET 5;
    """
    result = sqlfluff.lint(sql)

    results_AM09 = [r for r in result if r["code"] == "AM09"]
    assert len(results_AM09) == 1
    assert results_AM09[0]["description"] == (
        "LIMIT and OFFSET are used without ORDER BY,"
        " which may lead to non-deterministic results."
    )


def test__rules__std_AM09_with_order_by() -> None:
    """Test case for LIMIT and OFFSET with ORDER BY."""
    sql = """
    SELECT *
    FROM foo
    ORDER BY id
    LIMIT 10 OFFSET 5;
    """
    result = sqlfluff.lint(sql)

    results_AM09 = [r for r in result if r["code"] == "AM09"]
    assert len(results_AM09) == 0


def test__rules__std_AM09_no_limit_or_offset() -> None:
    """Test case for query without LIMIT or OFFSET."""
    sql = """
    SELECT *
    FROM foo;
    """
    result = sqlfluff.lint(sql)

    results_AM09 = [r for r in result if r["code"] == "AM09"]
    assert len(results_AM09) == 0


def test__rules__std_AM09_non_select_statement_integration() -> None:
    """Integration-style lint: non-SELECT statements should not flag AM09."""
    sql = """
    CREATE TABLE foo (id INT, name TEXT);
    """
    result = sqlfluff.lint(sql)

    # Ensure no AM09 violations are reported
    results_AM09 = [r for r in result if r["code"] == "AM09"]
    assert len(results_AM09) == 0


def test__rules__std_AM09_eval_short_circuit_on_non_select_segment() -> None:
    """Directly cover the guard that returns None for non-SELECT segments."""
    class FakeSegment:
        def is_type(self, _type: str) -> bool:
            return False  # not a select_statement

    fake_context = SimpleNamespace(segment=FakeSegment())

    # Bypass BaseRule.__init__ (which requires code/description).
    rule = Rule_AM09.__new__(Rule_AM09)
    assert rule._eval(fake_context) is None
