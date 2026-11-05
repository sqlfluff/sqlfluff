"""Implementation of Rule ST12."""

# Standard library imports intentionally minimal.

from sqlfluff.core.parser import BaseSegment
from sqlfluff.core.rules import (
    BaseRule,
    EvalResultType,
    LintFix,
    LintResult,
    RuleContext,
)
from sqlfluff.core.rules.crawlers import RootOnlyCrawler


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
    crawl_behaviour = RootOnlyCrawler()
    is_fix_compatible = True

    def _eval(self, context: RuleContext) -> EvalResultType:
        """Detect consecutive semicolons and provide fixes.

        Inspect the current token order, since earlier fixes may reorder
        segments without changing their original source positions.
        """
        if not context.segment.is_type("file"):  # pragma: no cover
            return None

        runs: list[list[BaseSegment]] = []
        run: list[BaseSegment] = []
        for segment in context.segment.raw_segments:
            if segment.is_meta or not segment.raw or segment.raw.isspace():
                continue
            if segment.is_type("statement_terminator") and segment.pos_marker:
                run.append(segment)
            else:
                if len(run) > 1:
                    runs.append(run)
                run = []
        if len(run) > 1:
            runs.append(run)

        results = [
            LintResult(
                anchor=run[0],
                fixes=[LintFix.delete(segment) for segment in run[1:]],
                description=(f"Consecutive semicolons detected (count {len(run)})."),
            )
            for run in runs
        ]

        # In templated files, collapse duplicate violations that map to
        # the same source slice to avoid repeated reports.
        if results and context.templated_file is not None:
            seen_keys = set()
            deduped_results: list[LintResult] = []
            for res in results:
                # Anchors from `terms` have position markers; assert the invariant.
                assert res.anchor is not None
                assert res.anchor.pos_marker is not None
                pm = res.anchor.pos_marker
                src_slice = pm.source_slice
                key = (
                    (
                        src_slice.start
                        if src_slice is not None
                        else pm.templated_slice.start
                    ),
                    res.anchor.raw,
                )
                if key in seen_keys:
                    continue
                seen_keys.add(key)
                deduped_results.append(res)
            results = deduped_results

        return results or None
