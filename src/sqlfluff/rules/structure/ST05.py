"""Implementation of Rule ST05."""

from collections.abc import Iterator
from functools import partial
from itertools import chain
from typing import NamedTuple, Optional, TypeVar, cast

from sqlfluff.core.dialects.base import Dialect
from sqlfluff.core.dialects.common import (
    AliasInfo,
    ObjectReferenceLevel,
    extract_possible_references,
    iter_raw_references,
)
from sqlfluff.core.parser import (
    BaseSegment,
    CodeSegment,
    KeywordSegment,
    NewlineSegment,
    SymbolSegment,
    WhitespaceSegment,
)
from sqlfluff.core.rules import (
    BaseRule,
    EvalResultType,
    LintFix,
    LintResult,
    RuleContext,
)
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.dialects.dialect_ansi import (
    CTEDefinitionSegment,
    TableExpressionSegment,
    TableReferenceSegment,
    WithCompoundStatementSegment,
)
from sqlfluff.utils.analysis.query import Query, Selectable
from sqlfluff.utils.analysis.select import get_select_statement_info
from sqlfluff.utils.functional import FunctionalContext, Segments
from sqlfluff.utils.functional.segment_predicates import (
    is_keyword,
    is_type,
    is_whitespace,
)

_SELECT_TYPES = [
    "with_compound_statement",
    "set_expression",
    "select_statement",
]


class _NestedSubQuerySummary(NamedTuple):
    query: Query
    selectable: Selectable
    table_alias: AliasInfo
    select_source_names: set[str]


_NormalizedTableReference = tuple[BaseSegment, str]


class _VisibleTableReferenceIndex(NamedTuple):
    """Cached table references grouped by their top-level visibility scope."""

    ctes: tuple[CTEDefinitionSegment, ...]
    cte_references: tuple[tuple[_NormalizedTableReference, ...], ...]
    root_references: tuple[_NormalizedTableReference, ...]


