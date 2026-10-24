"""Exercise BQ01 discovery, native configuration and actual layout fixing."""

import pytest
from click.testing import CliRunner

from sqlfluff.cli.commands import cli_format
from sqlfluff.core import FluffConfig, Linter
from sqlfluff.core.errors import SQLFluffUserError
from sqlfluff.core.rules import get_config_info
from sqlfluff.core.types import ConfigMappingType

PUBLIC_RULE_NAME = "bigquery.chained_functions"
NATIVE_RULES = ("LT02", "BQ01")
SQL = "SELECT\n    (foo).LOWER().TRIM() AS cleaned\nFROM t;\n"
BOUNDARIES = {
    "one_liner": "",
    "aligned": "\n    ",
    "indented": "\n        ",
    "consistent": "",
}


@pytest.mark.parametrize("reference", ["BQ01", PUBLIC_RULE_NAME, "bigquery", "layout"])
def test_rule_is_discovered_without_user_rules(
    reference: str, caplog: pytest.LogCaptureFixture
) -> None:
    """Plugin discovery must resolve the code, name and both rule groups."""
    linter = Linter(dialect="bigquery", rules=[reference])
    assert linter.user_rules == []
    rules = {rule.code: rule for rule in linter.get_rulepack().rules}
    rule = rules["BQ01"]
    assert rule.name == PUBLIC_RULE_NAME
    assert rule.writing_style == "consistent"
    assert rule.config_keywords == ["writing_style"]
    assert set(rule.groups) == {"all", "bigquery", "layout"}
    if reference != "layout":
        assert list(rules) == ["BQ01"]
    assert "unknown rule" not in caplog.text.lower()
    assert "unexpected rule" not in caplog.text.lower()


@pytest.mark.parametrize("style", BOUNDARIES)
def test_format_command_includes_bigquery_rule(style: str, tmp_path) -> None:
    """The dialect-specific bundle must remain part of ordinary SQL formatting."""
    config_path = tmp_path / ".sqlfluff"
    config_path.write_text(
        "[sqlfluff]\ndialect = bigquery\n\n"
        f"[sqlfluff:rules:{PUBLIC_RULE_NAME}]\nwriting_style = {style}\n",
        encoding="utf-8",
    )
    result = CliRunner().invoke(
        cli_format,
        [
            "-",
            "--config",
            str(config_path),
            "--ignore-local-config",
            "--disable-progress-bar",
        ],
        input=SQL,
    )
    assert result.exit_code == 0, result.output
    lines = result.stdout.splitlines()
    if style in {"aligned", "indented"}:
        call_lines = [line for line in lines if line.lstrip().startswith(".")]
        assert len(call_lines) == 2
        expected_indent = 8 if style == "indented" else 4
        assert all(
            len(line) - len(line.lstrip()) == expected_indent for line in call_lines
        )
    else:
        assert any("(foo).LOWER" in line and ".TRIM" in line for line in lines)
    # Other formatter rules control SELECT placement and spacing inside calls.
    config = FluffConfig.from_path(str(config_path))
    config.set_value(("core", "rules"), "BQ01,LT02")
    assert not Linter(config=config).lint_string(result.stdout).violations


