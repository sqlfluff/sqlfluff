"""Implementation of Rule L099."""
from collections import defaultdict
from typing import cast, Dict, List, NamedTuple, Optional, Union

from sqlfluff.core.dialects.base import Dialect
from sqlfluff.core.rules.base import BaseCrawler, LintResult
from sqlfluff.core.parser.segments.base import BaseSegment
from sqlfluff.core.rules.std import L020


class WildcardInfo(NamedTuple):
    """Structure returned by _get_wildcard_info()."""

    segment: BaseSegment
    tables: List[str]


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

    @classmethod
    def _get_wildcard_info(
        cls, select_info: L020.SelectStatementColumnsAndTables
    ) -> List[WildcardInfo]:
        buff = []
        for seg in select_info.select_targets:
            if seg.get_child("wildcard_expression"):
                if "." in seg.raw:
                    table = seg.raw.rsplit(".", 1)[0]
                    buff.append(WildcardInfo(seg, [table]))
                else:
                    # Unqualified '*', which means to include all columns from
                    # all the tables.
                    buff.append(
                        WildcardInfo(
                            seg,
                            [
                                alias_info.ref_str
                                for alias_info in select_info.table_aliases
                            ],
                        )
                    )
        return buff

    def gather_select_info(
        self, segment: BaseSegment, dialect: Dialect
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
    def get_select_info(
        cls,
        segment: BaseSegment,
        queries: Dict[str, List[L020.SelectStatementColumnsAndTables]],
        dialect: Dialect,
    ) -> Union[str, List[L020.SelectStatementColumnsAndTables]]:
        """Find SELECTs or table ref underneath segment.

        If we find a SELECT, return info list. If it's a table ref, return its
        name (str).
        """
        buff = []
        for seg in segment.recursive_crawl(
            "table_reference", "select_statement", recurse_into=False
        ):
            if seg is segment:
                # If we are starting with a select_statement, recursive_crawl()
                # returns the statement itself. Skip that.
                continue

            if seg.type == "table_reference":
                if not seg.is_qualified() and seg.raw in queries:
                    # It's a CTE.
                    return queries[seg.raw]
                else:
                    # It's an external table.
                    return seg.raw
            else:
                assert seg.type == "select_statement"
                # :TRICKY: Cast away "Optional" because early_exit=False ensures
                # we won't get a "None" result.
                buff.append(
                    cast(
                        L020.SelectStatementColumnsAndTables,
                        L020.Rule_L020.get_select_statement_info(
                            seg, dialect, early_exit=False
                        ),
                    )
                )
        if not buff:
            # If we reach here, the SELECT may be querying from a value table
            # function, e.g. UNNEST(). For our purposes, this is basically the
            # same as an external table. Return the "table" part as a string.
            table_expr = segment.get_child("main_table_expression")
            if table_expr:
                return table_expr.raw
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
                if wildcard.tables:
                    for wildcard_table in wildcard.tables:
                        self.logger.debug(
                            f"Wildcard: {wildcard.segment.raw} has target {wildcard_table}"
                        )
                        # Is it an alias?
                        alias_info = [
                            t
                            for t in select_info.table_aliases
                            if t.aliased and t.ref_str == wildcard_table
                        ]
                        if alias_info:
                            # Found the alias matching the wildcard. Recurse,
                            # analyzing the query associated with that alias.
                            select_info_target = self.get_select_info(
                                alias_info[0].table_expression, queries, dialect
                            )
                            if isinstance(select_info_target, str):
                                # It's an alias to an external table whose
                                # number of columns could vary without our
                                # knowledge. Thus, warn.
                                self.logger.debug(
                                    f"Query target {select_info_target} is external. Generating warning."
                                )
                                # TODO: It'd be better for the anchor to be the
                                # top-level query we started with. As currently
                                # written, this could be a deeply nested query
                                # where the rule finally determined to issue a
                                # warning. To be clear, the result is correct in
                                # terms of WHETHER to return a warning; this "TODO"
                                # is talking about what line of the query is
                                # referenced in the warning.
                                return LintResult(anchor=alias_info[0].table_expression)
                            else:
                                # Handle nested SELECT.
                                result = self.analyze_result_columns(
                                    select_info_target, dialect, queries
                                )
                                if result:
                                    return result
                        else:
                            # Not an alias. Is it a CTE?
                            if wildcard_table in queries:
                                # For each wildcard in select targets, recurse, i.e. look at the
                                # "upstream" query to see if it is wildcard free (i.e. known
                                # number of columns).
                                result = self.analyze_result_columns(
                                    queries[wildcard_table], dialect, queries
                                )
                                if result:
                                    return result
                            else:
                                # Not a CTE, not a table alias. Assume it's an external
                                # table whose number of columns could vary without our
                                # knowledge. Thus, warn.
                                self.logger.debug(
                                    f"Query target {wildcard_table} is external. Generating warning."
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
                    select_info_target = self.get_select_info(
                        select_info.select_statement, queries, dialect
                    )
                    assert isinstance(select_info_target, list)
                    result = self.analyze_result_columns(
                        cast(
                            List[L020.SelectStatementColumnsAndTables],
                            select_info_target,
                        ),
                        dialect,
                        queries,
                    )
                    if result:
                        return result

        return None

    def _eval(self, segment, **kwargs):
        """Outermost query should produce known number of columns."""
        if segment.is_type("statement"):
            dialect: Dialect = kwargs.get("dialect")
            queries = self.gather_select_info(segment, dialect)

            select_info = queries[None]
            return self.analyze_result_columns(select_info, dialect, queries)
        return None
