"""Exercise LT16 discovery, native configuration and actual layout fixing."""

import pytest

from sqlfluff.core import FluffConfig, Linter
from sqlfluff.core.errors import SQLFluffUserError
from sqlfluff.core.rules import get_config_info
from sqlfluff.core.types import ConfigMappingType
from sqlfluff.utils.reflow.chained_layout import configured_style

PUBLIC_RULE_NAME = "layout.chained_functions"
CONVERSION_RULE_NAME = "convention.prefer_chained_functions"
NATIVE_RULES = ("LT02", "LT16")
SQL = "SELECT\n    (foo).LOWER().TRIM() AS cleaned\nFROM t;\n"
BOUNDARIES = {
    "one_liner": "",
    "aligned": "\n    ",
    "indented": "\n        ",
    "consistent": "",
}


@pytest.mark.parametrize("reference", ["LT16", PUBLIC_RULE_NAME, "layout"])
def test_rule_is_discovered_without_user_rules(
    reference: str, caplog: pytest.LogCaptureFixture
) -> None:
    """Plugin discovery must resolve the code, name and layout group."""
    linter = Linter(dialect="bigquery", rules=[reference])
    assert linter.user_rules == []
    rules = {rule.code: rule for rule in linter.get_rulepack().rules}
    rule = rules["LT16"]
    assert rule.name == PUBLIC_RULE_NAME
    assert rule.writing_style == "consistent"
    assert rule.config_keywords == ["writing_style"]
    if reference != "layout":
        assert list(rules) == ["LT16"]
    assert "unknown rule" not in caplog.text.lower()
    assert "unexpected rule" not in caplog.text.lower()


@pytest.mark.parametrize("reference", ["LT16", PUBLIC_RULE_NAME])
def test_rule_can_be_excluded(reference: str) -> None:
    """Native allowlists and denylists must work for the new rule."""
    config = FluffConfig(
        configs={"rules": {PUBLIC_RULE_NAME: {"writing_style": "indented"}}},
        overrides={
            "dialect": "bigquery",
            "rules": "LT02,LT16",
            "exclude_rules": reference,
        },
    )
    linter = Linter(config=config)
    assert [rule.code for rule in linter.get_rulepack().rules] == ["LT02"]
    sql = "SELECT\n    (foo)\n        .LOWER()\n        .TRIM()\nFROM t;\n"
    result = linter.lint_string(sql, fix=True)
    assert not result.violations
    assert result.fix_string()[0] == sql


@pytest.mark.parametrize("style", BOUNDARIES)
@pytest.mark.parametrize("scope", ["generic", "specific"])
def test_ini_style_is_used_by_rule_and_reflow(style: str, scope: str) -> None:
    """Real INI settings must reach both native rule configuration and LT02."""
    section = "sqlfluff:rules"
    if scope == "specific":
        section += f":{PUBLIC_RULE_NAME}"
    config = FluffConfig.from_string(
        f"[sqlfluff]\ndialect = bigquery\nrules = LT02,LT16\n\n[{section}]\nwriting_style = {style}\n"
    )
    linter = Linter(config=config)
    rules = linter.get_rulepack().rules
    assert [rule.code for rule in rules] == ["LT02", "LT16"]
    assert rules[1].writing_style == style
    assert configured_style(config, rule_name=PUBLIC_RULE_NAME) == style
    boundary = BOUNDARIES[style]
    expected = (
        f"SELECT\n    (foo){boundary}.LOWER(){boundary}.TRIM() AS cleaned\nFROM t;\n"
    )
    result = linter.lint_string(SQL, fix=True)
    assert result.fix_string()[0] == expected
    if style in ("aligned", "indented"):
        assert any((v.rule_code() == "LT16" for v in result.violations))
    assert not linter.parse_string(expected).violations
    assert not linter.lint_string(expected).violations
    assert linter.lint_string(expected, fix=True).fix_string()[0] == expected


