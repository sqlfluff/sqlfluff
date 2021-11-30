"""Implementation of Rule L044."""
from typing import Dict, List, Optional

from sqlfluff.core.rules.analysis.select_crawler import Query, SelectCrawler
from sqlfluff.core.dialects.base import Dialect
from sqlfluff.core.rules.base import BaseRule, LintResult, RuleContext


class RuleFailure(Exception):
    """Exception class for reporting lint failure inside deeply nested code."""

    def __init__(self, anchor):
        self.anchor = anchor


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

    def _handle_alias(self, alias_info, dialect, query):
        select_info_target = SelectCrawler.get(
            query, alias_info.from_expression_element, dialect
        )
        if isinstance(select_info_target, str):
            # It's an alias to an external table whose
            # number of columns could vary without our
            # knowledge. Thus, warn.
            self.logger.debug(
                f"Query target {select_info_target} is external. Generating warning."
            )
            raise RuleFailure()
        else:
            # Handle nested SELECT.
            for o in select_info_target:
                if isinstance(o, list):
                    self._analyze_result_columns(o[0], dialect)
                    return

    def _analyze_result_columns(
        self,
        query: Query,
        dialect: Dialect,
    ):
        """Given info on a list of SELECTs, determine whether to warn."""
        # Recursively walk from the given query (select_info_list) to any
        # wildcard columns in the select targets. If every wildcard evdentually
        # resolves to a query without wildcards, all is well. Otherwise, warn.
        #for select_info in select_info_list:
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
                            self._handle_alias(alias_info, dialect, query)
                        else:
                            # Not an alias. Is it a CTE?
                            if wildcard_table in query.ctes:
                                # Wildcard refers to a CTE. Analyze it.
                                self._analyze_result_columns(
                                    query.ctes.pop(wildcard_table), dialect
                                )
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
                        # TODO: query.selectables[0] is wrong, probably needs to be a loop
                        query, query.selectables[0].selectable, dialect
                    )
                    for o in query_list:
                        if isinstance(o, list):
                            self._analyze_result_columns(
                                o[0],
                                dialect
                            )
                            return
                    assert False, "Should be unreachable"  # pragma: no cover

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Outermost query should produce known number of columns."""
        if context.segment.is_type("statement"):
            crawler = SelectCrawler.build(context.segment, context.dialect)

            # Begin analysis at the outer query.
            if crawler.query_tree.selectables:
                try:
                    return self._analyze_result_columns(
                        crawler.query_tree, crawler.dialect
                    )
                except RuleFailure as e:
                    return LintResult(
                        anchor=e.anchor
                    )
        return None
