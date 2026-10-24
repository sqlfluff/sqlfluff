"""Implementation of Rule CV14."""

from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler


class Rule_CV14(BaseRule):
    """Prefer returning the matched column in a searched ``CASE`` expression.

    When a ``WHEN`` clause compares a column with a quoted string and
    ``THEN`` repeats that exact string, referencing the column instead
    makes similar branches easier to identify.

    The values may differ under case-insensitive comparisons, padding, or
    implicit conversions. This opinionated rule is **disabled by default**
    and reports violations without automatically changing the SQL.
    Enable it with:

    .. code-block:: cfg

        [sqlfluff:rules:convention.case_then_column]
        force_enable = True

    **Anti-pattern**

    .. code-block:: sql

        SELECT CASE WHEN status = 'open' THEN 'open' END FROM orders

    **Best practice**

    .. code-block:: sql

        SELECT CASE WHEN status = 'open' THEN status END FROM orders

    """

    name = "convention.case_then_column"
    aliases = ()
    groups = ("all", "convention")
    config_keywords = ["force_enable"]
    crawl_behaviour = SegmentSeekerCrawler({"case_expression"})

    def _eval(self, context: RuleContext) -> list[LintResult]:
        """Report repeated string literals in directly matched CASE branches."""
        self.force_enable: bool
        if not self.force_enable:
            return []

        case = context.segment
        # A simple CASE has an expression between CASE and the first WHEN.
        for child in case.segments:
            if child.is_type("when_clause"):
                break
            if child.is_type("expression"):
                return []

        results = []
        for when_clause in case.get_children("when_clause"):
            expressions = when_clause.get_children("expression")
            if len(expressions) != 2:
                continue

            condition, then_expression = expressions
            condition_parts = [seg for seg in condition.segments if seg.is_code]
            then_parts = [seg for seg in then_expression.segments if seg.is_code]
            if len(condition_parts) != 3 or len(then_parts) != 1:
                continue

            column, operator, matched_literal = condition_parts
            returned_literal = then_parts[0]
            if not (
                column.is_type("column_reference")
                and operator.is_type("comparison_operator")
                and operator.raw == "="
                and matched_literal.is_type("quoted_literal")
                and returned_literal.is_type("quoted_literal")
                and matched_literal.raw == returned_literal.raw
            ):
                continue
            if condition.is_templated or then_expression.is_templated:
                continue

            results.append(
                LintResult(
                    anchor=returned_literal,
                    description=(
                        f"Consider using column {column.raw!r} instead of "
                        f"repeating {returned_literal.raw!r} in THEN."
                    ),
                )
            )
        return results
