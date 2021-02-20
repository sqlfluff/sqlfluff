"""Implementation of Rule L099."""
from collections import defaultdict
from typing import cast, Dict, List, NamedTuple, Optional

from sqlfluff.core.dialects.base import Dialect
from sqlfluff.core.rules.base import BaseCrawler, LintResult
from sqlfluff.core.parser.segments.base import BaseSegment
from sqlfluff.core.rules.std import L020


class WildcardInfo(NamedTuple):
    """Structure returned by _get_wildcard_info()."""

    segment: BaseSegment
    table: Optional[str]


class Rule_L099(BaseCrawler):
    """Query produces an unknown number of result columns.

    | **Anti-pattern**
    | Querying all columns using `*` produces a query result where the number
    | or ordering of columns may vary due to schema changes in upstream data
    | sources. This should be avoided because it is prone to breakage in
    | production.

    .. code-block::

        WITH cte AS (
            SELECT * FROM foo
        )

        SELECT * FROM cte

    | **Best practice**
    | Somewhere along the "path" to the source data, specify columns explicitly.

    .. code-block::

        WITH cte AS (
            SELECT * FROM foo
        )

        SELECT a, b FROM cte

    """

    _works_on_unparsable = False

    # with_compound_statement
    #   common_table_expression
    #     select_statement
    #       select_clause
    #         select_target_element
    #   common_table_expression ...
    #   select_statement
    #     select_clause
    #       select_target_element

    @classmethod
    def _get_wildcard_info(
        cls, select_info: L020.SelectStatementColumnsAndTables
    ) -> List[WildcardInfo]:
        buff = []
        for seg in select_info.select_targets:
            if seg.get_child("wildcard_expression"):
                if "." in seg.raw:
                    table = seg.raw.rsplit(".", 1)[0]
                else:
                    if len(select_info.table_aliases) == 1:
                        # Unqualified '*' and there is only one table, so that
                        # must be the table. Probably need to revisit this to
                        # reconcile/consider alias vs actual table name.
                        table = select_info.table_aliases[0].ref_str
                    else:
                        table = None
                buff.append(WildcardInfo(seg, table))
        return buff

    def gather_select_info(
        self, segment, dialect: Dialect
    ) -> Dict[str, List[L020.SelectStatementColumnsAndTables]]:
        """Find top-level SELECTs and CTEs, return info."""
        queries = defaultdict(list)
        # Get all the TOP-LEVEL select statements and CTEs, then get the path
        # to each to determine the structure.
        # We specify recurse_into=False because we only want top-level select
        # statmeents and CTEs. We'll deal with nested selects later as needed,
        # when processing their top-level parent.
        for select_statement in segment.recursive_crawl(
            "select_statement", recurse_into=False
        ):
            path_to = segment.path_to(select_statement)

            # If it's a CTE, get the name and info on the query inside.
            cte = None
            for seg in path_to:
                if seg.is_type("common_table_expression"):
                    cte = seg
                    break
            select_name = cte.segments[0].raw if cte else None
            # TODO: Avoid as much of this work as possible, e.g. if the outer
            # query does not use a wildcard, we don't need to look at any of
            # the CTEs.
            select_info = L020.Rule_L020.get_select_statement_info(
                select_statement, dialect, early_exit=False
            )
            self.logger.debug(f"Storing select info for {select_name}")
            queries[select_name].append(select_info)
        return dict(queries)

    @classmethod
    def get_nested_select_info(
        cls, segment, dialect
    ) -> List[L020.SelectStatementColumnsAndTables]:
        """Find SELECTs underneath segment. Assume no CTEs."""
        # TODO: This function is very similar to gather_select_info() except
        # that it assumes there are no CTEs. Can it be eliminated?
        buff = []
        for select_statement in segment.recursive_crawl(
            "select_statement", recurse_into=False
        ):
            if select_statement is segment:
                # If we are starting with a select_statement, recursive_crawl()
                # returns the statement itself. Skip that.
                continue
            # :TRICKY: Cast away "Optional" because early_exit=False ensures
            # we won't get a "None" result.
            buff.append(
                cast(
                    L020.SelectStatementColumnsAndTables,
                    L020.Rule_L020.get_select_statement_info(
                        select_statement, dialect, early_exit=False
                    ),
                )
            )
        return buff

    def analyze_result_columns(
        self,
        select_info_list: List[L020.SelectStatementColumnsAndTables],
        dialect: Dialect,
        queries: Dict[str, List[L020.SelectStatementColumnsAndTables]],
    ) -> Optional[LintResult]:
        """Given info on a list of SELECTs, determine whether to warn."""
        # Recursively walk from the final query (key=None) to any wildcard
        # columns in the select targets. If it's wildcards all the way, warn.
        for select_info in select_info_list:
            self.logger.debug(f"Analyzing query: {select_info.select_statement.raw}")
            wildcards = self._get_wildcard_info(select_info)
            for wildcard in wildcards:
                self.logger.debug(f"Wildcard: {wildcard.segment.raw} has target {wildcard.table}")
                if wildcard.table:
                    select_info_target = queries.get(wildcard.table)
                    if select_info_target:
                        # For each wildcard in select targets, recurse, i.e. look at the
                        # "upstream" query to see if it is wildcard free (i.e. known
                        # number of columns).
                        result = self.analyze_result_columns(
                            select_info_target, dialect, queries
                        )
                        if result:
                            return result
                    else:
                        # Not a CTE. Maybe an alias?
                        alias = [
                            t
                            for t in select_info.table_aliases
                            if t.aliased and t.ref_str == wildcard.table
                        ]
                        if alias:
                            # Found the alias matching the wildcard. Recurse,
                            # analyzing the query associated with that alias.
                            select_info_target = self.get_nested_select_info(
                                alias[0].table_expression, dialect
                            )
                            result = self.analyze_result_columns(
                                select_info_target, dialect, queries
                            )
                            if result:
                                return result
                        else:
                            # Not a CTE, not a table alias. Assume it's an external
                            # table whose number of columns could vary without our
                            # knowledge. Thus, warn.
                            self.logger.debug(
                                f"Query target {wildcard.table} is external. Generating warning."
                            )
                            # TODO: It'd be better for the anchor to be the
                            # top-level query we started with. As currently
                            # written, this could be a deeply nested query
                            # where the rule finally determined to issue a
                            # warning. To be clear, the result is correct in
                            # terms of WHETHER to return a warning; this "TODO"
                            # is talking about what line of the query is
                            # referenced in the warning.
                            return LintResult(anchor=select_info.select_statement)
                else:
                    # No table was specified with the wildcard. Assume we're
                    # querying from a nested select in FROM. Question: Is it
                    # possible we're querying from a single table in FROM like
                    # test_2?
                    select_info_target = self.get_nested_select_info(
                        select_info.select_statement, dialect
                    )
                    result = self.analyze_result_columns(
                        select_info_target, dialect, queries
                    )
                    if result:
                        return result

        return None

    def _eval(self, segment, **kwargs) -> Optional[LintResult]:
        """Outermost query should produce known number of columns."""
        if segment.is_type("statement"):
            dialect = kwargs.get("dialect")
            queries = self.gather_select_info(segment, dialect)

            select_info = queries[None]
            return self.analyze_result_columns(select_info, dialect, queries)
        return None
