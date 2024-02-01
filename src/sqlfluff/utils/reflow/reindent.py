"""Methods for deducing and understanding indents."""

import logging
from collections import defaultdict
from dataclasses import dataclass
from itertools import chain
from typing import (
    DefaultDict,
    Dict,
    FrozenSet,
    Iterator,
    List,
    Optional,
    Set,
    Tuple,
    cast,
)

from sqlfluff.core.errors import SQLFluffUserError
from sqlfluff.core.helpers.slice import slice_length
from sqlfluff.core.parser import (
    BaseSegment,
    NewlineSegment,
    RawSegment,
    WhitespaceSegment,
)
from sqlfluff.core.parser.segments import Indent, SourceFix
from sqlfluff.core.parser.segments.meta import MetaSegment, TemplateSegment
from sqlfluff.core.rules import LintFix, LintResult
from sqlfluff.utils.reflow.elements import (
    IndentStats,
    ReflowBlock,
    ReflowPoint,
    ReflowSequenceType,
)
from sqlfluff.utils.reflow.helpers import fixes_from_results
from sqlfluff.utils.reflow.rebreak import _RebreakSpan, identify_rebreak_spans

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
        if seg.is_type("newline") and (
            not seg.pos_marker or seg.pos_marker.is_literal()
        ):
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
    def closing_indent_balance(self) -> int:
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

    def __repr__(self) -> str:
        """Compressed repr method to ease logging."""
        return (
            f"IndentLine(iib={self.initial_indent_balance}, ipts=["
            + ", ".join(
                f"iPt@{ip.idx}({ip.indent_impulse}, {ip.indent_trough}, "
                f"{ip.initial_indent_balance}, {ip.last_line_break_idx}, "
                f"{ip.is_line_break}, {ip.untaken_indents})"
                for ip in self.indent_points
            )
            + "])"
        )

    @classmethod
    def from_points(cls, indent_points: List[_IndentPoint]) -> "_IndentLine":
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

    def desired_indent_units(self, forced_indents: List[int]) -> int:
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

    def closing_balance(self) -> int:
        """The closing indent balance of the line."""
        return self.indent_points[-1].closing_indent_balance

    def opening_balance(self) -> int:
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
            # So handle all blocks on the line.
            for i in range(line.indent_points[0].idx, line.indent_points[-1].idx):
                if isinstance(elements[i], ReflowPoint):
                    continue
                # We already checked that it's all templates.
                segment = cast(MetaSegment, elements[i].segments[0])
                assert segment.is_type("placeholder", "template_loop")
                # If it's not got a block uuid, it's not a block, so it
                # should just be indented as usual. No need to revise.
                # e.g. comments or variables
                if segment.block_uuid:
                    grouped[segment.block_uuid].append(idx)
                    depths[segment.block_uuid].append(line.initial_indent_balance)
                    reflow_logger.debug(
                        "  UUID: %s @ %s = %r",
                        segment.block_uuid,
                        idx,
                        segment.pos_marker.source_str(),
                    )

    # Sort through the lines, so we do to *most* indented first.
    sorted_group_indices = sorted(
        grouped.keys(), key=lambda x: max(depths[x]), reverse=True
    )
    reflow_logger.debug("  Sorted Group UUIDs: %s", sorted_group_indices)

    for group_idx, group_uuid in enumerate(sorted_group_indices):
        reflow_logger.debug("  Evaluating Group UUID: %s", group_uuid)

        group_lines = grouped[group_uuid]

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
            first_point_idx = line.indent_points[0].idx
            first_block = elements[first_point_idx + 1]

            assert first_block.segments
            first_segment = first_block.segments[0]
            if first_segment.is_type("template_loop"):
                # For template loops, don't count the line. They behave
                # strangely.
                continue

            for i in range(first_point_idx, 0, -1):
                if isinstance(elements[i], ReflowPoint):
                    for seg in elements[i].segments[::-1]:
                        if seg.is_type("indent"):
                            # If it's the one straight away, after a block_end or
                            # block_mid, skip it. We know this because it will have
                            # block_uuid.
                            if cast(Indent, seg).block_uuid:
                                continue
                            # Minus because we're going backward.
                            indent_balance -= cast(Indent, seg).indent_val
                            steps.add(indent_balance)
                # if it's anything other than a blank placeholder, break.
                # NOTE: We still need the forward version of this.
                elif not elements[i].segments[0].is_type("placeholder"):
                    break
                elif cast(TemplateSegment, elements[i].segments[0]).block_type not in (
                    "block_start",
                    "block_end",
                    "skipped_source",
                    "block_mid",
                ):
                    # Recreating this condition is hard, but we shouldn't allow any
                    # rendered content here.
                    break  # pragma: no cover

            # Run forward through the post point.
            indent_balance = line.initial_indent_balance
            last_point_idx = line.indent_points[-1].idx
            for seg in elements[last_point_idx].segments:
                if seg.is_type("indent"):
                    # If it's the one straight away, after a block_start or
                    # block_mid, skip it. We know this because it will have
                    # block_uuid.
                    if cast(Indent, seg).block_uuid:
                        continue
                    # Positive because we're going forward.
                    indent_balance += cast(Indent, seg).indent_val
                    steps.add(indent_balance)

            # NOTE: Edge case for consecutive blocks of the same type.
            # If we're next to another block which is "inner" (i.e.) has
            # already been handled. We can assume all options up to it's
            # new indent are open for use.

            _case_type = None
            if first_segment.is_type("placeholder"):
                _case_type = cast(TemplateSegment, first_segment).block_type

            if _case_type in ("block_start", "block_mid"):
                # Is following _line_ AND element also a block?
                # i.e. nothing else between.
                if (
                    idx + 1 < len(lines)
                    and first_point_idx + 3 == lines[idx + 1].indent_points[0].idx + 1
                ):
                    seg = elements[first_point_idx + 3].segments[0]
                    if seg.is_type("placeholder"):
                        if cast(TemplateSegment, seg).block_type == "block_start":
                            _inter_steps = list(
                                range(
                                    line.initial_indent_balance,
                                    lines[idx + 1].initial_indent_balance,
                                )
                            )
                            reflow_logger.debug(
                                "      Precedes block. Adding Steps: %s", _inter_steps
                            )
                            steps.update(_inter_steps)

            if _case_type in ("block_end", "block_mid"):
                # Is preceding _line_ AND element also a block?
                # i.e. nothing else between.
                if first_point_idx - 1 == lines[idx - 1].indent_points[0].idx + 1:
                    seg = elements[first_point_idx - 1].segments[0]
                    if seg.is_type("placeholder"):
                        if cast(TemplateSegment, seg).block_type == "block_end":
                            _inter_steps = list(
                                range(
                                    line.initial_indent_balance,
                                    lines[idx - 1].initial_indent_balance,
                                )
                            )
                            reflow_logger.debug(
                                "      Follows block. Adding Steps: %s", _inter_steps
                            )
                            steps.update(_inter_steps)

            reflow_logger.debug(
                "    Line %s: Initial Balance: %s Options: %s",
                idx,
                lines[idx].initial_indent_balance,
                steps,
            )
            options.append(steps)

        # We should also work out what all the indents are _between_
        # these options and make sure we don't go above that.

        # Because there might be _outer_ loops, we look for spans
        # between blocks in this group which don't contain any blocks
        # from _outer_ loops. i.e. we can't just take all the lines from
        # first to last.
        last_group_line: Optional[int] = group_lines[0]  # last = previous.
        net_balance = 0
        balance_trough: Optional[int] = None
        temp_balance_trough: Optional[int] = None
        inner_lines = []
        reflow_logger.debug("    Intermediate lines:")
        # NOTE: +1 on the last range to make sure we _do_ process the last one.
        for idx in range(group_lines[0] + 1, group_lines[-1] + 1):
            for grp in sorted_group_indices[group_idx + 1 :]:
                # found an "outer" group line, reset tracker.
                if idx in grouped[grp]:
                    last_group_line = None
                    net_balance = 0
                    temp_balance_trough = None  # Unset the buffer
                    break

            # Is it in this group?
            if idx in group_lines:
                # Stash the line indices of the inner lines.
                if last_group_line:
                    _inner_lines = list(range(last_group_line + 1, idx))
                    reflow_logger.debug(
                        "      Extending Intermediates with %s", _inner_lines
                    )
                    inner_lines.extend(_inner_lines)
                # if we have a temp balance - crystallise it
                if temp_balance_trough is not None:
                    balance_trough = (
                        temp_balance_trough
                        if balance_trough is None
                        else min(balance_trough, temp_balance_trough)
                    )
                    reflow_logger.debug(
                        "      + Save Trough: %s (min = %s)",
                        temp_balance_trough,
                        balance_trough,
                    )
                    temp_balance_trough = None
                last_group_line = idx
                net_balance = 0
            elif last_group_line:
                # It's not a group line, but we're still tracking. Update with impulses.
                is_subgroup_line = any(
                    idx in grouped[grp] for grp in sorted_group_indices[:group_idx]
                )
                for ip in lines[idx].indent_points[:-1]:
                    # Don't count the trough on group lines we've already covered.
                    if "placeholder" in elements[ip.idx + 1].class_types:
                        _block_type = cast(
                            TemplateSegment, elements[ip.idx + 1].segments[0]
                        ).block_type
                        if _block_type in ("block_end", "block_mid"):
                            reflow_logger.debug(
                                "      Skipping trough before %r", _block_type
                            )
                            continue
                    if ip.indent_trough < 0 and not is_subgroup_line:
                        # NOTE: We set it temporarily here, because if we're going
                        # to pass an outer template loop then we should discard it.
                        # i.e. only count intervals within inner loops.
                        _this_through = net_balance + ip.indent_trough
                        temp_balance_trough = (
                            _this_through
                            if temp_balance_trough is None
                            else min(temp_balance_trough, _this_through)
                        )
                        reflow_logger.debug(
                            "      Stash Trough: %s (min = %s) @ %s",
                            _this_through,
                            temp_balance_trough,
                            idx,
                        )
                    # NOTE: We update net_balance _after_ the clause above.
                    net_balance += ip.indent_impulse

        # Evaluate options.
        reflow_logger.debug("    Options: %s", options)
        overlap = set.intersection(*options)
        reflow_logger.debug("    Simple Overlap: %s", overlap)
        # Remove any options above the limit option.
        # We minus one from the limit, because if it comes into effect
        # we'll effectively remove the effects of the indents between the elements.

        # Is there a mutually agreeable option?
        reflow_logger.debug("    Balance Trough: %s", balance_trough)
        if not overlap or (balance_trough is not None and balance_trough <= 0):
            # Set the indent to the minimum of the existing ones.
            best_indent = min(lines[idx].initial_indent_balance for idx in group_lines)
            reflow_logger.debug(
                "    Case 3: Best: %s. Inner Lines: %s", best_indent, inner_lines
            )
            # Remove one indent from all intermediate lines.
            # This is because we're effectively saying that these
            # placeholders shouldn't impact the indentation within them.
            for idx in inner_lines:
                # MUTATION
                lines[idx].initial_indent_balance -= 1
        else:
            best_indent = max(overlap)
            reflow_logger.debug(
                "    Case 2: Best: %s, Overlap: %s", best_indent, overlap
            )

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


