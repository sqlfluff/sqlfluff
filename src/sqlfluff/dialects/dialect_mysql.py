"""The MySQL dialect.

For now the only change is the parsing of comments.
https://dev.mysql.com/doc/refman/8.0/en/differences-from-ansi.html
"""

from sqlfluff.core.parser import (
    NamedSegment,
    Ref,
    AnyNumberOf,
    Sequence,
    OneOf,
    Bracketed,
    RegexMatcher,
)
from sqlfluff.core.dialects import load_raw_dialect

ansi_dialect = load_raw_dialect("ansi")
mysql_dialect = ansi_dialect.copy_as("mysql")

mysql_dialect.patch_lexer_matchers(
    [
        RegexMatcher(
            "inline_comment",
            r"(-- |#)[^\n]*",
            segment_kwargs={"is_comment": True, "type": "comment", "trim_start": ("-- ", "#")}
        )
    ]
)

# Reserve USE, FORCE & IGNORE
mysql_dialect.sets("unreserved_keywords").difference_update(["FORCE", "IGNORE", "USE"])
mysql_dialect.sets("reserved_keywords").update(["FORCE", "IGNORE", "USE"])

mysql_dialect.replace(
    QuotedIdentifierSegment=NamedSegment.make(
        "back_quote", name="quoted_identifier", type="identifier", trim_chars=("`",)
    ),
    LiteralGrammar=ansi_dialect.get_grammar("LiteralGrammar").copy(
        insert=[
            Ref("DoubleQuotedLiteralSegment"),
        ]
    ),
    PostTableExpressionGrammar=Sequence(
        OneOf("IGNORE", "FORCE", "USE"),
        OneOf("INDEX", "KEY"),
        Sequence("FOR", OneOf("JOIN"), optional=True),
        Bracketed(Ref("ObjectReferenceSegment")),
    ),
)

mysql_dialect.add(
    DoubleQuotedLiteralSegment=NamedSegment.make(
        "double_quote", name="quoted_literal", type="literal", trim_chars=('"',)
    )
)


@mysql_dialect.segment(replace=True)
class CreateTableStatementSegment(
    ansi_dialect.get_segment("CreateTableStatementSegment")  # type: ignore
):
    """Create table segment.

    https://dev.mysql.com/doc/refman/8.0/en/create-table.html
    """

    match_grammar = ansi_dialect.get_segment(
        "CreateTableStatementSegment"
    ).match_grammar.copy(
        insert=[
            AnyNumberOf(
                Sequence(
                    Ref.keyword("DEFAULT", optional=True),
                    Ref("ParameterNameSegment"),
                    Ref("EqualsSegment"),
                    OneOf(Ref("LiteralGrammar"), Ref("ParameterNameSegment")),
                ),
            ),
        ],
    )
