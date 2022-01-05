"""The Amazon Redshift dialect.

This is based on postgres dialect, since it was initially based off of Postgres 8.
We should monitor in future and see if it should be rebased off of ANSI
"""

from sqlfluff.core.parser import (
    OneOf,
    AnyNumberOf,
    Ref,
    Sequence,
    Bracketed,
    BaseSegment,
    Delimited,
    Nothing,
    OptionallyBracketed,
)

from sqlfluff.core.dialects import load_raw_dialect

from sqlfluff.dialects.dialect_redshift_keywords import (
    redshift_reserved_keywords,
    redshift_unreserved_keywords,
)


postgres_dialect = load_raw_dialect("postgres")
ansi_dialect = load_raw_dialect("ansi")

redshift_dialect = postgres_dialect.copy_as("redshift")

# Set Keywords
redshift_dialect.sets("unreserved_keywords").clear()
redshift_dialect.sets("unreserved_keywords").update(
    [n.strip().upper() for n in redshift_unreserved_keywords.split("\n")]
)

redshift_dialect.sets("reserved_keywords").clear()
redshift_dialect.sets("reserved_keywords").update(
    [n.strip().upper() for n in redshift_reserved_keywords.split("\n")]
)

redshift_dialect.sets("bare_functions").clear()
redshift_dialect.sets("bare_functions").update(["current_date", "sysdate"])

redshift_dialect.replace(WellKnownTextGeometrySegment=Nothing())
# TODO: for the time use the ANSI definition and not the updated one from Postgres as not all
#       data types are supported by Redshift
redshift_dialect.replace(DatatypeSegment=ansi_dialect.get_segment("DatatypeSegment"))


@redshift_dialect.segment(replace=True)
class DatePartFunctionNameSegment(BaseSegment):
    """DATEADD function name segment.

    Override to support DATEDIFF as well
    """

    type = "function_name"
    match_grammar = OneOf("DATEADD", "DATEDIFF")


@redshift_dialect.segment(replace=True)
class FunctionSegment(BaseSegment):
    """A scalar or aggregate function.

    Revert back to the ANSI definition to support ignore nulls
    """

    type = "function"
    match_grammar = ansi_dialect.get_segment("FunctionSegment").match_grammar.copy()


@redshift_dialect.segment()
class ColumnEncodingSegment(BaseSegment):
    """ColumnEncoding segment.

    Indicates column compression encoding.

    As specified by: https://docs.aws.amazon.com/redshift/latest/dg/c_Compression_encodings.html
    """

    type = "column_encoding_segment"

    match_grammar = OneOf(
        "RAW",
        "AZ64",
        "BYTEDICT",
        "DELTA",
        "DELTA32K",
        "LZO",
        "MOSTLY8",
        "MOSTLY16",
        "MOSTLY32",
        "RUNLENGTH",
        "TEXT255",
        "TEXT32K",
        "ZSTD",
    )


@redshift_dialect.segment()
class ColumnAttributeSegment(BaseSegment):
    """Redshift specific column attributes.

    As specified in https://docs.aws.amazon.com/redshift/latest/dg/r_CREATE_TABLE_NEW.html
    """

    type = "column_attribute_segment"

    match_grammar = AnyNumberOf(
        Sequence("DEFAULT", Ref("ExpressionSegment")),
        Sequence(
            "IDENTITY",
            Bracketed(Delimited(Ref("NumericLiteralSegment"))),
        ),
        Sequence(
            "GENERATED",
            "BY",
            "DEFAULT",
            "AS",
            "IDENTITY",
            Bracketed(Delimited(Ref("NumericLiteralSegment"))),
        ),
        Sequence("ENCODE", Ref("ColumnEncodingSegment")),
        "DISTKEY",
        "SORTKEY",
        Sequence("COLLATE", OneOf("CASE_SENSITIVE", "CASE_INSENSITIVE")),
    )


@redshift_dialect.segment(replace=True)
class ColumnConstraintSegment(BaseSegment):
    """Redshift specific column constraints.

    As specified in https://docs.aws.amazon.com/redshift/latest/dg/r_CREATE_TABLE_NEW.html
    """

    type = "column_constraint_segment"

    match_grammar = AnyNumberOf(
        OneOf(Sequence("NOT", "NULL"), "NULL"),
        OneOf("UNIQUE", Sequence("PRIMARY", "KEY")),
        Sequence(
            "REFERENCES",
            Ref("TableReferenceSegment"),
            Bracketed(Ref("ColumnReferenceSegment"), optional=True),
        ),
    )


