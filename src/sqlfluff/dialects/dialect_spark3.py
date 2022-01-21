"""The Spark SQL dialect for ANSI Compliant Spark3.

Inherits from ANSI.
Spark SQL ANSI Mode is more restrictive regarding
keywords than the Default Mode, and still shares
some syntax with hive.

Based on:
https://spark.apache.org/docs/latest/sql-ref.html
https://spark.apache.org/docs/latest/sql-ref-ansi-compliance.html
https://github.com/apache/spark/blob/master/sql/catalyst/src/main/antlr4/org/apache/spark/sql/catalyst/parser/SqlBase.g4
"""

from sqlfluff.core.parser import (
    AnyNumberOf,
    BaseSegment,
    Bracketed,
    CommentSegment,
    Conditional,
    Dedent,
    Delimited,
    Indent,
    NamedParser,
    OneOf,
    OptionallyBracketed,
    Ref,
    RegexLexer,
    Sequence,
    StringParser,
    SymbolSegment,
    Anything,
)

from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.core.parser.segments.raw import CodeSegment, KeywordSegment
from sqlfluff.dialects.dialect_spark3_keywords import (
    RESERVED_KEYWORDS,
    UNRESERVED_KEYWORDS,
)

ansi_dialect = load_raw_dialect("ansi")
hive_dialect = load_raw_dialect("hive")
spark3_dialect = ansi_dialect.copy_as("spark3")

spark3_dialect.patch_lexer_matchers(
    [
        # Spark SQL, only -- is used for single-line comment
        RegexLexer(
            "inline_comment",
            r"(--)[^\n]*",
            CommentSegment,
            segment_kwargs={"trim_start": "--"},
        ),
        # == and <=> are valid equal operations
        # <=> is a non-null equals in Spark SQL
        # https://spark.apache.org/docs/latest/api/sql/index.html#_10
        RegexLexer("equals", r"=|==|<=>", CodeSegment),
        # identifiers are delimited with `
        # within a delimited identifier, ` is used to escape special characters,
        # including `
        # Ex: select `delimited `` with escaped` from `just delimited`
        # https://spark.apache.org/docs/latest/sql-ref-identifier.html#delimited-identifier
        RegexLexer("back_quote", r"`([^`]|``)*`", CodeSegment),
        # Numeric literal matches integers, decimals, and exponential formats.
        # https://spark.apache.org/docs/latest/sql-ref-literals.html#numeric-literal
        # Pattern breakdown:
        # (?>                                    Atomic grouping
        #                           (https://www.regular-expressions.info/atomic.html).
        #                                        3 distinct groups here:
        #                                        1. Obvious fractional types
        #                                           (can optionally be exponential).
        #                                        2. Integer followed by exponential.
        #                                           These must be fractional types.
        #                                        3. Integer only.
        #                                           These can either be integral or
        #                                           fractional types.
        #
        #     (?>                                1.
        #         \d+\.\d+                       e.g. 123.456
        #         |\d+\.                         e.g. 123.
        #         |\.\d+                         e.g. .123
        #     )
        #     ([eE][+-]?\d+)?                    Optional exponential.
        #     ([dDfF]|BD|bd)?                    Fractional data types.
        #     |\d+[eE][+-]?\d+([dDfF]|BD|bd)?    2. Integer + exponential with
        #                                           fractional data types.
        #     |\d+([dDfFlLsSyY]|BD|bd)?          3. Integer only with integral or
        #                                           fractional data types.
        # )
        # (
        #     (?<=\.)                            If matched character ends with .
        #                                        (e.g. 123.) then don't worry about
        #                                        word boundary check.
        #     |(?=\b)                            Check that we are at word boundary to
        #                                        avoid matching valid naked identifiers
        #                                        (e.g. 123column).
        # )
        RegexLexer(
            "numeric_literal",
            (
                r"(?>(?>\d+\.\d+|\d+\.|\.\d+)([eE][+-]?\d+)?([dDfF]|BD|bd)?"
                r"|\d+[eE][+-]?\d+([dDfF]|BD|bd)?"
                r"|\d+([dDfFlLsSyY]|BD|bd)?)"
                r"((?<=\.)|(?=\b))"
            ),
            CodeSegment,
        ),
    ]
)

