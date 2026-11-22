"""The DepthMap class is an enriched sequence of raw segments."""

import logging
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from typing import Optional

from sqlfluff.core.parser import BaseSegment
from sqlfluff.core.parser.segments.base import PathStep
from sqlfluff.core.parser.segments.raw import RawSegment

reflow_logger = logging.getLogger("sqlfluff.rules.reflow")


@dataclass(frozen=True)
class StackPosition:
    """An element of the stack_positions property of DepthInfo."""

    idx: int
    len: int
    type: str

    @staticmethod
    def _stack_pos_interpreter(path_step: PathStep) -> str:
        """Interpret a path step for stack_positions."""
        # If no code, then no.
        if not path_step.code_idxs:
            return ""
        # If there's only one code element, this must be it.
        elif len(path_step.code_idxs) == 1:
            return "solo"
        # Check for whether first or last code element.
        # NOTE: code_idxs is always sorted because of how it's constructed.
        # That means the lowest is always as the start and the highest at the end.
        elif path_step.idx == path_step.code_idxs[0]:
            return "start"
        elif path_step.idx == path_step.code_idxs[-1]:
            return "end"
        else:
            return ""  # NOTE: Empty string evaluates as falsy.

    @classmethod
    def from_path_step(cls, path_step: PathStep) -> "StackPosition":
        """Interpret a PathStep to construct a StackPosition.

        The reason we don't just use the same object is partly
        to interpret it a little more, but also to drop the reference
        to a specific segment which could induce bugs at a later
        stage if used.
        """
        return cls(path_step.idx, path_step.len, cls._stack_pos_interpreter(path_step))


@dataclass(frozen=True)
class DepthInfo:
    """An object to hold the depth information for a specific raw segment."""

    stack_depth: int
    stack_hashes: tuple[int, ...]
    # This is a convenience cache to speed up operations.
    stack_hash_set: frozenset[int]
    stack_class_types: tuple[frozenset[str], ...]
    stack_positions: dict[int, StackPosition]

    @classmethod
    def from_raw_and_stack(
        cls, raw: RawSegment, stack: Sequence[PathStep]
    ) -> "DepthInfo":
        """Construct from a raw and its stack."""
        stack_hashes = tuple(hash(ps.segment) for ps in stack)
        return cls(
            stack_depth=len(stack),
            stack_hashes=stack_hashes,
            stack_hash_set=frozenset(stack_hashes),
            stack_class_types=tuple(ps.segment.class_types for ps in stack),
            stack_positions={
                # Reuse the hash first calculated above.
                stack_hashes[idx]: StackPosition.from_path_step(ps)
                for idx, ps in enumerate(stack)
            },
        )

    def common_with(self, other: "DepthInfo") -> tuple[int, ...]:
        """Get the common depth and hashes with the other."""
        if self.stack_hashes is other.stack_hashes and self.stack_hashes:
            return self.stack_hashes
        # We use set intersection because it's faster and hashes should be unique.
        common_hashes = self.stack_hash_set.intersection(other.stack_hashes)
        # We should expect there to be _at least_ one common ancestor, because
        # they should share the same file segment. If that's not the case we
        # we should error because it's likely a bug or programming error.
        assert common_hashes, "DepthInfo comparison shares no common ancestor!"
        common_depth = len(common_hashes)
        return self.stack_hashes[:common_depth]

    def trim(self, amount: int) -> "DepthInfo":
        """Return a DepthInfo object with some amount trimmed."""
        # Excluded from coverage: no longer triggered since AL01 rule was refactored
        if amount == 0:  # pragma: no cover
            # The trivial case.
            return self
        new_hash_set = self.stack_hash_set.difference(self.stack_hashes[-amount:])
        return self.__class__(
            stack_depth=self.stack_depth - amount,
            stack_hashes=self.stack_hashes[:-amount],
            stack_hash_set=new_hash_set,
            stack_class_types=self.stack_class_types[:-amount],
            stack_positions={
                k: v for k, v in self.stack_positions.items() if k in new_hash_set
            },
        )


@dataclass(slots=True)
class _DepthFrame:
    """Mutable traversal frame for `DepthMap.from_parent()`."""

    children: Iterator[tuple[int, BaseSegment]]
    hashes: tuple[int, ...]
    hash_set: Optional[frozenset[int]]
    class_types: tuple[frozenset[str], ...]
    positions: dict[int, StackPosition]
    parent_hash: int
    stack_depth: int
    num_children: int
    last_idx: int
    solo: bool
    first_code: int
    last_code: int


