"""The Amazon Redshift dialect.

This is based on postgres dialect, since it was initially based off of Postgres 8.
We should monitor in future and see if it should be rebased off of ANSI
"""

from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.core.parser import (
    AnyNumberOf,
    AnySetOf,
    Anything,
    BaseSegment,
    Bracketed,
    Dedent,
    Delimited,
    IdentifierSegment,
    Indent,
    Matchable,
    Nothing,
    OneOf,
    OptionallyBracketed,
    ParseMode,
    Ref,
    RegexLexer,
    RegexParser,
    SegmentGenerator,
    Sequence,
    WordSegment,
)
from sqlfluff.dialects import dialect_ansi as ansi
from sqlfluff.dialects import dialect_postgres as postgres
from sqlfluff.dialects.dialect_redshift_keywords import (
    redshift_reserved_keywords,
    redshift_unreserved_keywords,
)

postgres_dialect = load_raw_dialect("postgres")
ansi_dialect = load_raw_dialect("ansi")
redshift_dialect = postgres_dialect.copy_as("redshift")

# Set Keywords
redshift_dialect.sets("unreserved_keywords").clear()
redshift_dialect.update_keywords_set_from_multiline_string(
    "unreserved_keywords", redshift_unreserved_keywords
)

redshift_dialect.sets("reserved_keywords").clear()
redshift_dialect.update_keywords_set_from_multiline_string(
    "reserved_keywords", redshift_reserved_keywords
)

redshift_dialect.sets("bare_functions").clear()
redshift_dialect.sets("bare_functions").update(
    [
        "current_date",
        "sysdate",
        "current_time",
        "current_timestamp",
        "user",
        "current_user",
        "current_aws_account",
        "current_namespace",
        "current_user_id",
    ]
)

redshift_dialect.sets("date_part_function_name").update(
    ["DATEADD", "DATEDIFF", "EXTRACT", "DATE_PART"]
)

# Add datetime units
# https://docs.aws.amazon.com/redshift/latest/dg/r_Dateparts_for_datetime_functions.html
redshift_dialect.sets("datetime_units").update(
    [
        # millennium
        "MILLENNIUM",
        "MILLENNIA",
        "MIL",
        "MILS",
        # century
        "CENTURY",
        "CENTURIES",
        "C",
        "CENT",
        "CENTS",
        # decade
        "DECADE",
        "DECADES",
        "DEC",
        "DECS",
        # epoch
        "EPOCH",
        # year
        "YEAR",
        "YEARS",
        "Y",
        "YR",
        "YRS",
        # quarter
        "QUARTER",
        "QUARTERS",
        "QTR",
        "QTRS",
        # month
        "MONTH",
        "MONTHS",
        "MON",
        "MONS",
        # week
        "WEEK",
        "WEEKS",
        "W",
        # day of week
        "DAYOFWEEK",
        "DOW",
        "DW",
        "WEEKDAY",
        # day of year
        "DAYOFYEAR",
        "DOY",
        "DY",
        "YEARDAY",
        # day
        "DAY",
        "DAYS",
        "D",
        # hour
        "HOUR",
        "HOURS",
        "H",
        "HR",
        "HRS",
        # minute
        "MINUTE",
        "MINUTES",
        "M",
        "MIN",
        "MINS",
        # second
        "SECOND",
        "SECONDS",
        "S",
        "SEC",
        "SECS",
        # millisec
        "MILLISECOND",
        "MILLISECONDS",
        "MS",
        "MSEC",
        "MSECS",
        "MSECOND",
        "MSECONDS",
        "MILLISEC",
        "MILLISECS",
        "MILLISECON",
        # microsec
        "MICROSECOND",
        "MICROSECONDS",
        "MICROSEC",
        "MICROSECS",
        "MICROSECOND",
        "USECOND",
        "USECONDS",
        "US",
        "USEC",
        "USECS",
        # timezone
        "TIMEZONE",
        "TIMEZONE_HOUR",
        "TIMEZONE_MINUTE",
    ]
)

redshift_dialect.replace(
    WellKnownTextGeometrySegment=Nothing(),
    JoinLikeClauseGrammar=Sequence(
        AnySetOf(
            Ref("FromPivotExpressionSegment"),
            Ref("FromUnpivotExpressionSegment"),
            min_times=1,
        ),
        Ref("AliasExpressionSegment", optional=True),
    ),
    NakedIdentifierSegment=SegmentGenerator(
        lambda dialect: RegexParser(
            # Optionally begins with # for temporary tables. Otherwise
            # must only contain digits, letters, underscore, and $ but
            # can’t be all digits.
            r"#?([A-Z_]+|[0-9]+[A-Z_$])[A-Z0-9_$]*",
            IdentifierSegment,
            type="naked_identifier",
            anti_template=r"^(" + r"|".join(dialect.sets("reserved_keywords")) + r")$",
        )
    ),
)

redshift_dialect.patch_lexer_matchers(
    [
        # add optional leading # to word for temporary tables
        RegexLexer(
            "word",
            r"#?[0-9a-zA-Z_]+[0-9a-zA-Z_$]*",
            WordSegment,
        ),
    ]
)


redshift_dialect.add(
    CompressionTypeGrammar=OneOf(
        "BZIP2",
        "GZIP",
        "LZOP",
        "ZSTD",
    ),
    ArgModeGrammar=OneOf(
        "IN",
        "OUT",
        "INOUT",
    ),
    ColumnEncodingGrammar=OneOf(
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
    ),
    QuotaGrammar=Sequence(
        "QUOTA",
        OneOf(
            Sequence(
                Ref("NumericLiteralSegment"),
                OneOf(
                    "MB",
                    "GB",
                    "TB",
                ),
            ),
            "UNLIMITED",
        ),
    ),
)


class FromUnpivotExpressionSegment(BaseSegment):
    """An UNPIVOT expression.

    See
    https://docs.aws.amazon.com/redshift/latest/dg/r_FROM_clause-pivot-unpivot-examples.html
    for details.
    """

    type = "from_unpivot_expression"
    match_grammar = Sequence(
        "UNPIVOT",
        Sequence(
            OneOf("INCLUDE", "EXCLUDE"),
            "NULLS",
            optional=True,
        ),
        Bracketed(
            Sequence(
                Ref("ColumnReferenceSegment"),
                "FOR",
                Ref("ColumnReferenceSegment"),
                "IN",
                Bracketed(
                    Delimited(
                        Sequence(
                            Ref("ColumnReferenceSegment"),
                            Ref("AliasExpressionSegment", optional=True),
                        )
                    ),
                ),
            ),
        ),
    )


class FromPivotExpressionSegment(BaseSegment):
    """A PIVOT expression.

    See
    https://docs.aws.amazon.com/redshift/latest/dg/r_FROM_clause-pivot-unpivot-examples.html
    for details.
    """

    type = "from_pivot_expression"
    match_grammar = Sequence(
        "PIVOT",
        Bracketed(
            Sequence(
                OptionallyBracketed(Ref("FunctionSegment")),
                Ref("AliasExpressionSegment", optional=True),
                "FOR",
                Ref("ColumnReferenceSegment"),
                "IN",
                Bracketed(
                    Delimited(
                        Sequence(
                            Ref("ExpressionSegment"),
                            Ref("AliasExpressionSegment", optional=True),
                        ),
                    ),
                ),
            ),
        ),
    )


class DateTimeTypeIdentifier(BaseSegment):
    """A Date Time type."""

    type = "datetime_type_identifier"
    match_grammar = OneOf(
        "DATE",
        "DATETIME",
        Sequence(
            OneOf("TIME", "TIMESTAMP"),
            Sequence(OneOf("WITH", "WITHOUT"), "TIME", "ZONE", optional=True),
        ),
        OneOf("TIMETZ", "TIMESTAMPTZ"),
        # INTERVAL types are not Datetime types under Redshift:
        # https://docs.aws.amazon.com/redshift/latest/dg/r_Datetime_types.html
    )


