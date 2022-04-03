"""Implementation of Rule L042."""
import copy
from functools import partial
from typing import Generator, List, NamedTuple, Optional, Type, TypeVar, cast
from sqlfluff.core.dialects.base import Dialect
from sqlfluff.core.parser.markers import PositionMarker

from sqlfluff.core.parser.segments.base import BaseSegment
from sqlfluff.core.parser.segments.raw import (
    CodeSegment,
    KeywordSegment,
    NewlineSegment,
    SymbolSegment,
    WhitespaceSegment,
)

from sqlfluff.core.rules.base import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.doc_decorators import (
    document_configuration,
    document_fix_compatible,
)
from sqlfluff.core.rules.functional.segment_predicates import is_name, is_type
from sqlfluff.core.rules.functional.segments import Segments
from sqlfluff.dialects.dialect_ansi import (
    CTEDefinitionSegment,
    TableExpressionSegment,
    TableReferenceSegment,
    WithCompoundStatementSegment,
)


class _NestedSubQuerySummary(NamedTuple):
    parent_clause_type: str
    parent_select_segments: Segments
    clause_segments: Segments
    subquery: BaseSegment


@document_fix_compatible
@document_configuration
class Rule_L042(BaseRule):
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

    config_keywords = ["forbid_subquery_in"]

    _config_mapping = {
        "join": ["join_clause"],
        "from": ["from_expression_element"],
        "both": ["join_clause", "from_expression_element"],
    }

    def _eval(self, context: RuleContext) -> Optional[List[LintResult]]:
        """Join/From clauses should not contain subqueries. Use CTEs instead."""
        select_types = [
            "with_compound_statement",
            "set_expression",
            "select_statement",
        ]
        self.forbid_subquery_in: str
        parent_types = self._config_mapping[self.forbid_subquery_in]
        segment = context.functional.segment
        parent_stack = context.functional.parent_stack
        is_select = segment.all(is_type(*select_types))
        is_select_child = parent_stack.any(is_type(*select_types))
        if not is_select or is_select_child:
            # Subvert the Crawler
            return None

        # Gather all possible offending Elements in one crawl
        nested_subqueries: List[_NestedSubQuerySummary] = []
        selects = segment.recursive_crawl(*select_types, recurse_into=True)
        for select in selects.iterate_segments():
            for res in _find_nested_subqueries(select):
                if res.parent_clause_type not in parent_types:
                    continue
                nested_subqueries.append(res)

        if not nested_subqueries:
            return None
        # If there are offending elements calculate fixes
        return _calculate_fixes(
            dialect=context.dialect,
            root_select=segment,
            nested_subqueries=nested_subqueries,
        )


def _calculate_fixes(
    dialect: Dialect,
    root_select: Segments,
    nested_subqueries: List[_NestedSubQuerySummary],
) -> List[LintResult]:
    """Given the Root select and the offending subqueries calculate fixes."""
    is_with = root_select.all(is_type("with_compound_statement"))
    # TODO: consider if we can fix recursive CTEs
    is_recursive = is_with and len(root_select.children(is_name("recursive"))) > 0
    case_preference = _get_case_preference(root_select)
    # generate an instance which will track and shape out output CTE
    ctes = _CTEBuilder()
    # Init the output/final select &
    # populate existing CTEs
    for cte in root_select.children(is_type("common_table_expression")):
        assert isinstance(cte, CTEDefinitionSegment), "TypeGuard"
        ctes.insert_cte(cte)

    output_select = root_select
    if is_with:
        output_select = root_select.children(
            is_type(
                "set_expression",
                "select_statement",
            )
        )

    lint_results: List[LintResult] = []
    clone_map = SegmentCloneMap(root_select[0])
    for parent_type, _, this_seg, subquery in nested_subqueries:
        alias_name = ctes.create_cte_alias(
            this_seg.children(is_type("alias_expression"))
        )
        new_cte = _create_cte_seg(
            alias_name=alias_name,
            subquery=clone_map[subquery],
            case_preference=case_preference,
            dialect=dialect,
        )
        ctes.insert_cte(new_cte)
        this_seg_clone = clone_map[this_seg[0]]
        assert this_seg_clone.pos_marker, "TypeGuard"
        this_seg_clone.segments = (
            _create_table_ref(alias_name, dialect, this_seg_clone.pos_marker),
        )
        anchor = subquery
        # Grab the first keyword or symbol in the subquery to use as the
        # anchor. This makes the lint warning less likely to be filtered out
        # if a bit of the subquery happens to be templated.
        for seg in subquery.recursive_crawl("keyword", "symbol"):
            anchor = seg
            break
        res = LintResult(
            anchor=anchor,
            description=f"{parent_type} clauses should not contain "
            "subqueries. Use CTEs instead",
            fixes=[],
        )
        lint_results.append(res)

    if ctes.has_duplicate_aliases() or is_recursive:
        # If we have duplicate CTE names just don't fix anything
        # Return the lint warnings anyway
        return lint_results

    # Add fixes to the last result only
    lint_results[-1].fixes = [
        LintFix.replace(
            root_select[0],
            edit_segments=[
                ctes.compose_select(
                    clone_map[output_select[0]],
                    case_preference=case_preference,
                ),
            ],
        )
    ]
    return lint_results


