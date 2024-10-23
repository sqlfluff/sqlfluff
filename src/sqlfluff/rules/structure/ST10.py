"""Implementation of Rule ST10."""

from typing import Iterator, Tuple

from sqlfluff.core.rules import BaseRule, EvalResultType, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler


class Rule_ST10(BaseRule):
    """Const expression rule.

    **Anti-pattern**

    .. code-block:: sql

         -- TODO
        SELECT 1;

    **Best practice**

    .. code-block:: sql

         -- TODO
        SELECT 1;

    """

    name = "structure.const_expression"
    aliases = ()
    groups: Tuple[str, ...] = ("all", "structure")
    config_keywords = []
    crawl_behaviour = SegmentSeekerCrawler({"expression"})
    is_fix_compatible = False

    def _eval(self, context: RuleContext) -> EvalResultType:
        return [lint_result for lint_result in self._eval_gen(context)]

    def _eval_gen(self, context: RuleContext) -> Iterator[LintResult]:
        assert context.segment.is_type("expression")
        subsegments = context.segment.segments
        count_subsegments = len(subsegments)
        for idx, seg in enumerate(context.segment.segments):
            if seg.is_type("comparison_operator"):
                if seg.raw not in ("=", "!=", "<>"):
                    continue
                lhs = next(
                    (
                        subsegments[i]
                        for i in range(idx - 1, -1, -1)
                        if not subsegments[i].is_whitespace
                    ),
                    None,
                )
                rhs = next(
                    (
                        subsegments[i]
                        for i in range(idx + 1, count_subsegments, 1)
                        if not subsegments[i].is_whitespace
                    ),
                    None,
                )
                if not lhs or not rhs:
                    continue
                if lhs.raw_normalized() != rhs.raw_normalized():
                    continue

                expr_str = f"{lhs.raw_normalized()} {seg.raw} {rhs.raw_normalized()}"
                if expr_str in ("1 = 1", "1 = 0"):
                    continue
                yield LintResult(context.segment)
