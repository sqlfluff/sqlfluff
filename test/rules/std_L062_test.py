"""Tests the python routines within L062."""
from sqlfluff.core import FluffConfig
from sqlfluff.core import Linter


def test__rules__std_L062_raised() -> None:
    """L062 is raised for use of blocked words with correct error message."""
    sql = "SELECT MYOLDFUNCTION(col1) FROM deprecated_table;\n"
    cfg = FluffConfig(overrides={"dialect": "ansi"})
    cfg.set_value(
        config_path=["rules", "L062", "blocked_words"],
        val="myoldfunction,deprecated_table",
    )
    linter = Linter(config=cfg)
    result_records = linter.lint_string_wrapped(sql).as_records()
    result = result_records[0]["violations"]

    assert len(result) == 2
    assert result[0]["description"] == "Use of blocked word 'MYOLDFUNCTION'."
    assert result[1]["description"] == "Use of blocked word 'deprecated_table'."
