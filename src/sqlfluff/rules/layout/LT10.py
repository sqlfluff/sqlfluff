"""Implementation of Rule LT10."""

from typing import Optional

from sqlfluff.core.parser import NewlineSegment, WhitespaceSegment
from sqlfluff.core.rules import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.utils.functional import FunctionalContext, sp


class Rule_LT10(BaseRule):
    """``SELECT`` modifiers (e.g. ``DISTINCT``) must be on the same line as ``SELECT``.

    **Anti-pattern**

    .. code-block:: sql

        select
            distinct a,
            b
        from x


    **Best practice**

    .. code-block:: sql

        select distinct
            a,
            b
        from x

    """

    name = "layout.select_modifiers"
    aliases = ("L041",)
    groups = ("all", "core", "layout")
    crawl_behaviour = SegmentSeekerCrawler({"select_clause"})
    is_fix_compatible = True

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Select clause modifiers must appear on same line as SELECT."""
        # We only care about select_clause.
        assert context.segment.is_type("select_clause")

        # Get children of select_clause and the corresponding select keyword.
        child_segments = FunctionalContext(context).segment.children()
        select_keyword = child_segments[0]

        # See if we have a select_clause_modifier.
        select_clause_modifier_seg = child_segments.first(
            sp.is_type("select_clause_modifier")
        )

        # Rule doesn't apply if there's no select clause modifier.
        if not select_clause_modifier_seg:
            return None

        select_clause_modifier = select_clause_modifier_seg[0]

        # Are there any newlines between the select keyword
        # and the select clause modifier.
        leading_newline_segments = child_segments.select(
            select_if=sp.is_type("newline"),
            loop_while=sp.or_(sp.is_whitespace(), sp.is_meta()),
            start_seg=select_keyword,
        )

        # Rule doesn't apply if select clause modifier
        # is already on the same line as the select keyword.
        if not leading_newline_segments:
            return None

        # We should check if there is whitespace before the select clause modifier
        # and remove this during the lint fix.
        leading_whitespace_segments = child_segments.select(
            select_if=sp.is_type("whitespace"),
            loop_while=sp.or_(sp.is_whitespace(), sp.is_meta()),
            start_seg=select_keyword,
        )

        # We should also check if the following select clause element
        # is on the same line as the select clause modifier.
        trailing_newline_segments = child_segments.select(
            select_if=sp.is_type("newline"),
            loop_while=sp.or_(sp.is_whitespace(), sp.is_meta()),
            start_seg=select_clause_modifier,
        )

        # We will insert these segments directly after the select keyword.
        edit_segments = [
            WhitespaceSegment(),
            select_clause_modifier,
        ]
        if not trailing_newline_segments:
            # if the first select clause element is on the same line
            # as the select clause modifier then also insert a newline.
            edit_segments.append(NewlineSegment())

        fixes = []
        # Move select clause modifier after select keyword.
        fixes.append(
            LintFix.create_after(
                anchor_segment=select_keyword,
                edit_segments=edit_segments,
            )
        )

        # Delete original newlines and whitespace between select keyword
        # and select clause modifier.

        # If there is not a newline after the select clause modifier then delete
        # newlines between the select keyword and select clause modifier.
        if not trailing_newline_segments:
            fixes.extend(LintFix.delete(s) for s in leading_newline_segments)
        # If there is a newline after the select clause modifier then delete both the
        # newlines and whitespace between the select keyword and select clause modifier.
        else:
            fixes.extend(
                LintFix.delete(s)
                for s in leading_newline_segments + leading_whitespace_segments
            )
        # Delete the original select clause modifier.
        fixes.append(LintFix.delete(select_clause_modifier))

        # If there is whitespace (on the same line) after the select clause modifier
        # then also delete this.
        trailing_whitespace_segments = child_segments.select(
            select_if=sp.is_whitespace(),
            loop_while=sp.or_(sp.is_type("whitespace"), sp.is_meta()),
            start_seg=select_clause_modifier,
        )
        if trailing_whitespace_segments:
            fixes.extend((LintFix.delete(s) for s in trailing_whitespace_segments))

        return LintResult(
            anchor=context.segment,
            fixes=fixes,
        )