def _find_nested_subqueries(
    select: Segments,
) -> Generator[_NestedSubQuerySummary, None, None]:
    """Find possible offending elements and return enough to fix them."""
    select_types = [
        "with_compound_statement",
        "set_expression",
        "select_statement",
    ]
    from_clause = select.children().first(is_type("from_clause")).children()
    offending_types = ["join_clause", "from_expression_element"]
    # Match any of the types we care about
    for this_seg in from_clause.children(is_type(*offending_types)).iterate_segments():
        parent_type = this_seg[0].get_type()
        # Ensure we are at the right depth (from_expression_element)
        if not this_seg.all(is_type("from_expression_element")):
            this_seg = this_seg.children(
                is_type("from_expression_element"),
            )

        table_expression_el = this_seg.children(
            is_type("table_expression"),
        )

        # Is it bracketed? If so, lint that instead.
        bracketed_expression = table_expression_el.children(
            is_type("bracketed"),
        )
        nested_select = bracketed_expression or table_expression_el
        # If we find a child with a "problem" type, raise an issue.
        # If not, we're fine.
        seg = nested_select.children(is_type(*select_types))
        if not seg:
            # If there is no match there is no error
            continue
        # Type, parent_select, parent_sequence
        yield _NestedSubQuerySummary(
            parent_type, select, this_seg, table_expression_el[0]
        )


class _CTEBuilder:
    """Gather CTE parts, maintain order and track naming/aliasing."""

    def __init__(self) -> None:
        self.ctes: List[CTEDefinitionSegment] = []
        self.name_idx = 0

    def list_used_names(self) -> List[str]:
        """Check CTEs and return used aliases."""
        used_names: List[str] = []
        for cte in self.ctes:
            id_seg = cte.get_identifier()
            cte_name = id_seg.raw
            if id_seg.is_name("quoted_identifier"):
                cte_name = cte_name[1:-1]

            used_names.append(cte_name)
        return used_names

    def has_duplicate_aliases(self) -> bool:
        used_names = self.list_used_names()
        return len(set(used_names)) != len(used_names)

    def insert_cte(self, cte: CTEDefinitionSegment):
        """Add a new CTE to the list as late as possible but before all its parents."""
        # This should still have the position markers of its true position
        inbound_subquery = Segments(cte).children().last()
        insert_position = next(
            (
                i
                for i, el in enumerate(self.ctes)
                if _is_child(Segments(el).children().last(), inbound_subquery)
            ),
            len(self.ctes),
        )

        self.ctes.insert(insert_position, cte)

    def create_cte_alias(self, alias_segment: Optional[Segments] = None) -> str:
        """Find or create the name for the next CTE."""
        if alias_segment:
            # If we know the name use it
            name = alias_segment.children().last()[0].raw
            return name

        self.name_idx = self.name_idx + 1
        name = f"prep_{self.name_idx}"
        if name in self.list_used_names():
            # corner case where prep_x exists in origin query
            return self.create_cte_alias(None)
        return name

    def get_cte_segements(self) -> List[BaseSegment]:
        """Return a valid list of CTES with required padding Segements."""
        cte_segments: List[BaseSegment] = []
        for cte in self.ctes:
            cte_segments = cte_segments + [
                cte,
                SymbolSegment(",", name="comma", type="comma"),
                NewlineSegment(),
            ]
        return cte_segments[:-2]

    def compose_select(self, output_select: BaseSegment, case_preference: str):
        """Compose our final new CTE."""
        new_select = WithCompoundStatementSegment(
            segments=tuple(
                [
                    _segmentify("WITH", case_preference),
                    WhitespaceSegment(),
                    *self.get_cte_segements(),
                    NewlineSegment(),
                    output_select,
                ]
            )
        )
        return new_select


