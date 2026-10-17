"""Check discovery, opt-in, scope and lifetime of the proposed CV14 rule."""

import pytest

from sqlfluff.core import FluffConfig, Linter
from sqlfluff.core.errors import SQLFluffUserError

PUBLIC_RULE_NAME = "layout.chained_functions"
CONVERSION_RULE_NAME = "convention.prefer_chained_functions"
NATIVE_RULES = ("LT02", "LT16")
SQL = "SELECT\n    LOWER(TRIM(foo)) AS cleaned\nFROM t;\n"


@pytest.mark.parametrize("reference", ["CV14", CONVERSION_RULE_NAME, "convention"])
def test_converter_is_discovered_without_user_rules(reference: str) -> None:
    """Discovery by code, name and group must not bypass the default opt-out."""
    linter = Linter(dialect="bigquery", rules=[reference])
    assert not linter.user_rules
    rules = {rule.code: rule for rule in linter.get_rulepack().rules}
    converter = rules["CV14"]
    assert converter.name == CONVERSION_RULE_NAME
    assert converter.config_keywords == ["force_enable"]
    assert converter.force_enable is False


@pytest.mark.parametrize(
    "force_enable", [None, False, True], ids=["default", "off", "on"]
)
def test_converter_requires_opt_in(force_enable: bool | None) -> None:
    """The selected rule must preserve nested syntax until explicitly enabled."""
    text = "[sqlfluff]\ndialect = bigquery\nrules = CV14,LT02,LT16\n"
    if force_enable is not None:
        text += f"\n[sqlfluff:rules:{CONVERSION_RULE_NAME}]\nforce_enable = {force_enable}\n"
    linter = Linter(config=FluffConfig.from_string(text))
    rules = linter.get_rulepack().rules
    assert [rule.code for rule in rules] == ["CV14", "LT02", "LT16"]
    assert rules[0].force_enable is bool(force_enable)
    result = linter.lint_string(SQL, fix=True)
    fixed = result.fix_string()[0]
    assert fixed == (
        SQL.replace("LOWER(TRIM(foo))", "(foo).TRIM().LOWER()") if force_enable else SQL
    )
    assert any((v.rule_code() == "CV14" for v in result.violations)) == bool(
        force_enable
    )
    assert not linter.lint_string(fixed).violations
    assert linter.lint_string(fixed, fix=True).fix_string()[0] == fixed


@pytest.mark.parametrize("reference", ["CV14", CONVERSION_RULE_NAME])
def test_excluded_converter_leaves_layout_enabled(reference: str) -> None:
    """Excluding conversion must still allow existing chains to be formatted."""
    config = FluffConfig(
        configs={
            "rules": {
                CONVERSION_RULE_NAME: {"force_enable": True},
                PUBLIC_RULE_NAME: {"writing_style": "indented"},
            }
        },
        overrides={
            "dialect": "bigquery",
            "rules": "CV14,LT02,LT16",
            "exclude_rules": reference,
        },
    )
    linter = Linter(config=config)
    assert [rule.code for rule in linter.get_rulepack().rules] == ["LT02", "LT16"]
    sql = "SELECT\n    LOWER(TRIM(foo)) AS nested,\n    (bar).LOWER().TRIM() AS chained\nFROM t;\n"
    expected = "SELECT\n    LOWER(TRIM(foo)) AS nested,\n    (bar)\n        .LOWER()\n        .TRIM() AS chained\nFROM t;\n"
    result = linter.lint_string(sql, fix=True)
    assert result.fix_string()[0] == expected
    assert any((v.rule_code() == "LT16" for v in result.violations))
    assert not linter.lint_string(expected).violations
    assert linter.lint_string(expected, fix=True).fix_string()[0] == expected


@pytest.mark.parametrize("dialect", ["ansi", "postgres", "snowflake"])
def test_force_enable_does_not_convert_other_dialects(dialect: str) -> None:
    """Opt-in must retain the converter's BigQuery-only dialect guard."""
    config = FluffConfig(
        configs={"rules": {CONVERSION_RULE_NAME: {"force_enable": True}}},
        overrides={"dialect": dialect, "rules": "CV14"},
    )
    linter = Linter(config=config)
    assert not linter.parse_string(SQL).violations
    result = linter.lint_string(SQL, fix=True)
    assert not result.violations
    assert result.fix_string()[0] == SQL


@pytest.mark.parametrize("value", ["yes", "invalid", 2])
def test_invalid_force_enable_uses_native_validation(value: str | int) -> None:
    """The core force_enable ConfigInfo must reject unsupported values."""
    config = FluffConfig(
        configs={"rules": {CONVERSION_RULE_NAME: {"force_enable": value}}},
        overrides={"dialect": "bigquery", "rules": "CV14"},
    )
    with pytest.raises(SQLFluffUserError, match="Invalid option.*force_enable"):
        Linter(config=config).get_rulepack()
