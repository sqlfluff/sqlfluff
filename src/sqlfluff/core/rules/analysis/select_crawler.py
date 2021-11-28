"""Tools for more complex analysis of SELECT statements."""
from collections import defaultdict
from typing import DefaultDict, Dict, Generator, List, NamedTuple, Optional, Union

from cached_property import cached_property

from sqlfluff.core.dialects.common import AliasInfo
from sqlfluff.core.dialects.base import Dialect
from sqlfluff.core.parser.segments.base import BaseSegment
from sqlfluff.core.rules.analysis.select import get_select_statement_info


class WildcardInfo(NamedTuple):
    """Structure returned by SelectCrawler.get_wildcard_info()."""

    segment: BaseSegment
    tables: List[str]


class SelectStatementInfo(NamedTuple):
    """Info about a select_statement."""

    cte: Optional[BaseSegment]

    @property
    def select_name(self):
        """If the select_statement is a CTE, what's its name?"""
        return self.cte.segments[0].raw if self.cte else None


class SelectCrawler:
    """Class for recursive dependency analysis related to SELECT statements.

    This class is a wrapper for select.get_select_statement_info(), but it adds
    recursive dependency walking.
    """

    @classmethod
    def gather(
        cls, segment: BaseSegment, dialect: Dialect
    ) -> Dict[Optional[str], List["SelectCrawler"]]:
        """Find top-level SELECTs and CTEs, return info."""
        queries: DefaultDict[Optional[str], List[SelectCrawler]] = defaultdict(list)
        cls._process_select_statements(segment, dialect, queries)
        return dict(queries)

    @classmethod
    def _process_select_statements(
        cls,
        segment: BaseSegment,
        dialect: Dialect,
        queries: DefaultDict[Optional[str], List["SelectCrawler"]],
    ):
        # We specify recurse_into=False because we only want top-level select
        # statements and CTEs. We'll deal with nested selects later as needed,
        # when processing their top-level parent.
        for select_statement in segment.recursive_crawl(
            "select_statement", recurse_into=False
        ):
            select_statement_info = cls._get_cte_info(select_statement, segment)
            if select_statement_info:
                queries[select_statement_info.select_name].append(
                    SelectCrawler(select_statement, dialect, select_statement_info.cte)
                )

    @classmethod
    def gather_nested_ctes(
        cls, segment: BaseSegment, dialect: Dialect
    ) -> Dict[Optional[str], List["SelectCrawler"]]:
        """Find nested CTEs."""
        queries: DefaultDict[Optional[str], List[SelectCrawler]] = defaultdict(list)
        cls._process_select_statements(segment, dialect, queries)
        for cte in segment.recursive_crawl(
            "common_table_expression", recurse_into=False
        ):
            cls._process_select_statements(cte, dialect, queries)
        return dict(queries)

    @classmethod
    def get(
        cls,
        segment: BaseSegment,
        queries: Dict[Optional[str], List["SelectCrawler"]],
        dialect: Dialect,
    ) -> Union[str, List["SelectCrawler"]]:
        """Find SELECTs, table refs, or value table function calls in segment.

        If we find a SELECT, return info list. Otherwise, return table name
        or function call string.
        """
        for o in cls.crawl(segment, queries, dialect, False):
            return o
        assert False, "Should be unreachable"  # pragma: no cover

    @classmethod
    def crawl(
        cls,
        segment: BaseSegment,
        queries: Dict[Optional[str], List["SelectCrawler"]],
        dialect: Dialect,
        recurse_into=True,
    ) -> Generator[Union[str, List["SelectCrawler"]], None, None]:
        """Find SELECTs, table refs, or value table function calls in segment.

        For each SELECT, yield a list of SelectCrawlers. As we find table
        references or function call strings, yield those.
        """
        buff = []
        for seg in segment.recursive_crawl(
            "table_reference", "select_statement", recurse_into=recurse_into
        ):
            if seg is segment:
                # If we are starting with a select_statement, recursive_crawl()
                # returns the statement itself. Skip that.
                continue

            if seg.is_type("table_reference"):
                if not seg.is_qualified() and seg.raw in queries:
                    # It's a CTE.
                    # :TRICKY: Pop the CTE from "queries" to help callers avoid
                    # infinite recursion. We could make this behavior optional
                    # someday, if necessary.
                    yield queries.pop(seg.raw)
                else:
                    # It's an external table.
                    yield seg.raw
            else:
                assert seg.is_type("select_statement")
                buff.append(SelectCrawler(seg, dialect))
        if not buff:
            # If we reach here, the SELECT may be querying from a value table
            # function, e.g. UNNEST(). For our purposes, this is basically the
            # same as an external table. Return the "table" part as a string.
            table_expr = segment.get_child("table_expression")
            if table_expr:
                yield table_expr.raw
        yield buff

    def __init__(self, select_statement, dialect, cte=None):
        self.select_statement = select_statement
        self.dialect = dialect
        self.cte = cte

    def __repr__(self):
        return f"<<SelectCrawler({self.select_statement.raw})>>"  # pragma: no cover

    @cached_property
    def select_info(self):
        """Returns SelectStatementColumnsAndTables on the SELECT."""
        result = get_select_statement_info(
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
                                if alias_info.aliased
                                else alias_info.from_expression_element.raw
                                for alias_info in self.select_info.table_aliases
                            ],
                        )
                    )
        return buff

    @staticmethod
    def _get_cte_info(
        select_statement: BaseSegment, ancestor_segment: BaseSegment
    ) -> Optional[SelectStatementInfo]:
        """Return name if CTE. If top-level, return None."""
        ctes = []
        path_to = ancestor_segment.path_to(select_statement)
        for seg in path_to:
            if seg.is_type("common_table_expression"):
                ctes.append(seg)
        if not ctes:
            return SelectStatementInfo(None)
        elif len(ctes) <= 1:
            return SelectStatementInfo(ctes[0])
        else:
            return None
