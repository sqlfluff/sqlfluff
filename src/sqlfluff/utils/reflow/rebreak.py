"""Static methods to support ReflowSequence.rebreak()."""

import logging
from dataclasses import dataclass

from typing import List, Type, Tuple, cast

from sqlfluff.core.parser import BaseSegment
from sqlfluff.core.rules import LintFix

from sqlfluff.utils.reflow.elements import ReflowBlock, ReflowPoint, ReflowSequenceType
from sqlfluff.utils.reflow.reindent import deduce_line_indent


# We're in the utils module, but users will expect reflow
# logs to appear in the context of rules. Hence it's a subset
# of the rules logger.
reflow_logger = logging.getLogger("sqlfluff.rules.reflow")


@dataclass(frozen=True)
class _RebreakSpan:
    """A location within a sequence to consider rebreaking."""

    target: BaseSegment
    start_idx: int
    end_idx: int
    line_position: str
    strict: bool


@dataclass(frozen=True)
class _RebreakIndices:
    """Indices of points for a _RebreakLocation."""

    dir: int
    adj_pt_idx: int
    newline_pt_idx: int
    pre_code_pt_idx: int

    @classmethod
    def from_elements(
        cls: Type["_RebreakIndices"],
        elements: ReflowSequenceType,
        start_idx: int,
        dir: int,
    ) -> "_RebreakIndices":
        """Iterate through the elements to deduce important point indices."""
        assert dir in (1, -1), "Direction must be a unit direction (i.e. 1 or -1)."
        # Limit depends on the direction
        limit = 0 if dir == -1 else len(elements)
        # The adjacent point is just the next one.
        adj_point_idx = start_idx + dir
        # The newline point is next. We hop in 2s because we're checking
        # only points, which alternate with blocks.
        for newline_point_idx in range(adj_point_idx, limit, 2 * dir):
            if "newline" in elements[newline_point_idx].class_types or any(
                seg.is_code for seg in elements[newline_point_idx + dir].segments
            ):
                break
        # Finally we look for the point preceding the next code element.
        for pre_code_point_idx in range(newline_point_idx, limit, 2 * dir):
            if any(seg.is_code for seg in elements[pre_code_point_idx + dir].segments):
                break
        return cls(dir, adj_point_idx, newline_point_idx, pre_code_point_idx)


@dataclass(frozen=True)
class _RebreakLocation:
    """A location within a sequence to rebreak, with metadata."""

    target: BaseSegment
    prev: _RebreakIndices
    next: _RebreakIndices
    line_position: str
    strict: bool

    @classmethod
    def from_span(
        cls: Type["_RebreakLocation"], span: _RebreakSpan, elements: ReflowSequenceType
    ) -> "_RebreakLocation":
        """Expand a span to a location."""
        return cls(
            span.target,
            _RebreakIndices.from_elements(elements, span.start_idx, -1),
            _RebreakIndices.from_elements(elements, span.end_idx, 1),
            span.line_position,
            span.strict,
        )

    def has_templated_newline(self, elements: ReflowSequenceType) -> bool:
        """Is either side a templated newline?

        If either side has a templated newline, then that's ok too.
        The intent here is that if the next newline is a _templated_
        one, then in the source there will be a tag ({{ tag }}), which
        acts like _not having a newline_.
        """
        # Check the _last_ newline of the previous point.
        # Slice backward to search in reverse.
        for seg in elements[self.prev.newline_pt_idx].segments[::-1]:
            if seg.is_type("newline"):
                if not seg.pos_marker.is_literal():
                    return True
                break
        # Check the _first_ newline of the next point.
        for seg in elements[self.next.newline_pt_idx].segments:
            if seg.is_type("newline"):
                if not seg.pos_marker.is_literal():
                    return True
                break
        return False

    def has_inappropriate_newlines(
        self, elements: ReflowSequenceType, strict: bool = False
    ) -> bool:
        """Is the span surrounded by one (but not two) line breaks?

        Args:
            elements: The elements of the ReflowSequence this element
               is taken from to allow comparison.
            strict (:obj:`bool`): If set to true, this will not allow
               the case where there aren't newlines on either side.
        """
        # Here we use the newline index, not
        # just the adjacent point, so that we can see past comments.
        n_prev_newlines = elements[self.prev.newline_pt_idx].num_newlines()
        n_next_newlines = elements[self.next.newline_pt_idx].num_newlines()
        newlines_on_neither_side = n_prev_newlines + n_next_newlines == 0
        newlines_on_both_sides = n_prev_newlines > 0 and n_next_newlines > 0
        return (
            # If there isn't a newline on either side then carry
            # on, unless it's strict.
            (newlines_on_neither_side and not strict)
            # If there is a newline on BOTH sides. That's ok.
            or newlines_on_both_sides
        )


