"""Implementation of Rule L041."""
from typing import Optional

from apm import match, Check, Some, Not

from sqlfluff.core.parser import NewlineSegment, WhitespaceSegment
from sqlfluff.core.rules.base import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.doc_decorators import document_fix_compatible
import sqlfluff.core.rules.functional.segment_predicates as sp


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
            # Analyze the select clause's children, looking for the following pattern:
            # 1. SELECT keyword (required)
            # 2. Newline (optional)
            # 3. Select modifier, e.g. "DISTINCT" (optional)
            matched = match(
                context.segment.segments,
                [
                    Check(
                        sp.and_(
                            sp.is_type("keyword"),
                            lambda seg: seg.raw.lower() == "select",
                        )
                    ),
                    Some(Not(Check(sp.is_type("newline"))), at_least=0),
                    "newline" @ Check(sp.is_type("newline")),
                    Some(Not(Check(sp.is_type("select_clause_modifier"))), at_least=0),
                    "modifier" @ Check(sp.is_type("select_clause_modifier")),
                    Some(...),
                ],
            )
            if not matched:
                return None

            # We found a pattern match, thus there's an issue.
            newline_between = matched.groups()["newline"]
            newline_idx = context.segment.segments.index(newline_between)
            select_modifier = matched.groups()["modifier"]

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
