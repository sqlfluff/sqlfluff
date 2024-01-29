"""Tests the python routines within CV02."""

import sqlfluff


def test__rules__std_CV02_raised() -> None:
    """CV02 is raised for use of ``IFNULL`` or ``NVL``."""
    sql = "SELECT\n\tIFNULL(NULL, 100),\n\tNVL(NULL,100);"
    result = sqlfluff.lint(sql, rules=["CV02"])

    assert len(result) == 2
    assert result[0]["description"] == "Use 'COALESCE' instead of 'IFNULL'."
    assert result[1]["description"] == "Use 'COALESCE' instead of 'NVL'."
