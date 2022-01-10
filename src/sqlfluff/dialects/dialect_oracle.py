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
                #Sequence(
                #    "MATERIALIZED",
                #    "VIEW",
                #    Ref("MaterializedViewReferenceSegment"),
                #)
            ),
            "IS",
            Sequence("IS", OneOf(Ref("QuotedLiteralSegment"), "NULL")),
        )
    )