spark3_dialect.insert_lexer_matchers(
    [
        RegexLexer("bytes_single_quote", r"X'([^'\\]|\\.)*'", CodeSegment),
        RegexLexer("bytes_double_quote", r'X"([^"\\]|\\.)*"', CodeSegment),
    ],
    before="single_quote",
)

# Set the bare functions
spark3_dialect.sets("bare_functions").clear()
spark3_dialect.sets("bare_functions").update(
    [
        "CURRENT_DATE",
        "CURRENT_TIMESTAMP",
        "CURRENT_USER",
    ]
)

# Set the datetime units
spark3_dialect.sets("datetime_units").clear()
spark3_dialect.sets("datetime_units").update(
    [
        "YEAR",
        # Alternate syntax for YEAR
        "YYYY",
        "YY",
        "QUARTER",
        "MONTH",
        # Alternate syntax for MONTH
        "MON",
        "MM",
        "WEEK",
        "DAY",
        # Alternate syntax for DAY
        "DD",
        "HOUR",
        "MINUTE",
        "SECOND",
    ]
)

# Set Keywords
spark3_dialect.sets("unreserved_keywords").update(UNRESERVED_KEYWORDS)
spark3_dialect.sets("reserved_keywords").update(RESERVED_KEYWORDS)

# Set Angle Bracket Pairs
spark3_dialect.sets("angle_bracket_pairs").update(
    [
        ("angle", "StartAngleBracketSegment", "EndAngleBracketSegment", False),
    ]
)

# Real Segments
spark3_dialect.replace(
    ComparisonOperatorGrammar=OneOf(
        Ref("EqualsSegment"),
        Ref("EqualsSegment_a"),
        Ref("EqualsSegment_b"),
        Ref("GreaterThanSegment"),
        Ref("LessThanSegment"),
        Ref("GreaterThanOrEqualToSegment"),
        Ref("LessThanOrEqualToSegment"),
        Ref("NotEqualToSegment"),
        Ref("LikeOperatorSegment"),
    ),
    TemporaryGrammar=Sequence(
        Sequence("GLOBAL", optional=True),
        OneOf("TEMP", "TEMPORARY"),
    ),
    QuotedIdentifierSegment=NamedParser(
        "back_quote",
        CodeSegment,
        name="quoted_identifier",
        type="identifier",
        trim_chars=("`",),
    ),
    QuotedLiteralSegment=hive_dialect.get_grammar("QuotedLiteralSegment"),
    LiteralGrammar=ansi_dialect.get_grammar("LiteralGrammar").copy(
        insert=[
            Ref("BytesQuotedLiteralSegment"),
        ]
    ),
)

