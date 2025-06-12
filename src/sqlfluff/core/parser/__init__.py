"""init file for the parser."""

from sqlfluff.core.parser.grammar import (
    AnyNumberOf,
    AnySetOf,
    Anything,
    Bracketed,
    Conditional,
    Delimited,
    Nothing,
    OneOf,
    OptionallyBracketed,
    OptionallyDelimited,
    Ref,
    Sequence,
)
from sqlfluff.core.parser.lexer import LexerType, RegexLexer, StringLexer
from sqlfluff.core.parser.markers import PositionMarker
from sqlfluff.core.parser.matchable import Matchable
from sqlfluff.core.parser.parser import Parser
from sqlfluff.core.parser.parsers import (
    MultiStringParser,
    RegexParser,
    StringParser,
    TypedParser,
)
from sqlfluff.core.parser.segments import (
    BaseFileSegment,
    BaseSegment,
    BinaryOperatorSegment,
    BracketedSegment,
    CodeSegment,
    CommentSegment,
    ComparisonOperatorSegment,
    CompositeBinaryOperatorSegment,
    CompositeComparisonOperatorSegment,
    Dedent,
    IdentifierSegment,
    ImplicitIndent,
    Indent,
    KeywordSegment,
    LiteralKeywordSegment,
    LiteralSegment,
    NewlineSegment,
    RawSegment,
    SegmentGenerator,
    SourceFix,
    SymbolSegment,
    UnlexableSegment,
    WhitespaceSegment,
    WordSegment,
)
from sqlfluff.core.parser.types import ParseMode

try:
    from sqlfluff.core.parser.lexer import PyRsLexer as Lexer
except ImportError:
    from sqlfluff.core.parser.lexer import PyLexer as Lexer  # type: ignore[assignment]

__all__ = (
    "BaseSegment",
    "SourceFix",
    "BaseFileSegment",
    "BracketedSegment",
    "RawSegment",
    "CodeSegment",
    "UnlexableSegment",
    "CommentSegment",
    "WhitespaceSegment",
    "NewlineSegment",
    "KeywordSegment",
    "SymbolSegment",
    "IdentifierSegment",
    "LiteralSegment",
    "LiteralKeywordSegment",
    "BinaryOperatorSegment",
    "CompositeBinaryOperatorSegment",
    "ComparisonOperatorSegment",
    "CompositeComparisonOperatorSegment",
    "WordSegment",
    "Indent",
    "Dedent",
    "ImplicitIndent",
    "SegmentGenerator",
    "Sequence",
    "OneOf",
    "Delimited",
    "Bracketed",
    "AnyNumberOf",
    "AnySetOf",
    "Ref",
    "Anything",
    "Nothing",
    "OptionallyBracketed",
    "OptionallyDelimited",
    "Conditional",
    "StringParser",
    "MultiStringParser",
    "TypedParser",
    "RegexParser",
    "PositionMarker",
    "Lexer",
    "LexerType",
    "StringLexer",
    "RegexLexer",
    "Parser",
    "Matchable",
    "ParseMode",
)
