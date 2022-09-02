"""Implementation of Rule L049."""
from typing import List, Optional, Union

from sqlfluff.core.parser import KeywordSegment, WhitespaceSegment
from sqlfluff.core.rules import LintResult, LintFix, RuleContext
from sqlfluff.core.rules.doc_decorators import document_fix_compatible, document_groups
from sqlfluff.rules.L006 import Rule_L006
from sqlfluff.utils.functional import sp, FunctionalContext


CorrectionListType = List[Union[WhitespaceSegment, KeywordSegment]]


@document_groups
@document_fix_compatible
class Rule_L049(Rule_L006):
    """Comparisons with NULL should use "IS" or "IS NOT".

    **Anti-pattern**

    In this example, the ``=`` operator is used to check for ``NULL`` values.

    .. code-block:: sql

        SELECT
            a
        FROM foo
        WHERE a = NULL


    **Best practice**

    Use ``IS`` or ``IS NOT`` to check for ``NULL`` values.

    .. code-block:: sql

        SELECT
            a
        FROM foo
        WHERE a IS NULL
    """

    groups = ("all", "core")
    # Inherit crawl behaviour from L006

    def _eval(self, context: RuleContext) -> Optional[List[LintResult]]:
        """Relational operators should not be used to check for NULL values."""
        # Context/motivation for this rule:
        # https://news.ycombinator.com/item?id=28772289
        # https://stackoverflow.com/questions/9581745/sql-is-null-and-null
        if len(context.segment.segments) <= 2:
            return None  # pragma: no cover

        # Allow assignments in SET clauses
        if context.parent_stack and context.parent_stack[-1].is_type(
            "set_clause_list", "execute_script_statement"
        ):
            return None

        # Allow assignments in EXEC clauses
        if context.segment.is_type("set_clause_list", "execute_script_statement"):
            return None

        segment = FunctionalContext(context).segment
        # Iterate through children of this segment looking for equals or "not
        # equals". Once found, check if the next code segment is a NULL literal.

        children = segment.children()
        operators = segment.children(sp.raw_is("=", "!=", "<>"))
        if len(operators) == 0:
            return None
        self.logger.debug("Operators found: %s", operators)

        results: List[LintResult] = []
        # We may have many operators
        for operator in operators:
            self.logger.debug("Children found: %s", children)
            after_op_list = children.select(start_seg=operator)
            # If nothing comes after operator then skip
            if not after_op_list:
                continue  # pragma: no cover
            null_literal = after_op_list.first(sp.is_code())
            # if the next bit of code isnt a NULL then we are good
            if not null_literal.all(sp.is_type("null_literal")):
                continue

            sub_seg = null_literal.get()
            assert sub_seg, "TypeGuard: Segment must exist"
            self.logger.debug(
                "Found NULL literal following equals/not equals @%s: %r",
                sub_seg.pos_marker,
                sub_seg.raw,
            )
            edit = _create_base_is_null_sequence(
                is_upper=sub_seg.raw[0] == "N",
                operator_raw=operator.raw,
            )
            prev_seg = after_op_list.first().get()
            next_seg = children.select(stop_seg=operator).last().get()
            if self._missing_whitespace(prev_seg, before=True):
                whitespace_segment: CorrectionListType = [WhitespaceSegment()]
                edit = whitespace_segment + edit
            if self._missing_whitespace(next_seg, before=False):
                edit = edit + [WhitespaceSegment()]
            res = LintResult(
                anchor=operator,
                fixes=[
                    LintFix.replace(
                        operator,
                        edit,
                    )
                ],
            )
            results.append(res)

        return results or None


def _create_base_is_null_sequence(
    is_upper: bool,
    operator_raw: str,
) -> CorrectionListType:
    is_seg = KeywordSegment("IS" if is_upper else "is")
    not_seg = KeywordSegment("NOT" if is_upper else "not")
    if operator_raw == "=":
        return [is_seg]

    return [
        is_seg,
        WhitespaceSegment(),
        not_seg,
    ]