spark3_dialect.add(
    # Add Hive Segments TODO : Is there a way to retrieve this w/o redefining?
    JsonfileKeywordSegment=StringParser(
        "JSONFILE",
        KeywordSegment,
        name="json_file",
        type="file_format",
    ),
    RcfileKeywordSegment=StringParser(
        "RCFILE", KeywordSegment, name="rc_file", type="file_format"
    ),
    SequencefileKeywordSegment=StringParser(
        "SEQUENCEFILE", KeywordSegment, name="sequence_file", type="file_format"
    ),
    TextfileKeywordSegment=StringParser(
        "TEXTFILE", KeywordSegment, name="text_file", type="file_format"
    ),
    StartAngleBracketSegment=StringParser(
        "<", SymbolSegment, name="start_angle_bracket", type="start_angle_bracket"
    ),
    EndAngleBracketSegment=StringParser(
        ">", SymbolSegment, name="end_angle_bracket", type="end_angle_bracket"
    ),
    # Add Spark Segments
    EqualsSegment_a=StringParser(
        "==", SymbolSegment, name="equals", type="comparison_operator"
    ),
    EqualsSegment_b=StringParser(
        "<=>", SymbolSegment, name="equals", type="comparison_operator"
    ),
    FileKeywordSegment=StringParser(
        "FILE", KeywordSegment, name="file", type="file_type"
    ),
    JarKeywordSegment=StringParser("JAR", KeywordSegment, name="jar", type="file_type"),
    WhlKeywordSegment=StringParser("WHL", KeywordSegment, name="whl", type="file_type"),
    # Add relevant Hive Grammar
    BracketedPropertyListGrammar=hive_dialect.get_grammar(
        "BracketedPropertyListGrammar"
    ),
    CommentGrammar=hive_dialect.get_grammar("CommentGrammar"),
    FileFormatGrammar=hive_dialect.get_grammar("FileFormatGrammar"),
    LocationGrammar=hive_dialect.get_grammar("LocationGrammar"),
    PropertyGrammar=hive_dialect.get_grammar("PropertyGrammar"),
    SerdePropertiesGrammar=hive_dialect.get_grammar("SerdePropertiesGrammar"),
    StoredAsGrammar=hive_dialect.get_grammar("StoredAsGrammar"),
    StoredByGrammar=hive_dialect.get_grammar("StoredByGrammar"),
    StorageFormatGrammar=hive_dialect.get_grammar("StorageFormatGrammar"),
    TerminatedByGrammar=hive_dialect.get_grammar("TerminatedByGrammar"),
    # Add Spark Grammar
    BucketSpecGrammar=Sequence(
        Ref("ClusterSpecGrammar"),
        Ref("SortSpecGrammar", optional=True),
        "INTO",
        Ref("NumericLiteralSegment"),
        "BUCKETS",
    ),
    ClusterSpecGrammar=Sequence(
        "CLUSTERED",
        "BY",
        Ref("BracketedColumnReferenceListGrammar"),
    ),
    DatabasePropertiesGrammar=Sequence(
        "DBPROPERTIES", Ref("BracketedPropertyListGrammar")
    ),
    DataSourceFormatGrammar=OneOf(
        # Spark Core Data Sources
        # https://spark.apache.org/docs/latest/sql-data-sources.html
        "AVRO",
        "CSV",
        "JSON",
        "PARQUET",
        "ORC",
        "JDBC",
        # Community Contributed Data Sources
        "DELTA",  # https://github.com/delta-io/delta
        "XML",  # https://github.com/databricks/spark-xml
    ),
    PartitionSpecGrammar=Sequence(
        OneOf("PARTITION", Sequence("PARTITIONED", "BY")),
        Bracketed(
            Delimited(
                Sequence(
                    Ref("ColumnReferenceSegment"),
                    Ref("EqualsSegment", optional=True),
                    Ref("LiteralGrammar", optional=True),
                    Ref("CommentGrammar", optional=True),
                ),
            ),
        ),
    ),
    ResourceFileGrammar=OneOf(
        Ref("JarKeywordSegment"),
        Ref("WhlKeywordSegment"),
        Ref("FileKeywordSegment"),
    ),
    ResourceLocationGrammar=Sequence(
        "USING",
        Ref("ResourceFileGrammar"),
        Ref("QuotedLiteralSegment"),
    ),
    SortSpecGrammar=Sequence(
        "SORTED",
        "BY",
        Bracketed(
            Delimited(
                Sequence(
                    Ref("ColumnReferenceSegment"),
                    OneOf("ASC", "DESC", optional=True),
                )
            )
        ),
        optional=True,
    ),
    UnsetTablePropertiesGrammar=Sequence(
        "UNSET",
        "TBLPROPERTIES",
        Ref("IfExistsGrammar", optional=True),
        Bracketed(Delimited(Ref("QuotedLiteralSegment"))),
    ),
    TablePropertiesGrammar=Sequence(
        "TBLPROPERTIES", Ref("BracketedPropertyListGrammar")
    ),
    BytesQuotedLiteralSegment=OneOf(
        NamedParser(
            "bytes_single_quote",
            CodeSegment,
            name="bytes_quoted_literal",
            type="literal",
        ),
        NamedParser(
            "bytes_double_quote",
            CodeSegment,
            name="bytes_quoted_literal",
            type="literal",
        ),
    ),
)


# Hive Segments
@spark3_dialect.segment()
class RowFormatClauseSegment(
    hive_dialect.get_segment("RowFormatClauseSegment")  # type: ignore
):
    """`ROW FORMAT` clause in a CREATE HIVEFORMAT TABLE statement."""

    type = "row_format_clause"


@spark3_dialect.segment()
class SkewedByClauseSegment(
    hive_dialect.get_segment("SkewedByClauseSegment")  # type: ignore
):
    """`SKEWED BY` clause in a CREATE HIVEFORMAT TABLE statement."""

    type = "skewed_by_clause"


