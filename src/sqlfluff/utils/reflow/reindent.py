"""Methods for deducing and understanding indents."""

from collections import defaultdict
import logging
from typing import Iterator, List, Optional, Set, Tuple, cast
from dataclasses import dataclass
from sqlfluff.core.errors import SQLFluffUserError

from sqlfluff.core.parser.segments import Indent

from sqlfluff.core.parser import RawSegment, BaseSegment
from sqlfluff.core.parser.segments.meta import MetaSegment, TemplateSegment
from sqlfluff.core.rules.base import LintFix
from sqlfluff.utils.reflow.elements import ReflowBlock, ReflowPoint, ReflowSequenceType
from sqlfluff.utils.reflow.rebreak import identify_rebreak_spans


# We're in the utils module, but users will expect reflow
# logs to appear in the context of rules. Hence it's a subset
# of the rules logger.
reflow_logger = logging.getLogger("sqlfluff.rules.reflow")


def has_untemplated_newline(point: ReflowPoint) -> bool:
    """Determine whether a point contains any literal newlines.

    NOTE: We check for standard literal newlines, but also
    potential placeholder newlines which have been consumed.
    """
    # If there are no newlines (or placeholders) at all - then False.
    if not point.class_types.intersection({"newline", "placeholder"}):
        return False

    for seg in point.segments:
        # Make sure it's not templated.
        # NOTE: An insertion won't have a pos_marker. But that
        # also means it's not templated.
        if seg.is_type("newline") and (not seg.pos_marker or not seg.is_templated):
            return True
        if seg.is_type("placeholder"):
            seg = cast(TemplateSegment, seg)
            assert (
                seg.block_type == "literal"
            ), "Expected only literal placeholders in ReflowPoint."
            if "\n" in seg.source_str:
                return True
    return False


@dataclass(frozen=True)
class _IndentPoint:
    """Temporary structure for holding metadata about an indented ReflowPoint.

    We only evaluate point which either *are* line breaks or
    contain Indent/Dedent segments.
    """

    idx: int
    indent_impulse: int
    indent_trough: int
    initial_indent_balance: int
    last_line_break_idx: Optional[int]
    is_line_break: bool
    # NOTE: an "untaken indent" is referenced by the value we go *up* to.
    # i.e. An Indent segment which takes the balance from 1 to 2 but with
    # no newline is an untaken indent of value 2.
    # It also only covers untaken indents _before_ this point. If this point
    # is _also_ an untaken indent, we should be able to infer that ourselves.
    untaken_indents: Tuple[int, ...]

    @property
    def closing_indent_balance(self):
        return self.initial_indent_balance + self.indent_impulse


@dataclass
class _IndentLine:
    """Temporary structure for handing a line of indent points.

    Mutable so that we can adjust the initial indent balance
    for things like comments and templated elements, after
    constructing all the metadata for the points on the line.
    """

    initial_indent_balance: int
    indent_points: List[_IndentPoint]

    @classmethod
    def from_points(cls, indent_points: List[_IndentPoint]):
        # Catch edge case for first line where we'll start with a
        # block if no initial indent.
        if indent_points[-1].last_line_break_idx:
            starting_balance = indent_points[0].closing_indent_balance
        else:
            starting_balance = 0
        return cls(starting_balance, indent_points)

    def iter_blocks(self, elements: ReflowSequenceType) -> Iterator[ReflowBlock]:
        # Edge case for initial lines (i.e. where last_line_break is None)
        if self.indent_points[-1].last_line_break_idx is None:
            range_slice = slice(None, self.indent_points[-1].idx)
        else:
            range_slice = slice(self.indent_points[0].idx, self.indent_points[-1].idx)
        for element in elements[range_slice]:
            if isinstance(element, ReflowPoint):
                continue
            yield element

    def _iter_block_segments(
        self, elements: ReflowSequenceType
    ) -> Iterator[RawSegment]:
        for block in self.iter_blocks(elements):
            yield from block.segments

    def is_all_comments(self, elements: ReflowSequenceType) -> bool:
        """Is this line made up of just comments?"""
        block_segments = list(self._iter_block_segments(elements))
        return bool(block_segments) and all(
            seg.is_type("comment") for seg in block_segments
        )

    def is_all_templates(self, elements: ReflowSequenceType) -> bool:
        """Is this line made up of just template elements?"""
        block_segments = list(self._iter_block_segments(elements))
        return bool(block_segments) and all(
            seg.is_type("placeholder", "template_loop") for seg in block_segments
        )

    def desired_indent_units(self, forced_indents: List[int]):
        """Calculate the desired indent units.

        This is the heart of the indentation calculations.

        First we work out how many previous indents are untaken.
        In the easy case, we just use the number of untaken
        indents from previous points. The more complicated example
        is where *this point* has both dedents *and* indents. In
        this case we use the `indent_trough` to prune any
        previous untaken indents which were above the trough at
        this point.

        After that we calculate the indent from the incoming
        balance, minus any relevant untaken events *plus* any
        previously untaken indents which have been forced (i.e.
        inserted by the same operation).
        """
        if self.indent_points[0].indent_trough:
            # This says - purge any untaken indents which happened before
            # the trough (or at least only _keep_ any which would have remained).
            # NOTE: Minus signs are really hard to get wrong here.
            relevant_untaken_indents = [
                i
                for i in self.indent_points[0].untaken_indents
                if i
                <= self.initial_indent_balance
                - (
                    self.indent_points[0].indent_impulse
                    - self.indent_points[0].indent_trough
                )
            ]
        else:
            relevant_untaken_indents = list(self.indent_points[0].untaken_indents)

        desired_indent = (
            self.initial_indent_balance
            - len(relevant_untaken_indents)
            + len(forced_indents)
        )

        reflow_logger.debug(
            "Desired Indent Calculation: IB: %s, RUI: %s, UIL: %s, "
            "iII: %s, iIT: %s. = %s",
            self.initial_indent_balance,
            relevant_untaken_indents,
            self.indent_points[0].untaken_indents,
            self.indent_points[0].indent_impulse,
            self.indent_points[0].indent_trough,
            desired_indent,
        )
        return desired_indent

    def closing_balance(self):
        """The closing indent balance of the line."""
        return self.indent_points[-1].closing_indent_balance

    def opening_balance(self):
        """The opening indent balance of the line.

        NOTE: We use the first point for the starting balance rather than
        the line starting balance because we're using this to detect missing
        lines and if the line has been corrected then we don't want to do
        that.
        """
        # Edge case for first line of a file (where starting indent must be zero).
        if self.indent_points[-1].last_line_break_idx is None:
            return 0
        return self.indent_points[0].closing_indent_balance


