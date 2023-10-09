"""Implementation of Rule LT05."""

from typing import List, cast

from sqlfluff.core.parser.segments import TemplateSegment
from sqlfluff.core.rules import LintResult, RuleContext
from sqlfluff.core.rules.base import BaseRule
from sqlfluff.core.rules.crawlers import RootOnlyCrawler
from sqlfluff.utils.reflow.sequence import ReflowSequence


class Rule_LT05(BaseRule):
    """Line is too long."""

    name = "layout.long_lines"
    aliases = ("L016",)
    groups = ("all", "core", "layout")
    crawl_behaviour = RootOnlyCrawler()
    targets_templated = True
    template_safe_fixes = True
    _adjust_anchors = True
    _check_docstring = False
    is_fix_compatible = True

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
            .break_long_lines()
            .get_results()
        )

        # Ignore any comment line if appropriate.
        if self.ignore_comment_lines:
            raw_segments = context.segment.raw_segments
            for res in results[:]:
                # First handle the easy case that the anchor (i.e. the start
                # of the line is a comment).
                assert res.anchor
                assert res.anchor.pos_marker
                if res.anchor.is_type("comment"):
                    self.logger.debug(
                        "Purging result on long line starting with comment: %s",
                        res.anchor.pos_marker.working_line_no,
                    )
                    results.remove(res)
                    continue
                # Then look for comments on the rest of the line:
                assert res.anchor.pos_marker
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
                assert res.anchor
                assert res.anchor.pos_marker
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