# Primitive Data Types
@spark3_dialect.segment()
class PrimitiveTypeSegment(BaseSegment):
    """Spark SQL Primitive data types.

    https://spark.apache.org/docs/latest/sql-ref-datatypes.html
    """

    type = "primitive_type"
    match_grammar = OneOf(
        "BOOLEAN",
        # TODO : not currently supported; add segment - see NumericLiteralSegment
        # "BYTE",
        "TINYINT",
        # TODO : not currently supported; add segment - see NumericLiteralSegment
        # "SHORT",
        "SMALLINT",
        "INT",
        "BIGINT",
        "FLOAT",
        "REAL",
        "DOUBLE",
        "DATE",
        "TIMESTAMP",
        "STRING",
        Sequence(
            OneOf("CHAR", "CHARACTER", "VARCHAR"),
            Bracketed(Ref("NumericLiteralSegment"), optional=True),
        ),
        "BINARY",
        Sequence(
            OneOf("DECIMAL", "DEC", "NUMERIC"),
            Bracketed(
                Ref("NumericLiteralSegment"),
                Ref("CommaSegment"),
                Ref("NumericLiteralSegment"),
                optional=True,
            ),
        ),
        "INTERVAL",
    )


@spark3_dialect.segment(replace=True)
class DatatypeSegment(PrimitiveTypeSegment):
    """Spark SQL Data types.

    https://spark.apache.org/docs/latest/sql-ref-datatypes.html
    """

    type = "data_type"
    match_grammar = OneOf(
        Ref("PrimitiveTypeSegment"),
        Sequence(
            "ARRAY",
            Bracketed(
                Ref("DatatypeSegment"),
                bracket_pairs_set="angle_bracket_pairs",
                bracket_type="angle",
            ),
        ),
        Sequence(
            "MAP",
            Bracketed(
                Sequence(
                    Ref("PrimitiveTypeSegment"),
                    Ref("CommaSegment"),
                    Ref("DatatypeSegment"),
                ),
                bracket_pairs_set="angle_bracket_pairs",
                bracket_type="angle",
            ),
        ),
        Sequence(
            "STRUCT",
            Bracketed(
                Delimited(
                    Sequence(
                        Ref("NakedIdentifierSegment"),
                        Ref("ColonSegment"),
                        Ref("DatatypeSegment"),
                        Ref("CommentGrammar", optional=True),
                    ),
                ),
                bracket_pairs_set="angle_bracket_pairs",
                bracket_type="angle",
            ),
        ),
    )


# Data Definition Statements
# http://spark.apache.org/docs/latest/sql-ref-syntax-ddl.html
@spark3_dialect.segment()
class AlterDatabaseStatementSegment(BaseSegment):
    """An `ALTER DATABASE/SCHEMA` statement.

    http://spark.apache.org/docs/latest/sql-ref-syntax-ddl-alter-database.html
    """

    type = "alter_database_statement"

    match_grammar = Sequence(
        "ALTER",
        OneOf("DATABASE", "SCHEMA"),
        Ref("DatabaseReferenceSegment"),
        "SET",
        Ref("DatabasePropertiesGrammar"),
    )


