"""Implementation of Rule L045."""
from sqlfluff.core.rules.base import BaseRule, EvalResultType, LintResult, RuleContext
from sqlfluff.core.rules.analysis.select_crawler import Query, SelectCrawler


class Rule_L045(BaseRule):
    """Query defines a CTE (common-table expression) but does not use it.

    **Anti-pattern**

    Defining a CTE that is not used by the query is harmless, but it means
    the code is unnecessary and could be removed.

    .. code-block:: sql

        WITH cte1 AS (
          SELECT a
          FROM t
        ),
        cte2 AS (
          SELECT b
          FROM u
        )

        SELECT *
        FROM cte1

    **Best practice**

    Remove unused CTEs.

    .. code-block:: sql

        WITH cte1 AS (
          SELECT a
          FROM t
        )

        SELECT *
        FROM cte1
    """

    @classmethod
    def _visit_sources(cls, query: Query):
        for selectable in query.selectables:
            for source in query.crawl_sources(selectable.selectable, pop=True):
                if isinstance(source, Query):
                    cls._visit_sources(source)

    def _eval(self, context: RuleContext) -> EvalResultType:
        if context.segment.is_type("statement"):
            crawler = SelectCrawler(context.segment, context.dialect)
            if crawler.query_tree:
                # Begin analysis at the final, outer query (key=None).
                self._visit_sources(crawler.query_tree)
                if crawler.query_tree.ctes:
                    return [
                        LintResult(
                            anchor=query.cte_name_segment,
                            description=f"Query defines CTE "
                            f'"{query.cte_name_segment.raw}" '
                            f"but does not use it.",
                        )
                        for query in crawler.query_tree.ctes.values()
                        if query.cte_name_segment
                    ]
        return None
