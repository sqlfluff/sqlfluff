"""Implementation of Rule AM06."""

from typing import List, Optional, Tuple

from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.utils.functional import FunctionalContext, sp


class Rule_AM06(BaseRule):
    """Inconsistent column references in ``GROUP BY/ORDER BY`` clauses.

    .. note::
       ``ORDER BY`` clauses from ``WINDOW`` clauses are ignored by this rule.

    **Anti-pattern**

    A mix of implicit and explicit column references are used in a ``GROUP BY``
    clause.

    .. code-block:: sql
       :force:

        SELECT
            foo,
            bar,
            sum(baz) AS sum_value
        FROM fake_table
        GROUP BY
            foo, 2;

        -- The same also applies to column
        -- references in ORDER BY clauses.

        SELECT
            foo,
            bar
        FROM fake_table
        ORDER BY
            1, bar;

    **Best practice**

    Reference all ``GROUP BY``/``ORDER BY`` columns either by name or by position.

    .. code-block:: sql
       :force:

        -- GROUP BY: Explicit
        SELECT
            foo,
            bar,
            sum(baz) AS sum_value
        FROM fake_table
        GROUP BY
            foo, bar;

        -- ORDER BY: Explicit
        SELECT
            foo,
            bar
        FROM fake_table
        ORDER BY
            foo, bar;

        -- GROUP BY: Implicit
        SELECT
            foo,
            bar,
            sum(baz) AS sum_value
        FROM fake_table
        GROUP BY
            1, 2;

        -- ORDER BY: Implicit
        SELECT
            foo,
            bar
        FROM fake_table
        ORDER BY
            1, 2;
    """

    name = "ambiguous.column_references"
    aliases = ("L054",)
    groups: Tuple[str, ...] = ("all", "core", "ambiguous")
    config_keywords = ["group_by_and_order_by_style"]
    crawl_behaviour = SegmentSeekerCrawler(
        {"groupby_clause", "orderby_clause", "grouping_expression_list"}
    )
    _ignore_types: List[str] = [
        "withingroup_clause",
        "window_specification",
        "aggregate_order_by",
    ]

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Inconsistent column references in GROUP BY/ORDER BY clauses."""
        # Config type hints
        self.group_by_and_order_by_style: str

        # We only care about GROUP BY/ORDER BY clauses.
        assert context.segment.is_type(
            "groupby_clause", "orderby_clause", "grouping_expression_list"
        )

        # Ignore Windowing clauses
        if FunctionalContext(context).parent_stack.any(sp.is_type(*self._ignore_types)):
            return LintResult(memory=context.memory)

        # Look at child segments and map column references to either the implicit or
        # explicit category.
        # N.B. segment names are used as the numeric literal type is 'raw', so best to
        # be specific with the name.
        column_reference_category_map = {
            "column_reference": "explicit",
            "expression": "explicit",
            "numeric_literal": "implicit",
        }
        column_reference_category_set = {
            column_reference_category_map[segment.get_type()]
            for segment in context.segment.segments
            if segment.is_type(*column_reference_category_map.keys())
        }

        # If there are no column references then just return
        if not column_reference_category_set:  # pragma: no cover
            return LintResult(memory=context.memory)

        if self.group_by_and_order_by_style == "consistent":
            # If consistent naming then raise lint error if either:

            if len(column_reference_category_set) > 1:
                # 1. Both implicit and explicit column references are found in the same
                # clause.
                return LintResult(
                    anchor=context.segment,
                    memory=context.memory,
                )
            else:
                # 2. A clause is found to contain column name references that
                #    contradict the precedent set in earlier clauses.
                current_group_by_order_by_convention = (
                    column_reference_category_set.pop()
                )
                prior_group_by_order_by_convention = context.memory.get(
                    "prior_group_by_order_by_convention"
                )

                if prior_group_by_order_by_convention and (
                    prior_group_by_order_by_convention
                    != current_group_by_order_by_convention
                ):
                    return LintResult(
                        anchor=context.segment,
                        memory=context.memory,
                    )

                context.memory["prior_group_by_order_by_convention"] = (
                    current_group_by_order_by_convention
                )
        else:
            # If explicit or implicit naming then raise lint error
            # if the opposite reference type is detected.
            if any(
                category != self.group_by_and_order_by_style
                for category in column_reference_category_set
            ):
                return LintResult(
                    anchor=context.segment,
                    memory=context.memory,
                )

        # Return memory for later clauses.
        return LintResult(memory=context.memory)
