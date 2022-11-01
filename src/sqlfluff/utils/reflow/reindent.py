"""Methods for deducing and understanding indents."""

from collections import defaultdict
import logging
from typing import Iterator, List, Optional, Set, Tuple, cast
from dataclasses import dataclass
from sqlfluff.core.errors import SQLFluffUserError

from sqlfluff.core.parser.segments import Indent

from sqlfluff.core.parser import RawSegment, BaseSegment
from sqlfluff.core.parser.segments.base import SourceFix
from sqlfluff.core.parser.segments.meta import MetaSegment, TemplateSegment
from sqlfluff.core.rules.base import LintFix
from sqlfluff.utils.reflow.elements import ReflowBlock, ReflowPoint, ReflowSequenceType


# We're in the utils module, but users will expect reflow
# logs to appear in the context of rules. Hence it's a subset
# of the rules logger.
reflow_logger = logging.getLogger("sqlfluff.rules.reflow")


def deduce_line_indent(raw_segment: RawSegment, root_segment: BaseSegment) -> str:
    """Given a raw segment, deduce the indent of it's line."""
    seg_idx = root_segment.raw_segments.index(raw_segment)
    indent_seg = None
    for seg in root_segment.raw_segments[seg_idx::-1]:
        if seg.is_code:
            indent_seg = None
        elif seg.is_type("whitespace"):
            indent_seg = seg
        elif seg.is_type("newline"):
            break
    reflow_logger.debug("Deduced indent for %s as %s", raw_segment, indent_seg)
    if indent_seg:
        return indent_seg.raw
    else:
        return ""


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
            if seg.block_type != "literal":
                continue
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
        # check there *are* segments - TODO DOCSRTINGS BETTER
        block_segments = list(self._iter_block_segments(elements))
        return bool(block_segments) and all(
            seg.is_type("comment") for seg in block_segments
        )

    def is_all_templates(self, elements: ReflowSequenceType) -> bool:
        # check there *are* segments - TODO DOCSRTINGS BETTER
        block_segments = list(self._iter_block_segments(elements))
        # reflow_logger.warning("BLOCK SEGS: %s", block_segments)
        return bool(block_segments) and all(
            seg.is_type("placeholder", "template_loop") for seg in block_segments
        )

    def desired_indent_units(self, forced_indents: List[int]):
        # TODO: I don't quite understand this logic. It works tho.
        # DOCUMENT THIS!!!!!
        if self.indent_points[0].indent_trough:
            # This says (I think) - purge any untaken indents which happened
            # before the trough (or at least only _keep_ any which would have remained.)
            # NEEEDS MORE TESTS.
            # Minus signs are really hard to get wrong here.
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


