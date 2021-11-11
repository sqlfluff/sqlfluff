"""Implementation of Rule L053."""
from typing import Optional

from sqlfluff.core.rules.base import BaseRule, LintResult, RuleContext


class Rule_L053(BaseRule):
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

        # Look at child code segments of GROUP BY clauses to detect the presence of a numeric literal.
        numeric_literal_segment = next(
            (
                segment
                for segment in context.segment.segments
                if segment.name == "numeric_literal"
            ),
            None,
        )

        # No numeric literal detected.
        if not numeric_literal_segment:
            return None

        # We have located a numeric literal column reference in the GROUP BY clause.
        # N.B. We can't fix this as we don't know underlying structure of the table
        # being referenced in the clause.
        return LintResult(
            anchor=numeric_literal_segment,
        )
