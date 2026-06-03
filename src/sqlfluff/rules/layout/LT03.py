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
        {"binary_operator", "comparison_operator", "assignment_operator"}
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
        idx = parent.segments.index(segment)
        base_position = line_position.split(":")[0]
        attached = "attached" in line_position
        has_newline_before = self._seek_newline(parent.segments, idx, dir=-1)
        has_newline_after = self._seek_newline(parent.segments, idx, dir=1)

        # Shortcut #1: Leading.
        if base_position == "leading":
            if attached:
                # leading:attached: shortcut when mid-line or truly leading.
                # Must reflow when trailing or on its own line (no newline after
                # means it cannot be standalone or trailing).
                return not has_newline_after
            # Standard: OK unless trailing (no newline before, but newline after).
            return has_newline_before or not has_newline_after

        # Shortcut #2: Trailing.
        elif base_position == "trailing":
            if attached:
                # trailing:attached: shortcut when mid-line or truly trailing.
                # Must reflow when leading or on its own line (no newline before
                # means it cannot be standalone or leading).
                return not has_newline_before
            # Standard: OK unless leading (no newline after, but newline before).
            return has_newline_after or not has_newline_before

        return False

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
        # detection.
        if context.segment.is_type("comparison_operator"):
            comparison_positioning = context.config.get(
                "line_position", ["layout", "type", "comparison_operator"]
            )
            if self._check_trail_lead_shortcut(
                context.segment, context.parent_stack[-1], comparison_positioning
            ):
                return [LintResult()]
        elif context.segment.is_type("binary_operator"):
            binary_positioning = context.config.get(
                "line_position", ["layout", "type", "binary_operator"]
            )
            if self._check_trail_lead_shortcut(
                context.segment, context.parent_stack[-1], binary_positioning
            ):
                return [LintResult()]
        elif context.segment.is_type("assignment_operator"):
            assignment_positioning = context.config.get(
                "line_position", ["layout", "type", "assignment_operator"]
            )
            if self._check_trail_lead_shortcut(
                context.segment, context.parent_stack[-1], assignment_positioning
            ):
                return [LintResult()]

        return (
            ReflowSequence.from_around_target(
                context.segment,
                root_segment=context.parent_stack[0],
                config=context.config,
            )
            .rebreak()
            .get_results()
        )
