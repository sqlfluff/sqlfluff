"""Build chained-call indent elements without importing ReflowSequence."""

from collections.abc import Iterator

from sqlfluff.core.parser import BaseSegment, Dedent, Indent
from sqlfluff.utils.reflow.elements import (
    ReflowBlock,
    ReflowPoint,
    ReflowSequenceType,
)


def call_groups(root: BaseSegment) -> Iterator[tuple[BaseSegment, BaseSegment]]:
    """Yield the first and last calls of each contiguous chain in the tree."""
    parents: dict[int, BaseSegment] = {}
    for call in root.recursive_crawl("chained_function_call"):
        parent = root.path_to(call)[-1].segment
        parents[parent.uuid] = parent
    for parent in parents.values():
        first: BaseSegment | None = None
        last: BaseSegment | None = None
        for child in parent.segments:
            if child.is_type("chained_function_call"):
                first = first or child
                last = child
            elif child.is_code and first is not None:
                assert last is not None
                yield first, last
                first = last = None
        if first is not None:
            assert last is not None
            yield first, last


def model_chained_indents(
    elements: ReflowSequenceType, root: BaseSegment
) -> ReflowSequenceType:
    """Copy whole-root elements and add balanced markers around each chain.

    Requires elements for the whole root: a focused slice may omit the group's
    start or end, whereas this helper locates both boundaries in the model.
    """
    modeled = elements.copy()
    block_indexes = {
        raw.uuid: index
        for index, element in enumerate(modeled)
        if isinstance(element, ReflowBlock)
        for raw in element.segments
    }
    for first, last in call_groups(root):
        first_raw, last_raw = first.raw_segments[0], last.raw_segments[-1]
        assert first_raw.pos_marker is not None and last_raw.pos_marker is not None
        for index, marker in (
            (
                block_indexes[first_raw.uuid] - 1,
                Indent(pos_marker=first_raw.pos_marker.start_point_marker()),
            ),
            (
                block_indexes[last_raw.uuid] + 1,
                Dedent(pos_marker=last_raw.pos_marker.end_point_marker()),
            ),
        ):
            if index == len(modeled):
                # A complete expression can end at the group's last block.
                modeled.append(ReflowPoint(segments=()))
            point = modeled[index]
            assert isinstance(point, ReflowPoint)
            modeled[index] = ReflowPoint(segments=(marker, *point.segments))
    return modeled