@spark3_dialect.segment(replace=True)
class AlterTableStatementSegment(BaseSegment):
    """A `ALTER TABLE` statement to change the table schema or properties.

    http://spark.apache.org/docs/latest/sql-ref-syntax-ddl-alter-table.html
    """

    type = "alter_table_statement"

    match_grammar = Sequence(
        "ALTER",
        "TABLE",
        Ref("TableReferenceSegment"),
        OneOf(
            # ALTER TABLE - RENAME TO `table_identifier`
            Sequence(
                "RENAME",
                "TO",
                Ref("TableReferenceSegment"),
            ),
            # ALTER TABLE - RENAME `partition_spec`
            Sequence(
                Ref("PartitionSpecGrammar"),
                "RENAME",
                "TO",
                Ref("PartitionSpecGrammar"),
            ),
            # ALTER TABLE - ADD COLUMNS
            Sequence(
                "ADD",
                "COLUMNS",
                Bracketed(
                    Delimited(
                        Ref("ColumnDefinitionSegment"),
                    ),
                ),
            ),
            # ALTER TABLE - ALTER OR CHANGE COLUMN
            Sequence(
                OneOf("ALTER", "CHANGE"),
                "COLUMN",
                Ref("ColumnReferenceSegment"),
                Sequence("TYPE", Ref("DatatypeSegment"), optional=True),
                Ref("CommentGrammar", optional=True),
                OneOf(
                    "FIRST",
                    Sequence("AFTER", Ref("ColumnReferenceSegment")),
                    optional=True,
                ),
                Sequence(OneOf("SET", "DROP"), "NOT NULL", optional=True),
            ),
            # ALTER TABLE - ADD PARTITION
            Sequence(
                "ADD",
                Ref("IfNotExistsGrammar", optional=True),
                AnyNumberOf(Ref("PartitionSpecGrammar")),
            ),
            # ALTER TABLE - DROP PARTITION
            Sequence(
                "DROP",
                Ref("IfExistsGrammar", optional=True),
                Ref("PartitionSpecGrammar"),
                Sequence("PURGE", optional=True),
            ),
            # ALTER TABLE - REPAIR PARTITION
            Sequence("RECOVER", "PARTITIONS"),
            # ALTER TABLE - SET PROPERTIES
            Sequence("SET", Ref("TablePropertiesGrammar")),
            # ALTER TABLE - UNSET PROPERTIES
            Ref("UnsetTablePropertiesGrammar"),
            # ALTER TABLE - SET SERDE
            Sequence(
                Ref("PartitionSpecGrammar", optional=True),
                "SET",
                OneOf(
                    Sequence(
                        "SERDEPROPERTIES",
                        Ref("BracketedPropertyListGrammar"),
                    ),
                    Sequence(
                        "SERDE",
                        Ref("QuotedLiteralSegment"),
                        Ref("SerdePropertiesGrammar", optional=True),
                    ),
                ),
            ),
            # ALTER TABLE - SET FILE FORMAT
            Sequence(
                Ref("PartitionSpecGrammar", optional=True),
                "SET",
                "FILEFORMAT",
                Ref("DataSourceFormatGrammar"),
            ),
            # ALTER TABLE - CHANGE FILE LOCATION
            Sequence(
                Ref("PartitionSpecGrammar"),
                "SET",
                Ref("LocationGrammar"),
            ),
        ),
    )


@spark3_dialect.segment()
class AlterViewStatementSegment(BaseSegment):
    """A `ALTER VIEW` statement to change the view schema or properties.

    https://spark.apache.org/docs/latest/sql-ref-syntax-ddl-alter-view.html
    """

    type = "alter_view_statement"

    match_grammar = Sequence(
        "ALTER",
        "VIEW",
        Ref("TableReferenceSegment"),
        OneOf(
            Sequence(
                "RENAME",
                "TO",
                Ref("TableReferenceSegment"),
            ),
            Sequence("SET", Ref("TablePropertiesGrammar")),
            Ref("UnsetTablePropertiesGrammar"),
            Sequence(
                "AS",
                OptionallyBracketed(Ref("SelectStatementSegment")),
            ),
        ),
    )


@spark3_dialect.segment(replace=True)
class CreateDatabaseStatementSegment(BaseSegment):
    """A `CREATE DATABASE` statement.

    https://spark.apache.org/docs/latest/sql-ref-syntax-ddl-create-database.html
    """

    type = "create_database_statement"
    match_grammar = Sequence(
        "CREATE",
        OneOf("DATABASE", "SCHEMA"),
        Ref("IfNotExistsGrammar", optional=True),
        Ref("DatabaseReferenceSegment"),
        Ref("CommentGrammar", optional=True),
        Ref("LocationGrammar", optional=True),
        Sequence(
            "WITH", "DBPROPERTIES", Ref("BracketedPropertyListGrammar"), optional=True
        ),
    )


@spark3_dialect.segment(replace=True)
class CreateFunctionStatementSegment(BaseSegment):
    """A `CREATE FUNCTION` statement.

    https://spark.apache.org/docs/latest/sql-ref-syntax-ddl-create-function.html
    """

    type = "create_function_statement"

    match_grammar = Sequence(
        "CREATE",
        Sequence("OR", "REPLACE", optional=True),
        Ref("TemporaryGrammar", optional=True),
        "FUNCTION",
        Anything(),
    )

    parse_grammar = Sequence(
        "CREATE",
        Sequence("OR", "REPLACE", optional=True),
        Ref("TemporaryGrammar", optional=True),
        "FUNCTION",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("FunctionNameIdentifierSegment"),
        "AS",
        Ref("QuotedLiteralSegment"),
        Ref("ResourceLocationGrammar", optional=True),
    )


