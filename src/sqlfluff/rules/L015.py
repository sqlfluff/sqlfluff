"""Implementation of Rule L015."""
from typing import Optional

from sqlfluff.core.parser import WhitespaceSegment

from sqlfluff.core.rules.base import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.doc_decorators import document_fix_compatible
import sqlfluff.core.rules.functional.segment_predicates as sp


@document_fix_compatible
class Rule_L015(BaseRule):
    """``DISTINCT`` used with parentheses.

    **Anti-pattern**

    In this example, parentheses are not needed and confuse
    ``DISTINCT`` with a function. The parentheses can also be misleading
    about which columns are affected by the ``DISTINCT`` (all the columns!).

    .. code-block:: sql

        SELECT DISTINCT(a), b FROM foo

    **Best practice**

    Remove parentheses to be clear that the ``DISTINCT`` applies to
    both columns.

    .. code-block:: sql

        SELECT DISTINCT a, b FROM foo

    """

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Looking for DISTINCT before a bracket.

        Look for DISTINCT keyword immediately followed by open parenthesis.
        """
        # We trigger on `select_clause` and look for `select_clause_modifier`
        if context.segment.is_type("select_clause"):
            children = context.functional.segment.children()
            modifier = children.select(sp.is_type("select_clause_modifier"))
            first_element = children.select(sp.is_type("select_clause_element")).first()
            if not modifier or not first_element:
                return None
            # is the first element only an expression with only brackets?
            expression = (
                first_element.children(sp.is_type("expression")).first()
                or first_element
            )
            bracketed = expression.children(sp.is_type("bracketed")).first()
            if bracketed:
                fixes = []
                # If there's nothing else in the expression, remove the brackets.
                if len(expression[0].segments) == 1:
                    # Remove the brackets and strip any meta segments.
                    fixes.append(
                        LintFix.replace(
                            bracketed[0], self.filter_meta(bracketed[0].segments)[1:-1]
                        ),
                    )
                # If no whitespace between DISTINCT and expression, add it.
                if not children.select(
                    sp.is_whitespace(), start_seg=modifier[0], stop_seg=first_element[0]
                ):
                    fixes.append(
                        LintFix.create_before(
                            first_element[0],
                            [WhitespaceSegment()],
                        )
                    )
                # If no fixes, no problem.
                if fixes:
                    return LintResult(anchor=modifier[0], fixes=fixes)
        return None
