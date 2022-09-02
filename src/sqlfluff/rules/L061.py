"""Implementation of Rule L061."""

from typing import Optional

from sqlfluff.core.parser.segments.raw import SymbolSegment
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.core.rules import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.doc_decorators import document_fix_compatible, document_groups
from sqlfluff.utils.functional import sp, FunctionalContext


@document_groups
@document_fix_compatible
class Rule_L061(BaseRule):
    """Use ``!=`` instead of ``<>`` for "not equal to" comparisons.

    **Anti-pattern**

    ``<>`` means ``not equal`` but doesn't sound like this when we say it out loud.

    .. code-block:: sql

        SELECT * FROM X WHERE 1 <> 2;

    **Best practice**

    Use ``!=`` instead because its sounds more natural and is more common in other
    programming languages.

    .. code-block:: sql

        SELECT * FROM X WHERE 1 != 2;

    """

    groups = ("all",)
    crawl_behaviour = SegmentSeekerCrawler({"comparison_operator"})

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Use ``!=`` instead of ``<>`` for "not equal to" comparison."""
        # Get the comparison operator children
        raw_comparison_operators = (
            FunctionalContext(context)
            .segment.children()
            .select(select_if=sp.is_type("raw_comparison_operator"))
        )

        # Only care about ``<>``
        if [r.raw for r in raw_comparison_operators] != ["<", ">"]:
            return None

        # Provide a fix and replace ``<>`` with ``!=``
        # As each symbol is a separate symbol this is done in two steps:
        # 1. Replace < with !
        # 2. Replace > with =
        fixes = [
            LintFix.replace(
                raw_comparison_operators[0],
                [SymbolSegment(raw="!", type="raw_comparison_operator")],
            ),
            LintFix.replace(
                raw_comparison_operators[1],
                [SymbolSegment(raw="=", type="raw_comparison_operator")],
            ),
        ]

        return LintResult(context.segment, fixes)
