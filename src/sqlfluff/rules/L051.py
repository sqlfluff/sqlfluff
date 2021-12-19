"""Implementation of Rule L051."""
from typing import Optional
from sqlfluff.core.parser.segments.raw import KeywordSegment, WhitespaceSegment

from sqlfluff.core.rules.base import BaseRule, LintResult, LintFix, RuleContext
from sqlfluff.core.rules.doc_decorators import document_fix_compatible


@document_fix_compatible
class Rule_L051(BaseRule):
    """INNER JOIN must be fully qualified.

    | **Anti-pattern**
    | Lone JOIN is used.

    .. code-block:: sql
       :force:

        SELECT
            foo
        FROM bar
        JOIN baz;

    | **Best practice**
    | Use INNER JOIN rather than JOIN.

    .. code-block:: sql
       :force:

        SELECT
            foo
        FROM bar
        INNER JOIN baz;
    """

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """INNER JOIN must be fully qualified."""
        # We are only interested in JOIN clauses.
        if context.segment.type != "join_clause":
            return None

        # We identify non-lone JOIN by looking at first child segment.
        if context.segment.segments[0].name != "join":
            return None

        # Replace lone JOIN with INNER JOIN.
        return LintResult(
            context.segment.segments[0],
            fixes=[
                LintFix.create_before(
                    context.segment.segments[0],
                    [KeywordSegment("INNER"), WhitespaceSegment()],
                )
            ],
        )
