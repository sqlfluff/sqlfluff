"""Implementation of Rule L013."""
from typing import Optional

from sqlfluff.core.rules.base import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.doc_decorators import document_configuration
import sqlfluff.core.rules.functional.segment_predicates as sp


@document_configuration
class Rule_L013(BaseRule):
    """Column expression without alias. Use explicit `AS` clause.

    **Anti-pattern**

    In this example, there is no alias for both sums.

    .. code-block:: sql

        SELECT
            sum(a),
            sum(b)
        FROM foo

    **Best practice**

    Add aliases.

    .. code-block:: sql

        SELECT
            sum(a) AS a_sum,
            sum(b) AS b_sum
        FROM foo

    """

    config_keywords = ["allow_scalar"]

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Column expression without alias. Use explicit `AS` clause.

        We look for the select_clause_element segment, and then evaluate
        whether it has an alias segment or not and whether the expression
        is complicated enough. `parent_stack` is to assess how many other
        elements there are.

        """
        segment = context.functional.segment
        children = segment.children()
        if segment.all(sp.is_type("select_clause_element")) and not children.any(
            sp.is_type("alias_expression")
        ):
            # Ignore if it's a function with EMITS clause as EMITS is equivalent to AS
            if (
                children.select(sp.is_type("function"))
                .children()
                .select(sp.is_type("emits_segment"))
            ):
                return None

            types = set(
                children.select(sp.not_(sp.is_name("star"))).apply(sp.get_type())
            )
            unallowed_types = types - {
                "whitespace",
                "newline",
                "column_reference",
                "wildcard_expression",
            }
            if unallowed_types:
                # No fixes, because we don't know what the alias should be,
                # the user should document it themselves.
                if self.allow_scalar:  # type: ignore
                    # Check *how many* elements there are in the select
                    # statement. If this is the only one, then we won't
                    # report an error.
                    immediate_parent = context.functional.parent_stack.last()
                    num_elements = len(
                        immediate_parent.children(sp.is_type("select_clause_element"))
                    )
                    if num_elements > 1:
                        return LintResult(anchor=context.segment)
                    else:
                        return None
                else:
                    # Just error if we don't care.
                    return LintResult(anchor=context.segment)
        return None
