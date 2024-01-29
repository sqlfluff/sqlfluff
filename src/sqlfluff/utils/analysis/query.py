"""Tools for more complex analysis of SELECT statements."""

import logging
from dataclasses import dataclass, field
from enum import Enum
from functools import cached_property
from typing import (
    Dict,
    Generic,
    Iterator,
    List,
    NamedTuple,
    Optional,
    Type,
    TypeVar,
    Union,
    cast,
)

from sqlfluff.core.dialects.base import Dialect
from sqlfluff.core.dialects.common import AliasInfo
from sqlfluff.core.parser import BaseSegment
from sqlfluff.dialects.dialect_ansi import ObjectReferenceSegment
from sqlfluff.utils.analysis.select import (
    SelectStatementColumnsAndTables,
    get_select_statement_info,
)
from sqlfluff.utils.functional import Segments, sp

analysis_logger = logging.getLogger("sqlfluff.rules.analysis")


# Segment types which directly are or contain selectables.
SELECTABLE_TYPES = (
    "with_compound_statement",
    "set_expression",
    "select_statement",
)

# Segment types which are likely to contain a subselect.
SUBSELECT_TYPES = (
    "merge_statement",
    "update_statement",
    "delete_statement",
    # NOTE: Values clauses won't have sub selects, but it's
    # also harmless to look, and they may appear in similar
    # locations. We include them here because they come through
    # the same code paths - although are likely to return nothing.
    "values_clause",
)


class QueryType(Enum):
    """Query type: Simple is just a query; WithCompound has CTE(s)."""

    Simple = 1
    WithCompound = 2


class WildcardInfo(NamedTuple):
    """Structure returned by Selectable.get_wildcard_info()."""

    segment: BaseSegment
    tables: List[str]


@dataclass
class Selectable:
    """A "SELECT" query segment."""

    selectable: BaseSegment
    dialect: Dialect

    def as_str(self) -> str:
        """String representation for logging/testing."""
        return self.selectable.raw

    @cached_property
    def select_info(self) -> Optional[SelectStatementColumnsAndTables]:
        """Returns SelectStatementColumnsAndTables on the SELECT."""
        if self.selectable.is_type("select_statement"):
            return get_select_statement_info(
                self.selectable, self.dialect, early_exit=False
            )
        else:  # DML or values_clause
            # This is a bit dodgy, but a very useful abstraction. Here, we
            # interpret a DML or values_clause segment as if it were a SELECT.
            # Someday, we may need to tweak this, e.g. perhaps add a separate
            # QueryType for this (depending on the needs of the rules that use
            # it.
            #
            # For more info on the syntax and behavior of VALUES and its
            # similarity to a SELECT statement with literal values (no table
            # source), see the "Examples" section of the Postgres docs page:
            # (https://www.postgresql.org/docs/8.2/sql-values.html).
            values = Segments(self.selectable)
            alias_expression = values.children().first(sp.is_type("alias_expression"))
            name = alias_expression.children().first(
                sp.is_type("naked_identifier", "quoted_identifier")
            )
            alias_info = AliasInfo(
                name[0].raw if name else "",
                name[0] if name else None,
                bool(name),
                self.selectable,
                alias_expression[0] if alias_expression else None,
                None,
            )

            return SelectStatementColumnsAndTables(
                select_statement=self.selectable,
                table_aliases=[alias_info],
                standalone_aliases=[],
                reference_buffer=[],
                select_targets=[],
                col_aliases=[],
                using_cols=[],
            )

    def get_wildcard_info(self) -> List[WildcardInfo]:
        """Find wildcard (*) targets in the SELECT."""
        buff: List[WildcardInfo] = []
        # Some select-like statements don't have select_info
        # (e.g. test_exasol_invalid_foreign_key_from)
        if not self.select_info:  # pragma: no cover
            # TODO: Review whether to remove this.
            # Restructure of Exasol dialect means it no longer applies.
            return buff
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
                                (
                                    alias_info.ref_str
                                    if alias_info.aliased
                                    else alias_info.from_expression_element.raw
                                )
                                for alias_info in self.select_info.table_aliases
                                if alias_info.ref_str
                            ],
                        )
                    )
        return buff

    def find_alias(self, table: str) -> Optional[AliasInfo]:
        """Find corresponding table_aliases entry (if any) matching "table"."""
        alias_info = [
            t
            for t in (self.select_info.table_aliases if self.select_info else [])
            if t.aliased and t.ref_str == table
        ]
        assert len(alias_info) <= 1
        return alias_info[0] if alias_info else None


