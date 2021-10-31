"""Indent and Dedent classes."""

from sqlfluff.core.parser.match_wrapper import match_wrapper
from sqlfluff.core.parser.segments.raw import RawSegment
from sqlfluff.core.parser.context import ParseContext
from typing import Optional, List


class MetaSegment(RawSegment):
    """A segment which is empty but indicates where something should be."""

    type = "meta"
    _is_code = False
    _template = "<unset>"
    indent_val = 0
    is_meta = True

    def __init__(self, is_template=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_template = is_template

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
    def simple(cls, parse_context: ParseContext) -> Optional[List[str]]:
        """Does this matcher support an uppercase hash matching route?

        This should be true if the MATCH grammar is simple. Most more
        complicated segments will be assumed to overwrite this method
        if they wish to be considered simple.
        """
        return None


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
    """A segment which is empty but indicates something should be.

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

    def __init__(self, pos_marker=None, source_str="", block_type=""):
        """Initialise a placeholder with the source code embedded."""
        if not source_str:  # pragma: no cover
            raise ValueError("Cannot instantiate TemplateSegment without a source_str.")
        self.source_str = source_str
        self.block_type = block_type
        # Call the super of the pos_marker.
        super().__init__(pos_marker=pos_marker)

    def _suffix(self):
        """Also output what it's a placeholder for."""
        return f"[Type: {self.block_type!r}, Raw: {self.source_str!r}]"

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
