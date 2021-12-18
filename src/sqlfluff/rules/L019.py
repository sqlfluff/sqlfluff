"""Implementation of Rule L019."""

from typing import Any, Dict, Optional, Tuple

from sqlfluff.core.parser import RawSegment, WhitespaceSegment
from sqlfluff.core.rules.base import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.doc_decorators import (
    document_fix_compatible,
    document_configuration,
)


@document_fix_compatible
@document_configuration
class Rule_L019(BaseRule):
    """Leading/Trailing comma enforcement.

    | **Anti-pattern**
    | There is a mixture of leading and trailing commas.

    .. code-block:: sql

        SELECT
            a
            , b,
            c
        FROM foo

    | **Best practice**
    | By default sqlfluff prefers trailing commas, however it
    | is configurable for leading commas. Whichever option you chose
    | it does expect you to be consistent.

    .. code-block:: sql

        SELECT
            a,
            b,
            c
        FROM foo

        -- Alternatively, set the configuration file to 'leading'
        -- and then the following would be acceptable:

        SELECT
            a
            , b
            , c
        FROM foo


    """

    _works_on_unparsable = False
    config_keywords = ["comma_style"]

    @staticmethod
    def _last_comment_seg(raw_stack):
        """Trace the raw stack back to the most recent comment segment.

        A return value of `None` indicates no code segments preceding the current position.
        """
        for segment in raw_stack[::-1]:
            if segment.is_comment:
                return segment
        return None

    @staticmethod
    def _last_code_seg(raw_stack: Tuple[RawSegment, ...]) -> Optional[RawSegment]:
        """Trace the raw stack back to the most recent code segment.

        A return value of `None` indicates no code segments preceding the current position.
        """
        for segment in raw_stack[::-1]:
            if segment.is_code or segment.is_type("newline"):
                return segment
        return None

    @staticmethod
    def _get_following_seg(
        raw_stack: Tuple[RawSegment, ...], segment: RawSegment
    ) -> RawSegment:
        """Given a segment in raw_stack, return the segment following."""
        idx = raw_stack.index(segment)
        if idx < len(raw_stack):
            return raw_stack[idx + 1]
        raise ValueError("No following segment available")  # pragma: no cover

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Enforce comma placement.

        For leading commas we're looking for trailing commas, so
        we look for newline segments. For trailing commas we're
        looking for leading commas, so we look for the comma itself.

        We also want to handle proper whitespace removal/addition. We remove
        any trailing whitespace after the leading comma, when converting a
        leading comma to a trailing comma. We add whitespace after the leading
        comma when converting a trailing comma to a leading comma.
        """
        # Config type hints
        self.comma_style: str

        if not context.memory:
            memory: Dict[str, Any] = {
                # Trailing comma keys
                #
                # Do we have a fix in place for removing a leading
                # comma violation, and inserting a new trailing comma?
                "insert_trailing_comma": False,
                # A list of whitespace segments that come after a
                # leading comma violation, to be removed during fixing.
                "whitespace_deletions": None,
                # The leading comma violation segment to be removed during fixing
                "last_leading_comma_seg": None,
                # The newline segment where we're going to insert our new trailing
                # comma during fixing
                "anchor_for_new_trailing_comma_seg": None,
                #
                # Leading comma keys
                #
                # Do we have a fix in place for removing a trailing
                # comma violation, and inserting a new leading comma?
                "insert_leading_comma": False,
                # The trailing comma violation segment to be removed during fixing
                "last_trailing_comma_segment": None,
            }
        else:
            memory = context.memory

        if self.comma_style == "trailing":
            # A comma preceded by a new line == a leading comma
            if context.segment.is_type("comma"):
                last_seg = self._last_code_seg(context.raw_stack)
                if last_seg and last_seg.is_type("newline"):
                    # Recorded where the fix should be applied
                    memory["last_leading_comma_seg"] = context.segment
                    last_comment_seg = self._last_comment_seg(context.raw_stack)
                    inline_comment = (
                        last_comment_seg.pos_marker.line_no
                        == last_seg.pos_marker.line_no
                        if last_comment_seg
                        else False
                    )
                    # If we have a comment right before the newline, then anchor
                    # the fix at the comment instead
                    memory["anchor_for_new_trailing_comma_seg"] = (
                        last_seg if not inline_comment else last_comment_seg
                    )
                    # Trigger fix routine
                    memory["insert_trailing_comma"] = True
                    memory["whitespace_deletions"] = []
                    return LintResult(memory=memory)
            # Have we found a leading comma violation?
            if memory["insert_trailing_comma"]:
                # Search for trailing whitespace to delete after the leading
                # comma violation
                if context.segment.is_type("whitespace"):
                    memory["whitespace_deletions"] += [context.segment]
                    return LintResult(memory=memory)
                else:
                    # We've run out of whitespace to delete, time to fix
                    last_leading_comma_seg = memory["last_leading_comma_seg"]
                    # Scan backwards to find the last code segment, skipping
                    # over lines that are either entirely blank or just a
                    # comment. We want to place the comma immediately after it.
                    last_code_seg = None
                    while last_code_seg is None or last_code_seg.is_type("newline"):
                        last_code_seg = self._last_code_seg(
                            context.raw_stack[
                                : context.raw_stack.index(
                                    last_code_seg
                                    if last_code_seg
                                    else memory["last_leading_comma_seg"]
                                )
                            ]
                        )
                    return LintResult(
                        anchor=last_leading_comma_seg,
                        description="Found leading comma. Expected only trailing.",
                        fixes=[
                            LintFix.delete(last_leading_comma_seg),
                            *[
                                LintFix.delete(d)
                                for d in memory["whitespace_deletions"]
                            ],
                            LintFix.create_before(
                                anchor_segment=self._get_following_seg(
                                    context.raw_stack, last_code_seg
                                ),
                                edit_segments=[last_leading_comma_seg],
                            ),
                        ],
                    )

        elif self.comma_style == "leading":
            # A new line preceded by a comma == a trailing comma
            if context.segment.is_type("newline"):
                last_seg = self._last_code_seg(context.raw_stack)
                # no code precedes the current position: no issue
                if last_seg is None:
                    return None
                if last_seg.is_type("comma"):
                    # Trigger fix routine
                    memory["insert_leading_comma"] = True
                    # Record where the fix should be applied
                    memory["last_trailing_comma_segment"] = last_seg
                    return LintResult(memory=memory)
            # Have we found a trailing comma violation?
            if memory["insert_leading_comma"]:
                # Only insert the comma here if this isn't a comment/whitespace segment
                if context.segment.is_code:
                    last_comma_seg = memory["last_trailing_comma_segment"]
                    # Create whitespace to insert after the new leading comma
                    new_whitespace_seg = WhitespaceSegment()
                    return LintResult(
                        anchor=last_comma_seg,
                        description="Found trailing comma. Expected only leading.",
                        fixes=[
                            LintFix.delete(last_comma_seg),
                            LintFix.create_before(
                                anchor_segment=context.segment,
                                edit_segments=[last_comma_seg, new_whitespace_seg],
                            ),
                        ],
                    )
        # Otherwise, no issue
        return None
