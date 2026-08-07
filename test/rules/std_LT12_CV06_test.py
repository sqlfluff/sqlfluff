"""Tests the python routines within LT12 and CV06."""

from sqlfluff.core import FluffConfig, Linter


def test__rules__std_LT12_and_CV06_interaction() -> None:
    """Test interaction between LT12 and CV06 doesn't stop CV06 from being applied."""
    # Test sql with no final newline and no final semicolon.
    sql = "SELECT foo FROM bar"

    # Ensure final semicolon requirement is active.
    cfg = FluffConfig(overrides={"dialect": "ansi"})
    cfg.set_value(
        config_path=["rules", "convention.terminator", "require_final_semicolon"],
        val=True,
    )
    linter = Linter(config=cfg)

    # Return linted/fixed file.
    linted_file = linter.lint_string(sql, fix=True)

    # Check expected lint errors are raised.
    assert set([v.rule.code for v in linted_file.violations]) == {"LT12", "CV06"}

    # Check file is fixed.
    assert linted_file.fix_string()[0] == "SELECT foo FROM bar;\n"


def _lint_cv06(sql: str, **rule_config: object) -> list:
    """Lint a string with only CV06 enabled and return its violations."""
    cfg = FluffConfig(overrides={"dialect": "ansi", "rules": "CV06"})
    for key, val in rule_config.items():
        cfg.set_value(config_path=["rules", "convention.terminator", key], val=val)
    return Linter(config=cfg).lint_string(sql).violations


def test__rules__std_CV06_description_semicolon_newline() -> None:
    """Placement violations should not claim the semi-colon is missing.

    The statement here already ends with a semi-colon; the only problem is that
    ``multiline_newline`` requires it on its own line. Reporting "Statements must
    end with a semi-colon." for this case is misleading (see issue #5987).
    """
    violations = _lint_cv06("SELECT a\nFROM foo;\n", multiline_newline=True)

    assert [v.rule.code for v in violations] == ["CV06"]
    assert (
        violations[0].description
        == "Semi-colon should be on a new line after a multi-line statement."
    )


def test__rules__std_CV06_description_semicolon_spacing() -> None:
    """A semi-colon separated from its statement is a spacing violation."""
    violations = _lint_cv06("SELECT a\nFROM foo\n;\n")

    assert [v.rule.code for v in violations] == ["CV06"]
    assert (
        violations[0].description
        == "Semi-colon should not be preceded by whitespace or newlines."
    )


def test__rules__std_CV06_description_missing_semicolon_unchanged() -> None:
    """A genuinely missing semi-colon keeps the original description."""
    violations = _lint_cv06("SELECT a\nFROM foo\n", require_final_semicolon=True)

    assert [v.rule.code for v in violations] == ["CV06"]
    assert violations[0].description == "Statements must end with a semi-colon."
