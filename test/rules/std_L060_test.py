"""Tests the python routines within L060."""
import sqlfluff


def test__rules__std_L060_raised() -> None:
    """L060 is raised for use of ``IFNULL`` or ``NVL``."""
    sql = "SELECT\n\tIFNULL(NULL, 100),\n\tNVL(NULL,100);"
    result = sqlfluff.lint(sql, rules=["L060"])

    assert len(result) == 2
    assert result[0]["description"] == "Use 'COALESCE' instead of 'IFNULL'."
    assert result[1]["description"] == "Use 'COALESCE' instead of 'NVL'."
