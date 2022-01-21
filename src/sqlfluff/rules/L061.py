"""Implementation of Rule L061."""

from typing import Optional

from sqlfluff.core.parser.segments.raw import CodeSegment
from sqlfluff.core.rules.base import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.doc_decorators import document_fix_compatible


@document_fix_compatible
class Rule_L061(BaseRule):
    """Use ``!=`` instead of ``<>`` for ``not equal to`` comparison.

    | **Anti-pattern**
    | ``<>`` means ``not equal`` but doesn't sound like this when
    | we say it loud.

    .. code-block:: sql

        SELECT * FROM X WHERE 1 <> 2;

    | **Best practice**
    | Use ``!=`` instead because it's sounds more natural and
    | is more common in other programming languages.

    .. code-block:: sql

        SELECT * FROM X WHERE 1 != 2;

    """

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Use ``!=`` instead of ``<>`` for ``not equal to`` comparison."""

        # Only care about not_equal_to segments.
        if context.segment.name != "not_equal_to":
            return None

        # Only care about ``<>``
        if not "<>" in context.segment.raw:
            return None

        # Provide a fix and replace ``<>`` with ``!=``
        fix = LintFix.replace(
            context.segment,
            [
                CodeSegment(
                    raw="!=",
                    name="not_equal_to",
                    type="comparison_operator",
                )
            ],
        )

        return LintResult(context.segment, [fix])
