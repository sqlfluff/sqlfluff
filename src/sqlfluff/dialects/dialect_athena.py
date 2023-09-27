"""The AWS Athena dialect.

https://docs.aws.amazon.com/athena/latest/ug/what-is.html
"""

from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.core.parser import (
    AnyNumberOf,
    BaseSegment,
    Bracketed,
    CodeSegment,
    Dedent,
    Delimited,
    IdentifierSegment,
    Indent,
    KeywordSegment,
    LiteralSegment,
    Matchable,
    Nothing,
    OneOf,
    OptionallyBracketed,
    Ref,
    RegexParser,
    SegmentGenerator,
    Sequence,
    StringLexer,
    StringParser,
    SymbolSegment,
    TypedParser,
)
from sqlfluff.dialects import dialect_ansi as ansi
from sqlfluff.dialects.dialect_athena_keywords import (
    athena_reserved_keywords,
    athena_unreserved_keywords,
)

ansi_dialect = load_raw_dialect("ansi")

athena_dialect = ansi_dialect.copy_as("athena")

athena_dialect.sets("unreserved_keywords").update(athena_unreserved_keywords)
athena_dialect.sets("reserved_keywords").update(athena_reserved_keywords)

athena_dialect.insert_lexer_matchers(
    # Array Operations: https://prestodb.io/docs/0.217/functions/array.html
    [
        StringLexer("right_arrow", "->", CodeSegment),
    ],
    before="like_operator",
)

athena_dialect.bracket_sets("angle_bracket_pairs").update(
    [
        ("angle", "StartAngleBracketSegment", "EndAngleBracketSegment", False),
    ]
)

athena_dialect.add(
    StartAngleBracketSegment=StringParser(
        "<", SymbolSegment, type="start_angle_bracket"
    ),
    EndAngleBracketSegment=StringParser(">", SymbolSegment, type="end_angle_bracket"),
    RightArrowOperator=StringParser("->", SymbolSegment, type="binary_operator"),
    JsonfileKeywordSegment=StringParser("JSONFILE", KeywordSegment, type="file_format"),
    RcfileKeywordSegment=StringParser("RCFILE", KeywordSegment, type="file_format"),
    OrcKeywordSegment=StringParser("ORCFILE", KeywordSegment, type="file_format"),
    ParquetKeywordSegment=StringParser(
        "PARQUETFILE", KeywordSegment, type="file_format"
    ),
    AvroKeywordSegment=StringParser("AVROFILE", KeywordSegment, type="file_format"),
    IonKeywordSegment=StringParser("IONFILE", KeywordSegment, type="file_format"),
    SequencefileKeywordSegment=StringParser(
        "SEQUENCEFILE", KeywordSegment, type="file_format"
    ),
    TextfileKeywordSegment=StringParser("TEXTFILE", KeywordSegment, type="file_format"),
    PropertyGrammar=Sequence(
        Ref("QuotedLiteralSegment"),
        Ref("EqualsSegment"),
        Ref("QuotedLiteralSegment"),
    ),
    LocationGrammar=Sequence("LOCATION", Ref("QuotedLiteralSegment")),
    BracketedPropertyListGrammar=Bracketed(Delimited(Ref("PropertyGrammar"))),
    CTASPropertyGrammar=Sequence(
        OneOf(
            "external_location",
            "format",
            "partitioned_by",
            "bucketed_by",
            "bucket_count",
            "write_compression",
            "orc_compression",
            "parquet_compression",
            "field_delimiter",
            "location",
        ),
        Ref("EqualsSegment"),
        Ref("LiteralGrammar"),
    ),
    CTASIcebergPropertyGrammar=Sequence(
        OneOf(
            "external_location",
            "format",
            "partitioned_by",
            "bucketed_by",
            "bucket_count",
            "write_compression",
            "orc_compression",
            "parquet_compression",
            "field_delimiter",
            "location",
            "is_external",
            "table_type",
            "partitioning",
            "vacuum_max_snapshot_age_ms",
            "vacuum_min_snapshots_to_keep",
        ),
        Ref("EqualsSegment"),
        Ref("LiteralGrammar"),
    ),
    BracketedCTASPropertyGrammar=Bracketed(
        OneOf(
            Delimited(
                Ref("CTASPropertyGrammar"),
            ),
            Delimited(
                Ref("CTASIcebergPropertyGrammar"),
            ),
        ),
    ),
    UnloadPropertyGrammar=Sequence(
        OneOf(
            "format",
            "partitioned_by",
            "compression",
            "field_delimiter",
        ),
        Ref("EqualsSegment"),
        Ref("LiteralGrammar"),
    ),
    BracketedUnloadPropertyGrammar=Bracketed(Delimited(Ref("UnloadPropertyGrammar"))),
    TablePropertiesGrammar=Sequence(
        "TBLPROPERTIES", Ref("BracketedPropertyListGrammar")
    ),
    SerdePropertiesGrammar=Sequence(
        "WITH", "SERDEPROPERTIES", Ref("BracketedPropertyListGrammar")
    ),
    TerminatedByGrammar=Sequence("TERMINATED", "BY", Ref("QuotedLiteralSegment")),
    FileFormatGrammar=OneOf(
        "SEQUENCEFILE",
        "TEXTFILE",
        "RCFILE",
        "ORC",
        "PARQUET",
        "AVRO",
        "JSONFILE",
        "ION",
        Sequence(
            "INPUTFORMAT",
            Ref("QuotedLiteralSegment"),
            "OUTPUTFORMAT",
            Ref("QuotedLiteralSegment"),
        ),
    ),
    StoredAsGrammar=Sequence("STORED", "AS", Ref("FileFormatGrammar")),
    StoredByGrammar=Sequence(
        "STORED",
        "BY",
        Ref("QuotedLiteralSegment"),
        Ref("SerdePropertiesGrammar", optional=True),
    ),
    StorageFormatGrammar=OneOf(
        Sequence(
            Ref("RowFormatClauseSegment", optional=True),
            Ref("StoredAsGrammar", optional=True),
        ),
        Ref("StoredByGrammar"),
    ),
    CommentGrammar=Sequence("COMMENT", Ref("QuotedLiteralSegment")),
    PartitionSpecGrammar=Sequence(
        "PARTITION",
        Bracketed(
            Delimited(
                Sequence(
                    Ref("ColumnReferenceSegment"),
                    Sequence(
                        Ref("EqualsSegment"),
                        Ref("LiteralGrammar"),
                        optional=True,
                    ),
                )
            )
        ),
    ),
    BackQuotedIdentifierSegment=TypedParser(
        "back_quote",
        LiteralSegment,
        type="quoted_identifier",
    ),
    DatetimeWithTZSegment=Sequence(OneOf("TIMESTAMP", "TIME"), "WITH", "TIME", "ZONE"),
)

