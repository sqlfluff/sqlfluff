"""Raw segment definitions.

This is designed to be the root segment, without
any children, and the output of the lexer.
"""

from typing import Any, FrozenSet, List, Optional, Tuple
from uuid import uuid4

from sqlfluff.core.parser.markers import PositionMarker
from sqlfluff.core.parser.segments.base import BaseSegment, SourceFix


class RawSegment(BaseSegment):
    """This is a segment without any subsegments."""

    type = "raw"
    _is_code = True
    _is_comment = False
    _is_whitespace = False
    # Classes inheriting from RawSegment may provide a _default_raw
    # to enable simple initialisation.
    _default_raw = ""

    def __init__(
        self,
        raw: Optional[str] = None,
        pos_marker: Optional[PositionMarker] = None,
        # For legacy and syntactic sugar we allow the simple
        # `type` argument here, but for more precise inheritance
        # we suggest using the `instance_types` option.
        type: Optional[str] = None,
        instance_types: Tuple[str, ...] = (),
        trim_start: Optional[Tuple[str, ...]] = None,
        trim_chars: Optional[Tuple[str, ...]] = None,
        source_fixes: Optional[List[SourceFix]] = None,
        uuid: Optional[int] = None,
    ):
        """Initialise raw segment.

        If raw is not provided, we default to _default_raw if present.
        If pos_marker is not provided, it is assume that this will be
        inserted later as part of a reposition phase.
        """
        if raw is not None:  # NB, raw *can* be an empty string and be valid
            self._raw = raw
        else:
            self._raw = self._default_raw
        self._raw_upper = self._raw.upper()
        # pos marker is required here. We ignore the typing initially
        # because it might *initially* be unset, but it will be reset
        # later.
        self.pos_marker: PositionMarker = pos_marker  # type: ignore
        # Set the segments attribute to be an empty tuple.
        self.segments = ()
        self.instance_types: Tuple[str, ...]
        if type:
            assert not instance_types, "Cannot set `type` and `instance_types`."
            self.instance_types = (type,)
        else:
            self.instance_types = instance_types
        # What should we trim off the ends to get to content
        self.trim_start = trim_start
        self.trim_chars = trim_chars
        # Keep track of any source fixes
        self._source_fixes = source_fixes
        # UUID for matching (the int attribute of it)
        self.uuid = uuid or uuid4().int
        self.representation = "<{}: ({}) {!r}>".format(
            self.__class__.__name__, self.pos_marker, self.raw
        )

    def __repr__(self) -> str:
        # This is calculated at __init__, because all elements are immutable
        # and this was previously recalculating the pos marker,
        # and became very expensive
        return self.representation

    def __setattr__(self, key: str, value: Any) -> None:
        """Overwrite BaseSegment's __setattr__ with BaseSegment's superclass."""
        super(BaseSegment, self).__setattr__(key, value)

    # ################ PUBLIC PROPERTIES

    @property
    def is_code(self) -> bool:
        """Return True if this segment is code."""
        return self._is_code

    @property
    def is_comment(self) -> bool:
        """Return True if this segment is a comment."""
        return self._is_comment

    @property
    def is_whitespace(self) -> bool:
        """Return True if this segment is whitespace."""
        return self._is_whitespace

    @property
    def raw(self) -> str:
        """Returns the raw segment."""
        return self._raw

    @property
    def raw_upper(self) -> str:
        """Returns the raw segment in uppercase."""
        return self._raw_upper

    @property
    def raw_segments(self) -> List["RawSegment"]:
        """Returns self to be compatible with calls to its superclass."""
        return [self]

    @property
    def class_types(self) -> FrozenSet[str]:
        """The set of full types for this segment, including inherited.

        Add the surrogate type for raw segments.
        """
        return frozenset(self.instance_types) | super().class_types

    @property
    def source_fixes(self) -> List[SourceFix]:
        """Return any source fixes as list."""
        return self._source_fixes or []

    # ################ INSTANCE METHODS

    def invalidate_caches(self) -> None:
        """Overwrite superclass functionality."""
        pass

    def get_type(self) -> str:
        """Returns the type of this segment as a string."""
        if self.instance_types:
            return self.instance_types[0]
        return super().get_type()

    def is_type(self, *seg_type: str) -> bool:
        """Extend the parent class method with the surrogate types."""
        if set(self.instance_types).intersection(seg_type):
            return True
        return self.class_is_type(*seg_type)

    def get_raw_segments(self) -> List["RawSegment"]:
        """Iterate raw segments, mostly for searching."""
        return [self]

    def raw_trimmed(self) -> str:
        """Return a trimmed version of the raw content.

        Returns:
            str: The trimmed version of the raw content.
        """
        raw_buff = self.raw
        if self.trim_start:
            for seq in self.trim_start:
                if raw_buff.startswith(seq):
                    raw_buff = raw_buff[len(seq) :]
        if self.trim_chars:
            raw_buff = self.raw
            # for each thing to trim
            for seq in self.trim_chars:
                # trim start
                while raw_buff.startswith(seq):
                    raw_buff = raw_buff[len(seq) :]
                # trim end
                while raw_buff.endswith(seq):
                    raw_buff = raw_buff[: -len(seq)]
            return raw_buff
        return raw_buff

    def stringify(
        self, ident: int = 0, tabsize: int = 4, code_only: bool = False
    ) -> str:
        """Use indentation to render this segment and its children as a string.

        Args:
            ident (int, optional): The indentation level. Defaults to 0.
            tabsize (int, optional): The size of each tab. Defaults to 4.
            code_only (bool, optional): Whether to render only the code.
                Defaults to False.

        Returns:
            str: The rendered string.
        """
        preface = self._preface(ident=ident, tabsize=tabsize)
        return preface + "\n"

    def _suffix(self) -> str:
        """Return any extra output required at the end when logging.

        NB Override this for specific subclasses if we want extra output.

        Returns:
            str: The extra output.
        """
        return f"{self.raw!r}"

    def edit(
        self, raw: Optional[str] = None, source_fixes: Optional[List[SourceFix]] = None
    ) -> "RawSegment":
        """Create a new segment, with exactly the same position but different content.

        Args:
            raw (Optional[str]): The new content for the segment.
            source_fixes (Optional[List[SourceFix]]): A list of fixes to be applied to
                the segment.

        Returns:
            RawSegment: A copy of this object with new contents.

        Used mostly by fixes.

        NOTE: This *doesn't* copy the uuid. The edited segment is a new
        segment.

        """
        return self.__class__(
            raw=raw or self.raw,
            pos_marker=self.pos_marker,
            instance_types=self.instance_types,
            trim_start=self.trim_start,
            trim_chars=self.trim_chars,
            source_fixes=source_fixes or self.source_fixes,
        )


__all__ = [
    "PositionMarker",
    "RawSegment",
    "SourceFix",
]
