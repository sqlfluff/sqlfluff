"""Tests for LT01 alignment."""

import sqlfluff
from sqlfluff.core.config import FluffConfig


def test_lt01_alignment_ignores_code_on_previous_line() -> None:
    """Leading commas should not inherit alignment from the previous line."""
    sql = (
        "SELECT\n"
        "    FirstCol = 'Some Value'\n"
        "    , SecondCol = 'Some other value'\n"
        "    , ThirdCol = 'yet another val'\n"
        "    , t.NonaliasedCol\n"
        "FROM TestTable AS t\n"
        ";\n"
    )
    expected = (
        "SELECT\n"
        "    FirstCol    = 'Some Value'\n"
        "    , SecondCol = 'Some other value'\n"
        "    , ThirdCol  = 'yet another val'\n"
        "    , t.NonaliasedCol\n"
        "FROM TestTable AS t\n"
        ";\n"
    )
    config = FluffConfig.from_string(
        """
[sqlfluff]
dialect = tsql
rules = LT01

[sqlfluff:layout:type:comma]
line_position = leading

[sqlfluff:layout:type:alias_operator]
spacing_before = align
align_within = select_clause
align_scope = bracketed

[sqlfluff:layout:type:alias_expression]
spacing_before = align
align_within = select_clause
align_scope = bracketed
"""
    )

    assert sqlfluff.fix(sql, config=config) == expected


def test_lt01_alignment_uses_multiline_segment_endpoint() -> None:
    """A multiline segment ending beside an alias should set the baseline."""
    sql = (
        "SELECT\n"
        "    'alpha\n"
        "a_long_tail' AS first_column,\n"
        "    c AS second_column\n"
        "FROM foo\n"
    )
    expected = (
        "SELECT\n"
        "    'alpha\n"
        "a_long_tail' AS first_column,\n"
        "    c        AS second_column\n"
        "FROM foo\n"
    )
    config = FluffConfig.from_string(
        """
[sqlfluff]
dialect = ansi
rules = LT01

[sqlfluff:layout:type:alias_expression]
spacing_before = align
align_within = select_clause
align_scope = bracketed
"""
    )

    assert sqlfluff.fix(sql, config=config) == expected
