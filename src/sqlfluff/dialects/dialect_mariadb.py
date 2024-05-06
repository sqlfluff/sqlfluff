"""MariaDB Dialect

<url>
"""

from sqlfluff.core.dialects import load_raw_dialect

from sqlfluff.core.parser import (
    AnyNumberOf,
    AnySetOf,
    Anything,
    BaseSegment,
    BinaryOperatorSegment,
    Bracketed,
    CodeSegment,
    CommentSegment,
    Dedent,
    Delimited,
    IdentifierSegment,
    Indent,
    KeywordSegment,
    LiteralSegment,
    Matchable,
    OneOf,
    OptionallyBracketed,
    ParseMode,
    Ref,
    RegexLexer,
    RegexParser,
    SegmentGenerator,
    Sequence,
    StringLexer,
    StringParser,
    SymbolSegment,
    TypedParser,
)

from sqlfluff.dialects import dialect_ansi as ansi, dialect_mysql as mysql
from sqlfluff.dialects.dialect_mariadb_keywords import (
    mariadb_reserved_keywords,
    mariadb_unreserved_keywords,
)

# ansi_dialect = load_raw_dialect("ansi")
mysql_dialect = load_raw_dialect("mysql")
mariadb_dialect = mysql_dialect.copy_as("mariadb")
mariadb_dialect.add()


