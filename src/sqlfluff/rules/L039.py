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
        results = sequence.respace(filter="inline").get_results()

        # For now, respace rules are separate for creation and reduction.
        # That shouldn't be true in future.

        # But, until then - "not enough whitespace" is handled in other
        # rules and this one should just handle "too much" (or "wrong amount").

        # That means we take the returned results, and only keep the ones
        # that modify or remove whitespace.
        return [
            result
            for result in results
            if any(fix.edit_type in ("replace", "delete") for fix in result.fixes)
        ]
