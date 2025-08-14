"""Implementation of Rule ST12."""

from sqlfluff.core.rules import (
    BaseRule,
    EvalResultType,
    LintFix,
    LintResult,
    RuleContext,
)
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler


class Rule_ST12(BaseRule):
    """Consecutive semicolons detected.

    This rule flags runs of two or more semicolons (optionally with intervening
    whitespace/newlines) which usually indicate an empty statement or an
    accidental duplicate terminator.

    **Anti-pattern**

    .. code-block:: sql
       :force:

        SELECT 1;;
        ;;SELECT 2;

    **Best practice**

    Collapse duplicate semicolons unless intentionally separating batches.

    .. code-block:: sql
       :force:

        SELECT 1;
        SELECT 2;
    """

    name = "structure.consecutive_semicolons"
    aliases: tuple[str, ...] = ()
    groups: tuple[str, ...] = ("all", "structure")
    crawl_behaviour = SegmentSeekerCrawler({"file"})
    is_fix_compatible = True

    def _eval(self, context: RuleContext) -> EvalResultType:
        """Find consecutive semicolons and provide fixes.

        1. Operate only at file segment root for comprehensive view
        2. Collect all statement terminators in source order
        3. Identify runs of consecutive semicolons (separated only by whitespace)
        4. For each run >= 2 semicolons, delete all but the first one
        """
        # Only operate once at file segment root.
        if not context.segment.is_type("file"):  # pragma: no cover
            return None

        file_seg = context.segment

        # Collect all statement terminators in source order.
        terms = [
            t for t in file_seg.recursive_crawl("statement_terminator") if t.pos_marker
        ]
        if not terms:
            return None

        terms.sort(
            key=lambda s: s.pos_marker.source_slice.start  # type: ignore[union-attr]
        )

        # Pre-fetch raw segments for whitespace-only checks between terminators.
        raw_segs = file_seg.raw_segments

        def whitespace_only_between(a, b) -> bool:
            """Return True if only whitespace exists between two terminators.

            We intentionally do NOT treat comments as whitespace; if comments
            or any other non-whitespace raw tokens appear between semicolons,
            this is not considered a consecutive run for the purposes of ST12.
            """
            assert a.pos_marker and b.pos_marker
            lo = a.pos_marker.source_slice.stop
            hi = b.pos_marker.source_slice.start
            if lo >= hi:
                return True
            for rs in raw_segs:
                assert rs.pos_marker
                s = rs.pos_marker.source_slice.start
                e = rs.pos_marker.source_slice.stop
                # Consider raw segments strictly between the two.
                if s >= lo and e <= hi:
                    if not rs.is_whitespace:
                        return False
            return True

        results: list[LintResult] = []
        i = 0
        n = len(terms)
        while i < n - 1:
            j = i
            # Grow the run while only whitespace is between adjacent semicolons.
            while j + 1 < n and whitespace_only_between(terms[j], terms[j + 1]):
                j += 1

            run_len = j - i + 1
            if run_len >= 2:
                anchor = terms[i]
                to_delete = terms[i + 1 : j + 1]
                fixes = [LintFix.delete(seg) for seg in to_delete]
                results.append(
                    LintResult(
                        anchor=anchor,
                        fixes=fixes,
                        description=(
                            f"Consecutive semicolons detected (count {run_len})."
                        ),
                    )
                )
                i = j + 1
            else:
                i += 1

        return results or None