def _revise_templated_lines(lines: List[_IndentLine], elements: ReflowSequenceType):
    """Given an initial set of individual lines. Revise templated ones.

    NOTE: This mutates the `lines` argument.

    We do this to ensure that templated lines are _somewhat_ consistent.

    Total consistency is very hard, given templated elements
    can be used in a wide range of places. What we do here is
    to try and take a somewhat rules based approach, but also
    one which should fit mostly with user expectations.

    To do this we have three scenarios:
    1. Template tags are already on the same indent.
    2. Template tags aren't, but can be hoisted without
       effectively crossing code to be on the same indent.
       This effectively does the same as "reshuffling"
       placeholders, whitespace and indent segments but
       does so without requiring intervention on the parsed
       file.
    3. Template tags which actively cut across the tree (i.e.
       start and end tags aren't at the same level and can't
       be hoisted). In this case the tags should be indented
       at the lowest indent of the matching set.

    In doing this we have to attempt to match up template
    tags. This might fail. As we battle-test this feature
    there may be some interesting bugs which come up!

    In addition to properly indenting block tags, we also
    filter out any jinja tags which contain newlines because
    if we try and fix them, we'll only fix the *initial*
    part of it. The rest won't be seen because it's within
    the tag.

    TODO: This could be an interesting way to extend the
    indentation algorithm to also cover indentation within
    jinja tags.
    """
    reflow_logger.debug("# Revise templated lines.")
    # Because we want to modify the original lines, we're going
    # to use their list index to keep track of them.
    depths = defaultdict(list)
    grouped = defaultdict(list)
    for idx, line in enumerate(lines):
        if line.is_all_templates(elements):
            # We can't assume they're all a single block.
            # But if they _start_ with a block, we should
            # respect the indent of that block.
            segment = cast(
                MetaSegment, elements[line.indent_points[-1].idx - 1].segments[0]
            )
            assert segment.is_type("placeholder", "template_loop")
            # If it's not got a block uuid, it's not a block, so it
            # should just be indented as usual. No need to revise.
            # e.g. comments or variables
            if segment.block_uuid:
                grouped[segment.block_uuid].append(idx)
                depths[segment.block_uuid].append(line.initial_indent_balance)

    # Sort through the lines, so we do to *most* indented first.
    sorted_group_indices = sorted(
        grouped.keys(), key=lambda x: max(depths[x]), reverse=True
    )
    reflow_logger.debug("  Sorted Group UUIDs: %s", sorted_group_indices)

    for group_uuid in sorted_group_indices:
        reflow_logger.debug("  Evaluating Group UUID: %s", group_uuid)

        group_lines = grouped[group_uuid]
        for idx in group_lines:
            reflow_logger.debug(
                "    Line %s: Initial Balance: %s",
                idx,
                lines[idx].initial_indent_balance,
            )

        # Check for case 1.
        if len(set(lines[idx].initial_indent_balance for idx in group_lines)) == 1:
            reflow_logger.debug("    Case 1: All the same")
            continue

        # Check for case 2.
        # In this scenario, we only need to check the adjacent points.
        # If there's any wiggle room, we pick the lowest option.
        options: List[Set[int]] = []
        for idx in group_lines:
            line = lines[idx]
            steps: Set[int] = {line.initial_indent_balance}
            # Run backward through the pre point.
            indent_balance = line.initial_indent_balance
            for seg in elements[line.indent_points[0].idx].segments[::-1]:
                if seg.is_type("indent"):
                    # Minus because we're going backward.
                    indent_balance -= cast(Indent, seg).indent_val
                steps.add(indent_balance)
            # Run forward through the post point.
            indent_balance = line.initial_indent_balance
            for seg in elements[line.indent_points[-1].idx].segments:
                if seg.is_type("indent"):
                    # Positive because we're going forward.
                    indent_balance += cast(Indent, seg).indent_val
                steps.add(indent_balance)
            reflow_logger.debug("    Line %s: Options: %s", idx, steps)
            options.append(steps)

        # We should also work out what all the indents are _between_
        # these options and make sure we don't go above that.
        first_line_idx = group_lines[0]
        last_line_idx = group_lines[-1]
        intermediate_lines = [
            line
            for line in lines[first_line_idx + 1 : last_line_idx]
            # Exclude lines which are in the group to avoid
            # issues with loop markers.
            if line not in [lines[idx] for idx in group_lines]
        ]
        reflow_logger.debug(
            "    Intermediate Lines: %s",
            [line.initial_indent_balance for line in intermediate_lines],
        )
        limit_indent = min(
            # Minus one to reverse the effect that the block has
            # already had.
            line.initial_indent_balance - 1
            for line in intermediate_lines
        )

        # Evaluate options.
        overlap = set.intersection(*options)
        reflow_logger.debug("    Simple Overlap: %s", overlap)
        # Remove any options above the limit option.
        # We minus one from the limit, because if it comes into effect
        # we'll effectively remove the effects of the indents between the elements.
        overlap = {i for i in overlap if i <= limit_indent}
        reflow_logger.debug("    Overlap: %s, Limit: %s", overlap, limit_indent)
        # Is there a mutually agreeable option?
        if overlap:
            # Go for the deeper option if there's flexibility, because this
            # will usually involve moving the fewest options.
            best_indent = max(overlap)
            reflow_logger.debug(
                "    Case 2: Best: %s, Overlap: %s", best_indent, overlap
            )
        # If no overlap, it's case 3
        else:
            # Set the indent to the minimum of the existing ones.
            best_indent = min(lines[idx].initial_indent_balance for idx in group_lines)
            reflow_logger.debug("    Case 3: Best: %s", best_indent)
            # Remove one indent from all intermediate lines.
            # This is because we're effectively saying that these
            # placeholders shouldn't impact the indentation within them.
            for idx in range(first_line_idx + 1, last_line_idx):
                if idx not in group_lines:
                    # MUTATION
                    lines[idx].initial_indent_balance -= 1

        # Set all the lines to this indent
        for idx in group_lines:
            # MUTATION
            lines[idx].initial_indent_balance = best_indent

    # Finally, look for any of the lines which contain newlines
    # inside the placeholders. We use a slice to make sure
    # we're iterating through a copy so that we can safely
    # modify the underlying list.
    for idx, line in enumerate(lines[:]):
        # Get the first segment.
        first_seg = elements[line.indent_points[0].idx + 1].segments[0]
        src_str = first_seg.pos_marker.source_str()
        if src_str != first_seg.raw and "\n" in src_str:
            reflow_logger.debug(
                "    Removing line %s from linting as placeholder "
                "contains newlines.",
                first_seg.pos_marker.working_line_no,
            )
            lines.remove(line)


