"""The MySQL dialect.

For now the only change is the parsing of comments.
https://dev.mysql.com/doc/refman/8.0/en/differences-from-ansi.html
"""

from sqlfluff.core.parser import NamedSegment, Ref, AnyNumberOf, Sequence, OneOf

from sqlfluff.core.dialects.dialect_ansi import (
    ansi_dialect,
    CreateTableStatementSegment as ansi_CreateTableStatementSegment
)

mysql_dialect = ansi_dialect.copy_as("mysql")

mysql_dialect.patch_lexer_struct(
    [
        # name, type, pattern, kwargs
        (
            "inline_comment",
            "regex",
            r"(-- |#)[^\n]*",
            dict(is_comment=True, type="comment", trim_start=("-- ", "#")),
        )
    ]
)

mysql_dialect.replace(
    QuotedIdentifierSegment=NamedSegment.make(
        "back_quote", name="quoted_identifier", type="identifier", trim_chars=("`",)
    ),
    LiteralGrammar=ansi_dialect.get("LiteralGrammar").copy(
        insert=[
            Ref("DoubleQuotedLiteralSegment"),
        ]
    ),
)

mysql_dialect.add(
    DoubleQuotedLiteralSegment=NamedSegment.make(
        "double_quote", name="quoted_literal", type="literal", trim_chars=('"',)
    )
)


@mysql_dialect.segment(replace=True)
class CreateTableStatementSegment(ansi_CreateTableStatementSegment):
    # https://dev.mysql.com/doc/refman/8.0/en/create-table.html
    match_grammar = ansi_dialect.get("CreateTableStatementSegment").match_grammar.copy(
        insert=[
            AnyNumberOf(
                Sequence(
                    Ref.keyword("DEFAULT", optional=True),
                    Ref("ParameterNameSegment"),
                    Ref("EqualsSegment"),
                    OneOf(
                        Ref("LiteralGrammar"),
                        Ref("ParameterNameSegment")
                    ),
                ),
            ),
        ],
    )
