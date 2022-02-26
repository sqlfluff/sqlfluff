"""Implementation of Rule L051."""
from typing import Optional
from sqlfluff.core.parser.segments.raw import KeywordSegment, WhitespaceSegment

from sqlfluff.core.rules.base import BaseRule, LintResult, LintFix, RuleContext
from sqlfluff.core.rules.doc_decorators import (
    document_fix_compatible,
    document_configuration,
)


@document_fix_compatible
@document_configuration
class Rule_L051(BaseRule):
    """Join clauses should be fully qualified.

    By default this rule is configured to enforce fully qualified ``INNER JOIN``
    clauses, but not ``[LEFT/RIGHT/FULL] OUTER JOIN``. If you prefer a stricter
    lint then this is configurable.

    **Anti-pattern**

    A join is specified without expliciting the **kind** of join.

    .. code-block:: sql
       :force:

        SELECT
            foo
        FROM bar
        JOIN baz;

    **Best practice**

    Use ``INNER JOIN`` rather than ``JOIN``.

    .. code-block:: sql
       :force:

        SELECT
            foo
        FROM bar
        INNER JOIN baz;
    """

    config_keywords = ["fully_qualify_join_types"]

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Fully qualify JOINs."""
        # Config type hints
        self.fully_qualify_join_types: str

        # We are only interested in JOIN clauses.
        if not context.segment.is_type("join_clause"):
            return None

        join_clause_keywords = [
            segment
            for segment in context.segment.segments
            if segment.is_type("keyword")
        ]

        # We identify LEFT/RIGHT/OUTER JOINs and if the next keyword is JOIN.
        if self.fully_qualify_join_types in ["outer", "both"] and join_clause_keywords[
            0
        ].name in ["right", "left", "full"]:
            if join_clause_keywords[1] == "join":
                return LintResult(
                    context.segment.segments[0],
                    fixes=[
                        LintFix.create_after(
                            context.segment.segments[0],
                            [KeywordSegment("OUTER"), WhitespaceSegment()],
                        )
                    ],
                )

        # We identify non-lone JOIN by looking at first child segment.
        if (
            self.fully_qualify_join_types in ["inner", "both"]
            and join_clause_keywords[0].name == "join"
        ):
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

        return None