def _revise_comment_lines(lines: List[_IndentLine], elements: ReflowSequenceType):
    """Given an initial set of individual lines. Revise comment ones.

    NOTE: This mutates the `lines` argument.

    We do this to ensure that lines with comments are aligned to
    the following non-comment element.
    """
    reflow_logger.debug("# Revise comment lines.")
    # new_lines: List[_ReindentLine] = []
    comment_line_buffer: List[int] = []

    # Slice to avoid copying
    for idx, line in enumerate(lines[:]):
        if line.is_all_comments(elements):
            comment_line_buffer.append(idx)
        else:
            # Not a comment only line, if there's a buffer anchor
            # to this one.
            for comment_line_idx in comment_line_buffer:
                reflow_logger.debug(
                    "  Comment Only Line: %s. Anchoring to %s", comment_line_idx, idx
                )
                # Mutate reference lines to match this one.
                lines[
                    comment_line_idx
                ].initial_indent_balance = line.initial_indent_balance
            # Reset the buffer
            comment_line_buffer = []

    # Any trailing comments should be anchored to the baseline.
    for comment_line_idx in comment_line_buffer:
        # Mutate reference lines to match this one.
        lines[comment_line_idx].initial_indent_balance = 0
        reflow_logger.debug(
            "  Comment Only Line: %s. Anchoring to baseline", comment_line_idx
        )