@pytest.mark.parametrize(
    "generic,specific", [("one_liner", "indented"), ("indented", "aligned")]
)
def test_specific_style_overrides_generic(generic: str, specific: str) -> None:
    """Native RuleSet and the shared helper must agree on config precedence."""
    config = FluffConfig.from_string(
        f"[sqlfluff]\ndialect = bigquery\nrules = LT02,LT16\n\n[sqlfluff:rules]\nwriting_style = {generic}\n\n[sqlfluff:rules:{PUBLIC_RULE_NAME}]\nwriting_style = {specific}\n"
    )
    linter = Linter(config=config)
    assert linter.get_rulepack().rules[1].writing_style == specific
    assert configured_style(config, rule_name=PUBLIC_RULE_NAME) == specific
    boundary = BOUNDARIES[specific]
    expected = (
        f"SELECT\n    (foo){boundary}.LOWER(){boundary}.TRIM() AS cleaned\nFROM t;\n"
    )
    fixed = linter.lint_string(SQL, fix=True).fix_string()[0]
    assert fixed == expected
    assert not linter.lint_string(fixed).violations
    assert linter.lint_string(fixed, fix=True).fix_string()[0] == fixed


@pytest.mark.parametrize("bad_style", ["invalid", "one-liner", "", True, 1])
@pytest.mark.parametrize("scope", ["generic", "specific"])
def test_invalid_style_is_rejected_by_native_validation(
    bad_style: str | bool | int, scope: str
) -> None:
    """RuleSet must reject invalid values before any SQL needs to be linted."""
    rules: ConfigMappingType = {"writing_style": bad_style}
    if scope == "specific":
        rules = {PUBLIC_RULE_NAME: rules}
    config = FluffConfig(
        configs={"rules": rules}, overrides={"dialect": "bigquery", "rules": "LT16"}
    )
    linter = Linter(config=config)
    with pytest.raises(SQLFluffUserError, match="Invalid option.*writing_style"):
        linter.get_rulepack()


def test_configuration_metadata_is_documented() -> None:
    """The rule metaclass must enrich docs from registered ConfigInfo."""
    linter = Linter(dialect="bigquery", rules=["LT16"])
    rule = linter.get_rulepack().rules[0]
    info = get_config_info()["writing_style"]
    assert set(info["validation"] or []) == set(BOUNDARIES)
    doc = type(rule).__doc__
    assert doc is not None
    assert "**Configuration**" in doc
    assert "writing_style" in doc
    assert "infer the style from the first chain" in doc
    assert all((style in doc for style in BOUNDARIES))


def test_default_consistent_resets_between_files() -> None:
    """A default-configured native LT16 must infer style separately per file."""
    linter = Linter(dialect="bigquery", rules=["LT02", "LT16"])
    assert [rule.code for rule in linter.get_rulepack().rules] == ["LT02", "LT16"]
    indented = "SELECT\n    (foo)\n        .LOWER()\n        .TRIM()\nFROM t;\n"
    aligned = "SELECT\n    (bar)\n    .LOWER()\n    .TRIM()\nFROM t;\n"
    for filename, sql in [("indented.sql", indented), ("aligned.sql", aligned)]:
        result = linter.lint_string(sql, fname=filename, fix=True)
        assert not result.violations
        assert result.fix_string()[0] == sql


def test_config_section_uses_name_not_code(caplog: pytest.LogCaptureFixture) -> None:
    """A code may select a rule, but its configuration section uses the name."""
    config = FluffConfig.from_string(
        "[sqlfluff]\ndialect = bigquery\nrules = LT16\n\n[sqlfluff:rules:LT16]\nwriting_style = aligned\n"
    )
    rule = Linter(config=config).get_rulepack().rules[0]
    assert rule.writing_style == "consistent"
    assert "unexpected rule 'LT16'" in caplog.text
    assert f"sqlfluff:rules:{PUBLIC_RULE_NAME}" in caplog.text
