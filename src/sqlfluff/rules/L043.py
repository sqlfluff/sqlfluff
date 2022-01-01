"""Implementation of Rule L043."""
from typing import List, NamedTuple, Optional

from sqlfluff.core.parser import (
    WhitespaceSegment,
    SymbolSegment,
    KeywordSegment,
)
from sqlfluff.core.parser.segments.base import BaseSegment

from sqlfluff.core.rules.base import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.doc_decorators import document_fix_compatible


class CaseExpressionInfo(NamedTuple):
    """Segments in the "WHEN" or "THEN" expression."""

    parent: BaseSegment  # parent segment (when_clause or then_clause)
    expression: BaseSegment  # the expression itself
    after_expression: BaseSegment  # the segment following the expression


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
        coalesce_arg_1: CaseExpressionInfo,
        coalesce_arg_2: BaseSegment,
        preceding_not: bool = False,
    ) -> List[LintFix]:
        """Generate list of fixes to convert CASE statement to COALESCE function."""
        # Generate list of segments to delete -- everything but the column
        # reference segment.
        delete_segments = []
        for s in context.segment.segments + coalesce_arg_1.parent.segments:
            if s not in (coalesce_arg_1.parent, coalesce_arg_1.expression):
                delete_segments.append(s)
        # Add coalesce and opening parenthesis.
        edits = []
        if preceding_not:
            edits += [
                KeywordSegment("not"),
                WhitespaceSegment(),
            ]
        edits += [
            KeywordSegment("coalesce"),
            SymbolSegment("(", name="start_bracket", type="start_bracket"),
        ]
        edit_coalesce_target = context.segment.segments[0]
        fixes = [
            LintFix.replace(
                edit_coalesce_target,
                edits,
            )
        ]
        # Add comma, bool, closing parenthesis.
        closing_parenthesis = [
            SymbolSegment(",", name="comma", type="comma"),
            WhitespaceSegment(),
            coalesce_arg_2,
            SymbolSegment(")", name="end_bracket", type="end_bracket"),
        ]
        fixes.append(
            LintFix.replace(
                coalesce_arg_1.after_expression,
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
            when_clauses = [
                segment
                for segment in context.segment.segments
                if segment.is_type("when_clause")
            ]
            if len(when_clauses) > 1:
                return None

            # Find condition and then expressions.
            for idx, child in enumerate(when_clauses[0].segments):
                if child.is_type("keyword"):
                    last_keyword = child.name
                if child.is_type("expression"):
                    info = CaseExpressionInfo(
                        when_clauses[0], child, when_clauses[0].segments[idx + 1]
                    )
                    if last_keyword == "when":
                        condition_expression = info
                    elif last_keyword == "then":
                        then_expression = info

            # Find ELSE result expression.
            else_clauses = [
                segment
                for segment in context.segment.segments
                if segment.is_type("else_clause")
            ]
            # If no ELSE segment is found then we cannot reduce the expression.
            if not else_clauses:
                return None

            for idx, segment in enumerate(else_clauses[0].segments):
                if segment.is_type("expression"):
                    else_expression = CaseExpressionInfo(
                        else_clauses[0], segment, else_clauses[0].segments[idx + 1]
                    )

            coalesce_arg_2: BaseSegment

            # Method 1: Check if THEN/ELSE expressions are both Boolean and can therefore be reduced.
            upper_bools = ["TRUE", "FALSE"]
            if (
                (then_expression.expression.raw_upper in upper_bools)
                and (else_expression.expression.raw_upper in upper_bools)
                and (
                    then_expression.expression.raw_upper
                    != else_expression.expression.raw_upper
                )
            ):
                coalesce_arg_1 = condition_expression
                coalesce_arg_2 = KeywordSegment("false")
                preceding_not = then_expression.expression.raw_upper == "FALSE"

                fixes = self._coalesce_fix_list(
                    context,
                    coalesce_arg_1,
                    coalesce_arg_2,
                    preceding_not,
                )

                return LintResult(
                    anchor=condition_expression.expression,
                    fixes=fixes,
                )

            # Method 2: Check if the condition expression is comparing a column reference to NULL
            # and whether that column reference is also in either the THEN/ELSE expression.
            # We can only apply this method when there is only one condition in the condition expression.
            condition_expression_segments_raw = {
                segment.raw_upper
                for segment in condition_expression.expression.segments
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
                        for segment in condition_expression.expression.segments
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
                    and column_reference_segment.raw_upper
                    == else_expression.expression.raw_upper
                ):
                    coalesce_arg_1 = else_expression
                    coalesce_arg_2 = then_expression.expression
                elif (
                    is_not_prefix
                    and column_reference_segment.raw_upper
                    == then_expression.expression.raw_upper
                ):
                    coalesce_arg_1 = then_expression
                    coalesce_arg_2 = else_expression.expression
                else:
                    return None

                fixes = self._coalesce_fix_list(
                    context,
                    coalesce_arg_1,
                    coalesce_arg_2,
                )

                return LintResult(
                    anchor=condition_expression.expression,
                    fixes=fixes,
                )

        return None