def _is_child(maybe_parent: Segments, maybe_child: Segments) -> bool:
    """Is the child actually between the start and end markers of the parent."""
    assert len(maybe_child) == 1, "Cannot assess Childness of multiple Segments"
    assert len(maybe_parent) == 1, "Cannot assess Childness of multiple Parents"
    child_markers = maybe_child[0].pos_marker
    parent_pos = maybe_parent[0].pos_marker
    if not parent_pos or not child_markers:
        return False  # pragma: no cover

    if child_markers < parent_pos.start_point_marker():
        return False  # pragma: no cover

    if child_markers > parent_pos.end_point_marker():
        return False

    return True


S = TypeVar("S", bound=Type[BaseSegment])


def _get_seg(class_def: S, dialect: Dialect) -> S:
    return cast(S, dialect.get_segment(class_def.__name__))


def _create_cte_seg(
    alias_name: str, subquery: BaseSegment, case_preference: str, dialect: Dialect
) -> CTEDefinitionSegment:
    CTESegment = _get_seg(CTEDefinitionSegment, dialect)
    element: CTEDefinitionSegment = CTESegment(
        segments=(
            CodeSegment(
                raw=alias_name,
                name="naked_identifier",
                type="identifier",
            ),
            WhitespaceSegment(),
            _segmentify("AS", casing=case_preference),
            WhitespaceSegment(),
            subquery,
        )
    )
    return element


def _create_table_ref(
    table_name: str, dialect: Dialect, position_marker: PositionMarker
) -> TableExpressionSegment:
    # The mutative change needs a position_marker
    position_marker = PositionMarker.from_point(
        position_marker.source_slice.start,
        position_marker.templated_slice.start,
        position_marker.templated_file,
    )
    Seg = partial(_get_seg, dialect=dialect)
    TableExpressionSeg = Seg(TableExpressionSegment)
    TableReferenceSeg = Seg(TableReferenceSegment)
    table_seg = TableExpressionSeg(
        segments=(
            TableReferenceSeg(
                segments=(
                    CodeSegment(
                        raw=table_name,
                        name="naked_identifier",
                        type="identifier",
                        pos_marker=position_marker,
                    ),
                ),
                pos_marker=position_marker,
            ),
        ),
        pos_marker=position_marker,
    )
    return table_seg  # type: ignore


def _get_case_preference(root_select: Segments):
    first_keyword = root_select.recursive_crawl(
        "keyword",
        recurse_into=False,
    ).first()[0]
    if first_keyword.raw[0].islower():
        return "LOWER"

    return "UPPER"


def _segmentify(input_el: str, casing: str) -> BaseSegment:
    """Apply casing and convert strings to Keywords."""
    input_el = input_el.lower()
    if casing == "UPPER":
        input_el = input_el.upper()

    return KeywordSegment(raw=input_el)


class SegmentCloneMap:
    """Clones a segment tree, maps from original segments to their clones."""

    def __init__(self, segment: BaseSegment):
        segment_copy = copy.deepcopy(segment)
        self.segment_map = {}
        for old_segment, new_segment in zip(
            segment.recursive_crawl_all(),
            segment_copy.recursive_crawl_all(),
        ):
            self.segment_map[id(old_segment)] = new_segment

    def __getitem__(self, old_segment: BaseSegment) -> BaseSegment:
        return self.segment_map[id(old_segment)]
