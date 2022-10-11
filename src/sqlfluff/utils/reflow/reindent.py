"""Methods for deducing and understanding indents."""

from collections import defaultdict
import logging
from typing import List, Set, Tuple, cast
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


def _revise_templated_lines(
    lines: List[_ReindentLine], elements: ReflowSequenceType
) -> List[_ReindentLine]:
    """Given an initial set of individual lines. Revise templated ones.

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


def map_reindent_lines(
    elements: ReflowSequenceType, initial_balance: int = 0
) -> List[_ReindentLine]:
    """Scan the sequence to map individual lines to indent."""
    init_idx = 0
    last_pt_idx = 0
    if elements and isinstance(elements[0], ReflowPoint):
        indent = elements[0].get_indent()
        # The initial point is a special case where we allow
        # .raw if .get_indent() returns None. That's because
        # the initial point may have no newline (i.e. the start
        # of the file).
        if indent is None:
            indent = elements[0].raw
    else:
        indent = ""
    indent_balance = initial_balance
    last_indent_balance = indent_balance
    result: List[_ReindentLine] = []
    untaken_indents: Tuple[int, ...] = ()
    last_untaken_indents = untaken_indents
    for idx, elem in enumerate(elements):
        if isinstance(elem, ReflowPoint):
            last_pt_idx = idx
            indent_impulse = elem.get_indent_impulse()
            indent_balance += indent_impulse

            # If our current indent balance is less than any untaken indent
            # levels then remove them.
            if any(x > indent_balance for x in untaken_indents):
                untaken_indents = tuple(x for x in untaken_indents if x <= indent_balance)

            # Have we found a newline?
            # We skip the trivial matches (mostly to avoid a weird start).
            if "newline" in elem.class_types and idx != init_idx:
                # Detect template markers alone on lines at this stage, because
                # we'll handle them a bit differently later.
                result.append(
                    _ReindentLine(
                        init_idx,
                        idx,
                        last_indent_balance,
                        indent,
                        _is_template_only(elements[init_idx : idx + 1]),
                        # Only report untaken indents less than the balance
                        untaken_indents=last_untaken_indents,
                    )
                )
                # Set the index and indent for next time
                indent = elem.get_indent() or ""
                init_idx = idx
                last_indent_balance = indent_balance
                last_untaken_indents = untaken_indents
            elif indent_impulse > 0:
                # If there's no newline, but there _is_ a positive impulse
                # then this is an untaken indent. Keep track of it.
                untaken_indents = untaken_indents + (indent_balance,)

    # Do we have meaningful content at the end.
    # NOTE: we don't handle any indent before the end_of_file segment.
    # Which is why we use last_pt_idx not just len(elements).
    if last_pt_idx - init_idx > 1:
        result.append(
            _ReindentLine(
                init_idx,
                last_pt_idx,
                last_indent_balance,
                indent,
                _is_template_only(elements[init_idx : last_pt_idx + 1]),
                untaken_indents=last_untaken_indents,
            )
        )

    return _revise_templated_lines(result, elements)


def lint_reindent_lines(
    elements: ReflowSequenceType,
    lines: List[_ReindentLine],
    indent_unit: str,
    tab_space_size: int,
):
    """Given _ReindentLines, lint what we've got.

    Each line is compared to the previous _good_ line with
    either the _same_ or _less_ indent balance than this one.

    To facilitate that, we maintain a stack of _ReindentLine
    objects to not need to go back and scan through all of them
    to do comparisons.

    Additionally, an indent balance of 0, implies there should
    be no indent, regardless of previous lines. This also allows
    us to clear the stack any time we reach 0.
    """
    if indent_unit == "tab":
        single_indent = "\t"
    elif indent_unit == "space":
        single_indent = " " * tab_space_size
    else:
        raise SQLFluffUserError(
            f"Expected indent_unit of 'tab' or 'space', instead got {indent_unit}"
        )

    stack: List[_ReindentLine] = []
    fixes: List[LintFix] = []
    element_buffer = elements.copy()
    # Iterate through the lines.
    for line in lines:
        # Three scenarios:
        # 1.  It's got an indent balance of zero.
        # 2a. There's a balance, and a stack.
        # 2b. There's a balance and no stack.

        # 2a can degrade to 2b, if there isn't an appropriate
        # comparison on the stack.

        start_point = cast(ReflowPoint, element_buffer[line.start_point_idx])

        # Handle the zero case first.
        if line.initial_indent_balance == 0:
            # Clear stack, we reached zero
            stack = []
            # If there's an indent, remove it.
            if line.current_indent:
                reflow_logger.debug(
                    "Reindent. Line %s. Zero line with indent. Fixing.", line
                )
                # The first line gets special handling, because it
                # contains no newline.
                if line.start_point_idx == 0:
                    if start_point.segments:
                        new_fixes = [
                            LintFix.delete(seg) for seg in start_point.segments
                        ]
                        new_point = ReflowPoint(())
                    else:
                        new_fixes, new_point = [], start_point
                # Otherwise use the normal indent logic
                else:
                    new_fixes, new_point = start_point.indent_to("")
                fixes.extend(new_fixes)
                # Replace with new point
                element_buffer[line.start_point_idx] = new_point
            continue

        # Prune anything from the stack which has a higher balance.
        for idx in range(len(stack) - 1, -1, -1):
            # Is it a good comparison point?
            if stack[idx].initial_indent_balance <= line.initial_indent_balance:
                # Good
                break
            else:
                # Otherwise get rid of it.
                stack.pop(idx)

        # Is there a stack left?
        if stack:
            # We're comparing to the top of the stack
            comparison = stack[-1]
            reflow_logger.debug("Reindent. Line %s. Comparing to %s.", line, comparison)
            desired_indent = comparison.current_indent + (
                single_indent
                * (line.initial_indent_balance - comparison.initial_indent_balance)
            )
            deeper = line.initial_indent_balance > comparison.initial_indent_balance
        else:
            # Without a stack to compare to we assume we're comparing to the baseline.
            reflow_logger.debug("Reindent. Line %s. Comparing to baseline.", line)
            desired_indent = single_indent * line.initial_indent_balance
            deeper = True

        if line.current_indent == desired_indent:
            # It's good. Add it to the stack, if we're deeper.
            if deeper:
                stack += [line]
        else:
            # It's not good. Adjust it.
            reflow_logger.debug(
                "Reindent. Line %s. %r != %r. Fixing",
                line,
                line.current_indent,
                desired_indent,
            )
            new_fixes, new_point = start_point.indent_to(desired_indent)
            fixes.extend(new_fixes)
            # Replace with new point
            element_buffer[line.start_point_idx] = new_point

    # Return the adjusted buffers.
    return element_buffer, fixes
