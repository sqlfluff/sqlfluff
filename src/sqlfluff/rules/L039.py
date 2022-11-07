"""Implementation of Rule L039."""
from typing import List, Optional

from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import RootOnlyCrawler
from sqlfluff.core.rules.doc_decorators import document_fix_compatible, document_groups
from sqlfluff.utils.reflow.sequence import ReflowSequence


@document_groups
@document_fix_compatible
class Rule_L039(BaseRule):
    """Unnecessary whitespace found.

    **Anti-pattern**

    .. code-block:: sql

        SELECT
            a,        b
        FROM foo

    **Best practice**

    Unless an indent or preceding a comment, whitespace should
    be a single space.

    .. code-block:: sql

        SELECT
            a, b
        FROM foo
    """

    groups = ("all", "core")
    crawl_behaviour = RootOnlyCrawler()

    def _eval(self, context: RuleContext) -> Optional[List[LintResult]]:
        """Unnecessary whitespace."""
        sequence = ReflowSequence.from_root(context.segment, config=context.config)
        fixes = sequence.respace(filter="inline").get_fixes()
        results = [
            LintResult(anchor=fix.anchor, fixes=[fix])
            for fix in fixes
            # Only handle replace and delete fixes here. They're the ones
            # we'll see if there's _too much_ whitespace. Linting issues
            # for _not enough_ whitespace are picked up elsewhere.
            if fix.edit_type in ("replace", "delete")
        ]
        return results
