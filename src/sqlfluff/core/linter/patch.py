"""Helpers for generating patches to fix files."""

import logging
from dataclasses import dataclass
from typing import (
    Iterator,
    List,
    Tuple,
)

from sqlfluff.core.parser import (
    BaseSegment,
)
from sqlfluff.core.templaters import TemplatedFile

linter_logger = logging.getLogger("sqlfluff.linter")


@dataclass
class FixPatch:
    """An edit patch for a source file."""

    templated_slice: slice
    fixed_raw: str
    # The patch category, functions mostly for debugging and explanation
    # than for function. It allows traceability of *why* this patch was
    # generated. It has no significance for processing.
    patch_category: str
    source_slice: slice
    templated_str: str
    source_str: str

    def dedupe_tuple(self) -> Tuple[slice, str]:
        """Generate a tuple of this fix for deduping."""
        return (self.source_slice, self.fixed_raw)


def _iter_source_fix_patches(
    segment: BaseSegment, templated_file: TemplatedFile
) -> Iterator[FixPatch]:
    """Yield any source patches as fixes now.

    NOTE: This yields source fixes for the segment and any of its
    children, so it's important to call it at the right point in
    the recursion to avoid yielding duplicates.
    """
    for source_fix in segment.source_fixes:
        yield FixPatch(
            source_fix.templated_slice,
            source_fix.edit,
            patch_category="source",
            source_slice=source_fix.source_slice,
            templated_str=templated_file.templated_str[source_fix.templated_slice],
            source_str=templated_file.source_str[source_fix.source_slice],
        )


def _iter_templated_patches(
    segment: BaseSegment, templated_file: TemplatedFile
) -> Iterator[FixPatch]:
    """Iterate through the segments generating fix patches.

    The patches are generated in TEMPLATED space. This is important
    so that we defer dealing with any loops until later. At this stage
    everything *should* happen in templated order.

    Occasionally we have an insertion around a placeholder, so we also
    return a hint to deal with that.
    """
    # Does it match? If so we can ignore it.
    assert segment.pos_marker
    templated_raw = templated_file.templated_str[segment.pos_marker.templated_slice]
    matches = segment.raw == templated_raw
    if matches:
        # First yield any source fixes
        yield from _iter_source_fix_patches(segment, templated_file)
        # Then return.
        return

    # If we're here, the segment doesn't match the original.
    linter_logger.debug(
        "# Changed Segment Found: %s at %s: Original: [%r] Fixed: [%r]",
        type(segment).__name__,
        segment.pos_marker.templated_slice,
        templated_raw,
        segment.raw,
    )

    # If it's all literal, then we don't need to recurse.
    if segment.pos_marker.is_literal():
        # First yield any source fixes
        yield from _iter_source_fix_patches(segment, templated_file)
        # Then yield the position in the source file and the patch
        yield FixPatch(
            source_slice=segment.pos_marker.source_slice,
            templated_slice=segment.pos_marker.templated_slice,
            patch_category="literal",
            fixed_raw=segment.raw,
            templated_str=templated_file.templated_str[
                segment.pos_marker.templated_slice
            ],
            source_str=templated_file.source_str[segment.pos_marker.source_slice],
        )
    # Can we go deeper?
    elif not segment.segments:
        # It's not literal, but it's also a raw segment. If we're going
        # to yield a change, we would have done it from the parent, so
        # we just abort from here.
        return  # pragma: no cover TODO?
    else:
        # This segment isn't a literal, but has changed, we need to go deeper.

        # If there's an end of file segment or indent, ignore them just for the
        # purposes of patch iteration.
        # NOTE: This doesn't mutate the underlying `self.segments`.
        segments = segment.segments
        while segments and segments[-1].is_type("end_of_file", "indent"):
            segments = segments[:-1]

        # Iterate through the child segments
        source_idx = segment.pos_marker.source_slice.start
        templated_idx = segment.pos_marker.templated_slice.start
        insert_buff = ""
        for seg in segments:
            # First check for insertions.
            # At this stage, everything should have a position.
            assert seg.pos_marker
            # We know it's an insertion if it has length but not in the templated
            # file.
            if seg.raw and seg.pos_marker.is_point():
                # Add it to the insertion buffer if it has length:
                if seg.raw:
                    insert_buff += seg.raw
                    linter_logger.debug(
                        "Appending insertion buffer. %r @idx: %s",
                        insert_buff,
                        templated_idx,
                    )
                continue

            # If we get here, then we know it's an original. Check for deletions at
            # the point before this segment (vs the TEMPLATED).
            # Deletions in this sense could also mean source consumption.
            start_diff = seg.pos_marker.templated_slice.start - templated_idx

            # Check to see whether there's a discontinuity before the current
            # segment
            if start_diff > 0 or insert_buff:
                # If we have an insert buffer, then it's an edit, otherwise a
                # deletion.

                # For the start of the next segment, we need the position of the
                # first raw, not the pos marker of the whole thing. That accounts
                # better for loops.
                first_segment_pos = seg.raw_segments[0].pos_marker
                yield FixPatch(
                    # Whether the source slice is zero depends on the start_diff.
                    # A non-zero start diff implies a deletion, or more likely
                    # a consumed element of the source. We can use the tracking
                    # markers from the last segment to recreate where this element
                    # should be inserted in both source and template.
                    source_slice=slice(
                        source_idx,
                        first_segment_pos.source_slice.start,
                    ),
                    templated_slice=slice(
                        templated_idx,
                        first_segment_pos.templated_slice.start,
                    ),
                    patch_category="mid_point",
                    fixed_raw=insert_buff,
                    templated_str="",
                    source_str="",
                )

                insert_buff = ""

            # Now we deal with any changes *within* the segment itself.
            yield from _iter_templated_patches(seg, templated_file=templated_file)

            # Once we've dealt with any patches from the segment, update
            # our position markers.
            source_idx = seg.pos_marker.source_slice.stop
            templated_idx = seg.pos_marker.templated_slice.stop

        # After the loop, we check whether there's a trailing deletion
        # or insert. Also valid if we still have an insertion buffer here.
        end_diff = segment.pos_marker.templated_slice.stop - templated_idx
        if end_diff or insert_buff:
            source_slice = slice(
                source_idx,
                segment.pos_marker.source_slice.stop,
            )
            templated_slice = slice(
                templated_idx,
                segment.pos_marker.templated_slice.stop,
            )
            # We determine the source_slice directly rather than
            # inferring it so that we can be very specific that
            # we ensure that fixes adjacent to source-only slices
            # (e.g. {% endif %}) are placed appropriately relative
            # to source-only slices.
            yield FixPatch(
                source_slice=source_slice,
                templated_slice=templated_slice,
                patch_category="end_point",
                fixed_raw=insert_buff,
                templated_str=templated_file.templated_str[templated_slice],
                source_str=templated_file.source_str[source_slice],
            )