def construct_single_indent(indent_unit: str, tab_space_size: int) -> str:
    """Construct a single indent unit."""
    if indent_unit == "tab":
        return "\t"
    elif indent_unit == "space":
        return " " * tab_space_size
    else:  # pragma: no cover
        raise SQLFluffUserError(
            f"Expected indent_unit of 'tab' or 'space', instead got {indent_unit}"
        )


def _crawl_indent_points(elements: ReflowSequenceType) -> Iterator[_IndentPoint]:
    """Crawl through a reflow sequence, mapping existing indents.

    This is where *most* of the logic for smart indentation
    happens. The values returned here have a large impact on
    exactly how indentation is treated.

    TODO: Once this function *works*, there's definitely headroom
    for simplification and optimisation. We should do that.
    """
    last_line_break_idx = None
    indent_balance = 0
    untaken_indents: Tuple[int, ...] = ()
    for idx, elem in enumerate(elements):
        if isinstance(elem, ReflowPoint):
            indent_impulse, indent_trough = elem.get_indent_impulse()

            # Is it a line break? AND not a templated one.
            if has_untemplated_newline(elem) and idx != last_line_break_idx:
                yield _IndentPoint(
                    idx,
                    indent_impulse,
                    indent_trough,
                    indent_balance,
                    last_line_break_idx,
                    True,
                    untaken_indents,
                )
                last_line_break_idx = idx
                has_newline = True
            # Is it otherwise meaningful as an indent point?
            # NOTE: a point at idx zero is meaningful because it's like an indent.
            # NOTE: Last edge case. If we haven't yielded yet, but the
            # next element is the end of the file. Yield.
            elif (
                indent_impulse
                or indent_trough
                or idx == 0
                or elements[idx + 1].segments[0].is_type("end_of_file")
            ):
                yield _IndentPoint(
                    idx,
                    indent_impulse,
                    indent_trough,
                    indent_balance,
                    last_line_break_idx,
                    False,
                    untaken_indents,
                )
                has_newline = False

            # Strip any untaken indents above the new balance.
            # NOTE: We strip back to the trough, not just the end point
            # if the trough was lower than the impulse.
            untaken_indents = tuple(
                x
                for x in untaken_indents
                if x
                <= (
                    indent_balance + indent_impulse + indent_trough
                    if indent_trough < indent_impulse
                    else indent_balance + indent_impulse
                )
            )

            # After stripping, we may have to add them back in.
            if indent_impulse > indent_trough and not has_newline:
                for i in range(indent_trough, indent_impulse):
                    untaken_indents += (indent_balance + i + 1,)

            # Update values
            indent_balance += indent_impulse


def _map_line_buffers(elements: ReflowSequenceType) -> List[_IndentLine]:
    """Map the existing elements, building up a list of _IndentLine."""
    # First build up the buffer of lines.
    lines = []
    point_buffer = []
    for indent_point in _crawl_indent_points(elements):
        # We evaluate all the points in a line at the same time, so
        # we first build up a buffer.
        point_buffer.append(indent_point)

        if not indent_point.is_line_break:
            continue

        # If it *is* a line break, then store it.
        lines.append(_IndentLine.from_points(point_buffer))
        # Reset the buffer
        point_buffer = [indent_point]

    # Handle potential final line
    if len(point_buffer) > 1:
        lines.append(_IndentLine.from_points(point_buffer))

    return lines


def _deduce_line_current_indent(
    elements: ReflowSequenceType, last_line_break_idx: Optional[int] = None
) -> str:
    """Deduce the current indent string.

    This method accounts for both literal indents and indents
    consumed from the source as by potential templating tags.
    """
    indent_seg = None
    if last_line_break_idx is not None:
        indent_seg = cast(
            ReflowPoint, elements[last_line_break_idx]
        )._get_indent_segment()
    elif isinstance(elements[0], ReflowPoint):
        # No last_line_break_idx, but this is a point. It's the first line.
        # Get the last whitespace element.
        # TODO: We don't currently handle the leading swallowed whitespace case.
        # That could be added here, but it's an edge case which can be done
        # at a later date easily. For now it won't get picked up.
        for indent_seg in elements[0].segments[::-1]:
            if indent_seg.is_type("whitespace"):
                break
        # Handle edge case of no whitespace, but with newline.
        if not indent_seg.is_type("whitespace"):
            indent_seg = None

    if not indent_seg:
        return ""

    # We have to check pos marker before checking is templated.
    # Insertions don't have pos_markers - so aren't templated,
    # but also don't support calling is_templated.
    if indent_seg.is_type("placeholder"):
        # It's a consumed indent.
        return cast(TemplateSegment, indent_seg).source_str.split("\n")[-1] or ""
    elif not indent_seg.pos_marker or not indent_seg.is_templated:
        assert "\n" not in indent_seg.raw, f"Found newline in indent: {indent_seg}"
        return indent_seg.raw
    else:  # pragma: no cover
        # It's templated. This shouldn't happen. Segments returned by
        # _get_indent_segment, should be valid indents (i.e. whitespace
        # or placeholders for consumed whitespace). This is a bug.
        raise NotImplementedError(
            "Unexpected templated indent. Report this as a bug on GitHub."
        )