@spark3_dialect.segment(replace=True)
class CreateTableStatementSegment(BaseSegment):
    """A `CREATE TABLE` statement using a Data Source or Like.

    http://spark.apache.org/docs/latest/sql-ref-syntax-ddl-create-table-datasource.html
    https://spark.apache.org/docs/latest/sql-ref-syntax-ddl-create-table-like.html
    """

    type = "create_table_statement"

    match_grammar = Sequence(
        "CREATE",
        "TABLE",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        OneOf(
            # Columns and comment syntax:
            Sequence(
                Bracketed(
                    Delimited(
                        Sequence(
                            Ref("ColumnDefinitionSegment"),
                            Ref("CommentGrammar", optional=True),
                        ),
                    ),
                ),
            ),
            # Like Syntax
            Sequence(
                "LIKE",
                Ref("TableReferenceSegment"),
            ),
            optional=True,
        ),
        Sequence("USING", Ref("DataSourceFormatGrammar"), optional=True),
        Ref("RowFormatClauseSegment", optional=True),
        Ref("StoredAsGrammar", optional=True),
        Sequence("OPTIONS", Ref("BracketedPropertyListGrammar"), optional=True),
        Ref("PartitionSpecGrammar", optional=True),
        Ref("BucketSpecGrammar", optional=True),
        AnyNumberOf(
            Ref("LocationGrammar", optional=True),
            Ref("CommentGrammar", optional=True),
            Ref("TablePropertiesGrammar", optional=True),
        ),
        # Create AS syntax:
        Sequence(
            "AS",
            OptionallyBracketed(Ref("SelectableGrammar")),
            optional=True,
        ),
    )


@spark3_dialect.segment()
class CreateHiveFormatTableStatementSegment(
    hive_dialect.get_segment("CreateTableStatementSegment")  # type: ignore
):
    """A `CREATE TABLE` statement using Hive format.

    https://spark.apache.org/docs/latest/sql-ref-syntax-ddl-create-table-hiveformat.html
    """

    type = "create_table_statement"


@spark3_dialect.segment(replace=True)
class CreateViewStatementSegment(BaseSegment):
    """A `CREATE VIEW` statement.

    https://spark.apache.org/docs/3.0.0/sql-ref-syntax-ddl-create-view.html#syntax
    """

    type = "create_view_statement"

    match_grammar = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        Ref("TemporaryGrammar", optional=True),
        "VIEW",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        # Columns and comment syntax:
        Sequence(
            Bracketed(
                Delimited(
                    Sequence(
                        Ref("ColumnReferenceSegment"),
                        Ref("CommentGrammar", optional=True),
                    ),
                ),
            ),
            optional=True,
        ),
        Ref("CommentGrammar", optional=True),
        Ref("TablePropertiesGrammar", optional=True),
        "AS",
        Ref("SelectableGrammar"),
        Ref("WithNoSchemaBindingClauseSegment", optional=True),
    )


@spark3_dialect.segment()
class DropFunctionStatementSegment(BaseSegment):
    """A `DROP FUNCTION` STATEMENT.

    https://spark.apache.org/docs/latest/sql-ref-syntax-ddl-drop-function.html
    """

    type = "drop_function_statement"

    match_grammar = Sequence(
        "DROP",
        Ref("TemporaryGrammar", optional=True),
        "FUNCTION",
        Ref("IfExistsGrammar", optional=True),
        Ref("FunctionNameSegment"),
    )


@spark3_dialect.segment()
class MsckRepairTableStatementSegment(
    hive_dialect.get_segment("MsckRepairTableStatementSegment")  # type: ignore
):
    """A `REPAIR TABLE` statement using Hive MSCK (Metastore Check) format.

    This class inherits from Hive since Spark leverages Hive format for this command and
    is dependent on the Hive metastore.

    https://spark.apache.org/docs/latest/sql-ref-syntax-ddl-repair-table.html
    """

    type = "msck_repair_table_statement"


