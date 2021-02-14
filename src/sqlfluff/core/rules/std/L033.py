"""Implementation of Rule L033."""

from sqlfluff.core.rules.base import BaseCrawler, LintResult


class Rule_L033(BaseCrawler):
    """UNION ALL is preferred over UNION.

    | **Anti-pattern**
    | In this example, UNION ALL should be preferred over UNION

    .. code-block:: sql

        SELECT a, b FROM table_1 UNION SELECT a, b FROM table_2

    | **Best practice**
    | Replace UNION with UNION ALL

    .. code-block:: sql

        SELECT a, b FROM table_1 UNION ALL SELECT a, b FROM table_2

    """

    def _eval(self, segment, raw_stack, **kwargs):
        """Look for UNION keyword not immediately followed by ALL keyword. Note that UNION DISTINCT is valid, rule only applies to bare UNION.

        The function does this by looking for a segment of type set_operator
        which has a UNION but no DISTINCT or ALL.
        """
        if segment.type == "set_operator":
            if "UNION" in segment.raw.upper() and not (
                "ALL" in segment.raw.upper() or "DISTINCT" in segment.raw.upper()
            ):
                return LintResult(anchor=segment)
        return LintResult()
