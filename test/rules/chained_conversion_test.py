"""Check conservative recognition and immutable conversion fixes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

import pytest

from sqlfluff.core import FluffConfig, Linter
from sqlfluff.core.parser import BaseSegment
from sqlfluff.core.rules.context import RuleContext

if TYPE_CHECKING:
    from sqlfluff.rules.convention.CV14 import FunctionCall


@dataclass(frozen=True)
class SegmentFake:
    """Fake the segment interface needed by the function recognizer.

    These are alternate internal tree shapes, not SQL parsing rejection tests.
    The recognizer must decline a rewrite when it does not understand a shape.
    """

    kind: str
    segments: tuple[SegmentFake, ...] = ()
    raw: str = ""
    is_code: bool = True

    def is_type(self, *types: str) -> bool:
        """Implement the parser segment's type query."""
        return self.kind in types

    @property
    def raw_upper(self) -> str:
        """Expose the case-insensitive text used for function names."""
        return self.raw.upper()


NAME = SegmentFake(
    "function_name",
    (SegmentFake("function_name_identifier", raw="LOWER"),),
    raw="LOWER",
)
INPUT = SegmentFake("expression", raw="foo")
NAMED = SegmentFake("named_argument", raw="suffix => 'x'")


def function(contents: SegmentFake) -> SegmentFake:
    """Provide a function shell while varying the parser's contents shape."""
    return SegmentFake("function", (NAME, contents))


def contents(*arguments: SegmentFake) -> SegmentFake:
    """Provide the usual bracketed argument container."""
    return SegmentFake(
        "function_contents",
        (
            SegmentFake(
                "bracketed",
                (SegmentFake("start_bracket"), *arguments, SegmentFake("end_bracket")),
            ),
        ),
    )


def recognize(segment: SegmentFake) -> FunctionCall | None:
    """Load rule metadata normally before using the isolated recognizer."""
    FluffConfig(overrides={"dialect": "bigquery"})
    from sqlfluff.rules.convention.CV14 import function_call

    return function_call(cast(BaseSegment, segment))


@pytest.mark.parametrize(
    "segment",
    [
        pytest.param(SegmentFake("column_reference", raw="foo"), id="not-a-function"),
        pytest.param(function(SegmentFake("window_specification")), id="unknown-body"),
        pytest.param(
            function(SegmentFake("function_contents", (INPUT,))),
            id="unbracketed-contents",
        ),
        pytest.param(
            function(
                contents(INPUT, SegmentFake("comma"), SegmentFake("lambda_expression"))
            ),
            id="unknown-argument-shape",
        ),
    ],
)
def test_unrecognized_tree_is_not_convertible(segment: SegmentFake) -> None:
    """Unknown structures must never be treated as a compatible call."""
    assert recognize(segment) is None


def test_recognized_arguments_keep_their_identity_and_order() -> None:
    """Recognizing a call must preserve its argument nodes for later rebuilding."""
    result = recognize(function(contents(INPUT, SegmentFake("comma"), NAMED)))
    assert result is not None
    assert result.name is NAME.segments[0]
    assert result.arguments == (INPUT, NAMED)
    assert result.arguments[0] is INPUT
    assert result.arguments[1] is NAMED


@pytest.mark.parametrize(
    "expression,expected",
    [
        (
            "REPLACE(LOWER(TRIM(foo)), 'a', 'b')",
            "(foo).TRIM().LOWER().REPLACE('a', 'b')",
        ),
        ("LOWER(TRIM(a || b))", "(a || b).TRIM().LOWER()"),
        (
            "REPLACE(LOWER(foo), LOWER(TRIM(bar)), 'x')",
            "(foo).LOWER().REPLACE(LOWER(TRIM(bar)), 'x')",
        ),
    ],
)
def test_building_fix_preserves_original_tree(expression: str, expected: str) -> None:
    """Planning a replacement must preserve original parents and source markers."""
    config = FluffConfig(
        configs={
            "rules": {
                "convention.prefer_chained_functions": {"force_enable": True},
                "layout.chained_functions": {"writing_style": "one_liner"},
            }
        },
        overrides={"dialect": "bigquery", "rules": "CV14"},
    )
    linter = Linter(config=config)
    parsed = linter.parse_string(f"SELECT {expression} AS cleaned FROM t;\n")
    assert parsed.tree is not None and not parsed.violations
    root = parsed.tree
    before_tree = root.stringify()
    before = [
        (segment, segment.get_parent(), segment.pos_marker)
        for segment in root.recursive_crawl_all()
    ]
    rule = linter.get_rulepack().rules[0]
    context = RuleContext(
        dialect=config.get("dialect_obj"),
        fix=True,
        templated_file=parsed.parsed_variants[0].templated_file,
        path=None,
        config=config,
        segment=root,
    )
    result = rule._eval(next(rule.crawl_behaviour.crawl(context)))
    assert result is not None and not isinstance(result, list)
    assert len(result.fixes) == 1
    assert result.fixes[0].edit is not None
    assert "".join(segment.raw for segment in result.fixes[0].edit) == expected
    assert root.stringify() == before_tree
    for segment, parent, position in before:
        assert segment.pos_marker is position
        current_parent = segment.get_parent()
        if parent is None:
            assert current_parent is None
        else:
            assert current_parent is not None, segment.raw
            assert current_parent[0] is parent[0], segment.raw
            assert current_parent[1] == parent[1], segment.raw