athena_dialect.replace(
    LiteralGrammar=ansi_dialect.get_grammar("LiteralGrammar").copy(
        insert=[
            Ref("ParameterSegment"),
        ]
    ),
    AccessorGrammar=Sequence(
        AnyNumberOf(
            Ref("ArrayAccessorSegment"),
            optional=True,
        ),
        AnyNumberOf(
            Sequence(
                Ref("ObjectReferenceDelimiterGrammar"),
                Ref("ObjectReferenceSegment"),
            ),
            optional=True,
        ),
    ),
    QuotedLiteralSegment=OneOf(
        TypedParser("single_quote", LiteralSegment, type="quoted_literal"),
        TypedParser("double_quote", LiteralSegment, type="quoted_literal"),
        TypedParser("back_quote", LiteralSegment, type="quoted_literal"),
    ),
    TrimParametersGrammar=Nothing(),
    NakedIdentifierSegment=SegmentGenerator(
        # Generate the anti template from the set of reserved keywords
        lambda dialect: RegexParser(
            r"[A-Z0-9_]*[A-Z_][A-Z0-9_]*",
            IdentifierSegment,
            type="naked_identifier",
            anti_template=r"^(" + r"|".join(dialect.sets("reserved_keywords")) + r")$",
        )
    ),
    SingleIdentifierGrammar=ansi_dialect.get_grammar("SingleIdentifierGrammar").copy(
        insert=[
            Ref("BackQuotedIdentifierSegment"),
        ]
    ),
    BinaryOperatorGrammar=OneOf(
        Ref("ArithmeticBinaryOperatorGrammar"),
        Ref("StringBinaryOperatorGrammar"),
        Ref("BooleanBinaryOperatorGrammar"),
        Ref("ComparisonOperatorGrammar"),
        # Add arrow operators for functions (e.g. filter)
        Ref("RightArrowOperator"),
    ),
    PostFunctionGrammar=ansi_dialect.get_grammar("PostFunctionGrammar").copy(
        # UNNEST can optionally have a WITH ORDINALITY clause
        insert=[
            Sequence("WITH", "ORDINALITY", optional=True),
        ]
    ),
)


class ArrayTypeSegment(ansi.ArrayTypeSegment):
    """Prefix for array literals specifying the type."""

    type = "array_type"
    match_grammar = Sequence(
        "ARRAY",
        Ref("ArrayTypeSchemaSegment", optional=True),
    )