class BracketedArguments(ansi.BracketedArguments):
    """A series of bracketed arguments.

    e.g. the bracketed part of numeric(1, 3)
    """

    match_grammar = Bracketed(
        # The brackets might be empty for some cases...
        Delimited(
            OneOf(
                Ref("LiteralGrammar"),
                # In redshift, character types offer on optional MAX
                # keyword in their parameters.
                "MAX",
            ),
            optional=True,
        ),
    )


class DatatypeSegment(BaseSegment):
    """A data type segment.

    Indicates a data type.

    https://docs.aws.amazon.com/redshift/latest/dg/c_Supported_data_types.html
    """

    type = "data_type"
    match_grammar = OneOf(
        # numeric types
        "SMALLINT",
        "INT2",
        "INTEGER",
        "INT",
        "INT4",
        "BIGINT",
        "INT8",
        "REAL",
        "FLOAT4",
        Sequence("DOUBLE", "PRECISION"),
        "FLOAT8",
        "FLOAT",
        # numeric types [precision ["," scale])]
        Sequence(
            OneOf("DECIMAL", "NUMERIC"),
            Ref("BracketedArguments", optional=True),
        ),
        # character types
        OneOf(
            Sequence(
                OneOf(
                    "CHAR",
                    "CHARACTER",
                    "NCHAR",
                    "VARCHAR",
                    Sequence("CHARACTER", "VARYING"),
                    "NVARCHAR",
                ),
                Ref("BracketedArguments", optional=True),
            ),
            "BPCHAR",
            "TEXT",
        ),
        Ref("DateTimeTypeIdentifier"),
        # INTERVAL is a data type *only* for conversion operations
        "INTERVAL",
        # boolean types
        OneOf("BOOLEAN", "BOOL"),
        # hllsketch type
        "HLLSKETCH",
        # super type
        "SUPER",
        # spatial data
        "GEOMETRY",
        "GEOGRAPHY",
        # binary type
        Sequence(
            OneOf(
                "VARBYTE",
                "VARBINARY",
                Sequence("BINARY", "VARYING"),
            ),
            Ref("BracketedArguments", optional=True),
        ),
        "ANYELEMENT",
    )


class DataFormatSegment(BaseSegment):
    """DataFormat segment.

    Indicates data format available for COPY commands.

    https://docs.aws.amazon.com/redshift/latest/dg/c_Compression_encodings.html
    """

    type = "data_format_segment"

    match_grammar = Sequence(
        Sequence(
            "FORMAT",
            Ref.keyword("AS", optional=True),
            optional=True,
        ),
        OneOf(
            Sequence(
                "CSV",
                Sequence(
                    "QUOTE",
                    Ref.keyword("AS", optional=True),
                    Ref("QuotedLiteralSegment"),
                    optional=True,
                ),
            ),
            Sequence(
                "SHAPEFILE",
                Sequence(
                    "SIMPLIFY",
                    Ref.keyword("AUTO", optional=True),
                    Ref("NumericLiteralSegment", optional=True),
                    optional=True,
                ),
            ),
            Sequence(
                OneOf("AVRO", "JSON"),
                Sequence(
                    Ref.keyword("AS", optional=True),
                    Ref("QuotedLiteralSegment"),
                    optional=True,
                ),
            ),
            "PARQUET",
            "ORC",
            "RCFILE",
            "SEQUENCEFILE",
        ),
    )


class AuthorizationSegment(BaseSegment):
    """Authorization segment.

    Specifies authorization to access data in another AWS resource.

    https://docs.aws.amazon.com/redshift/latest/dg/copy-parameters-authorization.html
    """

    type = "authorization_segment"

    match_grammar = AnySetOf(
        OneOf(
            Sequence(
                "IAM_ROLE",
                OneOf(
                    "DEFAULT",
                    Ref("QuotedLiteralSegment"),
                ),
            ),
            Sequence(
                Ref.keyword("WITH", optional=True),
                "CREDENTIALS",
                Ref.keyword("AS", optional=True),
                Ref("QuotedLiteralSegment"),
            ),
            Sequence(
                "ACCESS_KEY_ID",
                Ref("QuotedLiteralSegment"),
                "SECRET_ACCESS_KEY",
                Ref("QuotedLiteralSegment"),
                Sequence(
                    "SESSION_TOKEN",
                    Ref("QuotedLiteralSegment"),
                    optional=True,
                ),
            ),
            optional=False,
        ),
        Sequence(
            "KMS_KEY_ID",
            Ref("QuotedLiteralSegment"),
            optional=True,
        ),
        Sequence(
            "MASTER_SYMMETRIC_KEY",
            Ref("QuotedLiteralSegment"),
            optional=True,
        ),
    )


class ColumnAttributeSegment(BaseSegment):
    """Redshift specific column attributes.

    As specified in
    https://docs.aws.amazon.com/redshift/latest/dg/r_CREATE_TABLE_NEW.html
    """

    type = "column_attribute_segment"

    match_grammar = AnySetOf(
        Sequence("DEFAULT", Ref("ExpressionSegment")),
        Sequence(
            "IDENTITY",
            Bracketed(Delimited(Ref("NumericLiteralSegment")), optional=True),
        ),
        Sequence(
            "GENERATED",
            "BY",
            "DEFAULT",
            "AS",
            "IDENTITY",
            Bracketed(Delimited(Ref("NumericLiteralSegment")), optional=True),
        ),
        Sequence("ENCODE", Ref("ColumnEncodingGrammar")),
        "DISTKEY",
        "SORTKEY",
        Sequence("COLLATE", OneOf("CASE_SENSITIVE", "CASE_INSENSITIVE")),
    )


class ColumnConstraintSegment(BaseSegment):
    """Redshift specific column constraints.

    As specified in
    https://docs.aws.amazon.com/redshift/latest/dg/r_CREATE_TABLE_NEW.html
    """

    type = "column_constraint_segment"

    match_grammar = AnySetOf(
        OneOf(Sequence("NOT", "NULL"), "NULL"),
        OneOf("UNIQUE", Ref("PrimaryKeyGrammar")),
        Sequence(
            "REFERENCES",
            Ref("TableReferenceSegment"),
            Bracketed(Ref("ColumnReferenceSegment"), optional=True),
        ),
    )


class AlterTableActionSegment(BaseSegment):
    """Alter Table Action Segment.

    https://docs.aws.amazon.com/redshift/latest/dg/r_ALTER_TABLE.html
    """

    type = "alter_table_action_segment"

    match_grammar = OneOf(
        Sequence(
            "ADD",
            Ref("TableConstraintSegment"),
            Sequence("NOT", "VALID", optional=True),
        ),
        Sequence("VALIDATE", "CONSTRAINT", Ref("ParameterNameSegment")),
        Sequence(
            "DROP",
            "CONSTRAINT",
            Ref("ParameterNameSegment"),
            Ref("DropBehaviorGrammar", optional=True),
        ),
        Sequence(
            "OWNER",
            "TO",
            OneOf(
                OneOf(Ref("ParameterNameSegment"), Ref("QuotedIdentifierSegment")),
            ),
        ),
        Sequence(
            "RENAME",
            "TO",
            OneOf(
                OneOf(Ref("ParameterNameSegment"), Ref("QuotedIdentifierSegment")),
            ),
        ),
        Sequence(
            "RENAME",
            "COLUMN",
            "TO",
            OneOf(
                Ref("ColumnReferenceSegment"),
            ),
        ),
        Sequence(
            "ALTER",
            Ref.keyword("COLUMN", optional=True),
            Ref("ColumnReferenceSegment"),
            OneOf(
                Sequence(
                    "TYPE",
                    Ref("DatatypeSegment"),
                ),
                Sequence(
                    "ENCODE",
                    Delimited(
                        Ref("ColumnEncodingGrammar"),
                    ),
                ),
            ),
        ),
        Sequence(
            "ALTER",
            "DISTKEY",
            Ref("ColumnReferenceSegment"),
        ),
        Sequence(
            "ALTER",
            "DISTSTYLE",
            OneOf(
                "ALL",
                "EVEN",
                Sequence("KEY", "DISTKEY", Ref("ColumnReferenceSegment")),
                "AUTO",
            ),
        ),
        Sequence(
            "ALTER",
            Ref.keyword("COMPOUND", optional=True),
            "SORTKEY",
            Bracketed(
                Delimited(
                    Ref("ColumnReferenceSegment"),
                ),
            ),
        ),
        Sequence(
            "ALTER",
            "SORTKEY",
            OneOf(
                "AUTO",
                "NONE",
            ),
        ),
        Sequence(
            "ALTER",
            "ENCODE",
            "AUTO",
        ),
        Sequence(
            "ADD",
            Ref.keyword("COLUMN", optional=True),
            Ref("ColumnReferenceSegment"),
            Ref("DatatypeSegment"),
            Sequence("DEFAULT", Ref("ExpressionSegment"), optional=True),
            Sequence("COLLATE", Ref("CollationReferenceSegment"), optional=True),
            AnyNumberOf(Ref("ColumnConstraintSegment")),
        ),
        Sequence(
            "DROP",
            Ref.keyword("COLUMN", optional=True),
            Ref("ColumnReferenceSegment"),
            Ref("DropBehaviorGrammar", optional=True),
        ),
        Sequence(
            "APPEND",
            "FROM",
            Ref("TableReferenceSegment"),
            Ref.keyword("IGNOREEXTRA", optional=True),
            Ref.keyword("FILLTARGET", optional=True),
        ),
    )


