"""Methods for deducing and understanding indents."""

import logging
from typing import List, cast
from dataclasses import dataclass

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


def _is_template_only(elements: ReflowSequenceType):
    """Do the blocks in the given elements only contain templates?

    NOTE: We assume this comes "pre-sliced".
    """
    return all(
        all(seg.is_type("placeholder", "template_loop") for seg in elem.segments)
        for elem in elements
        if not isinstance(elem, ReflowPoint)
    )


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
    for idx, elem in enumerate(elements):
        if isinstance(elem, ReflowPoint):
            last_pt_idx = idx
            indent_balance += elem.get_indent_impulse()
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
                    )
                )
                # Set the index and indent for next time
                indent = elem.get_indent() or ""
                init_idx = idx
                last_indent_balance = indent_balance
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
            )
        )

    return result


def lint_reindent_lines(elements: ReflowSequenceType, lines: List[_ReindentLine]):
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
    stack: List[_ReindentLine] = []
    fixes: List[LintFix] = []
    element_buffer = elements.copy()
    # TODO: This should be driven by config!
    indent_unit = "  "
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
                indent_unit
                * (line.initial_indent_balance - comparison.initial_indent_balance)
            )
            deeper = line.initial_indent_balance > comparison.initial_indent_balance
        else:
            # Without a stack to compare to we assume we're comparing to the baseline.
            reflow_logger.debug("Reindent. Line %s. Comparing to baseline.", line)
            desired_indent = indent_unit * line.initial_indent_balance
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
