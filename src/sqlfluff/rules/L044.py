"""Implementation of Rule L044."""
from typing import Dict, List

from sqlfluff.core.rules.analysis.select_crawler import SelectCrawler
from sqlfluff.core.dialects.base import Dialect
from sqlfluff.core.rules.base import BaseRule, LintResult


class RuleFailure(Exception):
    """Exception class for reporting lint failure inside deeply nested code."""

    pass


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

    def _handle_alias(self, alias_info, dialect, queries):
        select_info_target = SelectCrawler.get(
            alias_info.from_expression_element, queries, dialect
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
            self._analyze_result_columns(select_info_target, dialect, queries)

    def _analyze_result_columns(
        self,
        select_info_list: List[SelectCrawler],
        dialect: Dialect,
        queries: Dict[str, List[SelectCrawler]],
    ):
        """Given info on a list of SELECTs, determine whether to warn."""
        # Recursively walk from the given query (select_info_list) to any
        # wildcard columns in the select targets. If every wildcard evdentually
        # resolves to a query without wildcards, all is well. Otherwise, warn.
        for select_info in select_info_list:
            self.logger.debug(f"Analyzing query: {select_info.select_statement.raw}")
            for wildcard in select_info.get_wildcard_info():
                if wildcard.tables:
                    for wildcard_table in wildcard.tables:
                        self.logger.debug(
                            f"Wildcard: {wildcard.segment.raw} has target {wildcard_table}"
                        )
                        # Is it an alias?
                        alias_info = select_info.find_alias(wildcard_table)
                        if alias_info:
                            # Found the alias matching the wildcard. Recurse,
                            # analyzing the query associated with that alias.
                            self._handle_alias(alias_info, dialect, queries)
                        else:
                            # Not an alias. Is it a CTE?
                            if wildcard_table in queries:
                                # Wildcard refers to a CTE. Analyze it.
                                self._analyze_result_columns(
                                    queries.pop(wildcard_table), dialect, queries
                                )
                            else:
                                # Not CTE, not table alias. Presumably an
                                # external table. Warn.
                                self.logger.debug(
                                    f"Query target {wildcard_table} is external. Generating warning."
                                )
                                raise RuleFailure()
                else:
                    # No table was specified with the wildcard. Assume we're
                    # querying from a nested select in FROM.
                    select_info_target = SelectCrawler.get(
                        select_info.select_statement, queries, dialect
                    )
                    assert isinstance(select_info_target, list)
                    self._analyze_result_columns(
                        select_info_target,
                        dialect,
                        queries,
                    )

    def _eval(self, segment, dialect, **kwargs):
        """Outermost query should produce known number of columns."""
        if segment.is_type("statement"):
            queries = SelectCrawler.gather(segment, dialect)

            # Begin analysis at the final, outer query (key=None).
            if None in queries:
                select_info = queries[None]
                try:
                    return self._analyze_result_columns(select_info, dialect, queries)
                except RuleFailure:
                    return LintResult(
                        anchor=queries[None][0].select_info.select_statement
                    )
        return None
