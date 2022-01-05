"""Implementation of Rule L043."""
from typing import List, NamedTuple, Optional

from sqlfluff.core.parser import (
    RawSegment,
    WhitespaceSegment,
    SymbolSegment,
    KeywordSegment,
)
from sqlfluff.core.parser.segments.base import BaseSegment

from sqlfluff.core.rules.base import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.doc_decorators import document_fix_compatible
from sqlfluff.core.rules.functional import Segments, sp


class CaseExpressionInfo(NamedTuple):
    """Segments in the "WHEN" or "THEN" expression."""

    parent: BaseSegment  # parent segment (when_clause or then_clause)
    expression: BaseSegment  # the expression itself
    after_expression: BaseSegment  # the segment following the expression


@document_fix_compatible
class Rule_L043(BaseRule):
    """Unnecessary ``CASE`` statement. Use ``COALESCE`` function instead.

    | **Anti-pattern**
    | ``CASE`` statement returns booleans.

    .. code-block:: sql
        :force:

        select
            case
                when fab > 0 then true
                else false
            end as is_fab
        from fancy_table

        -- This rule can also simplify ``CASE`` statements that aim to fill
        -- NULL values.

        select
            case
                when fab is null then 0
                else fab
            end as fab_clean
        from fancy_table

    | **Best practice**
    | Reduce to ``WHEN`` condition within ``COALESCE`` function.

    .. code-block:: sql
        :force:

        select
            coalesce(fab > 0, false) as is_fab
        from fancy_table

        -- To fill ``NULL`` values.

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
        # Add coalesce and opening parenthesis.
        edits: List[RawSegment] = (
            [
                KeywordSegment("not"),
                WhitespaceSegment(),
            ]
            if preceding_not
            else []
        ) + [
            KeywordSegment("coalesce"),
            SymbolSegment("(", name="start_bracket", type="start_bracket"),
        ]

        edit_coalesce_target = context.segment.segments[0]
        fixes = [
            LintFix.replace(
                edit_coalesce_target,
                edits,
            ),
            # Add comma, bool, closing parenthesis.
            LintFix.replace(
                coalesce_arg_1.after_expression,
                [
                    SymbolSegment(",", name="comma", type="comma"),
                    WhitespaceSegment(),
                    coalesce_arg_2,
                    SymbolSegment(")", name="end_bracket", type="end_bracket"),
                ],
                source=[coalesce_arg_2],
            ),
        ] + (
            # Segments to delete -- i.e. all child segments at both levels EXCEPT:
            # - 'CASE' keyword segment being edited to become a call to "coalesce("
            # - the overall 'when_clause' segment
            # - the 'WHEN' filter 'expression' segment
            # Re: The 'CASE' keyword segment: We avoid deleting this one because
            # deleting and editing the same segment has unpredictable behavior.
            context.functional.segment.children(
                lambda s: s not in [edit_coalesce_target, coalesce_arg_1.parent]
            )
            + Segments(coalesce_arg_1.parent).children(
                lambda s: s is not coalesce_arg_1.expression
            )
        ).apply(
            lambda s: LintFix.delete(s)
        )
        return fixes

    @staticmethod
    def _build_case_expression_info(
        clause_segment: BaseSegment, expr_idx: int
    ) -> CaseExpressionInfo:
        for idx, segment in enumerate(clause_segment.segments):
            if segment.is_type("expression"):
                if expr_idx:
                    expr_idx -= 1
                else:
                    break
        return CaseExpressionInfo(
            clause_segment, segment, clause_segment.segments[idx + 1]
        )

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Unnecessary CASE statement. Use COALESCE function instead."""
        # Look for CASE expression.
        if (
            context.segment.is_type("case_expression")
            and context.segment.segments[0].name == "case"
        ):
            # Find all 'WHEN' clauses and the optional 'ELSE' clause.
            children = context.functional.segment.children()
            when_clauses = children.select(sp.is_type("when_clause"))
            else_clauses = children.select(sp.is_type("else_clause"))

            # Can't fix if either or both of these hold:
            # - Multiple WHEN clauses
            # - No ELSE statement
            if len(when_clauses) > 1 or not else_clauses:
                return None

            # Find condition and then expressions.
            condition_expression = self._build_case_expression_info(when_clauses[0], 0)
            then_expression = self._build_case_expression_info(when_clauses[0], 1)
            else_expression = self._build_case_expression_info(else_clauses[0], 0)

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
                is_not_prefix = "NOT" in condition_expression_segments_raw

                # Locate column reference in condition expression.
                column_reference_segment = (
                    Segments(condition_expression.expression)
                    .children(sp.is_type("column_reference"))
                    .get()
                )

                # Return None if none found (this condition does not apply to functions).
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

                return LintResult(
                    anchor=condition_expression.expression,
                    fixes=self._coalesce_fix_list(
                        context,
                        coalesce_arg_1,
                        coalesce_arg_2,
                    ),
                )

        return None
