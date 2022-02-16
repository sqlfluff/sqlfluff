"""The Amazon Redshift dialect.

This is based on postgres dialect, since it was initially based off of Postgres 8.
We should monitor in future and see if it should be rebased off of ANSI
"""
from sqlfluff.core.parser import (
    OneOf,
    AnyNumberOf,
    AnySetOf,
    Anything,
    Ref,
    Sequence,
    Bracketed,
    BaseSegment,
    Delimited,
    Nothing,
    OptionallyBracketed,
    Matchable,
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

redshift_dialect.sets("date_part_function_name").update(["DATEADD", "DATEDIFF"])

redshift_dialect.replace(WellKnownTextGeometrySegment=Nothing())

ObjectReferenceSegment = redshift_dialect.get_segment("ObjectReferenceSegment")


# need to ignore type due to mypy rules on type variables
# see https://mypy.readthedocs.io/en/stable/common_issues.html#variables-vs-type-aliases
# for details
@redshift_dialect.segment(replace=True)
class ColumnReferenceSegment(ObjectReferenceSegment):  # type: ignore
    """A reference to column, field or alias.

    Adjusted to support column references for Redshift's SUPER data type
    (https://docs.aws.amazon.com/redshift/latest/dg/super-overview.html), which
    uses a subset of the PartiQL language (https://partiql.org/) to reference
    columns.
    """

    type = "column_reference"
    match_grammar: Matchable = Delimited(
        Sequence(
            Ref("SingleIdentifierGrammar"),
            AnyNumberOf(Ref("ArrayAccessorSegment")),
        ),
        delimiter=OneOf(
            Ref("DotSegment"), Sequence(Ref("DotSegment"), Ref("DotSegment"))
        ),
        terminator=OneOf(
            "ON",
            "AS",
            "USING",
            Ref("CommaSegment"),
            Ref("CastOperatorSegment"),
            Ref("BinaryOperatorGrammar"),
            Ref("ColonSegment"),
            Ref("DelimiterSegment"),
            Ref("JoinLikeClauseGrammar"),
        ),
        allow_gaps=False,
    )


@redshift_dialect.segment(replace=True)
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


@redshift_dialect.segment(replace=True)
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
            Bracketed(
                Delimited(Ref("NumericLiteralSegment")),
                optional=True,
            ),
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
                Bracketed(
                    OneOf(
                        Ref("NumericLiteralSegment"),
                        "MAX",
                    ),
                    optional=True,
                ),
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
            Bracketed(
                Ref("NumericLiteralSegment"),
                optional=True,
            ),
        ),
    )


@redshift_dialect.segment()
class ColumnEncodingSegment(BaseSegment):
    """ColumnEncoding segment.

    Indicates column compression encoding.

    As specified by:
    https://docs.aws.amazon.com/redshift/latest/dg/c_Compression_encodings.html
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
class CompressionTypeSegment(BaseSegment):
    """Compression type segment.

    Indicates file compression type.

    https://docs.aws.amazon.com/redshift/latest/dg/copy-parameters-file-compression.html # noqa
    """

    type = "compression_type_segment"

    match_grammar = OneOf(
        "BZIP2",
        "GZIP",
        "LZOP",
        "ZSTD",
    )


@redshift_dialect.segment()
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


@redshift_dialect.segment()
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


@redshift_dialect.segment()
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

    As specified in
    https://docs.aws.amazon.com/redshift/latest/dg/r_CREATE_TABLE_NEW.html
    """

    type = "column_constraint_segment"

    match_grammar = AnySetOf(
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


@redshift_dialect.segment(replace=True)
class TableConstraintSegment(BaseSegment):
    """Redshift specific table constraints.

    As specified in
    https://docs.aws.amazon.com/redshift/latest/dg/r_CREATE_TABLE_NEW.html
    """

    type = "table_constraint"

    match_grammar = AnySetOf(
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

    As specified in
    https://docs.aws.amazon.com/redshift/latest/dg/r_CREATE_TABLE_NEW.html
    """

    type = "like_option_segment"

    match_grammar = Sequence(OneOf("INCLUDING", "EXCLUDING"), "DEFAULTS")


@redshift_dialect.segment(replace=True)
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


@redshift_dialect.segment(replace=True)
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


@redshift_dialect.segment()
class ShowModelSegment(BaseSegment):
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


@redshift_dialect.segment()
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


@redshift_dialect.segment()
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


@redshift_dialect.segment()
class CreateLibraryStatementSegment(BaseSegment):
    """A `CREATE LIBRARY` statement.

    https://docs.aws.amazon.com/redshift/latest/dg/r_CREATE_LIBRARY.html
    """

    type = "create_library_statement"

    match_grammar = Sequence(
        "CREATE",
        Sequence(
            "OR",
            "REPLACE",
            optional=True,
        ),
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


@redshift_dialect.segment()
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
            Ref("CompressionTypeSegment", optional=True),
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


@redshift_dialect.segment(replace=True)
class CopyStatementSegment(BaseSegment):
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
            Ref("CompressionTypeSegment", optional=True),
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
                Ref("QuotedLiteralSegment"),
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
                Ref("QuotedLiteralSegment"),
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


@redshift_dialect.segment(replace=True)
class CreateSchemaStatementSegment(BaseSegment):
    """A `CREATE SCHEMA` statement.

    https://docs.aws.amazon.com/redshift/latest/dg/r_CREATE_SCHEMA.html
    TODO: support optional SCHEMA_ELEMENT
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
                    Ref("ObjectReferenceSegment"),
                    optional=True,
                ),
            ),
            Sequence(
                "AUTHORIZATION",
                Ref("ObjectReferenceSegment"),
            ),
        ),
        Sequence(
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
            optional=True,
        ),
    )


