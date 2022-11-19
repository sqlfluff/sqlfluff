"""Tests the python routines within L048."""
import sqlfluff


def test__rules__std_L048_raised() -> None:
    """L048 is raised for quoted literals not surrounded by a single whitespace."""
    sql = "SELECT a +'b'+'c' FROM tbl;"
    result = sqlfluff.lint(sql)

    assert len(result) == 7

    results_l048 = [r for r in result if r["code"] == "L048"]
    assert len(results_l048) == 3
    assert (
        results_l048[0]["description"]
        == "Expected single whitespace between binary operator '+' and quoted literal."
    )
    assert (
        results_l048[1]["description"]
        == "Expected single whitespace between quoted literal and binary operator '+'."
    )
    assert (
        results_l048[2]["description"]
        == "Expected single whitespace between binary operator '+' and quoted literal."
    )
