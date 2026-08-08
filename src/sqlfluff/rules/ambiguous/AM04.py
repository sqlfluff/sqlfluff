"""Implementation of Rule AM04."""

from typing import Optional, Union

from sqlfluff.core.parser import BaseSegment
from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.utils.analysis.query import Query

_START_TYPES = ["select_statement", "set_expression", "with_compound_statement"]
SourceTarget = Union[str, Query]


class RuleFailure(Exception):
    """Exception class for reporting lint failure inside deeply nested code."""

    def __init__(self, anchor: BaseSegment):
        self.anchor: BaseSegment = anchor


class Rule_AM04(BaseRule):
    """Query produces an unknown number of result columns.

    **Anti-pattern**

    Querying all columns using ``*`` produces a query result where the number
    or ordering of columns changes if the upstream table's schema changes.
    This should generally be avoided because it can cause slow performance,
    cause important schema changes to go undetected, or break production code.
    For example:

    * If a query does ``SELECT t.*`` and is expected to return columns ``a``, ``b``,
      and ``c``, the actual columns returned will be wrong/different if columns
      are added to or deleted from the input table.
    * ``UNION`` and ``DIFFERENCE`` clauses require the inputs have the same number
      of columns (and compatible types).
    * ``JOIN`` queries may break due to new column name conflicts, e.g. the
      query references a column ``c`` which initially existed in only one input
      table but a column of the same name is added to another table.
    * ``CREATE TABLE (<<column schema>>) AS SELECT *``


    .. code-block:: sql

        WITH cte AS (
            SELECT * FROM foo
        )

        SELECT * FROM cte
        UNION
        SELECT a, b FROM t

    **Best practice**

    Somewhere along the "path" to the source data, specify columns explicitly.

    .. code-block:: sql

        WITH cte AS (
            SELECT * FROM foo
        )

        SELECT a, b FROM cte
        UNION
        SELECT a, b FROM t

    """

    name = "ambiguous.column_count"
    aliases = ("L044",)
    groups: tuple[str, ...] = ("all", "ambiguous")
    config_keywords = ["require_explicit_source_projection"]
    # Only evaluate the outermost query.
    crawl_behaviour = SegmentSeekerCrawler(set(_START_TYPES), allow_recurse=False)

    def _analyze_source_ctes(self, query: Query) -> None:
        """Analyze CTEs recursively when explicit source projection is required."""
        for child in query.children:
            if child.cte_definition_segment:
                self._analyze_result_columns(child, pop=False)
            self._analyze_source_ctes(child)

    def _get_source_target(
        self,
        query: Query,
        source_segment: BaseSegment,
        pop: bool = True,
    ) -> Optional[SourceTarget]:
        """Resolve the direct source query or table for a FROM/JOIN element."""
        direct_query_segment = next(
            source_segment.recursive_crawl(*_START_TYPES, allow_self=False),
            None,
        )
        if direct_query_segment:
            return Query.from_segment(direct_query_segment, query.dialect, parent=query)

        sources = list(query.crawl_sources(source_segment, True, pop=pop))
        query_source = next(
            (source for source in sources if isinstance(source, Query)),
            None,
        )
        if query_source is not None:
            return query_source
        if sources:
            return sources[0]
        return None

    def _handle_alias(
        self,
        selectable,
        alias_info,
        query,
        pop: bool = True,
        visited: Optional[set[int]] = None,
    ) -> None:
        select_info_target = self._get_source_target(
            query,
            alias_info.from_expression_element,
            pop=pop,
        )
        assert select_info_target is not None
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
            self._analyze_result_columns(select_info_target, pop=pop, visited=visited)

    def _analyze_result_columns(
        self,
        query: Query,
        pop: bool = True,
        visited: Optional[set[int]] = None,
    ) -> None:
        """Given info on a list of SELECTs, determine whether to warn."""
        # Recursively walk from the given query (select_info_list) to any
        # wildcard columns in the select targets. If every wildcard eventually
        # resolves to a query without wildcards, all is well. Otherwise, warn.
        if not query.selectables:
            return None  # pragma: no cover
        visited = visited or set()
        if id(query) in visited:
            raise RuleFailure(query.selectables[0].selectable)
        visited.add(id(query))
        for selectable in query.selectables:
            self.logger.debug(f"Analyzing query: {selectable.selectable.raw}")
            for wildcard in selectable.get_wildcard_info():
                if wildcard.tables:
                    for wildcard_table in wildcard.tables:
                        self.logger.debug(
                            f"Wildcard: {wildcard.segment.raw} has target "
                            f"{wildcard_table}"
                        )
                        # Is it an alias?
                        alias_info = selectable.find_alias(wildcard_table)
                        if alias_info:
                            # Found the alias matching the wildcard. Recurse,
                            # analyzing the query associated with that alias.
                            self._handle_alias(
                                selectable,
                                alias_info,
                                query,
                                pop=pop,
                                visited=visited,
                            )
                        else:
                            # Not an alias. Is it a CTE?
                            cte = query.lookup_cte(wildcard_table, pop=pop)
                            if cte:
                                # Wildcard refers to a CTE. Analyze it.
                                self._analyze_result_columns(
                                    cte, pop=pop, visited=visited
                                )
                            else:
                                # Not CTE, not table alias. Presumably an
                                # external table. Warn.
                                self.logger.debug(
                                    f"Query target {wildcard_table} is external. "
                                    "Generating warning."
                                )
                                raise RuleFailure(selectable.selectable)
                else:
                    # No table was specified with the wildcard. Assume we're
                    # querying from an anonymous nested source in FROM/JOIN.
                    anonymous_sources = [
                        alias_info.from_expression_element
                        for alias_info in (
                            selectable.select_info.table_aliases
                            if selectable.select_info
                            else []
                        )
                        if not alias_info.ref_str
                    ]
                    if anonymous_sources:
                        for source_segment in anonymous_sources:
                            source_target = self._get_source_target(
                                query, source_segment, pop=pop
                            )
                            if isinstance(source_target, Query):
                                self._analyze_result_columns(
                                    source_target, pop=pop, visited=visited
                                )
                                continue
                            if isinstance(source_target, str):
                                self.logger.debug(
                                    f"Query target {source_target} is external. "
                                    "Generating warning."
                                )
                            self.logger.debug(
                                f'Query target "{selectable.selectable.raw}" has no '
                                "targets. Generating warning."
                            )
                            raise RuleFailure(selectable.selectable)
                        return None
                    self.logger.debug(
                        f'Query target "{selectable.selectable.raw}" has no '
                        "targets. Generating warning."
                    )
                    raise RuleFailure(selectable.selectable)

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Outermost query should produce known number of columns."""
        self.require_explicit_source_projection: bool
        query: Query = Query.from_segment(context.segment, context.dialect)

        try:
            if self.require_explicit_source_projection:
                self._analyze_source_ctes(query)
            # Begin analysis at the outer query.
            self._analyze_result_columns(query)
            return None
        except RuleFailure as e:
            return LintResult(anchor=e.anchor)
