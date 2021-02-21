"""Implementation of Rule L043."""
from collections import defaultdict
from typing import Dict, List, NamedTuple, Optional, Union

from cached_property import cached_property

from sqlfluff.core.dialects.dialect_ansi import AliasInfo
from sqlfluff.core.dialects.base import Dialect
from sqlfluff.core.rules.base import BaseCrawler, LintResult
from sqlfluff.core.parser.segments.base import BaseSegment
from sqlfluff.core.rules.std import L020


class RuleFailure(Exception):
    """Exception class for reporting lint failure inside deeply nested code."""

    pass


class WildcardInfo(NamedTuple):
    """Structure returned by SelectInfo.get_wildcard_info().

    This class is a wrapper for L020.Rule_L020.get_select_statement_info(), plus
    some additional functionality required by this rule.
    """

    segment: BaseSegment
    tables: List[str]


class SelectInfo:
    """Class for analyzing SELECT statements."""

    @classmethod
    def gather(
        cls, segment: BaseSegment, dialect: Dialect
    ) -> Dict[Optional[str], List["SelectInfo"]]:
        """Find top-level SELECTs and CTEs, return info."""
        queries = defaultdict(list)
        # We specify recurse_into=False because we only want top-level select
        # statmeents and CTEs. We'll deal with nested selects later as needed,
        # when processing their top-level parent.
        for select_statement in segment.recursive_crawl(
            "select_statement", recurse_into=False
        ):
            select_name = cls._get_name_if_cte(select_statement, segment)
            queries[select_name].append(SelectInfo(select_statement, dialect))
        return dict(queries)

    @classmethod
    def get(
        cls,
        segment: BaseSegment,
        queries: Dict[str, List["SelectInfo"]],
        dialect: Dialect,
    ) -> Union[str, List["SelectInfo"]]:
        """Find SELECTs, table refs, or value table function calls in segment.

        If we find a SELECT, return info list. Otherwise, return table name
        or function call string.
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
                buff.append(SelectInfo(seg, dialect))
        if not buff:
            # If we reach here, the SELECT may be querying from a value table
            # function, e.g. UNNEST(). For our purposes, this is basically the
            # same as an external table. Return the "table" part as a string.
            table_expr = segment.get_child("main_table_expression")
            if table_expr:
                return table_expr.raw
        return buff

    def __init__(self, select_statement, dialect):
        self.select_statement = select_statement
        self.dialect = dialect

    @cached_property
    def select_info(self):
        """Returns SelectStatementColumnsAndTables on the SELECT."""
        result = L020.Rule_L020.get_select_statement_info(
            self.select_statement, self.dialect, early_exit=False
        )
        return result

    def find_alias(self, table: str) -> Optional[AliasInfo]:
        """Find corresponding table_aliases entry (if any) matching "table"."""
        alias_info = [
            t
            for t in self.select_info.table_aliases
            if t.aliased and t.ref_str == table
        ]
        assert len(alias_info) <= 1
        return alias_info[0] if alias_info else None

    def get_wildcard_info(self) -> List[WildcardInfo]:
        """Find wildcard (*) targets in the SELECT."""
        buff = []
        for seg in self.select_info.select_targets:
            if seg.get_child("wildcard_expression"):
                if "." in seg.raw:
                    # The wildcard specifies a target table.
                    table = seg.raw.rsplit(".", 1)[0]
                    buff.append(WildcardInfo(seg, [table]))
                else:
                    # The wildcard is unqualified (i.e. does not specify a
                    # table). This means to include all columns from all the
                    # tables in the query.
                    buff.append(
                        WildcardInfo(
                            seg,
                            [
                                alias_info.ref_str
                                for alias_info in self.select_info.table_aliases
                            ],
                        )
                    )
        return buff

    @staticmethod
    def _get_name_if_cte(
        select_statement: BaseSegment, ancestor_segment: BaseSegment
    ) -> Optional[str]:
        """Return name if CTE. If top-level, return None."""
        cte = None
        path_to = ancestor_segment.path_to(select_statement)
        for seg in path_to:
            if seg.is_type("common_table_expression"):
                cte = seg
                break
        select_name = cte.segments[0].raw if cte else None
        return select_name


class Rule_L043(BaseCrawler):
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

    def _handle_alias(self, alias_info, dialect, queries):
        select_info_target = SelectInfo.get(
            alias_info.table_expression, queries, dialect
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
        select_info_list: List[SelectInfo],
        dialect: Dialect,
        queries: Dict[str, List[SelectInfo]],
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
                                    queries[wildcard_table], dialect, queries
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
                    select_info_target = SelectInfo.get(
                        select_info.select_statement, queries, dialect
                    )
                    assert isinstance(select_info_target, list)
                    self._analyze_result_columns(
                        select_info_target,
                        dialect,
                        queries,
                    )

    def _eval(self, segment, **kwargs):
        """Outermost query should produce known number of columns."""
        if segment.is_type("statement"):
            dialect: Dialect = kwargs.get("dialect")
            queries = SelectInfo.gather(segment, dialect)

            # Begin analysis at the final, outer query (key=None).
            select_info = queries[None]
            try:
                return self._analyze_result_columns(select_info, dialect, queries)
            except RuleFailure:
                return LintResult(anchor=queries[None][0].select_info.select_statement)
        return None
