"""Implementation of Rule L017."""

from ..base import BaseCrawler, LintFix, LintResult
from ..doc_decorators import document_fix_compatible


@document_fix_compatible
class Rule_L017(BaseCrawler):
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

    def _eval(self, segment, **kwargs):
        """Function name not immediately followed by bracket.

        Look for Function Segment with anything other than the
        function name before brackets
        """
        # We only trigger on start_bracket (open parenthesis)
        if segment.is_type("function"):
            # Look for the function name
            for fname_idx, seg in enumerate(segment.segments):
                if seg.is_type("function_name"):
                    break

            # Look for the start bracket
            for bracket_idx, seg in enumerate(segment.segments):
                if seg.name == "start_bracket":
                    break

            if bracket_idx != fname_idx + 1:
                return LintResult(
                    anchor=segment.segments[fname_idx + 1],
                    fixes=[
                        LintFix("delete", segment.segments[idx])
                        for idx in range(fname_idx + 1, bracket_idx)
                    ],
                )
        return LintResult()
