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


# Bracket pairs (a set of tuples).
# (name, startref, endref, persists)
# NOTE: The `persists` value controls whether this type
# of bracket is persisted during matching to speed up other
# parts of the matching process. Round brackets are the most
# common and match the largest areas and so are sufficient.
ansi_dialect.sets("bracket_pairs").update(
    [
        ("round", "StartBracketSegment", "EndBracketSegment", True),
        ("square", "StartSquareBracketSegment", "EndSquareBracketSegment", True),
        ("curly", "StartCurlyBracketSegment", "EndCurlyBracketSegment", False),
    ]
)


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
        r"[@][A-Za-z0-9_]+", CodeSegment, name="parameter", type="parameter"
    )
)

tsql_dialect.insert_lexer_matchers(
    [
        RegexLexer(
            "atsign",
            r"[@][a-zA-Z0-9_]+",
            CodeSegment,
        ),
    ],
    before="code",
)


@tsql_dialect.segment(replace=True)
class CreateFunctionStatementSegment(BaseSegment):
    """A `CREATE FUNCTION` statement.

    This version in the ANSI dialect should be a "common subset" of the
    structure of the code for those dialects.
    postgres: https://www.postgresql.org/docs/9.1/sql-createfunction.html
    snowflake: https://docs.snowflake.com/en/sql-reference/sql/create-function.html
    bigquery: https://cloud.google.com/bigquery/docs/reference/standard-sql/user-defined-functions
    """

    type = "create_function_statement"

    match_grammar = Sequence(
        "CREATE",
        Sequence("OR", "ALTER", optional=True),
        Ref("TemporaryGrammar", optional=True),
        "FUNCTION",
        Anything(),
    )
    parse_grammar = Sequence(
        "CREATE",
        Sequence("OR", "ALTER", optional=True),
        Ref("TemporaryGrammar", optional=True),
        "FUNCTION",       
        Sequence(
            Ref("StartSquareBracketSegment", optional=True),
            Ref("FunctionNameSegment"),
            Ref("EndSquareBracketSegment", optional=True),
            Ref("DotSegment"), optional=True),               
        Sequence(
            Ref("StartSquareBracketSegment", optional=True),
            Ref("FunctionNameSegment"),
            Ref("EndSquareBracketSegment", optional=True)),
        Ref("FunctionParameterListGrammar"),
        Sequence(  # Optional function return type
            "RETURNS",
            Ref("DatatypeSegment"),
            optional=True,
        ),
        Sequence("AS"),
        Sequence("BEGIN"),
        Ref("FunctionDefinitionGrammar"),
        Sequence("END"),
        Sequence("GO", optional=True),
    )


@tsql_dialect.segment(replace=True)
class FunctionDefinitionGrammar(BaseSegment):
    """This is the body of a `CREATE FUNCTION AS` statement."""

    match_grammar = Sequence(        
        GreedyUntil("RETURN", optional=True),
        Sequence("RETURN"),
        GreedyUntil("END"),
    )