@redshift_dialect.segment()
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


@redshift_dialect.segment()
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


@redshift_dialect.segment()
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


@redshift_dialect.segment()
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


@redshift_dialect.segment()
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


@redshift_dialect.segment()
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


@redshift_dialect.segment()
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


@redshift_dialect.segment()
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


@redshift_dialect.segment()
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


@redshift_dialect.segment()
class VacuumStatementSegment(BaseSegment):
    """A `VACUUM` statement.

    https://docs.aws.amazon.com/redshift/latest/dg/r_VACUUM_command.html
    """

    type = "vacuum_statement"
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
@redshift_dialect.segment(replace=True)
class StatementSegment(BaseSegment):
    """A generic segment, to any of its child subsegments."""

    type = "statement"

    parse_grammar = redshift_dialect.get_segment("StatementSegment").parse_grammar.copy(
        insert=[
            Ref("TableAttributeSegment"),
            Ref("ColumnAttributeSegment"),
            Ref("ColumnEncodingSegment"),
            Ref("AuthorizationSegment"),
            Ref("CreateLibraryStatementSegment"),
            Ref("CreateUserSegment"),
            Ref("CreateGroupSegment"),
            Ref("AlterUserSegment"),
            Ref("AlterGroupSegment"),
            Ref("CreateExternalTableAsStatementSegment"),
            Ref("CreateExternalTableStatementSegment"),
            Ref("PartitionedBySegment"),
            Ref("RowFormatDelimitedSegment"),
            Ref("DataFormatSegment"),
            Ref("CompressionTypeSegment"),
            Ref("UnloadStatementSegment"),
            Ref("CopyStatementSegment"),
            Ref("ShowModelSegment"),
            Ref("CreateDatashareStatementSegment"),
            Ref("DescDatashareStatementSegment"),
            Ref("DropDatashareStatementSegment"),
            Ref("ShowDatasharesStatementSegment"),
            Ref("AltereDatashareStatementSegment"),
            Ref("DeclareStatementSegment"),
            Ref("FetchStatementSegment"),
            Ref("CloseStatementSegment"),
            Ref("AnalyzeCompressionStatementSegment"),
            Ref("VacuumStatementSegment"),
        ],
    )

    match_grammar = redshift_dialect.get_segment(
        "StatementSegment"
    ).match_grammar.copy()


@redshift_dialect.segment()
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
                    Ref("DatatypeSegment"),
                ),
            ),
        ),
    )


@redshift_dialect.segment()
class RowFormatDelimitedSegment(BaseSegment):
    """Row Format Delimited Segment.

    As specified in
    https://docs.aws.amazon.com/redshift/latest/dg/r_CREATE_EXTERNAL_TABLE.html
    """

    type = "row_format_deimited_segment"

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
