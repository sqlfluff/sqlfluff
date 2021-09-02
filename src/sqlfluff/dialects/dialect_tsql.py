""" The MSSQL T-SQL dialect.

https://docs.microsoft.com/en-us/sql/t-sql/language-elements/language-elements-transact-sql


"""
from enum import Enum
from typing import Generator, List, Tuple, NamedTuple, Optional, Union

from sqlfluff.core.parser import (
    
    BaseSegment,
    
    Sequence,
    
    OneOf,
   
    Bracketed,
   
    Ref,
    
    Anything,
    
    RegexLexer,
    CodeSegment,
   
    RegexParser,
    
)

from sqlfluff.core.dialects.base import Dialect
from sqlfluff.core.dialects.common import AliasInfo
from sqlfluff.core.parser.segments.base import BracketedSegment

from sqlfluff.dialects.ansi_keywords import (
    ansi_reserved_keywords,
    ansi_unreserved_keywords,
)



from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.dialects.dialect_ansi import StatementSegment

ansi_dialect = load_raw_dialect("ansi")
tsql_dialect = ansi_dialect.copy_as("tsql")


# Update only RESERVED Keywords, not working yet, error UsingKeywordSegment
# from sqlfluff.dialects.tsql_keywords import (
#     RESERVED_KEYWORDS,
# )
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

# Below statement or similar is required to make sqlfluff understand the different statements within a file as these are not seperated by semicolons.
@tsql_dialect.segment(replace=True)
class StatementSegment(BaseSegment):
    """A generic segment, to any of its child subsegments."""

    type = "statement"
    match_grammar = OneOf(
        Ref("SelectableGrammar"),
        Ref("InsertStatementSegment"),
        Ref("TransactionStatementSegment"),
        Ref("DropStatementSegment"),
        Ref("TruncateStatementSegment"),
        Ref("AlterDefaultPrivilegesSegment"),
        Ref("AccessStatementSegment"),
        Ref("CreateTableStatementSegment"),
        Ref("CreateTypeStatementSegment"),
        Ref("CreateRoleStatementSegment"),
        Ref("AlterTableStatementSegment"),
        Ref("CreateSchemaStatementSegment"),
        Ref("SetSchemaStatementSegment"),
        Ref("DropSchemaStatementSegment"),
        Ref("CreateDatabaseStatementSegment"),
        Ref("CreateExtensionStatementSegment"),
        Ref("CreateIndexStatementSegment"),
        Ref("DropIndexStatementSegment"),
        Ref("CreateViewStatementSegment"),
        Ref("DeleteStatementSegment"),
        Ref("UpdateStatementSegment"),
        Ref("CreateFunctionStatementSegment"),
        Ref("CreateModelStatementSegment"),
        Ref("DropModelStatementSegment"),
        Ref("DescribeStatementSegment"),
        Ref("UseStatementSegment"),
        Ref("ExplainStatementSegment"),
        Ref("ExplainStatementSegment"),
        Ref("CreateProcedureStatementSegment"),
    )

#     parse_grammar = OneOf(
#         Ref("SelectableGrammar"),
#         Ref("InsertStatementSegment"),
#         Ref("TransactionStatementSegment"),
#         Ref("DropStatementSegment"),
#         Ref("TruncateStatementSegment"),
#         Ref("AlterDefaultPrivilegesSegment"),
#         Ref("AccessStatementSegment"),
#         Ref("CreateTableStatementSegment"),
#         Ref("CreateTypeStatementSegment"),
#         Ref("CreateRoleStatementSegment"),
#         Ref("AlterTableStatementSegment"),
#         Ref("CreateSchemaStatementSegment"),
#         Ref("SetSchemaStatementSegment"),
#         Ref("DropSchemaStatementSegment"),
#         Ref("CreateDatabaseStatementSegment"),
#         Ref("CreateExtensionStatementSegment"),
#         Ref("CreateIndexStatementSegment"),
#         Ref("DropIndexStatementSegment"),
#         Ref("CreateViewStatementSegment"),
#         Ref("DeleteStatementSegment"),
#         Ref("UpdateStatementSegment"),
#         Ref("CreateFunctionStatementSegment"),
#         Ref("CreateModelStatementSegment"),
#         Ref("DropModelStatementSegment"),
#         Ref("DescribeStatementSegment"),
#         Ref("UseStatementSegment"),
#         Ref("ExplainStatementSegment"),
#     )

@tsql_dialect.segment()
class GoStatementSegment(BaseSegment):
    """This is a Go statement to signal end of batch"""
    type = "go_statement"
    type = "go_statement"
    match_grammar = Sequence("GO")

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
        Ref("GoStatementSegment", optional=True),
    )

@tsql_dialect.segment(replace=True)
class FunctionDefinitionGrammar(BaseSegment):
    """This is the body of a `CREATE FUNCTION AS` statement."""
    type = "function_statement"
    name = "function_statement"

    match_grammar = Sequence(        
        Anything()
    )


@tsql_dialect.segment()
class CreateProcedureStatementSegment(BaseSegment):
    """A `CREATE PROCEDURE` statement.
    https://docs.microsoft.com/en-us/sql/t-sql/statements/create-procedure-transact-sql?view=sql-server-ver15
    """

    type = "create_procedure_statement"

    match_grammar = Sequence(
        "CREATE",
        Sequence("OR", "ALTER", optional=True),
        OneOf("PROCEDURE", "PROC"),
        Ref("SchemaNameSegment", optional=True),
        Ref("ObjectNameSegment"),
        Ref("FunctionParameterListGrammar", optional=True),
        "AS",
        Ref("ProcedureDefinitionGrammar"),
        Ref("GoStatementSegment", optional=True),
    )


@tsql_dialect.segment()
class ProcedureDefinitionGrammar(BaseSegment):
    """This is the body of a `CREATE OR ALTER PROCEDURE AS` statement."""
    type = "procedure_statement"
    name = "procedure_statement"

    match_grammar = Sequence(        
        Anything()
    )

@tsql_dialect.segment(replace=True)
class CreateViewStatementSegment(BaseSegment):
    """A `CREATE VIEW` statement."""

    type = "create_view_statement"
    # https://docs.microsoft.com/en-us/sql/t-sql/statements/create-view-transact-sql?view=sql-server-ver15#examples
    match_grammar = Sequence(
        "CREATE",
        Sequence("OR", "ALTER", optional=True),
        "VIEW",
        Ref("SchemaNameSegment", optional=True),
        Ref("ObjectNameSegment"),
        "AS",
        Ref("SelectableGrammar"),
        Ref("GoStatementSegment", optional=True),
        
    )