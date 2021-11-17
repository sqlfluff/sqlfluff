"""Implementation of Rule L054."""
from typing import Optional

from sqlfluff.core.rules.base import BaseRule, LintResult, RuleContext


class Rule_L054(BaseRule):
    """Inconsistent column references in GROUP BY/ORDER BY clauses.

    | **Anti-pattern**
    | A mix of implicit and explicit column references are used in a GROUP BY clause.

    .. code-block:: sql
       :force:

        SELECT
            foo,
            bar,
            sum(baz) AS sum_value
        FROM fake_table
        GROUP BY
            foo, 2;

        -- The same also applies to column
        -- references in ORDER BY clauses.

        SELECT
            foo,
            bar
        FROM fake_table
        ORDER BY
            1, bar;

    | **Best practice**
    | Reference all GROUP BY/ORDER BY columns either by name or by position.

    .. code-block:: sql
       :force:

        -- GROUP BY: Explicit
        SELECT
            foo,
            bar,
            sum(baz) AS sum_value
        FROM fake_table
        GROUP BY
            foo, bar;

        -- ORDER BY: Explicit
        SELECT
            foo,
            bar
        FROM fake_table
        ORDER BY
            foo, bar;

        -- GROUP BY: Implicit
        SELECT
            foo,
            bar,
            sum(baz) AS sum_value
        FROM fake_table
        GROUP BY
            1, 2;

        -- ORDER BY: Implicit
        SELECT
            foo,
            bar
        FROM fake_table
        ORDER BY
            1, 2;
    """

    config_keywords = ["group_by_and_order_by_style"]

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Inconsistent column references in GROUP BY/ORDER BY clauses."""
        # Config type hints
        self.group_by_and_order_by_style: str

        # We only care about GROUP BY/ORDER BY clauses.
        if context.segment.name not in {"GroupByClauseSegment", "OrderByClauseSegment"}:
            return None

        # Look at child segments to detect the presence of disallowed segments.
        child_segment_names = [segment.name for segment in context.segment.segments]
        disallowed_segment_names = {
            "explicit": "numeric_literal",
            "implicit": "ColumnReferenceSegment",
        }

        if self.group_by_and_order_by_style == "consistent":
            # If consistent naming then raise lint error if both
            # numeric literal and column reference segments are present.
            if all(name in child_segment_names for name in disallowed_segment_names.values()):
                return LintResult(anchor=context.segment)
        else:
            # If explicit or implicit naming then raise lint error
            # if the opposite reference type is detected.
            if any(
                name
                == disallowed_segment_names[self.group_by_and_order_by_style]
                for name in child_segment_names
            ):
                # If a disallowed segment is detected raise a linting error.
                return LintResult(anchor=context.segment)

        return None
