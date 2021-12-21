"""Implementation of Rule L015."""
from typing import Optional

from sqlfluff.core.parser import WhitespaceSegment

from sqlfluff.core.rules.base import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.doc_decorators import document_fix_compatible


@document_fix_compatible
class Rule_L015(BaseRule):
    """DISTINCT used with parentheses.

    | **Anti-pattern**
    | In this example, parenthesis are not needed and confuse
    | DISTINCT with a function. The parenthesis can also be misleading
    | in which columns they apply to.

    .. code-block:: sql

        SELECT DISTINCT(a), b FROM foo

    | **Best practice**
    | Remove parenthesis to be clear that the DISTINCT applies to
    | both columns.

    .. code-block:: sql

        SELECT DISTINCT a, b FROM foo

    """

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Looking for DISTINCT before a bracket.

        Look for DISTINCT keyword immediately followed by open parenthesis.
        """
        # We trigger on `select_clause` and look for `select_clause_modifier`
        if context.segment.is_type("select_clause"):
            modifier = context.segment.get_child("select_clause_modifier")
            if not modifier:
                return None
            first_element = context.segment.get_child("select_clause_element")
            if not first_element:
                return None  # pragma: no cover
            # is the first element only an expression with only brackets?
            expression = first_element.get_child("expression")
            if not expression:
                expression = first_element
            bracketed = expression.get_child("bracketed")
            if not bracketed:
                return None
            fixes = []
            # If there's nothing else in the expression, remove the brackets.
            if len(expression.segments) == 1:
                # Remove the brackets, and strip any meta segments.
                fixes = [
                    LintFix.replace(
                        bracketed, self.filter_meta(bracketed.segments)[1:-1]
                    ),
                ]
            # Is there any whitespace between DISTINCT and the expression?
            distinct_idx = context.segment.segments.index(modifier)
            elem_idx = context.segment.segments.index(first_element)
            if not any(
                seg.is_whitespace
                for seg in context.segment.segments[distinct_idx:elem_idx]
            ):
                fixes.append(
                    LintFix.create_before(
                        first_element,
                        [WhitespaceSegment()],
                    )
                )
            # If no fixes, no problem.
            if fixes:
                return LintResult(anchor=modifier, fixes=fixes)
        return None
