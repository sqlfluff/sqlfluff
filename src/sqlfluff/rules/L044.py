"""Implementation of Rule L044."""
from typing import Optional

from sqlfluff.core.rules.analysis.select_crawler import Query, SelectCrawler
from sqlfluff.core.parser import BaseSegment
from sqlfluff.core.rules.base import BaseRule, LintResult, RuleContext


class RuleFailure(Exception):
    """Exception class for reporting lint failure inside deeply nested code."""

    def __init__(self, anchor: BaseSegment):
        self.anchor: BaseSegment = anchor


class Rule_L044(BaseRule):
    """Query produces an unknown number of result columns.

    | **Anti-pattern**
    | Querying all columns using `*` produces a query result where the number
    | or ordering of columns changes if the upstream table's schema changes.
    | This should generally be avoided because it can cause slow performance,
    | cause important schema changes to go undetected, or break production code.
    | For example:
    | * If a query does `SELECT t.*` and is expected to return columns `a`, `b`,
    |   and `c`, the actual columns returned will be wrong/different if columns
    |   are added to or deleted from the input table.
    | * `UNION` and `DIFFERENCE` clauses require the inputs have the same number
    |   of columns (and compatible types).
    | * `JOIN` queries may break due to new column name conflicts, e.g. the
    |   query references a column "c" which initially existed in only one input
    |   table but a column of the same name is added to another table.
    | * `CREATE TABLE (<<column schema>>) AS SELECT *`


    .. code-block:: sql

        WITH cte AS (
            SELECT * FROM foo
        )

        SELECT * FROM cte
        UNION
        SELECT a, b FROM t

    | **Best practice**
    | Somewhere along the "path" to the source data, specify columns explicitly.

    .. code-block:: sql

        WITH cte AS (
            SELECT * FROM foo
        )

        SELECT a, b FROM cte
        UNION
        SELECT a, b FROM t

    """

    _works_on_unparsable = False

    def _handle_alias(self, selectable, alias_info, query):
        select_info_target = SelectCrawler.get(
            query, alias_info.from_expression_element
        )[0]
        if isinstance(select_info_target, str):
            # It's an alias to an external table whose
            # number of columns could vary without our
            # knowledge. Thus, warn.
            self.logger.debug(
                f"Query target {select_info_target} is external. Generating warning."
            )
            raise RuleFailure(selectable.selectable)
        else:
            # Handle nested SELECT.
            self._analyze_result_columns(select_info_target)

    def _analyze_result_columns(self, query: Query):
        """Given info on a list of SELECTs, determine whether to warn."""
        # Recursively walk from the given query (select_info_list) to any
        # wildcard columns in the select targets. If every wildcard evdentually
        # resolves to a query without wildcards, all is well. Otherwise, warn.
        assert query.selectables
        for selectable in query.selectables:
            self.logger.debug(f"Analyzing query: {selectable.selectable.raw}")
            for wildcard in selectable.get_wildcard_info():
                if wildcard.tables:
                    for wildcard_table in wildcard.tables:
                        self.logger.debug(
                            f"Wildcard: {wildcard.segment.raw} has target {wildcard_table}"
                        )
                        # Is it an alias?
                        alias_info = selectable.find_alias(wildcard_table)
                        if alias_info:
                            # Found the alias matching the wildcard. Recurse,
                            # analyzing the query associated with that alias.
                            self._handle_alias(selectable, alias_info, query)
                        else:
                            # Not an alias. Is it a CTE?
                            cte = query.lookup_cte(wildcard_table)
                            if cte:
                                # Wildcard refers to a CTE. Analyze it.
                                self._analyze_result_columns(cte)
                            else:
                                # Not CTE, not table alias. Presumably an
                                # external table. Warn.
                                self.logger.debug(
                                    f"Query target {wildcard_table} is external. Generating warning."
                                )
                                raise RuleFailure(selectable.selectable)
                else:
                    # No table was specified with the wildcard. Assume we're
                    # querying from a nested select in FROM.
                    query_list = SelectCrawler.get(
                        query, query.selectables[0].selectable
                    )
                    for o in query_list:
                        if isinstance(o, Query):
                            self._analyze_result_columns(o)
                            return
                    assert False, "Should be unreachable"  # pragma: no cover

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Outermost query should produce known number of columns."""
        if context.segment.is_type("statement"):
            crawler = SelectCrawler(context.segment, context.dialect)

            # Begin analysis at the outer query.
            if crawler.query_tree:
                try:
                    return self._analyze_result_columns(crawler.query_tree)
                except RuleFailure as e:
                    return LintResult(anchor=e.anchor)
        return None
