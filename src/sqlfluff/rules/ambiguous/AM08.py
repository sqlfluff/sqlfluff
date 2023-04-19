"""Implementation of Rule AM08."""
from typing import Optional, List, Tuple

from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.utils.functional import sp, FunctionalContext


class Rule_AM08(BaseRule):
    """Unnecessary ``ORDER BY`` clauses.

    .. note::
       ``ORDER BY`` clauses from ``WINDOW`` clauses are ignored by this rule.

    **Anti-pattern**

      ``ORDER BY`` columns in Redshift do nothing.
    
    .. code-block:: sql

        SELECT
            LAST_VALUE(foo) OVER (PARTITION BY bar ORDER BY bar) AS foo,
            bar
        FROM fake_table
        ORDER BY
            1, 2;

    **Best practice**

    REMOVE ``ORDER BY`` clause.

    .. code-block:: sql

        SELECT
            LAST_VALUE(foo) OVER (PARTITION BY bar ORDER BY bar) AS foo,
            bar,
        FROM fake_table
    """

    name = "ambiguous.order_by"
    aliases = ("L070",)
    groups: Tuple[str, ...] = ("all", "core", "ambiguous")
    crawl_behaviour = SegmentSeekerCrawler({"orderby_clause"})
    _ignore_types: List[str] = ["withingroup_clause", "window_specification"]

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Non operational ORDER BY clauses."""

        # We only care about ORDER BY clauses.
        assert context.segment.all(sp.is_type("orderby_clause"))
    
        # Ignore Windowing clauses
        if FunctionalContext(context).parent_stack.any(sp.is_type(*self._ignore_types)):
            return LintResult(memory=context.memory)
        
        #if segment.children(sp.is_type("orderby_clause")):
        return LintResult(memory=context.memory)
