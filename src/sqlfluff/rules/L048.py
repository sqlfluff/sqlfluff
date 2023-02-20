"""Implementation of Rule L048."""

from typing import List

from sqlfluff.core.rules.base import BaseRule, LintResult
from sqlfluff.core.rules.context import RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.utils.reflow import ReflowSequence


class Rule_L048(BaseRule):
    """Quoted literals should be surrounded by a single whitespace.

    **Anti-pattern**

    In this example, there is a space missing between the string
    ``'foo'`` and the keyword ``AS``.

    .. code-block:: sql

        SELECT
            'foo'AS bar
        FROM foo


    **Best practice**

    Keep a single space.

    .. code-block:: sql

        SELECT
            'foo' AS bar
        FROM foo
    """

    groups = ("all", "core")
    crawl_behaviour = SegmentSeekerCrawler(
        {"quoted_literal", "date_constructor_literal"}
    )
    is_fix_compatible = True

    def _eval(self, context: RuleContext) -> List[LintResult]:
        """Quoted literals should be surrounded by a single whitespace."""
        return (
            ReflowSequence.from_around_target(
                context.segment, context.parent_stack[0], config=context.config
            )
            .respace()
            .get_results()
        )
