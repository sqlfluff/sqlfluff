"""Implementation of Rule L016."""

from typing import List

from sqlfluff.core.rules import LintResult, RuleContext
from sqlfluff.core.rules.base import BaseRule
from sqlfluff.core.rules.crawlers import RootOnlyCrawler
from sqlfluff.core.rules.doc_decorators import (
    document_configuration,
    document_fix_compatible,
    document_groups,
)

from sqlfluff.utils.reflow.sequence import ReflowSequence


@document_groups
@document_fix_compatible
@document_configuration
class Rule_L016(BaseRule):
    """Line is too long."""

    groups = ("all", "core")
    crawl_behaviour = RootOnlyCrawler()
    _adjust_anchors = True
    _check_docstring = False

    config_keywords = [
        "ignore_comment_lines",
        "ignore_comment_clauses",
    ]

    def _eval(self, context: RuleContext) -> List[LintResult]:
        """Line is too long."""
        self.ignore_comment_lines: bool
        self.ignore_comment_clauses: bool
        # Reflow and generate fixes.
        results = (
            ReflowSequence.from_root(context.segment, context.config)
            .reindent()
            .get_results()
        )
        # Filter only to results which start with "Line is too long".
        results = [
            res for res in results if res.description.startswith("Line is too long")
        ]

        # Ignore any comment line if appropriate.
        if self.ignore_comment_lines:
            results = [res for res in results if not res.anchor.is_type("comment")]

        # Ignore any comment clauses if present.
        if self.ignore_comment_clauses:
            raw_segments = context.segment.raw_segments
            for res in results[:]:
                # The anchor should be the first raw on the line. Work forward
                # until we're not on the line. Check if any have a parent which
                # is a comment_clause.
                raw_idx = raw_segments.index(res.anchor)
                for idx, seg in enumerate(raw_segments, raw_idx):
                    path = context.segment.path_to(seg)
                    if (
                        seg.pos_marker.working_line_no
                        != res.anchor.pos_marker.working_line_no
                    ):
                        # We've gone past the end of the line. Stop looking.
                        break
                    # Is it in a comment clause?
                    elif any(ps.segment.is_type("comment_clause") for ps in path):
                        # It IS! Ok, purge this result from results.
                        results.remove(res)
                        break

        return results
