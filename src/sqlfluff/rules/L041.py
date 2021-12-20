"""Implementation of Rule L040."""
from typing import Optional

from sqlfluff.core.parser import NewlineSegment, WhitespaceSegment

from sqlfluff.core.rules.base import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.doc_decorators import document_fix_compatible


@document_fix_compatible
class Rule_L041(BaseRule):
    """SELECT clause modifiers such as DISTINCT must be on the same line as SELECT.

    | **Anti-pattern**

    .. code-block:: sql

        select
            distinct a,
            b
        from x


    | **Best practice**

    .. code-block:: sql

        select distinct
            a,
            b
        from x

    """

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Select clause modifiers must appear on same line as SELECT."""
        if context.segment.is_type("select_clause"):
            # Scan the select clause's children. Look for three things in sequence:
            # 1. SELECT keyword (required)
            # 2. Newline (optional)
            # 3. Select modifier, e.g. "DISTINCT" (optional)
            select_keyword = None
            newline_between = None
            select_modifier = None
            for idx, child in enumerate(context.segment.segments):
                if select_keyword is None:
                    if child.is_type("keyword") and child.raw.lower() == "select":
                        select_keyword = child
                if (
                    select_keyword
                    and newline_between is None
                    and select_modifier is None
                    and child.is_type("newline")
                ):
                    newline_between = child
                    newline_idx = idx
                if select_modifier is None and child.is_type("select_clause_modifier"):
                    select_modifier = child
                    break

            # Does the select clause have modifiers?
            if not select_modifier:
                return None  # No. We're done.

            # Does select clause contain a newline between SELECT and the modifiers?
            if not newline_between:
                return None  # No. We're done.

            # Yes to all the above. We found an issue.

            # E.g.: " DISTINCT\n"
            replace_newline_with = [
                WhitespaceSegment(),
                select_modifier,
                NewlineSegment(),
            ]
            fixes = [
                # E.g. "\n" -> " DISTINCT\n.
                LintFix.delete(newline_between),
                LintFix.create_before(
                    context.segment.segments[newline_idx + 1],
                    replace_newline_with,
                ),
                # E.g. "DISTINCT" -> X
                LintFix.delete(select_modifier),
            ]

            # E.g. " " after "DISTINCT"
            ws_to_delete = context.segment.select_children(
                start_seg=select_modifier,
                select_if=lambda s: s.is_type("whitespace"),
                loop_while=lambda s: s.is_type("whitespace") or s.is_meta,
            )

            # E.g. " " -> X
            fixes += [LintFix.delete(ws) for ws in ws_to_delete]
            return LintResult(
                anchor=context.segment,
                fixes=fixes,
            )

        return None