def _lint_line_starting_indent(
    elements: ReflowSequenceType,
    indent_line: _IndentLine,
    single_indent: str,
    forced_indents: List[int],
) -> List[LintFix]:
    """Lint the indent at the start of a line.

    NOTE: This mutates `elements` to avoid lots of copying.
    """
    indent_points = indent_line.indent_points
    # Set up the default anchor
    anchor = {"before": elements[indent_points[0].idx + 1].segments[0]}
    # Find initial indent, and deduce appropriate string indent.
    current_indent = _deduce_line_current_indent(
        elements, indent_points[-1].last_line_break_idx
    )
    desired_indent_units = indent_line.desired_indent_units(forced_indents)
    desired_starting_indent = desired_indent_units * single_indent
    initial_point = cast(ReflowPoint, elements[indent_points[0].idx])

    if current_indent == desired_starting_indent:
        return []

    reflow_logger.debug(
        "    Correcting indent @ line %s. Existing indent: %r -> %r",
        elements[indent_points[0].idx + 1].segments[0].pos_marker.working_line_no,
        current_indent,
        desired_starting_indent,
    )

    # Initial point gets special handling if it has no newlines.
    if indent_points[0].idx == 0 and not indent_points[0].is_line_break:
        new_fixes = [
            LintFix.delete(seg, description="First line should not be indented.")
            for seg in initial_point.segments
        ]
        new_point = ReflowPoint(())
    # Placeholder indents also get special treatment
    else:
        new_fixes, new_point = initial_point.indent_to(
            desired_starting_indent,
            **anchor,  # type: ignore
        )

    elements[indent_points[0].idx] = new_point
    return new_fixes


def _lint_line_untaken_positive_indents(
    elements: ReflowSequenceType, indent_line: _IndentLine, single_indent: str
) -> Tuple[List[LintFix], List[int]]:
    """Check for positive indents which should have been taken."""
    # If we don't close the line higher there won't be any.
    starting_balance = indent_line.opening_balance()
    if indent_line.closing_balance() <= starting_balance:
        return [], []

    indent_points = indent_line.indent_points

    # Account for the closing trough.
    if indent_points[-1].indent_trough:
        closing_trough = (
            indent_points[-1].initial_indent_balance + indent_points[-1].indent_trough
        )
    else:
        closing_trough = (
            indent_points[-1].initial_indent_balance + indent_points[-1].indent_impulse
        )
    # Edge case: if closing_balance > starting balance
    # but closing_trough isn't, then we shouldn't insert
    # a new line. That means we just dropped back down to
    # close the untaken newline.
    if closing_trough <= starting_balance:
        return [], []

    # On the way up we're looking for whether the ending balance
    # was an untaken indent or not. If it *was* untaken, there's
    # a good chance that we *should* take it.
    if closing_trough not in indent_points[-1].untaken_indents:
        # NOTE: I don't think we should ever get here. It's probably
        # an error if we do.
        return [], []

    # The closing indent balance *does* correspond to an
    # untaken indent on this line. We *should* force a newline
    # at that position.
    for ip in indent_points:
        if ip.closing_indent_balance == closing_trough:
            target_point_idx = ip.idx
            desired_indent = single_indent * (
                ip.closing_indent_balance - len(ip.untaken_indents)
            )
            break
    else:  # pragma: no cover
        raise NotImplementedError("We should always find the relevant point.")
    reflow_logger.debug(
        "    Detected missing +ve line break @ line %s. Indenting to %r",
        elements[target_point_idx + 1].segments[0].pos_marker.working_line_no,
        desired_indent,
    )
    target_point = cast(ReflowPoint, elements[target_point_idx])
    new_fixes, new_point = target_point.indent_to(
        desired_indent, before=elements[target_point_idx + 1].segments[0]
    )
    elements[target_point_idx] = new_point
    # Keep track of the indent we forced, by returning it.
    return new_fixes, [closing_trough]


