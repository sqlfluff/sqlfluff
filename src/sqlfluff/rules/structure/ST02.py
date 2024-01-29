"""Implementation of Rule ST02."""

from typing import List, Optional, Tuple

from sqlfluff.core.parser import (
    KeywordSegment,
    SymbolSegment,
    WhitespaceSegment,
    WordSegment,
)
from sqlfluff.core.parser.segments.base import BaseSegment
from sqlfluff.core.rules import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.utils.functional import FunctionalContext, Segments, sp


class Rule_ST02(BaseRule):
    """Unnecessary ``CASE`` statement.

    **Anti-pattern**

    ``CASE`` statement returns booleans.

    .. code-block:: sql
        :force:

        select
            case
                when fab > 0 then true
                else false
            end as is_fab
        from fancy_table

        -- This rule can also simplify CASE statements
        -- that aim to fill NULL values.

        select
            case
                when fab is null then 0
                else fab
            end as fab_clean
        from fancy_table

        -- This also covers where the case statement
        -- replaces NULL values with NULL values.

        select
            case
                when fab is null then null
                else fab
            end as fab_clean
        from fancy_table

    **Best practice**

    Reduce to ``WHEN`` condition within ``COALESCE`` function.

    .. code-block:: sql
        :force:

        select
            coalesce(fab > 0, false) as is_fab
        from fancy_table

        -- To fill NULL values.

        select
            coalesce(fab, 0) as fab_clean
        from fancy_table

        -- NULL filling NULL.

        select fab as fab_clean
        from fancy_table


    """

    name = "structure.simple_case"
    aliases = ("L043",)
    groups: Tuple[str, ...] = ("all", "structure")
    crawl_behaviour = SegmentSeekerCrawler({"case_expression"})
    is_fix_compatible = True

    @staticmethod
    def _coalesce_fix_list(
        context: RuleContext,
        coalesce_arg_1: BaseSegment,
        coalesce_arg_2: BaseSegment,
        preceding_not: bool = False,
    ) -> List[LintFix]:
        """Generate list of fixes to convert CASE statement to COALESCE function."""
        # Add coalesce and opening parenthesis.
        edits = [
            WordSegment("coalesce", type="function_name_identifier"),
            SymbolSegment("(", type="start_bracket"),
            coalesce_arg_1,
            SymbolSegment(",", type="comma"),
            WhitespaceSegment(),
            coalesce_arg_2,
            SymbolSegment(")", type="end_bracket"),
        ]

        if preceding_not:
            not_edits: List[BaseSegment] = [
                KeywordSegment("not"),
                WhitespaceSegment(),
            ]
            edits = not_edits + edits

        fixes = [
            LintFix.replace(
                context.segment,
                edits,
            )
        ]
        return fixes

    @staticmethod
    def _column_only_fix_list(
        context: RuleContext,
        column_reference_segment: BaseSegment,
    ) -> List[LintFix]:
        """Generate list of fixes to reduce CASE statement to a single column."""
        fixes = [
            LintFix.replace(
                context.segment,
                [column_reference_segment],
            )
        ]
        return fixes

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Unnecessary CASE statement."""
        # Look for CASE expression.
        if context.segment.segments[0].raw_upper == "CASE":
            # Find all 'WHEN' clauses and the optional 'ELSE' clause.
            children = FunctionalContext(context).segment.children()
            when_clauses = children.select(sp.is_type("when_clause"))
            else_clauses = children.select(sp.is_type("else_clause"))

            # Can't fix if multiple WHEN clauses.
            if len(when_clauses) > 1:
                return None

            # Find condition and then expressions.
            condition_expression = when_clauses.children(sp.is_type("expression"))[0]
            then_expression = when_clauses.children(sp.is_type("expression"))[1]

            # Method 1: Check if THEN/ELSE expressions are both Boolean and can
            # therefore be reduced.
            if else_clauses:
                else_expression = else_clauses.children(sp.is_type("expression"))[0]
                upper_bools = ["TRUE", "FALSE"]
                if (
                    (then_expression.raw_upper in upper_bools)
                    and (else_expression.raw_upper in upper_bools)
                    and (then_expression.raw_upper != else_expression.raw_upper)
                ):
                    coalesce_arg_1: BaseSegment = condition_expression
                    coalesce_arg_2: BaseSegment = KeywordSegment("false")
                    preceding_not = then_expression.raw_upper == "FALSE"

                    fixes = self._coalesce_fix_list(
                        context,
                        coalesce_arg_1,
                        coalesce_arg_2,
                        preceding_not,
                    )

                    return LintResult(
                        anchor=condition_expression,
                        fixes=fixes,
                        description="Unnecessary CASE statement. "
                        "Use COALESCE function instead.",
                    )

            # Method 2: Check if the condition expression is comparing a column
            # reference to NULL and whether that column reference is also in either the
            # THEN/ELSE expression. We can only apply this method when there is only
            # one condition in the condition expression.
            condition_expression_segments_raw = {
                segment.raw_upper for segment in condition_expression.segments
            }
            if {"IS", "NULL"}.issubset(condition_expression_segments_raw) and (
                not condition_expression_segments_raw.intersection({"AND", "OR"})
            ):
                # Check if the comparison is to NULL or NOT NULL.
                is_not_prefix = "NOT" in condition_expression_segments_raw

                # Locate column reference in condition expression.
                column_reference_segment = (
                    Segments(condition_expression)
                    .children(sp.is_type("column_reference"))
                    .get()
                )

                # Return None if none found (this condition does not apply to functions)
                if not column_reference_segment:
                    return None

                if else_clauses:
                    else_expression = else_clauses.children(sp.is_type("expression"))[0]
                    # Check if we can reduce the CASE expression to a single coalesce
                    # function.
                    if (
                        not is_not_prefix
                        and column_reference_segment.raw_upper
                        == else_expression.raw_upper
                    ):
                        coalesce_arg_1 = else_expression
                        coalesce_arg_2 = then_expression
                    elif (
                        is_not_prefix
                        and column_reference_segment.raw_upper
                        == then_expression.raw_upper
                    ):
                        coalesce_arg_1 = then_expression
                        coalesce_arg_2 = else_expression
                    else:
                        return None

                    if coalesce_arg_2.raw_upper == "NULL":
                        # Can just specify the column on it's own
                        # rather than using a COALESCE function.
                        return LintResult(
                            anchor=condition_expression,
                            fixes=self._column_only_fix_list(
                                context,
                                column_reference_segment,
                            ),
                            description="Unnecessary CASE statement. "
                            f"Just use column '{column_reference_segment.raw}'.",
                        )

                    return LintResult(
                        anchor=condition_expression,
                        fixes=self._coalesce_fix_list(
                            context,
                            coalesce_arg_1,
                            coalesce_arg_2,
                        ),
                        description="Unnecessary CASE statement. "
                        "Use COALESCE function instead.",
                    )
                elif column_reference_segment.raw_upper == then_expression.raw_upper:
                    # Can just specify the column on it's own
                    # rather than using a COALESCE function.
                    # In this case no ELSE statement is equivalent to ELSE NULL.
                    return LintResult(
                        anchor=condition_expression,
                        fixes=self._column_only_fix_list(
                            context,
                            column_reference_segment,
                        ),
                        description="Unnecessary CASE statement. "
                        f"Just use column '{column_reference_segment.raw}'.",
                    )

        return None
