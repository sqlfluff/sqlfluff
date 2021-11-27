"""Tests the python routines within L009 and L052."""
from sqlfluff.core import FluffConfig
from sqlfluff.core import Linter


def test__rules__std_L009_and_L052_interaction() -> None:
    """Test interaction between L009 and L052 doesn't stop L052 from being applied."""
    # Test sql with no final newline and no final semicolon.
    sql = "SELECT foo FROM bar"

    # Ensure final semicolon requirement is active.
    cfg = FluffConfig()
    cfg.set_value(config_path=["rules", "L052", "require_final_semicolon"], val=True)
    linter = Linter(config=cfg)

    # Return linted/fixed file.
    linted_file = linter.lint_string(sql, fix=True)

    # Check expected lint errors are raised.
    assert set([v.rule.code for v in linted_file.violations]) == {"L009", "L052"}

    # Check file is fixed.
    assert linted_file.fix_string()[0] == "SELECT foo FROM bar;\n"
