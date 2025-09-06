"""Implementation of Rule ST12."""

import re

from sqlfluff.core.rules import BaseRule, EvalResultType, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler

CONSECUTIVE_SEMICOLONS_REGEX = re.compile(r";(?:\s*;){1,}")


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
    groups = ("all", "structure")
    crawl_behaviour = SegmentSeekerCrawler({"file"})
    is_fix_compatible = False

    def _eval(self, context: RuleContext) -> EvalResultType:
        # Only operate once at file segment root.
        if not context.segment.is_type("file"):  # pragma: no cover
            return None

        raw = context.segment.raw
        results: list[LintResult] = []
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
