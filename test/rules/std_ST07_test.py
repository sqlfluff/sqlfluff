"""Tests the python routines within ST07."""

import sqlfluff


def test__rules__std_ST07_bigquery_hyphenated_table_no_fix():
    """ST07 must not propose a fix for BigQuery joins on hyphenated table names.

    The last dot-delimited part of a BigQuery table reference (e.g. "table-c"
    in "project-a.dataset-b.table-c") is not a valid naked identifier because
    it contains a hyphen. Splicing it directly into a generated ``ON`` clause
    (e.g. ``ON table-c.a = table-d.a``) produces invalid SQL, so the rule
    should still flag the ``USING`` clause but decline to offer an unsafe fix.
    """
    sql = (
        "SELECT * FROM project-a.dataset-b.table-c "
        "JOIN dataset-c.table-d USING (a);"
    )
    result = sqlfluff.lint(sql, rules=["ST07"], dialect="bigquery")
    assert len(result) == 1
    assert result[0]["fixes"] == []
