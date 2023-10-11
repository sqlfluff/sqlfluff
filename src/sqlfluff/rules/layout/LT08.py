"""Implementation of Rule LT08."""

from typing import List, Optional

from sqlfluff.core.parser import NewlineSegment
from sqlfluff.core.rules import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler


class Rule_LT08(BaseRule):
    """Blank line expected but not found after CTE closing bracket.

    **Anti-pattern**

    There is no blank line after the CTE closing bracket. In queries with many
    CTEs, this hinders readability.

    .. code-block:: sql

        WITH plop AS (
            SELECT * FROM foo
        )
        SELECT a FROM plop

    **Best practice**

    Add a blank line.

    .. code-block:: sql

        WITH plop AS (
            SELECT * FROM foo
        )

        SELECT a FROM plop

    """

    name = "layout.cte_newline"
    aliases = ("L022",)
    groups = ("all", "core", "layout")
    crawl_behaviour = SegmentSeekerCrawler({"with_compound_statement"})
    is_fix_compatible = True

    def _eval(self, context: RuleContext) -> Optional[List[LintResult]]:
        """Blank line expected but not found after CTE definition."""
        error_buffer = []
        global_comma_style = context.config.get(
            "line_position", ["layout", "type", "comma"]
        )
        assert context.segment.is_type("with_compound_statement")
        # First we need to find all the commas, the end brackets, the
        # things that come after that and the blank lines in between.

        # Find all the closing brackets. They are our anchor points.
        bracket_indices = []
        expanded_segments = list(
            context.segment.iter_segments(expanding=["common_table_expression"])
        )
        for idx, seg in enumerate(expanded_segments):
            if seg.is_type("bracketed"):
                bracket_indices.append(idx)

        # Work through each point and deal with it individually
        for bracket_idx in bracket_indices:
            forward_slice = expanded_segments[bracket_idx:]
            seg_idx = 1
            line_idx = 0
            comma_seg_idx = 0
            blank_lines = 0
            comma_line_idx = None
            line_blank = False
            comma_style: str
            line_starts = {}
            comment_lines = []

            self.logger.info(
                "## CTE closing bracket found at %s, idx: %s. Forward slice: %.20r",
                forward_slice[0].pos_marker,
                bracket_idx,
                "".join(elem.raw for elem in forward_slice),
            )

            # Work forward to map out the following segments.
            while (
                forward_slice[seg_idx].is_type("comma")
                or not forward_slice[seg_idx].is_code
            ):
                if forward_slice[seg_idx].is_type("newline"):
                    if line_blank:
                        # It's a blank line!
                        blank_lines += 1
                    line_blank = True
                    line_idx += 1
                    line_starts[line_idx] = seg_idx + 1
                elif forward_slice[seg_idx].is_type("comment"):
                    # Lines with comments aren't blank
                    line_blank = False
                    comment_lines.append(line_idx)
                elif forward_slice[seg_idx].is_type("comma"):
                    # Keep track of where the comma is.
                    # We'll evaluate it later.
                    comma_line_idx = line_idx
                    comma_seg_idx = seg_idx
                seg_idx += 1

            # Infer the comma style (NB this could be different for each case!)
            if comma_line_idx is None:
                comma_style = "final"
            elif line_idx == 0:
                comma_style = "oneline"
            elif comma_line_idx == 0:
                comma_style = "trailing"
            elif comma_line_idx == line_idx:
                comma_style = "leading"
            else:
                comma_style = "floating"

            # Readout of findings
            self.logger.info(
                "blank_lines: %s, comma_line_idx: %s. final_line_idx: %s, "
                "final_seg_idx: %s",
                blank_lines,
                comma_line_idx,
                line_idx,
                seg_idx,
            )
            self.logger.info(
                "comma_style: %r, line_starts: %r, comment_lines: %r",
                comma_style,
                line_starts,
                comment_lines,
            )

            # If we've got blank lines. We're good.
            if blank_lines >= 1:
                continue

            # We've got an issue
            self.logger.info("!! Found CTE without enough blank lines.")

            # Based on the current location of the comma we insert newlines
            # to correct the issue.

            # First handle the potential simple case of a current one line
            fix_type = "create_before"  # In most cases we just insert newlines.
            if comma_style == "oneline":
                # Here we respect the target comma style to insert at the
                # relevant point.
                if global_comma_style == "trailing":
                    # Add a blank line after the comma
                    fix_point = forward_slice[comma_seg_idx + 1]
                    # Optionally here, if the segment we've landed on is
                    # whitespace then we REPLACE it rather than inserting.
                    if forward_slice[comma_seg_idx + 1].is_type("whitespace"):
                        fix_type = "replace"
                elif global_comma_style == "leading":
                    # Add a blank line before the comma
                    fix_point = forward_slice[comma_seg_idx]
                else:  # pragma: no cover
                    raise NotImplementedError(
                        f"Unexpected global comma style {global_comma_style!r}"
                    )
                # In both cases it's a double newline.
                num_newlines = 2
            else:
                # In the following cases we only care which one we're in
                # when comments don't get in the way. If they *do*, then
                # we just work around them.
                if not comment_lines or line_idx - 1 not in comment_lines:
                    self.logger.info("Comment routines not applicable")
                    if comma_style in ("trailing", "final", "floating"):
                        # Detected an existing trailing comma or it's a final
                        # CTE, OR the comma isn't leading or trailing.
                        # If the preceding segment is whitespace, replace it
                        if forward_slice[seg_idx - 1].is_type("whitespace"):
                            fix_point = forward_slice[seg_idx - 1]
                            fix_type = "replace"
                        else:
                            # Otherwise add a single newline before the end
                            # content.
                            fix_point = forward_slice[seg_idx]
                    elif comma_style == "leading":
                        # Detected an existing leading comma.
                        fix_point = forward_slice[comma_seg_idx]
                else:
                    self.logger.info("Handling preceding comments")
                    offset = 1
                    while line_idx - offset in comment_lines:
                        offset += 1
                    # If the offset - 1 equals the line_idx then there aren't
                    # really any comment-only lines (ref #2945).
                    # Reset to line_idx
                    fix_point = forward_slice[
                        line_starts[line_idx - (offset - 1) or line_idx]
                    ]
                num_newlines = 1

            fixes = [
                LintFix(
                    fix_type,
                    fix_point,
                    [NewlineSegment()] * num_newlines,
                )
            ]
            # Create a result, anchored on the start of the next content.
            error_buffer.append(LintResult(anchor=forward_slice[seg_idx], fixes=fixes))
        # Return the buffer if we have one.
        return error_buffer or None
