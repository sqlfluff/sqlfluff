"""Definitions of the segment classes."""

from sqlfluff.core.parser.segments.base import (
    BaseSegment,
    FixPatch,
    SourceFix,
    UnparsableSegment,
)
from sqlfluff.core.parser.segments.bracketed import BracketedSegment
from sqlfluff.core.parser.segments.ephemeral import EphemeralSegment, allow_ephemeral
from sqlfluff.core.parser.segments.file import BaseFileSegment
from sqlfluff.core.parser.segments.generator import SegmentGenerator
from sqlfluff.core.parser.segments.meta import (
    Dedent,
    EndOfFile,
    ImplicitIndent,
    Indent,
    MetaSegment,
    TemplateLoop,
    TemplateSegment,
)
from sqlfluff.core.parser.segments.raw import (
    CodeSegment,
    CommentSegment,
    KeywordSegment,
    NewlineSegment,
    RawSegment,
    SymbolSegment,
    UnlexableSegment,
    WhitespaceSegment,
)

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
    "SymbolSegment",
    "EphemeralSegment",
    "allow_ephemeral",
    "MetaSegment",
    "Indent",
    "Dedent",
    "ImplicitIndent",
    "TemplateSegment",
    "EndOfFile",
    "TemplateLoop",
    "FixPatch",
    "SourceFix",
)