@spark3_dialect.segment(replace=True)
class TruncateStatementSegment(BaseSegment):
    """A `TRUNCATE TABLE` statement.

    https://spark.apache.org/docs/latest/sql-ref-syntax-ddl-truncate-table.html
    """

    type = "truncate_table_statement"

    match_grammar = Sequence(
        "TRUNCATE",
        "TABLE",
        Ref("TableReferenceSegment"),
        Ref("PartitionSpecGrammar", optional=True),
    )


@spark3_dialect.segment()
class UseDatabaseStatementSegment(BaseSegment):
    """A `USE DATABASE` statement.

    https://spark.apache.org/docs/latest/sql-ref-syntax-ddl-usedb.html
    """

    type = "use_database_statement"

    match_grammar = Sequence(
        "USE",
        Ref("DatabaseReferenceSegment"),
    )


# Data Manipulation Statements
@spark3_dialect.segment(replace=True)
class InsertStatementSegment(BaseSegment):
    """A `INSERT [TABLE]` statement to insert or overwrite new rows into a table.

    https://spark.apache.org/docs/latest/sql-ref-syntax-dml-insert-into.html
    https://spark.apache.org/docs/latest/sql-ref-syntax-dml-insert-overwrite-table.html
    """

    type = "insert_table_statement"

    match_grammar = Sequence(
        "INSERT",
        OneOf("INTO", "OVERWRITE"),
        Ref.keyword("TABLE", optional=True),
        Ref("TableReferenceSegment"),
        Ref("PartitionSpecGrammar", optional=True),
        Ref("BracketedColumnReferenceListGrammar", optional=True),
        OneOf(
            AnyNumberOf(
                Ref("ValuesClauseSegment"),
                min_times=1,
            ),
            Ref("SelectableGrammar"),
            Sequence(
                Ref.keyword("TABLE", optional=True),
                Ref("TableReferenceSegment"),
            ),
            Sequence(
                "FROM",
                Ref("TableReferenceSegment"),
                "SELECT",
                Delimited(
                    Ref("ColumnReferenceSegment"),
                ),
                Ref("WhereClauseSegment", optional=True),
                Ref("GroupByClauseSegment", optional=True),
                Ref("OrderByClauseSegment", optional=True),
                Ref("LimitClauseSegment", optional=True),
            ),
        ),
    )


@spark3_dialect.segment()
class InsertOverwriteDirectorySegment(BaseSegment):
    """An `INSERT OVERWRITE [LOCAL] DIRECTORY` statement.

    https://spark.apache.org/docs/latest/sql-ref-syntax-dml-insert-overwrite-directory.html
    """

    type = "insert_overwrite_directory_statement"

    match_grammar = Sequence(
        "INSERT",
        "OVERWRITE",
        Ref.keyword("LOCAL", optional=True),
        "DIRECTORY",
        Ref("QuotedLiteralSegment", optional=True),
        "USING",
        Ref("DataSourceFormatGrammar"),
        Sequence("OPTIONS", Ref("BracketedPropertyListGrammar"), optional=True),
        OneOf(
            AnyNumberOf(
                Ref("ValuesClauseSegment"),
                min_times=1,
            ),
            Ref("SelectableGrammar"),
        ),
    )


# Auxiliary Statements
@spark3_dialect.segment()
class AddExecutablePackage(BaseSegment):
    """A `ADD JAR` statement.

    https://spark.apache.org/docs/latest/sql-ref-syntax-aux-resource-mgmt-add-jar.html
    """

    type = "add_executable_package"

    match_grammar = Sequence(
        "ADD",
        Ref("ResourceFileGrammar"),
        Ref("QuotedLiteralSegment"),
    )


@spark3_dialect.segment()
class RefreshStatementSegment(BaseSegment):
    """A `REFRESH` statement for given data source path.

    https://spark.apache.org/docs/latest/sql-ref-syntax-aux-cache-refresh.html
    """

    type = "refresh_statement"

    match_grammar = Sequence(
        "REFRESH",
        Ref("QuotedLiteralSegment"),
    )


@spark3_dialect.segment()
class RefreshTableStatementSegment(BaseSegment):
    """A `REFRESH TABLE` statement.

    https://spark.apache.org/docs/latest/sql-ref-syntax-aux-cache-refresh-table.html
    """

    type = "refresh_table_statement"

    match_grammar = Sequence(
        "REFRESH",
        Ref.keyword("TABLE", optional=True),
        Ref("TableReferenceSegment"),
    )


