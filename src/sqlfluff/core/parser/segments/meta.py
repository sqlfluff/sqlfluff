"""Indent and Dedent classes."""

from uuid import UUID

from sqlfluff.core.parser.markers import PositionMarker
from sqlfluff.core.parser.match_wrapper import match_wrapper
from sqlfluff.core.parser.segments.raw import RawSegment, SourceFix
from sqlfluff.core.parser.context import ParseContext
from typing import Optional, List

from sqlfluff.core.templaters.base import TemplatedFile


class MetaSegment(RawSegment):
    """A segment which is empty but indicates where something should be."""

    type = "meta"
    _is_code = False
    _template = "<unset>"
    indent_val = 0
    # Implicit indents are to be considered _taken_ unless
    # closed on the same line.
    is_implicit = False
    is_meta = True

    def __init__(
        self,
        is_template: bool = False,
        block_uuid: Optional[UUID] = None,
        *args,
        **kwargs,
    ):
        """Constructor for MetaSegment.

        Args:
            is_template (:obj:`bool`): A flag to indicate whether
                this meta segment is related to a templated section.
                This allows proper handling.
            block_uuid (:obj:`UUID`): A reference to link together
                markers which refer to the same structure in a
                template (e.g. the beginning and end of an if
                statement).
        """
        super().__init__(*args, **kwargs)
        self.is_template = is_template
        self.block_uuid = block_uuid

    @staticmethod
    def _suffix():
        """Return any extra output required at the end when logging.

        Meta classes have not much to say here so just stay blank.
        """
        return ""

    @classmethod
    @match_wrapper()
    def match(cls, segments, parse_context):  # pragma: no cover
        """This will never be called. If it is then we're using it wrong."""
        raise NotImplementedError(
            "{} has no match method, it should only be used in a Sequence!".format(
                cls.__name__
            )
        )

    @classmethod
    def simple(cls, parse_context: ParseContext, crumbs=None) -> Optional[List[str]]:
        """Does this matcher support an uppercase hash matching route?

        This should be true if the MATCH grammar is simple. Most more
        complicated segments will be assumed to overwrite this method
        if they wish to be considered simple.
        """
        return None


class EndOfFile(MetaSegment):
    """A meta segment to indicate the end of the file."""

    type = "end_of_file"


class TemplateLoop(MetaSegment):
    """A meta segment to indicate the presence of a backward template jump.

    More specifically these indicate the presence of where there is a placeholder
    in the source, but in the templated file we don't have one _yet_ because
    we're going back for another pass around a loop.

    These are particularly useful for any rules concernced with layout, because
    and indented TemplateLoop is allowable, but without the marker we would just
    see trailing whitespace.
    """

    type = "template_loop"


class Indent(MetaSegment):
    """A segment which is empty but indicates where an indent should be.

    This segment is always empty, i.e. its raw format is '', but it indicates
    the position of a theoretical indent which will be used in linting
    and reconstruction. Even if there is an *actual indent* that occurs
    in the same place this intentionally *won't* capture it, they will just
    be compared later.
    """

    type = "indent"
    indent_val = 1


class ImplicitIndent(Indent):
    """A variant on the indent, that is considered *taken* unless closed in line.

    This is primarily for facilitating constructions which behave a little
    like hanging indents, without the complicated indentation spacing.

    .. code-block:: sql
        SELECT *
        FROM foo
        WHERE a  -- The theoretical indent between WHERE and "a" is implicit.
            AND b
    """

    is_implicit = True


class Dedent(Indent):
    """A segment which is empty but indicates where an dedent should be.

    This segment is always empty, i.e. its raw format is '', but it indicates
    the position of a theoretical dedent which will be used in linting
    and reconstruction. Even if there is an *actual dedent* that occurs
    in the same place this intentionally *won't* capture it, they will just
    be compared later.

    """

    type = "dedent"
    indent_val = -1


class TemplateSegment(MetaSegment):
    """A segment which is empty but indicates where something should be.

    This segment is always empty, i.e. its raw format is '', but it indicates
    the position of an element on a line which has been removed. This is used
    to record the position of template blocks, so that their indents are not
    removed during linting.

    This is used to hold a reference point for code from the source file
    which is removed in the templated version such as loop blocks or comments.
    On initialisation we optionally accept the source string as a kwarg in
    case rules want to lint this down the line.
    """

    type = "placeholder"

    def __init__(
        self,
        pos_marker: Optional[PositionMarker] = None,
        source_str: str = "",
        block_type: str = "",
        source_fixes: Optional[List[SourceFix]] = None,
        block_uuid: Optional[UUID] = None,
    ):
        """Initialise a placeholder with the source code embedded."""
        if not source_str:  # pragma: no cover
            raise ValueError("Cannot instantiate TemplateSegment without a source_str.")
        self.source_str = source_str
        self.block_type = block_type
        # Call the super of the pos_marker.
        super().__init__(
            pos_marker=pos_marker, source_fixes=source_fixes, block_uuid=block_uuid
        )

    def _suffix(self):
        """Also output what it's a placeholder for."""
        return f"[Type: {self.block_type!r}, Raw: {self.source_str!r}]"

    @classmethod
    def from_slice(
        cls,
        source_slice: slice,
        templated_slice: slice,
        block_type: str,
        templated_file: TemplatedFile,
        block_uuid: Optional[UUID] = None,
    ):
        """Construct template segment from slice of a source file."""
        pos_marker = PositionMarker(
            source_slice,
            templated_slice,
            templated_file,
        )
        return cls(
            pos_marker=pos_marker,
            source_str=templated_file.source_str[source_slice],
            block_type=block_type,
            block_uuid=block_uuid,
        )

    def to_tuple(self, code_only=False, show_raw=False, include_meta=False):
        """Return a tuple structure from this segment.

        Unlike most segments, we return the _source_ content for placeholders
        if viewing metas is allowed. This allows verification of the content
        of those placeholders for inspection or debugging.
        """
        if include_meta:
            return (self.get_type(), self.source_str)
        else:  # pragma: no cover TODO?
            return (self.get_type(), self.raw)

    def edit(
        self,
        raw: Optional[str] = None,
        source_fixes: Optional[List[SourceFix]] = None,
        source_str: Optional[str] = None,
    ):
        """Create a new segment, with exactly the same position but different content.

        Returns:
            A copy of this object with new contents.

        Used mostly by fixes.

        NOTE: This *doesn't* copy the uuid. The edited segment is a new segment.

        """
        if raw:
            raise ValueError(
                "Cannot set raw of a template placeholder!"
            )  # pragma: no cover
        return self.__class__(
            pos_marker=self.pos_marker,
            source_str=source_str if source_str is not None else self.source_str,
            block_type=self.block_type,
            source_fixes=source_fixes or self.source_fixes,
            block_uuid=self.block_uuid,
        )
