"""Raw segment definitions.

This is designed to be the root segment, without
any children, and the output of the lexer.
"""

from typing import Any, Callable, Optional, Union, cast
from uuid import uuid4

import regex as re

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
        instance_types: tuple[str, ...] = (),
        trim_start: Optional[tuple[str, ...]] = None,
        trim_chars: Optional[tuple[str, ...]] = None,
        source_fixes: Optional[list[SourceFix]] = None,
        uuid: Optional[int] = None,
        quoted_value: Optional[tuple[str, Union[int, str]]] = None,
        escape_replacements: Optional[list[tuple[str, str]]] = None,
        casefold: Optional[Callable[[str], str]] = None,
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
        self.instance_types: tuple[str, ...]
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
        self.quoted_value = quoted_value
        self.escape_replacements = escape_replacements
        self.casefold = casefold
        self._raw_value: str = self.normalize()

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
    def raw_segments(self) -> list["RawSegment"]:
        """Returns self to be compatible with calls to its superclass."""
        return [self]

    @property
    def class_types(self) -> frozenset[str]:
        """The set of full types for this segment, including inherited.

        Add the surrogate type for raw segments.
        """
        return frozenset(self.instance_types) | super().class_types

    @property
    def source_fixes(self) -> list[SourceFix]:
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

    def get_raw_segments(self) -> list["RawSegment"]:
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

    def normalize(self, value: Optional[str] = None) -> str:
        """Returns the normalized version of a string using the segment's rules.

        By default this uses the raw value of the segment.
        E.g. This removes leading and trailing quote characters, removes escapes

        Return:
        str: The normalized value
        """
        raw_buff = value or self.raw
        if self.quoted_value:
            _match = re.match(self.quoted_value[0], raw_buff)
            if _match:
                _group_match = _match.group(self.quoted_value[1])
                if isinstance(_group_match, str):
                    raw_buff = _group_match
        if self.escape_replacements:
            for old, new in self.escape_replacements:
                raw_buff = re.sub(old, new, raw_buff)
        return raw_buff

    def raw_normalized(self, casefold: bool = True) -> str:
        """Returns a normalized string of the raw content.

        E.g. This removes leading and trailing quote characters, removes escapes,
        optionally casefolds to the dialect's casing

        Return:
        str: The normalized version of the raw content
        """
        raw_buff = self._raw_value
        if self.casefold and casefold:
            raw_buff = self.casefold(raw_buff)
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
        self, raw: Optional[str] = None, source_fixes: Optional[list[SourceFix]] = None
    ) -> "RawSegment":
        """Create a new segment, with exactly the same position but different content.

        Args:
            raw (Optional[str]): The new content for the segment.
            source_fixes (Optional[list[SourceFix]]): A list of fixes to be applied to
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
            quoted_value=self.quoted_value,
            escape_replacements=self.escape_replacements,
            casefold=self.casefold,
            source_fixes=source_fixes or self.source_fixes,
        )

    def _get_raw_segment_kwargs(self) -> dict[str, Any]:
        return {
            "quoted_value": self.quoted_value,
            "escape_replacements": self.escape_replacements,
            "casefold": self.casefold,
        }

    # ################ CLASS METHODS

    @classmethod
    def from_result_segments(
        cls,
        result_segments: tuple[BaseSegment, ...],
        segment_kwargs: dict[str, Any],
    ) -> "RawSegment":
        """Create a RawSegment from result segments."""
        assert len(result_segments) == 1
        raw_seg = cast("RawSegment", result_segments[0])
        new_segment_kwargs = raw_seg._get_raw_segment_kwargs()
        new_segment_kwargs.update(segment_kwargs)
        return cls(
            raw=raw_seg.raw,
            pos_marker=raw_seg.pos_marker,
            **new_segment_kwargs,
        )


__all__ = [
    "PositionMarker",
    "RawSegment",
    "SourceFix",
]
