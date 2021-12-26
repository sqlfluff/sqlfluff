"""Implementation of Rule L043."""
from typing import List, Optional

from sqlfluff.core.parser import (
    WhitespaceSegment,
    SymbolSegment,
    KeywordSegment,
    RawSegment,
)
from sqlfluff.core.parser.segments.base import BaseSegment

from sqlfluff.core.rules.base import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.doc_decorators import document_fix_compatible
import sqlfluff.core.rules.functional.segment_predicates as sp


@document_fix_compatible
class Rule_L043(BaseRule):
    """Unnecessary CASE statement. Use COALESCE function instead.

    | **Anti-pattern**
    | CASE statement returns booleans.

    .. code-block:: sql
        :force:

        select
            case
                when fab > 0 then true
                else false
            end as is_fab
        from fancy_table

        -- We can also simplify CASE statements that aim to fill NULL values.

        select
            case
                when fab is null then 0
                else fab
            end as fab_clean
        from fancy_table

    | **Best practice**
    | Reduce to WHEN condition within COALESCE function.

    .. code-block:: sql
        :force:

        select
            coalesce(fab > 0, false) as is_fab
        from fancy_table

        -- To fill NULL values.

        select
            coalesce(fab, 0) as fab_clean
        from fancy_table

    """

    @staticmethod
    def _coalesce_fix_list(
        context: RuleContext,
        coalesce_arg_1: BaseSegment,
        coalesce_arg_2: BaseSegment,
        coalesce_arg_1_idx: int,
        preceding_not: bool = False,
    ) -> List[LintFix]:
        """Generate list of fixes to convert CASE statement to COALESCE function.

        Returns:
            :obj:`List[LintFix]`.
        """
        # Add coalesce and opening parenthesis.
        edits: List[RawSegment]
        edits = [
            KeywordSegment("coalesce"),
            SymbolSegment("(", name="start_bracket", type="start_bracket"),
        ]
        if preceding_not:
            edits = [
                KeywordSegment("not"),
                WhitespaceSegment(),
            ] + edits
        edit_coalesce_target = context.segment.segments[0]
        fixes = [
            LintFix.replace(
                edit_coalesce_target,
                edits,
            ),
            # Add comma, bool, closing parenthesis.
            LintFix.replace(
                context.segment.segments[coalesce_arg_1_idx + 1],
                [
                    SymbolSegment(",", name="comma", type="comma"),
                    WhitespaceSegment(),
                    coalesce_arg_2,
                    SymbolSegment(")", name="end_bracket", type="end_bracket"),
                ],
            ),
        ] + (
            # Delete all child segments EXCEPT:
            # - Column reference segment
            # - the one being edited to become a call to "coalesce("
            # Re: The latter -- deleting and editing the same segment has
            # unpredictable behavior.
            context.functional.segment.children(
                lambda seg: seg not in (coalesce_arg_1, edit_coalesce_target)
            ).apply(lambda seg: LintFix.delete(seg))
        )
        return fixes

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Unnecessary CASE statement. Use COALESCE function instead."""
        # Look for CASE expression.
        if (
            context.segment.is_type("case_expression")
            and context.segment.segments[0].name == "case"
        ):
            # We can't reduce CASE expressions with multiple WHEN clauses.
            children = context.functional.segment.children()
            if len(children.select(sp.is_name("when"))) > 1:
                return None

            # Find condition expression.
            condition_expression = children.select(
                sp.is_type("expression"), loop_while=sp.not_(sp.is_name("then"))
            )
            if condition_expression:
                condition_expression_idx = children.index(condition_expression[0])

                # Next, find THEN result expression.
                then_expression = children.select(
                    sp.is_type("expression"),
                    start_seg=condition_expression[0],
                    loop_while=sp.not_(sp.is_name("when", "else", "end")),
                )
                if then_expression:
                    then_expression_idx = children.index(then_expression[0])

                    # Finally, find the ELSE result expression.
                    else_or_expression = children.select(
                        sp.or_(sp.is_type("expression"), sp.is_name("else")),
                        start_seg=then_expression[0],
                        loop_while=sp.not_(sp.is_name("when", "end")),
                    )
                    # If no ELSE segment is found then we cannot reduce the expression.
                    else_expression = else_or_expression.first(sp.is_type("expression"))
                    if else_or_expression.first(sp.is_name("else")) and else_expression:
                        else_expression_idx = children.index(else_expression[0])

                        # Method 1: Check if THEN/ELSE expressions are both
                        # Boolean and can therefore be reduced.
                        upper_bools = ["TRUE", "FALSE"]
                        if (
                            (then_expression[0].raw_upper in upper_bools)
                            and (else_expression[0].raw_upper in upper_bools)
                            and (
                                then_expression[0].raw_upper
                                != else_expression[0].raw_upper
                            )
                        ):
                            return LintResult(
                                anchor=condition_expression[0],
                                fixes=self._coalesce_fix_list(
                                    context,
                                    condition_expression[0],
                                    KeywordSegment("false"),
                                    condition_expression_idx,
                                    then_expression[0].raw_upper == "FALSE",
                                ),
                            )

            # Method 2: Check if the condition expression is comparing a column reference to NULL
            # and whether that column reference is also in either the THEN/ELSE expression.
            # We can only apply this method when there is only one condition in the condition expression.
            condition_expression_segments_raw = set(
                condition_expression.children().apply(lambda seg: seg.raw_upper)
            )
            if {"IS", "NULL"}.issubset(condition_expression_segments_raw) and (
                not condition_expression_segments_raw.intersection({"AND", "OR"})
            ):
                # Check if the comparison is to NULL or NOT NULL.
                is_not_prefix = "NOT" in condition_expression_segments_raw

                # Locate column reference in condition expression.
                column_reference_segment = condition_expression.children(
                    sp.is_type("column_reference")
                ).get()

                # Return None if no column reference is detected (this condition
                # does not apply to functions).
                if not column_reference_segment:
                    return None

                # Check if we can reduce the CASE expression to a single
                # coalesce function.
                if (
                    not is_not_prefix
                    and column_reference_segment.raw_upper
                    == else_expression[0].raw_upper
                ):
                    coalesce_arg_1 = else_expression[0]
                    coalesce_arg_2 = then_expression[0]
                    coalesce_arg_1_idx = else_expression_idx
                elif (
                    is_not_prefix
                    and column_reference_segment.raw_upper
                    == then_expression[0].raw_upper
                ):
                    coalesce_arg_1 = then_expression[0]
                    coalesce_arg_2 = else_expression[0]
                    coalesce_arg_1_idx = then_expression_idx
                else:
                    return None

                return LintResult(
                    anchor=condition_expression[0],
                    fixes=self._coalesce_fix_list(
                        context,
                        coalesce_arg_1,
                        coalesce_arg_2,
                        coalesce_arg_1_idx,
                    ),
                )

        return None
