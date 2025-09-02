"""Implementation of Rule TQ02: Warn on consecutive semicolons in T-SQL.

This rule flags runs of two or more semicolons (optionally with intervening
whitespace/newlines) which usually indicate an empty statement or an
accidental duplicate terminator. While T-SQL permits extra semicolons,
surfacing them helps users clean up scripts or diagnose parsing issues.

Currently this rule ONLY emits a warning (no automatic fix). Replacing partial
raw slices at file-root safely needs more invasive changes. A future iteration
could implement targeted fixes by reconstructing affected segments.
"""

from __future__ import annotations

import re

from sqlfluff.core.rules import BaseRule, EvalResultType, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler

# Matches two or more semicolons where only whitespace (incl. newlines) may
# appear between them. Examples matched: ';;', '; ;', ';; ;', ';\n;', ';;\n;'
# and longer runs like '; ; ;' or ';;  ;'. A single semicolon or runs with
# non-whitespace characters between semicolons (e.g. ';x;') are not matched.
CONSECUTIVE_SEMICOLONS_REGEX = re.compile(r";(?:\s*;){1,}")


class Rule_TQ02(BaseRule):
    """Consecutive semicolons detected.

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

    name = "tsql.consecutive_semicolons"
    # Keep only the canonical name; avoid alias collision with code grouping.
    aliases: tuple[str, ...] = tuple()
    groups = ("all", "tsql")
    # Seek only the root file segment so we run once per file.
    crawl_behaviour = SegmentSeekerCrawler({"file"})

    def _eval(self, context: RuleContext) -> EvalResultType:
        # Only apply to tsql dialect.
        if context.dialect.name != "tsql":  # pragma: no cover
            return None
        # Only operate once at file segment root.
        if not context.segment.is_type("file"):  # pragma: no cover
            return None

        raw = context.segment.raw
        results: list[LintResult] = []
        # Iterate with non-overlapping logic by advancing index manually
        idx = 0
        while True:
            m = CONSECUTIVE_SEMICOLONS_REGEX.search(raw, idx)
            if not m:
                break
            span_raw = m.group(0)
            count = span_raw.count(";")
            start = m.start()
            line = raw.count("\n", 0, start) + 1
            last_newline = raw.rfind("\n", 0, start)
            if last_newline == -1:
                col = start + 1
            else:
                col = start - last_newline
            description = (
                "Consecutive semicolons detected (count "
                f"{count}). At line {line}, column {col}."
            )
            # Anchor: attempt to find the first raw semicolon segment at this position.
            anchor_seg = context.segment
            cumulative = 0
            for seg in context.segment.get_raw_segments():
                seg_len = len(seg.raw)
                if cumulative <= start < cumulative + seg_len:
                    if seg.raw.startswith(";"):
                        anchor_seg = seg
                    break
                cumulative += seg_len
            results.append(
                LintResult(
                    anchor=anchor_seg,
                    description=description,
                )
            )
            idx = m.end()
        return results or None
