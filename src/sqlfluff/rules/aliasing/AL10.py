"""Implementation of Rule AL10."""

from sqlfluff.core.parser import BaseSegment
from sqlfluff.core.rules import BaseRule, EvalResultType, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler


class Rule_AL10(BaseRule):
    """Derived tables must have an alias.

    A derived table (subquery in a ``FROM`` clause) without an alias will
    cause a runtime error in most SQL dialects including MySQL, PostgreSQL,
    and T-SQL.

    **Anti-pattern**

    A subquery in a ``FROM`` clause without an alias.

    .. code-block:: sql

        SELECT *
        FROM (
            SELECT 1 AS a
        )

    **Best practice**

    Add an alias to the derived table.

    .. code-block:: sql

        SELECT *
        FROM (
            SELECT 1 AS a
        ) AS derived

    """

    name = "aliasing.required"
    aliases = ()
    groups = ("all", "core", "aliasing")
    crawl_behaviour = SegmentSeekerCrawler({"from_expression_element"})
    is_fix_compatible = False

    def _eval(self, context: RuleContext) -> EvalResultType:
        """Check that derived tables have an alias."""
        assert context.segment.is_type("from_expression_element")

        # Check if this FROM expression contains a derived table.
        if not self._contains_derived_table(context.segment):
            return None

        # It's a derived table. Check if it has an alias.
        if context.segment.get_child("alias_expression"):
            return None

        # Derived table without an alias.
        return LintResult(
            anchor=context.segment,
            description="Derived table must have an alias.",
        )

    @staticmethod
    def _contains_derived_table(from_expression_element: BaseSegment) -> bool:
        """Check whether a FROM expression element contains a derived table.

        A derived table is a subquery (SELECT, set expression, or CTE)
        nested inside a FROM clause, potentially wrapped in brackets.
        """
        for segment in from_expression_element.iter_segments(expanding=("bracketed",)):
            if segment.is_type("table_expression"):
                # Check for nested SELECT, UNION/INTERSECT/EXCEPT, or CTE.
                for seg in segment.iter_segments(expanding=("bracketed",)):
                    if seg.is_type(
                        "select_statement",
                        "set_expression",
                        "with_compound_statement",
                    ):
                        return True
        return False