class TableAttributeSegment(BaseSegment):
    """Redshift specific table attributes.

    As specified in
    https://docs.aws.amazon.com/redshift/latest/dg/r_CREATE_TABLE_NEW.html
    """

    type = "table_constraint"

    match_grammar = AnySetOf(
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


class TableConstraintSegment(BaseSegment):
    """Redshift specific table constraints.

    As specified in
    https://docs.aws.amazon.com/redshift/latest/dg/r_CREATE_TABLE_NEW.html
    """

    type = "table_constraint"

    match_grammar = Sequence(
        Sequence(  # [ CONSTRAINT <Constraint name> ]
            "CONSTRAINT", Ref("ObjectReferenceSegment"), optional=True
        ),
        OneOf(
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
                Bracketed(Delimited(Ref("ColumnReferenceSegment"))),
            ),
        ),
    )


class LikeOptionSegment(BaseSegment):
    """Like Option Segment.

    As specified in
    https://docs.aws.amazon.com/redshift/latest/dg/r_CREATE_TABLE_NEW.html
    """

    type = "like_option_segment"

    match_grammar = Sequence(OneOf("INCLUDING", "EXCLUDING"), "DEFAULTS")


class CreateTableStatementSegment(BaseSegment):
    """A `CREATE TABLE` statement.

    As specified in
    https://docs.aws.amazon.com/redshift/latest/dg/r_CREATE_TABLE_NEW.html
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
            Delimited(
                # Columns and comment syntax:
                AnyNumberOf(
                    Sequence(
                        Ref("ColumnReferenceSegment"),
                        Ref("DatatypeSegment"),
                        AnyNumberOf(
                            Ref("ColumnAttributeSegment"),
                            Ref("ColumnConstraintSegment"),
                            optional=True,
                        ),
                    ),
                    Ref("TableConstraintSegment"),
                    Sequence(
                        "LIKE",
                        Ref("TableReferenceSegment"),
                        AnyNumberOf(Ref("LikeOptionSegment"), optional=True),
                    ),
                ),
            )
        ),
        Sequence("BACKUP", OneOf("YES", "NO", optional=True), optional=True),
        AnyNumberOf(Ref("TableAttributeSegment"), optional=True),
    )


class CreateTableAsStatementSegment(BaseSegment):
    """A `CREATE TABLE AS` statement.

    As specified in
    https://docs.aws.amazon.com/redshift/latest/dg/r_CREATE_TABLE_AS.html
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
        OptionallyBracketed(Ref("SelectableGrammar")),
    )


class CreateModelStatementSegment(BaseSegment):
    """A `CREATE MODEL` statement.

    https://docs.aws.amazon.com/redshift/latest/dg/r_CREATE_MODEL.html
    NB: order of keywords matter
    """

    type = "create_model_statement"
    match_grammar = Sequence(
        "CREATE",
        "MODEL",
        Ref("ObjectReferenceSegment"),
        Sequence(
            "FROM",
            OneOf(
                Ref("QuotedLiteralSegment"),
                Bracketed(Ref("SelectableGrammar")),
                Ref("ObjectReferenceSegment"),
            ),
            optional=True,
        ),
        Sequence(
            "TARGET",
            Ref("ColumnReferenceSegment"),
            optional=True,
        ),
        Sequence(
            "FUNCTION",
            Ref("ObjectReferenceSegment"),
            Bracketed(
                Delimited(Ref("DatatypeSegment")),
                optional=True,
            ),
        ),
        Sequence(
            "RETURNS",
            Ref("DatatypeSegment"),
            optional=True,
        ),
        Sequence(
            "SAGEMAKER",
            Ref("QuotedLiteralSegment"),
            optional=True,
        ),
        Sequence(
            "IAM_ROLE",
            OneOf(
                "DEFAULT",
                Ref("QuotedLiteralSegment"),
            ),
        ),
        Sequence(
            "AUTO",
            OneOf(
                "ON",
                "OFF",
            ),
            optional=True,
        ),
        Sequence(
            "MODEL_TYPE",
            OneOf(
                "XGBOOST",
                "MLP",
                "KMEANS",
            ),
            optional=True,
        ),
        Sequence(
            "PROBLEM_TYPE",
            OneOf(
                "REGRESSION",
                "BINARY_CLASSIFICATION",
                "MULTICLASS_CLASSIFICATION",
            ),
            optional=True,
        ),
        Sequence(
            "OBJECTIVE",
            Ref("QuotedLiteralSegment"),
            optional=True,
        ),
        Sequence(
            "PREPROCESSORS",
            Ref("QuotedLiteralSegment"),
            optional=True,
        ),
        Sequence(
            "HYPERPARAMETERS",
            "DEFAULT",
            Sequence(
                "EXCEPT",
                Bracketed(
                    Delimited(
                        Anything(),
                    ),
                ),
                optional=True,
            ),
            optional=True,
        ),
        Sequence(
            "SETTINGS",
            Bracketed(
                Sequence(
                    "S3_BUCKET",
                    Ref("QuotedLiteralSegment"),
                    Sequence(
                        "KMS_KEY_ID",
                        Ref("QuotedLiteralSegment"),
                        optional=True,
                    ),
                    Sequence(
                        "S3_GARBAGE_COLLECT",
                        OneOf(
                            "ON",
                            "OFF",
                        ),
                        optional=True,
                    ),
                    Sequence(
                        "MAX_CELLS",
                        Ref("NumericLiteralSegment"),
                        optional=True,
                    ),
                    Sequence(
                        "MAX_RUNTIME",
                        Ref("NumericLiteralSegment"),
                        optional=True,
                    ),
                ),
            ),
            optional=True,
        ),
    )


class ShowModelStatementSegment(BaseSegment):
    """A `SHOW MODEL` statement.

    As specified in: https://docs.aws.amazon.com/redshift/latest/dg/r_SHOW_MODEL.html
    """

    type = "show_model_statement"

    match_grammar = Sequence(
        "SHOW",
        "MODEL",
        OneOf(
            "ALL",
            Ref("ObjectReferenceSegment"),
        ),
    )


