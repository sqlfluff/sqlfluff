"""Implementation of Rule LT06."""

from sqlfluff.core.rules import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.utils.functional import FunctionalContext, sp


class Rule_LT06(BaseRule):
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

    name = "layout.functions"
    aliases = ("L017",)
    groups = ("all", "core", "layout")
    crawl_behaviour = SegmentSeekerCrawler({"function"})
    is_fix_compatible = True

    def _eval(self, context: RuleContext) -> LintResult:
        """Function name not immediately followed by bracket.

        Look for Function Segment with anything other than the
        function name before brackets

        NOTE: This hasn't been combined with LT01 because it has
        some special treatment for comments. That might be something
        we revisit at a later point if duplicate errors become
        problematic.
        """
        segment = FunctionalContext(context).segment
        # We only trigger on start_bracket (open parenthesis)
        assert segment.all(sp.is_type("function"))
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
