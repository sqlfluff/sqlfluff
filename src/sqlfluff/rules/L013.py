"""Implementation of Rule L013."""
from typing import Optional

from sqlfluff.core.rules.base import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.doc_decorators import document_configuration
import sqlfluff.core.rules.functional.segment_predicates as sp
from sqlfluff.core.rules.functional.segments import Segments


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
        # If we have an alias its all good
        if children.any(sp.is_type("alias_expression")):
            return None

        # If this is not a select_clause then this rule doesn't apply
        if not segment.all(sp.is_type("select_clause_element")):
            return None

        # Ignore if it's a function with EMITS clause as EMITS is equivalent to AS
        if (
            children.select(sp.is_type("function"))
            .children()
            .select(sp.is_type("emits_segment"))
        ):
            return None

        select_clause_children = children.select(sp.not_(sp.is_name("star")))
        is_complex_clause = _recursively_check_is_complex(select_clause_children)
        if not is_complex_clause:
            return None
        # No fixes, because we don't know what the alias should be,
        # the user should document it themselves.
        if self.allow_scalar:  # type: ignore
            # Check *how many* elements/columns there are in the select
            # statement. If this is the only one, then we won't
            # report an error.
            immediate_parent = context.functional.parent_stack.last()
            elements = immediate_parent.children(sp.is_type("select_clause_element"))
            num_elements = len(elements)

            if num_elements > 1:
                return LintResult(anchor=context.segment)
            return None

        return LintResult(anchor=context.segment)


def _recursively_check_is_complex(select_clause_or_exp_children: Segments) -> bool:
    forgiveable_types = [
        "whitespace",
        "newline",
        "column_reference",
        "wildcard_expression",
        "cast_expression",
        "bracketed",
    ]
    selector = sp.not_(sp.is_type(*forgiveable_types))
    filtered = select_clause_or_exp_children.select(selector)
    remaining_count = len(filtered)

    # Once we have removed the above if nothing remains,
    # then this statement/expression was simple
    if remaining_count == 0:
        return False

    first_el = filtered.first()
    # Anything except a single expresion seg remains
    # Then it was complex
    if remaining_count > 1 or not first_el.all(sp.is_type("expression")):
        return True

    # If we have just an expression check if it was simple
    return _recursively_check_is_complex(first_el.children())