class ArrayTypeSchemaSegment(ansi.ArrayTypeSegment):
    """Prefix for array literals specifying the type."""

    type = "array_type_schema"
    match_grammar = Bracketed(
        Ref("DatatypeSegment"),
        bracket_pairs_set="angle_bracket_pairs",
        bracket_type="angle",
    )


class MapTypeSegment(BaseSegment):
    """Expression to construct a MAP datatype."""

    type = "map_type"
    match_grammar = Sequence(
        "MAP",
        Ref("MapTypeSchemaSegment", optional=True),
    )


class MapTypeSchemaSegment(BaseSegment):
    """Expression to construct the schema of a MAP datatype."""

    type = "map_type_schema"
    match_grammar = Bracketed(
        Sequence(
            Ref("PrimitiveTypeSegment"),
            Ref("CommaSegment"),
            Ref("DatatypeSegment"),
        ),
        bracket_pairs_set="angle_bracket_pairs",
        bracket_type="angle",
    )


class StructTypeSegment(ansi.StructTypeSegment):
    """Expression to construct a STRUCT datatype."""

    match_grammar = Sequence(
        "STRUCT",
        Ref("StructTypeSchemaSegment", optional=True),
    )


class StructTypeSchemaSegment(BaseSegment):
    """Expression to construct the schema of a STRUCT datatype."""

    type = "struct_type_schema"
    match_grammar = Bracketed(
        Delimited(
            Sequence(
                Ref("NakedIdentifierSegment"),
                Ref("ColonSegment"),
                Ref("DatatypeSegment"),
                Ref("CommentGrammar", optional=True),
            ),
            bracket_pairs_set="angle_bracket_pairs",
        ),
        bracket_pairs_set="angle_bracket_pairs",
        bracket_type="angle",
    )


class PrimitiveTypeSegment(BaseSegment):
    """Support Athena subset of Hive types.

    Primary Source: https://docs.aws.amazon.com/athena/latest/ug/data-types.html
    Additional Details:
        https://cwiki.apache.org/confluence/display/Hive/LanguageManual+Types
    """

    type = "primitive_type"
    match_grammar = OneOf(
        "BOOLEAN",
        "TINYINT",
        "SMALLINT",
        "INTEGER",  # used in DML queries
        "INT",  # used in DDL queries
        "BIGINT",
        "DOUBLE",
        "FLOAT",  # used in DDL
        "REAL",  # used "in SQL functions like SELECT CAST"
        Sequence(
            OneOf("DECIMAL", "CHAR", "VARCHAR"),
            Ref("BracketedArguments", optional=True),
        ),
        "STRING",
        "BINARY",
        "DATE",
        "TIMESTAMP",
        "VARBINARY",
        "JSON",
        "TIME",
        "IPADDRESS",
        "HyperLogLog",
        "P4HyperLogLog",
    )


class DatatypeSegment(BaseSegment):
    """Support complex Athena data types.

    Complex data types are typically used in either DDL statements or as
    the target type in casts.
    """

    type = "data_type"
    match_grammar = OneOf(
        Ref("PrimitiveTypeSegment"),
        Ref("StructTypeSegment"),
        Ref("ArrayTypeSegment"),
        Ref("MapTypeSegment"),
        Sequence(
            "ROW",
            Bracketed(
                Delimited(
                    AnyNumberOf(
                        Sequence(
                            Ref("NakedIdentifierSegment"),
                            Ref("DatatypeSegment"),
                        ),
                        Ref("LiteralGrammar"),
                    )
                )
            ),
        ),
        Ref("DatetimeWithTZSegment"),
    )


class StatementSegment(ansi.StatementSegment):
    """Overriding StatementSegment to allow for additional segment parsing."""

    match_grammar = ansi.StatementSegment.match_grammar.copy(
        insert=[
            Ref("MsckRepairTableStatementSegment"),
            Ref("UnloadStatementSegment"),
            Ref("PrepareStatementSegment"),
            Ref("ExecuteStatementSegment"),
            Ref("ShowStatementSegment"),
        ],
        remove=[
            Ref("TransactionStatementSegment"),
            Ref("CreateSchemaStatementSegment"),
            Ref("SetSchemaStatementSegment"),
            Ref("CreateModelStatementSegment"),
            Ref("DropModelStatementSegment"),
        ],
    )


