"""Implementation of Rule L065."""
from typing import List, Optional, Iterable

import sqlfluff.core.rules.functional.segment_predicates as sp
from sqlfluff.core.parser import BaseSegment, NewlineSegment
from sqlfluff.core.rules.base import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.doc_decorators import document_fix_compatible, document_groups


@document_groups
@document_fix_compatible
class Rule_L065(BaseRule):
    """Set operators should be surrounded by newlines.

    **Anti-pattern**

    In this example, `UNION ALL` is not on a line ifself.

    .. code-block:: sql

        SELECT 'a' AS col UNION ALL
        SELECT 'b' AS col

    **Best practice**

    .. code-block:: sql

        SELECT 'a' AS col
        UNION ALL
        SELECT 'b' AS col

    """

    groups = ("all",)

    _target_elems = ("set_operator",)

    def _eval(self, context: RuleContext) -> List[LintResult]:
        """Set operators should be surrounded by newlines.

        For any set operator we check if there is any NewLineSegment in the non-code
        segments preceeding or following it.

        In particular, as part of this rule we allow multiple NewLineSegments.
        """
        segment = context.functional.segment

        expression = segment.children()
        set_operator_segments = segment.children(sp.is_type(*self._target_elems))
        results: List[LintResult] = []

        # If len(set_operator) == 0 this will essentially not run
        for set_operator in set_operator_segments:
            preceeding_code = (
                expression.reversed().select(start_seg=set_operator).first(sp.is_code())
            )
            following_code = expression.select(start_seg=set_operator).first(
                sp.is_code()
            )
            res = {
                "before": expression.select(
                    start_seg=preceeding_code.get(), stop_seg=set_operator
                ),
                "after": expression.select(
                    start_seg=set_operator, stop_seg=following_code.get()
                ),
            }

            newline_before_set_operator = res["before"].first(sp.is_type("newline"))
            newline_after_set_operator = res["after"].first(sp.is_type("newline"))

            # If there is a whitespace directly preceeding/following the set operator we
            # are replacing it with a newline later.
            preceeding_whitespace = res["before"].first(sp.is_type("whitespace")).get()
            following_whitespace = res["after"].first(sp.is_type("whitespace")).get()

            if newline_before_set_operator and newline_after_set_operator:
                continue
            elif not newline_before_set_operator and newline_after_set_operator:
                results.append(
                    LintResult(
                        anchor=set_operator,
                        description=(
                            "Set operators should be surrounded by newlines. "
                            f"Missing newline before set operator {set_operator.raw}."
                        ),
                        fixes=_generate_fixes(whitespace_segment=preceeding_whitespace),
                    )
                )
            elif newline_before_set_operator and not newline_after_set_operator:
                results.append(
                    LintResult(
                        anchor=set_operator,
                        description=(
                            "Set operators should be surrounded by newlines. "
                            f"Missing newline after set operator {set_operator.raw}."
                        ),
                        fixes=_generate_fixes(whitespace_segment=following_whitespace),
                    )
                )
            else:
                preceeding_whitespace_fixes = _generate_fixes(
                    whitespace_segment=preceeding_whitespace
                )
                following_whitespace_fixes = _generate_fixes(
                    whitespace_segment=following_whitespace
                )

                # make mypy happy
                assert isinstance(preceeding_whitespace_fixes, Iterable)
                assert isinstance(following_whitespace_fixes, Iterable)

                fixes = []
                fixes.extend(preceeding_whitespace_fixes)
                fixes.extend(following_whitespace_fixes)

                results.append(
                    LintResult(
                        anchor=set_operator,
                        description=(
                            "Set operators should be surrounded by newlines. "
                            "Missing newline before and after set operator "
                            f"{set_operator.raw}."
                        ),
                        fixes=fixes,
                    )
                )

        return results


def _generate_fixes(
    whitespace_segment: BaseSegment,
) -> Optional[List[LintFix]]:

    if whitespace_segment:
        return [
            LintFix.replace(
                anchor_segment=whitespace_segment,
                # NB: Currently we are just inserting a Newline here. This alone will
                # produce not properly indented SQL. We rely on L003 to deal with
                # indentation later.
                # As a future improvement we could maybe add WhitespaceSegment( ... )
                # here directly.
                edit_segments=[NewlineSegment()],
            )
        ]
    else:
        # We should rarely reach here as set operators are always surrounded by either
        # WhitespaceSegment or NewlineSegment.
        # However, in exceptional cases the WhitespaceSegment might be enclosed in the
        # surrounding segment hierachy and not accessible by the rule logic.
        # At the time of writing this is true for `tsql` as covered in the test
        # `test_fail_autofix_in_tsql_disabled`. If we encounter such case, we skip
        # fixing.
        return []