class CreateExternalTableStatementSegment(BaseSegment):
    """A `CREATE EXTERNAL TABLE` statement.

    https://docs.aws.amazon.com/redshift/latest/dg/r_CREATE_EXTERNAL_TABLE.html
    """

    type = "create_external_table_statement"

    match_grammar = Sequence(
        "CREATE",
        "EXTERNAL",
        "TABLE",
        Ref("TableReferenceSegment"),
        Bracketed(
            # Columns and comment syntax:
            Delimited(
                Sequence(
                    Ref("ColumnReferenceSegment"),
                    Ref("DatatypeSegment"),
                ),
            ),
        ),
        Ref("PartitionedBySegment", optional=True),
        Sequence(
            "ROW",
            "FORMAT",
            OneOf(
                Sequence(
                    "DELIMITED",
                    Ref("RowFormatDelimitedSegment"),
                ),
                Sequence(
                    "SERDE",
                    Ref("QuotedLiteralSegment"),
                    Sequence(
                        "WITH",
                        "SERDEPROPERTIES",
                        Bracketed(
                            Delimited(
                                Sequence(
                                    Ref("QuotedLiteralSegment"),
                                    Ref("EqualsSegment"),
                                    Ref("QuotedLiteralSegment"),
                                ),
                            ),
                        ),
                        optional=True,
                    ),
                ),
            ),
            optional=True,
        ),
        "STORED",
        "AS",
        OneOf(
            "PARQUET",
            "RCFILE",
            "SEQUENCEFILE",
            "TEXTFILE",
            "ORC",
            "AVRO",
            Sequence(
                "INPUTFORMAT",
                Ref("QuotedLiteralSegment"),
                "OUTPUTFORMAT",
                Ref("QuotedLiteralSegment"),
            ),
        ),
        "LOCATION",
        Ref("QuotedLiteralSegment"),
        Sequence(
            "TABLE",
            "PROPERTIES",
            Bracketed(
                Delimited(
                    Sequence(
                        Ref("QuotedLiteralSegment"),
                        Ref("EqualsSegment"),
                        Ref("QuotedLiteralSegment"),
                    ),
                ),
            ),
            optional=True,
        ),
    )


class CreateExternalTableAsStatementSegment(BaseSegment):
    """A `CREATE EXTERNAL TABLE AS` statement.

    https://docs.aws.amazon.com/redshift/latest/dg/r_CREATE_EXTERNAL_TABLE.html
    """

    type = "create_external_table_statement"

    match_grammar = Sequence(
        "CREATE",
        "EXTERNAL",
        "TABLE",
        Ref("TableReferenceSegment"),
        Ref("PartitionedBySegment", optional=True),
        Sequence(
            "ROW",
            "FORMAT",
            "DELIMITED",
            Ref("RowFormatDelimitedSegment"),
            optional=True,
        ),
        "STORED",
        "AS",
        OneOf(
            "PARQUET",
            "TEXTFILE",
        ),
        "LOCATION",
        Ref("QuotedLiteralSegment"),
        Sequence(
            "TABLE",
            "PROPERTIES",
            Bracketed(
                Delimited(
                    Sequence(
                        Ref("QuotedLiteralSegment"),
                        Ref("EqualsSegment"),
                        Ref("QuotedLiteralSegment"),
                    ),
                ),
            ),
            optional=True,
        ),
        "AS",
        OptionallyBracketed(Ref("SelectableGrammar")),
    )


class CreateExternalSchemaStatementSegment(BaseSegment):
    """A `CREATE EXTERNAL SCHEMA` statement.

    https://docs.aws.amazon.com/redshift/latest/dg/r_CREATE_EXTERNAL_SCHEMA.html
    """

    type = "create_external_schema_statement"

    match_grammar = Sequence(
        "CREATE",
        "EXTERNAL",
        "SCHEMA",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("SchemaReferenceSegment"),
        "FROM",
        OneOf(
            Sequence("DATA", "CATALOG"),
            Sequence("HIVE", "METASTORE"),
            "POSTGRES",
            "MYSQL",
            "KINESIS",
            "REDSHIFT",
        ),
        AnySetOf(
            Sequence("DATABASE", Ref("QuotedLiteralSegment")),
            Sequence("REGION", Ref("QuotedLiteralSegment")),
            Sequence("SCHEMA", Ref("QuotedLiteralSegment")),
            Sequence(
                "URI",
                Ref("QuotedLiteralSegment"),
                Sequence("PORT", Ref("NumericLiteralSegment"), optional=True),
            ),
            Sequence(
                "IAM_ROLE",
                OneOf(
                    "DEFAULT",
                    Ref("QuotedLiteralSegment"),
                ),
            ),
            Sequence("SECRET_ARN", Ref("QuotedLiteralSegment")),
            Sequence("CATALOG_ROLE", Ref("QuotedLiteralSegment")),
            Sequence("CREATE", "EXTERNAL", "DATABASE", "IF", "NOT", "EXISTS"),
            optional=True,
        ),
    )


class CreateLibraryStatementSegment(BaseSegment):
    """A `CREATE LIBRARY` statement.

    https://docs.aws.amazon.com/redshift/latest/dg/r_CREATE_LIBRARY.html
    """

    type = "create_library_statement"

    match_grammar = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        "LIBRARY",
        Ref("ObjectReferenceSegment"),
        "LANGUAGE",
        "PLPYTHONU",
        "FROM",
        Ref("QuotedLiteralSegment"),
        AnySetOf(
            Ref("AuthorizationSegment", optional=False),
            Sequence(
                "REGION",
                Ref.keyword("AS", optional=True),
                Ref("QuotedLiteralSegment"),
                optional=True,
            ),
        ),
    )


class UnloadStatementSegment(BaseSegment):
    """A `UNLOAD` statement.

    https://docs.aws.amazon.com/redshift/latest/dg/r_UNLOAD.html
    """

    type = "unload_statement"

    match_grammar = Sequence(
        "UNLOAD",
        Bracketed(Ref("QuotedLiteralSegment")),
        "TO",
        Ref("QuotedLiteralSegment"),
        AnySetOf(
            Ref("AuthorizationSegment", optional=False),
            Sequence(
                "REGION",
                Ref.keyword("AS", optional=True),
                Ref("QuotedLiteralSegment"),
                optional=True,
            ),
            Ref("CompressionTypeGrammar", optional=True),
            Sequence(
                Sequence(
                    "FORMAT",
                    Ref.keyword("AS", optional=True),
                    optional=True,
                ),
                OneOf(
                    "CSV",
                    "JSON",
                    "PARQUET",
                ),
                optional=True,
            ),
            Sequence(
                "PARTITION",
                "BY",
                Ref("BracketedColumnReferenceListGrammar"),
                Ref.keyword("INCLUDE", optional=True),
            ),
            Sequence(
                "PARALLEL",
                OneOf(
                    "PRESET",
                    "ON",
                    "OFF",
                    "TRUE",
                    "FALSE",
                    optional=True,
                ),
                optional=True,
            ),
            OneOf(
                Sequence(
                    "DELIMITER",
                    Ref.keyword("AS", optional=True),
                    Ref("QuotedLiteralSegment"),
                ),
                Sequence(
                    "FIXEDWIDTH",
                    Ref.keyword("AS", optional=True),
                    Ref("QuotedLiteralSegment"),
                ),
                optional=True,
            ),
            Sequence(
                "MANIFEST",
                Ref.keyword("VERBOSE", optional=True),
                optional=True,
            ),
            Sequence(
                "NULL",
                "AS",
                Ref("QuotedLiteralSegment"),
                optional=True,
            ),
            Sequence(
                "NULL",
                "AS",
                Ref("QuotedLiteralSegment"),
                optional=True,
            ),
            AnySetOf(
                OneOf(
                    "MAXFILESIZE",
                    "ROWGROUPSIZE",
                ),
                Ref.keyword("AS", optional=True),
                Ref("NumericLiteralSegment"),
                OneOf(
                    "MB",
                    "GB",
                ),
                optional=True,
            ),
            Sequence(
                "ENCRYPTED",
                Ref.keyword("AUTO", optional=True),
                optional=True,
            ),
            Ref.keyword("ALLOWOVERWRITE", optional=True),
            Ref.keyword("CLEANPATH", optional=True),
            Ref.keyword("ESCAPE", optional=True),
            Ref.keyword("ADDQUOTES", optional=True),
            Ref.keyword("HEADER", optional=True),
        ),
    )