@pytest.mark.parametrize("reference", ["BQ01", PUBLIC_RULE_NAME])
def test_rule_can_be_excluded(reference: str) -> None:
    """Native allowlists and denylists must work for the new rule."""
    config = FluffConfig(
        configs={"rules": {PUBLIC_RULE_NAME: {"writing_style": "indented"}}},
        overrides={
            "dialect": "bigquery",
            "rules": "LT02,BQ01",
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
def test_ini_style_is_used_by_rule_and_reflow(style: str) -> None:
    """Real INI settings must reach both native rule configuration and LT02."""
    config = FluffConfig.from_string(
        f"[sqlfluff]\ndialect = bigquery\nrules = LT02,BQ01\n\n[sqlfluff:rules:{PUBLIC_RULE_NAME}]\nwriting_style = {style}\n"
    )
    linter = Linter(config=config)
    rules = linter.get_rulepack().rules
    assert [rule.code for rule in rules] == ["BQ01", "LT02"]
    assert rules[0].writing_style == style
    assert config.get("dialect_obj").get_root_segment().get_indentation_config(config)[
        "indented_chained_functions"
    ] == (style in ("indented", "consistent"))
    boundary = BOUNDARIES[style]
    expected = (
        f"SELECT\n    (foo){boundary}.LOWER(){boundary}.TRIM() AS cleaned\nFROM t;\n"
    )
    result = linter.lint_string(SQL, fix=True)
    assert result.fix_string()[0] == expected
    if style in ("aligned", "indented"):
        assert any((v.rule_code() == "BQ01" for v in result.violations))
    assert not linter.parse_string(expected).violations
    assert not linter.lint_string(expected).violations
    assert linter.lint_string(expected, fix=True).fix_string()[0] == expected


@pytest.mark.parametrize("style", BOUNDARIES)
def test_rule_default_is_scoped_to_chained_functions(style: str) -> None:
    """The rule's own default must take precedence over generic rule values."""
    config = FluffConfig(overrides={"dialect": "bigquery", "rules": "BQ01"})
    assert config.get("writing_style", ["rules"]) is None
    assert config.get("writing_style", ["rules", PUBLIC_RULE_NAME]) == "consistent"
    config.set_value(("rules", "writing_style"), style)
    rule = Linter(config=config).get_rulepack().rules[0]
    assert rule.writing_style == "consistent"
    assert config.get("indented_chained_functions", ["indentation"]) is None


@pytest.mark.parametrize(
    "generic,specific", [("one_liner", "indented"), ("indented", "aligned")]
)
def test_specific_style_overrides_generic(generic: str, specific: str) -> None:
    """Native rules and grammar must agree on the rule's config precedence."""
    config = FluffConfig.from_string(
        f"[sqlfluff]\ndialect = bigquery\nrules = LT02,BQ01\n\n[sqlfluff:rules]\nwriting_style = {generic}\n\n[sqlfluff:rules:{PUBLIC_RULE_NAME}]\nwriting_style = {specific}\n"
    )
    linter = Linter(config=config)
    assert linter.get_rulepack().rules[0].writing_style == specific
    boundary = BOUNDARIES[specific]
    expected = (
        f"SELECT\n    (foo){boundary}.LOWER(){boundary}.TRIM() AS cleaned\nFROM t;\n"
    )
    fixed = linter.lint_string(SQL, fix=True).fix_string()[0]
    assert fixed == expected
    assert not linter.lint_string(fixed).violations
    assert linter.lint_string(fixed, fix=True).fix_string()[0] == fixed


@pytest.mark.parametrize("style", BOUNDARIES)
def test_layout_formats_chains_without_converting_nested_calls(style: str) -> None:
    """Formatting an existing chain must leave ordinary nested calls intact."""
    config = FluffConfig(
        configs={"rules": {PUBLIC_RULE_NAME: {"writing_style": style}}},
        overrides={"dialect": "bigquery", "rules": "LT02,BQ01"},
    )
    linter = Linter(config=config)
    sql = (
        "SELECT\n"
        "    LOWER(TRIM(foo)) AS nested_result,\n"
        "    (bar).LOWER().TRIM() AS chained_result\n"
        "FROM t;\n"
    )
    boundary = BOUNDARIES[style]
    expected = (
        "SELECT\n"
        "    LOWER(TRIM(foo)) AS nested_result,\n"
        f"    (bar){boundary}.LOWER(){boundary}.TRIM() AS chained_result\n"
        "FROM t;\n"
    )
    result = linter.lint_string(sql, fix=True)
    assert result.fix_string()[0] == expected
    assert not linter.lint_string(expected).violations


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
        configs={"rules": rules}, overrides={"dialect": "bigquery", "rules": "BQ01"}
    )
    linter = Linter(config=config)
    with pytest.raises(SQLFluffUserError, match="Invalid option.*writing_style"):
        linter.get_rulepack()


def test_configuration_metadata_is_documented() -> None:
    """The rule metaclass must enrich docs from registered ConfigInfo."""
    linter = Linter(dialect="bigquery", rules=["BQ01"])
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
    """A default-configured native BQ01 must infer style separately per file."""
    linter = Linter(dialect="bigquery", rules=["LT02", "BQ01"])
    assert [rule.code for rule in linter.get_rulepack().rules] == ["BQ01", "LT02"]
    indented = "SELECT\n    (foo)\n        .LOWER()\n        .TRIM()\nFROM t;\n"
    aligned = "SELECT\n    (bar)\n    .LOWER()\n    .TRIM()\nFROM t;\n"
    for filename, sql in [("indented.sql", indented), ("aligned.sql", aligned)]:
        result = linter.lint_string(sql, fname=filename, fix=True)
        assert not result.violations
        assert result.fix_string()[0] == sql


def test_config_section_uses_name_not_code(caplog: pytest.LogCaptureFixture) -> None:
    """A code may select a rule, but its configuration section uses the name."""
    config = FluffConfig.from_string(
        "[sqlfluff]\ndialect = bigquery\nrules = BQ01\n\n[sqlfluff:rules:BQ01]\nwriting_style = aligned\n"
    )
    rule = Linter(config=config).get_rulepack().rules[0]
    assert rule.writing_style == "consistent"
    assert "unexpected rule 'BQ01'" in caplog.text
    assert f"sqlfluff:rules:{PUBLIC_RULE_NAME}" in caplog.text
