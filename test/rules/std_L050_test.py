"""Tests the python routines within L050."""
from sqlfluff.core import FluffConfig, Linter


def test__rules__std_L050_no_jinja_violation_for_default_config() -> None:
    """L050 is not raised for leading whitespace before a jinja template when using default config.

    This is due to ignore_templated_areas=False in the default config.
    """
    sql = "\n{# I am a comment #}\nSELECT foo FROM bar\n"

    cfg = FluffConfig.from_root()
    lnt = Linter(config=cfg)
    res = lnt.lint_string(in_str=sql)

    assert len(res.violations) == 0


def test__rules__std_L050_jinja_violation_for_custom_config() -> None:
    """L050 is raised for leading whitespace before a jinja template when ignore_templated_areas=False."""
    sql = "\n{# I am a comment #}\nSELECT foo FROM bar\n"

    cfg = FluffConfig.from_root(overrides=dict(ignore_templated_areas=False))
    lnt = Linter(config=cfg)
    res = lnt.lint_string(in_str=sql)

    assert len(res.violations) == 1
    assert res.violations[0].rule.code == "L050"