class Rule_ST05(BaseRule):
    """Join/From clauses should not contain subqueries. Use CTEs instead.

    By default this rule is configured to allow subqueries within ``FROM``
    clauses but not within ``JOIN`` clauses. If you prefer a stricter lint
    then this is configurable.

    .. note::
       Some dialects don't allow CTEs, and for those dialects
       this rule makes no sense and should be disabled.

    **Anti-pattern**

    .. code-block:: sql

        select
            a.x, a.y, b.z
        from a
        join (
            select x, z from b
        ) using(x)


    **Best practice**

    .. code-block:: sql

        with c as (
            select x, z from b
        )
        select
            a.x, a.y, c.z
        from a
        join c using(x)

    """

    name = "structure.subquery"
    aliases = ("L042",)
    groups = ("all", "structure")
    config_keywords = ["forbid_subquery_in"]
    crawl_behaviour = SegmentSeekerCrawler(set(_SELECT_TYPES))

    _config_mapping = {
        "join": ["join_clause"],
        "from": ["from_expression_element"],
        "both": ["join_clause", "from_expression_element"],
    }
    is_fix_compatible = True

    # These are dialects that support WITH ... INSERT ... SELECT instead of
    # INSERT ... WITH ... SELECT
    # NOTE: this may be incomplete
    # NOTE: postgres supports both ways, so I've not included it here.
    _with_before_insert = {"tsql"}

    def _eval(self, context: RuleContext) -> EvalResultType:
        """Join/From clauses should not contain subqueries. Use CTEs instead."""
        self.forbid_subquery_in: str
        functional_context = FunctionalContext(context)
        segment = functional_context.segment
        parent_stack = functional_context.parent_stack
        is_select = segment.all(is_type(*_SELECT_TYPES))
        is_select_child = parent_stack.any(is_type(*_SELECT_TYPES))
        insert_parent = parent_stack.last(is_type("insert_statement"))
        if not is_select or is_select_child:
            # Nothing to do.
            return None

        query: Query = Query.from_segment(context.segment, context.dialect)

        is_with = segment.all(is_type("with_compound_statement"))
        # TODO: consider if we can fix recursive CTEs
        is_recursive = is_with and len(segment.children(is_keyword("recursive"))) > 0
        case_preference = _get_case_preference(segment)
        output_select = segment
        if is_with:
            output_select = segment.children(
                is_type(
                    "set_expression",
                    "select_statement",
                    "insert_statement",
                )
            )
        elif insert_parent and context.dialect.name in self._with_before_insert:
            # Here we select the parent `insert_statement` because it should be where
            # we place the new CTE.
            output_select = insert_parent
            segment = insert_parent

        # generate an instance which will track and shape our output CTE
        ctes = _CTEBuilder()
        # Init the output/final select & populate existing CTEs.
        # For WITH compound statements, collect all CTEs in document order,
        # including expression CTEs (e.g. ClickHouse ``expr AS alias``) that
        # are not captured by query.ctes (which only handles selectable CTEs).
        # For non-WITH statements (select_statement, set_expression), query.ctes
        # is always empty because Query.from_segment only populates ctes for
        # with_compound_statement segments, so there is nothing to pre-populate.
        if is_with:
            for cte_seg in context.segment.recursive_crawl(
                "common_table_expression",
                recurse_into=False,
                no_recursive_seg_type="with_compound_statement",
            ):
                ctes.insert_cte(cast(CTEDefinitionSegment, cte_seg))

        # Issue 3617: In T-SQL (and possibly other dialects) the automated fix
        # leaves parentheses in a location that causes a syntax error. This is an
        # unusual corner case. For simplicity, we still generate the lint warning
        # but don't try to generate a fix. Someone could look at this later (a
        # correct fix would involve removing the parentheses.)
        bracketed_ctas = [seg.type for seg in parent_stack[-2:]] == [
            "create_table_statement",
            "bracketed",
        ]

        # If there are offending elements calculate fixes
        clone_map = SegmentCloneMap(segment[0])
        results = self._lint_query(
            dialect=context.dialect,
            query=query,
            ctes=ctes,
            case_preference=case_preference,
            clone_map=clone_map,
            root_segment=context.segment,
        )

        results_list: list[tuple[LintResult, BaseSegment, str, BaseSegment, bool]] = []
        for result in results:
            (
                lint_result,
                from_expression,
                alias_name,
                subquery_parent,
                is_fixable,
            ) = result
            assert any(
                from_expression is seg for seg in subquery_parent.recursive_crawl_all()
            )
            results_list.append(result)
            if not is_fixable:
                continue
            this_seg_clone = clone_map[from_expression]
            new_table_ref = _create_table_ref(alias_name, context.dialect)
            # Add positions to the new table reference, other rules may need a position
            # but the clone is not a typical "fix".
            assert this_seg_clone.pos_marker
            this_seg_clone.segments = this_seg_clone._position_segments(
                (new_table_ref,), this_seg_clone.pos_marker
            )
            ctes.replace_with_clone(subquery_parent, clone_map)

        for (
            lint_result,
            from_expression,
            alias_name,
            subquery_parent,
            is_fixable,
        ) in results_list:
            if bracketed_ctas or is_recursive or not is_fixable:
                continue
            # Compute fix.
            output_select_clone = clone_map[output_select[0]]
            fixes = ctes.ensure_space_after_from(
                output_select[0], output_select_clone, subquery_parent
            )
            new_select = ctes.compose_select(
                output_select_clone, case_preference=case_preference
            )
            lint_result.fixes = [
                LintFix.replace(
                    segment[0],
                    edit_segments=[new_select],
                )
            ]
            lint_result.fixes += fixes
        return [lint_result[0] for lint_result in results_list]

    def _nested_subqueries(
        self, query: Query, dialect: Dialect
    ) -> Iterator[_NestedSubQuerySummary]:
        parent_types = self._config_mapping[self.forbid_subquery_in]
        for i, q in enumerate([query] + list(query.ctes.values())):
            for selectable in q.selectables:
                if not selectable.select_info:
                    continue  # pragma: no cover
                select_source_names = set()
                for a in selectable.select_info.table_aliases:
                    # For each table in FROM, return table name and any alias.
                    if a.ref_str:
                        select_source_names.add(a.ref_str)
                    if a.object_reference:
                        select_source_names.add(a.object_reference.raw)
                for table_alias in selectable.select_info.table_aliases:
                    try:
                        query = Query.from_root(
                            table_alias.from_expression_element, dialect
                        )
                    except AssertionError:
                        # Couldn't find a selectable, carry on.
                        continue

                    path_to = selectable.selectable.path_to(
                        table_alias.from_expression_element
                    )
                    if not (
                        # The from_expression_element
                        table_alias.from_expression_element.is_type(*parent_types)
                        # Or any of it's parents up to the selectable
                        or any(ps.segment.is_type(*parent_types) for ps in path_to)
                    ):
                        continue
                    # A set expression has one selectable per branch.
                    if any(
                        _is_correlated_subquery(
                            Segments(selectable_.selectable),
                            select_source_names,
                            dialect,
                        )
                        for selectable_ in query.selectables
                    ):
                        continue
                    yield _NestedSubQuerySummary(
                        q, selectable, table_alias, select_source_names
                    )
                    # Recursively find nested queries in CTEs
                    if i > 0:
                        yield from self._nested_subqueries(query, dialect)

    def _lint_query(
        self,
        dialect: Dialect,
        query: Query,
        ctes: "_CTEBuilder",
        case_preference: str,
        clone_map,
        root_segment: BaseSegment,
    ) -> Iterator[tuple[LintResult, BaseSegment, str, BaseSegment, bool]]:
        """Given the root query, compute lint warnings."""
        nsq: _NestedSubQuerySummary
        for nsq in self._nested_subqueries(query, dialect):
            # 'anchor' is the TableExpressionSegment we fix/replace w/CTE name.
            anchor = nsq.table_alias.from_expression_element.segments[0]

            # if the subquery is table_expression, get the bracketed child instead.
            if anchor.is_type("table_expression"):
                bracket_anchor = anchor.get_child("bracketed")
                # if the table_expression isn't bracketed, assume it isn't a subquery.
                if not bracket_anchor:
                    continue
            else:
                bracket_anchor = anchor

            # we can't create a CTE from a nested subquery here, ignore it.
            structurally_fixable = bracket_anchor.is_type(
                "bracketed"
            ) and not bracket_anchor.get_child("table_expression")
            visible_table_names = (
                ctes.list_visible_table_names(
                    parent_selectable=nsq.selectable.selectable,
                    extracted_subquery=bracket_anchor,
                    root_segment=root_segment,
                    dialect_name=dialect.name,
                )
                if structurally_fixable
                else set()
            )
            alias_name, _ = ctes.create_cte_alias(
                nsq.table_alias,
                dialect=dialect,
                reserved_names=visible_table_names,
            )
            # If we have duplicate CTE names just don't fix anything.
            # Return the lint warnings anyway.
            is_fixable = (
                structurally_fixable
                and alias_name not in ctes.list_used_names()
                and _normalize_generated_identifier(alias_name, dialect)
                not in visible_table_names
            )
            if is_fixable:
                new_cte = _create_cte_seg(  # 'prep_1 as (select ...)'
                    alias_name=alias_name,
                    subquery=clone_map[bracket_anchor],
                    case_preference=case_preference,
                    dialect=dialect,
                )
                ctes.insert_cte(new_cte)

            # Grab the first keyword or symbol in the subquery to
            # use as the anchor. This makes the lint warning less
            # likely to be filtered out if a bit of the subquery
            # happens to be templated.
            anchor = next(anchor.recursive_crawl("keyword", "symbol"))
            res = LintResult(
                anchor=anchor,
                description=f"{nsq.selectable.selectable.type} clauses "
                "should not contain subqueries. Use CTEs instead",
                fixes=[],
            )
            yield (
                res,
                # FromExpressionElementSegment, parent of original "anchor" segment
                nsq.table_alias.from_expression_element,
                alias_name,  # Name of CTE we're creating from the nested query
                # Query with the subquery: 'select a from (select x from b)'
                nsq.selectable.selectable,
                is_fixable,
            )


