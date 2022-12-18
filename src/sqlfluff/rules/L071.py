"""Implementation of Rule L071."""

from typing import List, Optional

from sqlfluff.core.rules.base import BaseRule, LintResult
from sqlfluff.core.rules.context import RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.core.rules.doc_decorators import document_fix_compatible, document_groups

from sqlfluff.utils.reflow.sequence import ReflowSequence


@document_groups
@document_fix_compatible
class Rule_L071(BaseRule):
    """Parenthesis blocks should be surrounded by whitespaces.

    **Anti-pattern**

    In this example, there is a space missing between the parenthesis block
    ``( ... )`` and the keyword ``FROM`` and the keyword ``AS``.

    .. code-block:: sql

        SELECT * FROM(SELECT 1 AS C1)AS T1;

    **Best practice**

    Keep a single space.

    .. code-block:: sql

        SELECT * FROM (SELECT 1 AS C1) AS T1;

    """

    groups = ("all", "core")
    crawl_behaviour = SegmentSeekerCrawler(
        {"start_bracket", "end_bracket"}, provide_raw_stack=True
    )

    def _eval(self, context: RuleContext) -> Optional[List[LintResult]]:
        """Parenthesis blocks should be surrounded by whitespaces."""
        if (
            context.segment.is_type("start_bracket")
            and len(context.raw_stack) > 2
            and context.raw_stack[-2].is_type("keyword")
        ):
            # and prior section not from or where
            # reserved_keywords
            return (
                ReflowSequence.from_around_target(
                    context.segment,
                    context.parent_stack[0],
                    config=context.config,
                    sides="before",
                )
                .respace()
                .get_results()
            )
        if context.segment.is_type("end_bracket"):
            return (
                ReflowSequence.from_around_target(
                    context.segment,
                    context.parent_stack[0],
                    config=context.config,
                    sides="after",
                )
                .respace()
                .get_results()
            )

        return None