@spark3_dialect.segment()
class RefreshFunctionStatementSegment(BaseSegment):
    """A `REFRESH FUNCTION` statement.

    https://spark.apache.org/docs/latest/sql-ref-syntax-aux-cache-refresh-function.html
    """

    type = "refresh_function_statement"

    match_grammar = Sequence(
        "REFRESH",
        "FUNCTION",
        Ref("FunctionNameSegment"),
    )


@spark3_dialect.segment(replace=True)
class StatementSegment(BaseSegment):
    """Overriding StatementSegment to allow for additional segment parsing."""

    match_grammar = ansi_dialect.get_segment("StatementSegment").match_grammar.copy()

    parse_grammar = ansi_dialect.get_segment("StatementSegment").parse_grammar.copy(
        # Segments defined in Spark3 dialect
        insert=[
            # Data Definition Statements
            Ref("AlterDatabaseStatementSegment"),
            Ref("AlterTableStatementSegment"),
            Ref("AlterViewStatementSegment"),
            Ref("CreateHiveFormatTableStatementSegment"),
            Ref("DropFunctionStatementSegment"),
            Ref("MsckRepairTableStatementSegment"),
            Ref("UseDatabaseStatementSegment"),
            # Auxiliary Statements
            Ref("AddExecutablePackage"),
            Ref("RefreshStatementSegment"),
            Ref("RefreshTableStatementSegment"),
            Ref("RefreshFunctionStatementSegment"),
            # Data Manipulation Statements
            Ref("InsertOverwriteDirectorySegment"),
        ],
        remove=[
            Ref("TransactionStatementSegment"),
            Ref("CreateSchemaStatementSegment"),
            Ref("SetSchemaStatementSegment"),
            Ref("CreateExtensionStatementSegment"),
            Ref("CreateModelStatementSegment"),
            Ref("DropModelStatementSegment"),
        ],
    )


@spark3_dialect.segment(replace=True)
class JoinClauseSegment(BaseSegment):
    """Any number of join clauses, including the `JOIN` keyword.

    https://spark.apache.org/docs/3.0.0/sql-ref-syntax-qry-select-join.html
    TODO: Add NATURAL JOIN syntax.
    """

    type = "join_clause"
    match_grammar = Sequence(
        # NB These qualifiers are optional
        # TODO: Allow nested joins like:
        # ....FROM S1.T1 t1 LEFT JOIN ( S2.T2 t2 JOIN S3.T3 t3 ON t2.col1=t3.col1) ON
        # tab1.col1 = tab2.col1
        OneOf(
            "CROSS",
            "INNER",
            Sequence(
                OneOf(
                    "FULL",
                    "LEFT",
                    "RIGHT",
                ),
                Ref.keyword("OUTER", optional=True),
            ),
            Sequence(
                Ref.keyword("LEFT", optional=True),
                "SEMI",
            ),
            Sequence(
                Ref.keyword("LEFT", optional=True),
                "ANTI",
            ),
            optional=True,
        ),
        Ref("JoinKeywords"),
        Indent,
        Sequence(
            Ref("FromExpressionElementSegment"),
            Conditional(Dedent, indented_using_on=False),
            # NB: this is optional
            OneOf(
                # ON clause
                Ref("JoinOnConditionSegment"),
                # USING clause
                Sequence(
                    "USING",
                    Indent,
                    Bracketed(
                        # NB: We don't use BracketedColumnReferenceListGrammar
                        # here because we're just using SingleIdentifierGrammar,
                        # rather than ObjectReferenceSegment or ColumnReferenceSegment.
                        # This is a) so that we don't lint it as a reference and
                        # b) because the column will probably be returned anyway
                        # during parsing.
                        Delimited(
                            Ref("SingleIdentifierGrammar"),
                            ephemeral_name="UsingClauseContents",
                        )
                    ),
                    Dedent,
                ),
                # Unqualified joins *are* allowed. They just might not
                # be a good idea.
                optional=True,
            ),
            Conditional(Indent, indented_using_on=False),
        ),
        Dedent,
    )

    get_eventual_alias = ansi_dialect.get_segment(
        "JoinClauseSegment"
    ).get_eventual_alias