def _lint_line_untaken_negative_indents(
    elements: ReflowSequenceType,
    indent_line: _IndentLine,
    single_indent: str,
    forced_indents: List[int],
) -> List[LintFix]:
    """Check for negative indents which should have been taken."""
    # If we don't close lower than we start, there won't be any.
    if indent_line.closing_balance() >= indent_line.opening_balance():
        return []

    fixes: List[LintFix] = []
    # On the way down we're looking for indents which *were* taken on
    # the way up, but currently aren't on the way down. We slice so
    # that the _last_ point isn't evaluated, because that's fine.
    for ip in indent_line.indent_points[:-1]:
        # Is line break, or positive indent?
        if ip.is_line_break or ip.indent_impulse >= 0:
            continue
        # It's negative, is it untaken?
        if (
            ip.initial_indent_balance in ip.untaken_indents
            and ip.initial_indent_balance not in forced_indents
        ):
            # Yep, untaken.
            continue
        # Edge Case: Semicolons. For now, semicolon placement is a little
        # more complicated than what we do here. For now we don't (by
        # default) introduce missing -ve indents before semicolons.
        # TODO: Review whether this is a good idea, or whether this should be
        # more configurable.
        # NOTE: This could potentially lead to a weird situation if two
        # statements are already on the same line. That's a bug to solve later.
        if (
            elements[ip.idx + 1 :]
            and "statement_terminator" in elements[ip.idx + 1].class_types
        ):
            reflow_logger.debug(
                "    Detected missing -ve line break @ line %s, before "
                "semicolon. Ignoring...",
                elements[ip.idx + 1].segments[0].pos_marker.working_line_no,
            )
            continue

        # Edge case: template blocks. These sometimes sit in odd places
        # in the parse tree so don't force newlines before them
        if elements[ip.idx + 1 :] and "placeholder" in elements[ip.idx + 1].class_types:
            # are any of those placeholders blocks?
            if any(
                cast(TemplateSegment, seg).block_type.startswith("block")
                for seg in elements[ip.idx + 1].segments
                if seg.is_type("placeholder")
            ):
                reflow_logger.debug(
                    "    Detected missing -ve line break @ line %s, before "
                    "block placeholder. Ignoring...",
                    elements[ip.idx + 1].segments[0].pos_marker.working_line_no,
                )
                continue

        # It's negative, not a line break and was taken on the way up.
        # This *should* be an indent!
        desired_indent = single_indent * (
            ip.closing_indent_balance - len(ip.untaken_indents) + len(forced_indents)
        )
        reflow_logger.debug(
            "    Detected missing -ve line break @ line %s. Indenting to %r",
            elements[ip.idx + 1].segments[0].pos_marker.working_line_no,
            desired_indent,
        )
        target_point = cast(ReflowPoint, elements[ip.idx])
        new_fixes, new_point = target_point.indent_to(
            desired_indent, before=elements[ip.idx + 1].segments[0]
        )
        elements[ip.idx] = new_point
        fixes += new_fixes

    return fixes


def _lint_line_buffer_indents(
    elements: ReflowSequenceType,
    indent_line: _IndentLine,
    single_indent: str,
    forced_indents: List[int],
) -> List[LintFix]:  # Tuple[List[LintFix], List[_IndentLine]]
    """Evaluate a single set of indent points on one line.

    NOTE: This mutates the given `elements` and `forced_indents` input to avoid
    lots of copying.

    Order of operations:
    1. Evaluate the starting indent for this line.
    2. For points which aren't line breaks in the line, we evaluate them
       to see whether they *should* be. We separately address missing indents
       on the way *up* and then on the way *down*.
       - *Up* in this sense means where the indent balance goes up, but isn't
         closed again within the same line - e.g. :code:`SELECT a + (2 +` where
         the indent implied by the bracket isn't closed out before the end of the
         line.
       - *Down* in this sense means where we've dropped below the starting
         indent balance of the line - e.g. :code:`1 + 1) FROM foo` where the
         line starts within a bracket and then closes that *and* closes an
         apparent SELECT clause without a newline.

    This method returns fixes, including appropriate descriptions, to
    allow generation of LintResult objects directly from them.
    """
    reflow_logger.debug(
        "  Evaluate Line #%s [source line #%s]. FI %s",
        elements[indent_line.indent_points[0].idx + 1]
        .segments[0]
        .pos_marker.working_line_no,
        elements[indent_line.indent_points[0].idx + 1]
        .segments[0]
        .pos_marker.source_position()[0],
        forced_indents,
    )
    reflow_logger.debug(
        "   Line Segments: %s",
        [
            elem.segments
            for elem in elements[
                indent_line.indent_points[0].idx : indent_line.indent_points[-1].idx
            ]
        ],
    )
    reflow_logger.info("  Evaluate Line: %s. FI %s", indent_line, forced_indents)
    fixes = []

    # First, handle starting indent.
    fixes += _lint_line_starting_indent(
        elements, indent_line, single_indent, forced_indents
    )

    # Second, handle potential missing positive indents.
    new_fixes, new_indents = _lint_line_untaken_positive_indents(
        elements, indent_line, single_indent
    )
    # If we have any, bank them and return. We don't need to check for
    # negatives because we know we're on the way up.
    if new_fixes:
        fixes += new_fixes
        # Keep track of any indents we forced
        forced_indents.extend(new_indents)
        return fixes

    # Third, handle potential missing negative indents.
    fixes += _lint_line_untaken_negative_indents(
        elements, indent_line, single_indent, forced_indents
    )

    # Lastly remove any forced indents above the closing balance.
    # Iterate through a slice so we're not editing the thing
    # that we're iterating through.
    for i in forced_indents[:]:
        if i > indent_line.closing_balance():
            forced_indents.remove(i)

    return fixes