def _revise_comment_lines(
    lines: List[_IndentLine], elements: ReflowSequenceType, ignore_comment_lines: bool
):
    """Given an initial set of individual lines. Revise comment ones.

    NOTE: This mutates the `lines` argument.

    We do this to ensure that lines with comments are aligned to
    the following non-comment element.
    """
    reflow_logger.debug("# Revise comment lines.")
    comment_line_buffer: List[int] = []

    # Slice to avoid copying
    for idx, line in enumerate(lines[:]):
        if line.is_all_comments(elements):
            if ignore_comment_lines:
                # If we're removing comment lines, purge this line from the buffer.
                reflow_logger.debug("Ignoring comment line idx: %s", idx)
                lines.remove(line)
            else:
                comment_line_buffer.append(idx)
        else:
            # Not a comment only line, if there's a buffer anchor
            # to this one.
            for comment_line_idx in comment_line_buffer:
                reflow_logger.debug(
                    "  Comment Only Line: %s. Anchoring to %s", comment_line_idx, idx
                )
                # Mutate reference lines to match this one.
                lines[comment_line_idx].initial_indent_balance = (
                    line.initial_indent_balance
                )
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


def _prune_untaken_indents(
    untaken_indents: Tuple[int, ...],
    incoming_balance: int,
    indent_stats: IndentStats,
    has_newline: bool,
) -> Tuple[int, ...]:
    """Update the tracking of untaken indents.

    This is an internal helper function for `_crawl_indent_points`.

    We use the `trough` of the given indent stats to remove any untaken
    indents which are now no longer relevant after balances are taken
    into account.
    """
    # Strip any untaken indents above the new balance.
    # NOTE: We strip back to the trough, not just the end point
    # if the trough was lower than the impulse.
    ui = tuple(
        x
        for x in untaken_indents
        if x
        <= (
            incoming_balance + indent_stats.impulse + indent_stats.trough
            if indent_stats.trough < indent_stats.impulse
            else incoming_balance + indent_stats.impulse
        )
    )

    # After stripping, we may have to add them back in.
    # NOTE: all the values in the indent_stats are relative to the incoming
    # indent, so we correct both of them here by using the incoming_balance.
    if indent_stats.impulse > indent_stats.trough and not has_newline:
        for i in range(indent_stats.trough, indent_stats.impulse):
            indent_val = incoming_balance + i + 1
            if indent_val - incoming_balance not in indent_stats.implicit_indents:
                ui += (indent_val,)

    return ui


def _update_crawl_balances(
    untaken_indents: Tuple[int, ...],
    incoming_balance: int,
    indent_stats: IndentStats,
    has_newline: bool,
) -> Tuple[int, Tuple[int, ...]]:
    """Update the tracking of untaken indents and balances.

    This is an internal helper function for `_crawl_indent_points`.
    """
    new_untaken_indents = _prune_untaken_indents(
        untaken_indents, incoming_balance, indent_stats, has_newline
    )
    new_balance = incoming_balance + indent_stats.impulse

    return new_balance, new_untaken_indents


