"""Implementation of Rule L005."""
from typing import Optional

from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.core.rules.doc_decorators import document_fix_compatible, document_groups
from sqlfluff.utils.reflow.sequence import ReflowSequence


@document_groups
@document_fix_compatible
class Rule_L005(BaseRule):
    """Commas should not have whitespace directly before them.

    Unless it's an indent. Trailing/leading commas are dealt with
    in a different rule.

    **Anti-pattern**

    The ``•`` character represents a space.
    There is an extra space in line two before the comma.

    .. code-block:: sql
       :force:

        SELECT
            a•,
            b
        FROM foo

    **Best practice**

    Remove the space before the comma.

    .. code-block:: sql

        SELECT
            a,
            b
        FROM foo
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
                sides="before",
            )
            .respace()
            .get_fixes()
        )
        deletes = [fix for fix in fixes if fix.edit_type == "delete"]
        if deletes:
            # There should just be one, so just take the first.
            return LintResult(anchor=deletes[0].anchor, fixes=deletes[:1])
        return None
