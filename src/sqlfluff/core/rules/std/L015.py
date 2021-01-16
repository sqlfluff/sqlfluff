"""Implementation of Rule L015."""

from sqlfluff.core.rules.base import BaseCrawler, LintResult


class Rule_L015(BaseCrawler):
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

    def _eval(self, segment, raw_stack, **kwargs):
        """Looking for DISTINCT before a bracket.

        Look for DISTINCT keyword immediately followed by open parenthesis.
        """
        # We only trigger on start_bracket (open parenthesis)
        if segment.name == "start_bracket":
            filt_raw_stack = self.filter_meta(raw_stack)
            if len(filt_raw_stack) > 0 and filt_raw_stack[-1].name == "DISTINCT":
                # If we find DISTINCT followed by open_bracket, then bad.
                return LintResult(anchor=segment)
        return LintResult()
