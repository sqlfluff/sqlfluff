"""The MSSQL T-SQL dialect.

https://docs.microsoft.com/en-us/sql/t-sql/language-elements/language-elements-transact-sql
"""

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
    Delimited,
    AnyNumberOf,
    Matchable,
    NamedParser,
)

from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.dialects.tsql_keywords import RESERVED_KEYWORDS

ansi_dialect = load_raw_dialect("ansi")
tsql_dialect = ansi_dialect.copy_as("tsql")

# Update only RESERVED Keywords
# Should really clear down the old keywords but some are needed by certain segments
# tsql_dialect.sets("reserved_keywords").clear()
tsql_dialect.sets("reserved_keywords").update(RESERVED_KEYWORDS)


tsql_dialect.insert_lexer_matchers(
    [
        RegexLexer(
            "atsign",
            r"[@][a-zA-Z0-9_]+",
            CodeSegment,
        ),
        RegexLexer(
            "square_quote",
            r"\[([a-zA-Z][^\[\]]*)*\]",
            CodeSegment,
        ),
    ],
    before="back_quote",
)

tsql_dialect.add(
    BracketedIdentifierSegment=NamedParser(
        "square_quote", CodeSegment, name="quoted_identifier", type="identifier"
    ),
)

tsql_dialect.replace(
    # Below delimiterstatement might need to be removed in the future as delimiting
    # is optional with semicolon and GO is a end of statement indicator.
    DelimiterSegment=OneOf(
        Sequence(Ref("SemicolonSegment"), Ref("GoStatementSegment")),
        Ref("SemicolonSegment"),
        Ref("GoStatementSegment"),
    ),
    SingleIdentifierGrammar=OneOf(
        Ref("NakedIdentifierSegment"),
        Ref("QuotedIdentifierSegment"),
        Ref("BracketedIdentifierSegment"),
    ),
    ParameterNameSegment=RegexParser(
        r"[@][A-Za-z0-9_]+", CodeSegment, name="parameter", type="parameter"
    ),
    FunctionNameIdentifierSegment=RegexParser(
        r"[A-Z][A-Z0-9_]*|\[[A-Z][A-Z0-9_]*\]",
        CodeSegment,
        name="function_name_identifier",
        type="function_name_identifier",
    ),
    DatatypeIdentifierSegment=Ref("SingleIdentifierGrammar"),
)


@tsql_dialect.segment(replace=True)
class StatementSegment(ansi_dialect.get_segment("StatementSegment")):  # type: ignore
    """Overriding StatementSegment to allow for additional segment parsing."""

    parse_grammar = ansi_dialect.get_segment("StatementSegment").parse_grammar.copy(
        insert=[
            Ref("CreateProcedureStatementSegment"),
        ],
    )


@tsql_dialect.segment(replace=True)
class ObjectReferenceSegment(BaseSegment):
    """A reference to an object.

    Update ObjectReferenceSegment to only allow dot separated SingleIdentifierGrammar
    So Square Bracketed identifers can be matched.
    """

    type = "object_reference"
    # match grammar (don't allow whitespace)

    match_grammar: Matchable = Delimited(
        Ref("SingleIdentifierGrammar"),
        delimiter=OneOf(
            Ref("DotSegment"), Sequence(Ref("DotSegment"), Ref("DotSegment"))
        ),
        allow_gaps=False,
    )


@tsql_dialect.segment()
class GoStatementSegment(BaseSegment):
    """This is a Go statement to signal end of batch."""

    type = "go_statement"
    match_grammar = Sequence("GO")


@tsql_dialect.segment(replace=True)
class TableReferenceSegment(ObjectReferenceSegment):
    """TableReferenceSegment.

    Update TableReferenceSegment to only allow dot separated SingleIdentifierGrammar
    So Square Bracketed identifers can be matched.
    """

    type = "table_reference"
    match_grammar: Matchable = Delimited(
        Ref("SingleIdentifierGrammar"),
        delimiter=OneOf(
            Ref("DotSegment"), Sequence(Ref("DotSegment"), Ref("DotSegment"))
        ),
        allow_gaps=False,
    )


@tsql_dialect.segment(replace=True)
class DatatypeSegment(BaseSegment):
    """A data type segment.

    Supports timestamp with(out) time zone. Doesn't currently support intervals.
    """

    type = "data_type"
    match_grammar = Sequence(
        # Some dialects allow optional qualification of data types with schemas
        Sequence(
            Ref("SingleIdentifierGrammar"),
            Ref("DotSegment"),
            allow_gaps=False,
            optional=True,
        ),
        OneOf(
            Ref("DatatypeIdentifierSegment"),
            Bracketed(Ref("DatatypeIdentifierSegment"), bracket_type="square"),
        ),
        Bracketed(
            OneOf(
                Delimited(Ref("ExpressionSegment")),
                # The brackets might be empty for some cases...
                optional=True,
            ),
            # There may be no brackets for some data types
            optional=True,
        ),
        Ref("CharCharacterSetSegment", optional=True),
    )


