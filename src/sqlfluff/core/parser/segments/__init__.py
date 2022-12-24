"""Definitions of the segment classes."""

from sqlfluff.core.parser.segments.base import (
    BaseSegment,
    BaseFileSegment,
    UnparsableSegment,
    BracketedSegment,
    IdentitySet,
    FixPatch,
    SourceFix,
)
from sqlfluff.core.parser.segments.generator import SegmentGenerator
from sqlfluff.core.parser.segments.raw import (
    RawSegment,
    CodeSegment,
    UnlexableSegment,
    CommentSegment,
    WhitespaceSegment,
    NewlineSegment,
    KeywordSegment,
    SymbolSegment,
)
from sqlfluff.core.parser.segments.ephemeral import EphemeralSegment, allow_ephemeral
from sqlfluff.core.parser.segments.meta import (
    MetaSegment,
    Indent,
    Dedent,
    ImplicitIndent,
    TemplateSegment,
    EndOfFile,
    TemplateLoop,
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
    "IdentitySet",
    "FixPatch",
    "SourceFix",
)
