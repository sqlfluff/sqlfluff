"""Implementation of Rule CV01."""

from typing import Optional

from sqlfluff.core.parser import SymbolSegment
from sqlfluff.core.rules import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.utils.functional import FunctionalContext, sp


class Rule_CV01(BaseRule):
    """Consistent usage of ``!=`` or ``<>`` for "not equal to" operator.

    **Anti-pattern**

    .. code-block:: sql

        SELECT * FROM X WHERE 1 <> 2 AND 3 != 4;

    **Best practice**

    Ensure all "not equal to" comparisons are consistent, not mixing ``!=`` and ``<>``.

    .. code-block:: sql

        SELECT * FROM X WHERE 1 != 2 AND 3 != 4;

    """

    name = "convention.not_equal"
    aliases = ("L061",)
    groups = ("all", "convention")
    crawl_behaviour = SegmentSeekerCrawler({"comparison_operator"})
    config_keywords = ["preferred_not_equal_style"]
    is_fix_compatible = True

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Enforce consistent "not equal to" style."""
        self.preferred_not_equal_style: str

        # Get the comparison operator children
        raw_comparison_operators = (
            FunctionalContext(context)
            .segment.children()
            .select(select_if=sp.is_type("raw_comparison_operator"))
        )

        # Only check ``<>`` or ``!=`` operators
        raw_operator_list = [r.raw for r in raw_comparison_operators]
        if raw_operator_list not in [["<", ">"], ["!", "="]]:
            return None

        memory = context.memory
        # If style is consistent, add the style of the first occurence to memory
        if self.preferred_not_equal_style == "consistent":
            preferred_not_equal_style = context.memory.get("preferred_not_equal_style")
            if not preferred_not_equal_style:
                preferred_not_equal_style = (
                    "ansi" if raw_operator_list == ["<", ">"] else "c_style"
                )
                memory["preferred_not_equal_style"] = preferred_not_equal_style
        else:
            preferred_not_equal_style = self.preferred_not_equal_style

        if preferred_not_equal_style == "c_style":
            replacement = ["!", "="]
        elif preferred_not_equal_style == "ansi":
            replacement = ["<", ">"]

        # This operator already matches the existing style
        if raw_operator_list == replacement:
            return LintResult(memory=memory)

        # Provide a fix and replace ``<>`` with ``!=``
        # As each symbol is a separate symbol this is done in two steps:
        # Depending on style type, flip any inconsistent operators
        # 1. Flip < and !
        # 2. Flip > and =
        fixes = [
            LintFix.replace(
                raw_comparison_operators[0],
                [SymbolSegment(raw=replacement[0], type="raw_comparison_operator")],
            ),
            LintFix.replace(
                raw_comparison_operators[1],
                [SymbolSegment(raw=replacement[1], type="raw_comparison_operator")],
            ),
        ]

        return LintResult(anchor=context.segment, fixes=fixes, memory=memory)