def identify_rebreak_spans(
    element_buffer: ReflowSequenceType, root_segment: BaseSegment
) -> List[_RebreakSpan]:
    """Identify areas in file to rebreak.

    A span here is a block, or group of blocks which have
    explicit configs for their line position, either directly
    as raw segments themselves or by virtue of one of their
    parent segments.
    """
    spans: List[_RebreakSpan] = []
    # We'll need at least two elements each side, so constrain
    # our range accordingly.
    for idx in range(2, len(element_buffer) - 2):
        # Only evaluate blocks:
        elem = element_buffer[idx]
        # Only evaluate blocks
        if not isinstance(elem, ReflowBlock):
            continue
        # Does the element itself have config? (The easy case)
        if elem.line_position:
            # Blocks should only have one segment so it's easy to pick it.
            spans.append(
                _RebreakSpan(
                    elem.segments[0],
                    idx,
                    idx,
                    # NOTE: this isn't pretty but until it needs to be more
                    # complex, this works.
                    elem.line_position.split(":")[0],
                    elem.line_position.endswith("strict"),
                )
            )
        # Do any of its parents have config, and are we at the start
        # of them?
        for key in elem.line_position_configs.keys():
            # If we're not at the start of the segment, then pass.
            if elem.depth_info.stack_positions[key].idx != 0:
                continue
            # Can we find the end?
            for end_idx in range(idx, len(element_buffer) - 2):
                end_elem = element_buffer[end_idx]
                if not isinstance(end_elem, ReflowBlock):
                    continue
                if end_elem.depth_info.stack_positions[key].type in ("end", "solo"):
                    # Found the end. Add it to the stack.
                    # We reference the appropriate element from the parent stack.
                    target_depth = elem.depth_info.stack_hashes.index(key)
                    target = root_segment.path_to(element_buffer[idx].segments[0])[
                        target_depth
                    ].segment
                    spans.append(
                        _RebreakSpan(
                            target,
                            idx,
                            end_idx,
                            # NOTE: this isn't pretty but until it needs to be more
                            # complex, this works.
                            elem.line_position_configs[key].split(":")[0],
                            elem.line_position_configs[key].endswith("strict"),
                        )
                    )
                    break
            # If we find the start, but not the end, it's not a problem, but
            # we won't be rebreaking this span. This is important so that we
            # don't rebreak part of something without the context of what's
            # in the rest of it. We continue without adding it to the buffer.
    return spans