def _log_hints(patch: FixPatch, templated_file: TemplatedFile):
    """Log hints for debugging during patch generation."""
    max_log_length = 10
    if patch.templated_slice.start >= max_log_length:
        pre_hint = templated_file.templated_str[
            patch.templated_slice.start - max_log_length : patch.templated_slice.start
        ]
    else:
        pre_hint = templated_file.templated_str[: patch.templated_slice.start]
    if patch.templated_slice.stop + max_log_length < len(templated_file.templated_str):
        post_hint = templated_file.templated_str[
            patch.templated_slice.stop : patch.templated_slice.stop + max_log_length
        ]
    else:
        post_hint = templated_file.templated_str[patch.templated_slice.stop :]
    linter_logger.debug("        Templated Hint: ...%r <> %r...", pre_hint, post_hint)


def generate_source_patches(
    tree: BaseSegment, templated_file: TemplatedFile
) -> List[FixPatch]:
    """Use the fixed tree to generate source patches.

    Importantly here we deduplicate and sort the patches from their position
    in the templated file into their intended order in the source file.

    Any source fixes are generated in `_iter_templated_patches` and included
    alongside any standard fixes. That means we treat them the same here.
    """
    # Iterate patches, filtering and translating as we go:
    linter_logger.debug("### Beginning Patch Iteration.")
    filtered_source_patches = []
    dedupe_buffer = []
    # We use enumerate so that we get an index for each patch. This is entirely
    # so when debugging logs we can find a given patch again!
    for idx, patch in enumerate(
        _iter_templated_patches(tree, templated_file=templated_file)
    ):
        linter_logger.debug("  %s Yielded patch: %s", idx, patch)
        _log_hints(patch, templated_file)

        # Check for duplicates
        if patch.dedupe_tuple() in dedupe_buffer:
            linter_logger.info(
                "      - Skipping. Source space Duplicate: %s",
                patch.dedupe_tuple(),
            )
            continue

        # We now evaluate patches in the source-space for whether they overlap
        # or disrupt any templated sections unless designed to do so.
        # NOTE: We rely here on the patches being generated in order.

        # Get the affected raw slices.
        local_raw_slices = templated_file.raw_slices_spanning_source_slice(
            patch.source_slice
        )
        local_type_list = [slc.slice_type for slc in local_raw_slices]

        # Deal with the easy cases of 1) New code at end 2) only literals
        if not local_type_list or set(local_type_list) == {"literal"}:
            linter_logger.info(
                "      * Keeping patch on new or literal-only section.",
            )
            filtered_source_patches.append(patch)
            dedupe_buffer.append(patch.dedupe_tuple())
        # Handle the easy case of an explicit source fix
        elif patch.patch_category == "source":
            linter_logger.info(
                "      * Keeping explicit source fix patch.",
            )
            filtered_source_patches.append(patch)
            dedupe_buffer.append(patch.dedupe_tuple())
        # Is it a zero length patch.
        elif (
            patch.source_slice.start == patch.source_slice.stop
            and patch.source_slice.start == local_raw_slices[0].source_idx
        ):
            linter_logger.info(
                "      * Keeping insertion patch on slice boundary.",
            )
            filtered_source_patches.append(patch)
            dedupe_buffer.append(patch.dedupe_tuple())
        else:  # pragma: no cover
            # We've got a situation where the ends of our patch need to be
            # more carefully mapped. This used to happen with greedy template
            # element matching, but should now never happen. In the event that
            # it does, we'll warn but carry on.
            linter_logger.warning(
                "Skipping edit patch on uncertain templated section [%s], "
                "Please report this warning on GitHub along with the query "
                "that produced it.",
                (patch.patch_category, patch.source_slice),
            )
            continue

    # Sort the patches before building up the file.
    return sorted(filtered_source_patches, key=lambda x: x.source_slice.start)
