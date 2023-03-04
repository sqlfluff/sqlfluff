"""Tests the python routines within L009 and CV06."""
from sqlfluff.core import FluffConfig
from sqlfluff.core import Linter


def test__rules__std_L009_and_CV06_interaction() -> None:
    """Test interaction between L009 and CV06 doesn't stop CV06 from being applied."""
    # Test sql with no final newline and no final semicolon.
    sql = "SELECT foo FROM bar"

    # Ensure final semicolon requirement is active.
    cfg = FluffConfig(overrides={"dialect": "ansi"})
    cfg.set_value(config_path=["rules", "CV06", "require_final_semicolon"], val=True)
    linter = Linter(config=cfg)

    # Return linted/fixed file.
    linted_file = linter.lint_string(sql, fix=True)

    # Check expected lint errors are raised.
    assert set([v.rule.code for v in linted_file.violations]) == {"L009", "CV06"}

    # Check file is fixed.
    assert linted_file.fix_string()[0] == "SELECT foo FROM bar;\n"
