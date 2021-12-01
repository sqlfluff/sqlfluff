"""Tools for more complex analysis of SELECT statements."""
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Generator, List, NamedTuple, Optional, Union

from cached_property import cached_property

from sqlfluff.core.dialects.common import AliasInfo
from sqlfluff.core.dialects.base import Dialect
from sqlfluff.core.parser import BaseSegment
from sqlfluff.core.rules.analysis.select import get_select_statement_info


class QueryType(Enum):
    """Query type: Simple is just a query; WithCompound has CTE(s)."""

    Simple = 1
    WithCompound = 2


class WildcardInfo(NamedTuple):
    """Structure returned by SelectCrawler.get_wildcard_info()."""

    segment: BaseSegment
    tables: List[str]


@dataclass
class Selectable:
    """A "SELECT" query segment."""

    selectable: BaseSegment
    dialect: Dialect

    @cached_property
    def select_info(self):
        """Returns SelectStatementColumnsAndTables on the SELECT."""
        return get_select_statement_info(
            self.selectable, self.dialect, early_exit=False
        )

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
                                if alias_info.aliased
                                else alias_info.from_expression_element.raw
                                for alias_info in self.select_info.table_aliases
                            ],
                        )
                    )
        return buff

    def find_alias(self, table: str) -> Optional[AliasInfo]:
        """Find corresponding table_aliases entry (if any) matching "table"."""
        alias_info = [
            t
            for t in self.select_info.table_aliases
            if t.aliased and t.ref_str == table
        ]
        assert len(alias_info) <= 1
        return alias_info[0] if alias_info else None


@dataclass
class Query:
    """A main SELECT query plus possible CTEs."""

    query_type: QueryType
    dialect: Dialect
    selectables: List[Selectable] = field(default_factory=list)
    ctes: Dict[str, "Query"] = field(default_factory=dict)
    # Parent scope. This query can "see" CTEs defined by parents.
    parent: Optional["Query"] = field(default=None)

    def lookup_cte(self, name: str, pop: bool = True) -> Optional["Query"]:
        """Look up a CTE by name, in the current or any parent scope."""
        cte = self.ctes.get(name)
        if cte:
            if pop:
                del self.ctes[name]
            return cte
        if self.parent:
            return self.parent.lookup_cte(name, pop)
        else:
            return None

    def crawl_sources(
        self, segment: BaseSegment, recurse_into=True
    ) -> Generator[Union[str, "Query"], None, None]:
        """Find SELECTs, table refs, or value table function calls in segment.

        For each SELECT, yield a list of Query objects. As we find table
        references or function call strings, yield those.
        """
        found_nested_select = False
        for seg in segment.recursive_crawl(
            "table_reference",
            "set_expression",
            "select_statement",
            recurse_into=recurse_into,
        ):
            if seg is segment:
                # If we are starting with a select_statement, recursive_crawl()
                # returns the statement itself. Skip that.
                continue

            if seg.is_type("table_reference"):
                if not seg.is_qualified():
                    cte = self.lookup_cte(seg.raw, pop=False)
                    if cte:
                        # It's a CTE.
                        yield cte
                # It's an external table.
                yield seg.raw
            else:
                assert seg.is_type("set_expression", "select_statement")
                found_nested_select = True
                crawler = SelectCrawler(seg, self.dialect, self)
                yield crawler.query_tree
        if not found_nested_select:
            # If we reach here, the SELECT may be querying from a value table
            # function, e.g. UNNEST(). For our purposes, this is basically the
            # same as an external table. Return the "table" part as a string.
            table_expr = segment.get_child("table_expression")
            if table_expr:
                yield table_expr.raw


class SelectCrawler:
    """Class for recursive dependency analysis related to SELECT statements.

    This class is a wrapper for select.get_select_statement_info(), but it adds
    recursive dependency walking.
    """

    def __init__(
        self, segment: BaseSegment, dialect: Dialect, parent: Optional[Query] = None
    ):
        self.dialect: Dialect = dialect
        self.query_tree: Query = None

        queries: List[Query] = []
        pop_queries_for = []

        def append_query(query):
            if queries:
                query.parent = queries[-1]
            queries.append(query)
            pop_queries_for.append(path[-1])

        cte_name = None
        for event, path in SelectCrawler.visit_segments(segment):
            in_with = queries and queries[-1].query_type == QueryType.WithCompound
            if event == "start":
                if path[-1].is_type("set_expression", "select_statement"):
                    if not in_with:
                        if path[-1].is_type("select_statement"):
                            selectable = Selectable(path[-1], dialect)
                            if len(path) >= 2 and path[-2].is_type("set_expression"):
                                queries[-1].selectables.append(selectable)
                            else:
                                query = Query(QueryType.Simple, dialect, [selectable])
                                append_query(query)
                        else:
                            query = Query(QueryType.Simple, dialect)
                            append_query(query)
                        if cte_name:
                            queries[-1].ctes[cte_name] = query
                            cte_name = None
                    else:
                        if not cte_name:
                            if not any(
                                seg.is_type("from_expression_element") for seg in path
                            ):
                                if path[-1].is_type("select_statement"):
                                    queries[-1].selectables.append(
                                        Selectable(path[-1], dialect)
                                    )
                        else:
                            query = Query(QueryType.Simple, dialect)
                            if path[-1].is_type("select_statement"):
                                query.selectables.append(Selectable(path[-1], dialect))
                            queries[-1].ctes[cte_name] = query
                            cte_name = None
                            append_query(query)
                elif path[-1].is_type("with_compound_statement"):
                    query = Query(QueryType.WithCompound, dialect)
                    if cte_name:
                        queries[-1].ctes[cte_name] = query
                        cte_name = None
                    append_query(query)
                elif path[-1].is_type("common_table_expression"):
                    cte_name = path[-1].segments[0].raw
                if len(queries) == 1 and self.query_tree is None:
                    self.query_tree = queries[0]
                    self.query_tree.parent = parent
            elif event == "end":
                try:
                    idx = pop_queries_for.index(path[-1])
                    queries.pop()
                    del pop_queries_for[idx]
                except ValueError:
                    pass

    @classmethod
    def get(cls, query: Query, segment: BaseSegment) -> List[Union[str, "Query"]]:
        """Find SELECTs, table refs, or value table function calls in segment.

        If we find a SELECT, return info list. Otherwise, return table name
        or function call string.
        """
        return list(query.crawl_sources(segment, True))

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

    @classmethod
    def visit_segments(cls, seg, path=None):
        """Recursive crawl all segments."""
        if path is None:
            path = []
        path.append(seg)
        yield "start", path
        for seg in seg.segments:
            yield from cls.visit_segments(seg, path)
        yield "end", path
        path.pop()