def lint_indent_points(
    elements: ReflowSequenceType,
    single_indent: str,
    skip_indentation_in: Set[str] = set(),
) -> Tuple[ReflowSequenceType, List[LintFix]]:
    """Lint the indent points to check we have line breaks where we should.

    For linting indentation - we *first* need to make sure there are
    line breaks in all the places there should be. This takes an input
    set of indent points, and inserts additional line breaks in the
    necessary places to make sure indentation can be valid.

    Specifically we're addressing two things:

    1. Any untaken indents. An untaken indent is only valid if it's
    corresponding dedent is on the same line. If that is not the case,
    there should be a line break at the location of the indent and dedent.

    2. The indentation of lines. Given the line breaks are in the right
    place, is the line indented correctly.

    We do these at the same time, because we can't do the second without
    having line breaks in the right place, but if we're inserting a line
    break, we need to also know how much to indent by.
    """
    # First map the line buffers.
    lines: List[_IndentLine] = _map_line_buffers(elements)

    # Revise templated indents
    _revise_templated_lines(lines, elements)
    # Revise comment indents
    _revise_comment_lines(lines, elements)

    # Skip elements we're configured to not touch (i.e. scripts)
    for line in lines[:]:
        for block in line.iter_blocks(elements):
            if any(
                skip_indentation_in.intersection(types)
                for types in block.depth_info.stack_class_types
            ):
                reflow_logger.debug(
                    "Skipping line %s because it is within one of %s",
                    line,
                    skip_indentation_in,
                )
                lines.remove(line)
                break

    reflow_logger.debug("# Evaluate lines for indentation.")
    # Last: handle each of the lines.
    fixes: List[LintFix] = []
    # NOTE: forced_indents is mutated by _lint_line_buffer_indents
    # It's used to pass from one call to the next.
    forced_indents: List[int] = []
    elem_buffer = elements.copy()  # Make a working copy to mutate.
    for line in lines:
        fixes += _lint_line_buffer_indents(
            elem_buffer, line, single_indent, forced_indents
        )

    return elem_buffer, fixes