class CopyStatementSegment(postgres.CopyStatementSegment):
    """A `COPY` statement.

    :
        - https://docs.aws.amazon.com/redshift/latest/dg/r_COPY.html
        - https://docs.aws.amazon.com/redshift/latest/dg/r_COPY-parameters.html
    """

    type = "copy_statement"

    match_grammar = Sequence(
        "COPY",
        Ref("TableReferenceSegment"),
        Ref("BracketedColumnReferenceListGrammar", optional=True),
        "FROM",
        Ref("QuotedLiteralSegment"),
        AnySetOf(
            Ref("AuthorizationSegment", optional=False),
            Sequence(
                "REGION",
                Ref.keyword("AS", optional=True),
                Ref("QuotedLiteralSegment"),
                optional=True,
            ),
            Ref("CompressionTypeGrammar", optional=True),
            Ref("DataFormatSegment", optional=True),
            OneOf(
                Sequence(
                    "DELIMITER",
                    Ref.keyword("AS", optional=True),
                    Ref("QuotedLiteralSegment"),
                ),
                Sequence(
                    "FIXEDWIDTH",
                    Ref.keyword("AS", optional=True),
                    Ref("QuotedLiteralSegment"),
                ),
                optional=True,
            ),
            Sequence(
                "ENCRYPTED",
                Ref.keyword("AUTO", optional=True),
                optional=True,
            ),
            Ref.keyword("MANIFEST", optional=True),
            Sequence(
                "COMPROWS",
                Ref("NumericLiteralSegment"),
                optional=True,
            ),
            Sequence(
                "MAXERROR",
                Ref.keyword("AS", optional=True),
                Ref("NumericLiteralSegment"),
                optional=True,
            ),
            Sequence(
                "COMPUPDATE",
                OneOf(
                    "PRESET",
                    "ON",
                    "OFF",
                    "TRUE",
                    "FALSE",
                    optional=True,
                ),
                optional=True,
            ),
            Sequence(
                "STATUPDATE",
                OneOf(
                    "ON",
                    "OFF",
                    "TRUE",
                    "FALSE",
                    optional=True,
                ),
                optional=True,
            ),
            Ref.keyword("NOLOAD", optional=True),
            Ref.keyword("ACCEPTANYDATE", optional=True),
            Sequence(
                "ACCEPTINVCHARS",
                Ref.keyword("AS", optional=True),
                Ref("QuotedLiteralSegment", optional=True),
                optional=True,
            ),
            Ref.keyword("BLANKSASNULL", optional=True),
            Sequence(
                "DATEFORMAT",
                Ref.keyword("AS", optional=True),
                OneOf(
                    "AUTO",
                    Ref("QuotedLiteralSegment"),
                ),
                optional=True,
            ),
            Ref.keyword("EMPTYASNULL", optional=True),
            Sequence(
                "ENCODING",
                Ref.keyword("AS", optional=True),
                OneOf(
                    "UTF8",
                    "UTF16",
                    "UTF16BE",
                    "UTF16LE",
                ),
                optional=True,
            ),
            Ref.keyword("ESCAPE", optional=True),
            Ref.keyword("EXPLICIT_IDS", optional=True),
            Ref.keyword("FILLRECORD", optional=True),
            Ref.keyword("IGNOREBLANKLINES", optional=True),
            Sequence(
                "IGNOREHEADER",
                Ref.keyword("AS", optional=True),
                Ref("LiteralGrammar"),
                optional=True,
            ),
            Sequence(
                "NULL",
                "AS",
                Ref("QuotedLiteralSegment"),
                optional=True,
            ),
            Sequence(
                "READRATIO",
                Ref("NumericLiteralSegment"),
                optional=True,
            ),
            Ref.keyword("REMOVEQUOTES", optional=True),
            Ref.keyword("ROUNDEC", optional=True),
            Sequence(
                "TIMEFORMAT",
                Ref.keyword("AS", optional=True),
                OneOf(
                    "AUTO",
                    "EPOCHSECS",
                    "EPOCHMILLISECS",
                    Ref("QuotedLiteralSegment"),
                ),
                optional=True,
            ),
            Ref.keyword("TRIMBLANKS", optional=True),
            Ref.keyword("TRUNCATECOLUMNS", optional=True),
        ),
    )


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


class CreateSchemaStatementSegment(BaseSegment):
    """A `CREATE SCHEMA` statement.

    https://docs.aws.amazon.com/redshift/latest/dg/r_CREATE_SCHEMA.html
    TODO: support optional SCHEMA_ELEMENT (should mostly be provided by ansi)
    """

    type = "create_schema_statement"
    match_grammar = Sequence(
        "CREATE",
        "SCHEMA",
        OneOf(
            Sequence(
                Ref("IfNotExistsGrammar", optional=True),
                Ref("SchemaReferenceSegment"),
                Sequence(
                    "AUTHORIZATION",
                    Ref("RoleReferenceSegment"),
                    optional=True,
                ),
            ),
            Sequence(
                "AUTHORIZATION",
                Ref("RoleReferenceSegment"),
            ),
        ),
        Ref("QuotaGrammar", optional=True),
    )


class ProcedureParameterListSegment(BaseSegment):
    """The parameters for a procedure.

    https://docs.aws.amazon.com/redshift/latest/dg/r_CREATE_PROCEDURE.html
    """

    type = "procedure_parameter_list"
    # Odd syntax, but prevents eager parameters being confused for data types
    _param_type = OneOf("REFCURSOR", Ref("DatatypeSegment"))
    match_grammar = Bracketed(
        Delimited(
            Sequence(
                AnyNumberOf(
                    Ref(
                        "ParameterNameSegment",
                        exclude=OneOf(_param_type, Ref("ArgModeGrammar")),
                        optional=True,
                    ),
                    Ref("ArgModeGrammar", optional=True),
                    max_times_per_element=1,
                ),
                _param_type,
            ),
            optional=True,
        ),
    )


class CreateProcedureStatementSegment(BaseSegment):
    """A `CREATE PROCEDURE` statement.

    https://www.postgresql.org/docs/14/sql-createprocedure.html

    TODO: Just a basic statement for now, without full syntax.
    based on CreateFunctionStatementSegment without a return type.
    """

    type = "create_procedure_statement"

    match_grammar = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        "PROCEDURE",
        Ref("FunctionNameSegment"),
        Ref("ProcedureParameterListSegment"),
        Ref("FunctionDefinitionGrammar"),
    )


class AlterProcedureStatementSegment(BaseSegment):
    """An `ALTER PROCEDURE` statement.

    https://docs.aws.amazon.com/redshift/latest/dg/r_ALTER_PROCEDURE.html
    """

    type = "alter_procedure_statement"

    match_grammar = Sequence(
        "ALTER",
        "PROCEDURE",
        Ref("FunctionNameSegment"),
        Ref("ProcedureParameterListSegment", optional=True),
        OneOf(
            Sequence("RENAME", "TO", Ref("FunctionNameSegment")),
            Sequence(
                "OWNER",
                "TO",
                OneOf(
                    OneOf(Ref("ParameterNameSegment"), Ref("QuotedIdentifierSegment")),
                    "CURRENT_USER",
                    "SESSION_USER",
                ),
            ),
        ),
    )


class DropProcedureStatementSegment(BaseSegment):
    """An `DROP PROCEDURE` statement.

    https://docs.aws.amazon.com/redshift/latest/dg/r_DROP_PROCEDURE.html
    """

    type = "drop_procedure_statement"

    match_grammar = Sequence(
        "DROP",
        "PROCEDURE",
        Ref("IfExistsGrammar", optional=True),
        Delimited(
            Sequence(
                Ref("FunctionNameSegment"),
                Ref("ProcedureParameterListSegment", optional=True),
            ),
        ),
    )


class AlterDefaultPrivilegesSchemaObjectsSegment(
    postgres.AlterDefaultPrivilegesSchemaObjectsSegment
):
    """`ALTER DEFAULT PRIVILEGES` schema object types.

    https://docs.aws.amazon.com/redshift/latest/dg/r_ALTER_DEFAULT_PRIVILEGES.html
    """

    match_grammar = (
        postgres.AlterDefaultPrivilegesSchemaObjectsSegment.match_grammar.copy(
            insert=[Sequence("PROCEDURES")]
        )
    )


class DeclareStatementSegment(BaseSegment):
    """A `DECLARE` statement.

    As specified in
    https://docs.aws.amazon.com/redshift/latest/dg/declare.html
    """

    type = "declare_statement"
    match_grammar = Sequence(
        "DECLARE",
        Ref("ObjectReferenceSegment"),
        "CURSOR",
        "FOR",
        Ref("SelectableGrammar"),
    )


