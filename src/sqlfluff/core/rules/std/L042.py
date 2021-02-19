"""Implementation of Rule L042."""

from sqlfluff.core.rules.base import BaseCrawler, LintResult


class Rule_L042(BaseCrawler):
    """Join clauses should not contain subqueries. Use CTEs instead.

    NB: Some dialects don't allow CTEs, and for those dialects
    this rule makes no sense and should be disabled.

    | **Anti-pattern**

    .. code-block:: sql

        select
            a.x, a.y, b.z
        from a
        join (
            select x, z from b
        ) using(x)


    | **Best practice**

    .. code-block:: sql

        with c as (
            select x, z from b
        )
        select
            a.x, a.y, c.z
        from a
        join c using(x)

    """

    def _eval(self, segment, **kwargs):
        """Join clauses should not contain subqueries. Use CTEs instead.

        NB: No fix for this routine because it would be very complex to
        implement reliably.
        """
        if segment.is_type("join_clause"):
            # Get the referenced table segment
            table_expression = segment.get_child("table_expression")
            if not table_expression:
                return None  # There isn't one. We're done.
            # Get the main bit
            table_expression = table_expression.get_child("main_table_expression")
            if not table_expression:
                return None  # There isn't one. We're done.

            # If any of the following are found, raise an issue.
            # If not, we're fine.
            problem_children = [
                "with_compound_statement",
                "set_expression",
                "select_statement",
            ]
            for seg_type in problem_children:
                seg = table_expression.get_child(seg_type)
                if seg:
                    return LintResult(anchor=seg)
