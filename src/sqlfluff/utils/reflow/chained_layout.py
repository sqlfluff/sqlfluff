"""Shared layout analysis for chained function calls."""

from collections.abc import Sequence
from typing import Any

from sqlfluff.core.config import FluffConfig
from sqlfluff.core.errors import SQLFluffUserError
from sqlfluff.core.parser import BaseSegment
from sqlfluff.utils.reflow.helpers import deduce_line_indent

STYLES = ("consistent", "one_liner", "aligned", "indented")
RULE_NAME = "layout.chained_functions"
DEFAULT_STYLE = "consistent"


def validate_style(value: Any) -> str:
    """Reject unsupported configuration values before evaluating SQL."""
    if not isinstance(value, str) or value not in STYLES:
        raise SQLFluffUserError(f"writing_style must be one of {STYLES}; got {value!r}")
    return value


def configured_style(config: FluffConfig, *, rule_name: str = RULE_NAME) -> str:
    """Match SQLFluff's specific-rule, general-rule, then default precedence."""
    general = config.get("writing_style", ["rules"], default=DEFAULT_STYLE)
    return validate_style(
        config.get("writing_style", ["rules", rule_name], default=general)
    )


def preceding_gap(siblings: Sequence[BaseSegment]) -> list[BaseSegment]:
    """Collect the non-code siblings immediately before a chained call."""
    gap = []
    for segment in reversed(siblings):
        if segment.is_code:
            break
        gap.append(segment)
    return list(reversed(gap))


def input_indent(siblings: Sequence[BaseSegment], root: BaseSegment) -> str:
    """Find the input indentation without inheriting another chain's offset."""
    chain_input = next(
        seg
        for seg in reversed(siblings)
        if seg.is_code and not seg.is_type("chained_function_call")
    )
    first_raw = chain_input.raw_segments[0]
    indent = deduce_line_indent(first_raw, root)
    if first_raw.pos_marker and first_raw.pos_marker.working_line_pos > len(indent) + 1:
        # In `(foo).LOWER() || (bar).TRIM()`, bar shares the line of a call
        # belonging to another group. Its line indent includes that group's
        # extra level, so use the containing expression's original anchor.
        expression_start = next(seg for seg in siblings if seg.is_code)
        return deduce_line_indent(expression_start.raw_segments[0], root)
    return indent


def infer_style(
    call: BaseSegment,
    siblings: Sequence[BaseSegment],
    root: BaseSegment,
    tab_size: int,
) -> str:
    """Classify a chain by its first call boundary, including mixed chains."""
    if not any(seg.is_type("newline") for seg in preceding_gap(siblings)):
        return "one_liner"
    base_indent = input_indent(siblings, root)
    call_indent = deduce_line_indent(call.raw_segments[0], root)
    if len(call_indent.expandtabs(tab_size)) > len(base_indent.expandtabs(tab_size)):
        return "indented"
    return "aligned"


def style_for_tree(
    root: BaseSegment, config: FluffConfig, *, rule_name: str = RULE_NAME
) -> str:
    """Resolve the file's style independently of a rule or reflow caller."""
    style = configured_style(config, rule_name=rule_name)
    if style != "consistent":
        return style
    first = next(root.recursive_crawl("chained_function_call"), None)
    if first is None:
        return "one_liner"
    path = root.path_to(first)
    parent_step = path[-1]
    return infer_style(
        first,
        parent_step.segment.segments[: parent_step.idx],
        root,
        config.get("tab_space_size", ["indentation"]),
    )
