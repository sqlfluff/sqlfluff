"""Implementation of Rule LT04."""

from typing import List

from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.utils.reflow import ReflowSequence


class Rule_LT04(BaseRule):
    """Leading/Trailing comma enforcement.

    **Anti-pattern**

    There is a mixture of leading and trailing commas.

    .. code-block:: sql

        SELECT
            a
            , b,
            c
        FROM foo

    **Best practice**

    By default, `SQLFluff` prefers trailing commas. However it
    is configurable for leading commas. The chosen style must be used
    consistently throughout your SQL.

    .. code-block:: sql

        SELECT
            a,
            b,
            c
        FROM foo

        -- Alternatively, set the configuration file to 'leading'
        -- and then the following would be acceptable:

        SELECT
            a
            , b
            , c
        FROM foo
    """

    name = "layout.commas"
    aliases = ("L019",)
    groups = ("all", "layout")
    crawl_behaviour = SegmentSeekerCrawler({"comma"})
    _adjust_anchors = True
    is_fix_compatible = True

    def _eval(self, context: RuleContext) -> List[LintResult]:
        """Enforce comma placement.

        For leading commas we're looking for trailing commas, so
        we look for newline segments. For trailing commas we're
        looking for leading commas, so we look for the comma itself.

        We also want to handle proper whitespace removal/addition. We remove
        any trailing whitespace after the leading comma, when converting a
        leading comma to a trailing comma. We add whitespace after the leading
        comma when converting a trailing comma to a leading comma.
        """
        return (
            ReflowSequence.from_around_target(
                context.segment,
                root_segment=context.parent_stack[0],
                config=context.config,
            )
            .rebreak()
            .get_results()
        )
