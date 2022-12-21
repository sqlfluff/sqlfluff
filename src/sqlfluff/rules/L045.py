"""Implementation of Rule L045."""
from typing import Iterator

from sqlfluff.core.rules import BaseRule, EvalResultType, LintResult, RuleContext
from sqlfluff.utils.analysis.select_crawler import Query, SelectCrawler
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.core.rules.doc_decorators import document_groups


@document_groups
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

    groups = ("all", "core")
    crawl_behaviour = SegmentSeekerCrawler({"statement"})

    @classmethod
    def _find_all_ctes(cls, query: Query) -> Iterator[Query]:
        if query.ctes:
            yield query
        for query in query.ctes.values():
            yield from cls._find_all_ctes(query)

    @classmethod
    def _visit_sources(cls, query: Query):
        for selectable in query.selectables:
            for source in query.crawl_sources(selectable.selectable, pop=True):
                if isinstance(source, Query):
                    cls._visit_sources(source)
        for child in query.children:
            cls._visit_sources(child)

    def _eval(self, context: RuleContext) -> EvalResultType:
        result = []
        crawler = SelectCrawler(context.segment, context.dialect)
        if crawler.query_tree:
            # Begin analysis at the final, outer query (key=None).
            queries_with_ctes = list(self._find_all_ctes(crawler.query_tree))
            self._visit_sources(crawler.query_tree)
            for query in queries_with_ctes:
                if query.ctes:
                    result += [
                        LintResult(
                            anchor=query.cte_name_segment,
                            description=f"Query defines CTE "
                            f'"{query.cte_name_segment.raw}" '
                            f"but does not use it.",
                        )
                        for query in query.ctes.values()
                        if query.cte_name_segment
                    ]
        return result
