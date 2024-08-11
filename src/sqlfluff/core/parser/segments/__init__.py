"""Definitions of the segment classes."""

from sqlfluff.core.parser.segments.base import (
    BaseSegment,
    SourceFix,
    UnparsableSegment,
)
from sqlfluff.core.parser.segments.bracketed import BracketedSegment
from sqlfluff.core.parser.segments.common import (
    BinaryOperatorSegment,
    CodeSegment,
    CommentSegment,
    ComparisonOperatorSegment,
    CompositeBinaryOperatorSegment,
    CompositeComparisonOperatorSegment,
    IdentifierSegment,
    LiteralSegment,
    NewlineSegment,
    SymbolSegment,
    UnlexableSegment,
    WhitespaceSegment,
    WordSegment,
)
from sqlfluff.core.parser.segments.file import BaseFileSegment
from sqlfluff.core.parser.segments.generator import SegmentGenerator
from sqlfluff.core.parser.segments.keyword import KeywordSegment, LiteralKeywordSegment
from sqlfluff.core.parser.segments.meta import (
    Dedent,
    EndOfFile,
    ImplicitIndent,
    Indent,
    MetaSegment,
    TemplateLoop,
    TemplateSegment,
)
from sqlfluff.core.parser.segments.raw import RawSegment

__all__ = (
    "BaseSegment",
    "BaseFileSegment",
    "UnparsableSegment",
    "BracketedSegment",
    "SegmentGenerator",
    "RawSegment",
    "CodeSegment",
    "UnlexableSegment",
    "CommentSegment",
    "WhitespaceSegment",
    "NewlineSegment",
    "KeywordSegment",
    "LiteralKeywordSegment",
    "SymbolSegment",
    "MetaSegment",
    "Indent",
    "Dedent",
    "ImplicitIndent",
    "TemplateSegment",
    "EndOfFile",
    "TemplateLoop",
    "SourceFix",
    "IdentifierSegment",
    "LiteralSegment",
    "BinaryOperatorSegment",
    "CompositeBinaryOperatorSegment",
    "ComparisonOperatorSegment",
    "CompositeComparisonOperatorSegment",
    "WordSegment",
)