@redshift_dialect.segment()
class TableAttributeSegment(BaseSegment):
    """Redshift specific table attributes.

    As specified in https://docs.aws.amazon.com/redshift/latest/dg/r_CREATE_TABLE_NEW.html
    """

    type = "table_constraint_segment"

    match_grammar = AnyNumberOf(
        Sequence("DISTSTYLE", OneOf("AUTO", "EVEN", "KEY", "ALL"), optional=True),
        Sequence("DISTKEY", Bracketed(Ref("ColumnReferenceSegment")), optional=True),
        OneOf(
            Sequence(
                OneOf("COMPOUND", "INTERLEAVED", optional=True),
                "SORTKEY",
                Bracketed(Delimited(Ref("ColumnReferenceSegment"))),
            ),
            Sequence("SORTKEY", "AUTO"),
            optional=True,
        ),
        Sequence("ENCODE", "AUTO", optional=True),
    )


@redshift_dialect.segment(replace=True)
class TableConstraintSegment(BaseSegment):
    """Redshift specific table constraints.

    As specified in https://docs.aws.amazon.com/redshift/latest/dg/r_CREATE_TABLE_NEW.html
    """

    type = "table_constraint_segment"

    match_grammar = AnyNumberOf(
        Sequence("UNIQUE", Bracketed(Delimited(Ref("ColumnReferenceSegment")))),
        Sequence(
            "PRIMARY",
            "KEY",
            Bracketed(Delimited(Ref("ColumnReferenceSegment"))),
        ),
        Sequence(
            "FOREIGN",
            "KEY",
            Bracketed(Delimited(Ref("ColumnReferenceSegment"))),
            "REFERENCES",
            Ref("TableReferenceSegment"),
            Sequence(Bracketed(Ref("ColumnReferenceSegment"))),
        ),
    )


@redshift_dialect.segment(replace=True)
class LikeOptionSegment(BaseSegment):
    """Like Option Segment.

    As specified in https://docs.aws.amazon.com/redshift/latest/dg/r_CREATE_TABLE_NEW.html
    """

    type = "like_option_segment"

    match_grammar = Sequence(OneOf("INCLUDING", "EXCLUDING"), "DEFAULTS")


@redshift_dialect.segment(replace=True)
class CreateTableStatementSegment(BaseSegment):
    """A `CREATE TABLE` statement.

    As specified in https://docs.aws.amazon.com/redshift/latest/dg/r_CREATE_TABLE_NEW.html
    """

    type = "create_table_statement"

    match_grammar = Sequence(
        "CREATE",
        Ref.keyword("LOCAL", optional=True),
        Ref("TemporaryGrammar", optional=True),
        "TABLE",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        Bracketed(
            OneOf(
                # Columns and comment syntax:
                Delimited(
                    Sequence(
                        Ref("ColumnReferenceSegment"),
                        Ref("DatatypeSegment"),
                        AnyNumberOf(Ref("ColumnAttributeSegment"), optional=True),
                        AnyNumberOf(Ref("ColumnConstraintSegment"), optional=True),
                    ),
                    Ref("TableConstraintSegment", optional=True),
                ),
                Sequence(
                    "LIKE",
                    Ref("TableReferenceSegment"),
                    AnyNumberOf(Ref("LikeOptionSegment"), optional=True),
                ),
            )
        ),
        Sequence("BACKUP", OneOf("YES", "NO", optional=True), optional=True),
        AnyNumberOf(Ref("TableAttributeSegment"), optional=True),
    )


@redshift_dialect.segment(replace=True)
class CreateTableAsStatementSegment(BaseSegment):
    """A `CREATE TABLE AS` statement.

    As specified in https://docs.aws.amazon.com/redshift/latest/dg/r_CREATE_TABLE_AS.html
    """

    type = "create_table_as_statement"
    match_grammar = Sequence(
        "CREATE",
        Sequence(
            Ref.keyword("LOCAL", optional=True),
            OneOf("TEMPORARY", "TEMP"),
            optional=True,
        ),
        "TABLE",
        Ref("ObjectReferenceSegment"),
        Bracketed(
            Delimited(
                Ref("ColumnReferenceSegment"),
            ),
            optional=True,
        ),
        Sequence("BACKUP", OneOf("YES", "NO"), optional=True),
        Ref("TableAttributeSegment", optional=True),
        "AS",
        Ref("SelectableGrammar"),
    )


