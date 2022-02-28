"""Implementation of Rule L007."""
import copy
from typing import List, Optional, Tuple, cast
from sqlfluff.core.parser.segments.base import BaseSegment
from sqlfluff.core.rules.base import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.doc_decorators import (
    document_configuration,
    document_fix_compatible,
)

after_description = "Operators near newlines should be after, not before the newline"
before_description = "Operators near newlines should be before, not after the newline"


@document_fix_compatible
@document_configuration
class Rule_L007(BaseRule):
    """Operators should follow a standard for being before/after newlines.

    **Anti-pattern**

    In this example, if ``operator_new_lines = after`` (or unspecified, as is the
    default), then the operator ``+`` should not be at the end of the second line.

    .. code-block:: sql

        SELECT
            a +
            b
        FROM foo


    **Best practice**

    If ``operator_new_lines = after`` (or unspecified, as this is the default),
    place the operator after the newline.

    .. code-block:: sql

        SELECT
            a
            + b
        FROM foo

    If ``operator_new_lines = before``, place the operator before the newline.

    .. code-block:: sql

        SELECT
            a +
            b
        FROM foo
    """

    config_keywords = ["operator_new_lines"]

    def _eval(self, context: RuleContext) -> LintResult:
        """Operators should follow a standard for being before/after newlines.

        We use the memory to keep track of whitespace up to now, and
        whether the last code segment was an operator or not.
        Anchor is our signal as to whether there's a problem.

        We only trigger if we have an operator FOLLOWED BY a newline
        before the next meaningful code segment.

        """
        anchor = None
        memory = context.memory
        parent_stack = context.parent_stack
        fixes: List[LintFix] = []
        # bring var to this scope so as to only have one type ignore
        operator_new_lines: str = self.operator_new_lines  # type: ignore
        description = after_description
        if operator_new_lines == "before":
            description = before_description

        # The parent stack tells us whether we're in an expression or not.
        is_relavent_segment = parent_stack and parent_stack[-1].is_type("expression")
        if not is_relavent_segment:
            # Reset the memory if we're not in an expression
            memory = {"last_code": None, "since_code": []}
            return LintResult(memory=memory)

        if not context.segment.is_code:
            # This isn't a code segment...
            # Prepare memory for later
            memory["since_code"].append(context.segment)
            return LintResult(memory=memory)

        # This is code, what kind?
        if context.segment.is_type("binary_operator", "comparison_operator"):
            # If it's an operator, then check if in "before" mode
            if operator_new_lines == "before":
                # If we're in "before" mode, then check if newline since last
                # code
                for s in memory["since_code"]:
                    if s.name == "newline":
                        anchor = context.segment
                        # Had a newline - so mark this operator as a fail

        elif memory["last_code"] and memory["last_code"].is_type(
            "binary_operator", "comparison_operator"
        ):
            # It's not an operator, but the last code was.
            if operator_new_lines != "before":
                # If in "after" mode, then check to see
                # there is a newline between us and the last operator.
                for s in memory["since_code"]:
                    if s.name == "newline":
                        # Had a newline - so mark last operator as a fail
                        anchor = memory["last_code"]

        # Prepare memory for later
        memory["last_code"] = context.segment
        memory["since_code"] = []

        # Anchor is our signal as to whether there's a problem
        if not anchor:
            return LintResult(memory=memory)

        expr = cast(Tuple[BaseSegment], parent_stack[-1].segments)
        fixes = _generate_fixes(expr, anchor, operator_new_lines)
        return LintResult(
            anchor=anchor,
            memory=memory,
            description=description,
            fixes=fixes,
        )


def _generate_fixes(
    expr: Tuple[BaseSegment],
    anchor: BaseSegment,
    operator_new_lines: str,
) -> List[LintFix]:
    """Generate Fixes.

    Take operator_new_lines==after as the default case.
    Consider "before" as a modification on this behaviour.

    """
    fixes = [LintFix.delete(anchor)]
    res = list(_get_surrounding_segments(expr, anchor))
    if operator_new_lines == "before":
        res = [list(reversed(els)) for els in reversed(res)]

    change_list, anchor_list = res
    insert_anchor = anchor_list[-1]
    change_list = change_list[1:]
    for el in change_list:
        fixes.append(LintFix.delete(el))

    change_list.append(anchor)
    if operator_new_lines == "before":
        # We do yet another reverse here,
        # This could be avoided but makes all "changes" relate to "before" config state
        change_list = list(reversed(change_list))

    change_list = list(map(_copy_el, reversed(change_list)))
    edit_type = "create_after" if operator_new_lines == "before" else "create_before"
    fixes.append(
        LintFix(
            edit_type=edit_type,
            edit=change_list,
            anchor=insert_anchor,
        )
    )
    return fixes


def _copy_el(segment: BaseSegment):
    """Safely duplicate segment without position markers."""
    el = copy.deepcopy(segment)
    el.pos_marker = None  # type: ignore
    return el


def _get_surrounding_segments(
    expr: Tuple[BaseSegment],
    symbol: BaseSegment,
) -> Tuple[List[BaseSegment], List[BaseSegment]]:
    """Create two lists of symbols surrounding operator.

    1 from last code to operator/symbol,
    2 from operator to next code

    """
    before_list: List[BaseSegment] = []
    after_list: List[BaseSegment] = []
    start_code: Optional[BaseSegment] = None
    symbol_hit = False
    for el in expr:
        if el == symbol:
            symbol_hit = True
            continue
        if el.is_code:
            if symbol_hit:
                # Exit condition, we have found code on the other side of the operator
                after_list.append(el)
                return before_list, after_list

            start_code = el
            before_list = []
            after_list = []

        if symbol_hit:
            after_list.append(el)
            continue

        if start_code:
            before_list.append(el)
    # This code is unreachable if a valid expr and symbol/operator segment are passed.
    raise Exception("Ivalid Expr: must contain binary_operator or comparison_operator")
