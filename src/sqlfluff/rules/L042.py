"""Implementation of Rule L042."""
from functools import partial
from typing import Generator, List, Optional, Tuple, Union

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
    WithCompoundStatementSegment,
)


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

        root_select = segment
        nested_subqueries: List[Tuple[str, Segments, Segments, BaseSegment]] = []
        selects = segment.recursive_crawl(*select_types, recurse_into=True)
        for select in selects.iterate_segments():
            for res in _find_nested_subqueries(select):
                clause_type = res[0]
                if clause_type not in parent_types:
                    continue
                nested_subqueries.append(res)

        if not nested_subqueries:
            return None

        return _calculate_fixes(root_select, nested_subqueries)


def _calculate_fixes(
    root_select: Segments,
    nested_subqueries: List[Tuple[str, Segments, Segments, BaseSegment]],
):
    """Given the Root select and the offending subqueries calculate fixes."""
    ctes = _CTEChecker()
    is_with = root_select.all(is_type("with_compound_statement"))
    # TODO: consider if we can fix recursive CTEs
    is_recursive = is_with and len(root_select.children(is_name("recursive"))) > 0
    segmentify = partial(
        _segmentify,
        casing=_get_casing_preference(root_select),
    )
    # Init the output/final select &
    # populate existing CTEs
    output_select = root_select
    if is_with:
        output_select = root_select.children(
            is_type(
                "set_expression",
                "select_statement",
            )
        )
        for cte in root_select.children(is_type("common_table_expression")):
            assert isinstance(cte, CTEDefinitionSegment), "TypeGaurd"
            ctes.insert_cte(cte)

    lint_results: List[LintResult] = []
    for parent_type, _, this_seg, subquery in nested_subqueries:
        alias_name = ctes.get_name(this_seg.children(is_type("alias_expression")))
        ctes.insert_cte(
            CTEDefinitionSegment(
                segments=(
                    CodeSegment(
                        raw=alias_name,
                        name="naked_identifier",
                        type="identifier",
                    ),
                    WhitespaceSegment(),
                    segmentify("AS"),
                    WhitespaceSegment(),
                    subquery,
                )
            )
        )
        # TODO: Create non-mutative helper function.
        # We will replace the whole tree, mutate the table expression.
        this_seg[0].segments = (
            CodeSegment(
                raw=alias_name,
                name="naked_identifier",
                type="identifier",
            ),
        )
        res = LintResult(
            anchor=subquery,
            description=f"{parent_type} clauses should not contain "
            "subqueries. Use CTEs instead",
            fixes=[],
        )
        lint_results.append(res)

    if ctes.has_duplicates() or is_recursive:
        # If we have duplicate CTE names just don't fix anything
        return lint_results

    new_select = WithCompoundStatementSegment(
        segments=tuple(
            [
                segmentify("WITH"),
                WhitespaceSegment(),
                *ctes.get_segements(),
                NewlineSegment(),
                output_select[0],
            ]
        )
    )
    # Add fixes to the last result only
    res = lint_results.pop()
    res.fixes = [LintFix.replace(root_select[0], edit_segments=[new_select])]
    lint_results.append(res)
    return lint_results


def _is_child(maybe_parent: Segments, maybe_child: Segments) -> bool:
    """Is the child actually between the start and end markers of the parent."""
    if len(maybe_child) > 1:
        raise ValueError("Cannot assess Childness of multiple Segments")

    child_markers = maybe_child[0].pos_marker
    if not child_markers:
        return False
    for segement in maybe_parent:
        parent_pos = segement.pos_marker
        if not parent_pos:
            continue

        if child_markers < parent_pos.start_point_marker():
            continue

        if child_markers > parent_pos.end_point_marker():
            continue

        return True

    return False


def _find_nested_subqueries(
    select: Segments,
) -> Generator[Tuple[str, Segments, Segments, BaseSegment], None, None]:
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
        yield (parent_type, select, this_seg, table_expression_el[0])


def _get_casing_preference(root_select: Segments):
    first_keyword = root_select.recursive_crawl("keyword", recurse_into=False).first()[
        0
    ]
    if first_keyword.raw[0] == first_keyword.raw[0].lower():
        return "LOWER"

    return "UPPER"


class _CTEChecker:
    """Buffer CTE movements, so they can be applied in bulk without a recrawl."""

    def __init__(self) -> None:
        self.used_names: List[str] = []
        self.ctes: List[BaseSegment] = []
        self.name_idx = 0

    def has_duplicates(self) -> bool:
        return len(set(self.used_names)) != len(self.used_names)

    def insert_cte(self, cte: CTEDefinitionSegment):
        """Add a new CTE to the list as late as possible but before all its parents."""
        output: List[BaseSegment] = []
        id_seg = cte.get_identifier()
        print(id_seg, id_seg.raw, id_seg.name)
        cte_name = id_seg.raw
        if id_seg.is_name("quoted_identifier"):
            cte_name = cte_name[1:-1]

        self.used_names.append(cte_name)
        # This should still have the position markers of its true position
        inbound_subquery = Segments(cte).children().last()
        for el in self.ctes:
            if cte in output:
                output.append(el)
                continue
            if _is_child(Segments(el).children().last(), inbound_subquery):
                output.append(cte)

            output.append(el)

        if cte not in output:
            output.append(cte)

        self.ctes = output

    def get_name(self, alias_segment: Optional[Segments] = None) -> str:
        """Find or create the name for the next CTE."""
        if alias_segment:
            name = alias_segment.children().last()[0].raw
            return name

        self.name_idx = self.name_idx + 1
        name = f"prep_{self.name_idx}"
        return name

    def get_segements(self) -> List[BaseSegment]:
        """Return a valid list of CTES with required padding Segements."""
        cte_segments: List[BaseSegment] = []
        for cte in self.ctes:
            cte_segments = cte_segments + [
                cte,
                SymbolSegment(",", name="comma", type="comma"),
                NewlineSegment(),
            ]
        return cte_segments[:-2]


def _segmentify(
    input_el: Union[str, BaseSegment], casing: str
) -> BaseSegment:
    """Apply casing an convert strings to Keywords or Whitespace."""
    if isinstance(input_el, BaseSegment):
        return input_el

    if input_el[0] == " ":
        return WhitespaceSegment(raw=input_el)

    input_el = input_el.lower()
    if casing == "UPPER":
        input_el = input_el.upper()

    return KeywordSegment(raw=input_el)