def _revise_templated_lines(lines: List[_IndentLine], elements: ReflowSequenceType):
    """Given an initial set of individual lines. Revise templated ones.

    NOTE: This mutates the `lines` argument.

    We do this to ensure that templated lines are _somewhat_ consistent.

    Total consistency is very hard, given templated elements
    can be used in a wide range of places. What we do here is
    to try and take a somewhat rules based approach, but also
    one which should fit mostly with user expectations.

    To do this we have three scenarios:
    1. Template tags area already on the same indent.
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

    # Any trailing comments should be anchored the baseline.
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
    else:
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


def _evaluate_indent_point_buffer(
    elements: ReflowSequenceType,
    indent_line: _IndentLine,
    single_indent: str,
    forced_indents: List[int],
) -> List[LintFix]:
    """Evalute a single set of indent points on one line.

    NOTE: This mutates the given `elements` and `forced_indents` input to avoid
    lots of copying.
    """
    # TODO: Rethink these comments.
    # 1. Evaluate starting indent
    # 2. Evaluate any points which aren't line breaks - should they be?
    # After all evaluations, generate fixes and return - with metadata
    # to allow later functions to correct.

    # New indents on the way up?
    # The closing indent is an untaken indent in the same line.

    # New indents on the way down
    # There's a jump on the way down which *wasn't* an untaken one.
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

    # Catch edge case for first line where we'll start with a block if
    # no initial indent.
    starting_balance = indent_line.initial_indent_balance
    indent_points = indent_line.indent_points
    # Set up the default anchor
    anchor = {"before": elements[indent_points[0].idx + 1].segments[0]}

    # Find initial indent, and deduce appropriate string indent.
    # We also account for potential templated indents.
    indent_seg = None
    if indent_points[-1].last_line_break_idx:
        indent_seg = cast(
            ReflowPoint, elements[indent_points[-1].last_line_break_idx]
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
        else:
            NotImplementedError(
                "Cannot find whitespace in leading point. Report this as a bug."
            )

    if indent_seg:
        # We have to check pos marker before checking is templated.
        # Insertions don't have pos_markers - so aren't templated,
        # but also don't support calling is_templated.
        if indent_seg.is_type("placeholder"):
            # It's a consumed indent.
            current_indent = indent_seg.source_str.split("\n")[-1] or ""
        elif not indent_seg.pos_marker or not indent_seg.is_templated:
            current_indent = indent_seg.raw
        else:
            # It's templated. Handle this.
            # If it *starts* with a literal slice, then we use that as the indent.
            # Otherwise just bail out - it's a totally templated indent.
            source_slice = indent_seg.pos_marker.source_slice
            raw_slices = (
                indent_seg.pos_marker.templated_file.raw_slices_spanning_source_slice(
                    source_slice
                )
            )
            # We care most about the first one.
            # Is it literal?
            if raw_slices[0].slice_type == "literal":
                # Excellent. Take as much as we can.
                current_indent = raw_slices[0].raw[
                    source_slice.start - raw_slices[0].source_idx :
                ]
                # NOTE: There's a risk here that we take too much, but I think
                # given the first slice is literal, but we know the whole segment
                # is templated - the next MUST be something exotic.
            else:
                # It's not literal. That means it's a tag or something.
                # We know the newline wasn't templated (otherwise we wouldn't)
                # be here, so that means it's an unindented tag.
                # If we edit this indent, we should create _after_ the newline.
                for last_newline in elements[0].segments[::-1]:
                    if last_newline.is_type("newline"):
                        break
                else:
                    raise NotImplementedError(
                        "Could not find newline. Report this as a bug."
                    )
                anchor = {"after": last_newline}
                current_indent = ""
    else:
        current_indent = ""

    # First handle starting indent.
    desired_indent_units = indent_line.desired_indent_units(forced_indents)
    desired_starting_indent = desired_indent_units * single_indent
    initial_point = cast(ReflowPoint, elements[indent_points[0].idx])
    closing_balance = indent_points[-1].closing_indent_balance

    if current_indent != desired_starting_indent:
        reflow_logger.debug(
            "    Correcting indent @ line %s. Existing indent: %r -> %r",
            elements[indent_points[0].idx + 1].segments[0].pos_marker.working_line_no,
            current_indent,
            desired_starting_indent,
        )
        # Initial point gets special handling it it has no newlines.
        if indent_points[0].idx == 0 and not indent_points[0].is_line_break:
            new_fixes = [LintFix.delete(seg) for seg in initial_point.segments]
            new_point = ReflowPoint(())
        # Placeholder indents also get special treatment
        elif indent_seg and indent_seg.is_type("placeholder"):
            # From here we do a _source edit_ to edit the placeholder.
            # Back calculate the source slice from the length of the current indent.
            source_slice = slice(
                indent_seg.pos_marker.source_slice.stop - len(current_indent),
                indent_seg.pos_marker.source_slice.stop,
            )
            new_placeholder = indent_seg.edit(
                source_fixes=[
                    SourceFix(
                        desired_starting_indent,
                        source_slice,
                        indent_seg.pos_marker.templated_slice,
                    )
                ],
                source_str=indent_seg.source_str[: -len(current_indent)]
                + desired_starting_indent,
            )
            new_fixes = [
                LintFix.replace(
                    indent_seg,
                    [new_placeholder],
                )
            ]
            new_segments = [
                new_placeholder if seg is indent_seg else seg
                for seg in initial_point.segments
            ]
            new_point = ReflowPoint(tuple(new_segments))
        else:
            new_fixes, new_point = initial_point.indent_to(
                desired_starting_indent,
                **anchor,
            )
        elements[indent_points[0].idx] = new_point
        fixes += new_fixes

    # Then check for new lines. Either on the way up...
    if closing_balance > starting_balance:
        if indent_points[-1].indent_trough:
            closing_trough = (
                indent_points[-1].initial_indent_balance
                + indent_points[-1].indent_trough
            )
        else:
            closing_trough = (
                indent_points[-1].initial_indent_balance
                + indent_points[-1].indent_impulse
            )
        # On the way up we're looking for whether the ending balance
        # was an untaken indent on the way up.
        if closing_trough in indent_points[-1].untaken_indents:
            # It was! Force a new indent there.
            for ip in indent_points:
                if ip.closing_indent_balance == closing_trough:
                    target_point_idx = ip.idx
                    desired_indent = single_indent * (
                        ip.closing_indent_balance - len(ip.untaken_indents)
                    )
                    break
            else:
                NotImplementedError("We should always find the relevant point.")
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
            fixes += new_fixes
            # Keep track of the indent we forced
            forced_indents.append(closing_balance)

    # Or the way down.
    elif closing_balance < starting_balance:
        # On the way down we're looking for indents which *were* taken on
        # The way up, but currently aren't on the way down. We slice so
        # that the _last_ point isn't evaluated, because that's fine.
        for ip in indent_points[:-1]:
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
            # It's negative, not a line break and was taken on the way up.
            # This *should* be an indent!
            desired_indent = single_indent * (
                ip.closing_indent_balance
                - len(ip.untaken_indents)
                + len(forced_indents)
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

    # Remove any forced indents above the closing balance.
    # Iterate through a slice so we're not editing the thing
    # that we're iterating through.
    for i in forced_indents[:]:
        if i > closing_balance:
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
    lines = _map_line_buffers(elements)

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

    reflow_logger.debug("# Evaluate indent point buffer.")
    # Last: handle each of the lines.
    fixes = []
    # NOTE: forced_indents is mutated by _evaluate_indent_point_buffer
    # It's used to pass from one call to the next.
    forced_indents: List[int] = []
    elem_buffer = elements.copy()  # Make a working copy to mutate.
    for line in lines:
        fixes += _evaluate_indent_point_buffer(
            elem_buffer, line, single_indent, forced_indents
        )

    return elem_buffer, fixes