def _crawl_indent_points(
    elements: ReflowSequenceType, allow_implicit_indents: bool = False
) -> Iterator[_IndentPoint]:
    """Crawl through a reflow sequence, mapping existing indents.

    This is where *most* of the logic for smart indentation
    happens. The values returned here have a large impact on
    exactly how indentation is treated.

    NOTE: If a line ends with a comment, indent impulses are pushed
    to the point _after_ the comment rather than before to aid with
    indentation. This saves searching for them later.

    TODO: Once this function *works*, there's definitely headroom
    for simplification and optimisation. We should do that.
    """
    last_line_break_idx = None
    indent_balance = 0
    untaken_indents: Tuple[int, ...] = ()
    cached_indent_stats: Optional[IndentStats] = None
    cached_point: Optional[_IndentPoint] = None
    for idx, elem in enumerate(elements):
        if isinstance(elem, ReflowPoint):
            # NOTE: The following line should never lead to an index error
            # because files should always have a trailing IndentBlock containing
            # an "end_of_file" marker, and so the final IndentPoint should always
            # have _something_ after it.
            indent_stats = IndentStats.from_combination(
                cached_indent_stats,
                elem.get_indent_impulse(),
            )
            # If don't allow implicit indents we should remove them here.
            # Also, if we do - we should check for brackets.
            # NOTE: The reason we check following class_types is because
            # bracketed expressions behave a little differently and are an
            # exception to the normal implicit indent rules. For implicit
            # indents which precede bracketed expressions, the implicit indent
            # is treated as a normal indent. In this case the start_bracket
            # must be the start of the bracketed section which isn't closed
            # on the same line - if it _is_ closed then we keep the implicit
            # indents.
            if indent_stats.implicit_indents:
                unclosed_bracket = False
                if (
                    allow_implicit_indents
                    and "start_bracket" in elements[idx + 1].class_types
                ):
                    # Is it closed in the line? Iterate forward to find out.
                    # get the stack depth
                    next_elem = cast(ReflowBlock, elements[idx + 1])
                    depth = next_elem.depth_info.stack_depth
                    for elem_j in elements[idx + 1 :]:
                        if isinstance(elem_j, ReflowPoint):
                            if elem_j.num_newlines() > 0:
                                unclosed_bracket = True
                                break
                        elif (
                            "end_bracket" in elem_j.class_types
                            and elem_j.depth_info.stack_depth == depth
                        ):
                            break
                    else:  # pragma: no cover
                        unclosed_bracket = True

                if unclosed_bracket or not allow_implicit_indents:
                    # Blank indent stats if not using them
                    indent_stats = IndentStats(
                        indent_stats.impulse, indent_stats.trough, ()
                    )

            # Was there a cache?
            if cached_indent_stats:
                # If there was we can safely assume there is a cached point.
                assert cached_point
                # If there was, this is a signal that we need to yield two points.
                # The content of those points depends on the newlines that surround the
                # last segments (which will be comment block).
                # _leading_ comments (i.e. those preceded by a newline): Yield _before_
                # _trailing_ comments (or rare "mid" comments): Yield _after_
                # TODO: We might want to reconsider the treatment of comments in the
                # middle of lines eventually, but they're fairly unusual so not well
                # covered in tests as of writing.

                # We yield the first of those points here, and then manipulate the
                # indent_stats object to allow the following code to yield the other.

                # We can refer back to the cached point as a framework. In both
                # cases we use the combined impulse and trough, but we use the
                # current indent balance and untaken indents.
                if cached_point.is_line_break:
                    # It's a leading comment. Yield all the info in that point.
                    yield _IndentPoint(
                        cached_point.idx,
                        indent_stats.impulse,
                        indent_stats.trough,
                        indent_balance,
                        cached_point.last_line_break_idx,
                        True,
                        untaken_indents,
                    )
                    # Before zeroing, crystallise any effect on overall balances.
                    indent_balance, untaken_indents = _update_crawl_balances(
                        untaken_indents, indent_balance, indent_stats, True
                    )
                    # Set indent stats to zero because we've already yielded.
                    indent_stats = IndentStats(0, 0, indent_stats.implicit_indents)
                else:
                    # It's a trailing (or mid) comment. Yield it in the next.
                    yield _IndentPoint(
                        cached_point.idx,
                        0,
                        0,
                        indent_balance,
                        cached_point.last_line_break_idx,
                        False,
                        untaken_indents,
                    )
                    # No need to reset indent stats. It's already good.

            # Reset caches.
            cached_indent_stats = None
            has_newline = False
            cached_point = None

            # Do we have a newline?
            has_newline = has_untemplated_newline(elem) and idx != last_line_break_idx

            # Construct the point we may yield
            indent_point = _IndentPoint(
                idx,
                indent_stats.impulse,
                indent_stats.trough,
                indent_balance,
                last_line_break_idx,
                has_newline,
                untaken_indents,
            )

            # Update the last newline index if this is a newline.
            # NOTE: We used the previous value in the construction of the
            # _IndentPoint above and we only reset after that construction.
            if has_newline:
                last_line_break_idx = idx

            # Is the next element a comment? If so - delay the decision until we've
            # got any indents from after the comment too.
            if "comment" in elements[idx + 1].class_types:
                cached_indent_stats = indent_stats
                # Create parts of a point to use later.
                cached_point = indent_point
                # We loop around so that we don't do the untaken indent calcs yet.
                continue
            # Is it meaningful as an indent point?
            # i.e. Is it a line break? AND not a templated one.
            # NOTE: a point at idx zero is meaningful because it's like an indent.
            # NOTE: Last edge case. If we haven't yielded yet, but the
            # next element is the end of the file. Yield.
            elif (
                has_newline
                or indent_stats.impulse
                or indent_stats.trough
                or idx == 0
                or elements[idx + 1].segments[0].is_type("end_of_file")
            ):
                yield indent_point

            # Update balances
            indent_balance, untaken_indents = _update_crawl_balances(
                untaken_indents, indent_balance, indent_stats, has_newline
            )


def _map_line_buffers(
    elements: ReflowSequenceType, allow_implicit_indents: bool = False
) -> Tuple[List[_IndentLine], List[int]]:
    """Map the existing elements, building up a list of _IndentLine.

    Returns:
        :obj:`tuple` of a :obj:`list` of :obj:`_IndentLine` and a
            :obj:`list` of :obj:`int`. The first is the main output
            and is designed to be used in assessing indents and
            their effect through a SQL file. The latter is a list of
            "imbalanced" indent locations, where the positive indent
            is untaken, but its corresponding negative indent *is*
            taken.

    """
    # First build up the buffer of lines.
    lines = []
    point_buffer = []
    _previous_points = {}
    # Buffers to keep track of indents which are untaken on the way
    # up but taken on the way down. We track them explicitly so we
    # can force them later.

    #: dict of ints: maps indentation balance values to the last
    #: index location where they were seen. This is a working buffer
    #: and not directly returned by the function.
    untaken_indent_locs = {}
    #: list of ints: a list of element indices which contain untaken
    #: positive indents, that should be forced later because their
    #: corresponding negative indent _was_ taken. Several edge cases
    #: are excluded from this list and so not included. See code below.
    imbalanced_locs = []

    for indent_point in _crawl_indent_points(
        elements, allow_implicit_indents=allow_implicit_indents
    ):
        # We evaluate all the points in a line at the same time, so
        # we first build up a buffer.
        point_buffer.append(indent_point)
        _previous_points[indent_point.idx] = indent_point

        if not indent_point.is_line_break:
            # If it's not a line break, we should still check whether it's
            # a positive untaken to keep track of them.
            # ...unless it's implicit.
            indent_stats = cast(
                ReflowPoint, elements[indent_point.idx]
            ).get_indent_impulse()
            if indent_point.indent_impulse > indent_point.indent_trough and not (
                allow_implicit_indents and indent_stats.implicit_indents
            ):
                untaken_indent_locs[
                    indent_point.initial_indent_balance + indent_point.indent_impulse
                ] = indent_point.idx
            continue

        # If it *is* a line break, then store it.
        lines.append(_IndentLine.from_points(point_buffer))

        # We should also evaluate whether this point inserts a newline at the close
        # of an indent which was untaken on the way up.
        # https://github.com/sqlfluff/sqlfluff/issues/4234
        # Special case 1:
        # If we're at the end of the file we shouldn't interpret it as a line break
        # for problem indents, they're a bit of a special case.
        # Special case 2:
        # Bracketed expressions are a bit odd here.
        # e.g.
        #   WHERE (
        #       foo = bar
        #   )
        #   LIMIT 1
        #
        # Technically there's an untaken indent before the opening bracket
        # but this layout is common practice so we're not going to force
        # one there even though there _is_ a line break after the closing
        # bracket.
        following_class_types = elements[indent_point.idx + 1].class_types
        if (
            indent_point.indent_trough
            # End of file ends case. (Special case 1)
            and "end_of_file" not in following_class_types
        ):
            passing_indents = list(
                range(
                    indent_point.initial_indent_balance,
                    indent_point.initial_indent_balance + indent_point.indent_trough,
                    -1,
                )
            )
            # There might be many indents at this point, but if any match, then
            # we should still force an indent

            # NOTE: We work _inward_ to check which have been taken.
            for i in reversed(passing_indents):
                # Was this outer one untaken?
                if i not in untaken_indent_locs:
                    # No? Stop the loop. If we've a corresponding indent for
                    # this dedent, we shouldn't use the same location to force
                    # untaken indents at inner levels.
                    break

                loc = untaken_indent_locs[i]

                # First check for bracket special case. It's less about whether
                # the section _ends_ with a lone bracket, and more about whether
                # the _starting point_ is a bracket which closes a line. If it
                # is, then skip this location. (Special case 2).
                # NOTE: We can safely "look ahead" here because we know all files
                # end with an IndentBlock, and we know here that `loc` refers to
                # an IndentPoint.
                if "start_bracket" in elements[loc + 1].class_types:
                    continue

                # If the location was in the line we're just closing. That's
                # not a problem because it's an untaken indent which is closed
                # on the same line.
                if any(ip.idx == loc for ip in point_buffer):
                    continue

                # If the only elements between current point and the end of the
                # reference line are comments, then don't trigger, it's a misplaced
                # indent.
                # First find the end of the reference line.
                for j in range(loc, indent_point.idx):
                    _pt = _previous_points.get(j, None)
                    if not _pt:
                        continue
                    if _pt.is_line_break:
                        break
                assert _pt
                # Then check if all comments.
                if all(
                    "comment" in elements[k].class_types
                    for k in range(_pt.idx + 1, indent_point.idx, 2)
                ):
                    # It is all comments. Ignore it.
                    continue

                imbalanced_locs.append(loc)

        # Remove any which are now no longer relevant from the working buffer.
        for k in list(untaken_indent_locs.keys()):
            if k > indent_point.initial_indent_balance + indent_point.indent_trough:
                del untaken_indent_locs[k]

        # Reset the buffer
        point_buffer = [indent_point]

    # Handle potential final line
    if len(point_buffer) > 1:
        lines.append(_IndentLine.from_points(point_buffer))

    return lines, imbalanced_locs