def _get_first_select_statement_descendant(
    segment: BaseSegment,
) -> Optional[BaseSegment]:
    """Find first SELECT statement segment (if any) in descendants of 'segment'."""
    for select_statement in segment.recursive_crawl(
        "select_statement", recurse_into=False
    ):
        # We only want the first one.
        return select_statement
    return None  # pragma: no cover


def _is_correlated_subquery(
    nested_select: Segments, select_source_names: set[str], dialect: Dialect
) -> bool:
    """Given nested select and the sources of its parent, determine if correlated.

    https://en.wikipedia.org/wiki/Correlated_subquery
    """
    select_statement = _get_first_select_statement_descendant(nested_select[0])
    if not select_statement:
        return False  # pragma: no cover
    nested_select_info = get_select_statement_info(select_statement, dialect)
    if nested_select_info:
        for r in nested_select_info.reference_buffer:
            for tr in extract_possible_references(
                r, level=ObjectReferenceLevel.TABLE, dialect_name=dialect.name
            ):
                # Check for correlated subquery, as indicated by use of a
                # parent reference.
                if tr.part in select_source_names:
                    return True
    return False


class _CTEBuilder:
    """Gather CTE parts, maintain order and track naming/aliasing."""

    def __init__(self) -> None:
        self.ctes: list[CTEDefinitionSegment] = []
        self.name_idx = 0
        self._visible_table_reference_indexes: dict[
            tuple[int, str], _VisibleTableReferenceIndex
        ] = {}

    def list_used_names(self) -> list[str]:
        """Check CTEs and return used aliases."""
        used_names: list[str] = []
        for cte in self.ctes:
            id_seg = cte.get_identifier()
            cte_name = id_seg.raw
            if id_seg.is_type("quoted_identifier"):
                cte_name = cte_name[1:-1]

            used_names.append(cte_name)
        return used_names

    def insert_cte(self, cte: CTEDefinitionSegment) -> None:
        """Add a new CTE to the list as late as possible but before all its parents."""
        # This should still have the position markers of its true position
        inbound_subquery = (
            Segments(cte).children().last(lambda seg: bool(seg.pos_marker))
        )
        insert_position = self._insertion_position(inbound_subquery)

        self.ctes.insert(insert_position, cte)

    def _insertion_position(self, inbound_subquery: Segments) -> int:
        """Return where a CTE must be inserted to precede its consumer."""
        return next(
            (
                i
                for i, el in enumerate(self.ctes)
                if _is_child(Segments(el).children().last(), inbound_subquery)
            ),
            len(self.ctes),
        )

    def list_visible_table_names(
        self,
        parent_selectable: BaseSegment,
        extracted_subquery: BaseSegment,
        root_segment: BaseSegment,
        dialect_name: str,
    ) -> set[str]:
        """Return table names that a generated CTE could capture."""
        reference_index = self._get_visible_table_reference_index(
            root_segment, dialect_name
        )
        insert_position = next(
            (
                i
                for i, cte in enumerate(reference_index.ctes)
                if _is_child(
                    Segments(cte).children().last(), Segments(parent_selectable)
                )
            ),
            len(reference_index.ctes),
        )
        # SQLite permits forward references to later CTEs, so adding a CTE can
        # also capture a physical-table reference in an earlier CTE body.
        cte_references = (
            reference_index.cte_references
            if dialect_name == "sqlite"
            else reference_index.cte_references[insert_position:]
        )
        table_references = chain.from_iterable(
            (*cte_references, reference_index.root_references)
        )
        return {
            normalized_reference
            for table_reference, normalized_reference in table_references
            if not _is_child(Segments(extracted_subquery), Segments(table_reference))
        }

    def _get_visible_table_reference_index(
        self, root_segment: BaseSegment, dialect_name: str
    ) -> _VisibleTableReferenceIndex:
        """Return a cached reference index for one parsed statement."""
        cache_key = (id(root_segment), dialect_name)
        cached_index = self._visible_table_reference_indexes.get(cache_key)
        if cached_index is not None:
            return cached_index

        # The parsed statement is immutable during this rule evaluation. New
        # generated CTEs reuse subqueries already present in this tree, so their
        # references are already represented by this index.
        ctes = tuple(
            cast(CTEDefinitionSegment, child)
            for child in root_segment.segments
            if child.is_type("common_table_expression")
        )
        existing_cte_names = {
            identifier.raw_normalized(casefold=True)
            for cte in ctes
            if (identifier := cte.get_identifier())
        }

        def normalized_references(
            segment: BaseSegment,
        ) -> Iterator[_NormalizedTableReference]:
            for table_reference in self._iter_unshadowed_table_references(
                segment, existing_cte_names, dialect_name
            ):
                normalized_reference = self._normalize_table_reference(
                    table_reference, dialect_name
                )
                if normalized_reference:
                    yield table_reference, normalized_reference

        reference_index = _VisibleTableReferenceIndex(
            ctes=ctes,
            cte_references=tuple(tuple(normalized_references(cte)) for cte in ctes),
            root_references=tuple(
                reference
                for child in root_segment.segments
                if not child.is_type("common_table_expression")
                for reference in normalized_references(child)
            ),
        )
        self._visible_table_reference_indexes[cache_key] = reference_index
        return reference_index

    @classmethod
    def _iter_unshadowed_table_references(
        cls,
        segment: BaseSegment,
        scoped_cte_names: set[str],
        dialect_name: str,
    ) -> Iterator[BaseSegment]:
        """Yield references that are not resolved by a nested CTE scope."""
        if segment.is_type("with_compound_statement"):
            ctes = [
                cast(CTEDefinitionSegment, cte)
                for cte in segment.segments
                if cte.is_type("common_table_expression")
            ]
            if dialect_name == "sqlite":
                # SQLite allows CTE bodies to refer to later CTE declarations.
                local_cte_names = scoped_cte_names | {
                    identifier.raw_normalized(casefold=True)
                    for cte in ctes
                    if (identifier := cte.get_identifier())
                }
                for child in segment.segments:
                    yield from cls._iter_unshadowed_table_references(
                        child, local_cte_names, dialect_name
                    )
                return

            # Other supported dialects expose CTEs in declaration order. A
            # recursive CTE can also see its own name while its body is parsed.
            visible_cte_names = set(scoped_cte_names)
            is_recursive = any(
                child.is_type("keyword") and child.raw_upper == "RECURSIVE"
                for child in segment.segments
            )
            for child in segment.segments:
                if child.is_type("common_table_expression"):
                    cte = cast(CTEDefinitionSegment, child)
                    identifier = cte.get_identifier()
                    cte_name = (
                        identifier.raw_normalized(casefold=True) if identifier else None
                    )
                    child_scope = visible_cte_names
                    if is_recursive and cte_name:
                        child_scope = visible_cte_names | {cte_name}
                    yield from cls._iter_unshadowed_table_references(
                        child, child_scope, dialect_name
                    )
                    if cte_name:
                        visible_cte_names.add(cte_name)
                else:
                    yield from cls._iter_unshadowed_table_references(
                        child, visible_cte_names, dialect_name
                    )
            return

        if segment.is_type("table_reference"):
            normalized_reference = cls._normalize_table_reference(segment, dialect_name)
            if (
                normalized_reference is None
                or normalized_reference not in scoped_cte_names
            ):
                yield segment
            return
        for child in segment.segments:
            yield from cls._iter_unshadowed_table_references(
                child, scoped_cte_names, dialect_name
            )

    @staticmethod
    def _normalize_table_reference(
        table_reference: BaseSegment, dialect_name: str
    ) -> Optional[str]:
        """Normalize an unqualified table reference using dialect case rules."""
        reference_parts = list(
            iter_raw_references(table_reference, dialect_name=dialect_name)
        )
        if len(reference_parts) != 1:
            # A generated unqualified CTE name cannot capture a qualified
            # reference such as schema.table.
            return None
        return "".join(
            segment.raw_normalized(casefold=True)
            for segment in reference_parts[0].segments
        )

    def create_cte_alias(
        self,
        alias: Optional[AliasInfo],
        dialect: Dialect,
        reserved_names: set[str] | None = None,
    ) -> tuple[str, bool]:
        """Find or create the name for the next CTE."""
        if alias and alias.aliased and alias.ref_str:
            # If we know the name use it
            return alias.ref_str, False

        self.name_idx = self.name_idx + 1
        name = f"prep_{self.name_idx}"
        if name in self.list_used_names() or _normalize_generated_identifier(
            name, dialect
        ) in (reserved_names or set()):
            # corner case where prep_x exists in origin query
            return self.create_cte_alias(
                None, dialect=dialect, reserved_names=reserved_names
            )
        return name, True

    def get_cte_segments(self) -> list[BaseSegment]:
        """Return a valid list of CTES with required padding segments."""
        cte_segments: list[BaseSegment] = []
        for cte in self.ctes:
            cte_segments += [
                cte,
                SymbolSegment(",", type="comma"),
                NewlineSegment(),
            ]
        return cte_segments[:-2]

    def compose_select(
        self, output_select_clone: BaseSegment, case_preference: str
    ) -> BaseSegment:
        """Compose our final new CTE."""
        # Compose the CTE.
        new_select = WithCompoundStatementSegment(
            segments=tuple(
                [
                    _segmentify("WITH", case_preference),
                    WhitespaceSegment(),
                    *self.get_cte_segments(),
                    NewlineSegment(),
                    output_select_clone,
                ]
            )
        )
        return new_select

    def ensure_space_after_from(
        self,
        output_select: BaseSegment,
        output_select_clone: BaseSegment,
        subquery_parent: BaseSegment,
    ) -> list[LintFix]:
        """Ensure there's whitespace between "FROM" and the CTE table name."""
        fixes = []
        if subquery_parent is output_select:
            (
                missing_space_after_from,
                from_clause,
                from_clause_children,
                from_segment,
            ) = self._missing_space_after_from(output_select_clone)
            if missing_space_after_from:
                # Case 1: from_clause is a child of cloned "output_select_clone"
                # that will be inserted by a fix. We can directly manipulate the
                # "segments" list. to insert whitespace between "FROM" and the
                # CTE table name.
                idx_from = from_clause_children.index(from_segment[0])
                from_clause.segments = list(
                    from_clause_children[: idx_from + 1]
                    + (WhitespaceSegment(),)
                    + from_clause_children[idx_from + 1 :]
                )
        else:
            (
                missing_space_after_from,
                from_clause,
                from_clause_children,
                from_segment,
            ) = self._missing_space_after_from(subquery_parent)
            if missing_space_after_from:
                # Case 2. from_segment is in the current parse tree, so we can't
                # modify it directly. Create a LintFix to do it.
                fixes.append(
                    LintFix.create_after(from_segment[0], [WhitespaceSegment()])
                )
        return fixes

    @staticmethod
    def _missing_space_after_from(segment: BaseSegment):
        missing_space_after_from = False
        from_clause_children = None
        from_segment = None
        from_clause = segment.get_child("from_clause")
        if from_clause is not None:
            from_clause_children = Segments(*from_clause.segments)
            from_segment = from_clause_children.first(is_keyword("from"))
            if from_segment and not from_clause_children.select(
                start_seg=from_segment[0], loop_while=is_whitespace()
            ):
                missing_space_after_from = True
        return missing_space_after_from, from_clause, from_clause_children, from_segment

    def replace_with_clone(self, segment, clone_map) -> None:
        for idx, cte in enumerate(self.ctes):
            if any(segment is seg for seg in cte.recursive_crawl_all()):
                self.ctes[idx] = clone_map[self.ctes[idx]]
                return None


