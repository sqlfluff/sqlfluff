"""Tests the python routines within CV09."""

from sqlfluff.core import FluffConfig, Linter


def test__rules__std_CV09_raised() -> None:
    """CV09 is raised for use of blocked words with correct error message."""
    sql = "SELECT MYOLDFUNCTION(col1) FROM deprecated_table;\n"
    cfg = FluffConfig(overrides={"dialect": "ansi"})
    cfg.set_value(
        config_path=["rules", "convention.blocked_words", "blocked_words"],
        val="myoldfunction,deprecated_table",
    )
    linter = Linter(config=cfg)
    result_records = linter.lint_string_wrapped(sql).as_records()
    result = result_records[0]["violations"]

    assert len(result) == 2
    assert result[0]["description"] == "Use of blocked word 'MYOLDFUNCTION'."
    assert result[1]["description"] == "Use of blocked word 'deprecated_table'."
