"""Definitions of the segment classes."""

# flake8: noqa: F401

from src.sqlfluff.core.parser.segments.base import BaseSegment, UnparsableSegment
from src.sqlfluff.core.parser.segments.generator import SegmentGenerator
from src.sqlfluff.core.parser.segments.raw import RawSegment
from src.sqlfluff.core.parser.segments.ephemeral import EphemeralSegment
from src.sqlfluff.core.parser.segments.indent import Indent, Dedent, TemplateSegment
from src.sqlfluff.core.parser.segments.keyword import (
    KeywordSegment,
    SymbolSegment,
    ReSegment,
    NamedSegment,
)
