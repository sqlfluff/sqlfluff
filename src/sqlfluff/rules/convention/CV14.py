"""Implementation of Rule CV14."""

from collections.abc import Sequence
from dataclasses import dataclass

from sqlfluff.core.parser import (
    BaseSegment,
    BracketedSegment,
    Dedent,
    Indent,
    NewlineSegment,
    PositionMarker,
    SymbolSegment,
    WhitespaceSegment,
)
from sqlfluff.core.rules import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.utils.reflow.chained_layout import RULE_NAME, style_for_tree
from sqlfluff.utils.reflow.helpers import deduce_line_indent
from sqlfluff.utils.reflow.reindent import construct_single_indent


@dataclass(frozen=True)
class FunctionCall:
    """A simple function name and its ordered, comma-separated arguments."""

    name: BaseSegment
    arguments: tuple[BaseSegment, ...]


def function_call(segment: BaseSegment) -> FunctionCall | None:
    """Recognize the subset whose first argument can become a chained input.

    Special syntax, window clauses, multipart names and aggregate modifiers
    deliberately remain outside the supported subset. Conditional expressions
    are also excluded, because their short-circuit behavior needs separate review.
    """
    if not segment.is_type("function"):
        return None
    children = [s for s in segment.segments if s.is_code]
    if len(children) != 2 or not children[0].is_type("function_name"):
        return None
    name, contents = children
    identifiers = [s for s in name.segments if s.is_code]
    if len(identifiers) != 1 or not identifiers[0].is_type("function_name_identifier"):
        return None
    # A quoted multipart name can be a single identifier token. It still
    # needs BigQuery's parenthesized function-name syntax in a chain.
    if not identifiers[0].raw.isidentifier():
        return None
    if name.raw_upper in {
        "GROUPING",
        "IF",
        "IFNULL",
        "NULLIF",
        "COALESCE",
        "UNNEST",
        "ARRAY",
    }:
        return None
    if not contents.is_type("function_contents"):
        return None
    content_children = [s for s in contents.segments if s.is_code]
    if len(content_children) != 1 or not content_children[0].is_type("bracketed"):
        return None
    bracket = content_children[0]
    items = [s for s in bracket.segments if s.is_code][1:-1]
    if not items or len(items) % 2 == 0 or not items[0].is_type("expression"):
        return None
    for index, item in enumerate(items):
        if index % 2:
            if not item.is_type("comma"):
                return None
        elif not item.is_type("expression", "named_argument"):
            return None
    return FunctionCall(identifiers[0], tuple(items[::2]))


def sole_function(expression: BaseSegment) -> BaseSegment | None:
    """Unwrap grouping parentheses, but never cross operators or accessors."""
    current = expression
    while current.is_type("expression", "bracketed"):
        children = [
            s
            for s in current.segments
            if s.is_code and not s.is_type("start_bracket", "end_bracket")
        ]
        if len(children) != 1:
            return None
        current = children[0]
    return current if current.is_type("function") else None


def bracketed(
    contents: Sequence[BaseSegment], position: PositionMarker
) -> BracketedSegment:
    """Build parser-shaped brackets around copies of the supplied contents."""
    start = SymbolSegment(
        "(", type="start_bracket", pos_marker=position.start_point_marker()
    )
    end = SymbolSegment(")", type="end_bracket", pos_marker=position.end_point_marker())
    return BracketedSegment(
        segments=(
            start,
            Indent(pos_marker=position.start_point_marker()),
            # Attaching children updates their parent links. Keep the source
            # tree intact while constructing the proposed replacement.
            *(segment.copy() for segment in contents),
            Dedent(pos_marker=position.end_point_marker()),
            end,
        ),
        start_bracket=(start,),
        end_bracket=(end,),
    )


def unpositioned_copy(segment: BaseSegment) -> BaseSegment:
    """Let the fix loop position copied containers around the moved tokens.

    A new container can inherit the same starting position as its replacement
    while containing tokens that moved inside it. Clearing the copy's marker
    forces recursive realignment; leaves retain their original source slices.
    """
    children = tuple(unpositioned_copy(child) for child in segment.segments)
    copied = segment.copy(segments=children)
    if children:
        copied.pos_marker = None
    return copied