class FetchStatementSegment(BaseSegment):
    """A `FETCH` statement.

    As specified in
    https://docs.aws.amazon.com/redshift/latest/dg/fetch.html
    """

    type = "fetch_statement"
    match_grammar = Sequence(
        "fetch",
        OneOf(
            "NEXT",
            "ALL",
            Sequence(
                "FORWARD",
                OneOf(
                    "ALL",
                    Ref("NumericLiteralSegment"),
                ),
            ),
        ),
        "FROM",
        Ref("ObjectReferenceSegment"),
    )


class CloseStatementSegment(BaseSegment):
    """A `CLOSE` statement.

    As specified in
    https://docs.aws.amazon.com/redshift/latest/dg/close.html
    """

    type = "close_statement"
    match_grammar = Sequence(
        "CLOSE",
        Ref("ObjectReferenceSegment"),
    )


class AltereDatashareStatementSegment(BaseSegment):
    """An `ALTER DATASHARE` statement.

    https://docs.aws.amazon.com/redshift/latest/dg/r_ALTER_DATASHARE.html
    """

    type = "create_datashare_statement"
    match_grammar = Sequence(
        "ALTER",
        "DATASHARE",
        Ref("ObjectReferenceSegment"),
        OneOf(
            # add or remove objects to the datashare
            Sequence(
                OneOf(
                    "ADD",
                    "REMOVE",
                ),
                OneOf(
                    Sequence(
                        "TABLE",
                        Delimited(Ref("TableReferenceSegment")),
                    ),
                    Sequence(
                        "SCHEMA",
                        Delimited(Ref("SchemaReferenceSegment")),
                    ),
                    Sequence(
                        "FUNCTION",
                        Delimited(Ref("FunctionNameSegment")),
                    ),
                    Sequence(
                        "ALL",
                        OneOf("TABLES", "FUNCTIONS"),
                        "IN",
                        "SCHEMA",
                        Delimited(Ref("SchemaReferenceSegment")),
                    ),
                ),
            ),
            # configure the properties of the datashare
            Sequence(
                "SET",
                OneOf(
                    Sequence(
                        "PUBLICACCESSIBLE",
                        Ref("EqualsSegment", optional=True),
                        Ref("BooleanLiteralGrammar"),
                    ),
                    Sequence(
                        "INCLUDENEW",
                        Ref("EqualsSegment", optional=True),
                        Ref("BooleanLiteralGrammar"),
                        "FOR",
                        "SCHEMA",
                        Ref("SchemaReferenceSegment"),
                    ),
                ),
            ),
        ),
    )


class CreateDatashareStatementSegment(BaseSegment):
    """A `CREATE DATASHARE` statement.

    https://docs.aws.amazon.com/redshift/latest/dg/r_CREATE_DATASHARE.html
    """

    type = "create_datashare_statement"
    match_grammar = Sequence(
        "CREATE",
        "DATASHARE",
        Ref("ObjectReferenceSegment"),
        Sequence(
            Ref.keyword("SET", optional=True),
            "PUBLICACCESSIBLE",
            Ref("EqualsSegment", optional=True),
            OneOf(
                "TRUE",
                "FALSE",
            ),
            optional=True,
        ),
    )


class DescDatashareStatementSegment(BaseSegment):
    """A `DESC DATASHARE` statement.

    https://docs.aws.amazon.com/redshift/latest/dg/r_DESC_DATASHARE.html
    """

    type = "desc_datashare_statement"
    match_grammar = Sequence(
        "DESC",
        "DATASHARE",
        Ref("ObjectReferenceSegment"),
        Sequence(
            "OF",
            Sequence(
                "ACCOUNT",
                Ref("QuotedLiteralSegment"),
                optional=True,
            ),
            "NAMESPACE",
            Ref("QuotedLiteralSegment"),
            optional=True,
        ),
    )


class DropDatashareStatementSegment(BaseSegment):
    """A `DROP DATASHARE` statement.

    https://docs.aws.amazon.com/redshift/latest/dg/r_DROP_DATASHARE.html
    """

    type = "drop_datashare_statement"
    match_grammar = Sequence(
        "DROP",
        "DATASHARE",
        Ref("ObjectReferenceSegment"),
    )


class ShowDatasharesStatementSegment(BaseSegment):
    """A `SHOW DATASHARES` statement.

    https://docs.aws.amazon.com/redshift/latest/dg/r_SHOW_DATASHARES.html
    """

    type = "show_datashares_statement"
    match_grammar = Sequence(
        "SHOW",
        "DATASHARES",
        Sequence(
            "LIKE",
            Ref("QuotedLiteralSegment"),
            optional=True,
        ),
    )


class GrantUsageDatashareStatementSegment(BaseSegment):
    """A `GRANT DATASHARES` statement.

    https://docs.aws.amazon.com/redshift/latest/dg/r_GRANT.html
    section "Granting datashare permissions"
    Note: According to docummentation, multiple accounts and namespaces can be
          specified. However, tests using redshift instance showed this causes a syntax
          error.
    """

    type = "grant_datashare_statement"
    match_grammar = Sequence(
        OneOf("GRANT", "REVOKE"),
        "USAGE",
        "ON",
        "DATASHARE",
        Ref("ObjectReferenceSegment"),
        OneOf("TO", "FROM"),
        OneOf(
            Sequence("NAMESPACE", Ref("QuotedLiteralSegment")),
            Sequence(
                "ACCOUNT",
                Sequence(
                    Ref("QuotedLiteralSegment"),
                    Sequence("VIA", "DATA", "CATALOG", optional=True),
                ),
            ),
        ),
    )


class CreateRlsPolicyStatementSegment(BaseSegment):
    """A `CREATE RLS POLICY` statement.

    https://docs.aws.amazon.com/redshift/latest/dg/r_CREATE_RLS_POLICY.html
    """

    type = "create_rls_policy_statement"
    match_grammar = Sequence(
        "CREATE",
        "RLS",
        "POLICY",
        Ref("ObjectReferenceSegment"),
        Sequence(
            "WITH",
            Bracketed(
                Delimited(
                    Sequence(
                        Ref("ColumnReferenceSegment"),
                        Ref("DatatypeSegment"),
                    ),
                ),
            ),
            Sequence(
                Ref.keyword("AS", optional=True),
                Ref("AliasExpressionSegment"),
                optional=True,
            ),
            optional=True,
        ),
        Sequence(
            "USING",
            Bracketed(Ref("ExpressionSegment")),
        ),
    )


class ManageRlsPolicyStatementSegment(BaseSegment):
    """An `ATTACH/DETACH RLS POLICY` statement.

    https://docs.aws.amazon.com/redshift/latest/dg/r_ATTACH_RLS_POLICY.html
    https://docs.aws.amazon.com/redshift/latest/dg/r_DETACH_RLS_POLICY.html
    """

    # 1 statement for both ATTACH and DETACH since same syntax
    type = "manage_rls_policy_statement"
    match_grammar = Sequence(
        OneOf("ATTACH", "DETACH"),
        "RLS",
        "POLICY",
        Ref("ObjectReferenceSegment"),
        "ON",
        Ref.keyword("TABLE", optional=True),
        Delimited(
            Ref("TableReferenceSegment"),
        ),
        OneOf("TO", "FROM"),
        Delimited(
            OneOf(
                Sequence(
                    Ref.keyword("ROLE", optional=True),
                    Ref("RoleReferenceSegment"),
                ),
                "PUBLIC",
            ),
        ),
    )


class DropRlsPolicyStatementSegment(BaseSegment):
    """A `DROP RLS POLICY` statement.

    https://docs.aws.amazon.com/redshift/latest/dg/r_DROP_RLS_POLICY.html
    """

    type = "drop_rls_policy_statement"
    match_grammar = Sequence(
        "DROP",
        "RLS",
        "POLICY",
        Ref("IfExistsGrammar", optional=True),
        Ref("ObjectReferenceSegment"),
        OneOf(
            "CASCADE",
            "RESTRICT",
            optional=True,
        ),
    )


