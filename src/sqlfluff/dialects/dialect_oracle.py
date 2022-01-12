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

oracle_dialect.sets("unreserved_keywords").difference_update(["PROMPT", "COMMENT"])
oracle_dialect.sets("reserved_keywords").update(["ON"])

# Adding Oracle specific statements.
@oracle_dialect.segment(replace=True)
class StatementSegment(BaseSegment):
    """A generic segment, to any of its child subsegments."""

    type = "statement"

    parse_grammar = ansi_dialect.get_segment("StatementSegment").parse_grammar.copy(
        insert=[
            Ref("PromptStatementSegment"),
            Ref("CommentStatementSegment"),
        ],
    )

    match_grammar = ansi_dialect.get_segment("StatementSegment").match_grammar.copy()


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
