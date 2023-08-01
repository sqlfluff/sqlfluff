"""Implementation of Rule AL06."""

from typing import List, Optional

from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.utils.functional import FunctionalContext


class Rule_AL06(BaseRule):
    """Enforce table alias lengths in from clauses and join conditions.

    **Anti-pattern**

    In this example, alias ``o`` is used for the orders table.

    .. code-block:: sql

        SELECT
            SUM(o.amount) as order_amount,
        FROM orders as o


    **Best practice**

    Avoid aliases. Avoid short aliases when aliases are necessary.

    See also: :class:`Rule_AL07`.

    .. code-block:: sql

        SELECT
            SUM(orders.amount) as order_amount,
        FROM orders

        SELECT
            replacement_orders.amount,
            previous_orders.amount
        FROM
            orders AS replacement_orders
        JOIN
            orders AS previous_orders
            ON replacement_orders.id = previous_orders.replacement_id
    """

    name = "aliasing.length"
    aliases = ("L066",)
    groups = ("all", "core", "aliasing")
    config_keywords = ["min_alias_length", "max_alias_length"]
    crawl_behaviour = SegmentSeekerCrawler({"select_statement"})

    def _eval(self, context: RuleContext) -> Optional[List[LintResult]]:
        """Identify aliases in from clause and join conditions.

        Find base table, table expressions in join, and other expressions in select
        clause and decide if it's needed to report them.
        """
        self.min_alias_length: Optional[int]
        self.max_alias_length: Optional[int]

        assert context.segment.is_type("select_statement")
        children = FunctionalContext(context).segment.children()
        from_expression_elements = children.recursive_crawl("from_expression_element")

        return self._lint_aliases(from_expression_elements) or None

    def _lint_aliases(self, from_expression_elements) -> Optional[List[LintResult]]:
        """Lint all table aliases."""
        # A buffer to keep any violations.
        violation_buff = []

        # For each table, check whether it is aliased, and if so check the
        # lengths.
        for from_expression_element in from_expression_elements:
            table_expression = from_expression_element.get_child("table_expression")
            table_ref = (
                table_expression.get_child("object_reference")
                if table_expression
                else None
            )

            # If the from_expression_element has no object_reference - skip it
            # An example case is a lateral flatten, where we have a function segment
            # instead of a table_reference segment.
            if not table_ref:
                continue

            # If there's no alias expression - skip it
            alias_exp_ref = from_expression_element.get_child("alias_expression")
            if alias_exp_ref is None:
                continue

            alias_identifier_ref = alias_exp_ref.get_child("identifier")

            if self.min_alias_length is not None:
                if len(alias_identifier_ref.raw) < self.min_alias_length:
                    violation_buff.append(
                        LintResult(
                            anchor=alias_identifier_ref,
                            description=(
                                "Aliases should be at least {} character(s) long."
                            ).format(self.min_alias_length),
                        )
                    )

            if self.max_alias_length is not None:
                if len(alias_identifier_ref.raw) > self.max_alias_length:
                    violation_buff.append(
                        LintResult(
                            anchor=alias_identifier_ref,
                            description=(
                                "Aliases should be no more than {} character(s) long."
                            ).format(self.max_alias_length),
                        )
                    )

        return violation_buff or None