def _is_child(maybe_parent: Segments, maybe_child: Segments) -> bool:
    """Is the child actually between the start and end markers of the parent."""
    assert len(maybe_child) == 1, (
        "Cannot assess child relationship of multiple segments"
    )
    assert len(maybe_parent) == 1, (
        "Cannot assess child relationship of multiple parents"
    )
    child_markers = maybe_child[0].pos_marker
    parent_pos = maybe_parent[0].pos_marker
    assert parent_pos and child_markers
    if child_markers.start_point_marker() < parent_pos.start_point_marker():
        return False  # pragma: no cover

    if child_markers.end_point_marker() > parent_pos.end_point_marker():
        return False

    return True


S = TypeVar("S", bound=type[BaseSegment])


def _get_seg(class_def: S, dialect: Dialect) -> S:
    return cast(S, dialect.get_segment(class_def.__name__))


def _create_cte_seg(
    alias_name: str, subquery: BaseSegment, case_preference: str, dialect: Dialect
) -> CTEDefinitionSegment:
    CTESegment = _get_seg(CTEDefinitionSegment, dialect)
    IdentifierSegment = cast(
        type[CodeSegment], dialect.get_segment("IdentifierSegment")
    )
    element: CTEDefinitionSegment = CTESegment(
        segments=(
            IdentifierSegment(
                raw=alias_name,
                type="naked_identifier",
            ),
            WhitespaceSegment(),
            _segmentify("AS", casing=case_preference),
            WhitespaceSegment(),
            # Return the bracketed segment instead of the table expression
            subquery,
        )
    )
    return element


