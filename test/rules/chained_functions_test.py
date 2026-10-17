"""Check conversion and layout with the native rule order."""

from pathlib import Path

import pytest

from sqlfluff.core import FluffConfig, Linter
from sqlfluff.utils.testing.rules import RuleTestCase, load_test_cases

PUBLIC_RULE_NAME = "layout.chained_functions"
CONVERSION_RULE_NAME = "convention.prefer_chained_functions"
NATIVE_RULES = ("LT02", "LT16")
IDS, CASES = load_test_cases(
    str(Path(__file__).parents[1] / "fixtures/rules/std_rule_cases/CV14.yml")
)
CASES = [
    case._replace(fix_str=case.fix_str.replace("\n  ", "\n    "))
    if case_id == "CV14_test_issue_multiline_before" and case.fix_str is not None
    else case
    for case_id, case in zip(IDS, CASES)
]
CASES_BY_ID = dict(zip(IDS, CASES))
STYLES = ("one_liner", "aligned", "indented", "consistent")


def conversion_linter(
    style: str, rules: tuple[str, ...] = ("CV14", "LT02", "LT16")
) -> Linter:
    """Select the public rules with conversion explicitly enabled."""
    config = FluffConfig(
        configs={
            "rules": {
                CONVERSION_RULE_NAME: {"force_enable": True},
                PUBLIC_RULE_NAME: {"writing_style": style},
            }
        },
        overrides={"dialect": "bigquery", "rules": ",".join(rules)},
    )
    linter = Linter(config=config)
    assert not linter.user_rules
    assert [rule.code for rule in linter.get_rulepack().rules] == list(rules)
    return linter


@pytest.mark.parametrize("case", CASES, ids=IDS)
def test_acceptance_cases_in_native_order(
    case: RuleTestCase, caplog: pytest.LogCaptureFixture
) -> None:
    """Every reviewed conversion case must still work with CV14 before LT02."""
    sql = case.fail_str or case.pass_str
    assert sql is not None
    expected = case.fix_str or sql
    linter = conversion_linter("one_liner")
    assert not linter.parse_string(sql).violations
    result = linter.lint_string(sql, fix=True)
    assert any((v.rule_code() == "CV14" for v in result.violations)) == bool(
        case.fail_str
    )
    assert result.fix_string()[0] == expected
    assert not linter.parse_string(expected).violations
    assert not linter.lint_string(expected).violations
    assert linter.lint_string(expected, fix=True).fix_string()[0] == expected
    assert "Unexpected exception" not in caplog.text
    assert "would re-cause the same error" not in caplog.text


@pytest.mark.parametrize("style", STYLES)
@pytest.mark.parametrize(
    "case_id",
    ["CV14_test_issue_traditional", "CV14_test_issue_multiline_before"],
    ids=["traditional", "multiline"],
)
def test_issue_before_examples_all_styles(style: str, case_id: str) -> None:
    """Both actual Before examples must convert and converge in native order."""
    case = CASES_BY_ID[case_id]
    assert case.fail_str is not None and case.fix_str is not None
    expected = case.fix_str
    if style in ("aligned", "indented"):
        indent = "        " if style == "indented" else "    "
        expected = expected.replace(".", "\n" + indent + ".")
    linter = conversion_linter(style)
    result = linter.lint_string(case.fail_str, fix=True)
    assert result.fix_string()[0] == expected
    assert any((v.rule_code() == "CV14" for v in result.violations))
    assert not linter.parse_string(expected).violations
    assert not linter.lint_string(expected).violations
    assert linter.lint_string(expected, fix=True).fix_string()[0] == expected


@pytest.mark.parametrize("style", STYLES)
def test_converter_alone_reads_public_layout_style(style: str) -> None:
    """LT16 must not be needed to repair a converter using the wrong namespace."""
    sql = "SELECT\n    LOWER(TRIM(foo)) AS cleaned\nFROM t;\n"
    boundary = {"aligned": "\n    ", "indented": "\n        "}.get(style, "")
    expected = (
        f"SELECT\n    (foo){boundary}.TRIM(){boundary}.LOWER() AS cleaned\nFROM t;\n"
    )
    linter = conversion_linter(style, rules=("CV14",))
    result = linter.lint_string(sql, fix=True)
    assert result.fix_string()[0] == expected
    assert not linter.parse_string(expected).violations
    assert not linter.lint_string(expected).violations
    assert linter.lint_string(expected, fix=True).fix_string()[0] == expected


