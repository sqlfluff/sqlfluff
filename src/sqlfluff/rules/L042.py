"""Implementation of Rule L042."""

from sqlfluff.core.rules.base import BaseRule, LintResult
from sqlfluff.core.rules.doc_decorators import document_configuration


@document_configuration
class Rule_L042(BaseRule):
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
        "from": ["from_expression"],
        "both": ["join_clause", "from_expression"],
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
                from_expression_element = segment.get_child("from_expression_element")
                if not from_expression_element:  # pragma: no cover
                    return None  # There isn't one. We're done.
                # Get the main bit
                from_expression_element = from_expression_element.get_child(
                    "table_expression"
                )
                if not from_expression_element:  # pragma: no cover
                    return None  # There isn't one. We're done.
                # Is it bracketed?
                bracketed_expression = from_expression_element.get_child("bracketed")
                # If it is, lint that instead
                if bracketed_expression:
                    from_expression_element = bracketed_expression
                # If any of the following are found, raise an issue.
                # If not, we're fine.
                problem_children = [
                    "with_compound_statement",
                    "set_expression",
                    "select_statement",
                ]
                for seg_type in problem_children:
                    seg = from_expression_element.get_child(seg_type)
                    if seg:
                        return LintResult(
                            anchor=seg,
                            description=f"{parent_type} clauses should not contain subqueries. Use CTEs instead",
                        )
