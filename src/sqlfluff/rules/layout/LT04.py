"""Implementation of Rule LT04."""

from typing import List

from sqlfluff.core.rules import LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.rules.layout.LT03 import Rule_LT03
from sqlfluff.utils.reflow import ReflowSequence


class Rule_LT04(Rule_LT03):
    """Leading/Trailing comma enforcement.

    The configuration for whether operators should be ``trailing`` or
    ``leading`` is part of :ref:`layoutconfig`. The default configuration is:

    .. code-block:: cfg

        [sqlfluff:layout:type:comma]
        line_position = trailing

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

        For the fixing routines we delegate to the reflow utils. However
        for performance reasons we have some initial shortcuts to quickly
        identify situations which are _ok_ to avoid the overhead of the
        full reflow path.
        """
        comma_positioning = context.config.get(
            "line_position", ["layout", "type", "comma"]
        )
        # NOTE: These shortcuts assume that any newlines will be direct
        # siblings of the comma in question. This isn't _always_ the case
        # but is true often enough to have meaningful upside from early
        # detection.
        if self._check_trail_lead_shortcut(
            context.segment, context.parent_stack[-1], comma_positioning
        ):
            return [LintResult()]

        return (
            ReflowSequence.from_around_target(
                context.segment,
                root_segment=context.parent_stack[0],
                config=context.config,
            )
            .rebreak()
            .get_results()
        )
