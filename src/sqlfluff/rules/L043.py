"""Implementation of Rule L043."""
from typing import List, Optional

from sqlfluff.core.parser import (
    WhitespaceSegment,
    SymbolSegment,
    KeywordSegment,
)
from sqlfluff.core.parser.segments.base import BaseSegment

from sqlfluff.core.rules.base import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.doc_decorators import document_fix_compatible


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
        # Generate list of segments to delete.
        # Everything but the column reference segment.
        delete_segments = []
        for s in context.segment.segments:
            if s != coalesce_arg_1:
                delete_segments.append(s)
        # Add coalesce and opening parenthesis.
        edits = []
        if preceding_not:
            edits.extend(
                [
                    KeywordSegment("not"),
                    WhitespaceSegment(),
                ]
            )
        edits.extend(
            [
                KeywordSegment("coalesce"),
                SymbolSegment("(", name="start_bracket", type="start_bracket"),
            ]
        )
        edit_coalesce_target = context.segment.segments[0]
        fixes = []
        fixes.append(
            LintFix.replace(
                edit_coalesce_target,
                edits,
            )
        )
        # Add comma, bool, closing parenthesis.
        closing_parenthesis = [
            SymbolSegment(",", name="comma", type="comma"),
            WhitespaceSegment(),
            coalesce_arg_2,
            SymbolSegment(")", name="end_bracket", type="end_bracket"),
        ]
        fixes.append(
            LintFix.replace(
                context.segment.segments[coalesce_arg_1_idx + 1],
                closing_parenthesis,
            )
        )
        # Generate a "delete" action for each segment in
        # delete_segments EXCEPT the one being edited to become a call
        # to "coalesce(". Deleting and editing the same segment has
        # unpredictable behavior.
        fixes += [
            LintFix.delete(s) for s in delete_segments if s is not edit_coalesce_target
        ]
        return fixes

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Unnecessary CASE statement. Use COALESCE function instead."""
        # Look for CASE expression.
        if (
            context.segment.is_type("case_expression")
            and context.segment.segments[0].name == "case"
        ):
            # We can't reduce CASE expressions with multiple WHEN clauses.
            if (
                len(
                    [
                        segment
                        for segment in context.segment.segments
                        if segment.name == "when"
                    ]
                )
                > 1
            ):
                return None

            # Find condition expression.
            idx = 0
            while context.segment.segments[idx].name != "then":
                if context.segment.segments[idx].is_type("expression"):
                    condition_expression_idx = idx
                idx += 1

            # Find THEN result expression.
            while context.segment.segments[idx].name not in ["when", "else", "end"]:
                if context.segment.segments[idx].is_type("expression"):
                    then_expression_idx = idx
                idx += 1

            # Find ELSE result expression.
            else_found = False
            while context.segment.segments[idx].name not in ["when", "end"]:
                if context.segment.segments[idx].name == "else":
                    else_found = True
                if context.segment.segments[idx].is_type("expression"):
                    else_expression_idx = idx
                idx += 1

            # If no ELSE segment is found then we cannot reduce the expression.
            if not else_found:
                return None

            condition_expression = context.segment.segments[condition_expression_idx]
            then_expression = context.segment.segments[then_expression_idx]
            else_expression = context.segment.segments[else_expression_idx]

            # Method 1: Check if THEN/ELSE expressions are both Boolean and can therefore be reduced.
            upper_bools = ["TRUE", "FALSE"]
            if (
                (then_expression.raw_upper in upper_bools)
                and (else_expression.raw_upper in upper_bools)
                and (then_expression.raw_upper != else_expression.raw_upper)
            ):
                coalesce_arg_1 = condition_expression
                coalesce_arg_2 = KeywordSegment("false")
                coalesce_arg_1_idx = condition_expression_idx
                preceding_not = then_expression.raw_upper == "FALSE"

                fixes = self._coalesce_fix_list(
                    context,
                    coalesce_arg_1,
                    coalesce_arg_2,
                    coalesce_arg_1_idx,
                    preceding_not,
                )

                return LintResult(
                    anchor=context.segment.segments[condition_expression_idx],
                    fixes=fixes,
                )

            # Method 2: Check if the condition expression is comparing a column reference to NULL
            # and whether that column reference is also in either the THEN/ELSE expression.
            # We can only apply this method when there is only one condition in the condition expression.
            condition_expression_segments_raw = {
                segment.raw_upper for segment in condition_expression.segments
            }
            if {"IS", "NULL"}.issubset(condition_expression_segments_raw) and (
                not condition_expression_segments_raw.intersection({"AND", "OR"})
            ):
                # Check if the comparison is to NULL or NOT NULL.
                if "NOT" in condition_expression_segments_raw:
                    is_not_prefix = True
                else:
                    is_not_prefix = False

                # Locate column reference in condition expression.
                column_reference_segment = next(
                    (
                        segment
                        for segment in condition_expression.segments
                        if segment.type == "column_reference"
                    ),
                    None,
                )

                # Return None if no column reference is detected (this condition does not apply to functions).
                if not column_reference_segment:
                    return None

                # Check if we can reduce the CASE expression to a single coalesce function.
                if (
                    not is_not_prefix
                    and column_reference_segment.raw_upper == else_expression.raw_upper
                ):
                    coalesce_arg_1 = else_expression
                    coalesce_arg_2 = then_expression
                    coalesce_arg_1_idx = else_expression_idx
                elif (
                    is_not_prefix
                    and column_reference_segment.raw_upper == then_expression.raw_upper
                ):
                    coalesce_arg_1 = then_expression
                    coalesce_arg_2 = else_expression
                    coalesce_arg_1_idx = then_expression_idx
                else:
                    return None

                fixes = self._coalesce_fix_list(
                    context,
                    coalesce_arg_1,
                    coalesce_arg_2,
                    coalesce_arg_1_idx,
                )

                return LintResult(
                    anchor=context.segment.segments[condition_expression_idx],
                    fixes=fixes,
                )

        return None
