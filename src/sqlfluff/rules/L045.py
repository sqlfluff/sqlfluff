"""Implementation of Rule L045."""
from typing import Dict, List

from sqlfluff.core.dialects.base import Dialect
from sqlfluff.core.rules.base import BaseRule, LintResult
from sqlfluff.core.rules.analysis.select_crawler import SelectCrawler
from sqlfluff.core.rules.doc_decorators import document_fix_compatible


@document_fix_compatible
class Rule_L045(BaseRule):
    """Query defines a CTE (common-table expression) but does not use it.

    | **Anti-pattern**
    | Defining a CTE that is not used by the query is harmless, but it means
    | the code is unnecesary and could be removed.

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

    | **Best practice**
    | Remove unused CTEs.

    .. code-block:: sql

        WITH cte1 AS (
          SELECT a
          FROM t
        )

        SELECT *
        FROM cte1
    """

    @classmethod
    def _visit_sources(
        cls,
        select_info_list: List[SelectCrawler],
        dialect: Dialect,
        queries: Dict[str, List[SelectCrawler]],
    ):
        for select_info in select_info_list:
            for source in SelectCrawler.crawl(
                select_info.select_statement, queries, dialect
            ):
                if isinstance(source, list):
                    cls._visit_sources(source, dialect, queries)

    def _eval(self, segment, dialect, **kwargs):
        if segment.is_type("statement"):
            queries = SelectCrawler.gather(segment, dialect)
            if None in queries:
                # Begin analysis at the final, outer query (key=None).
                self._visit_sources(queries.pop(None), dialect, queries)
                if queries:
                    return LintResult(anchor=segment)
        return None