def rebreak_sequence(
    elements: ReflowSequenceType, root_segment: BaseSegment
) -> Tuple[ReflowSequenceType, List[LintFix]]:
    """Reflow line breaks within a sequence.

    Initially this only _moves_ existing segments
    around line breaks (e.g. for operators and commas),
    but eventually this method should also handle line
    length considerations too.

    This intentionally does *not* handle indentation,
    as the existing indents are assumed to be correct.
    """
    fixes: List[LintFix] = []
    elem_buff: ReflowSequenceType = elements.copy()

    # Given a sequence we should identify the objects which
    # make sense to rebreak. That includes any raws with config,
    # but also and parent segments which have config and we can
    # find both ends for. Given those spans, we then need to find
    # the points either side of them and then the blocks either
    # side to respace them at the same time.

    # 1. First find appropriate spans.
    spans = identify_rebreak_spans(elem_buff, root_segment)

    # The spans give us the edges of operators, but for line positioning we need
    # to handle comments differently. There are two other important points:
    # 1. The next newline outward before code (but passing over comments).
    # 2. The point before the next _code_ segment (ditto comments).
    locations = [_RebreakLocation.from_span(span, elem_buff) for span in spans]

    # Handle each span:
    for loc in locations:

        reflow_logger.debug(
            "Handing Rebreak Span (%r: %s): %r",
            loc.line_position,
            loc.target,
            "".join(
                elem.raw
                for elem in elem_buff[
                    loc.prev.pre_code_pt_idx - 1 : loc.next.pre_code_pt_idx + 2
                ]
            ),
        )

        if loc.has_inappropriate_newlines(elem_buff, strict=loc.strict):
            continue

        if loc.has_templated_newline(elem_buff):
            continue

        # Points and blocks either side are just offsets from the indices.
        prev_point = cast(ReflowPoint, elem_buff[loc.prev.adj_pt_idx])
        next_point = cast(ReflowPoint, elem_buff[loc.next.adj_pt_idx])

        # So we know we have a preference, is it ok?
        if loc.line_position == "leading":
            if elem_buff[loc.prev.newline_pt_idx].num_newlines():
                # We're good. It's already leading.
                continue
            # Is it the simple case with no comments between the
            # old and new desired locations and only a single following
            # whitespace?
            elif (
                loc.next.adj_pt_idx == loc.next.pre_code_pt_idx
                and elem_buff[loc.next.newline_pt_idx].num_newlines() == 1
            ):
                reflow_logger.debug("  Trailing Easy Case")
                # Simple case. No comments.
                # Strip newlines from the next point. Apply the indent to
                # the previous point.
                fixes, prev_point = prev_point.indent_to(
                    next_point.get_indent() or "", before=loc.target
                )
                fixes, next_point = next_point.respace_point(
                    cast(ReflowBlock, elem_buff[loc.next.adj_pt_idx - 1]),
                    cast(ReflowBlock, elem_buff[loc.next.adj_pt_idx + 1]),
                    root_segment=root_segment,
                    fixes=fixes,
                    strip_newlines=True,
                )
                # Update the points in the buffer
                elem_buff[loc.prev.adj_pt_idx] = prev_point
                elem_buff[loc.next.adj_pt_idx] = next_point
            else:
                reflow_logger.debug("  Trailing Tricky Case")
                # Otherwise we've got a tricky scenario where there are comments
                # to negotiate around. In this case, we _move the target_
                # rather than just adjusting the whitespace.

                # Delete the existing position of the target, and
                # the _preceding_ point.
                fixes.append(LintFix.delete(loc.target))
                for seg in elem_buff[loc.prev.adj_pt_idx].segments:
                    fixes.append(LintFix.delete(seg))

                # We always reinsert after the first point, but respace
                # the inserted point to ensure it's the right size given
                # configs.
                fixes, new_point = ReflowPoint(()).respace_point(
                    cast(ReflowBlock, elem_buff[loc.next.adj_pt_idx - 1]),
                    cast(ReflowBlock, elem_buff[loc.next.pre_code_pt_idx + 1]),
                    root_segment=root_segment,
                    fixes=fixes,
                    anchor_on="after",
                )
                fixes.append(
                    LintFix.create_after(
                        elem_buff[loc.next.pre_code_pt_idx].segments[-1],
                        [loc.target],
                    )
                )

                elem_buff = (
                    elem_buff[: loc.prev.adj_pt_idx]
                    + elem_buff[loc.next.adj_pt_idx : loc.next.pre_code_pt_idx + 1]
                    + elem_buff[
                        loc.prev.adj_pt_idx + 1 : loc.next.adj_pt_idx
                    ]  # the target
                    + [new_point]
                    + elem_buff[loc.next.pre_code_pt_idx + 1 :]
                )

        elif loc.line_position == "trailing":
            if elem_buff[loc.next.newline_pt_idx].num_newlines():
                # We're good, it's already trailing.
                continue
            # Is it the simple case with no comments between the
            # old and new desired locations and only one previous newline?
            elif (
                loc.prev.adj_pt_idx == loc.prev.pre_code_pt_idx
                and elem_buff[loc.prev.newline_pt_idx].num_newlines() == 1
            ):
                reflow_logger.debug("  Leading Easy Case")
                # Simple case. No comments.
                # Strip newlines from the previous point. Apply the indent
                # to the next point.
                fixes, next_point = next_point.indent_to(
                    prev_point.get_indent() or "", after=loc.target
                )
                fixes, prev_point = prev_point.respace_point(
                    cast(ReflowBlock, elem_buff[loc.prev.adj_pt_idx - 1]),
                    cast(ReflowBlock, elem_buff[loc.prev.adj_pt_idx + 1]),
                    root_segment=root_segment,
                    fixes=fixes,
                    strip_newlines=True,
                )
                # Update the points in the buffer
                elem_buff[loc.prev.adj_pt_idx] = prev_point
                elem_buff[loc.next.adj_pt_idx] = next_point
            else:
                reflow_logger.debug("  Leading Tricky Case")
                # Otherwise we've got a tricky scenario where there are comments
                # to negotiate around. In this case, we _move the target_
                # rather than just adjusting the whitespace.

                # Delete the existing position of the target, and
                # the _following_ point.
                fixes.append(LintFix.delete(loc.target))
                for seg in elem_buff[loc.next.adj_pt_idx].segments:
                    fixes.append(LintFix.delete(seg))

                # We always reinsert before the first point, but respace
                # the inserted point to ensure it's the right size given
                # configs.
                fixes, new_point = ReflowPoint(()).respace_point(
                    cast(ReflowBlock, elem_buff[loc.prev.pre_code_pt_idx - 1]),
                    cast(ReflowBlock, elem_buff[loc.prev.adj_pt_idx + 1]),
                    root_segment=root_segment,
                    fixes=fixes,
                    anchor_on="before",
                )
                fixes.append(
                    LintFix.create_before(
                        elem_buff[loc.prev.pre_code_pt_idx].segments[0],
                        [loc.target],
                    )
                )

                elem_buff = (
                    elem_buff[: loc.prev.pre_code_pt_idx]
                    + [new_point]
                    + elem_buff[
                        loc.prev.adj_pt_idx + 1 : loc.next.adj_pt_idx
                    ]  # the target
                    + elem_buff[loc.prev.pre_code_pt_idx : loc.prev.adj_pt_idx + 1]
                    + elem_buff[loc.next.adj_pt_idx + 1 :]
                )

        elif loc.line_position == "alone":
            # If we get here we can assume that the element is currently
            # either leading or trailing and needs to be moved onto its
            # own line.

            # First handle the following newlines first (easy).
            if not elem_buff[loc.next.newline_pt_idx].num_newlines():
                reflow_logger.debug("  Found missing newline after in alone case")
                pre_fixes, next_point = next_point.indent_to(
                    deduce_line_indent(loc.target.raw_segments[-1], root_segment),
                    after=loc.target,
                )
                fixes += pre_fixes
                # Update the point in the buffer
                elem_buff[loc.next.adj_pt_idx] = next_point

            # Then handle newlines before. (hoisting past comments if needed).
            if not elem_buff[loc.prev.adj_pt_idx].num_newlines():
                reflow_logger.debug("  Found missing newline before in alone case")
                # NOTE: In the case that there are comments _after_ the
                # target, they will be moved with it. This might break things
                # but there isn't an unambiguous way to do this, because we
                # can't be sure what the comments are referring to.
                # Given that, we take the simple option.
                post_fixes, prev_point = prev_point.indent_to(
                    deduce_line_indent(loc.target.raw_segments[0], root_segment),
                    before=loc.target,
                )
                fixes += post_fixes
                # Update the point in the buffer
                elem_buff[loc.prev.adj_pt_idx] = prev_point

        else:
            raise NotImplementedError(  # pragma: no cover
                f"Unexpected line_position config: {loc.line_position}"
            )

    return elem_buff, fixes
