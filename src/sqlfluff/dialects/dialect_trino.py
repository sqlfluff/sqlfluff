"""The Trino dialect."""

from sqlfluff.core.parser import (
    AnyNumberOf,
    Anything,
    BaseSegment,
    Bracketed,
    CodeSegment,
    CommentSegment,
    Dedent,
    Delimited,
    Indent,
    Matchable,
    TypedParser,
    NewlineSegment,
    OneOf,
    OptionallyBracketed,
    Ref,
    RegexLexer,
    RegexParser,
    SegmentGenerator,
    Sequence,
    SymbolSegment,
    StartsWith,
    StringParser,
)
from sqlfluff.core.parser.segments.base import BracketedSegment

from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.core.parser.grammar.anyof import AnySetOf
from sqlfluff.core.parser.lexer import StringLexer
from sqlfluff.dialects.dialect_trino_keywords import (
    trino_reserved_keywords,
    trino_nonreserved_keywords,
)

from sqlfluff.dialects import dialect_ansi as ansi

ansi_dialect = load_raw_dialect("ansi")
trino_dialect = ansi_dialect.copy_as("trino")
