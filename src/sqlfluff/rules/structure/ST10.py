"""Implementation of Rule ST10."""

from collections.abc import Iterator

from sqlfluff.core.rules import BaseRule, EvalResultType, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler


class Rule_ST10(BaseRule):
    """Redundant constant expression.

    Including an expression that always evaluates to
    either ``TRUE`` or ``FALSE`` regardless of the input columns is
    unnecessary and makes statements harder to read and understand.

    Constant conditions are sometimes mistakes (by mistyping the column
    name intended), and sometimes the result of incorrect information that
    they are necessary in some circumstances. In the former case, they can
    sometimes result in a cartesian join if it was supposed to be a join
    condition. Given the ambiguity of intent, this rule does not suggest
    an automatic fix, and instead invites the user to resolve the problem
    manually.

    **Anti-pattern**

    .. code-block:: sql

        SELECT *
        FROM my_table
        -- This following WHERE clause is redundant.
        WHERE my_table.col = my_table.col

    **Best practice**

    .. code-block:: sql

        SELECT *
        FROM my_table
        -- Replace with a condition that includes meaningful logic,
        -- or remove the condition entirely.
        WHERE my_table.col > 3
    """

    name = "structure.constant_expression"
    aliases = ()
    groups: tuple[str, ...] = ("all", "structure")
    config_keywords = []
    crawl_behaviour = SegmentSeekerCrawler({"expression"})
    is_fix_compatible = False

    def _eval(self, context: RuleContext) -> EvalResultType:
        return [lint_result for lint_result in self._eval_gen(context)]

    def _eval_gen(self, context: RuleContext) -> Iterator[LintResult]:
        assert context.segment.is_type("expression")
        subsegments = context.segment.segments
        count_subsegments = len(subsegments)
        # The following literal expressions are allowable because they're
        # often included in auto-generated code.
        # NOTE: In future this could become a configuration option.
        allowable_literal_expressions = {"1 = 1", "1 = 0"}

        for idx, seg in enumerate(context.segment.segments):
            if seg.is_type("comparison_operator"):
                if seg.raw not in ("=", "!=", "<>"):
                    continue

                has_other_operators_on_lhs = any(
                    subsegments[i]
                    for i in range(idx - 1, -1, -1)
                    if subsegments[i].is_type("comparison_operator", "binary_operator")
                )

                has_other_operators_on_rhs = any(
                    subsegments[i]
                    for i in range(idx - 1, -1, -1)
                    if subsegments[i].is_type("comparison_operator", "binary_operator")
                )

                if has_other_operators_on_lhs or has_other_operators_on_rhs:
                    # Figuring our precedence of different operators is outside of scope
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
                    # Should be unreachable with correctly parsed tree
                    continue  # pragma: no cover

                if lhs.is_templated or rhs.is_templated:
                    continue

                # literals need explicit handling (due to well-defined allow-list)
                if lhs.is_type("literal") and rhs.is_type("literal"):
                    expr_s = f"{lhs.raw_normalized()} {seg.raw} {rhs.raw_normalized()}"
                    if expr_s in allowable_literal_expressions:
                        # ignore based on allowlist
                        continue
                else:
                    if lhs.type != rhs.type:
                        continue
                    if lhs.raw_normalized() != rhs.raw_normalized():
                        continue

                # attach violation to eq/ne operator in expression
                yield LintResult(seg)
