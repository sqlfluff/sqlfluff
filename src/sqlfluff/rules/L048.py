"""Implementation of Rule L048."""

from typing import List

from sqlfluff.core.rules.base import BaseRule, LintResult
from sqlfluff.core.rules.context import RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.core.rules.doc_decorators import document_fix_compatible, document_groups
from sqlfluff.utils.reflow import ReflowSequence


@document_groups
@document_fix_compatible
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

    def _eval(self, context: RuleContext) -> List[LintResult]:
        """Quoted literals should be surrounded by a single whitespace."""
        return (
            ReflowSequence.from_around_target(
                context.segment, context.parent_stack[0], config=context.config
            )
            .respace()
            .get_results()
        )
