"""Tests the python routines within ST07."""

import sqlfluff


def test__rules__std_ST07_bigquery_hyphenated_table_no_fix():
    """No fix for hyphenated names: ref_str spans several parse segments."""
    sql = (
        "SELECT * FROM project-a.dataset-b.table-c "
        "JOIN dataset-c.table-d USING (a);"
    )
    result = sqlfluff.lint(sql, rules=["ST07"], dialect="bigquery")
    assert len(result) == 1
    assert result[0]["fixes"] == []


def test__rules__std_ST07_unqualified_using_column_no_fix():
    """No fix when a USING column is referenced unqualified (issue #7230)."""
    sql = (
        "SELECT field_1, field_2, field_3 FROM table_a "
        "INNER JOIN table_b USING (field_1)"
    )
    result = sqlfluff.lint(sql, rules=["ST07"], dialect="bigquery")
    assert len(result) == 1
    assert result[0]["fixes"] == []

    fixed = sqlfluff.fix(sql, rules=["ST07"], dialect="bigquery")
    assert fixed == sql


def test__rules__std_ST07_qualified_references_still_fixed():
    """Fix still offered when all USING column references are qualified."""
    sql = (
        "SELECT table_a.field_1, table_b.field_2 FROM table_a "
        "INNER JOIN table_b USING (field_1)"
    )
    fixed = sqlfluff.fix(sql, rules=["ST07"], dialect="bigquery")
    assert "ON table_a.field_1 = table_b.field_1" in fixed
