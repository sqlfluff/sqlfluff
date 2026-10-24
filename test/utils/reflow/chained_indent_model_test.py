"""Check the independent chained-call model against real parsed SQL."""

import pytest

from sqlfluff.core import FluffConfig, Linter
from sqlfluff.utils.reflow.chained_indent_model import (
    call_groups,
    model_chained_indents,
)
from sqlfluff.utils.reflow.sequence import ReflowSequence


@pytest.mark.parametrize(
    "sql,groups",
    [
        ("SELECT (foo).LOWER().TRIM();", 1),
        ("SELECT (foo).LOWER() || (bar).TRIM();", 2),
        ("SELECT (foo).REPLACE((bar).TRIM(), 'x').LOWER();", 2),
        ("SELECT (foo).LOWER() || bar;", 1),
    ],
)
def test_virtual_markers_preserve_source_and_tree(sql: str, groups: int) -> None:
    """Each group gets one balanced scope without mutating the input model."""
    config = FluffConfig(overrides={"dialect": "bigquery"})
    parsed = Linter(config=config).parse_string(sql)
    assert parsed.tree is not None and not parsed.violations
    root = parsed.tree
    before_tree = root.stringify()
    sequence = ReflowSequence.from_raw_segments(root.raw_segments, root, config)
    before_elements = sequence.elements.copy()
    original_ids = {raw.uuid for raw in root.raw_segments}
    modeled = model_chained_indents(sequence.elements, root)
    added = [
        raw
        for element in modeled
        for raw in element.segments
        if raw.uuid not in original_ids
    ]
    assert sum(raw.indent_val for raw in added) == 0
    assert sum(raw.indent_val == 1 for raw in added) == groups
    assert sum(raw.indent_val == -1 for raw in added) == groups
    assert len(list(call_groups(root))) == groups
    assert sequence.elements == before_elements
    assert root.stringify() == before_tree
    assert "".join(element.raw for element in modeled) == sql


@pytest.mark.parametrize(
    "expression,groups",
    [
        ("(foo).LOWER()", 1),
        ("(foo).LOWER().TRIM()", 1),
        ("(foo).LOWER() || (bar).TRIM()", 2),
        ("(foo).REPLACE((bar).TRIM(), 'x').LOWER()", 2),
    ],
)
def test_from_root_handles_expression_ending_in_chain(
    expression: str, groups: int
) -> None:
    """A complete expression can end in a call without a trailing reflow point."""
    config = FluffConfig(
        configs={"rules": {"layout.chained_functions": {"writing_style": "indented"}}},
        overrides={"dialect": "bigquery"},
    )
    parsed = Linter(config=config).parse_string(f"SELECT {expression}")
    assert parsed.tree is not None and not parsed.violations
    root = next(parsed.tree.recursive_crawl("expression"))
    assert root.raw == expression
    before_tree = root.stringify()
    original_ids = {raw.uuid for raw in root.raw_segments}

    for _ in range(2):
        sequence = ReflowSequence.from_root(root, config)
        added = [
            raw
            for element in sequence.elements
            for raw in element.segments
            if raw.uuid not in original_ids
        ]
        assert sequence.get_raw() == expression
        assert len(added) == 2 * groups
        assert sum(raw.indent_val == 1 for raw in added) == groups
        assert sum(raw.indent_val == -1 for raw in added) == groups
        assert root.stringify() == before_tree