def _normalize_generated_identifier(identifier: str, dialect: Dialect) -> str:
    """Normalize a generated naked identifier using dialect case rules."""
    casefold = getattr(dialect.ref("NakedIdentifierSegment"), "casefold", None)
    return casefold(identifier) if casefold else identifier


def _create_table_ref(table_name: str, dialect: Dialect) -> TableExpressionSegment:
    Seg = partial(_get_seg, dialect=dialect)
    TableExpressionSeg = Seg(TableExpressionSegment)
    TableReferenceSeg = Seg(TableReferenceSegment)
    IdentifierSegment = cast(
        type[CodeSegment], dialect.get_segment("IdentifierSegment")
    )
    return TableExpressionSeg(
        segments=(
            TableReferenceSeg(
                segments=(
                    IdentifierSegment(
                        raw=table_name,
                        type="naked_identifier",
                    ),
                ),
            ),
        ),
    )


def _get_case_preference(root_select: Segments):
    # First get the segment itself so we have access to the generator
    root_segment = root_select.get()
    assert root_segment, "Root SELECT not found."
    # Get the first item of the recursive crawl.
    first_keyword = next(
        root_segment.recursive_crawl(
            "keyword",
            recurse_into=False,
        ),
        None,
    )
    assert first_keyword, "Keyword not found."
    # Get case preference based on the case of that keyword.
    if first_keyword.raw.islower():
        return "LOWER"
    return "UPPER"


