"""Methods for deducing and understanding indents."""

from collections import defaultdict
import logging
from typing import Dict, Iterable, Iterator, List, Optional, Set, Tuple, cast
from dataclasses import dataclass
from sqlfluff.core.errors import SQLFluffUserError

from sqlfluff.core.parser.segments import Indent

from sqlfluff.core.parser import RawSegment, BaseSegment
from sqlfluff.core.rules.base import LintFix
from sqlfluff.utils.reflow.elements import ReflowPoint, ReflowSequenceType


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


@dataclass
class _ReindentLine:
    start_point_idx: int
    end_point_idx: int
    initial_indent_balance: int
    current_indent: str
    template_only: bool = False
    untaken_indents: Tuple[int, ...] = ()


def _is_template_only(elements: ReflowSequenceType):
    """Do the blocks in the given elements only contain templates?

    NOTE: We assume this comes "pre-sliced".
    """
    return all(
        all(seg.is_type("placeholder", "template_loop") for seg in elem.segments)
        for elem in elements
        if not isinstance(elem, ReflowPoint)
    )


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
        # Catch edge case for first line where we'll start with a block if no initial indent.
        if indent_points[-1].last_line_break_idx:
            starting_balance = indent_points[0].closing_indent_balance
        else:
            starting_balance = 0
        return cls(starting_balance, indent_points)

    def _iter_block_segments(
        self, elements: ReflowSequenceType
    ) -> Iterator[RawSegment]:
        for element in elements[self.indent_points[0].idx : self.indent_points[-1].idx]:
            if isinstance(element, ReflowPoint):
                continue
            yield from element.segments

    def is_all_comments(self, elements: ReflowSequenceType) -> bool:
        return all(
            seg.is_type("comment") for seg in self._iter_block_segments(elements)
        )

    def is_all_templates(self, elements: ReflowSequenceType) -> bool:
        return all(
            seg.is_type("placeholder", "template_loop")
            for seg in self._iter_block_segments(elements)
        )