@tsql_dialect.segment(replace=True)
class ColumnOptionSegment(BaseSegment):
    """A column option; each CREATE TABLE column can have 0 or more."""

    type = "column_constraint"
    # Column constraint from
    # https://www.postgresql.org/docs/12/sql-createtable.html
    match_grammar = Sequence(
        Sequence(
            "CONSTRAINT",
            Ref("ObjectReferenceSegment"),  # Constraint name
            optional=True,
        ),
        OneOf(
            Sequence(Ref.keyword("NOT", optional=True), "NULL"),  # NOT NULL or NULL
            Sequence(  # DEFAULT <value>
                "DEFAULT",
                OneOf(
                    Ref("LiteralGrammar"),
                    Ref("FunctionSegment"),
                    # ?? Ref('IntervalExpressionSegment')
                ),
            ),
            Ref("PrimaryKeyGrammar"),
            "UNIQUE",  # UNIQUE
            "CLUSTERED",
            "AUTO_INCREMENT",  # AUTO_INCREMENT (MySQL)
            "UNSIGNED",  # UNSIGNED (MySQL)
            Sequence(  # REFERENCES reftable [ ( refcolumn) ]
                "REFERENCES",
                Ref("ColumnReferenceSegment"),
                # Foreign columns making up FOREIGN KEY constraint
                Ref("BracketedColumnReferenceListGrammar", optional=True),
            ),
            Ref("CommentClauseSegment"),
        ),
    )


@tsql_dialect.segment(replace=True)
class ColumnDefinitionSegment(BaseSegment):
    """A column definition, e.g. for CREATE TABLE or ALTER TABLE."""

    type = "column_definition"
    match_grammar = Sequence(
        Ref("SingleIdentifierGrammar"),
        Ref("DatatypeSegment"),  # Column type
        Bracketed(Anything(), optional=True),  # For types like VARCHAR(100)
        AnyNumberOf(
            Ref("ColumnOptionSegment", optional=True),
        ),
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
        Ref("ObjectReferenceSegment"),
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

    match_grammar = Sequence(Anything())


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
        Ref("ObjectReferenceSegment"),
        Ref("FunctionParameterListGrammar", optional=True),
        "AS",
        Ref("ProcedureDefinitionGrammar"),
    )


@tsql_dialect.segment()
class ProcedureDefinitionGrammar(BaseSegment):
    """This is the body of a `CREATE OR ALTER PROCEDURE AS` statement."""

    type = "procedure_statement"
    name = "procedure_statement"

    match_grammar = Sequence(Anything())


@tsql_dialect.segment(replace=True)
class CreateViewStatementSegment(BaseSegment):
    """A `CREATE VIEW` statement."""

    type = "create_view_statement"
    # https://docs.microsoft.com/en-us/sql/t-sql/statements/create-view-transact-sql?view=sql-server-ver15#examples
    match_grammar = Sequence(
        "CREATE",
        Sequence("OR", "ALTER", optional=True),
        "VIEW",
        Ref("ObjectReferenceSegment"),
        "AS",
        Ref("SelectableGrammar"),
        Ref("GoStatementSegment", optional=True),
    )


# @tsql_dialect.segment(replace=True)
# class StatementSegment(BaseSegment):
#     """A generic segment, to any of its child subsegments."""

#     type = "statement"
#     match_grammar = GreedyUntil(Ref("DelimiterSegment"))

#     parse_grammar = OneOf(
#         Ref("SelectableGrammar"),
#         Ref("InsertStatementSegment"),
#         Ref("TransactionStatementSegment"),
#         Ref("DropStatementSegment"),
#         Ref("TruncateStatementSegment"),
#         # Ref("AlterDefaultPrivilegesSegment"),
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
#         Ref("CreateProcedureStatementSegment")
#     )

#     def get_table_references(self):
#         """Use parsed tree to extract table references."""
#         table_refs = {
#             tbl_ref.raw for tbl_ref in self.recursive_crawl("table_reference")
#         }
#         cte_refs = {
#             cte_def.get_identifier().raw
#             for cte_def in self.recursive_crawl("common_table_expression")
#         }
#         # External references are any table references which aren't
#         # also cte aliases.
#         return table_refs - cte_refs


# @tsql_dialect.segment(replace=True)
# class CreateTableStatementSegment(BaseSegment):
#     """A `CREATE TABLE` statement."""

#     type = "create_table_statement"
#     # https://docs.microsoft.com/en-us/sql/t-sql/statements/create-table-transact-sql?view=sql-server-ver15

#     match_grammar = Sequence(
#         "CREATE",
#         Ref("OrReplaceGrammar", optional=True),
#         Ref("TemporaryTransientGrammar", optional=True),
#         "TABLE",
#         Ref("IfNotExistsGrammar", optional=True),
#         Ref("TableReferenceSegment"),
#         Sequence(
#                 Bracketed(
#                     Delimited(
#                         OneOf(
#                             Ref("TableConstraintSegment"),
#                             Ref("ColumnDefinitionSegment"),
#                         ),
#                     )
#                 ),
#                 Ref("CommentClauseSegment", optional=True),
#             ),
#         # Anything(),
#         # OneOf(
#         #     # Columns and comment syntax:
#         #     Sequence(
#         #         Bracketed(
#         #             Delimited(
#         #                 OneOf(
#         #                     Ref("TableConstraintSegment"),
#         #                     Ref("ColumnDefinitionSegment"),
#         #                 ),
#         #             )
#         #         ),
#         #         Ref("CommentClauseSegment", optional=True),
#         #     ),
#             # # Create AS syntax:
#             # Sequence(
#             #     "AS",
#             #     OptionallyBracketed(Ref("SelectableGrammar")),
#             # ),
#             # # Create like syntax
#             # Sequence("LIKE", Ref("TableReferenceSegment")),
#         # ),
#         # Anything(),
#         # Ref("GoStatementSegment", optional=True),
#     )
