"""Implementation of Rule L040."""

from sqlfluff.core.rules.base import BaseCrawler, LintFix, LintResult
from sqlfluff.core.rules.doc_decorators import document_fix_compatible


@document_fix_compatible
class Rule_L041(BaseCrawler):
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

    def _eval(self, segment, **kwargs):
        """Select clause modifiers must appear on same line as SELECT."""
        if segment.is_type("select_clause"):
            # Does the select clause have modifiers?
            select_modifier = segment.get_child("select_clause_modifier")
            if not select_modifier:
                return None  # No. We're done.
            select_modifier_idx = segment.segments.index(select_modifier)

            # Does the select clause contain a newline?
            newline = segment.get_child("newline")
            if not newline:
                return None  # No. We're done.
            newline_idx = segment.segments.index(newline)

            # Is there a newline before the select modifier?
            if newline_idx > select_modifier_idx:
                return None  # No, we're done.

            # Yes to all the above. We found an issue.

            # E.g.: " DISTINCT\n"
            replace_newline_with = [
                self.make_whitespace(raw=" ", pos_marker=newline.pos_marker),
                select_modifier,
                self.make_newline(pos_marker=newline.pos_marker),
            ]
            fixes = [
                # E.g. "\n" -> " DISTINCT\n.
                LintFix("edit", newline, replace_newline_with),
                # E.g. "DISTINCT" -> X
                LintFix("delete", select_modifier),
            ]

            # E.g. " " after "DISTINCT"
            ws_to_delete = segment.select_children(
                start_seg=select_modifier,
                select_if=lambda s: s.is_type("whitespace"),
                loop_while=lambda s: s.is_type("whitespace") or s.is_meta,
            )

            # E.g. " " -> X
            fixes += [LintFix("delete", ws) for ws in ws_to_delete]
            return LintResult(
                anchor=segment,
                fixes=fixes,
            )
