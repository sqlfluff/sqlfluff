"""Implementation of Rule L054."""
from typing import Optional

from sqlfluff.core.rules.base import BaseRule, LintFix, LintResult, RuleContext


class Rule_L054(BaseRule):
    """GROUP BY clause must not contain implicit positional references.

    | **Anti-pattern**
    | Implicit references to column position are used in the GROUP BY clause.

    .. code-block:: sql
       :force:

        SELECT
            fake_column_1,
            fake_column_2,
            sum(fake_value) AS sum_value
        FROM fake_table
        GROUP BY
            1, 2;

    | **Best practice**
    | Reference GROUP BY columns by name.

    .. code-block:: sql
       :force:

        SELECT
            fake_column_1,
            fake_column_2,
            sum(fake_value) AS sum_value
        FROM fake_table
        GROUP BY
            fake_column_1, fake_column_2;
    """

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """GROUP BY clause must not contain implicit positional references."""
        # We only care about GROUP BY clauses.
        if context.segment.name != "GroupByClauseSegment":
            return None

        # Look at child code segments of GROUP BY clauses
        # to detect the presence of numeric literals.
        numeric_literal_segments = [
            segment
            for segment in context.segment.segments
            if segment.name == "numeric_literal"
        ]

        # No numeric literals detected.
        if not numeric_literal_segments:
            return None

        # Locate preceding SELECT clause and its elements.
        prior_select_clause_segment = next(
            segment
            for segment in context.siblings_pre[::-1]
            if segment.name == "SelectClauseSegment"
        )
        select_clause_element_segments = [
            segment
            for segment in prior_select_clause_segment.segments
            if segment.name == "SelectClauseElementSegment"
        ]

        fixes = []
        for segment in numeric_literal_segments:
            try:
                # Iterate over numeric literal segments to try and locate
                # the corresponding column in the SELECT clause elements.
                select_clause_element_segment = select_clause_element_segments[
                    int(segment.raw) - 1
                ]
            except IndexError:
                # Index is not in the SELECT clause elements.
                continue

            if select_clause_element_segment.segments[0].name == "FunctionSegment":
                # Functions (SUM, MIN, MAX, etc.) can't be used as GROUP BY columns.
                continue
            
            # Replace the numeric literal with the corresponding column reference segment.
            column_reference_segment = next(
                segment
                for segment in select_clause_element_segment.segments
                if segment.name == "ColumnReferenceSegment"
            )
            fixes.append(LintFix("edit", segment, [column_reference_segment]))

        return LintResult(anchor=context.segment, fixes=fixes)