class CreateTableStatementSegment(mysql.CreateTableStatementSegment):
    """A CREATE TABLE segment.

    https://mariadb.com/kb/en/create-table/
    """

    match_grammar: Matchable = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        Ref("TemporaryTransientGrammar", optional=True),
        "TABLE",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        OneOf(
            # Columns and comment syntax:
            Sequence(
                Bracketed(
                    Delimited(
                        OneOf(
                            Ref("TableConstraintSegment"),
                            Ref("ColumnDefinitionSegment"),
                        ),
                    )
                ),
                Ref("CommentClauseSegment", optional=True),
                Sequence(
                    Ref.keyword("AS", optional=True),
                    OptionallyBracketed(Ref("SelectableGrammar")),
                    optional=True,
                ),
            ),
            # Create AS syntax:
            Sequence(
                Ref.keyword("AS", optional=True),
                OptionallyBracketed(Ref("SelectableGrammar")),
            ),
            # Create like syntax
            Sequence("LIKE", Ref("TableReferenceSegment")),
        ),
        Ref("TableEndClauseSegment", optional=True),
        # Table Options
        # https://mariadb.com/kb/en/create-table/#table-options
        AnyNumberOf(
            Sequence(
                Ref.keyword("DEFAULT", optional=True),
                OneOf(
                    Ref("ParameterNameSegment"),
                    Sequence("CHARACTER", "SET"),
                    Sequence("DATA", "DIRECTORY"),
                    Sequence("INDEX", "DIRECTORY"),
                    Sequence("WITH", "SYSTEM"),
                ),
                Ref("EqualsSegment", optional=True),
                OneOf(
                    Ref("LiteralGrammar"),
                    Ref("ParameterNameSegment"),
                    Ref("QuotedLiteralSegment"),
                    Ref("SingleQuotedIdentifierSegment"),
                    Ref("NumericLiteralSegment"),
                    # Union option
                    Bracketed(
                        Delimited(Ref("TableReferenceSegment")),
                    ),
                ),
            ),
            # Partition Options
            # https://mariadb.com/kb/en/create-table/#partitions
            Sequence(
                "PARTITION",
                "BY",
                Sequence(
                    OneOf(
                        Sequence(
                            Ref.keyword("LINEAR", optional=True),
                            OneOf(
                                Sequence("HASH", Ref("ExpressionSegment")),
                                Sequence(
                                    "KEY", Delimited(Ref("ColumnReferenceSegment"))
                                ),
                            ),
                        ),
                        Sequence(
                            OneOf("RANGE", "LIST"),
                            Ref("ExpressionSegment"),
                        ),
                        # FIXME: SYSTEM_TIME Sequence() inclusion causes failure
                    ),
                    Sequence("PARTITIONS", Ref("NumericLiteralSegment"), optional=True),
                    Sequence(
                        "SUBPARTITION",
                        "BY",
                        Sequence(
                            Ref.keyword("LINEAR", optional=True),
                            OneOf(
                                Sequence("HASH", Ref("ExpressionSegment")),
                                Sequence(
                                    "KEY", Delimited(Ref("ColumnReferenceSegment"))
                                ),
                            ),
                        ),
                        Sequence(
                            "SUBPARTITIONS", Ref("NumericLiteralSegment"), optional=True
                        ),
                        optional=True,
                    ),
                    # optional partition_definition(s)
                    AnyNumberOf(
                        Sequence(
                            Ref.keyword("PARTITION", optional=True),
                            Ref("LiteralGrammar"),
                            AnyNumberOf(
                                Sequence(
                                    "VALUES",
                                    OneOf(
                                        Sequence(
                                            "LESS",
                                            "THAN",
                                            OneOf(
                                                "MAXVALUE",
                                                Bracketed(Ref("ExpressionSegment")),
                                            ),
                                        ),
                                        Sequence(
                                            "IN",
                                            Bracketed(Ref("ObjectReferenceSegment")),
                                        ),
                                    ),
                                ),
                                Sequence(
                                    Ref.keyword("DEFAULT", optional=True),
                                    OneOf(
                                        Ref("ParameterNameSegment"),
                                        Sequence("CHARACTER", "SET"),
                                        Sequence("DATA", "DIRECTORY"),
                                        Sequence("INDEX", "DIRECTORY"),
                                        Sequence("WITH", "SYSTEM"),
                                    ),
                                    Ref("EqualsSegment", optional=True),
                                    OneOf(
                                        Ref("LiteralGrammar"),
                                        Ref("ParameterNameSegment"),
                                        Ref("QuotedLiteralSegment"),
                                        Ref("SingleQuotedIdentifierSegment"),
                                        Ref("NumericLiteralSegment"),
                                        # Union option
                                        Bracketed(
                                            Delimited(Ref("TableReferenceSegment")),
                                        ),
                                    ),
                                ),
                                # optional subpartition_definition(s)
                                Sequence(
                                    Ref.keyword("SUBPARTITION", optional=True),
                                    Ref("LiteralGrammar"),
                                    AnyNumberOf(
                                        Sequence(
                                            "VALUES",
                                            OneOf(
                                                Sequence(
                                                    "LESS",
                                                    "THAN",
                                                    OneOf(
                                                        "MAXVALUE",
                                                        Bracketed(
                                                            Ref("ExpressionSegment")
                                                        ),
                                                    ),
                                                ),
                                                Sequence(
                                                    "IN",
                                                    Bracketed(
                                                        Ref("ObjectReferenceSegment")
                                                    ),
                                                ),
                                            ),
                                        ),
                                        Sequence(
                                            Ref.keyword("DEFAULT", optional=True),
                                            OneOf(
                                                Ref("ParameterNameSegment"),
                                                Sequence("CHARACTER", "SET"),
                                                Sequence("DATA", "DIRECTORY"),
                                                Sequence("INDEX", "DIRECTORY"),
                                                Sequence("WITH", "SYSTEM"),
                                            ),
                                            Ref("EqualsSegment", optional=True),
                                            OneOf(
                                                Ref("LiteralGrammar"),
                                                Ref("ParameterNameSegment"),
                                                Ref("QuotedLiteralSegment"),
                                                Ref("SingleQuotedIdentifierSegment"),
                                                Ref("NumericLiteralSegment"),
                                                # Union option
                                                Bracketed(
                                                    Delimited(
                                                        Ref("TableReferenceSegment")
                                                    ),
                                                ),
                                            ),
                                        ),
                                    ),
                                ),
                            ),
                            optional=True,
                        ),
                    ),
                ),
                optional=True,
            ),
        ),
    )
