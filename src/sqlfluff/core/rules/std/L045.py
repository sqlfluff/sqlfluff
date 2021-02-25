"""Implementation of Rule L045."""
from typing import Dict, List

from sqlfluff.core.dialects.base import Dialect
from sqlfluff.core.rules.base import BaseCrawler, LintResult
from sqlfluff.core.rules.doc_decorators import document_fix_compatible
from sqlfluff.core.rules.std.L044 import SelectInfo


@document_fix_compatible
class Rule_L045(BaseCrawler):
    """Query defines a CTE (common-table expression) but does not use it.

    | **Anti-pattern**
    | Defining a CTE that is not used by the query is harmless, but it means
    | the code is unnecesary and could be removed.

    .. code-block::

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

    .. code-block::

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
        select_info_list: List[SelectInfo],
        dialect: Dialect,
        queries: Dict[str, List[SelectInfo]],
    ):
        for select_info in select_info_list:
            for alias_info in select_info.select_info.table_aliases:
                # Does the query read from a CTE? If so, visit the CTE.
                target = alias_info.table_expression.raw
                if target in queries:
                    select_info_target = queries.pop(target)
                    if isinstance(select_info_target, list):
                        cls._visit_sources(select_info_target, dialect, queries)

    def _eval(self, segment, **kwargs):
        if segment.is_type("statement"):
            dialect: Dialect = kwargs.get("dialect")
            queries = SelectInfo.gather(segment, dialect)

            # Begin analysis at the final, outer query (key=None).
            self._visit_sources(queries.pop(None), dialect, queries)
            if queries:
                return LintResult(anchor=segment)
        return None