class CreateTableStatementSegment(BaseSegment):
    """A `CREATE TABLE` statement.

    Inspired on Hive Dialect with adjustments based on:
    https://docs.aws.amazon.com/pt_br/athena/latest/ug/create-table.html
    """

    type = "create_table_statement"
    match_grammar = Sequence(
        "CREATE",
        Ref.keyword("EXTERNAL", optional=True),
        "TABLE",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        OneOf(
            # Columns and comment syntax:
            Sequence(
                Bracketed(
                    Delimited(
                        OneOf(
                            Ref("TableConstraintSegment", optional=True),
                            Sequence(
                                Ref("ColumnDefinitionSegment"),
                                Ref("CommentGrammar", optional=True),
                            ),
                        ),
                        bracket_pairs_set="angle_bracket_pairs",
                    ),
                    optional=True,
                ),
                Ref("CommentGrammar", optional=True),
                # `STORED AS` can be called before or after the additional table
                # properties below
                Ref("StoredAsGrammar", optional=True),
                Sequence(
                    "PARTITIONED",
                    "BY",
                    Bracketed(
                        Delimited(
                            Sequence(
                                Ref("ColumnDefinitionSegment"),
                                Ref("CommentGrammar", optional=True),
                            ),
                        ),
                    ),
                    optional=True,
                ),
                Sequence(
                    "CLUSTERED",
                    "BY",
                    Ref("BracketedColumnReferenceListGrammar"),
                    "INTO",
                    Ref("NumericLiteralSegment"),
                    "BUCKETS",
                    optional=True,
                ),
                # Second call of `STORED AS` to match when appears after
                Ref("StoredAsGrammar", optional=True),
                Ref("StorageFormatGrammar", optional=True),
                Ref("LocationGrammar", optional=True),
                Ref("TablePropertiesGrammar", optional=True),
                Ref("CommentGrammar", optional=True),
            ),
            Sequence(
                Sequence("WITH", Ref("BracketedCTASPropertyGrammar"), optional=True),
                "AS",
                OptionallyBracketed(
                    Ref("SelectableGrammar"),
                ),
                Sequence("WITH", "NO", "DATA", optional=True),
            ),
        ),
    )


class MsckRepairTableStatementSegment(BaseSegment):
    """An `MSCK REPAIR TABLE` statement.

    The `MSCK REPAIR TABLE` command scans a file system such as Amazon S3 for
    Hive compatible partitions that were added to the file system after the
    table was created.

    https://docs.aws.amazon.com/athena/latest/ug/msck-repair-table.html
    """

    type = "msck_repair_table_statement"

    match_grammar = Sequence(
        "MSCK",
        "REPAIR",
        "TABLE",
        Ref("TableReferenceSegment"),
    )


class RowFormatClauseSegment(BaseSegment):
    """`ROW FORMAT` clause in a CREATE statement."""

    type = "row_format_clause"
    match_grammar = Sequence(
        "ROW",
        "FORMAT",
        OneOf(
            Sequence(
                "DELIMITED",
                Sequence(
                    "FIELDS",
                    Ref("TerminatedByGrammar"),
                    Sequence(
                        "ESCAPED", "BY", Ref("QuotedLiteralSegment"), optional=True
                    ),
                    optional=True,
                ),
                Sequence(
                    "COLLECTION", "ITEMS", Ref("TerminatedByGrammar"), optional=True
                ),
                Sequence("MAP", "KEYS", Ref("TerminatedByGrammar"), optional=True),
                Sequence("LINES", Ref("TerminatedByGrammar"), optional=True),
                Sequence(
                    "NULL", "DEFINED", "AS", Ref("QuotedLiteralSegment"), optional=True
                ),
            ),
            Sequence(
                "SERDE",
                Ref("QuotedLiteralSegment"),
                Ref("SerdePropertiesGrammar", optional=True),
            ),
        ),
    )


class InsertStatementSegment(BaseSegment):
    """`INSERT INTO` statement.

    https://docs.aws.amazon.com/athena/latest/ug/insert-into.html
    """

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


class UnloadStatementSegment(BaseSegment):
    """An `UNLOAD` statement.

    https://docs.aws.amazon.com/redshift/latest/dg/r_UNLOAD.html
    """

    type = "unload_statement"

    match_grammar = Sequence(
        "UNLOAD",
        Bracketed(Ref("SelectableGrammar")),
        "TO",
        Ref("QuotedLiteralSegment"),
        Sequence("WITH", Ref("BracketedUnloadPropertyGrammar"), optional=True),
    )