class Rule_CV14(BaseRule):
    """Prefer chained calls for compatible nested BigQuery functions.

    This convention is disabled by default. Set ``force_enable = True`` to
    enable conversion; other dialects are always skipped. Layout is controlled
    by ``writing_style`` in ``layout.chained_functions``. With ``consistent``,
    use the first existing chain's style, or ``one_liner`` if there is no chain.

    Converts at least two ordinary calls nested through their first positional
    argument. Special syntax, multipart or quoted function names, aggregate
    modifiers, window clauses and conditional expressions are not converted.
    Expressions containing comments or template expansions are left unchanged.

    **Anti-pattern**

    .. code-block:: sql

        SELECT LOWER(TRIM(foo)) FROM t;

    **Best practice**

    .. code-block:: sql

        SELECT (foo).TRIM().LOWER() FROM t;
    """

    name = "convention.prefer_chained_functions"
    groups = ("all", "convention")
    config_keywords = ["force_enable"]
    force_enable: bool
    crawl_behaviour = SegmentSeekerCrawler({"function"})
    is_fix_compatible = True
    layout_rule_name: str = RULE_NAME

    def _eval(self, context: RuleContext) -> LintResult | None:
        if not self.force_enable or context.dialect.name != "bigquery":
            return None
        memory = context.memory or {}
        replaced = memory.setdefault("replaced", set())
        if any(parent.uuid in replaced for parent in context.parent_stack):
            return LintResult(memory=memory)

        # A whole-expression rewrite must not drop comments or copy rendered
        # template output into the source. Leave these areas for a later design.
        enclosing_functions = [
            s for s in (*context.parent_stack, context.segment) if s.is_type("function")
        ]
        if any(
            any(raw.is_comment for raw in fn.raw_segments)
            or (fn.pos_marker is not None and not fn.pos_marker.is_literal())
            for fn in enclosing_functions
        ):
            return LintResult(memory=memory)

        steps: list[FunctionCall] = []
        current = context.segment
        while (call := function_call(current)) is not None:
            steps.append(call)
            nested = sole_function(call.arguments[0])
            if nested is None:
                break
            current = nested
        if len(steps) < 2:
            return LintResult(memory=memory)

        root = context.parent_stack[0]
        if "style" not in memory:
            # Infer from an original existing chain, before adding any new ones.
            memory["style"] = style_for_tree(
                root, context.config, rule_name=self.layout_rule_name
            )
        style = memory["style"]
        indent = deduce_line_indent(context.segment.raw_segments[0], root)
        if style == "indented":
            indent += construct_single_indent(
                context.config.get("indent_unit", ["indentation"]),
                context.config.get("tab_space_size", ["indentation"]),
            )

        chain_input = steps[-1].arguments[0]
        assert chain_input.pos_marker is not None
        parts: list[BaseSegment] = [bracketed([chain_input], chain_input.pos_marker)]
        chain_class = context.dialect.get_segment("ChainedFunctionCallSegment")
        for step in reversed(steps):
            assert step.name.pos_marker is not None
            call_point = step.name.pos_marker.start_point_marker()
            arguments: list[BaseSegment] = []
            for argument in step.arguments[1:]:
                if arguments:
                    assert argument.pos_marker is not None
                    argument_point = argument.pos_marker.start_point_marker()
                    arguments.extend(
                        [
                            SymbolSegment(",", type="comma", pos_marker=argument_point),
                            WhitespaceSegment(pos_marker=argument_point),
                        ]
                    )
                arguments.append(argument)
            if style != "one_liner":
                parts.append(NewlineSegment(pos_marker=call_point))
                if indent:
                    parts.append(WhitespaceSegment(indent, pos_marker=call_point))
            parts.append(
                chain_class(
                    segments=(
                        SymbolSegment(".", type="dot", pos_marker=call_point),
                        step.name.copy(),
                        bracketed(arguments, step.name.pos_marker.end_point_marker()),
                    )
                )
            )

        # Keep the parse-shaped expression flat when replacing a function
        # already inside an expression (e.g. one followed by another accessor).
        edit = parts
        if not context.parent_stack[-1].is_type("expression"):
            edit = [
                context.dialect.get_segment("ExpressionSegment")(segments=tuple(parts))
            ]
        replaced.add(context.segment.uuid)
        return LintResult(
            anchor=context.segment,
            fixes=[
                LintFix.replace(
                    context.segment,
                    [unpositioned_copy(segment) for segment in edit],
                    source=[context.segment],
                )
            ],
            memory=memory,
        )
