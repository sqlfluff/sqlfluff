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
        # TODO: Move the discussion below into a Github issue, and update this comment to reference the issue.
        # N.B. Although we could provide a fix by backchecking the preceding SELECT statement in the simple case e.g.
        # SELECT
        #     fake_column_1,
        #     fake_column_2,
        #     sum(fake_value) AS sum_value
        # FROM fake_table
        # GROUP BY
        #     1, 2;
        #
        # This becomes incredibly complicated when you consider that the parser will not
        # raise a parse error for invalid SELECT/GROUP BY interactions:
        # 1. Differing number of SELECT columns and GROUP BY columns e.g.
        # SELECT
        #     fake_column_1,
        #     fake_column_2,
        #     fake_column_3,
        #     sum(fake_value) AS sum_value
        # FROM fake_table
        # GROUP BY
        #     1, 2;
        #
        # 2. Wildcards in select clause
        # SELECT
        #     *,
        #     fake_column_1,
        #     fake_column_2,
        #     fake_column_3,
        #     sum(fake_value) AS sum_value
        # FROM fake_table
        # GROUP BY
        #     1, 2;
        #
        # 3. Aggregate function out of order
        # SELECT
        #     fake_column_1,
        #     sum(fake_value) AS sum_value
        #     fake_column_2,
        # FROM fake_table
        # GROUP BY
        #     1, 2;
        #
        # 4. Mix of numeric literal and column reference in GROUP BY
        # SELECT
        #     fake_column_1,
        #     fake_column_2,
        #     fake_column_3,
        #     sum(fake_value) AS sum_value
        # FROM fake_table
        # GROUP BY
        #     1, fake_column_2, 3;
        #
        # To save implementing all this logic,
        # which belongs more in the parser rather than the rule,
        # The sensible approach is to flag the lint violation
        # to the user and let them fix it.
        return LintResult(
            anchor=numeric_literal_segment,
        )
