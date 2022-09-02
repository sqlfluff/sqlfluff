"""Implementation of Rule L039."""
from typing import List, Optional

from sqlfluff.core.parser import WhitespaceSegment
from sqlfluff.core.rules import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import ParentOfSegmentCrawler
from sqlfluff.core.rules.doc_decorators import document_fix_compatible, document_groups


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
        # For the given segment, lint whitespace directly within it.
        violations = []
        # For some segments, strip all whitespace.
        if context.segment.is_type("object_reference", "comparison_operator"):
            for child_seg in context.segment.get_raw_segments():
                if child_seg.is_whitespace:
                    violations.append(
                        LintResult(
                            anchor=child_seg,
                            fixes=[LintFix.delete(child_seg)],
                        )
                    )
        # Otherwise handle normally
        else:
            non_meta_segs = [seg for seg in context.segment.segments if not seg.is_meta]
            for idx, seg in enumerate(non_meta_segs):
                if seg.is_type("whitespace"):
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
                        # TODO: This line lost coverage during #3808. Consider
                        # removing as part of whitespace consolidation.
                        continue  # pragma: no cover
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
                                fixes=[
                                    LintFix.replace(
                                        seg,
                                        [WhitespaceSegment()],
                                    )
                                ],
                            )
                        )
        return violations