T = TypeVar("T", bound="Query")


@dataclass
class Query(Generic[T]):
    """A main SELECT query plus possible CTEs."""

    query_type: QueryType
    dialect: Dialect
    selectables: List[Selectable] = field(default_factory=list)
    ctes: Dict[str, T] = field(default_factory=dict)
    # Parent scope. This query can "see" CTEs defined by parents.
    parent: Optional[T] = field(default=None)
    # subqueries are subselects in either the SELECT or FROM clause.
    subqueries: List[T] = field(default_factory=list)
    cte_definition_segment: Optional[BaseSegment] = field(default=None)
    cte_name_segment: Optional[BaseSegment] = field(default=None)

    def __post_init__(self):
        # Once instantiated, set the `parent` attribute of any
        # subqueries and ctes. Some might already be set - but
        # we'll reset them anyway here.
        for subquery in self.subqueries:
            subquery.parent = self
        # NOTE: In normal operation, CTEs are typically set after
        # instantiation, and so for this method there aren't normally
        # any present. It is included here for completeness but not
        # covered in the test suite.
        # See `.from_segment()` for the way `parent` is set for CTEs.
        for cte in self.ctes.values():  # pragma: no cover
            cte.parent = self

    @property
    def children(self: T) -> List[T]:
        """Children could be CTEs, subselects or Others."""
        return list(self.ctes.values()) + self.subqueries

    def as_dict(self: T) -> Dict:
        """Dict representation for logging/testing."""
        result: Dict[str, Union[str, List[str], Dict, List[Dict]]] = {}
        if self.query_type != QueryType.Simple:
            result["query_type"] = self.query_type.name
        if self.selectables:
            result["selectables"] = [s.as_str() for s in self.selectables]
        if self.ctes:
            result["ctes"] = {k: v.as_dict() for k, v in self.ctes.items()}
        if self.subqueries:
            result["subqueries"] = [q.as_dict() for q in self.subqueries]
        return result

    def lookup_cte(self: T, name: str, pop: bool = True) -> Optional[T]:
        """Look up a CTE by name, in the current or any parent scope."""
        cte = self.ctes.get(name.upper())
        if cte:
            if pop:
                del self.ctes[name.upper()]
            return cte
        if self.parent:
            return self.parent.lookup_cte(name, pop)
        else:
            return None

    def crawl_sources(
        self: T, segment: BaseSegment, recurse_into=True, pop=False, lookup_cte=True
    ) -> Iterator[Union[str, T]]:
        """Find SELECTs, table refs, or value table function calls in segment.

        For each SELECT, yield a list of Query objects. As we find table
        references or function call strings, yield those.
        """
        found_nested_select = False
        for seg in segment.recursive_crawl(
            "table_reference",
            "set_expression",
            "select_statement",
            "values_clause",
            recurse_into=False,
            allow_self=False,
        ):
            # Crawl efficiently, don't recurse here. We do that later.
            # What do we have?
            # 1. If it's a table reference, work out whether it's to a CTE
            #    or to an external table.
            if seg.is_type("table_reference"):
                _seg = cast(ObjectReferenceSegment, seg)
                if not _seg.is_qualified() and lookup_cte:
                    cte = self.lookup_cte(_seg.raw, pop=pop)
                    if cte:
                        # It's a CTE.
                        yield cte
                # It's an external table reference.
                yield _seg.raw
            # 2. If it's some kind of more complex expression which is still
            #    valid in this position, generate an appropriate sub-select.
            else:
                assert seg.is_type(
                    "set_expression", "select_statement", "values_clause"
                )
                found_nested_select = True
                # Generate a subquery, referencing the current query
                # as the parent.
                yield self.__class__.from_segment(seg, self.dialect, parent=self)
        if not found_nested_select:
            # If we reach here, the SELECT may be querying from a value table
            # function, e.g. UNNEST(). For our purposes, this is basically the
            # same as an external table. Return the "table" part as a string.
            table_expr = segment.get_child("table_expression")
            if table_expr:
                yield table_expr.raw

    @classmethod
    def _extract_subqueries(
        cls: Type[T], selectable: Selectable, dialect: Dialect
    ) -> Iterator[T]:
        """Given a Selectable, extract subqueries."""
        assert selectable.selectable.is_type(
            *SELECTABLE_TYPES,
            *SUBSELECT_TYPES,
        ), f"Found unexpected {selectable.selectable}"

        # For MERGE, UPDATE & DELETE, we should expect to find a sub select.
        for subselect in selectable.selectable.recursive_crawl(
            *SELECTABLE_TYPES,
            recurse_into=False,
            allow_self=False,
        ):
            # NOTE: We don't need to set the parent here, because it will
            # be set when attached to the parent later.
            yield cls.from_segment(subselect, dialect=dialect)

    @classmethod
    def from_root(cls: Type[T], root_segment, dialect: Dialect) -> T:
        """Given a root segment, find the first appropriate selectable and analyse."""
        selectable_segment = next(
            # Could be a Selectable or a MERGE
            root_segment.recursive_crawl(*SELECTABLE_TYPES, "merge_statement"),
            None,
        )
        assert selectable_segment, f"No selectable found in {root_segment.raw!r}."
        return cls.from_segment(selectable_segment, dialect=dialect)

    @classmethod
    def from_segment(
        cls: Type[T],
        segment: BaseSegment,
        dialect: Dialect,
        parent: Optional[T] = None,
    ) -> T:
        """Recursively generate a query from an appropriate segment."""
        assert segment.is_type(
            *SELECTABLE_TYPES, *SUBSELECT_TYPES
        ), f"Invalid segment for `from_segment`: {segment}"

        selectables = []
        subqueries = []
        cte_defs = []
        query_type = QueryType.Simple

        if segment.is_type("select_statement", *SUBSELECT_TYPES):
            # It's a select. Instantiate a Query.
            selectables = [Selectable(segment, dialect=dialect)]
        elif segment.is_type("set_expression"):
            # It's a set expression. There may be multiple selectables.
            for _seg in segment.get_children("select_statement"):
                selectables.append(Selectable(_seg, dialect=dialect))
        else:
            # Otherwise it's a WITH statement.
            assert segment.is_type("with_compound_statement")
            query_type = QueryType.WithCompound
            for _seg in segment.recursive_crawl(
                # NOTE: We don't _specify_ set expressions here, because
                # all set expressions are made of selects, and we
                # want to look straight through to those child
                # expressions.
                "select_statement",
                recurse_into=False,
                no_recursive_seg_type="common_table_expression",
            ):
                selectables.append(Selectable(_seg, dialect=dialect))

            # We also need to handle CTEs
            for _seg in segment.recursive_crawl(
                "common_table_expression",
                recurse_into=False,
                # Don't recurse into any other WITH statements.
                no_recursive_seg_type="with_compound_statement",
            ):
                # Just store the segments for now.
                cte_defs.append(_seg)

        # Extract subqueries from any selectables.
        for selectable in selectables:
            # NOTE: If any VALUES clauses are present, they pass through here
            # safely without Exception. They won't yield any subqueries.
            subqueries += list(cls._extract_subqueries(selectable, dialect))

        # Instantiate the query
        outer_query = cls(
            query_type,
            dialect,
            selectables,
            parent=parent,
            subqueries=subqueries,
        )

        # If we don't have any CTEs, we can stop now.
        if not cte_defs:
            return outer_query

        # Otherwise build up the CTE map.
        ctes = {}
        for cte in cte_defs:
            # NOTE: This feels a little risky to just assume the first segment
            # is the name, but it's the same functionality we've run with for
            # a while.
            name_seg = cte.segments[0]
            name = name_seg.raw_upper
            # Get the query out of it, just stop on the first one we find.
            try:
                inner_qry = next(
                    cte.recursive_crawl(
                        *SELECTABLE_TYPES,
                        "values_clause",
                        # Very rarely, we might find things like update
                        # clauses in here, handle them accordingly.
                        *SUBSELECT_TYPES,
                    ),
                )
            # If this fails it's because we didn't find anything "selectable"
            # in the CTE. Flag this up, but then carry on. It's likely something
            # strange (w.g. a Clickhouse WITH clause setting a with).
            except StopIteration:  # pragma: no cover
                # Log it as an issue, but otherwise skip this one.
                analysis_logger.info(f"Skipping unexpected CTE structure: {cte.raw!r}")
                continue
            qry = cls.from_segment(inner_qry, dialect=dialect, parent=outer_query)
            assert qry
            # Populate the CTE specific args.
            qry.cte_definition_segment = cte
            qry.cte_name_segment = name_seg
            # File it in the dictionary.
            ctes[name] = qry

        # Set the CTEs attribute on the outer.
        # NOTE: Because we're setting this after instantiation, it's important
        # that we've already set the `parent` value of the cte queries.
        outer_query.ctes = ctes
        return outer_query
