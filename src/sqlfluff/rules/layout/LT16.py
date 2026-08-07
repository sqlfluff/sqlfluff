"""Implementation of Rule LT16."""

from typing import Optional

from sqlfluff.core.parser import BaseSegment, NewlineSegment
from sqlfluff.core.rules import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.utils.functional import Segments, sp

# The clauses handled by this rule, mapped from the config keyword which
# controls them to the segment types which they're parsed as. NOTE: BigQuery's
# `GROUP AND ORDER BY` is a `GROUP BY` with an extra modifier, so it's covered
# by the group by policy.
CLAUSE_POLICIES = {
    "group_by_policy": ("groupby_clause", "group_and_orderby_clause"),
    "order_by_policy": ("orderby_clause",),
}

# Within these segments, the clause is part of a larger inline expression
# (e.g. the `ORDER BY` of a window function or an aggregate function), and
# so shouldn't be split over several lines.
INLINE_CONTEXTS = (
    "window_specification",
    "aggregate_order_by",
    "withingroup_clause",
)


class Rule_LT16(BaseRule):
    """List targets should be on a new line unless there is only one target.

    This is the equivalent of :sqlfluff:ref:`LT09` for the other lists of
    targets in a statement, so that they're all laid out consistently.

    .. note::
       By default this applies to both ``GROUP BY`` and ``ORDER BY``. Either
       can be relaxed by setting the relevant policy to ``same_line``, e.g.
       ``order_by_policy = same_line``. BigQuery's ``GROUP AND ORDER BY``
       follows ``group_by_policy``.

    .. note::
       ``ORDER BY`` clauses which are part of a larger expression (e.g. within
       a window function, an aggregate function or a ``WITHIN GROUP`` clause)
       are never affected by this rule.

    **Anti-pattern**

    Multiple targets on the same line.

    .. code-block:: sql

        select
            a,
            b
        from fct
        group by a, b;

    **Best practice**

    Multiple targets each on their own line.

    .. code-block:: sql

        select
            a,
            b
        from fct
        group by
            a,
            b;

        -- A single target may still share a line with the keyword.

        select
            a,
            b
        from fct
        group by a;

    """

    name = "layout.list_targets"
    groups = ("all", "layout")
    config_keywords = ["group_by_policy", "order_by_policy"]
    crawl_behaviour = SegmentSeekerCrawler(
        {seg_type for types in CLAUSE_POLICIES.values() for seg_type in types}
    )
    is_fix_compatible = True

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        self.group_by_policy: str
        self.order_by_policy: str
        if not self._is_enabled(context.segment):
            return None
        # Skip clauses which are only part of a larger inline expression.
        if any(parent.is_type(*INLINE_CONTEXTS) for parent in context.parent_stack):
            return None

        fixes: list[LintFix] = []
        segment = context.segment
        children = segment.segments
        clause_raws = Segments(segment).raw_segments
        for target_idx in self._list_target_idxs(segment):
            target = children[target_idx]
            target_initial_code = (
                Segments(target).raw_segments.first(sp.is_code()).get()
            )
            assert target_initial_code
            # Find where the previous target ended. We ignore commas here so
            # that leading comma layouts aren't broken up unnecessarily.
            previous_code = (
                clause_raws.select(
                    select_if=sp.and_(sp.is_code(), sp.not_(sp.raw_is(","))),
                    stop_seg=target_initial_code,
                )
                .last()
                .get()
            )
            assert previous_code
            assert previous_code.pos_marker and target_initial_code.pos_marker
            # If this target doesn't start on the line that the previous one
            # (or the keyword) ended on, then there's nothing to do.
            if (
                previous_code.pos_marker.working_line_no
                != target_initial_code.pos_marker.working_line_no
            ):
                continue

            fixes.extend(
                LintFix.delete(ws)
                for ws in self._preceding_whitespace(children, target_idx)
            )
            fixes.append(LintFix.create_before(target, [NewlineSegment()]))

        if fixes:
            return LintResult(anchor=segment, fixes=fixes)
        return None

    def _is_enabled(self, segment: BaseSegment) -> bool:
        """Is this rule configured to apply to this clause?"""
        return any(
            segment.is_type(*seg_types) and getattr(self, policy) == "new_line"
            for policy, seg_types in CLAUSE_POLICIES.items()
        )

    @staticmethod
    def _list_target_idxs(segment: BaseSegment) -> list[int]:
        """Get the indices of the children which start each list target.

        Returns an empty list if there aren't multiple targets to lay out,
        e.g. for ``GROUP BY ALL`` or a single ``ORDER BY`` target. Note that
        only the commas at the top level of the clause count, so the contents
        of e.g. ``GROUP BY ROLLUP(a, b)`` are left alone.
        """
        children = segment.segments
        comma_idxs = [idx for idx, seg in enumerate(children) if seg.is_type("comma")]
        if not comma_idxs:
            return []

        target_idxs = []
        # The first target starts after the introducing keywords (e.g. the
        # `GROUP BY` of `GROUP BY a, b`, or the `ORDER BY ALL` of some
        # dialects). Any other keywords are part of a target.
        for idx, seg in enumerate(children):
            if seg.is_code and not seg.is_type("keyword"):
                target_idxs.append(idx)
                break
        # Every other target starts at the first code after a comma.
        for comma_idx in comma_idxs:
            for idx in range(comma_idx + 1, len(children)):
                if children[idx].is_code:
                    target_idxs.append(idx)
                    break
        return sorted(set(target_idxs))

    @staticmethod
    def _preceding_whitespace(
        children: tuple[BaseSegment, ...], target_idx: int
    ) -> list[BaseSegment]:
        """Get the whitespace to remove before a target we're moving."""
        whitespace = []
        for seg in reversed(children[:target_idx]):
            if seg.is_type("whitespace"):
                whitespace.append(seg)
            elif not (seg.is_type("comma") or seg.is_meta):
                # Anything else (including comments) means we've reached the
                # end of the previous target.
                break
        return whitespace