class PrepareStatementSegment(BaseSegment):
    """A `prepare` statement.

    https://docs.aws.amazon.com/athena/latest/ug/querying-with-prepared-statements.html
    """

    type = "prepare_statement"
    match_grammar = Sequence(
        "PREPARE",
        Ref("TableReferenceSegment"),
        "FROM",
        OptionallyBracketed(
            OneOf(
                Ref("SelectableGrammar"),
                Ref("UnloadStatementSegment"),
                Ref("InsertStatementSegment"),
            ),
        ),
    )


class ExecuteStatementSegment(BaseSegment):
    """An `execute` statement.

    https://docs.aws.amazon.com/athena/latest/ug/querying-with-prepared-statements.html
    """

    type = "execute_statement"
    match_grammar = Sequence(
        "EXECUTE",
        Ref("TableReferenceSegment"),
        OneOf(
            Sequence(
                "USING",
                Delimited(
                    Ref("LiteralGrammar"),
                ),
            ),
            optional=True,
        ),
    )


class IntervalExpressionSegment(BaseSegment):
    """An interval expression segment.

    Full Apache Hive `INTERVAL` reference here:
    https://cwiki.apache.org/confluence/display/hive/languagemanual+types#LanguageManualTypes-Intervals
    """

    type = "interval_expression"
    match_grammar = Sequence(
        Ref.keyword("INTERVAL", optional=True),
        OneOf(
            Sequence(
                OneOf(
                    Ref("QuotedLiteralSegment"),
                    Ref("NumericLiteralSegment"),
                    Bracketed(Ref("ExpressionSegment")),
                ),
                Ref("DatetimeUnitSegment"),
                Sequence("TO", Ref("DatetimeUnitSegment"), optional=True),
            ),
        ),
    )


class GroupByClauseSegment(ansi.GroupByClauseSegment):
    """A `GROUP BY` clause like in `SELECT`.

    https://docs.aws.amazon.com/athena/latest/ug/select.html#:~:text=%5B-,GROUP,-BY%20%5B%20ALL%20%7C%20DISTINCT%20%5D%20grouping_expressions
    """

    match_grammar: Matchable = Sequence(
        "GROUP",
        "BY",
        Indent,
        Delimited(
            OneOf(
                Ref("CubeRollupClauseSegment"),
                Ref("GroupingSetsClauseSegment"),
                Ref("ColumnReferenceSegment"),
                Ref("NumericLiteralSegment"),  # Can `GROUP BY 1`
                Ref("ExpressionSegment"),  # Can `GROUP BY coalesce(col, 1)`
            ),
            terminators=[
                Sequence("ORDER", "BY"),
                "LIMIT",
                "OFFSET",
                "HAVING",
                Ref("SetOperatorSegment"),
            ],
        ),
        Dedent,
    )


class ShowStatementSegment(BaseSegment):
    """A `show` execute statement.

    Full Apache Hive `SHOW` reference:
    https://cwiki.apache.org/confluence/display/Hive/LanguageManual+DDL#LanguageManualDDL-Show

    Athena supported subset:
    https://docs.aws.amazon.com/athena/latest/ug/ddl-reference.html
    """

    type = "show_statement"
    match_grammar = Sequence(
        "SHOW",
        OneOf(
            Sequence(
                "COLUMNS",
                OneOf("FROM", "IN"),
                OneOf(
                    Sequence(
                        Ref("DatabaseReferenceSegment"), Ref("TableReferenceSegment")
                    ),
                    Sequence(
                        Ref("TableReferenceSegment"),
                        Sequence(
                            OneOf("FROM", "IN"),
                            Ref("DatabaseReferenceSegment"),
                            optional=True,
                        ),
                    ),
                ),
            ),
            Sequence(
                "CREATE",
                OneOf("TABLE", "VIEW"),
                Ref("TableReferenceSegment"),
            ),
            Sequence(
                OneOf("DATABASES", "SCHEMAS"),
                Sequence("LIKE", Ref("QuotedLiteralSegment"), optional=True),
            ),
            Sequence(
                "PARTITIONS",
                Ref("TableReferenceSegment"),
            ),
            Sequence(
                "TABLES",
                Sequence("IN", Ref("DatabaseReferenceSegment"), optional=True),
                Ref("QuotedLiteralSegment", optional=True),
            ),
            Sequence(
                "TBLPROPERTIES",
                Ref("TableReferenceSegment"),
                Bracketed(Ref("QuotedLiteralSegment"), optional=True),
            ),
            Sequence(
                "VIEWS",
                Sequence("IN", Ref("DatabaseReferenceSegment"), optional=True),
                Sequence("LIKE", Ref("QuotedLiteralSegment"), optional=True),
            ),
        ),
    )
