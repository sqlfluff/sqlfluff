"""Implementation of Rule L007."""
import copy
from typing import List, Optional
from sqlfluff.core.parser.segments.base import BaseSegment
from sqlfluff.core.rules.base import BaseRule, LintFix, LintResult, RuleContext
import sqlfluff.core.rules.functional.segment_predicates as sp

from sqlfluff.core.rules.doc_decorators import (
    document_configuration,
    document_fix_compatible,
)
from sqlfluff.core.rules.functional.segments import Segments

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

    def _eval(self, context: RuleContext) -> Optional[List[LintResult]]:
        """Operators should follow a standard for being before/after newlines.

        We use the memory to keep track of whitespace up to now, and
        whether the last code segment was an operator or not.
        Anchor is our signal as to whether there's a problem.

        We only trigger if we have an operator FOLLOWED BY a newline
        before the next meaningful code segment.

        """
        relevent_types = ["binary_operator", "comparison_operator"]
        segment = context.functional.segment
        # bring var to this scope so as to only have one type ignore
        operator_new_lines: str = self.operator_new_lines  # type: ignore
        expr = segment.children()
        operator_segments = segment.children(sp.is_type(*relevent_types))
        results: List[LintResult] = []
        # If len(operator_segments) == 0 this will essentially not run
        for operator in operator_segments:
            start = expr.reversed().select(start_seg=operator).first(sp.is_code())
            end = expr.select(start_seg=operator).first(sp.is_code())
            res = [
                expr.select(start_seg=start.get(), stop_seg=operator),
                expr.select(start_seg=operator, stop_seg=end.get()),
            ]
            # anchor and change els are reversed in the before case
            if operator_new_lines == "before":
                res = [els.reversed() for els in reversed(res)]

            change_list, anchor_list = res
            # If the anchor side of the list has no newline
            # then everything is ok already
            if not anchor_list.any(sp.is_name("newline")):
                continue

            insert_anchor = anchor_list.last().get()
            assert insert_anchor, "Insert Anchor must be present"
            lint_res = _generate_fixes(
                operator_new_lines,
                change_list,
                operator,
                insert_anchor,
            )
            results.append(lint_res)

        if len(results) == 0:
            return None
        return results


def _generate_fixes(
    operator_new_lines: str,
    change_list: Segments,
    operator: BaseSegment,
    insert_anchor: BaseSegment,
) -> LintResult:
    # Duplicate the change list and append the operator
    inserts: List[BaseSegment] = [
        *change_list,
        operator,
    ]

    if operator_new_lines == "before":
        # We do yet another reverse here,
        # This could be avoided but makes all "changes" relate to "before" config state
        inserts = [*reversed(inserts)]

    # ensure to insert in the right place
    edit_type = "create_before" if operator_new_lines == "before" else "create_after"
    fixes = [
        # Insert elements reversed
        LintFix(
            edit_type=edit_type,
            edit=map(lambda el: copy.deepcopy(el), reversed(inserts)),
            anchor=insert_anchor,
        ),
        # remove the Op
        LintFix.delete(operator),
        # Delete the original elements (related to insert)
        *change_list.apply(LintFix.delete),
    ]
    desc = before_description if operator_new_lines == "before" else after_description
    return LintResult(
        anchor=operator,
        description=desc,
        fixes=fixes,
    )
