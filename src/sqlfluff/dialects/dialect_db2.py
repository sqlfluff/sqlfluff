"""The Db2 dialect.

https://www.ibm.com/docs/en/i/7.4?topic=overview-db2-i
"""

from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.core.parser import (
    AnyNumberOf,
    BaseSegment,
    Bracketed,
    CodeSegment,
    CommentSegment,
    IdentifierSegment,
    OneOf,
    ParseMode,
    Ref,
    RegexLexer,
    RegexParser,
    SegmentGenerator,
    Sequence,
    StringLexer,
    StringParser,
    SymbolSegment,
    WordSegment,
)
from sqlfluff.dialects import dialect_ansi as ansi
from sqlfluff.dialects.dialect_db2_keywords import UNRESERVED_KEYWORDS

ansi_dialect = load_raw_dialect("ansi")

db2_dialect = ansi_dialect.copy_as("db2")
db2_dialect.sets("unreserved_keywords").update(UNRESERVED_KEYWORDS)


db2_dialect.replace(
    # Db2 allows # in field names, and doesn't use it as a comment
    NakedIdentifierSegment=SegmentGenerator(
        # Generate the anti template from the set of reserved keywords
        lambda dialect: RegexParser(
            r"[A-Z0-9_#]*[A-Z#][A-Z0-9_#]*",
            IdentifierSegment,
            type="naked_identifier",
            anti_template=r"^(" + r"|".join(dialect.sets("reserved_keywords")) + r")$",
        )
    ),
    FunctionContentsExpressionGrammar=OneOf(
        Ref("ExpressionSegment"),
        Ref("NamedArgumentSegment"),
    ),
    PostFunctionGrammar=OneOf(
        Ref("OverClauseSegment"),
        Ref("WithinGroupClauseSegment"),
    ),
    Expression_C_Grammar=OneOf(
        Sequence("EXISTS", Bracketed(Ref("SelectableGrammar"))),
        # should be first priority, otherwise EXISTS() would be matched as a function
        Sequence(
            OneOf(
                Ref("Expression_D_Grammar"),
                Ref("CaseExpressionSegment"),
            ),
            AnyNumberOf(Ref("TimeZoneGrammar")),
        ),
        Ref("ShorthandCastSegment"),
        Sequence(Ref("NumericLiteralSegment"), OneOf("DAYS", "DAY")),
    ),
)

db2_dialect.insert_lexer_matchers(
    [
        StringLexer("right_arrow", "=>", CodeSegment),
    ],
    before="equals",
)

db2_dialect.patch_lexer_matchers(
    [
        # Patching comments to remove hash comments
        RegexLexer(
            "inline_comment",
            r"(--)[^\n]*",
            CommentSegment,
            segment_kwargs={"trim_start": ("--")},
        ),
        # In Db2, the only escape character is ' for single quote strings
        RegexLexer(
            "single_quote",
            r"(?s)('')+?(?!')|('.*?(?<!')(?:'')*'(?!'))",
            CodeSegment,
        ),
        # In Db2, there is no escape character for double quote strings
        RegexLexer(
            "double_quote",
            r'(?s)".+?"',
            CodeSegment,
        ),
        # In Db2, a field could have a # pound/hash sign
        RegexLexer("word", r"[0-9a-zA-Z_#]+", WordSegment),
    ]
)

db2_dialect.add(
    RightArrowSegment=StringParser("=>", SymbolSegment, type="right_arrow"),
)


class CallStoredProcedureSegment(BaseSegment):
    """This is a CALL statement used to execute a stored procedure.

    https://www.ibm.com/docs/en/db2/11.5?topic=statements-call
    """

    type = "call_segment"

    match_grammar = Sequence(
        "CALL",
        OneOf(
            Ref("FunctionSegment"),
            # Call without parenthesis
            Ref("FunctionNameSegment", reset_terminators=True),
        ),
    )


class NamedArgumentSegment(BaseSegment):
    """Named argument to a function.

    https://www.ibm.com/docs/en/db2/11.5?topic=statements-call
    """

    type = "named_argument"
    match_grammar = Sequence(
        Ref("NakedIdentifierSegment"),
        Ref("RightArrowSegment"),
        Ref("ExpressionSegment"),
    )


class WithinGroupClauseSegment(BaseSegment):
    """An WITHIN GROUP clause for window functions."""

    type = "withingroup_clause"

    match_grammar = Sequence(
        "WITHIN",
        "GROUP",
        Bracketed(
            Ref("OrderByClauseSegment", optional=True), parse_mode=ParseMode.GREEDY
        ),
    )


class StatementSegment(ansi.StatementSegment):
    """An element in the targets of a select statement."""

    match_grammar = ansi.StatementSegment.match_grammar.copy(
        insert=[
            Ref("CallStoredProcedureSegment"),
        ]
    )