def _deduce_line_current_indent(
    elements: ReflowSequenceType, last_line_break_idx: Optional[int] = None
) -> str:
    """Deduce the current indent string.

    This method accounts for both literal indents and indents
    consumed from the source as by potential templating tags.
    """
    indent_seg = None
    if not elements[0].segments:
        return ""
    elif last_line_break_idx:
        indent_seg = cast(
            ReflowPoint, elements[last_line_break_idx]
        )._get_indent_segment()
    elif isinstance(elements[0], ReflowPoint) and elements[0].segments[
        0
    ].pos_marker.working_loc == (1, 1):
        # No last_line_break_idx, but this is a point. It's the first line.

        # First check whether this is a first line with a leading
        # placeholder.
        if elements[0].segments[0].is_type("placeholder"):
            reflow_logger.debug("    Handling as initial leading placeholder")
            seg = cast(TemplateSegment, elements[0].segments[0])
            # Is the placeholder a consumed whitespace?
            if seg.source_str.startswith((" ", "\t")):
                indent_seg = seg
        # Otherwise it's an initial leading literal whitespace.
        else:
            reflow_logger.debug("    Handling as initial leading whitespace")
            for indent_seg in elements[0].segments[::-1]:
                if indent_seg.is_type("whitespace") and not indent_seg.is_templated:
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
        # It's a literal
        assert "\n" not in indent_seg.raw, f"Found newline in indent: {indent_seg}"
        return indent_seg.raw
    else:  # pragma: no cover
        # It's templated. This shouldn't happen. Segments returned by
        # _get_indent_segment, should be valid indents (i.e. whitespace
        # or placeholders for consumed whitespace). This is a bug.
        if indent_seg.pos_marker:
            reflow_logger.warning(
                "Segment position marker: %s: [SRC: %s, TMP:%s]",
                indent_seg.pos_marker,
                indent_seg.pos_marker.source_slice,
                indent_seg.pos_marker.templated_slice,
            )
        raise NotImplementedError(
            "Unexpected templated indent. Report this as a bug on "
            f"GitHub. Segment: {indent_seg}\n"
            "https://github.com/sqlfluff/sqlfluff/issues/new/choose"
        )


def _lint_line_starting_indent(
    elements: ReflowSequenceType,
    indent_line: _IndentLine,
    single_indent: str,
    forced_indents: List[int],
) -> List[LintResult]:
    """Lint the indent at the start of a line.

    NOTE: This mutates `elements` to avoid lots of copying.
    """
    indent_points = indent_line.indent_points
    # Set up the default anchor
    initial_point_idx = indent_points[0].idx
    anchor = {"before": elements[initial_point_idx + 1].segments[0]}
    # Find initial indent, and deduce appropriate string indent.
    current_indent = _deduce_line_current_indent(
        elements, indent_points[-1].last_line_break_idx
    )
    desired_indent_units = indent_line.desired_indent_units(forced_indents)
    desired_starting_indent = desired_indent_units * single_indent
    initial_point = cast(ReflowPoint, elements[initial_point_idx])

    if current_indent == desired_starting_indent:
        return []

    if initial_point_idx > 0 and initial_point_idx < len(elements) - 1:
        # Edge case: Lone comments. Normally comments are anchored to the line
        # _after_ where they come. However, if the existing location _matches_
        # the _preceding line_, then we will allow it. It's not the "expected"
        # location but it is allowable.
        if "comment" in elements[initial_point_idx + 1].class_types:
            last_indent = _deduce_line_current_indent(
                elements, indent_points[0].last_line_break_idx
            )
            if len(current_indent) == len(last_indent):
                reflow_logger.debug("    Indent matches previous line. OK.")
                return []

        # Edge case: Multiline comments. If the previous line was a multiline
        # comment and this line starts with a multiline comment, then we should
        # only lint the indent if it's _too small_. Otherwise we risk destroying
        # indentation which the logic here is not smart enough to handle.
        if (
            "block_comment" in elements[initial_point_idx - 1].class_types
            and "block_comment" in elements[initial_point_idx + 1].class_types
        ):
            if len(current_indent) > len(desired_starting_indent):
                reflow_logger.debug("    Indent is bigger than required. OK.")
                return []

    reflow_logger.debug(
        "    Correcting indent @ line %s. Existing indent: %r -> %r",
        elements[initial_point_idx + 1].segments[0].pos_marker.working_line_no,
        current_indent,
        desired_starting_indent,
    )

    # Initial point gets special handling if it has no newlines.
    if indent_points[0].idx == 0 and not indent_points[0].is_line_break:
        init_seg = elements[indent_points[0].idx].segments[0]
        if init_seg.is_type("placeholder"):
            init_seg = cast(TemplateSegment, init_seg)
            # If it's a placeholder initial indent, then modify the placeholder
            # to remove the indent from it.
            src_fix = SourceFix(
                "",
                source_slice=slice(0, len(current_indent) + 1),
                templated_slice=slice(0, 0),
            )
            fixes = [
                LintFix.replace(
                    init_seg,
                    [init_seg.edit(source_fixes=[src_fix], source_str="")],
                )
            ]
        else:
            # Otherwise it's just initial whitespace. Remove it.
            fixes = [LintFix.delete(seg) for seg in initial_point.segments]

        new_results = [
            LintResult(
                initial_point.segments[0],
                fixes,
                description="First line should not be indented.",
                source="reflow.indent.existing",
            )
        ]
        new_point = ReflowPoint(())
    # Placeholder indents also get special treatment
    else:
        new_results, new_point = initial_point.indent_to(
            desired_starting_indent,
            source="reflow.indent.existing",
            **anchor,  # type: ignore
        )

    elements[initial_point_idx] = new_point
    return new_results