class AnalyzeCompressionStatementSegment(BaseSegment):
    """An `ANALYZE COMPRESSION` statement.

    https://docs.aws.amazon.com/redshift/latest/dg/r_ANALYZE_COMPRESSION.html
    """

    type = "analyze_compression_statement"
    match_grammar = Sequence(
        OneOf("ANALYZE", "ANALYSE"),
        "COMPRESSION",
        Sequence(
            Ref("TableReferenceSegment"),
            Bracketed(
                Delimited(
                    Ref("ColumnReferenceSegment"),
                ),
                optional=True,
            ),
            Sequence(
                "COMPROWS",
                Ref("NumericLiteralSegment"),
                optional=True,
            ),
            optional=True,
        ),
    )


class VacuumStatementSegment(postgres.VacuumStatementSegment):
    """A `VACUUM` statement.

    https://docs.aws.amazon.com/redshift/latest/dg/r_VACUUM_command.html
    """

    match_grammar = Sequence(
        "VACUUM",
        OneOf(
            "FULL",
            "REINDEX",
            "RECLUSTER",
            Sequence(
                OneOf(
                    "SORT",
                    "DELETE",
                ),
                "ONLY",
            ),
            optional=True,
        ),
        Ref("TableReferenceSegment", optional=True),
        Sequence(
            "TO",
            Ref("NumericLiteralSegment"),
            "PERCENT",
            optional=True,
        ),
        Ref.keyword("BOOST", optional=True),
    )


# Adding Redshift specific statements
class StatementSegment(postgres.StatementSegment):
    """A generic segment, to any of its child subsegments."""

    type = "statement"

    match_grammar = postgres.StatementSegment.match_grammar.copy(
        insert=[
            Ref("CreateLibraryStatementSegment"),
            Ref("CreateGroupStatementSegment"),
            Ref("AlterUserStatementSegment"),
            Ref("AlterGroupStatementSegment"),
            Ref("CreateExternalTableAsStatementSegment"),
            Ref("CreateExternalTableStatementSegment"),
            Ref("CreateExternalSchemaStatementSegment"),
            Ref("DataFormatSegment"),
            Ref("UnloadStatementSegment"),
            Ref("CopyStatementSegment"),
            Ref("ShowModelStatementSegment"),
            Ref("CreateDatashareStatementSegment"),
            Ref("DescDatashareStatementSegment"),
            Ref("DropDatashareStatementSegment"),
            Ref("ShowDatasharesStatementSegment"),
            Ref("AltereDatashareStatementSegment"),
            Ref("DeclareStatementSegment"),
            Ref("FetchStatementSegment"),
            Ref("CloseStatementSegment"),
            Ref("AnalyzeCompressionStatementSegment"),
            Ref("AlterProcedureStatementSegment"),
            Ref("CallStatementSegment"),
            Ref("CreateRlsPolicyStatementSegment"),
            Ref("ManageRlsPolicyStatementSegment"),
            Ref("DropRlsPolicyStatementSegment"),
            Ref("CreateExternalFunctionStatementSegment"),
            Ref("GrantUsageDatashareStatementSegment"),
        ],
    )


class PartitionedBySegment(BaseSegment):
    """Partitioned By Segment.

    As specified in
    https://docs.aws.amazon.com/redshift/latest/dg/r_CREATE_EXTERNAL_TABLE.html
    """

    type = "partitioned_by_segment"

    match_grammar = Sequence(
        Ref.keyword("PARTITIONED"),
        "BY",
        Bracketed(
            Delimited(
                Sequence(
                    Ref("ColumnReferenceSegment"),
                    Ref("DatatypeSegment", optional=True),
                ),
            ),
        ),
    )


class RowFormatDelimitedSegment(BaseSegment):
    """Row Format Delimited Segment.

    As specified in
    https://docs.aws.amazon.com/redshift/latest/dg/r_CREATE_EXTERNAL_TABLE.html
    """

    type = "row_format_delimited_segment"

    match_grammar = AnySetOf(
        Sequence(
            "FIELDS",
            "TERMINATED",
            "BY",
            Ref("QuotedLiteralSegment"),
        ),
        Sequence(
            "LINES",
            "TERMINATED",
            "BY",
            Ref("QuotedLiteralSegment"),
        ),
        optional=True,
    )


