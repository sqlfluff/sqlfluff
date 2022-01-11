"""The Oracle dialect.

This inherits from the ansi dialect.
"""
from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.core.parser.segments import NewlineSegment
from sqlfluff.core.parser import (
    Anything,
    BaseSegment,
    GreedyUntil,
    CommentSegment,
    RegexLexer,
    Ref,
    Sequence,
    StartsWith,
    OptionallyBracketed,
    OneOf,
)

ansi_dialect = load_raw_dialect("ansi")
oracle_dialect = ansi_dialect.copy_as("oracle")

# https://docs.oracle.com/database/121/SQLRF/ap_keywd001.htm#SQLRF55621
# Remove unused keywords from the dialect.
# oracle_dialect.sets("unreserved_keywords").difference_update(
oracle_dialect.sets("unreserved_keywords").update(["PROMPT"])
#    [
        #  "ABORT",
        #  "ABS",
        #  "ABSOLUTE",
        #  "ACCOUNT",
        #  "ACCOUNTS",
        #  "ACTION",
        #  "ADA",
        #  "ADMIN",
        #  "AFTER",
        #  "AGGREGATE",
        #  "ALIAS",
        #  "ALLOCATE",
        #  "ALSO",
        #  "ALWAYS",
        #  "ANALYSE",
        #  "ANALYZE",
        #  "APPLY",
        #  "ARE",
        #  "ARRAY",
        #  "ASENSITIVE",
        #  "ASSERTION",
        #  "ASSIGNMENT",
        #  "ASYMMETRIC",
        #  "AT",
        #  "ATOMIC",
        #  "ATTRIBUTE",
        #  "ATTRIBUTES",
        #  "AUTHORIZATION",
        #  "AUTO_INCREMENT",
        #  "AVG",
        #  "AVG_ROW_LENGTH",
        #  "BACKUP",
        #  "BACKWARD",
        #  "BEFORE",
        #  "BEGIN",
        #  "BERNOULLI",

        #  "PROMPT",
    #  ]
#  )

#oracle_dialect.insert_lexer_matchers(
#        [
#            RegexLexer("prompt_statement", "(.*)", BaseSegment)
#        ],
#        before=Ref("Anything"),
#    )

#oracle_dialect.patch_lexer_matchers(     
#    [
#        RegexLexer(
#            "inline_comment",
#            r"COMMENT[^\n]*",
#            CommentSegment,
#        ),
#        RegexLexer("prompt_statement", r"PROMPT[^\n]", CommentSegment),
#    ]
#)

#  oracle_dialect.sets("unreserved_keywords").update(
    #  [
        #  "AND",
    #  ]
#  )


@oracle_dialect.segment()
class PromptStatementSegment(BaseSegment):
    """A `Prompt` statement.
    PRO[MPT] [text]
    https://docs.oracle.com/cd/E11882_01/server.112/e16604/ch_twelve032.htm#SQPUG052
    """
    
    type = "prompt_statement"
    
    match_grammar = StartsWith("PROMPT")
    
    parse_grammar = Sequence(
        "PROMPT",
        Anything()
    )

@oracle_dialect.segment()
class CommentStatementSegment(BaseSegment):
    """A `Comment` statement.
    COMMENT [text]
    https://docs.oracle.com/cd/B19306_01/server.102/b14200/statements_4009.htm
    """
    
    type = "comment_statement"
    
    match_grammar = StartsWith(Sequence("COMMENT", "ON"))
    
    parse_grammar = Sequence(
        "COMMENT",
        "ON",
        Sequence(
            OneOf(
                Sequence(
                    OneOf(
                        "TABLE",
                        "VIEW",
                    ),
                    Ref("TableReferenceSegment"),
                ),
                Sequence(
                    "COLUMN",
                    Ref("ColumnReferenceSegment"),
                ),
                Sequence(
                    "OPERATOR",
                    Ref("OperatorReferenceSegment"),
                ),
                #Sequence(
                #    "INDEXTYPE",
                #    Ref("IndexTypeReferenceSegment"),
                #),
                Sequence(
                    "MATERIALIZED",
                    "VIEW",
                    Ref("MaterializedViewReferenceSegment"),
                )
            ),
            Sequence("IS", OneOf(Ref("QuotedLiteralSegment"), "NULL")),
        )
    )