def _lint_line_untaken_positive_indents(
    elements: ReflowSequenceType,
    indent_line: _IndentLine,
    single_indent: str,
    imbalanced_indent_locs: List[int],
) -> Tuple[List[LintResult], List[int]]:
    """Check for positive indents which should have been taken."""
    # First check whether this line contains any of the untaken problem points.
    for ip in indent_line.indent_points:
        if ip.idx in imbalanced_indent_locs:
            # Force it at the relevant position.
            desired_indent = single_indent * (
                ip.closing_indent_balance - len(ip.untaken_indents)
            )
            reflow_logger.debug(
                "    Detected imbalanced +ve break @ line %s. Indenting to %r",
                elements[ip.idx + 1].segments[0].pos_marker.working_line_no,
                desired_indent,
            )
            target_point = cast(ReflowPoint, elements[ip.idx])
            results, new_point = target_point.indent_to(
                desired_indent,
                before=elements[ip.idx + 1].segments[0],
                source="reflow.indent.imbalance",
            )
            elements[ip.idx] = new_point
            # Keep track of the indent we forced, by returning it.
            return results, [ip.closing_indent_balance]

    # If we don't close the line higher there won't be any.
    starting_balance = indent_line.opening_balance()
    last_ip = indent_line.indent_points[-1]
    # Check whether it closes the opening indent.
    if last_ip.initial_indent_balance + last_ip.indent_trough <= starting_balance:
        return [], []
    # It's not, we don't close out an opened indent.
    # NOTE: Because trailing comments should always shift their any
    # surrounding indentation effects to _after_ their position, we
    # should just be able to evaluate them safely from the end of the line.

    indent_points = indent_line.indent_points

    # Account for the closing trough.
    closing_trough = last_ip.initial_indent_balance + (
        last_ip.indent_trough or last_ip.indent_impulse
    )

    # Edge case: Adjust closing trough for trailing indents
    # after comments disrupting closing trough.
    _bal = 0
    for elem in elements[last_ip.idx + 1 :]:
        if not isinstance(elem, ReflowPoint):
            if "comment" not in elem.class_types:
                break
            continue
        # Otherwise it's a point
        stats = elem.get_indent_impulse()
        # If it's positive, stop. We likely won't find enough negative to come.
        if stats.impulse > 0:  # pragma: no cover
            break
        closing_trough = _bal + stats.trough
        _bal += stats.impulse

    # On the way up we're looking for whether the ending balance
    # was an untaken indent or not. If it *was* untaken, there's
    # a good chance that we *should* take it.
    # NOTE: an implicit indent would not force a newline
    # because it wouldn't be in the untaken_indents. It's
    # considered _taken_ even if not.
    if closing_trough not in indent_points[-1].untaken_indents:
        # If the closing point doesn't correspond to an untaken
        # indent within the line (i.e. it _was_ taken), then
        # there won't be an appropriate place to force an indent.
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
    results, new_point = target_point.indent_to(
        desired_indent,
        before=elements[target_point_idx + 1].segments[0],
        source="reflow.indent.positive",
    )
    elements[target_point_idx] = new_point
    # Keep track of the indent we forced, by returning it.
    return results, [closing_trough]


