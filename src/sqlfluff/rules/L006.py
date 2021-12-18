"""Implementation of Rule L006."""


from typing import Tuple, List

from sqlfluff.core.parser import WhitespaceSegment

from sqlfluff.core.rules.base import (
    BaseRule,
    LintResult,
    LintFix,
    RuleContext,
    EvalResultType,
)
from sqlfluff.core.rules.doc_decorators import document_fix_compatible


@document_fix_compatible
class Rule_L006(BaseRule):
    """Operators should be surrounded by a single whitespace.

    | **Anti-pattern**
    | In this example, there is a space missing space between the operator and 'b'.

    .. code-block:: sql

        SELECT
            a +b
        FROM foo


    | **Best practice**
    | Keep a single space.

    .. code-block:: sql

        SELECT
            a + b
        FROM foo
    """

    _target_elems: List[Tuple[str, str]] = [
        ("type", "binary_operator"),
        ("type", "comparison_operator"),
    ]

    @staticmethod
    def _missing_whitespace(seg, before=True):
        """Check whether we're missing whitespace given an adjoining segment."""
        # There is a segment
        if not seg:
            return False
        # And it's not whitespace
        if seg.is_whitespace:
            return False
        # And it's not an opening/closing bracket
        if seg.name.endswith("_bracket"):
            if seg.name.startswith("start_" if before else "end_"):
                return False
        if seg.is_meta:  # pragma: no cover
            if before:
                if seg.source_str.endswith(" ") or seg.source_str.endswith("\n"):
                    return False
            else:
                if seg.source_str.startswith(" ") or seg.source_str.startswith("\n"):
                    return False
        return True

    @staticmethod
    def _find_segment(idx, segments, before=True):
        """Go back or forward to find the next relevant segment."""
        step = -1 if before else 1
        j = idx + step
        while (j >= 0) if before else (j < len(segments)):
            # Don't trigger on indents, but placeholders are allowed.
            if segments[j].is_type("indent"):
                j += step
            else:
                return segments[j]
        return None

    def _eval(self, context: RuleContext) -> EvalResultType:
        """Operators should be surrounded by a single whitespace.

        Rewritten to assess direct children of a segment to make
        whitespace insertion more sensible.

        We only need to handle *missing* whitespace because excess
        whitespace is handled by L039.

        NOTE: We also allow bracket characters either side.
        """
        # Iterate through children of this segment looking for any of the
        # target types. We also check for whether any of the children start
        # or end with the targets.

        # We ignore any targets which start or finish this segment. They'll
        # be dealt with by the parent segment. That also means that we need
        # to have at least three children.

        if len(context.segment.segments) <= 2:
            return LintResult()

        violations = []

        for idx, sub_seg in enumerate(context.segment.segments):
            check_before = False
            check_after = False
            before_anchor = sub_seg
            after_anchor = sub_seg
            # Skip anything which is whitespace
            if sub_seg.is_whitespace:
                continue
            # Skip any non-code elements
            if not sub_seg.is_code:
                continue

            # Is it a target in itself?
            if self.matches_target_tuples(sub_seg, self._target_elems):
                self.logger.debug(
                    "Found Target [main] @%s: %r", sub_seg.pos_marker, sub_seg.raw
                )
                check_before = True
                check_after = True
            # Is it a compound segment ending or starting with the target?
            elif sub_seg.segments:
                # Get first and last raw segments.
                raw_list = list(sub_seg.get_raw_segments())
                if len(raw_list) > 1:
                    leading = raw_list[0]
                    trailing = raw_list[-1]
                    if self.matches_target_tuples(leading, self._target_elems):
                        before_anchor = leading
                        self.logger.debug(
                            "Found Target [leading] @%s: %r",
                            before_anchor.pos_marker,
                            before_anchor.raw,
                        )
                        check_before = True
                    if self.matches_target_tuples(trailing, self._target_elems):
                        after_anchor = trailing
                        self.logger.debug(
                            "Found Target [trailing] @%s: %r",
                            after_anchor.pos_marker,
                            after_anchor.raw,
                        )
                        check_after = True

            if check_before:
                prev_seg = self._find_segment(
                    idx, context.segment.segments, before=True
                )
                if self._missing_whitespace(prev_seg, before=True):
                    self.logger.debug(
                        "Missing Whitespace Before %r. Found %r instead.",
                        before_anchor.raw,
                        prev_seg.raw,
                    )
                    violations.append(
                        LintResult(
                            anchor=before_anchor,
                            description="Missing whitespace before {}".format(
                                before_anchor.raw[:10]
                            ),
                            fixes=[
                                LintFix.create_before(
                                    # NB the anchor here is always in the parent and not anchor
                                    anchor_segment=sub_seg,
                                    edit_segments=[WhitespaceSegment(raw=" ")],
                                )
                            ],
                        )
                    )

            if check_after:
                next_seg = self._find_segment(
                    idx, context.segment.segments, before=False
                )
                if self._missing_whitespace(next_seg, before=False):
                    self.logger.debug(
                        "Missing Whitespace After %r. Found %r instead.",
                        after_anchor.raw,
                        next_seg.raw,
                    )
                    violations.append(
                        LintResult(
                            anchor=after_anchor,
                            description="Missing whitespace after {}".format(
                                after_anchor.raw[-10:]
                            ),
                            fixes=[
                                LintFix.create_before(
                                    # NB the anchor here is always in the parent and not anchor
                                    anchor_segment=next_seg,
                                    edit_segments=[WhitespaceSegment(raw=" ")],
                                )
                            ],
                        )
                    )

        if violations:
            return violations

        return LintResult()