def lint_line_length(
    elements: ReflowSequenceType,
    root_segment: BaseSegment,
    single_indent: str,
    line_length_limit: int,
) -> Tuple[ReflowSequenceType, List[LintFix]]:
    """Lint the sequence to lines over the configured length.

    NOTE: This assumes that `lint_indent_points` has already
    been run. The method won't necessarily *fail* but it does
    assume that the current indent is correct and that indents
    have already been inserted where they're missing.
    """
    # TODO: Outstanding questions:
    # 1. Template loop segments should probably exclude a line.
    # 2. Need to handle lengths in the source for template elements.
    #    [probably lots of testing too]

    reflow_logger.debug("# Evaluate lines for length.")
    # Make a working copy to mutate.
    elem_buffer: ReflowSequenceType = elements.copy()
    line_buffer: ReflowSequenceType = []
    fixes: List[LintFix] = []

    last_indent_idx = None
    for i, elem in enumerate(elements):
        # Are there newlines in the element?
        # If not, add it to the buffer and wait to evaluate the line.
        # If yes, it's time to evaluate the line.
        if not elem.num_newlines():
            line_buffer.append(elem)
            continue

        # If we don't have a buffer yet, also carry on. Nothing to lint.
        if not line_buffer:
            continue

        # Evaluate a line

        # reflow_logger.warning("LINE:")
        # for idx, e in enumerate(line_buffer):
        #     reflow_logger.warning("    #%s: %s", idx, [s.raw for s in e.segments])

        # Get the current indent.
        current_indent = _deduce_line_current_indent(elements, last_indent_idx)
        # reflow_logger.warning("INDENT @%s: %r = %s", last_indent_idx, ind, len(ind))
        # Get the length of all the elements on the line (other than the indent).
        # TODO: This needs to handle templated elements.
        char_len = sum(sum(len(seg.raw) for seg in e.segments) for e in line_buffer)
        # reflow_logger.warning("CHARLEN @%s: %r", last_indent_idx, char_len)

        # Is the line over the limit length?
        line_len = len(current_indent) + char_len
        line_no = line_buffer[0].segments[0].pos_marker.working_line_no
        if line_len <= line_length_limit:
            reflow_logger.debug(
                "    Line #%s. Length %s <= %s. OK.",
                line_no,
                line_len,
                line_length_limit,
            )
        else:
            reflow_logger.debug(
                "    Line #%s. Length %s > %s. PROBLEM.",
                line_no,
                line_len,
                line_length_limit,
            )

            # Potential places to shorten the line are either indent locations
            # or segments with a defined line position (like operators).

            # NOTE: We need the closing indent too for the next operations because
            # it might be an option contain the closing indent for a potential
            # indent earlier in the line.
            line_elements = line_buffer + [elem]

            # Identify rebreak spans first so we can work out their indentation
            # in the next section.
            spans = identify_rebreak_spans(line_elements, root_segment)
            # The index to insert a potential indent at depends on the
            # line_position of the span. Infer that here and store the indices
            # in the elements.
            rebreak_indices = []
            for span in spans:
                if span.line_position == "leading":
                    rebreak_indices.append(span.start_idx - 1)
                elif span.line_position == "trailing":
                    rebreak_indices.append(span.end_idx + 1)
                else:
                    raise NotImplementedError(
                        "Unexpected line position: %s", span.line_position
                    )
            reflow_logger.debug("    rebreak_indices: %s", rebreak_indices)

            # Identify indent points second, taking into account rebreak_indices.
            balance = 0
            # Expect fractional keys, because of the half values for
            # rebreak points.
            matched_indents: defaultdict[float, List[ReflowPoint]] = defaultdict(list)
            for idx, e in enumerate(line_elements):
                # We only care about points, because only they contain indents.
                if not isinstance(e, ReflowPoint):
                    continue

                # As usual, indents are referred to by their "uphill" side
                # so what number we store the point against depends on whether
                # it's positive or negative.
                indent_stats = e.get_indent_impulse()
                if indent_stats[1] < 0:  # NOTE: for negative, *trough* counts.
                    matched_indents[balance * 1.0].append(e)
                    balance += indent_stats[0]
                elif indent_stats[0] > 0:  # NOTE: for positive, *impulse* counts.
                    balance += indent_stats[0]
                    matched_indents[balance * 1.0].append(e)
                elif idx in rebreak_indices:
                    # For potential rebreak options (i.e. ones without an indent)
                    # we add 0.5 so that they sit *between* the varying indent
                    # options. that means we split them before any of their
                    # content, but don't necessarily split them when their
                    # container is split.
                    matched_indents[balance + 0.5].append(e)
                else:
                    continue

            # Before working out the lowest option, we purge any which contain
            # ONLY the final point. That's because adding indents there won't
            # actually help the line length. There's *already* a newline there.
            for indent_level in list(matched_indents.keys()):
                if matched_indents[indent_level] == [elem]:
                    matched_indents.pop(indent_level)
                    reflow_logger.debug(
                        "    purging balance of %s, it references only the "
                        "final element",
                        indent_level,
                    )

            # Matched sets logging
            # reflow_logger.warning("  matched_indents:")
            # for balance in matched_indents.keys():
            #     reflow_logger.warning("    BAL: %s", balance)
            #     for pt in matched_indents[balance]:
            #         reflow_logger.warning("      PT: %s", pt)

            # As a blunt solution, force indents at the lowest available option.
            # TODO: Make this more elegant later, with the option to potentially
            # add linebreaks at more than one level.
            target_balance = min(matched_indents.keys())
            desired_indent = current_indent
            if target_balance >= 1:
                desired_indent += single_indent
            reflow_logger.debug(
                "    Targetting balance of %s, indent: %r for %s",
                target_balance,
                desired_indent,
                matched_indents[target_balance],
            )
            # TODO: This is messy, should just use indices FROM THE START.
            for e in matched_indents[target_balance]:
                # If the option is the final element. Don't touch it, because
                # there's already an indent there.
                if e is elem:
                    continue
                e_idx = elements.index(e)
                new_fixes, new_point = e.indent_to(
                    desired_indent,
                )
                # NOTE: Mutation of elements.
                elements[e_idx] = new_point
                fixes += new_fixes

        # Regardless of whether the line was good or not, clear
        # the buffers ready for the next line.
        line_buffer = []
        last_indent_idx = i

    # TODO: Some of these fixes are going to need to be grouped together
    # to make any sense to the user.

    return elem_buffer, fixes
