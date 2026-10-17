"""Check that focused native fixes coexist with whole-file chain indentation."""

from unittest.mock import patch

import pytest

from sqlfluff.core import FluffConfig, Linter
from sqlfluff.core.types import ConfigMappingType
from sqlfluff.utils.reflow.sequence import ReflowSequence

PUBLIC_RULE_NAME = "layout.chained_functions"
CONVERSION_RULE_NAME = "convention.prefer_chained_functions"
NATIVE_RULES = ("LT02", "LT16")


def layout_linter(
    style: str | None = None,
    configs: ConfigMappingType | None = None,
    rules: tuple[str, ...] = ("LT02", "LT16"),
) -> Linter:
    """Build an ordinary Linter using the registered native rule settings."""
    config = FluffConfig(
        configs=configs, overrides={"dialect": "bigquery", "rules": ",".join(rules)}
    )
    if style is not None:
        config.set_value(("rules", PUBLIC_RULE_NAME, "writing_style"), style)
    return Linter(config=config)


BOUNDARIES = {
    "one_liner": "",
    "aligned": "\n    ",
    "indented": "\n        ",
    "consistent": "",
}
FOCUSED_CASES = [
    pytest.param(
        "LT03",
        "SELECT\n    (foo).LOWER().TRIM() ||\n    (bar).UPPER()\nFROM t;\n",
        "SELECT\n    (foo){call}.LOWER(){call}.TRIM()\n    || (bar){call}.UPPER()\nFROM t;\n",
        id="operator-between-chains",
    ),
    pytest.param(
        "LT04",
        "SELECT\n    (foo).LOWER().TRIM()\n    , (bar).UPPER()\nFROM t;\n",
        "SELECT\n    (foo){call}.LOWER(){call}.TRIM(),\n    (bar){call}.UPPER()\nFROM t;\n",
        id="comma-after-chain",
    ),
    pytest.param(
        "LT11",
        "SELECT\n    (foo).LOWER().TRIM()\nFROM t UNION ALL SELECT\n    (bar).UPPER()\nFROM u;\n",
        "SELECT\n    (foo){call}.LOWER(){call}.TRIM()\nFROM t\nUNION ALL\nSELECT\n    (bar){call}.UPPER()\nFROM u;\n",
        id="union-between-queries",
    ),
    pytest.param(
        "CV05",
        "SELECT\n    (foo).REPLACE(IF(bar = NULL, 'a', 'b'), 'x').TRIM()\nFROM t;\n",
        "SELECT\n    (foo){call}.REPLACE(IF(bar IS NULL, 'a', 'b'), 'x'){call}.TRIM()\nFROM t;\n",
        id="null-comparison-inside-argument",
    ),
    pytest.param(
        "ST08",
        "SELECT DISTINCT\n    ((foo).LOWER().TRIM())\nFROM t;\n",
        "SELECT DISTINCT\n    (foo){call}.LOWER (){call}.TRIM ()\nFROM t;\n",
        id="distinct-removes-outer-brackets",
    ),
]


@pytest.mark.parametrize("style", BOUNDARIES)
@pytest.mark.parametrize("rule,sql,expected", FOCUSED_CASES)
def test_native_focused_fixes_with_chains(
    style: str, rule: str, sql: str, expected: str, caplog: pytest.LogCaptureFixture
) -> None:
    """Real partial reflow must fix SQL without conflicting with chain layout."""
    linter = layout_linter(style, rules=("LT02", rule, "LT16"))
    assert not linter.parse_string(sql).violations
    original = ReflowSequence.from_around_target
    with patch.object(ReflowSequence, "from_around_target", wraps=original) as spy:
        result = linter.lint_string(sql, fix=True)
        assert spy.called
    assert any((v.rule_code() == rule for v in result.violations))
    fixed = result.fix_string()[0]
    assert fixed == expected.format(call=BOUNDARIES[style])
    assert not linter.parse_string(fixed).violations
    assert not linter.lint_string(fixed).violations
    assert linter.lint_string(fixed, fix=True).fix_string()[0] == fixed
    assert "Unexpected exception" not in caplog.text
    assert "would re-cause the same error" not in caplog.text


