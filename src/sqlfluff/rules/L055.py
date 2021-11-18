"""Implementation of Rule L055."""
from typing import Optional

from sqlfluff.core.rules.base import BaseRule, LintResult, RuleContext


class Rule_L055(BaseRule):
    """Use LEFT JOIN instead of RIGHT JOIN.

    | **Anti-pattern**
    | RIGHT JOIN is used.

    .. code-block:: sql
       :force:

        SELECT
            foo.col1,
            bar.col2
        FROM foo
        RIGHT JOIN bar
            ON foo.bar_id = bar.id;

    | **Best practice**
    | Refactor and use LEFT JOIN instead.

    .. code-block:: sql
       :force:

        SELECT
            foo.col1,
            bar.col2
        FROM bar
        LEFT JOIN foo
            ON foo.bar_id = bar.id;
    """

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Use LEFT JOIN instead of RIGHT JOIN."""
        # We are only interested in JOIN clauses.
        if context.segment.type != "join_clause":
            return None

        # We identify non-lone JOIN by looking at first child segment.
        if {"right", "join"}.issubset(
            {segment.name for segment in context.segment.segments}
        ):
            return LintResult(context.segment.segments[0])

        return None