class CreateUserStatementSegment(ansi.CreateUserStatementSegment):
    """`CREATE USER` statement.

    https://docs.aws.amazon.com/redshift/latest/dg/r_CREATE_USER.html
    """

    match_grammar = Sequence(
        "CREATE",
        "USER",
        Ref("RoleReferenceSegment"),
        Ref.keyword("WITH", optional=True),
        "PASSWORD",
        OneOf(Ref("QuotedLiteralSegment"), "DISABLE"),
        AnySetOf(
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


class CreateGroupStatementSegment(BaseSegment):
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


class AlterUserStatementSegment(BaseSegment):
    """`ALTER USER` statement.

    https://docs.aws.amazon.com/redshift/latest/dg/r_ALTER_USER.html
    """

    type = "alter_user_statement"

    match_grammar = Sequence(
        "ALTER",
        "USER",
        Ref("RoleReferenceSegment"),
        Ref.keyword("WITH", optional=True),
        AnySetOf(
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


class AlterGroupStatementSegment(BaseSegment):
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


class TransactionStatementSegment(BaseSegment):
    """A `BEGIN|START`, `COMMIT|END` or `ROLLBACK|ABORT` transaction statement.

    https://docs.aws.amazon.com/redshift/latest/dg/r_BEGIN.html
    """

    type = "transaction_statement"
    match_grammar = Sequence(
        OneOf("BEGIN", "START", "COMMIT", "END", "ROLLBACK", "ABORT"),
        OneOf("TRANSACTION", "WORK", optional=True),
        Sequence(
            "ISOLATION",
            "LEVEL",
            OneOf(
                "SERIALIZABLE",
                Sequence("READ", "COMMITTED"),
                Sequence("READ", "UNCOMMITTED"),
                Sequence("REPEATABLE", "READ"),
            ),
            optional=True,
        ),
        OneOf(
            Sequence("READ", "ONLY"),
            Sequence("READ", "WRITE"),
            optional=True,
        ),
    )


class AlterSchemaStatementSegment(BaseSegment):
    """An `ALTER SCHEMA` statement.

    https://docs.aws.amazon.com/redshift/latest/dg/r_ALTER_SCHEMA.html
    """

    type = "alter_schema_statement"
    match_grammar = Sequence(
        "ALTER",
        "SCHEMA",
        Ref("SchemaReferenceSegment"),
        OneOf(
            Sequence(
                "RENAME",
                "TO",
                Ref("SchemaReferenceSegment"),
            ),
            Sequence(
                "OWNER",
                "TO",
                Ref("RoleReferenceSegment"),
            ),
            Ref("QuotaGrammar"),
        ),
    )


class LockTableStatementSegment(BaseSegment):
    """An `LOCK TABLE` statement.

    https://www.postgresql.org/docs/14/sql-lock.html
    """

    type = "lock_table_statement"
    match_grammar: Matchable = Sequence(
        "LOCK",
        Ref.keyword("TABLE", optional=True),
        Delimited(
            Ref("TableReferenceSegment"),
        ),
    )


class TableExpressionSegment(ansi.TableExpressionSegment):
    """The main table expression e.g. within a FROM clause.

    Override to add Object unpivoting.
    """

    match_grammar = ansi.TableExpressionSegment.match_grammar.copy(
        insert=[
            Ref("ObjectUnpivotSegment", optional=True),
            Ref("ArrayUnnestSegment", optional=True),
        ],
        before=Ref("TableReferenceSegment"),
    )


class ObjectUnpivotSegment(BaseSegment):
    """Object unpivoting.

    https://docs.aws.amazon.com/redshift/latest/dg/query-super.html#unpivoting
    """

    type = "object_unpivoting"
    match_grammar: Matchable = Sequence(
        "UNPIVOT",
        Ref("ObjectReferenceSegment"),
        "AS",
        Ref("SingleIdentifierGrammar"),
        "AT",
        Ref("SingleIdentifierGrammar"),
    )


class ArrayAccessorSegment(ansi.ArrayAccessorSegment):
    """Array element accessor.

    Redshift allows multiple levels of array access, like Postgres,
    but it
    * doesn't allow ranges like `myarray[1:2]`
    * does allow function or column expressions `myarray[idx]`
    """

    match_grammar = Sequence(
        AnyNumberOf(
            Bracketed(
                OneOf(Ref("NumericLiteralSegment"), Ref("ExpressionSegment")),
                bracket_type="square",
            )
        )
    )


class ArrayUnnestSegment(BaseSegment):
    """Array unnesting.

    https://docs.aws.amazon.com/redshift/latest/dg/query-super.html
    """

    type = "array_unnesting"
    match_grammar: Matchable = Sequence(
        Ref("ObjectReferenceSegment"),
        "AS",
        Ref("SingleIdentifierGrammar"),
        "AT",
        Ref("SingleIdentifierGrammar"),
    )


class CallStatementSegment(BaseSegment):
    """A `CALL` statement.

    https://docs.aws.amazon.com/redshift/latest/dg/r_CALL_procedure.html
    """

    type = "call_statement"
    match_grammar = Sequence(
        "CALL",
        Ref("FunctionSegment"),
    )


class SelectClauseModifierSegment(postgres.SelectClauseModifierSegment):
    """Things that come after SELECT but before the columns."""

    match_grammar = postgres.SelectClauseModifierSegment.match_grammar.copy(
        insert=[Sequence("TOP", Ref("NumericLiteralSegment"))],
    )


class ConvertFunctionNameSegment(BaseSegment):
    """CONVERT function name segment.

    Function taking a data type identifier and an expression.
    An alternative to CAST.
    """

    type = "function_name"
    match_grammar = Sequence("CONVERT")


class FunctionSegment(ansi.FunctionSegment):
    """A scalar or aggregate function.

    Maybe in the future we should distinguish between
    aggregate functions and other functions. For now
    we treat them the same because they look the same
    for our purposes.
    """

    type = "function"
    match_grammar: Matchable = OneOf(
        Sequence(
            # Treat functions which take date parts separately
            # So those functions parse date parts as DatetimeUnitSegment
            # rather than identifiers.
            Sequence(
                Ref("DatePartFunctionNameSegment"),
                Bracketed(
                    Delimited(
                        Ref("DatetimeUnitSegment"),
                        Ref(
                            "FunctionContentsGrammar",
                            # The brackets might be empty for some functions...
                            optional=True,
                        ),
                    ),
                    parse_mode=ParseMode.GREEDY,
                ),
            ),
        ),
        Sequence(
            Sequence(
                OneOf(
                    Ref(
                        "FunctionNameSegment",
                        exclude=OneOf(
                            Ref("DatePartFunctionNameSegment"),
                            Ref("ValuesClauseSegment"),
                            Ref("ConvertFunctionNameSegment"),
                        ),
                    ),
                    Sequence(
                        Ref.keyword("APPROXIMATE"),
                        Ref(
                            "FunctionNameSegment",
                            exclude=OneOf(
                                Ref("DatePartFunctionNameSegment"),
                                Ref("ValuesClauseSegment"),
                                Ref("ConvertFunctionNameSegment"),
                            ),
                        ),
                    ),
                ),
                Bracketed(
                    Ref(
                        "FunctionContentsGrammar",
                        # The brackets might be empty for some functions...
                        optional=True,
                    ),
                    parse_mode=ParseMode.GREEDY,
                ),
            ),
            Ref("PostFunctionGrammar", optional=True),
        ),
        Sequence(
            Ref("ConvertFunctionNameSegment"),
            Bracketed(
                Ref("DatatypeSegment"),
                Ref("CommaSegment"),
                Ref("ExpressionSegment"),
            ),
        ),
    )


class FromClauseSegment(ansi.FromClauseSegment):
    """Slightly modified version which allows for using brackets for content of FROM."""

    match_grammar = Sequence(
        "FROM",
        Delimited(
            OptionallyBracketed(Ref("FromExpressionSegment")),
        ),
    )


class CreateViewStatementSegment(BaseSegment):
    """A `CREATE VIEW` statement."""

    type = "create_view_statement"
    # https://crate.io/docs/sql-99/en/latest/chapters/18.html#create-view-statement
    # https://dev.mysql.com/doc/refman/8.0/en/create-view.html
    # https://www.postgresql.org/docs/12/sql-createview.html
    match_grammar: Matchable = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        "VIEW",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        # Optional list of column names
        Ref("BracketedColumnReferenceListGrammar", optional=True),
        "AS",
        OptionallyBracketed(Ref("SelectableGrammar")),
        Ref("WithNoSchemaBindingClauseSegment", optional=True),
    )


class CreateMaterializedViewStatementSegment(
    postgres.CreateMaterializedViewStatementSegment
):
    """A `CREATE MATERIALIZED VIEW` statement.

    # https://docs.aws.amazon.com/redshift/latest/dg/materialized-view-create-sql-command.html
    """

    type = "create_materialized_view_statement"
    match_grammar = Sequence(
        "CREATE",
        "MATERIALIZED",
        "VIEW",
        Ref("TableReferenceSegment"),
        Sequence("BACKUP", OneOf("YES", "NO"), optional=True),
        Ref("TableAttributeSegment", optional=True),
        Sequence("AUTO", "REFRESH", OneOf("YES", "NO"), optional=True),
        "AS",
        OneOf(
            OptionallyBracketed(Ref("SelectableGrammar")),
            OptionallyBracketed(Sequence("TABLE", Ref("TableReferenceSegment"))),
            Ref("ValuesClauseSegment"),
            OptionallyBracketed(Sequence("EXECUTE", Ref("FunctionSegment"))),
        ),
        Ref("WithDataClauseSegment", optional=True),
    )


class CreateExternalFunctionStatementSegment(BaseSegment):
    """A `CREATE EXTERNAL FUNCTION` segment.

    https://docs.aws.amazon.com/redshift/latest/dg/r_CREATE_EXTERNAL_FUNCTION.html
    """

    type = "create_external_function_statement"
    match_grammar = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        "EXTERNAL",
        "FUNCTION",
        Ref("FunctionNameSegment"),
        Bracketed(
            Delimited(
                Ref("DatatypeSegment"),
                optional=True,
            ),
        ),
        "RETURNS",
        Ref("DatatypeSegment"),
        OneOf("VOLATILE", "STABLE", "IMMUTABLE"),
        OneOf("LAMBDA", "SAGEMAKER"),
        Ref("QuotedLiteralSegment"),
        "IAM_ROLE",
        OneOf("DEFAULT", Ref("QuotedLiteralSegment")),
        Sequence(
            "RETRY_TIMEOUT",
            Ref("NumericLiteralSegment"),
            optional=True,
        ),
    )


class QualifyClauseSegment(BaseSegment):
    """A `QUALIFY` clause like in `SELECT`.

    https://docs.aws.amazon.com/redshift/latest/dg/r_QUALIFY_clause.html
    """

    type = "qualify_clause"
    match_grammar = Sequence(
        "QUALIFY",
        Indent,
        Ref("ExpressionSegment"),
        Dedent,
    )


class SelectStatementSegment(postgres.SelectStatementSegment):
    """A snowflake `SELECT` statement including optional Qualify.

    https://docs.aws.amazon.com/redshift/latest/dg/r_QUALIFY_clause.html
    """

    type = "select_statement"

    match_grammar = postgres.SelectStatementSegment.match_grammar.copy(
        insert=[Ref("QualifyClauseSegment", optional=True)],
        before=Ref("OrderByClauseSegment", optional=True),
        terminators=[Ref("SetOperatorSegment")],
    )


class UnorderedSelectStatementSegment(ansi.UnorderedSelectStatementSegment):
    """A snowflake unordered `SELECT` statement including optional Qualify.

    https://docs.aws.amazon.com/redshift/latest/dg/r_QUALIFY_clause.html
    """

    type = "select_statement"

    match_grammar = ansi.UnorderedSelectStatementSegment.match_grammar.copy(
        insert=[Ref("QualifyClauseSegment", optional=True)],
        before=Ref("OverlapsClauseSegment", optional=True),
    )