@pytest.mark.parametrize("call_index", [0, 1, 2], ids=["first", "middle", "last"])
@pytest.mark.parametrize("sides", ["before", "after", "both"])
def test_partial_factories_keep_native_slice(call_index: int, sides: str) -> None:
    """A focused sequence must retain native tokens and its original boundaries."""
    linter = layout_linter("indented")
    parsed = linter.parse_string(
        "SELECT\n    (foo).LOWER().TRIM().UPPER() AS cleaned,\n    bar\nFROM t;\n"
    )
    assert parsed.tree is not None and (not parsed.violations)
    root = parsed.tree
    before_tree = root.stringify()
    original_ids = {raw.uuid for raw in root.raw_segments}
    expected_slices = [
        {"before": ").LOWER()", "after": ".LOWER().", "both": ").LOWER()."},
        {"before": ").TRIM()", "after": ".TRIM().", "both": ").TRIM()."},
        {"before": ").UPPER()", "after": ".UPPER() AS", "both": ").UPPER() AS"},
    ]
    target = list(root.recursive_crawl("chained_function_call"))[call_index]
    native = ReflowSequence.from_around_target(
        target, root, config=linter.config, sides=sides
    )
    original_raws = tuple(
        (raw for element in native.elements for raw in element.segments)
    )
    focused = ReflowSequence.from_around_target(
        target, root, config=linter.config, sides=sides
    )
    direct = ReflowSequence.from_raw_segments(original_raws, root, config=linter.config)
    for actual in (focused, direct):
        actual_raws = tuple(
            (raw for element in actual.elements for raw in element.segments)
        )
        assert all(raw.uuid in original_ids for raw in actual_raws)
        assert actual.get_raw() == expected_slices[call_index][sides]
        assert [raw.uuid for raw in actual_raws] == [raw.uuid for raw in original_raws]
        assert actual.get_raw() == native.get_raw()
        assert [type(element) for element in actual.elements] == [
            type(element) for element in native.elements
        ]
    assert root.stringify() == before_tree


@pytest.mark.parametrize(
    "first_style,operator_lines", [("aligned", "    || "), ("indented", "    ||\n    ")]
)
def test_focused_operator_fix_preserves_consistent_style(
    first_style: str, operator_lines: str
) -> None:
    """Moving an operator must retain the style selected by the first chain."""
    boundary = BOUNDARIES[first_style]
    first_chain = f"(foo){boundary}.LOWER(){boundary}.TRIM()"
    sql = f"SELECT\n    {first_chain} ||\n    (bar).UPPER()\nFROM t;\n"
    expected = (
        f"SELECT\n    {first_chain}\n{operator_lines}(bar){boundary}.UPPER()\nFROM t;\n"
    )
    linter = layout_linter("consistent", rules=("LT02", "LT03", "LT16"))
    result = linter.lint_string(sql, fix=True)
    assert result.violations
    assert result.fix_string()[0] == expected
    assert not linter.parse_string(expected).violations
    assert not linter.lint_string(expected).violations
    assert linter.lint_string(expected, fix=True).fix_string()[0] == expected


def test_native_lt02_method_is_executed() -> None:
    """A spy verifies that chain formatting invokes the native indentation rule."""
    linter = layout_linter("indented", rules=NATIVE_RULES)
    from sqlfluff.rules.layout.LT02 import Rule_LT02

    assert type(linter.get_rulepack().rules[0]) is Rule_LT02
    original_eval = Rule_LT02._eval
    sql = "SELECT\n    (foo).LOWER().TRIM()\nFROM t;\n"
    with patch.object(
        Rule_LT02, "_eval", autospec=True, side_effect=original_eval
    ) as spy:
        result = linter.lint_string(sql, fix=True)
        assert spy.called
        assert all((call.args[0].code == "LT02" for call in spy.call_args_list))
    expected = "SELECT\n    (foo)\n        .LOWER()\n        .TRIM()\nFROM t;\n"
    assert result.fix_string()[0] == expected


