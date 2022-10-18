"""Implementation of Rule L001."""
from typing import List
from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import RootOnlyCrawler
from sqlfluff.core.rules.doc_decorators import (
    document_fix_compatible,
    document_groups,
)
from sqlfluff.utils.reflow import ReflowSequence


@document_groups
@document_fix_compatible
class Rule_L001(BaseRule):
    """Unnecessary trailing whitespace.

    **Anti-pattern**

    The ``•`` character represents a space.

    .. code-block:: sql
       :force:

        SELECT
            a
        FROM foo••

    **Best practice**

    Remove trailing spaces.

    .. code-block:: sql

        SELECT
            a
        FROM foo
    """

    groups = ("all", "core")
    crawl_behaviour = RootOnlyCrawler()

    def _eval(self, context: RuleContext) -> List[LintResult]:
        """Unnecessary trailing whitespace.

        Look for newline segments, and then evaluate what
        it was preceded by.
        """
        sequence = ReflowSequence.from_root(context.segment, config=context.config)
        fixes = sequence.respace(filter="newline").get_fixes()
        results = [LintResult(anchor=fix.anchor, fixes=[fix]) for fix in fixes]
        return results
