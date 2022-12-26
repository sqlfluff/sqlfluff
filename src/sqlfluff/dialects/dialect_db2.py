"""The Db2 dialect.

https://www.ibm.com/docs/en/i/7.4?topic=overview-db2-i
"""

from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.core.parser import (
    CodeSegment,
    CommentSegment,
    RegexLexer,
    RegexParser,
    SegmentGenerator,
)
from sqlfluff.dialects import dialect_ansi as ansi

from sqlfluff.dialects.dialect_db2_keywords import UNRESERVED_KEYWORDS

from sqlfluff.core.parser.grammar.base import Ref
from sqlfluff.core.parser.grammar.sequence import Sequence
from sqlfluff.core.parser.segments.base import BaseSegment

from sqlfluff.core.parser.grammar.base import Anything
from sqlfluff.core.parser.grammar.sequence import Bracketed

from sqlfluff.core.parser.grammar.anyof import OneOf

from sqlfluff.core.parser.grammar.anyof import AnyNumberOf

ansi_dialect = load_raw_dialect("ansi")

db2_dialect = ansi_dialect.copy_as("db2")
db2_dialect.sets("unreserved_keywords").update(UNRESERVED_KEYWORDS)


db2_dialect.replace(
    # Db2 allows # in field names, and doesn't use it as a comment
    NakedIdentifierSegment=SegmentGenerator(
        # Generate the anti template from the set of reserved keywords
        lambda dialect: RegexParser(
            r"[A-Z0-9_#]*[A-Z#][A-Z0-9_#]*",
            ansi.IdentifierSegment,
            type="naked_identifier",
            anti_template=r"^(" + r"|".join(dialect.sets("reserved_keywords")) + r")$",
        )
    ),
    PostFunctionGrammar=Sequence(
        Ref("WithinGroupClauseSegment", optional=True),
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
        Sequence(Ref("NumericLiteralSegment"), "DAYS"),
    ),
)


db2_dialect.patch_lexer_matchers(
    [
        # Patching comments to remove hash comments
        RegexLexer(
            "inline_comment",
            r"(--)[^\n]*",
            CommentSegment,
            segment_kwargs={"trim_start": ("--"), "type": "inline_comment"},
        ),
        # In Db2, the only escape character is ' for single quote strings
        RegexLexer(
            "single_quote",
            r"(?s)('')+?(?!')|('.*?(?<!')(?:'')*'(?!'))",
            CodeSegment,
            segment_kwargs={"type": "single_quote"},
        ),
        # In Db2, there is no escape character for double quote strings
        RegexLexer(
            "double_quote",
            r'(?s)".+?"',
            CodeSegment,
            segment_kwargs={"type": "double_quote"},
        ),
        # In Db2, a field could have a # pound/hash sign
        RegexLexer("code", r"[0-9a-zA-Z_#]+", CodeSegment),
    ]
)


class WithinGroupClauseSegment(BaseSegment):
    """An WITHIN GROUP clause for window functions."""

    type = "withingroup_clause"
    match_grammar = Sequence(
        "WITHIN",
        "GROUP",
        Bracketed(Anything(optional=True)),
    )

    parse_grammar = Sequence(
        "WITHIN",
        "GROUP",
        Bracketed(Ref("OrderByClauseSegment", optional=True)),
    )