def test_jinja_variable_source_is_preserved() -> None:
    """A rendered input must remain a template variable in the fixed source."""
    linter = layout_linter(
        "indented",
        configs={"templater": {"jinja": {"context": {"column": "foo"}}}},
        rules=NATIVE_RULES,
    )
    sql = "SELECT\n    ({{ column }}).LOWER().TRIM() AS cleaned\nFROM t;\n"
    expected = "SELECT\n    ({{ column }})\n        .LOWER()\n        .TRIM() AS cleaned\nFROM t;\n"
    fixed = linter.lint_string(sql, fix=True).fix_string()[0]
    assert fixed == expected
    assert not linter.parse_string(fixed).violations
    assert not linter.lint_string(fixed).violations
    assert linter.lint_string(fixed, fix=True).fix_string()[0] == fixed


@pytest.mark.parametrize("include_column", [True, False])
def test_jinja_conditional_source_is_preserved(include_column: bool) -> None:
    """With one render variant, format only the selected conditional branch."""
    linter = layout_linter(
        "indented",
        configs={
            "core": {"render_variant_limit": 1},
            "templater": {"jinja": {"context": {"include_column": include_column}}},
        },
        rules=NATIVE_RULES,
    )
    sql = "SELECT\n{% if include_column %}\n    (foo).LOWER().TRIM() AS cleaned,\n{% endif %}\n    bar\nFROM t;\n"
    expected = sql
    if include_column:
        expected = "SELECT\n    {% if include_column %}\n        (foo)\n            .LOWER()\n            .TRIM() AS cleaned,\n    {% endif %}\n    bar\nFROM t;\n"
    assert not linter.parse_string(sql).violations
    fixed = linter.lint_string(sql, fix=True).fix_string()[0]
    assert fixed == expected
    assert not linter.parse_string(fixed).violations
    assert not linter.lint_string(fixed).violations
    assert linter.lint_string(fixed, fix=True).fix_string()[0] == fixed


def test_jinja_loop_source_is_preserved() -> None:
    """Repeated rendered chains must map back to one unchanged template loop."""
    linter = layout_linter(
        "indented",
        configs={"templater": {"jinja": {"context": {"columns": ["foo", "bar"]}}}},
        rules=NATIVE_RULES,
    )
    sql = "SELECT\n{% for column in columns %}\n    ({{ column }}).LOWER().TRIM() AS clean_{{ column }}{% if not loop.last %},{% endif %}\n{% endfor %}\nFROM t;\n"
    expected = "SELECT\n    {% for column in columns %}\n        ({{ column }})\n            .LOWER()\n            .TRIM() AS clean_{{ column }}{% if not loop.last %},{% endif %}\n    {% endfor %}\nFROM t;\n"
    assert not linter.parse_string(sql).violations
    fixed = linter.lint_string(sql, fix=True).fix_string()[0]
    assert fixed == expected
    assert not linter.parse_string(fixed).violations
    assert not linter.lint_string(fixed).violations
    assert linter.lint_string(fixed, fix=True).fix_string()[0] == fixed


def test_factory_models_each_sequence_once() -> None:
    """Repeated construction must not accumulate virtual markers in the AST."""
    linter = layout_linter("indented", rules=NATIVE_RULES)
    parsed = linter.parse_string("SELECT (foo).LOWER().TRIM();")
    assert parsed.tree is not None
    tree = parsed.tree
    before = tree.stringify()
    original_ids = {raw.uuid for raw in tree.raw_segments}
    for _ in range(2):
        sequence = ReflowSequence.from_root(tree, linter.config)
        added = [
            raw
            for element in sequence.elements
            for raw in element.segments
            if raw.uuid not in original_ids
        ]
        assert [raw.get_type() for raw in added] == ["indent", "dedent"]
        assert sequence.get_raw() == tree.raw
        assert tree.stringify() == before


def test_configurations_do_not_leak() -> None:
    """Two native linters must obey their own indentation configurations."""
    indented = layout_linter("indented", rules=("LT02",))
    aligned = layout_linter("aligned", rules=("LT02",))
    sql = "SELECT\n    (foo)\n        .LOWER()\nFROM t;\n"
    assert indented.lint_string(sql, fix=True).fix_string()[0] == sql
    assert aligned.lint_string(sql, fix=True).fix_string()[0] == sql.replace(
        "        .LOWER()", "    .LOWER()"
    )
