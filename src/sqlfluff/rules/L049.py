"""Implementation of Rule L049."""
from typing import Tuple

from apm import match, Check, Some

from sqlfluff.core.parser import KeywordSegment, RawSegment, WhitespaceSegment
from sqlfluff.core.rules.base import LintResult, LintFix, RuleContext
from sqlfluff.core.rules.doc_decorators import document_fix_compatible
import sqlfluff.core.rules.functional.segment_predicates as sp
from sqlfluff.rules.L006 import Rule_L006


@document_fix_compatible
class Rule_L049(Rule_L006):
    """Comparisons with NULL should use "IS" or "IS NOT".

    | **Anti-pattern**
    | In this example, the "=" operator is used to check for NULL values'.

    .. code-block:: sql

        SELECT
            a
        FROM foo
        WHERE a = NULL


    | **Best practice**
    | Use "IS" or "IS NOT" to check for NULL values.

    .. code-block:: sql

        SELECT
            a
        FROM foo
        WHERE a IS NULL
    """

    def _eval(self, context: RuleContext) -> LintResult:
        """Relational operators should not be used to check for NULL values."""
        # Context/motivation for this rule:
        # https://news.ycombinator.com/item?id=28772289
        # https://stackoverflow.com/questions/9581745/sql-is-null-and-null
        if len(context.segment.segments) <= 2:
            return LintResult()

        # Allow assignments in SET clauses
        if context.parent_stack and context.parent_stack[-1].is_type("set_clause_list"):
            return LintResult()

        children = context.functional.segment.children()
        matched = match(
            children,
            [
                Some(Check(sp.not_(sp.is_name("equals", "not_equal_to"))), at_least=0),
                # "=" or "<>"
                "operator" @ Check(sp.is_name("equals", "not_equal_to")),
                Some(Check(sp.not_(sp.is_name("null_literal"))), at_least=0),
                # "NULL" literal
                "null" @ Check(sp.is_name("null_literal")),
                Some(...),
            ],
        )
        if not matched:
            return LintResult()

        if matched["null"].raw[0] == "N":
            is_seg = KeywordSegment("IS")
            not_seg = KeywordSegment("NOT")
        else:
            is_seg = KeywordSegment("is")
            not_seg = KeywordSegment("not")

        edit: Tuple[RawSegment, ...] = (
            (is_seg,)
            if matched["operator"].name == "equals"
            else (
                is_seg,
                WhitespaceSegment(),
                not_seg,
            )
        )
        idx_operator = children.index(matched["operator"])
        prev_seg = self._find_segment(
            idx_operator, context.segment.segments, before=True
        )
        if self._missing_whitespace(prev_seg, before=True):
            edit = (WhitespaceSegment(),) + edit
        next_seg = self._find_segment(
            idx_operator, context.segment.segments, before=False
        )
        if self._missing_whitespace(next_seg, before=False):
            edit = edit + (WhitespaceSegment(),)
        return LintResult(
            anchor=matched["operator"],
            fixes=[
                LintFix.replace(
                    matched["operator"],
                    edit,
                )
            ],
        )
