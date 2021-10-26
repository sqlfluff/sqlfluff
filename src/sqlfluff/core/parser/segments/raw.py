"""Raw segment definitions.

This is designed to be the root segment, without
any children, and the output of the lexer.
"""

from typing import Optional, Tuple

from sqlfluff.core.parser.segments.base import BaseSegment
from sqlfluff.core.parser.markers import PositionMarker


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
        type: Optional[str] = None,
        name: Optional[str] = None,
        trim_start: Optional[Tuple[str, ...]] = None,
        trim_chars: Optional[Tuple[str, ...]] = None,
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
        # if a surrogate type is provided, store it for later.
        self._surrogate_type = type
        self._surrogate_name = name
        # What should we trim off the ends to get to content
        self.trim_start = trim_start
        self.trim_chars = trim_chars
        # A cache variable for expandable
        self._is_expandable = None

    def __repr__(self):
        return "<{}: ({}) {!r}>".format(
            self.__class__.__name__, self.pos_marker, self.raw
        )

    def __setattr__(self, key, value):
        """Overwrite BaseSegment's __setattr__ with BaseSegment's superclass."""
        super(BaseSegment, self).__setattr__(key, value)

    # ################ PUBLIC PROPERTIES

    @property
    def matched_length(self):
        """Return the length of the segment in characters."""
        return len(self._raw)

    @property
    def is_expandable(self):
        """Return true if it is meaningful to call `expand` on this segment."""
        return False

    @property
    def is_code(self):
        """Return True if this segment is code."""
        return self._is_code

    @property
    def is_comment(self):
        """Return True if this segment is a comment."""
        return self._is_comment

    @property
    def is_whitespace(self):
        """Return True if this segment is whitespace."""
        return self._is_whitespace

    @property
    def raw(self):
        """Returns the raw segment."""
        return self._raw

    @property
    def raw_upper(self):
        """Returns the raw segment in uppercase."""
        return self._raw_upper

    @property
    def raw_segments(self):
        """Returns self to be compatible with calls to its superclass."""
        return [self]

    @property
    def segments(self):
        """Return an empty list of child segments.

        This is in case something tries to iterate on this segment.
        """
        return []

    # ################ INSTANCE METHODS

    def invalidate_caches(self):
        """Overwrite superclass functionality."""
        pass

    def get_type(self):
        """Returns the type of this segment as a string."""
        return self._surrogate_type or self.type

    def is_type(self, *seg_type):
        """Extend the parent class method with the surrogate types."""
        if self._surrogate_type and self._surrogate_type in seg_type:
            return True
        return self.class_is_type(*seg_type)

    def get_raw_segments(self):
        """Iterate raw segments, mostly for searching."""
        return [self]

    def raw_trimmed(self):
        """Return a trimmed version of the raw content."""
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

    def raw_list(self):  # pragma: no cover TODO?
        """Return a list of the raw content of this segment."""
        return [self.raw]

    def stringify(self, ident=0, tabsize=4, code_only=False):
        """Use indentation to render this segment and its children as a string."""
        preface = self._preface(ident=ident, tabsize=tabsize)
        return preface + "\n"

    def _suffix(self):
        """Return any extra output required at the end when logging.

        NB Override this for specific subclasses if we want extra output.
        """
        return f"{self.raw!r}"

    def edit(self, raw):
        """Create a new segment, with exactly the same position but different content.

        Returns:
            A copy of this object with new contents.

        Used mostly by fixes.

        """
        return self.__class__(
            raw=raw,
            pos_marker=self.pos_marker,
            type=self._surrogate_type,
            name=self._surrogate_name,
            trim_start=self.trim_start,
            trim_chars=self.trim_chars,
        )


class CodeSegment(RawSegment):
    """An alias for RawSegment.

    This has a more explicit name for segment creation.
    """

    pass


class UnlexableSegment(CodeSegment):
    """A placeholder to unlexable sections.

    This otherwise behaves exaclty like a code section.
    """

    type = "unlexable"


class CommentSegment(RawSegment):
    """Segment containing a comment."""

    type = "comment"
    _name = "comment"
    _is_code = False
    _is_comment = True


class WhitespaceSegment(RawSegment):
    """Segment containing whitespace."""

    type = "whitespace"
    _name = "whitespace"
    _is_whitespace = True
    _is_code = False
    _is_comment = False
    _default_raw = " "


class NewlineSegment(RawSegment):
    """Segment containing a newline.

    NOTE: NewlineSegment does not inherit from WhitespaceSegment.
    Therefore NewlineSegment.is_type('whitespace') returns False.

    This is intentional and convenient for rules. If users want
    to match on both, call .is_type('whitespace', 'newline')
    """

    type = "newline"
    _name = "newline"
    _is_whitespace = True
    _is_code = False
    _is_comment = False
    _default_raw = "\n"


class KeywordSegment(CodeSegment):
    """A segment used for matching single words.

    We rename the segment class here so that descendants of
    _ProtoKeywordSegment can use the same functionality
    but don't end up being labelled as a `keyword` later.
    """

    type = "keyword"

    def __init__(
        self,
        raw: Optional[str] = None,
        pos_marker: Optional[PositionMarker] = None,
        type: Optional[str] = None,
        name: Optional[str] = None,
    ):
        """If no other name is provided we extrapolate it from the raw."""
        if raw and not name:
            # names are all lowercase by convention.
            name = raw.lower()
        super().__init__(raw=raw, pos_marker=pos_marker, type=type, name=name)

    def edit(self, raw):
        """Create a new segment, with exactly the same position but different content.

        Returns:
            A copy of this object with new contents.

        Used mostly by fixes.

        """
        return self.__class__(
            raw=raw,
            pos_marker=self.pos_marker,
            type=self._surrogate_type,
            name=self._surrogate_name,
        )


class SymbolSegment(CodeSegment):
    """A segment used for matching single entities which aren't keywords.

    We rename the segment class here so that descendants of
    _ProtoKeywordSegment can use the same functionality
    but don't end up being labelled as a `keyword` later.
    """

    type = "symbol"
