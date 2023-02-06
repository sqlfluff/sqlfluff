"""Implementation of Rule L016."""

from typing import List, cast

from sqlfluff.core.parser.segments import TemplateSegment

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
    targets_templated = True
    template_safe_fixes = True
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

        # Filter only to results which with the long line flag,
        # or to other indent ones on the same line as those.
        fixable_long_lines = set(
            res.anchor.pos_marker.working_line_no
            for res in results
            if res.source == "reflow.long_line" and res.fixes
        )
        unfixable_long_lines = set(
            res.anchor.pos_marker.working_line_no
            for res in results
            if res.source == "reflow.long_line" and not res.fixes
        )
        results = [
            res
            for res in results
            # Allow other fixes on lines which are too long AND FIXABLE.
            if res.anchor.pos_marker.working_line_no in fixable_long_lines
            # OR if it's not fixable, don't correct indents.
            or (
                res.anchor.pos_marker.working_line_no in unfixable_long_lines
                and res.source != "reflow.indent.existing"
            )
        ]

        # Ignore any comment line if appropriate.
        if self.ignore_comment_lines:
            raw_segments = context.segment.raw_segments
            for res in results[:]:
                # First handle the easy case that the anchor (i.e. the start
                # of the line is a comment).
                if res.anchor.is_type("comment"):
                    self.logger.debug(
                        "Purging result on long line starting with comment: %s",
                        res.anchor.pos_marker.working_line_no,
                    )
                    results.remove(res)
                    continue
                # Then look for comments on the rest of the line:
                raw_idx = raw_segments.index(res.anchor)
                for seg in raw_segments[raw_idx:]:
                    if (
                        seg.pos_marker.working_line_no
                        != res.anchor.pos_marker.working_line_no
                    ):
                        # We've gone past the end of the line. Stop looking.
                        break  # pragma: no cover
                    # Is it a comment?
                    if seg.is_type("comment"):
                        self.logger.debug(
                            "Purging result on long line containing comment: %s",
                            res.anchor.pos_marker.working_line_no,
                        )
                        results.remove(res)
                        break
                    # Is it a template comment?
                    elif (
                        seg.is_type("placeholder")
                        and cast(TemplateSegment, seg).block_type == "comment"
                    ):
                        self.logger.debug(
                            "Purging result with template comment line: %s",
                            res.anchor.pos_marker.working_line_no,
                        )
                        results.remove(res)
                        break

        # Ignore any comment clauses if present.
        if self.ignore_comment_clauses:
            raw_segments = context.segment.raw_segments
            for res in results[:]:
                # The anchor should be the first raw on the line. Work forward
                # until we're not on the line. Check if any have a parent which
                # is a comment_clause.
                raw_idx = raw_segments.index(res.anchor)
                for seg in raw_segments[raw_idx:]:
                    if (
                        seg.pos_marker.working_line_no
                        != res.anchor.pos_marker.working_line_no
                    ):
                        # We've gone past the end of the line. Stop looking.
                        break
                    # Look to see if any are in comment clauses
                    for ps in context.segment.path_to(seg):
                        if ps.segment.is_type(
                            "comment_clause", "comment_equals_clause"
                        ):
                            # It IS! Ok, purge this result from results, unless
                            # the line is already too long without the comment.
                            # We'll know that based on the line position of
                            # the comment.
                            # We can fairly confidently assert that the segment
                            # will have a position marker at this stage.
                            assert ps.segment.pos_marker
                            line_pos = ps.segment.pos_marker.working_line_pos
                            if line_pos < context.config.get("max_line_length"):
                                # OK purge it.
                                self.logger.debug(
                                    "Purging result on long line with comment "
                                    "clause: %s",
                                    res.anchor.pos_marker.working_line_no,
                                )
                                results.remove(res)
                                break
                            self.logger.debug(
                                "Keeping result on long line with comment clause. "
                                "Still too long without comment: %s",
                                res.anchor.pos_marker.working_line_no,
                            )
                    # If we finish the loop without breaking, we didn't find a
                    # comment. Keep looking.
                    else:
                        continue
                    # If we did finish with a break, we should break the outer
                    # loop too.
                    break

        return results