@redshift_dialect.segment()
class CreateExternalTableStatementSegment(BaseSegment):
    """A `CREATE EXTERNAL TABLE` statement.

    As specified in https://docs.aws.amazon.com/redshift/latest/dg/r_CREATE_EXTERNAL_TABLE.html
    """

    type = "create_external_table_statement"

    match_grammar = Sequence(
        "CREATE",
        "EXTERNAL",
        "TABLE",
        Ref("TableReferenceSegment"),
        Bracketed(
            OneOf(
                # Columns and comment syntax:
                Delimited(
                    Sequence(
                        Ref("ColumnReferenceSegment"),
                        Ref("DatatypeSegment"),
                    ),
                ),
            )
        ),
        OneOf(Ref("PartitionedBySegment"), optional=True),
        "STORED",
        "AS",
        OneOf(
            "PARQUET",
            "RCFILE",
            "SEQUENCEFILE",
            "TEXTFILE",
            "ORC",
            "AVRO",
            Ref("QuotedLiteralSegment"),
        ),
        "LOCATION",
        Ref("QuotedLiteralSegment"),
    )


@redshift_dialect.segment()
class CreateExternalTableAsStatementSegment(BaseSegment):
    """A `CREATE EXTERNAL TABLE AS` statement.

    As specified in https://docs.aws.amazon.com/redshift/latest/dg/r_CREATE_EXTERNAL_TABLE.html
    """

    type = "create_external_table_statement"

    match_grammar = Sequence(
        "CREATE",
        "EXTERNAL",
        "TABLE",
        Ref("TableReferenceSegment"),
        OneOf(Ref("PartitionedBySegment"), optional=True),
        "STORED",
        "AS",
        OneOf(
            "PARQUET",
            "RCFILE",
            "SEQUENCEFILE",
            "TEXTFILE",
            "ORC",
            "AVRO",
            Ref("QuotedLiteralSegment"),
        ),
        "LOCATION",
        Ref("QuotedLiteralSegment"),
        "AS",
        OptionallyBracketed(Ref("SelectableGrammar")),
    )


@redshift_dialect.segment(replace=True)
class InsertStatementSegment(BaseSegment):
    """An`INSERT` statement.

    Redshift has two versions of insert statements:
        - https://docs.aws.amazon.com/redshift/latest/dg/r_INSERT_30.html
        - https://docs.aws.amazon.com/redshift/latest/dg/r_INSERT_external_table.html
    """

    # TODO: This logic can be streamlined. However, there are some odd parsing issues.
    # See https://github.com/sqlfluff/sqlfluff/pull/1896

    type = "insert_statement"
    match_grammar = Sequence(
        "INSERT",
        "INTO",
        Ref("TableReferenceSegment"),
        OneOf(
            OptionallyBracketed(Ref("SelectableGrammar")),
            Sequence("DEFAULT", "VALUES"),
            Sequence(
                Ref("BracketedColumnReferenceListGrammar", optional=True),
                OneOf(
                    Ref("ValuesClauseSegment"),
                    OptionallyBracketed(Ref("SelectableGrammar")),
                ),
            ),
        ),
    )


# Adding Redshift specific statements
@redshift_dialect.segment(replace=True)
class StatementSegment(BaseSegment):
    """A generic segment, to any of its child subsegments."""

    type = "statement"

    parse_grammar = redshift_dialect.get_segment("StatementSegment").parse_grammar.copy(
        insert=[
            Ref("AlterGroupSegment"),
            Ref("AlterUserSegment"),
            Ref("ColumnAttributeSegment"),
            Ref("ColumnEncodingSegment"),
            Ref("CreateExternalTableAsStatementSegment"),
            Ref("CreateExternalTableStatementSegment"),
            Ref("CreateGroupSegment"),
            Ref("CreateUserSegment"),
            Ref("PartitionedBySegment"),
            Ref("TableAttributeSegment"),
        ],
    )

    match_grammar = redshift_dialect.get_segment(
        "StatementSegment"
    ).match_grammar.copy()


@redshift_dialect.segment()
class PartitionedBySegment(BaseSegment):
    """Partitioned By Segment.

    As specified in https://docs.aws.amazon.com/redshift/latest/dg/r_CREATE_EXTERNAL_TABLE.html
    """

    type = "partitioned_by_segment"

    match_grammar = Sequence(
        Ref.keyword("PARTITIONED"),
        "BY",
        Bracketed(
            OneOf(
                Delimited(
                    Sequence(
                        Ref("ColumnReferenceSegment"),
                        Ref("DatatypeSegment"),
                    ),
                ),
            )
        ),
    )


