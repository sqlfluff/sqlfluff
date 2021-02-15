"""The MySQL dialect.

For now the only change is the parsing of comments.
https://dev.mysql.com/doc/refman/8.0/en/differences-from-ansi.html
"""

from sqlfluff.core.parser import NamedSegment, OneOf, Ref

from sqlfluff.core.dialects.dialect_ansi import ansi_dialect

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
    LiteralGrammar=OneOf(
        Ref("QuotedLiteralSegment"),
        Ref("DoubleQuotedLiteralSegment"),
        Ref("NumericLiteralSegment"),
        Ref("BooleanLiteralGrammar"),
        Ref("QualifiedNumericLiteralSegment"),
        Ref("NullKeywordSegment"),
    ),
)

mysql_dialect.add(
    DoubleQuotedLiteralSegment=NamedSegment.make(
        "double_quote", name="quoted_literal", type="literal", trim_chars=('"',)
    )
)
