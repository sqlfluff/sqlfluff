""" The MSSQL T-SQL dialect.

https://docs.microsoft.com/en-us/sql/t-sql/language-elements/language-elements-transact-sql


"""
from enum import Enum
from typing import Generator, List, Tuple, NamedTuple, Optional, Union

from sqlfluff.core.parser import (
    Matchable,
    RawSegment,
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

# from sqlfluff.dialects.tsql_keywords import (
#     # BARE_FUNCTIONS,
#     RESERVED_KEYWORDS,
#     # UNRESERVED_KEYWORDS,
# )

from sqlfluff.core.dialects import load_raw_dialect

ansi_dialect = load_raw_dialect("ansi")
tsql_dialect = ansi_dialect.copy_as("tsql")


# Update only RESERVED Keywords
# tsql_dialect.sets("reserved_keywords").clear()
# tsql_dialect.sets("reserved_keywords").update(RESERVED_KEYWORDS)


tsql_dialect.replace(
    ParameterNameSegment=RegexParser(
        r"[@][A-Za-z0-9_]+", CodeSegment, name="parameter", type="parameter"
    ),
    QuotedIdentifierSegment=Bracketed(
        RegexParser(
          r"[A-Z][A-Z0-9_]*", CodeSegment, name="quoted_identifier", type="identifier"
        ),
        bracket_type="square",
    ),
    # QuotedIdentifierSegment=NamedParser(
    #     BracketedSegment(
    #         CodeSegment,        
    #         start_bracket="sq_brackets_open",
    #         end_bracket="sq_brackets_close",
    #     ),
    #     name="quoted_identifier",
    #     type="identifier",
    # )
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


@tsql_dialect.segment()
class SchemaNameSegment(BaseSegment):
    """This is a schema name optionally bracketed"""
    type = "schema_name"
    name = "schema"
    match_grammar = Sequence(
            
            Ref("StartSquareBracketSegment", optional=True),
            Ref("SingleIdentifierGrammar"),
            Ref("EndSquareBracketSegment", optional=True),
            Ref("DotSegment")
        )

@tsql_dialect.segment()
class ObjectNameSegment(BaseSegment):
    """This is the body of a `CREATE FUNCTION AS` statement."""
    type = "object_name"
    match_grammar = Sequence(
            Ref("StartSquareBracketSegment", optional=True),
            Ref("SingleIdentifierGrammar"),
            Ref("EndSquareBracketSegment", optional=True),
        )



@tsql_dialect.segment(replace=True)
class CreateFunctionStatementSegment(BaseSegment):
    """A `CREATE FUNCTION` statement.

    This version in the TSQL dialect should be a "common subset" of the
    structure of the code for those dialects.
    postgres: https://www.postgresql.org/docs/9.1/sql-createfunction.html
    snowflake: https://docs.snowflake.com/en/sql-reference/sql/create-function.html
    bigquery: https://cloud.google.com/bigquery/docs/reference/standard-sql/user-defined-functions
    tsql/mssql : https://docs.microsoft.com/en-us/sql/t-sql/statements/create-function-transact-sql?view=sql-server-ver15
    """

    type = "create_function_statement"

    match_grammar = Sequence(
        "CREATE",
        Sequence("OR", "ALTER", optional=True),
        "FUNCTION",
        Anything(),
    )
    parse_grammar = Sequence(
        "CREATE",
        Sequence("OR", "ALTER", optional=True),
        "FUNCTION",        
        Ref("SchemaNameSegment"),
        Ref("ObjectNameSegment"),
        Ref("FunctionParameterListGrammar"),
        Sequence(  # Optional function return type
            "RETURNS",
            Ref("DatatypeSegment"),
            optional=True,
        ),
       "AS",       
        Ref("FunctionDefinitionGrammar"),
    )

@tsql_dialect.segment(replace=True)
class FunctionDefinitionGrammar(BaseSegment):
    """This is the body of a `CREATE FUNCTION AS` statement."""
    type = "function_statement"
    name = "function_statement"

    match_grammar = Sequence(        
        Anything()
    )

# @tsql_dialect.segment()
# class FunctionReturnGrammar(BaseSegment):
#     """This is the body of a `CREATE FUNCTION AS` statement."""
#     type = "function_return_statement"
#     name = "function_return_statement"
#     match_grammar = Sequence(        
#         Anything()        
#     )
