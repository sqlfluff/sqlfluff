"""Implementation of Rule LT03."""

from collections.abc import Sequence

from sqlfluff.core.parser import BaseSegment
from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.utils.reflow import ReflowSequence


class Rule_LT03(BaseRule):
    """Operators should follow a standard for being before/after newlines.

    The configuration for whether operators should be ``trailing`` or
    ``leading`` is part of :ref:`layoutconfig`. The default configuration is:

    .. code-block:: cfg

        [sqlfluff:layout:type:binary_operator]
        line_position = leading

        [sqlfluff:layout:type:comparison_operator]
        line_position = leading

    **Anti-pattern**

    In this example, if ``line_position = leading`` (or unspecified, as is the
    default), then the operator ``+`` should not be at the end of the second line.

    .. code-block:: sql

        SELECT
            a +
            b
        FROM foo


    **Best practice**

    If ``line_position = leading`` (or unspecified, as this is the default),
    place the operator after the newline.

    .. code-block:: sql

        SELECT
            a
            + b
        FROM foo

    If ``line_position = trailing``, place the operator before the newline.

    .. code-block:: sql

        SELECT
            a +
            b
        FROM foo
    """

    name = "layout.operators"
    aliases = ("L007",)
    groups = ("all", "layout")
    crawl_behaviour = SegmentSeekerCrawler(
        {
            "binary_operator",
            "comparison_operator",
            "assignment_operator",
            "pipe_operator",
        }
    )
    is_fix_compatible = True

    def _seek_newline(
        self, segments: Sequence[BaseSegment], idx: int, dir: int
    ) -> bool:
        """Seek in a direction, looking for newlines.

        Args:
            segments: A sequence of segments to seek within.
            idx: The index of the "current" segment.
            dir: The direction to seek in (+1 for forward, -1 for backward)
        """
        assert dir in (1, -1)
        for segment in segments[idx + dir :: dir]:
            if segment.is_type("newline"):
                # It's definitely leading. No problems.
                self.logger.debug(
                    "Shortcut (dir = %s) OK. Found newline: %s", dir, segment
                )
                return True
            elif not segment.is_type("whitespace", "indent", "comment"):
                # We found something before it which suggests it's not leading.
                # We should run the full reflow routine to check.
                break
        return False

    def _check_trail_lead_shortcut(
        self, segment: BaseSegment, parent: BaseSegment, line_position: str
    ) -> bool:
        """Check to see whether we should pass the rule and shortcut.

        Args:
            segment: The target segment.
            parent: The parent segment (must contain `segment`).
            line_position: The `line_position` config for the segment.
        """
        base_position = line_position.split(":")[0]
        if base_position not in ("leading", "trailing"):
            return False
        attached = "attached" in line_position
        strict = line_position.endswith("strict")

        # `leading`/`trailing` are mirror images, so resolve the sides relative
        # to the desired position and share the logic.
        idx = parent.segments.index(segment)
        has_newline_before = self._seek_newline(parent.segments, idx, dir=-1)
        has_newline_after = self._seek_newline(parent.segments, idx, dir=1)
        if base_position == "leading":
            in_position, opposite = has_newline_before, has_newline_after
        else:
            in_position, opposite = has_newline_after, has_newline_before

        if attached:
            # `attached` also forbids floating alone on its own line.
            if opposite:
                return False
            return in_position or not strict
        # OK unless mispositioned; `strict` also rejects mid-line.
        return in_position or (not strict and not opposite)

    def _eval(self, context: RuleContext) -> list[LintResult]:
        """Operators should follow a standard for being before/after newlines.

        For the fixing routines we delegate to the reflow utils. However
        for performance reasons we have some initial shortcuts to quickly
        identify situations which are _ok_ to avoid the overhead of the
        full reflow path.
        """
        # NOTE: These shortcuts assume that any newlines will be direct
        # siblings of the operator in question. This isn't _always_ the case
        # but is true often enough to have meaningful upside from early
        # detection. `pipe_operator` has no shortcut and falls through to reflow.
        for operator_type in (
            "comparison_operator",
            "binary_operator",
            "assignment_operator",
        ):
            if context.segment.is_type(operator_type):
                positioning = context.config.get(
                    "line_position", ["layout", "type", operator_type]
                )
                if self._check_trail_lead_shortcut(
                    context.segment, context.parent_stack[-1], positioning
                ):
                    return [LintResult()]
                break

        return (
            ReflowSequence.from_around_target(
                context.segment,
                root_segment=context.parent_stack[0],
                config=context.config,
            )
            .rebreak()
            .get_results()
        )
