"""Implementation of Rule CV05."""

from typing import List, Optional, Union

from sqlfluff.core.parser import KeywordSegment, WhitespaceSegment
from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.utils.functional import Segments, sp
from sqlfluff.utils.reflow import ReflowSequence

CorrectionListType = List[Union[WhitespaceSegment, KeywordSegment]]


class Rule_CV05(BaseRule):
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

    name = "convention.is_null"
    aliases = ("L049",)
    groups = ("all", "core", "convention")
    crawl_behaviour = SegmentSeekerCrawler({"comparison_operator"})
    is_fix_compatible = True

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Relational operators should not be used to check for NULL values."""
        # Context/motivation for this rule:
        # https://news.ycombinator.com/item?id=28772289
        # https://stackoverflow.com/questions/9581745/sql-is-null-and-null

        # Allow assignments in SET clauses
        if len(context.parent_stack) >= 2 and context.parent_stack[-2].is_type(
            "set_clause_list", "execute_script_statement", "options_segment"
        ):
            return None

        # Allow assignments in EXEC clauses, or any other explicit assignments
        if context.parent_stack and context.parent_stack[-1].is_type(
            "set_clause_list", "execute_script_statement", "assignment_operator"
        ):
            return None

        # If the operator is in an EXCLUDE constraint (PostgreSQL feature), the SQL
        # could look like: EXCLUDE (field WITH =).  In that case, we can exit early
        # to avoid an assertion failure due to no segment following the operator.
        # Note that if the EXCLUDE is based on an expression, we will still be
        # checking that expression because it will be under a different child segment.
        if context.parent_stack and context.parent_stack[-1].is_type(
            "exclusion_constraint_element"
        ):
            return None

        # We only care about equality operators.
        if context.segment.raw not in ("=", "!=", "<>"):
            return None

        # We only care if it's followed by a NULL literal.
        siblings = Segments(*context.parent_stack[-1].segments)
        after_op_list = siblings.select(start_seg=context.segment)
        next_code = after_op_list.first(sp.is_code())

        if not next_code.all(sp.is_type("null_literal")):
            return None

        sub_seg = next_code.get()
        assert sub_seg, "TypeGuard: Segment must exist"
        self.logger.debug(
            "Found NULL literal following equals/not equals @%s: %r",
            sub_seg.pos_marker,
            sub_seg.raw,
        )

        edit = _create_base_is_null_sequence(
            is_upper=sub_seg.raw[0] == "N",
            operator_raw=context.segment.raw,
        )

        return LintResult(
            anchor=context.segment,
            fixes=ReflowSequence.from_around_target(
                context.segment, context.parent_stack[0], config=context.config
            )
            .replace(context.segment, edit)
            .respace()
            .get_fixes(),
        )


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