@pytest.mark.parametrize("style", ["one_liner", "aligned", "indented"])
@pytest.mark.parametrize("nested_first", [False, True])
def test_consistent_uses_original_chain_in_native_order(
    style: str, nested_first: bool
) -> None:
    """Running conversion first must retain the style of an original chain."""
    boundary = {"one_liner": "", "aligned": "\n    ", "indented": "\n        "}[style]
    chain = f"    (original){boundary}.LOWER(){boundary}.TRIM() AS old_result"
    nested = "    LOWER(TRIM(foo)) AS new_result"
    converted = f"    (foo){boundary}.TRIM(){boundary}.LOWER() AS new_result"
    fields = [nested, chain] if nested_first else [chain, nested]
    expected_fields = [converted, chain] if nested_first else [chain, converted]
    sql = "SELECT\n" + ",\n".join(fields) + "\nFROM t;\n"
    expected = "SELECT\n" + ",\n".join(expected_fields) + "\nFROM t;\n"
    linter = conversion_linter("consistent")
    result = linter.lint_string(sql, fix=True)
    assert result.fix_string()[0] == expected
    assert not linter.lint_string(expected).violations
    assert linter.lint_string(expected, fix=True).fix_string()[0] == expected


@pytest.mark.parametrize("style", ["one_liner", "aligned", "indented"])
@pytest.mark.parametrize("column", ["foo", "fooo", "foooo"])
def test_working_positions_in_native_order(style: str, column: str) -> None:
    """Moved tokens must retain correct working positions in the new rule order."""
    linter = conversion_linter(style)
    result = linter.lint_string(
        f"SELECT\n    LOWER(UPPER({column}))\nFROM t;\n", fix=True
    )
    assert any((v.rule_code() == "CV14" for v in result.violations))
    assert result.tree is not None
    line, position = (1, 1)
    for raw in result.tree.raw_segments:
        if not raw.is_meta:
            assert raw.pos_marker is not None
            assert raw.pos_marker.working_loc == (line, position), raw.raw
        if "\n" in raw.raw:
            line += raw.raw.count("\n")
            position = len(raw.raw.rsplit("\n", 1)[-1]) + 1
        else:
            position += len(raw.raw)


@pytest.mark.parametrize("style", STYLES)
def test_converter_with_native_standard_layout(style: str) -> None:
    """Conversion must agree with native spacing, indentation and line length."""
    sql = CASES_BY_ID["CV14_test_issue_multiline_before"].fail_str
    assert sql is not None
    linter = conversion_linter(style, rules=("CV14", "LT01", "LT02", "LT05", "LT16"))
    fixed = linter.lint_string(sql, fix=True).fix_string()[0]
    assert not linter.parse_string(fixed).violations
    assert not linter.lint_string(fixed).violations
    assert linter.lint_string(fixed, fix=True).fix_string()[0] == fixed
    assert all(
        (
            len(line) <= linter.config.get("max_line_length")
            for line in fixed.splitlines()
        )
    )


def test_consistent_conversion_resets_between_files() -> None:
    """Reusing a Linter must not reuse the previous file's inferred style."""
    linter = conversion_linter("consistent")
    for style, boundary in [("indented", "\n        "), ("aligned", "\n    ")]:
        chain = f"    (bar){boundary}.LOWER(){boundary}.TRIM() AS old_result"
        sql = f"SELECT\n    LOWER(TRIM(foo)) AS new_result,\n{chain}\nFROM t;\n"
        expected = f"SELECT\n    (foo){boundary}.TRIM(){boundary}.LOWER() AS new_result,\n{chain}\nFROM t;\n"
        result = linter.lint_string(sql, fname=f"{style}.sql", fix=True)
        assert result.fix_string()[0] == expected
        assert not linter.lint_string(expected).violations


def test_jinja_input_remains_source_template() -> None:
    """Explicitly enabled CV14 must retain the template expansion guard."""
    config = FluffConfig(
        configs={
            "rules": {CONVERSION_RULE_NAME: {"force_enable": True}},
            "templater": {"jinja": {"context": {"column": "foo"}}},
        },
        overrides={"dialect": "bigquery", "rules": "CV14,LT02,LT16"},
    )
    linter = Linter(config=config)
    sql = "SELECT LOWER(TRIM({{ column }})) FROM t;\n"
    result = linter.lint_string(sql, fix=True)
    assert not result.violations
    assert result.fix_string()[0] == sql
    assert not linter.parse_string(sql).violations


@pytest.mark.parametrize(
    "style,expected",
    [
        ("aligned", "SELECT\n    (foo)\n    .TRIM()\n    .LOWER();\n"),
        ("indented", "SELECT (foo)\n    .TRIM()\n    .LOWER();\n"),
    ],
)
def test_inline_nested_input_converges(style: str, expected: str) -> None:
    """An input sharing the SELECT line must not cause indentation oscillation."""
    linter = conversion_linter(style)
    result = linter.lint_string("SELECT LOWER(TRIM(foo));\n", fix=True)
    assert any(v.rule_code() == "CV14" for v in result.violations)
    assert result.fix_string()[0] == expected
    assert not linter.parse_string(expected).violations
    assert not linter.lint_string(expected).violations
    assert linter.lint_string(expected, fix=True).fix_string()[0] == expected