@redshift_dialect.segment()
class CreateUserSegment(BaseSegment):
    """`CREATE USER` statement.

    https://docs.aws.amazon.com/redshift/latest/dg/r_CREATE_USER.html
    """

    type = "create_user"

    match_grammar = Sequence(
        "CREATE",
        "USER",
        Ref("ObjectReferenceSegment"),
        Ref.keyword("WITH", optional=True),
        "PASSWORD",
        OneOf(Ref("QuotedLiteralSegment"), "DISABLE"),
        AnyNumberOf(
            OneOf(
                "CREATEDB",
                "NOCREATEDB",
            ),
            OneOf(
                "CREATEUSER",
                "NOCREATEUSER",
            ),
            Sequence(
                "SYSLOG",
                "ACCESS",
                OneOf(
                    "RESTRICTED",
                    "UNRESTRICTED",
                ),
            ),
            Sequence("IN", "GROUP", Delimited(Ref("ObjectReferenceSegment"))),
            Sequence("VALID", "UNTIL", Ref("QuotedLiteralSegment")),
            Sequence(
                "CONNECTION",
                "LIMIT",
                OneOf(
                    Ref("NumericLiteralSegment"),
                    "UNLIMITED",
                ),
            ),
            Sequence(
                "SESSION",
                "TIMEOUT",
                Ref("NumericLiteralSegment"),
            ),
        ),
    )


@redshift_dialect.segment()
class CreateGroupSegment(BaseSegment):
    """`CREATE GROUP` statement.

    https://docs.aws.amazon.com/redshift/latest/dg/r_CREATE_GROUP.html
    """

    type = "create_group"

    match_grammar = Sequence(
        "CREATE",
        "GROUP",
        Ref("ObjectReferenceSegment"),
        Sequence(
            Ref.keyword("WITH", optional=True),
            "USER",
            Delimited(
                Ref("ObjectReferenceSegment"),
            ),
            optional=True,
        ),
    )


@redshift_dialect.segment()
class AlterUserSegment(BaseSegment):
    """`ALTER USER` statement.

    https://docs.aws.amazon.com/redshift/latest/dg/r_ALTER_USER.html
    """

    type = "alter_user"

    match_grammar = Sequence(
        "ALTER",
        "USER",
        Ref("ObjectReferenceSegment"),
        Ref.keyword("WITH", optional=True),
        AnyNumberOf(
            OneOf(
                "CREATEDB",
                "NOCREATEDB",
            ),
            OneOf(
                "CREATEUSER",
                "NOCREATEUSER",
            ),
            Sequence(
                "SYSLOG",
                "ACCESS",
                OneOf(
                    "RESTRICTED",
                    "UNRESTRICTED",
                ),
            ),
            Sequence(
                "PASSWORD",
                OneOf(
                    Ref("QuotedLiteralSegment"),
                    "DISABLE",
                ),
                Sequence("VALID", "UNTIL", Ref("QuotedLiteralSegment"), optional=True),
            ),
            Sequence(
                "RENAME",
                "TO",
                Ref("ObjectReferenceSegment"),
            ),
            Sequence(
                "CONNECTION",
                "LIMIT",
                OneOf(
                    Ref("NumericLiteralSegment"),
                    "UNLIMITED",
                ),
            ),
            OneOf(
                Sequence(
                    "SESSION",
                    "TIMEOUT",
                    Ref("NumericLiteralSegment"),
                ),
                Sequence(
                    "RESET",
                    "SESSION",
                    "TIMEOUT",
                ),
            ),
            OneOf(
                Sequence(
                    "SET",
                    Ref("ObjectReferenceSegment"),
                    OneOf(
                        "TO",
                        Ref("EqualsSegment"),
                    ),
                    OneOf(
                        "DEFAULT",
                        Ref("LiteralGrammar"),
                    ),
                ),
                Sequence(
                    "RESET",
                    Ref("ObjectReferenceSegment"),
                ),
            ),
            min_times=1,
        ),
    )


@redshift_dialect.segment()
class AlterGroupSegment(BaseSegment):
    """`ALTER GROUP` statement.

    https://docs.aws.amazon.com/redshift/latest/dg/r_ALTER_GROUP.html
    """

    type = "alter_group"

    match_grammar = Sequence(
        "ALTER",
        "GROUP",
        Ref("ObjectReferenceSegment"),
        OneOf(
            Sequence(
                OneOf("ADD", "DROP"),
                "USER",
                Delimited(
                    Ref("ObjectReferenceSegment"),
                ),
            ),
            Sequence(
                "RENAME",
                "TO",
                Ref("ObjectReferenceSegment"),
            ),
        ),
    )