def _lint_line_untaken_negative_indents(
    elements: ReflowSequenceType,
    indent_line: _IndentLine,
    single_indent: str,
    forced_indents: List[int],
) -> List[LintResult]:
    """Check for negative indents which should have been taken."""
    # If we don't close lower than we start, there won't be any.
    if indent_line.closing_balance() >= indent_line.opening_balance():
        return []

    results: List[LintResult] = []
    # On the way down we're looking for indents which *were* taken on
    # the way up, but currently aren't on the way down. We slice so
    # that the _last_ point isn't evaluated, because that's fine.
    for ip in indent_line.indent_points[:-1]:
        # Is line break, or positive indent?
        if ip.is_line_break or ip.indent_impulse >= 0:
            continue

        # When using implicit indents, we may find untaken negatives which
        # aren't shallower than the line they're on. This is because they
        # were implicit on the way up and so not included in `untaken_indents`.
        # To catch them we also check that we're shallower than the start of
        # of the line.
        if (
            ip.initial_indent_balance + ip.indent_trough
            >= indent_line.opening_balance()
        ):
            continue

        # It's negative, is it untaken? In the case of a multi-dedent
        # they must _all_ be untaken to take this route.
        covered_indents = set(
            range(
                ip.initial_indent_balance,
                ip.initial_indent_balance + ip.indent_trough,
                -1,
            )
        )
        untaken_indents = set(ip.untaken_indents).difference(forced_indents)
        if covered_indents.issubset(untaken_indents):
            # Yep, untaken.
            continue

        # Edge Case: Comments. Since introducing the code to push indent effects
        # to the point _after_ comments, we no longer need to detect an edge case
        # for them here. If we change that logic again in the future, so that
        # indent values are allowed before comments - that code should be
        # reintroduced here.

        # Edge Case: Semicolons. For now, semicolon placement is a little
        # more complicated than what we do here. For now we don't (by
        # default) introduce missing -ve indents before semicolons.
        # TODO: Review whether this is a good idea, or whether this should be
        # more configurable.
        # NOTE: This could potentially lead to a weird situation if two
        # statements are already on the same line. That's a bug to solve later.
        if elements[ip.idx + 1 :] and elements[ip.idx + 1].class_types.intersection(
            ("statement_terminator", "comma")
        ):
            reflow_logger.debug(
                "    Detected missing -ve line break @ line %s, before "
                "semicolon or comma. Ignoring...",
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
        new_results, new_point = target_point.indent_to(
            desired_indent,
            before=elements[ip.idx + 1].segments[0],
            source="reflow.indent.negative",
        )
        elements[ip.idx] = new_point
        results += new_results

    return results


def _lint_line_buffer_indents(
    elements: ReflowSequenceType,
    indent_line: _IndentLine,
    single_indent: str,
    forced_indents: List[int],
    imbalanced_indent_locs: List[int],
) -> List[LintResult]:
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
    reflow_logger.info(
        "    Line #%s [source line #%s]. idx=%s:%s. FI %s. UPI: %s.",
        elements[indent_line.indent_points[0].idx + 1]
        .segments[0]
        .pos_marker.working_line_no,
        elements[indent_line.indent_points[0].idx + 1]
        .segments[0]
        .pos_marker.source_position()[0],
        indent_line.indent_points[0].idx,
        indent_line.indent_points[-1].idx,
        forced_indents,
        imbalanced_indent_locs,
    )
    reflow_logger.debug(
        "   Line Content: %s",
        [
            repr(elem.raw)
            for elem in elements[
                indent_line.indent_points[0].idx : indent_line.indent_points[-1].idx
            ]
        ],
    )
    reflow_logger.debug("  Evaluate Line: %s. FI %s", indent_line, forced_indents)
    results = []

    # First, handle starting indent.
    results += _lint_line_starting_indent(
        elements, indent_line, single_indent, forced_indents
    )

    # Second, handle potential missing positive indents.
    new_results, new_indents = _lint_line_untaken_positive_indents(
        elements, indent_line, single_indent, imbalanced_indent_locs
    )
    # If we have any, bank them and return. We don't need to check for
    # negatives because we know we're on the way up.
    if new_results:
        results += new_results
        # Keep track of any indents we forced
        forced_indents.extend(new_indents)
        return results

    # Third, handle potential missing negative indents.
    results += _lint_line_untaken_negative_indents(
        elements, indent_line, single_indent, forced_indents
    )

    # Lastly remove any forced indents above the closing balance.
    # Iterate through a slice so we're not editing the thing
    # that we're iterating through.
    for i in forced_indents[:]:
        if i > indent_line.closing_balance():
            forced_indents.remove(i)

    return results


def lint_indent_points(
    elements: ReflowSequenceType,
    single_indent: str,
    skip_indentation_in: FrozenSet[str] = frozenset(),
    allow_implicit_indents: bool = False,
    ignore_comment_lines: bool = False,
) -> Tuple[ReflowSequenceType, List[LintResult]]:
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
    lines: List[_IndentLine]
    imbalanced_indent_locs: List[int]
    lines, imbalanced_indent_locs = _map_line_buffers(
        elements, allow_implicit_indents=allow_implicit_indents
    )

    # Revise templated indents
    _revise_templated_lines(lines, elements)
    # Revise comment indents
    _revise_comment_lines(lines, elements, ignore_comment_lines=ignore_comment_lines)

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
    results: List[LintResult] = []
    # NOTE: forced_indents is mutated by _lint_line_buffer_indents
    # It's used to pass from one call to the next.
    forced_indents: List[int] = []
    elem_buffer = elements.copy()  # Make a working copy to mutate.
    for line in lines:
        line_results = _lint_line_buffer_indents(
            elem_buffer, line, single_indent, forced_indents, imbalanced_indent_locs
        )
        if line_results:
            reflow_logger.info("      PROBLEMS:")
            for res in line_results:
                reflow_logger.info("        %s @ %s", res.source, res.anchor)
                reflow_logger.info("          %s", res.description)
        results += line_results

    return elem_buffer, results


def _source_char_len(elements: ReflowSequenceType):
    """Calculate length in the source file.

    NOTE: This relies heavily on the sequence already being
    split appropriately. It will raise errors if not.

    TODO: There's a good chance that this might not play well
    with other fixes. If we find segments without positions
    then it will probably error. Those will need ironing
    out.

    TODO: This probably needs more tests. It's already
    the source of quite a few fiddly sections.
    """
    char_len = 0
    last_source_slice: Optional[slice] = None
    for seg in chain.from_iterable(elem.segments for elem in elements):
        # Indent tokens occasionally have strange position markers.
        # They also don't have length so skip them.
        # TODO: This is actually caused by bugs and inconsistencies
        # in how the source_slice is generated for the position markers
        # of indent and dedent tokens. That's a job for another day
        # however.
        if seg.is_type("indent"):
            continue
        # Get the source position. If there is no source position then it's
        # a recent edit or modification. We shouldn't evaluate it until it's
        # been positioned. Without a source marker we don't know how to treat
        # it.
        if not seg.pos_marker:  # pragma: no cover
            break
        source_slice = seg.pos_marker.source_slice
        # Is there a newline in the source string?
        source_str = seg.pos_marker.source_str()
        if "\n" in source_str:
            # There is. Stop here. It's probably a complicated
            # jinja tag, so it's safer to stop here.
            # TODO: In future, we should probably be a little
            # smarter about this, but for now this is ok. Without
            # an algorithm for layout out code _within_ jinja tags
            # we won't be able to suggest appropriate fixes.
            char_len += source_str.index("\n")
            break
        slice_len = slice_length(source_slice)
        # Only update the length if it's a new slice.
        if source_slice != last_source_slice:
            # If it's got size in the template but not in the source, it's
            # probably an insertion.
            if seg.raw and not slice_len:
                char_len += len(seg.raw)
                # NOTE: Don't update the last_source_slice.
            elif not slice_len:
                # If it's not got a raw and no length, it's
                # irrelevant. Ignore it. It's probably a meta.
                continue
            # Otherwise if we're literal, use the raw length
            # because it might be an edit.
            elif seg.pos_marker.is_literal():
                char_len += len(seg.raw)
                last_source_slice = source_slice
            # Otherwise assume it's templated code.
            else:
                char_len += slice_length(source_slice)
                last_source_slice = source_slice

    return char_len


def _rebreak_priorities(spans: List[_RebreakSpan]) -> Dict[int, int]:
    """Process rebreak spans into opportunities to split lines.

    The index to insert a potential indent at depends on the
    line_position of the span. Infer that here and store the indices
    in the elements.
    """
    rebreak_priority = {}
    for span in spans:
        if span.line_position == "leading":
            rebreak_indices = [span.start_idx - 1]
        elif span.line_position == "trailing":
            rebreak_indices = [span.end_idx + 1]
        elif span.line_position == "alone":
            rebreak_indices = [span.start_idx - 1, span.end_idx + 1]
        else:  # pragma: no cover
            raise NotImplementedError(
                "Unexpected line position: %s", span.line_position
            )
        # NOTE: Operator precedence here is hard coded. It could be
        # moved to configuration in the layout section in the future.
        # Operator precedence is fairly consistent between dialects
        # so for now it feels ok that it's coded here - it also wouldn't
        # be a breaking change at that point so no pressure to release
        # it early.
        span_raw = span.target.raw_upper
        priority = 6  # Default to 6 for now i.e. the same as '+'
        # Override priority for specific precedence.
        if span_raw == ",":
            priority = 1
        elif span.target.is_type("assignment_operator"):
            # This one is a little rarer so not covered in tests yet.
            # Logic is the same as others though.
            priority = 2  # pragma: no cover
        elif span_raw == "OR":
            priority = 3
        elif span_raw == "AND":
            priority = 4
        elif span.target.is_type("comparison_operator"):
            priority = 5
        elif span_raw in ("*", "/", "%"):
            priority = 7

        for rebreak_idx in rebreak_indices:
            rebreak_priority[rebreak_idx] = priority

    return rebreak_priority


MatchedIndentsType = DefaultDict[float, List[int]]


def _increment_balance(
    input_balance: int,
    indent_stats: IndentStats,
    elem_idx: int,
) -> Tuple[int, MatchedIndentsType]:
    """Logic for stepping through _match_indents.

    This is the part of that logic which is potentially fragile
    so is separated here into a more isolated function for
    better testing. It's very easy to get wrong and necessary
    so we don't mistake empty elements, but potentially
    fragile nonetheless.

    Returns:
        A tuple where the first element is the resulting balance
            and the second is a :obj:`defaultdict` of the new
            elements to add to `matched_indents`.

    Positive indent example:
    >>> _increment_balance(0, IndentStats(1, 0), 7)
    (1, defaultdict(<class 'list'>, {1.0: [7]}))

    Negative indent example:
    >>> _increment_balance(3, IndentStats(-1, -1), 11)
    (2, defaultdict(<class 'list'>, {3.0: [11]}))

    Double negative indent example:
    >>> _increment_balance(3, IndentStats(-2, -2), 16)
    (1, defaultdict(<class 'list'>, {3.0: [16], 2.0: [16]}))

    Dip indent example:
    >>> _increment_balance(3, IndentStats(0, -1), 21)
    (3, defaultdict(<class 'list'>, {3.0: [21]}))
    """
    balance = input_balance
    matched_indents: MatchedIndentsType = defaultdict(list)
    if indent_stats.trough < 0:  # NOTE: for negative, *trough* counts.
        # in case of more than one indent we loop and apply to all.
        for b in range(0, indent_stats.trough, -1):
            matched_indents[(balance + b) * 1.0].append(elem_idx)
        # NOTE: We carry forward the impulse, not the trough.
        # This is important for dedent+indent pairs.
        balance += indent_stats.impulse
    elif indent_stats.impulse > 0:  # NOTE: for positive, *impulse* counts.
        # in case of more than one indent we loop and apply to all.
        for b in range(0, indent_stats.impulse):
            matched_indents[(balance + b + 1) * 1.0].append(elem_idx)
        balance += indent_stats.impulse
    return balance, matched_indents


def _match_indents(
    line_elements: ReflowSequenceType,
    rebreak_priorities: Dict[int, int],
    newline_idx: int,
    allow_implicit_indents: bool = False,
) -> MatchedIndentsType:
    """Identify indent points, taking into account rebreak_priorities.

    Expect fractional keys, because of the half values for
    rebreak points.
    """
    balance = 0
    matched_indents: MatchedIndentsType = defaultdict(list)
    implicit_indents: Dict[int, Tuple[int, ...]] = {}
    for idx, e in enumerate(line_elements):
        # We only care about points, because only they contain indents.
        if not isinstance(e, ReflowPoint):
            continue

        # As usual, indents are referred to by their "uphill" side
        # so what number we store the point against depends on whether
        # it's positive or negative.
        # NOTE: Here we don't actually pass in the forward types because
        # we don't need them for the output. It doesn't make a difference.
        indent_stats = e.get_indent_impulse()
        e_idx = newline_idx - len(line_elements) + idx + 1
        # Save any implicit indents.
        if indent_stats.implicit_indents:
            implicit_indents[e_idx] = indent_stats.implicit_indents
        balance, nmi = _increment_balance(balance, indent_stats, e_idx)
        # Incorporate nmi into matched_indents
        for b, indices in nmi.items():
            matched_indents[b].extend(indices)

        # Something can be both an indent point AND a rebreak point.
        if idx in rebreak_priorities:
            # For potential rebreak options (i.e. ones without an indent)
            # we add 0.5 so that they sit *between* the varying indent
            # options. that means we split them before any of their
            # content, but don't necessarily split them when their
            # container is split.

            # Also to spread out the breaks within an indent, we further
            # add hints to distinguish between them. This is where operator
            # precedence (as defined above) actually comes into effect.
            priority = rebreak_priorities[idx]
            # Assume `priority` in range 0 - 50. So / 100 to add to 0.5.
            matched_indents[balance + 0.5 + (priority / 100)].append(e_idx)
        else:
            continue

    # Before working out the lowest option, we purge any which contain
    # ONLY the final point. That's because adding indents there won't
    # actually help the line length. There's *already* a newline there.
    for indent_level in list(matched_indents.keys()):
        if matched_indents[indent_level] == [newline_idx]:
            matched_indents.pop(indent_level)
            reflow_logger.debug(
                "    purging balance of %s, it references only the final element.",
                indent_level,
            )

    # ADDITIONALLY - if implicit indents are allowed we should
    # only use them if they match another untaken point (which isn't
    # implicit, or the end of the line).
    # NOTE: This logic might be best suited to be sited elsewhere
    # when (and if) we introduce smarter choices on where to add
    # indents.
    if allow_implicit_indents:
        for indent_level in list(matched_indents.keys()):
            major_points = set(matched_indents[indent_level]).difference(
                [newline_idx], implicit_indents.keys()
            )
            if not major_points:
                matched_indents.pop(indent_level)
                reflow_logger.debug(
                    "    purging balance of %s, it references implicit indents "
                    "or the final indent.",
                    indent_level,
                )

    return matched_indents


def _fix_long_line_with_comment(
    line_buffer: ReflowSequenceType,
    elements: ReflowSequenceType,
    current_indent: str,
    line_length_limit: int,
    last_indent_idx: Optional[int],
    trailing_comments: str = "before",
) -> Tuple[ReflowSequenceType, List[LintFix]]:
    """Fix long line by moving trailing comments if possible.

    This method (unlike the ones for normal lines), just returns
    a new `elements` argument rather than mutating it.
    """
    # If the comment contains a noqa, don't fix it. It's unsafe.
    if "noqa" in line_buffer[-1].segments[-1].raw:
        reflow_logger.debug("    Unfixable because noqa unsafe to move.")
        return elements, []

    # If the comment is longer than the limit _anyway_, don't move
    # it. It will still be too long.
    if len(line_buffer[-1].segments[-1].raw) + len(current_indent) > line_length_limit:
        reflow_logger.debug("    Unfixable because comment too long anyway.")
        return elements, []

    comment_seg = line_buffer[-1].segments[-1]
    first_seg = line_buffer[0].segments[0]
    last_elem_idx = elements.index(line_buffer[-1])

    assert trailing_comments in (
        "after",
        "before",
    ), f"Unexpected value for `trailing_comments`: {trailing_comments!r}"

    # The simpler case if if we're moving the comment to the line
    # _after_. In that case we just coerce the point before it to
    # be an indent.
    if trailing_comments == "after":
        anchor_point = cast(ReflowPoint, line_buffer[-2])
        results, new_point = anchor_point.indent_to(current_indent, before=comment_seg)
        elements = (
            elements[: last_elem_idx - 1] + [new_point] + elements[last_elem_idx:]
        )
        return elements, fixes_from_results(results)

    # Otherwise we're moving it up and _before_ the line, which is
    # a little more involved (but also the default).
    fixes = [
        # Remove the comment from it's current position, and any
        # whitespace in the previous point.
        LintFix.delete(comment_seg),
        *[
            LintFix.delete(ws)
            for ws in line_buffer[-2].segments
            if ws.is_type("whitespace")
        ],
    ]

    # Are we at the start of the file? If so, there's no
    # indent, and also no previous segments to deal with.
    if last_indent_idx is None:
        new_point = ReflowPoint((NewlineSegment(),))
        prev_elems = []
        anchor = first_seg
    else:
        new_segments: Tuple[RawSegment, ...] = (NewlineSegment(),)
        if current_indent:
            new_segments += (WhitespaceSegment(current_indent),)
        new_point = ReflowPoint(new_segments)
        prev_elems = elements[: last_indent_idx + 1]
        anchor = elements[last_indent_idx + 1].segments[0]

    fixes.append(
        # NOTE: This looks a little convoluted, but we create
        # *before* a block here rather than *after* a point,
        # because the point may have been modified already by
        # reflow code and may not be a reliable anchor.
        LintFix.create_before(
            anchor,
            [
                comment_seg,
                *new_point.segments,
            ],
        )
    )

    elements = (
        prev_elems
        + [
            line_buffer[-1],
            new_point,
        ]
        + line_buffer[:-2]
        + elements[last_elem_idx + 1 :]
    )

    return elements, fixes


def _fix_long_line_with_fractional_targets(
    elements: ReflowSequenceType, target_breaks: List[int], desired_indent: str
) -> List[LintResult]:
    """Work out fixes for splitting a long line at locations like operators.

    NOTE: This mutates `elements` to avoid copying.

    This is a helper function within .lint_line_length().
    """
    line_results = []
    for e_idx in target_breaks:
        e = cast(ReflowPoint, elements[e_idx])
        new_results, new_point = e.indent_to(
            desired_indent,
            after=elements[e_idx - 1].segments[-1],
            before=elements[e_idx + 1].segments[0],
        )
        # NOTE: Mutation of elements.
        elements[e_idx] = new_point
        line_results += new_results
    return line_results


def _fix_long_line_with_integer_targets(
    elements: ReflowSequenceType,
    target_breaks: List[int],
    line_length_limit: int,
    inner_indent: str,
    outer_indent: str,
) -> List[LintResult]:
    """Work out fixes for splitting a long line at locations like indents.

    NOTE: This mutates `elements` to avoid copying.

    This is a helper function within .lint_line_length().
    """
    line_results = []

    # If we can get to the uphill indent of later break, and still be within
    # the line limit, then we can skip everything before it.
    purge_before = 0
    for e_idx in target_breaks:
        # Is the following block already past the limit?
        # NOTE: We use the block because we know it will have segments.
        if not elements[e_idx + 1].segments[0].pos_marker:
            # If it doesn't have position - we should just bow out
            # now. It's too complicated.
            break  # pragma: no cover
        if (
            elements[e_idx + 1].segments[0].pos_marker.working_line_pos
            > line_length_limit
        ):
            # If we're past the line length limit, stop looking.
            break

        e = cast(ReflowPoint, elements[e_idx])
        if e.get_indent_impulse().trough < 0:
            # It's negative. Skip onward.
            continue

        # If we get this far, then it's positive, but still within
        # the line limit. We can purge any pairs before this.
        purge_before = e_idx
        reflow_logger.debug("    ...breaks before %s unnecessary.", purge_before)
    # Only keep indices which are after the critical point.
    target_breaks = [e_idx for e_idx in target_breaks if e_idx >= purge_before]
    reflow_logger.debug("    Remaining breaks: %s.", target_breaks)

    for e_idx in target_breaks:
        e = cast(ReflowPoint, elements[e_idx])
        indent_stats = e.get_indent_impulse()
        # NOTE: We check against the _impulse_ here rather than the
        # _trough_ because if we're about to step back up again then
        # it should still be indented.
        if indent_stats.impulse < 0:
            new_indent = outer_indent
            # NOTE: If we're about to insert a dedent before a
            # comma or semicolon ... don't. They are a bit special
            # in being allowed to trail.
            if elements[e_idx + 1].class_types.intersection(
                ("statement_terminator", "comma")
            ):
                reflow_logger.debug("    Skipping dedent before comma or semicolon.")
                # We break rather than continue because this is
                # necessarily a step back down.
                break
        else:
            new_indent = inner_indent

        new_results, new_point = e.indent_to(
            new_indent,
            after=elements[e_idx - 1].segments[-1],
            before=elements[e_idx + 1].segments[0],
        )
        # NOTE: Mutation of elements.
        elements[e_idx] = new_point
        line_results += new_results

        # If the balance is *also* negative, then we should also stop.
        # We've indented a whole section - that's enough for now.
        # We've already skipped over any unnecessary sections, and they shouldn't
        # be reassessed on the next pass. If there are later sections which *also*
        # need to be reindented, then we'll catch them when we come back around.
        if indent_stats.trough < 0:
            reflow_logger.debug("    Stopping as we're back down.")
            break

    return line_results


def lint_line_length(
    elements: ReflowSequenceType,
    root_segment: BaseSegment,
    single_indent: str,
    line_length_limit: int,
    allow_implicit_indents: bool = False,
    trailing_comments: str = "before",
) -> Tuple[ReflowSequenceType, List[LintResult]]:
    """Lint the sequence to lines over the configured length.

    NOTE: This assumes that `lint_indent_points` has already
    been run. The method won't necessarily *fail* but it does
    assume that the current indent is correct and that indents
    have already been inserted where they're missing.
    """
    # First check whether we should even be running this check.
    if line_length_limit <= 0:
        reflow_logger.debug("# Line length check disabled.")
        return elements, []

    reflow_logger.debug("# Evaluate lines for length.")
    # Make a working copy to mutate.
    elem_buffer: ReflowSequenceType = elements.copy()
    line_buffer: ReflowSequenceType = []
    results: List[LintResult] = []

    last_indent_idx = None
    for i, elem in enumerate(elem_buffer):
        # Are there newlines in the element?
        # If not, add it to the buffer and wait to evaluate the line.
        # If yes, it's time to evaluate the line.

        if isinstance(elem, ReflowPoint) and (
            # Is it the end of the file?
            # NOTE: Here, we're actually looking to see whether we're
            # currently on the _point before the end of the file_ rather
            # than actually on the final block. This is important because
            # the following code assumes we're on a point and not a block.
            # We're safe from indexing errors if we're on a point, because
            # we know there's always a trailing block.
            "end_of_file" in elem_buffer[i + 1].class_types
            # Or is there a newline?
            or has_untemplated_newline(elem)
        ):
            # In either case we want to process this, so carry on.
            pass
        else:
            # Otherwise build up the buffer and loop around again.
            line_buffer.append(elem)
            continue

        # If we don't have a buffer yet, also carry on. Nothing to lint.
        if not line_buffer:
            continue

        # Evaluate a line

        # Get the current indent.
        if last_indent_idx is not None:
            current_indent = _deduce_line_current_indent(elem_buffer, last_indent_idx)
        else:
            current_indent = ""

        # Get the length of all the elements on the line (other than the indent).
        # NOTE: This is the length in the _source_, because that's the line
        # length that the reader is actually looking at.
        char_len = _source_char_len(line_buffer)

        # Is the line over the limit length?
        line_len = len(current_indent) + char_len
        # NOTE: We should be able to rely on the first elements of the line having
        # a non-zero number of segments. If this isn't the case we may need to add
        # a clause to handle that scenario here.
        assert line_buffer[0].segments
        first_seg = line_buffer[0].segments[0]
        line_no = first_seg.pos_marker.working_line_no
        if line_len <= line_length_limit:
            reflow_logger.info(
                "    Line #%s. Length %s <= %s. OK.",
                line_no,
                line_len,
                line_length_limit,
            )
        else:
            reflow_logger.info(
                "    Line #%s. Length %s > %s. PROBLEM.",
                line_no,
                line_len,
                line_length_limit,
            )

            # Potential places to shorten the line are either indent locations
            # or segments with a defined line position (like operators).

            # NOTE: We make a buffer including the closing point, because we're
            # looking for pairs of indents and dedents. The closing dedent for one
            # of those pairs might be in the closing point so if we don't have it
            # then we'll miss any locations which have their closing dedent at
            # the end of the line.
            line_elements = line_buffer + [elem]

            # Type hints
            fixes: List[LintFix]

            # Identify rebreak spans first so we can work out their indentation
            # in the next section.
            # NOTE: In identifying spans, we give the method a little more than
            # the line, so that it can correctly identify the ends of things
            # accurately. It's safe to go to i+1 because there is always an
            # end_of_file marker at the end which we could span into.
            spans = identify_rebreak_spans(
                line_elements + [elements[i + 1]], root_segment
            )
            reflow_logger.debug("    spans: %s", spans)
            rebreak_priorities = _rebreak_priorities(spans)
            reflow_logger.debug("    rebreak_priorities: %s", rebreak_priorities)

            # Identify indent points second, taking into
            # account rebreak_priorities.
            matched_indents = _match_indents(
                line_elements,
                rebreak_priorities,
                i,
                allow_implicit_indents=allow_implicit_indents,
            )
            reflow_logger.debug("    matched_indents: %s", matched_indents)

            # If we don't have any matched_indents, we don't have any options.
            # This could be for things like comment lines.
            desc = f"Line is too long ({line_len} > {line_length_limit})."
            # Easiest option are lines ending with comments, but that aren't *all*
            # comments and the comment itself is shorter than the limit.
            # The reason for that last clause is that if the comment (plus an indent)
            # is already longer than the limit, then there's no point just putting it
            # on a new line - it will still fail - so it doesn't actually fix the issue.
            # Deal with them first.
            if (
                len(line_buffer) > 1
                # We can only fix _inline_ comments in this way. Others should
                # just be flagged as issues.
                and line_buffer[-1].segments[-1].is_type("inline_comment")
            ):
                reflow_logger.debug("    Handling as inline comment line.")
                elem_buffer, fixes = _fix_long_line_with_comment(
                    line_buffer,
                    elem_buffer,
                    current_indent,
                    line_length_limit,
                    last_indent_idx,
                    trailing_comments=trailing_comments,
                )

            # Then check for cases where we have no other options.
            elif not matched_indents:
                # NOTE: In this case we have no options for shortening the line.
                # We'll still report a linting issue - but no fixes are provided.
                reflow_logger.debug("    Handling as unfixable line.")
                fixes = []

            # Lastly deal with the "normal" case.
            else:
                # For now, the algorithm we apply isn't particularly elegant
                # and just finds the "outermost" opportunity to add additional
                # line breaks and adds them.
                # TODO: Make this more elegant later. The two obvious directions
                # would be to potentially add a) line breaks at multiple levels
                # in a single pass and b) to selectively skip levels if they're
                # "trivial", or if there would be a more suitable inner indent
                # to add first (e.g. the case of "(((((((a)))))))").
                reflow_logger.debug("    Handling as normal line.")
                # NOTE: Double indents (or more likely dedents) will be
                # potentially in *multiple* sets - don't double count them
                # if we start doing something more clever.
                target_balance = min(matched_indents.keys())
                desired_indent = current_indent
                if target_balance >= 1:
                    desired_indent += single_indent
                target_breaks = matched_indents[target_balance]
                reflow_logger.debug(
                    "    Targeting balance of %s, indent: %r for %s",
                    target_balance,
                    desired_indent,
                    target_breaks,
                )

                # Is one of the locations the final element? If so remove it.
                # There's already a line break there.
                if i in target_breaks:
                    target_breaks.remove(i)

                # Is it an "integer" indent or a fractional indent?
                # Integer indents (i.e. 1.0, 2.0, ...) are based on Indent and
                # Dedent tokens. Fractional indents (i.e. 1.5, 1.52, ...) are
                # based more on rebreak spans (e.g. around commas and operators).
                # The latter is simpler in that it doesn't change the indents,
                # just adds line breaks. The former is more complicated.
                # NOTE: Both of these methods mutate the `elem_buffer`.
                if target_balance % 1 == 0:
                    line_results = _fix_long_line_with_integer_targets(
                        elem_buffer,
                        target_breaks,
                        line_length_limit,
                        desired_indent,
                        current_indent,
                    )
                else:
                    line_results = _fix_long_line_with_fractional_targets(
                        elem_buffer, target_breaks, desired_indent
                    )

                # Consolidate all the results for the line into one.
                fixes = fixes_from_results(line_results)

            results.append(
                LintResult(
                    # First segment on the line is the result anchor.
                    first_seg,
                    fixes=fixes,
                    description=desc,
                    source="reflow.long_line",
                )
            )

        # Regardless of whether the line was good or not, clear
        # the buffers ready for the next line.
        line_buffer = []
        last_indent_idx = i

    return elem_buffer, results