def _segmentify(input_el: str, casing: str) -> BaseSegment:
    """Apply casing and convert strings to Keywords."""
    input_el = input_el.lower()
    if casing == "UPPER":
        input_el = input_el.upper()

    return KeywordSegment(raw=input_el)


class SegmentCloneMap:
    """Clones a segment tree, maps from original segments to their clones.

    The clone (a full ``segment.copy()``) is built lazily on first lookup: the
    caller builds the map for every SELECT statement but only *uses* it when
    there are subqueries to rewrite, so deferring avoids cloning the whole
    statement tree on the common no-subquery path (a notable cost over the Rust
    arena façade, where copy() materialises real segments).
    """

    def __init__(self, segment: BaseSegment):
        self._segment = segment
        self.segment_map: Optional[dict[int, BaseSegment]] = None

    def _build(self) -> dict[int, BaseSegment]:
        segment = self._segment
        segment_copy = segment.copy()
        segment_map: dict[int, BaseSegment] = {}
        for old_segment, new_segment in zip(
            segment.recursive_crawl_all(),
            segment_copy.recursive_crawl_all(),
        ):
            new_segment.pos_marker = old_segment.pos_marker
            segment_map[id(old_segment)] = new_segment
        self.segment_map = segment_map
        return segment_map

    def __getitem__(self, old_segment: BaseSegment) -> BaseSegment:
        segment_map = self.segment_map
        if segment_map is None:
            segment_map = self._build()
        return segment_map[id(old_segment)]
