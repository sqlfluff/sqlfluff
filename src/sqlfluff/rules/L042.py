"""Implementation of Rule L042."""
from typing import Optional

from sqlfluff.core.rules.base import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.doc_decorators import document_configuration
from sqlfluff.core.rules.functional.segment_predicates import is_type


@document_configuration
class Rule_L042(BaseRule):
    """Join/From clauses should not contain subqueries. Use CTEs instead.

    By default this rule is configured to allow subqueries within ``FROM``
    clauses but not within ``JOIN`` clauses. If you prefer a stricter lint
    then this is configurable.

    .. note::
       Some dialects don't allow CTEs, and for those dialects
       this rule makes no sense and should be disabled.

    **Anti-pattern**

    .. code-block:: sql

        select
            a.x, a.y, b.z
        from a
        join (
            select x, z from b
        ) using(x)


    **Best practice**

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

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Join/From clauses should not contain subqueries. Use CTEs instead.

        NB: No fix for this routine because it would be very complex to
        implement reliably.
        """
        parent_types = self._config_mapping[self.forbid_subquery_in]  # type: ignore
        for parent_type in parent_types:
            if context.segment.is_type(parent_type):
                # Get the referenced table segment
                from_expression_element = context.functional.segment.children(
                    is_type("from_expression_element")
                ).children(is_type("table_expression"))

                # Is it bracketed? If so, lint that instead.
                bracketed_expression = from_expression_element.children(
                    is_type("bracketed")
                )
                if bracketed_expression:
                    from_expression_element = bracketed_expression

                # If we find a child with a "problem" type, raise an issue.
                # If not, we're fine.
                seg = from_expression_element.children(
                    is_type(
                        "with_compound_statement",
                        "set_expression",
                        "select_statement",
                    )
                )
                if seg:
                    return LintResult(
                        anchor=seg[0],
                        description=f"{parent_type} clauses should not contain "
                        "subqueries. Use CTEs instead",
                    )
        return None
