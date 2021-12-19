"""Implementation of Rule L017."""

from sqlfluff.core.rules.base import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.doc_decorators import document_fix_compatible


@document_fix_compatible
class Rule_L017(BaseRule):
    """Function name not immediately followed by bracket.

    | **Anti-pattern**
    | In this example, there is a space between the function and the parenthesis.

    .. code-block:: sql

        SELECT
            sum (a)
        FROM foo

    | **Best practice**
    | Remove the space between the function and the parenthesis.

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
        # We only trigger on start_bracket (open parenthesis)
        if context.segment.is_type("function"):
            # Look for the function name
            for fname_idx, seg in enumerate(context.segment.segments):
                if seg.is_type("function_name"):
                    break

            # Look for the start bracket
            for bracket_idx, seg in enumerate(context.segment.segments):
                if seg.is_type("bracketed"):
                    break

            if bracket_idx != fname_idx + 1:
                # It's only safe to fix if there is only whitespace
                # or newlines in the intervening section.
                intermediate_segments = context.segment.segments[
                    fname_idx + 1 : bracket_idx
                ]
                if all(
                    seg.is_type("whitespace", "newline")
                    for seg in intermediate_segments
                ):
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
