"""Implementation of Rule CV01."""

from typing import Optional

from sqlfluff.core.parser import SymbolSegment
from sqlfluff.core.rules import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.utils.functional import FunctionalContext, sp


class Rule_CV01(BaseRule):
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

    name = "convention.not_equal"
    aliases = ("L061",)
    groups = ("all", "convention")
    crawl_behaviour = SegmentSeekerCrawler({"comparison_operator"})
    is_fix_compatible = True

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
