"""The Db2 dialect.

https://www.ibm.com/docs/en/i/7.4?topic=overview-db2-i
"""

from sqlfluff.core.parser import (
    SegmentGenerator,
    RegexParser,
    CodeSegment,
    RegexLexer,
    CommentSegment,
)

from sqlfluff.dialects import dialect_ansi as ansi

from sqlfluff.core.dialects import load_raw_dialect

ansi_dialect = load_raw_dialect("ansi")

db2_dialect = ansi_dialect.copy_as("db2")


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
            "single_quote", r"(?s)('')+?(?!')|('.*?(?<!')(?:'')*'(?!'))", CodeSegment
        ),
        # In Db2, there is no escape character for double quote strings
        RegexLexer("double_quote", r'(?s)".+?"', CodeSegment),
        # In Db2, a field could have a # pound/hash sign
        RegexLexer("code", r"[0-9a-zA-Z_#]+", CodeSegment),
    ]
)