class DepthMap:
    """A mapping of raw segments to depth and parent information.

    This class addresses two needs:
    - To understand configuration of segments with no whitespace
      within them - so the config is related to the parent and
      not the segment)
    - To map the depth of an indent points to apply some precedence
      for where to insert line breaks.

    The internals are structured around a list to do lookups
    and a dict (keyed with the raw segment UUID) to hold the rest.

    """

    def __init__(self, raws_with_stack: Sequence[tuple[RawSegment, list[PathStep]]]):
        self.depth_info = {}
        for raw, stack in raws_with_stack:
            self.depth_info[raw.uuid] = DepthInfo.from_raw_and_stack(raw, stack)

    @classmethod
    def from_parent(cls: type["DepthMap"], parent: BaseSegment) -> "DepthMap":
        """Generate a DepthMap from all the children of a segment.

        NOTE: This is the most efficient way to construct a DepthMap. It
        gives the same result as building each raw segment's `DepthInfo`
        from its stack (see `raw_segments_with_ancestors`), but walks the
        tree once, and shares the parts of each stack that siblings have in
        common rather than rebuilding them for every raw segment. It walks
        with a loop rather than recursion.
        """
        depth_map = cls(raws_with_stack=())
        depth_info = depth_map.depth_info
        # Precomputing code_idxs and child bounds once per parent avoids
        # redoing that work each time the loop resumes after a non-raw child.
        root_segments = parent.segments
        root_hash = hash(parent)
        root_hashes: tuple[int, ...] = (root_hash,)
        root_code_idxs = parent._code_indices
        root_num = len(root_segments)
        stack: list[_DepthFrame] = [
            _DepthFrame(
                children=enumerate(root_segments),
                hashes=root_hashes,
                hash_set=None,
                class_types=(parent.class_types,),
                positions={},
                parent_hash=root_hash,
                stack_depth=1,
                num_children=root_num,
                last_idx=root_num - 1,
                solo=len(root_code_idxs) == 1,
                first_code=root_code_idxs[0] if root_code_idxs else -1,
                last_code=root_code_idxs[-1] if root_code_idxs else -1,
            )
        ]
        stack_pos_cls = StackPosition
        depth_info_cls = DepthInfo
        frame_cls = _DepthFrame
        pos_cache: dict[tuple[int, int, str], StackPosition] = {}
        while stack:
            frame = stack[-1]
            hashes = frame.hashes
            hash_set = frame.hash_set
            class_types = frame.class_types
            positions = frame.positions
            parent_hash = frame.parent_hash
            stack_depth = frame.stack_depth
            num_children = frame.num_children
            last_idx = frame.last_idx
            solo = frame.solo
            first_code = frame.first_code
            last_code = frame.last_code
            for idx, child in frame.children:
                if solo:
                    pos_type = "solo"
                elif idx == first_code:
                    pos_type = "start"
                elif idx == last_code:
                    pos_type = "end"
                else:
                    pos_type = ""
                # Reuse the parent's positions dict for its last child (which
                # includes every single-child wrapper); no later sibling will
                # read it again.
                child_positions = positions if idx == last_idx else positions.copy()
                pos_key = (idx, num_children, pos_type)
                stack_pos = pos_cache.get(pos_key)
                if stack_pos is None:
                    stack_pos = stack_pos_cls(idx, num_children, pos_type)
                    pos_cache[pos_key] = stack_pos
                child_positions[parent_hash] = stack_pos
                if isinstance(child, RawSegment):
                    if hash_set is None:
                        hash_set = frozenset(hashes)
                        frame.hash_set = hash_set
                    depth_info[child.uuid] = depth_info_cls(
                        stack_depth=stack_depth,
                        stack_hashes=hashes,
                        stack_hash_set=hash_set,
                        stack_class_types=class_types,
                        stack_positions=child_positions,
                    )
                else:
                    child_segments = child.segments
                    child_hash = hash(child)
                    child_code_idxs = child._code_indices
                    child_num = len(child_segments)
                    stack.append(
                        frame_cls(
                            children=enumerate(child_segments),
                            hashes=hashes + (child_hash,),
                            hash_set=None,
                            class_types=class_types + (child.class_types,),
                            positions=child_positions,
                            parent_hash=child_hash,
                            stack_depth=stack_depth + 1,
                            num_children=child_num,
                            last_idx=child_num - 1,
                            solo=len(child_code_idxs) == 1,
                            first_code=child_code_idxs[0] if child_code_idxs else -1,
                            last_code=child_code_idxs[-1] if child_code_idxs else -1,
                        )
                    )
                    break
            else:
                stack.pop()
        return depth_map

    @classmethod
    def from_raws_and_root(
        cls: type["DepthMap"],
        raw_segments: Sequence[RawSegment],
        root_segment: BaseSegment,
    ) -> "DepthMap":
        """Generate a DepthMap a sequence of raws and a root.

        NOTE: This is the less efficient way to construct a DepthMap
        as it doesn't take advantage of caching in the same way as
        `from_parent`.
        """
        buff = []
        for raw in raw_segments:
            stack = root_segment.path_to(raw)
            buff.append((raw, stack))
        return cls(raws_with_stack=buff)

    def get_depth_info(self, raw: RawSegment) -> DepthInfo:
        """Get the depth info for a given segment."""
        try:
            return self.depth_info[raw.uuid]
        except KeyError as err:  # pragma: no cover
            reflow_logger.exception("Available UUIDS: %s", self.depth_info.keys())
            raise KeyError(
                "Tried to get depth info for unknown "
                f"segment {raw} with UUID {raw.uuid}"
            ) from err

    def copy(self) -> "DepthMap":
        """Return a copy, so `copy_depth_info()` on it doesn't change this one."""
        depth_map = self.__class__(raws_with_stack=())
        depth_map.depth_info = self.depth_info.copy()
        return depth_map

    def copy_depth_info(
        self, anchor: RawSegment, new_segment: RawSegment, trim: int = 0
    ) -> None:
        """Copy the depth info for one segment and apply to another.

        This mutates the existing depth map. That's ok because it's
        an idempotent operation and uuids should be unique.

        This is used in edits to a reflow sequence when new segments are
        inserted and can't infer their own depth info.

        NOTE: we don't remove the old one because it causes no harm.
        """
        self.depth_info[new_segment.uuid] = self.get_depth_info(anchor).trim(trim)