#@oracle_dialect.segment()
#class CreateMaterializedViewStatementSegment(BaseSegment):
#    """A `CREATE MATERIALIZED VIEW` statement.
#
#    As specified in https://www.postgresql.org/docs/14/sql-creatematerializedview.html
#    """
#
#    type = "create_materialized_view_statement"
#
#    match_grammar = StartsWith(Sequence("CREATE", "MATERIALIZED", "VIEW"))
#
#    parse_grammar = Sequence(
#        "CREATE",
#        "MATERIALIZED",
#        "VIEW",
#        Ref("IfNotExistsGrammar", optional=True),
#        Ref("TableReferenceSegment"),
#        Ref("BracketedColumnReferenceListGrammar", optional=True),
#        AnyNumberOf(
#            Sequence("USING", Ref("ParameterNameSegment"), optional=True),
#            Sequence("TABLESPACE", Ref("ParameterNameSegment"), optional=True),
#            Sequence(
#                "WITH",
#                Bracketed(
#                    Delimited(
#                        Sequence(
#                            Ref("ParameterNameSegment"),
#                            Sequence(
#                                Ref("EqualsSegment"),
#                                Ref("LiteralGrammar"),
#                                optional=True,
#                            ),
#                        ),
#                    )
#                ),
#            ),
#        ),
#        "AS",
#        OneOf(
#            OptionallyBracketed(Ref("SelectableGrammar")),
#            OptionallyBracketed(Sequence("TABLE", Ref("TableReferenceSegment"))),
#            Ref("ValuesClauseSegment"),
#            OptionallyBracketed(Sequence("EXECUTE", Ref("FunctionSegment"))),
#        ),
#        Ref("WithDataClauseSegment", optional=True),
#    )
#
#
#@postgres_dialect.segment()
#class AlterMaterializedViewStatementSegment(BaseSegment):
#    """A `ALTER MATERIALIZED VIEW` statement.
#
#    As specified in https://www.postgresql.org/docs/14/sql-altermaterializedview.html
#    """
#
#    type = "alter_materialized_view_statement"
#
#    match_grammar = StartsWith(Sequence("ALTER", "MATERIALIZED", "VIEW"))
#
#    parse_grammar = Sequence(
#        "ALTER",
#        "MATERIALIZED",
#        "VIEW",
#        OneOf(
#            Sequence(
#                Sequence("IF", "EXISTS", optional=True),
#                Ref("TableReferenceSegment"),
#                OneOf(
#                    Delimited(Ref("AlterMaterializedViewActionSegment")),
#                    Sequence(
#                        "RENAME",
#                        Sequence("COLUMN", optional=True),
#                        Ref("ColumnReferenceSegment"),
#                        "TO",
#                        Ref("ColumnReferenceSegment"),
#                    ),
#                    Sequence("RENAME", "TO", Ref("TableReferenceSegment")),
#                    Sequence("SET", "SCHEMA", Ref("SchemaReferenceSegment")),
#                ),
#            ),
#            Sequence(
#                Ref("TableReferenceSegment"),
#                Ref.keyword("NO", optional=True),
#                "DEPENDS",
#                "ON",
#                "EXTENSION",
#                Ref("ParameterNameSegment"),
#            ),
#            Sequence(
#                "ALL",
#                "IN",
#                "TABLESPACE",
#                Ref("TableReferenceSegment"),
#                Sequence(
#                    "OWNED",
#                    "BY",
#                    Delimited(Ref("ObjectReferenceSegment")),
#                    optional=True,
#                ),
#                "SET",
#                "TABLESPACE",
#                Ref("ParameterNameSegment"),
#                Sequence("NOWAIT", optional=True),
#            ),
#        ),
#    )
#
#
#@postgres_dialect.segment()
#class RefreshMaterializedViewStatementSegment(BaseSegment):
#    """A `REFRESH MATERIALIZED VIEW` statement.
#
#    As specified in https://www.postgresql.org/docs/14/sql-refreshmaterializedview.html
#    """
#
#    type = "refresh_materialized_view_statement"
#
#    match_grammar = StartsWith(Sequence("REFRESH", "MATERIALIZED", "VIEW"))
#
#    parse_grammar = Sequence(
#        "REFRESH",
#        "MATERIALIZED",
#        "VIEW",
#        Ref.keyword("CONCURRENTLY", optional=True),
#        Ref("TableReferenceSegment"),
#        Ref("WithDataClauseSegment", optional=True),
#    )
#
#
#@postgres_dialect.segment()
#class DropMaterializedViewStatementSegment(BaseSegment):
#    """A `DROP MATERIALIZED VIEW` statement.
#
#    As specified in https://www.postgresql.org/docs/14/sql-dropmaterializedview.html
#    """
#
#    type = "drop_materialized_view_statement"
#
#    match_grammar = StartsWith(Sequence("DROP", "MATERIALIZED", "VIEW"))
#
#    parse_grammar = Sequence(
#        "DROP",
#        "MATERIALIZED",
#        "VIEW",
#        Sequence("IF", "EXISTS", optional=True),
#        Delimited(Ref("TableReferenceSegment")),
#        OneOf("CASCADE", "RESTRICT", optional=True),
#    )
