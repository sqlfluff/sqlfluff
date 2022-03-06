"""Implementation of Rule L042."""
from typing import List, Optional, Union

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
from sqlfluff.core.rules.functional.segment_predicates import is_type
from sqlfluff.core.rules.functional.segments import Segments


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

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Join/From clauses should not contain subqueries. Use CTEs instead.

        NB: No fix for this routine because it would be very complex to
        implement reliably.
        """
        self.forbid_subquery_in: str
        parent_types = self._config_mapping[self.forbid_subquery_in]
        segment = context.functional.segment
        memory = context.memory

        if memory and memory.flush_anchor == segment:
            # If we reach the "final" segment in the top most select
            # then we can finalise our lints/fixes
            return memory.flush()

        select_types = [
            "with_compound_statement",
            "set_expression",
            "select_statement",
        ]
        if not segment.all(is_type(*select_types)):
            # If its not a select just keep crawling
            return LintResult(memory=memory)

        children = segment.children()
        if not memory:
            # memory always anchors us to the top most Select
            # this allows us to hoist CTEs to the top instead of just one above
            memory = _MyMemory(segment)

        from_clause = children.first(is_type("from_clause")).children()
        # Match any of the types we care about
        for this_seg in from_clause.children(is_type(*parent_types)).iterate_segments():
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

            # We buffer up errors in so that we can apply later as a batch
            # taking care of order and duplicate CTE names
            alias_if_exists = this_seg.children(is_type("alias_expression"))
            subquery = table_expression_el[0]
            alias_name = memory.buffer_fix(
                subquery,
                alias_if_exists,
            )

            # Remove "AS x" if it exists (new CTE will be called "x") anyway
            rest_els = this_seg.children().select(
                start_seg=subquery,
            )

            res = LintResult(
                anchor=seg[0],
                description=f"{parent_type} clauses should not contain "
                "subqueries. Use CTEs instead",
                fixes=[
                    LintFix.replace(
                        subquery,
                        edit_segments=[
                            CodeSegment(
                                raw=alias_name,
                                name="naked_identifier",
                                type="identifier",
                            )
                        ],
                    ),
                    *rest_els.apply(LintFix.delete),
                ],
                memory=memory,
            )
            memory.buffer_result(res)

        return LintResult(memory=memory)


class _MyMemory:
    """Buffer CTE movements, so they can be applied in bulk without a recrawl."""

    def __init__(self, root_select_anchor: Segments) -> None:
        self.root_select_anchor = root_select_anchor
        self.is_with = root_select_anchor.all(is_type("with_compound_statement"))
        # Gather the last possible segment in this select
        self.flush_anchor = root_select_anchor.dive_last(max_depth=6)
        first_keyword = (
            root_select_anchor.children().children().first(is_type("keyword")).get(0)
        )
        assert first_keyword, "TypeGaurd"
        self.anchor: BaseSegment = first_keyword
        if self.is_with:
            self.anchor = root_select_anchor.children().children().first()[0]

        self.first_keyword = first_keyword.raw.lower()
        self.casing_prefrence = (
            "LOWER" if first_keyword.raw[0] == self.first_keyword[0] else "UPPER"
        )
        self.used_names: List[str] = []
        # TODO: fix duplicate names (in bound from existing CTE)
        self.name_idx = 0
        self.fixes = -1
        self.edit_segments: List[BaseSegment] = []
        self.lint_results: List[LintResult] = []

    @property
    def needs_with(self) -> bool:
        if self.is_with:
            return False

        if self.first_keyword == "with":
            return False

        return self.fixes == 0

    def get_name(self, alias_segment: Optional[Segments] = None) -> str:
        """Find or create the name for the next CTE."""
        if alias_segment:
            name = alias_segment.children().last()[0].raw
            self.used_names.append(name)
            return name

        self.name_idx = self.name_idx + 1
        name = f"prep_{self.name_idx}"
        self.used_names.append(name)
        return name

    def buffer_result(self, res: LintResult):
        # We buffer fixes so as not to trigger a crawl and memory wipe
        self.lint_results.append(res)

    def buffer_fix(self, subquery: BaseSegment, alias_segment: Segments) -> str:
        """Create and ordering for Segments that should be moved to CTEs."""
        alias_name = self.get_name(alias_segment)
        self.fixes = self.fixes + 1

        start_stmt: List[Union[str, BaseSegment]] = [
            "WITH",
            " ",
        ]
        if not self.needs_with:
            start_stmt = [
                SymbolSegment(",", name="comma", type="comma"),
                NewlineSegment(),
            ]

        edits: List[Union[str, BaseSegment]] = [
            *start_stmt,
            CodeSegment(raw=alias_name, name="naked_identifier", type="identifier"),
            " ",
            "AS",
            " ",
            subquery,
            NewlineSegment(),
        ]

        if self.fixes > 0:
            # Always remove the newline
            # of the previous CTE
            self.edit_segments.pop()

        # utility to calc
        self.edit_segments = self.edit_segments + [
            _segmentify(el, self.casing_prefrence) for el in edits
        ]

        return alias_name

    def flush(self) -> List[LintResult]:
        edit = self.edit_segments
        if self.is_with and edit:
            edit = edit[2:-1] + [
                SymbolSegment(",", name="comma", type="comma"),
                NewlineSegment(),
            ]
        res = LintResult(
            memory=None,
            fixes=[
                LintFix("create_before", self.anchor, edit=edit),
            ],
        )
        print(edit)
        return self.lint_results + [res]


def _segmentify(input_el: Union[str, BaseSegment], casing: str) -> BaseSegment:
    """Apply casing an convert strings to Keywords or Whitespace."""
    if isinstance(input_el, BaseSegment):
        return input_el

    if input_el[0] == " ":
        return WhitespaceSegment(raw=input_el)

    input_el = input_el.lower()
    if casing == "UPPER":
        input_el = input_el.upper()

    return KeywordSegment(raw=input_el)
