"""Implementation of Rule L036."""

from sqlfluff.core.rules.base import BaseCrawler, LintFix, LintResult
from sqlfluff.core.rules.doc_decorators import document_fix_compatible


@document_fix_compatible
class Rule_L040(BaseCrawler):
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
                return None

            newline_idx = -1
            modifiers_idx = -1
            for fname_idx, seg in enumerate(segment.segments):
                if seg is select_modifier:
                    modifiers_idx = fname_idx
                if seg.is_type("newline") and newline_idx == -1:
                    newline_idx = fname_idx

            if newline_idx < modifiers_idx:
                insert_buff = [
                    self.make_whitespace(raw=" ", pos_marker=segment.segments[newline_idx].pos_marker),
                    select_modifier,
                    self.make_newline(pos_marker=segment.segments[newline_idx].pos_marker),
                ]
                return LintResult(
                    anchor=segment,
                    fixes=[
                        # Replace "newline" with <<MODIFIERS>>, "newline".
                        LintFix("edit", segment.segments[newline_idx], insert_buff),
                        # Delete the modifiers from their original location.
                        LintFix("delete", select_modifier)
                    ])
        return None