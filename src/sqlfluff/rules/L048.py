"""Implementation of Rule L048."""

from typing import Tuple, List

from sqlfluff.core.parser import BaseSegment, WhitespaceSegment

from sqlfluff.core.rules.base import (
    LintResult,
    LintFix,
    RuleContext,
    EvalResultType,
)
from sqlfluff.core.rules.doc_decorators import document_fix_compatible

from sqlfluff.rules.L006 import Rule_L006


@document_fix_compatible
class Rule_L048(Rule_L006):
    """Quoted literals should be surrounded by a single whitespace.

    **Anti-pattern**

    In this example, there is a space missing between the string
    ``'foo'`` and the keyword ``AS``.

    .. code-block:: sql

        SELECT
            'foo'AS bar
        FROM foo


    **Best practice**

    Keep a single space.

    .. code-block:: sql

        SELECT
            'foo' AS bar
        FROM foo
    """

    _require_three_children: bool = False

    _target_elems: List[Tuple[str, str]] = [
        ("name", "quoted_literal"),
    ]

    @staticmethod
    def _missing_whitespace(seg: BaseSegment, before=True) -> bool:
        """Check whether we're missing whitespace given an adjoining segment.

        This avoids flagging for commas after quoted strings.
        https://github.com/sqlfluff/sqlfluff/issues/943
        """
        simple_res = Rule_L006._missing_whitespace(seg, before=before)
        if (
            not before
            and seg
            and (
                seg.is_type("comma", "statement_terminator")
                or (
                    seg.is_type("cast_expression") and seg.get_child("casting_operator")
                )
            )
        ):
            return False
        return simple_res

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

        if self._require_three_children and len(context.segment.segments) <= 2:
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
                # NB: Should not check for whitespaces inside of
                # Interval Literals for SparkSQL dialect
                # https://spark.apache.org/docs/latest/sql-ref-literals.html#interval-literal
                if context.dialect.name in ["sparksql"]:
                    possible_interval_segment = self._find_segment(
                        idx, context.segment.segments, before=True, step=-3
                    )
                    if (
                        possible_interval_segment is not None
                        and possible_interval_segment.raw.upper() == "INTERVAL"
                    ):
                        continue
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
                                before_anchor.raw
                            ),
                            fixes=[
                                LintFix.create_before(
                                    # NB the anchor here is always in the parent and not
                                    # anchor
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
                                after_anchor.raw
                            ),
                            fixes=[
                                LintFix.create_before(
                                    # NB the anchor here is always in the parent and not
                                    # anchor
                                    anchor_segment=next_seg,
                                    edit_segments=[WhitespaceSegment(raw=" ")],
                                )
                            ],
                        )
                    )

        if violations:
            return violations

        return LintResult()