def _revise_templated_lines(lines: List[_IndentLine], elements: ReflowSequenceType):
    """Given an initial set of individual lines. Revise templated ones.

    NOTE: This mutates the `line` argument.

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
    new_lines = lines.copy()
    # Are there any templated elements?
    templated_lines = [line for line in lines if line.template_only]
    reflow_logger.debug("Templated Lines: %s", templated_lines)

    grouped = defaultdict(list)
    for line in templated_lines:
        # I think we can assume they're a single block
        assert line.end_point_idx - line.start_point_idx == 2
        segment = elements[line.start_point_idx + 1].segments[0]
        assert segment.is_type("placeholder", "template_loop")
        # We should expect all of them to have a block uuid.
        # If not, this logic should probably be extended, maybe
        # just skip them here and leave them where they are?
        assert segment.block_uuid  # type: ignore
        grouped[segment.block_uuid].append(line)  # type: ignore

    for group_uuid in grouped.keys():
        reflow_logger.debug("Evaluating Group UUID: %s", group_uuid)
        group_lines = grouped[group_uuid]
        for line in group_lines:
            reflow_logger.debug("    Line: %s", line)

        # Check for case 1.
        if all(
            line.initial_indent_balance == group_lines[0].initial_indent_balance
            for line in group_lines
        ):
            reflow_logger.debug("    Case 1: All the same")
            continue

        # Check for case 2.
        # In this scenario, we only need to check the adjacent points.
        # If there's any wiggle room, we pick the lowest option.
        options: List[Set[int]] = []
        for line in group_lines:
            steps: Set[int] = set()
            # Run backward through the pre point.
            indent_balance = line.initial_indent_balance
            for seg in elements[line.start_point_idx].segments[::-1]:
                if seg.is_type("indent"):
                    # Minus because we're going backward.
                    indent_balance -= cast(Indent, seg).indent_val
                steps.add(indent_balance)
            # Run forward through the post point.
            indent_balance = line.initial_indent_balance
            for seg in elements[line.start_point_idx].segments:
                if seg.is_type("indent"):
                    # Minus because we're going backward.
                    indent_balance += cast(Indent, seg).indent_val
                steps.add(indent_balance)

            options.append(steps)

        # We should also work out what all the indents are _between_
        # these options and make sure we don't go above that.
        first_line_idx = new_lines.index(group_lines[0])
        last_line_idx = new_lines.index(group_lines[-1])
        reflow_logger.debug(
            "    Intermediate Lines: %s", new_lines[first_line_idx + 1 : last_line_idx]
        )
        limit_indent = min(
            line.initial_indent_balance
            for line in new_lines[first_line_idx + 1 : last_line_idx]
        )

        # Evaluate options.
        overlap = set.intersection(*options)
        # Remove any options above the limit option.
        # We minus one from the limit, because if it comes into effect
        # we'll effectively remove the effects of the indents between the elements.
        overlap = {i for i in overlap if i <= limit_indent - 1}
        reflow_logger.debug("    Overlap: %s, Limit: %s", overlap, limit_indent)
        # Is there a mutually agreeable option?
        if overlap:
            best_indent = min(overlap)
            reflow_logger.debug(
                "    Case 2: Best: %s, Overlap: %s", best_indent, overlap
            )
        # If no overlap, it's case 3
        else:
            # Set the indent to the minimum of the existing ones.
            best_indent = min(line.initial_indent_balance for line in group_lines)
            reflow_logger.debug("    Case 3: Best: %s", best_indent)
            # Remove one indent from all intermediate lines.
            # This is because we're effectively saying that these
            # placeholders shouldn't impact the indentation within them.
            for line in new_lines[first_line_idx + 1 : last_line_idx]:
                if line not in group_lines:
                    line.initial_indent_balance -= 1

        # Set all the lines to this indent
        for idx in range(len(new_lines)):
            if new_lines[idx] in group_lines:
                new_lines[idx].initial_indent_balance = best_indent

    return new_lines


def _revise_comment_lines(lines: List[_IndentLine], elements: ReflowSequenceType):
    """Given an initial set of individual lines. Revise comment ones.

    NOTE: This mutates the `line` argument.

    We do this to ensure that lines with comments are aligned to
    the following non-comment element.
    """
    new_lines: List[_ReindentLine] = []
    comment_line_buffer: List[_ReindentLine] = []
    for line in lines:
        is_comment_only_line = all(
            all(seg.is_type("comment") for seg in elem.segments)
            for elem in elements[line.idx : line.end_point_idx]
            if not isinstance(elem, ReflowPoint)
        )
        if is_comment_only_line:
            comment_line_buffer.append(line)
        else:
            # Not a comment only line, if there's a buffer anchor
            # to this one.
            for comment_line in comment_line_buffer:
                # There is a mutation risk here but we don't plan
                # on reusing the initial buffer so it's probably ok.
                comment_line.initial_indent_balance = line.initial_indent_balance
                new_lines.append(comment_line)
                reflow_logger.debug(
                    "Comment Only Line: %s. Anchoring to %s", comment_line, line
                )
            # Reset the buffer
            comment_line_buffer = []
            # Keep the line itself.
            new_lines.append(line)
    # Any trailing comments should be anchored the baseline.
    for comment_line in comment_line_buffer:
        comment_line.initial_indent_balance = 0
        new_lines.append(comment_line)
        reflow_logger.debug(
            "Comment Only Line: %s. Anchoring to baseline", comment_line
        )
    return new_lines


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
    """Crawl through a reflow sequence, mapping existing indents."""
    last_line_break_idx = None
    indent_balance = 0
    untaken_indents: Tuple[int, ...] = ()
    for idx, elem in enumerate(elements):
        if isinstance(elem, ReflowPoint):
            indent_impulse, indent_trough = elem.get_indent_impulse()

            # Is it a line break?
            if "newline" in elem.class_types and idx != last_line_break_idx:
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
            # Is it otherwise meaningful as an indent point?
            # NOTE, a point at idx zero is meaningful because it's like an indent.
            elif indent_impulse or indent_trough or idx == 0:
                yield _IndentPoint(
                    idx,
                    indent_impulse,
                    indent_trough,
                    indent_balance,
                    last_line_break_idx,
                    False,
                    untaken_indents,
                )
                # Are there untaken positive indents in here?
                for i in range(0, indent_impulse):
                    untaken_indents += (indent_balance + i + 1,)

            # Update values
            indent_balance += indent_impulse

            # Strip any untaken indents above the trough.
            untaken_indents = tuple(
                x for x in untaken_indents if x <= indent_balance + indent_trough
            )


def _map_line_buffers(elements: ReflowSequenceType) -> List[_IndentLine]:
    """Map the existing elements, building up a list of _IndentLine"""
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
    ### TODO: ADD LOTS MORE LOGGING HERE

    # 1. Evaluate starting indent
    # 2. Evalutate any points which aren't line breaks - should they be?
    # After all evaluations, generate fixes and return - with metadata to allow later functions to correct.

    # New indents on the way up?
    # The closing indent is an untaken indent in the same line.

    # New indents on the way down
    # There's a jump on the way down which *wasn't* an untaken one.
    reflow_logger.debug("Evaluate Line: %s. FI %s", indent_line, forced_indents)
    fixes = []

    # Catch edge case for first line where we'll start with a block if no initial indent.
    starting_balance = indent_line.initial_indent_balance
    indent_points = indent_line.indent_points
    if indent_points[-1].last_line_break_idx:
        current_indent = elements[indent_points[-1].last_line_break_idx].get_indent()
    elif isinstance(elements[0], ReflowPoint):
        current_indent = elements[0].raw
    else:
        current_indent = ""

    # First handle starting indent.
    desired_starting_indent = single_indent * (
        starting_balance - len(indent_points[0].untaken_indents) + len(forced_indents)
    )
    initial_point = elements[indent_points[0].idx]
    closing_balance = indent_points[-1].closing_indent_balance

    if current_indent != desired_starting_indent:
        reflow_logger.debug(
            "  Correcting indent @ line %s. Existing indent: %r -> %r",
            elements[indent_points[0].idx + 1].segments[0].pos_marker.working_line_no,
            current_indent,
            desired_starting_indent,
        )
        # Initial point gets special handling it it has no newlines.
        if indent_points[0].idx == 0 and not indent_points[0].is_line_break:
            new_fixes = [LintFix.delete(seg) for seg in initial_point.segments]
            new_point = ReflowPoint(())
        else:
            new_fixes, new_point = initial_point.indent_to(
                desired_starting_indent,
                before=elements[indent_points[0].idx + 1].segments[0],
            )
        elements[indent_points[0].idx] = new_point
        fixes += new_fixes

    # Then check for new lines. Either on the way up...
    if closing_balance > starting_balance:
        # On the way up we're looking for whether the ending balance
        # was an untaken indent on the way up.
        if closing_balance in indent_points[-1].untaken_indents:
            # It was! Force a new indent there.
            for ip in indent_points:
                if ip.closing_indent_balance == closing_balance:
                    target_point_idx = ip.idx
                    desired_indent = single_indent * (
                        ip.closing_indent_balance - len(ip.untaken_indents)
                    )
                    break
            else:
                NotImplementedError("We should always find the relevant point.")
            reflow_logger.debug(
                "  Detected missing +ve line break @ line %s. Indenting to %r",
                elements[target_point_idx + 1].segments[0].pos_marker.working_line_no,
                desired_indent,
            )
            target_point = elements[target_point_idx]
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
                ip.closing_indent_balance in ip.untaken_indents
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
                "  Detected missing -ve line break @ line %s. Indenting to %r",
                elements[ip.idx + 1].segments[0].pos_marker.working_line_no,
                desired_indent,
            )
            target_point = elements[ip.idx]
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

    # TODO: RE-ENABLE
    # Revise templated indents
    # _revise_templated_lines(lines, elements)
    # Revise comment indents
    # _revise_comment_lines(lines, elements)
    # SKIP ELEMENTS WE'RE NOT SUPPOSED TO REINDENT IN (i.e. scripts).

    # Last: handle each of the lines.
    fixes = []
    forced_indents = []
    elem_buffer = elements.copy()  # Make a working copy to mutate.
    for line in lines:
        fixes += _evaluate_indent_point_buffer(
            elem_buffer, line, single_indent, forced_indents
        )

    return elem_buffer, fixes
