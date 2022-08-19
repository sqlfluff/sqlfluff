"""Implementation of Rule L039."""
from typing import List, Optional

from sqlfluff.core.parser import WhitespaceSegment
from sqlfluff.core.rules import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import ParentOfSegmentCrawler
from sqlfluff.core.rules.doc_decorators import document_fix_compatible, document_groups
from sqlfluff.utils.functional import sp
from sqlfluff.utils.functional.context import FunctionalContext


@document_groups
@document_fix_compatible
class Rule_L039(BaseRule):
    """Unnecessary whitespace found.

    **Anti-pattern**

    .. code-block:: sql

        SELECT
            a,        b
        FROM foo

    **Best practice**

    Unless an indent or preceding a comment, whitespace should
    be a single space.

    .. code-block:: sql

        SELECT
            a, b
        FROM foo
    """

    groups = ("all", "core")
    # We're looking for whitespace.
    crawl_behaviour = ParentOfSegmentCrawler({"whitespace"})

    @staticmethod
    def _check_diff_idx_for_casting_operator(segments, idx: int, diff: int) -> bool:
        """Check whether this segment adjoins a casting operator.

        Args:
            segments: A sequence of segments containing the segment
                we're evaluating.
            idx (int): The index of the segment we care about within
                `segments`.
            diff (int): Either 1 or -1 to indicate whether we want
                to check for casting operators before (-1) or after
                (+1).

        Returns:
            bool: The return value. True for casting operator
                detected, False otherwise.

        """
        ref_idx = idx + diff
        # Do we have a long enough sequence to check?
        if ref_idx < 0 or ref_idx >= len(segments):
            return False
        # Get the reference segment to check against
        ref_seg = segments[ref_idx]
        # Is it a casting operator?
        if ref_seg.is_type("casting_operator"):
            return True
        # Does it contain raw segments?
        if not ref_seg.raw_segments:
            return False  # pragma: no cover
        # Does the reference segment start or end with
        # a casting operator as a child?
        if diff == -1:
            child_raw = ref_seg.raw_segments[-1]
        elif diff == 1:
            child_raw = ref_seg.raw_segments[0]
        else:
            raise ValueError("Diff should be 1 or -1")  # pragma: no cover
        return child_raw.is_type("casting_operator")

    def _eval(self, context: RuleContext) -> Optional[List[LintResult]]:
        """Unnecessary whitespace."""
        # Config type hints
        self.align_alias: bool
        # For the given segment, lint whitespace directly within it.
        violations = []
        # If align_alias is true, then collect related violations.
        if self.align_alias:
            align_violation = self._align_aliases(context)
            if align_violation:
                violations.append(align_violation)
        # For some segments, strip all whitespace.
        if context.segment.is_type("object_reference", "comparison_operator"):
            for child_seg in context.segment.get_raw_segments():
                if child_seg.is_whitespace:
                    violations.append(
                        LintResult(anchor=child_seg, fixes=[LintFix.delete(child_seg)])
                    )
        # Otherwise handle normally
        else:
            non_meta_segs = [seg for seg in context.segment.segments if not seg.is_meta]
            for idx, seg in enumerate(non_meta_segs):
                if seg.is_type("whitespace"):
                    if self.align_alias and self._skip_aliases(context, seg):
                        continue
                    # Casting operators shouldn't have any whitespace around them.
                    # Look for preceeding or following casting operators either as raw
                    # segments or at the end of a parent segment.
                    if self._check_diff_idx_for_casting_operator(
                        non_meta_segs, idx, -1
                    ) or self._check_diff_idx_for_casting_operator(
                        non_meta_segs, idx, 1
                    ):
                        violations.append(
                            LintResult(
                                anchor=seg,
                                fixes=[
                                    LintFix.delete(
                                        seg,
                                    )
                                ],
                            )
                        )
                    # If we find whitespace at the start of a segment it's probably
                    # from a fix, so leave it be. It otherwise shouldn't be there.
                    elif idx == 0:
                        continue
                    # Otherwise indents are allowed
                    elif non_meta_segs[idx - 1].is_type("newline", "whitespace"):
                        continue
                    # And whitespace before comments is.
                    # Whitespace before newlines isn't allowed but for now that's
                    # a different rule.
                    # (check there _is_ a next segment first to avoid index errors).
                    elif idx + 1 < len(non_meta_segs) and non_meta_segs[
                        idx + 1
                    ].is_type("comment", "newline"):
                        continue
                    # But otherwise it should be a single space.
                    elif seg.raw != " ":
                        violations.append(
                            LintResult(
                                anchor=seg,
                                fixes=[LintFix.replace(seg, [WhitespaceSegment()])],
                            )
                        )
        return violations

    def _skip_aliases(self, context: RuleContext, seg) -> bool:
        """Checks whether segment formatting was handled by _align_aliases."""
        segments = context.segment.segments
        if context.segment.is_type("select_clause_element"):
            segment_index = segments.index(seg)
            if len(segments) > segment_index + 1:
                prev_seg = segments[segment_index - 1]
                next_seg = segments[segment_index + 1]
                prev_is_col_expression = prev_seg.is_type(
                    "expression"
                ) or prev_seg.is_type("column_reference")
                next_is_alias = next_seg.is_type("alias_expression")
                if prev_is_col_expression and next_is_alias:
                    return True
        return False

    def _pad_unaligned_aliases(self, elements, max_len) -> List[LintFix]:
        """Finds expressions before aliases, and ensures they are padded to line up."""
        fixes = []
        # We loop over `select_clause_element`s again to pad each expression/apply fixes
        for element in elements:
            if element.is_type("select_clause_element"):
                for expression_segment in element.segments:
                    is_expression = expression_segment.is_type("expression")
                    is_column = expression_segment.is_type("column_reference")
                    if is_expression or is_column:
                        # Determine how much padding is needed for expression
                        padding = max_len - expression_segment.matched_length + 1
                        # Fetch existing WhiteSpace element following this expression
                        old_white_space = element.segments[
                            element.segments.index(expression_segment) + 1
                        ]
                        # Create new WhiteSpace element with correct padding
                        new_white_space = WhitespaceSegment(raw=" " * padding)
                        # If existing WhiteSpace isn't long enough, replace it
                        old_white_space_len = old_white_space.matched_length
                        new_white_space_len = new_white_space.matched_length
                        if old_white_space_len < new_white_space_len:
                            fixes.append(
                                LintFix.replace(old_white_space, [new_white_space]),
                            )
        return fixes

    def _align_aliases(self, context: RuleContext) -> Optional[LintResult]:
        """Loops through each select clause and pads all aliases evenly.

          * Sets max_len to the length of the longest expression using an Alias.
        Loops through all select_clause_elements in the select clause again
          * pads each expression with (max_len - len(expression)) whitespace.
        """
        children = FunctionalContext(context).segment.children()
        select_clause_elements = children.select(sp.is_type("select_clause_element"))
        max_len = 0
        # We loop over `select_clause_element`s to find length of the longest expression
        for element in select_clause_elements:
            for expression_segment in element.segments:
                is_expression = expression_segment.is_type("expression")
                is_column = expression_segment.is_type("column_reference")
                if is_expression or is_column:
                    max_len = max(max_len, expression_segment.matched_length)
        fixes = self._pad_unaligned_aliases(
            elements=select_clause_elements, max_len=max_len
        )
        if fixes:
            description = "Aliases are not aligned in the Select statement."
            return LintResult(
                anchor=fixes[0].anchor, fixes=fixes, description=description
            )

        return None
