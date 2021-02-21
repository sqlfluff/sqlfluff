"""Implementation of Rule L042."""

from sqlfluff.core.rules.base import BaseCrawler, LintResult
from sqlfluff.core.rules.doc_decorators import document_configuration


@document_configuration
class Rule_L042(BaseCrawler):
    """Join/From clauses should not contain subqueries. Use CTEs instead.

    By default this rule is configured to allow subqueries within `FROM`
    clauses but not within `JOIN` clauses. If you prefer a stricter lint
    then this is configurable.

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

    config_keywords = ["forbid_subquery_in"]

    _config_mapping = {
        "join": ["join_clause"],
        "from": ["from_clause"],
        "both": ["join_clause", "from_clause"],
    }

    def _eval(self, segment, **kwargs):
        """Join/From clauses should not contain subqueries. Use CTEs instead.

        NB: No fix for this routine because it would be very complex to
        implement reliably.
        """
        parent_types = self._config_mapping[self.forbid_subquery_in]
        for parent_type in parent_types:
            if segment.is_type(parent_type):
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
                        return LintResult(
                            anchor=seg,
                            description=f"{parent_type} clauses should not contain subqueries. Use CTEs instead",
                        )
