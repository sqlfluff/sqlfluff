"""Implementation of Rule L008."""
from typing import Optional

from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.core.rules.doc_decorators import document_fix_compatible, document_groups

from sqlfluff.utils.reflow.sequence import ReflowSequence


@document_groups
@document_fix_compatible
class Rule_L008(BaseRule):
    """Commas should be followed by a single whitespace unless followed by a comment.

    **Anti-pattern**

    In this example, there is no space between the comma and ``'zoo'``.

    .. code-block:: sql

        SELECT
            *
        FROM foo
        WHERE a IN ('plop','zoo')

    **Best practice**

    Keep a single space after the comma. The ``•`` character represents a space.

    .. code-block:: sql
       :force:

        SELECT
            *
        FROM foo
        WHERE a IN ('plop',•'zoo')
    """

    groups = ("all", "core")
    crawl_behaviour = SegmentSeekerCrawler({"comma"})

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Commas should not have whitespace directly before them."""
        fixes = (
            ReflowSequence.from_around_target(
                context.segment,
                context.parent_stack[0],
                config=context.config,
                sides="after",
            )
            .respace()
            .get_fixes()
        )
        if fixes:
            # There should just be one, so just take the first.
            return LintResult(anchor=fixes[0].anchor, fixes=fixes[:1])
        return None
