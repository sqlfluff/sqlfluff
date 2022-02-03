"""Implementation of Rule L017."""

from sqlfluff.core.rules.base import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.doc_decorators import document_fix_compatible
import sqlfluff.core.rules.functional.segment_predicates as sp


@document_fix_compatible
class Rule_L017(BaseRule):
    """Function name not immediately followed by parenthesis.

    **Anti-pattern**

    In this example, there is a space between the function and the parenthesis.

    .. code-block:: sql

        SELECT
            sum (a)
        FROM foo

    **Best practice**

    Remove the space between the function and the parenthesis.

    .. code-block:: sql

        SELECT
            sum(a)
        FROM foo

    """

    def _eval(self, context: RuleContext) -> LintResult:
        """Function name not immediately followed by bracket.

        Look for Function Segment with anything other than the
        function name before brackets
        """
        segment = context.functional.segment
        # We only trigger on start_bracket (open parenthesis)
        if segment.all(sp.is_type("function")):
            children = segment.children()

            function_name = children.first(sp.is_type("function_name"))[0]
            start_bracket = children.first(sp.is_type("bracketed"))[0]

            intermediate_segments = children.select(
                start_seg=function_name, stop_seg=start_bracket
            )
            if intermediate_segments:
                # It's only safe to fix if there is only whitespace
                # or newlines in the intervening section.
                if intermediate_segments.all(sp.is_type("whitespace", "newline")):
                    return LintResult(
                        anchor=intermediate_segments[0],
                        fixes=[LintFix.delete(seg) for seg in intermediate_segments],
                    )
                else:
                    # It's not all whitespace, just report the error.
                    return LintResult(
                        anchor=intermediate_segments[0],
                    )

        return LintResult()
