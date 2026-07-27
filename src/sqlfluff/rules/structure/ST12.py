"""Implementation of Rule ST12."""

# Standard library imports intentionally minimal.

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

        Operates at the file root, builds a cached bounded prefix of
        non-whitespace characters, then finds adjacent terminators that
        are separated only by whitespace.
        """
        if not context.segment.is_type("file"):  # pragma: no cover
            return None

        file_seg = context.segment

        def _pos_start(seg):
            m = seg.pos_marker
            assert m
            # Use templated positions when a templated file exists.
            # Otherwise use source positions.
            return (
                m.templated_slice.start
                if context.templated_file is not None
                else m.source_slice.start
            )

        def _pos_stop(seg):
            m = seg.pos_marker
            assert m
            return (
                m.templated_slice.stop
                if context.templated_file is not None
                else m.source_slice.stop
            )

        # Collect semicolon terminators assuming they are in order.
        terms = [
            t for t in file_seg.recursive_crawl("statement_terminator") if t.pos_marker
        ]
        if len(terms) <= 1:
            return None

        # Calculate the bounding window across all terminators. Using the
        # min and max across all starts/stops avoids relying on their order
        # in the parse tree and eliminates the need for a defensive guard.
        starts = [_pos_start(t) for t in terms]
        stops = [_pos_stop(t) for t in terms]
        min_start = min(starts)
        max_stop = max(stops)

        # Prefer the templated view when available.
        # Otherwise fall back to the raw file text.
        s = (
            context.templated_file.templated_str
            if context.templated_file is not None
            else file_seg.raw
        )
        sub = s[min_start:max_stop]
        # prefix[i] counts non-whitespace characters in sub[:i]
        prefix = [0] * (len(sub) + 1)
        acc = 0
        _isspace = str.isspace
        for i, ch in enumerate(sub):
            if not _isspace(ch):
                acc += 1
            prefix[i + 1] = acc

        # Is the range between two segments only whitespace?
        def _whitespace_only_between(a, b) -> bool:
            lo = _pos_stop(a)
            hi = _pos_start(b)
            lo_rel = lo - min_start
            hi_rel = hi - min_start
            # If the end is at or after the start there are no characters
            # between them, so consider that whitespace-only (i.e. empty).
            if hi_rel <= lo_rel:
                return True
            # Relative indices should be within the prefix range.
            # Compute the difference.
            return (prefix[hi_rel] - prefix[lo_rel]) == 0

        # Find runs of adjacent semicolons separated only by whitespace
        results: list[LintResult] = []
        i = 0
        n = len(terms)
        while i < n - 1:
            j = i
            while j + 1 < n and _whitespace_only_between(terms[j], terms[j + 1]):
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
        # Run detection complete

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
