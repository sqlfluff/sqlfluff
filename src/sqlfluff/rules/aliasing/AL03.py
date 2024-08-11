"""Implementation of Rule AL03."""

from typing import Optional

from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.utils.functional import FunctionalContext, Segments, sp


class Rule_AL03(BaseRule):
    """Column expression without alias. Use explicit `AS` clause.

    **Anti-pattern**

    In this example, there is no alias for both sums.

    .. code-block:: sql

        SELECT
            sum(a),
            sum(b)
        FROM foo

    **Best practice**

    Add aliases.

    .. code-block:: sql

        SELECT
            sum(a) AS a_sum,
            sum(b) AS b_sum
        FROM foo

    """

    name = "aliasing.expression"
    aliases = ("L013",)
    groups = ("all", "core", "aliasing")
    config_keywords = ["allow_scalar"]
    crawl_behaviour = SegmentSeekerCrawler({"select_clause_element"})

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Column expression without alias. Use explicit `AS` clause.

        We look for the select_clause_element segment, and then evaluate
        whether it has an alias segment or not and whether the expression
        is complicated enough. `parent_stack` is to assess how many other
        elements there are.

        """
        functional_context = FunctionalContext(context)
        segment = functional_context.segment
        children = segment.children()
        # If we have an alias its all good
        if children.any(sp.is_type("alias_expression")):
            return None

        # Ignore if it's a function with EMITS clause as EMITS is equivalent to AS
        if (
            children.select(sp.is_type("function"))
            .children()
            .select(sp.is_type("emits_segment"))
        ):
            return None

        # Ignore if it's a cast_expression with non-function enclosed children
        # For example, we do not want to ignore something like func()::type
        # but we can ignore something like a::type
        if children.children().select(
            sp.is_type("cast_expression")
        ) and not children.children().select(
            sp.is_type("cast_expression")
        ).children().any(
            sp.is_type("function")
        ):
            return None

        parent_stack = functional_context.parent_stack

        # Ignore if it is part of a CTE with column names
        if (
            parent_stack.last(sp.is_type("common_table_expression"))
            .children()
            .any(sp.is_type("cte_column_list"))
        ):
            return None

        # Ignore if using a columns expression. A nested function such as
        # ``MIN(COLUMNS(*))`` will assign the same alias to all columns.
        if len(children.recursive_crawl("columns_expression")) > 0:
            return None

        select_clause_children = children.select(sp.not_(sp.is_type("star")))
        is_complex_clause = _recursively_check_is_complex(select_clause_children)
        if not is_complex_clause:
            return None
        # No fixes, because we don't know what the alias should be,
        # the user should document it themselves.
        if self.allow_scalar:  # type: ignore
            # Check *how many* elements/columns there are in the select
            # statement. If this is the only one, then we won't
            # report an error.
            immediate_parent = parent_stack.last()
            elements = immediate_parent.children(sp.is_type("select_clause_element"))
            num_elements = len(elements)

            if num_elements > 1:
                return LintResult(anchor=context.segment)
            return None

        return LintResult(anchor=context.segment)


def _recursively_check_is_complex(select_clause_or_exp_children: Segments) -> bool:
    forgiveable_types = [
        "whitespace",
        "newline",
        "column_reference",
        "wildcard_expression",
        "bracketed",
    ]
    selector = sp.not_(sp.is_type(*forgiveable_types))
    filtered = select_clause_or_exp_children.select(selector)
    remaining_count = len(filtered)

    # Once we have removed the above if nothing remains,
    # then this statement/expression was simple
    if remaining_count == 0:
        return False

    first_el = filtered.first()
    # Anything except a single expression seg remains
    # Then it was complex
    if remaining_count > 1 or not first_el.all(sp.is_type("expression")):
        return True

    # If we have just an expression check if it was simple
    return _recursively_check_is_complex(first_el.children())
