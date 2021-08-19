""" The MSSQL T-SQL dialect.

https://docs.microsoft.com/en-us/sql/t-sql/language-elements/language-elements-transact-sql


"""
from enum import Enum
from typing import Generator, List, Tuple, NamedTuple, Optional, Union

from sqlfluff.core.parser import (
    Matchable,
    BaseSegment,
    KeywordSegment,
    SymbolSegment,
    Sequence,
    GreedyUntil,
    StartsWith,
    OneOf,
    Delimited,
    Bracketed,
    AnyNumberOf,
    Ref,
    SegmentGenerator,
    Anything,
    Indent,
    Dedent,
    Nothing,
    OptionallyBracketed,
    StringLexer,
    RegexLexer,
    CodeSegment,
    CommentSegment,
    WhitespaceSegment,
    NewlineSegment,
    StringParser,
    NamedParser,
    RegexParser,
    Conditional,
)

from sqlfluff.core.dialects.base import Dialect
from sqlfluff.core.dialects.common import AliasInfo
from sqlfluff.core.parser.segments.base import BracketedSegment

from sqlfluff.dialects.ansi_keywords import (
    ansi_reserved_keywords,
    ansi_unreserved_keywords,
)
from sqlfluff.dialects.tsql_keywords import (
    # BARE_FUNCTIONS,
    RESERVED_KEYWORDS,
    # UNRESERVED_KEYWORDS,
)

from sqlfluff.core.dialects import load_raw_dialect


ansi_dialect = load_raw_dialect("ansi")
tsql_dialect = ansi_dialect.copy_as("tsql")

# Update only RESERVED Keywords
# tsql_dialect.sets("reserved_keywords").clear()
# tsql_dialect.sets("reserved_keywords").update(RESERVED_KEYWORDS)

tsql_dialect.add(
    AtSignLiteralSegment=NamedParser(
        "atsign",
        CodeSegment,
        name="atsign_literal",
        type="literal",
        trim_chars=("@",),
    ),
)

tsql_dialect.add(    
    AtSignSignSegment=StringParser(
        "@", SymbolSegment, name="atsign", type="user_designator"
    ),   
    SessionVariableNameSegment=RegexParser(
        r"[@][a-zA-Z0-9_]*",
        CodeSegment,
        name="declared_variable",
        type="variable",
    ),
)

tsql_dialect.replace(
    ParameterNameSegment=RegexParser(
        r"`?[A-Za-z0-9_]*`?", CodeSegment, name="parameter", type="parameter"
    )
)

tsql_dialect.insert_lexer_matchers(
    [
        RegexLexer(
            "atsign",
            r"[@][a-zA-Z0-9_]*",
            CodeSegment,
        ),
    ],
    before="code",
)