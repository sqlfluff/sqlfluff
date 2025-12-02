"""Common segment types used as building blocks of dialects.

The expectation for these segments is that they have no additional
logic (or very minimal logic).
"""

from sqlfluff.core.parser.segments.base import BaseSegment
from sqlfluff.core.parser.segments.raw import RawSegment


class CodeSegment(RawSegment):
    """An alias for RawSegment.

    This has a more explicit name for segment creation.
    """

    pass


class UnlexableSegment(CodeSegment):
    """A placeholder to unlexable sections.

    This otherwise behaves exactly like a code section.
    """

    type = "unlexable"


class CommentSegment(RawSegment):
    """Segment containing a comment."""

    type = "comment"
    _is_code = False
    _is_comment = True


class WhitespaceSegment(RawSegment):
    """Segment containing whitespace."""

    type = "whitespace"
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
    _is_whitespace = True
    _is_code = False
    _is_comment = False
    _default_raw = "\n"


class SymbolSegment(CodeSegment):
    """A segment used for matching single entities which aren't keywords.

    We rename the segment class here so that descendants of
    _ProtoKeywordSegment can use the same functionality
    but don't end up being labelled as a `keyword` later.
    """

    type = "symbol"


class IdentifierSegment(CodeSegment):
    """An identifier segment.

    Defined here for type inheritance.
    """

    type = "identifier"


class LiteralSegment(CodeSegment):
    """A literal segment.

    Defined here for type inheritance.
    """

    type = "literal"


class BinaryOperatorSegment(CodeSegment):
    """A binary operator segment.

    Defined here for type inheritance. Inherits from RawSegment.
    """

    type = "binary_operator"


class CompositeBinaryOperatorSegment(BaseSegment):
    """A composite binary operator segment.

    Defined here for type inheritance. Inherits from BaseSegment.
    """

    type = "binary_operator"


class ComparisonOperatorSegment(CodeSegment):
    """A comparison operator segment.

    Defined here for type inheritance. Inherits from RawSegment.
    """

    type = "comparison_operator"


class CompositeComparisonOperatorSegment(BaseSegment):
    """A comparison operator segment.

    Defined here for type inheritance. Inherits from BaseSegment.
    """

    type = "comparison_operator"


class WordSegment(CodeSegment):
    """A generic (likely letters only) segment.

    Defined here for type inheritance.

    This is the base segment for things like keywords and
    naked identifiers.
    """

    type = "word"
