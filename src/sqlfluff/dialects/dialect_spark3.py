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

from sqlfluff.core.dialects import load_raw_dialect
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
    StartsWith,
)
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
    FromClauseTerminatorGrammar=OneOf(
        "WHERE",
        "LIMIT",
        Sequence("GROUP", "BY"),
        Sequence("ORDER", "BY"),
        Sequence("CLUSTER", "BY"),
        Sequence("DISTRIBUTE", "BY"),
        Sequence("SORT", "BY"),
        # TODO Add PIVOT, LATERAL VIEW, and DISTRIBUTE BY clauses
        "HAVING",
        "WINDOW",
        Ref("SetOperatorSegment"),
        Ref("WithNoSchemaBindingClauseSegment"),
        Ref("WithDataClauseSegment"),
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
    NaturalJoinKeywords=Sequence(
        "NATURAL",
        Ref("JoinTypeKeywords", optional=True),
    ),
    LikeGrammar=OneOf(
        # https://spark.apache.org/docs/latest/sql-ref-syntax-qry-select-like.html
        Sequence(
            "LIKE",
            OneOf(
                "ALL",
                "ANY",
                # `SOME` is equivalent to `ANY`
                "SOME",
                optional=True,
            ),
        ),
        "RLIKE",
        "REGEXP",
    ),
)

spark3_dialect.add(
    BinaryfileKeywordSegment=StringParser(
        "BINARYFILE",
        KeywordSegment,
        name="binary_file",
        type="file_format",
    ),
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
    LocationGrammar=hive_dialect.get_grammar("LocationGrammar"),
    PropertyGrammar=hive_dialect.get_grammar("PropertyGrammar"),
    SerdePropertiesGrammar=hive_dialect.get_grammar("SerdePropertiesGrammar"),
    StoredAsGrammar=hive_dialect.get_grammar("StoredAsGrammar"),
    StoredByGrammar=hive_dialect.get_grammar("StoredByGrammar"),
    StorageFormatGrammar=hive_dialect.get_grammar("StorageFormatGrammar"),
    TerminatedByGrammar=hive_dialect.get_grammar("TerminatedByGrammar"),
    # Add Spark Grammar
    BucketSpecGrammar=Sequence(
        Ref("ClusteredBySpecGrammar"),
        Ref("SortedBySpecGrammar", optional=True),
        "INTO",
        Ref("NumericLiteralSegment"),
        "BUCKETS",
    ),
    ClusteredBySpecGrammar=Sequence(
        "CLUSTERED",
        "BY",
        Ref("BracketedColumnReferenceListGrammar"),
    ),
    DatabasePropertiesGrammar=Sequence(
        "DBPROPERTIES", Ref("BracketedPropertyListGrammar")
    ),
    DataSourcesV2FileTypeGrammar=OneOf(
        # https://github.com/apache/spark/tree/master/sql/core/src/main/scala/org/apache/spark/sql/execution/datasources/v2  # noqa: E501
        # Separated here because these allow for additional
        # commands such as Select From File
        # https://spark.apache.org/docs/latest/sql-ref-syntax-qry-select-file.html
        # Spark Core Data Sources
        # https://spark.apache.org/docs/latest/sql-data-sources.html
        "AVRO",
        "CSV",
        "JSON",
        "PARQUET",
        "ORC",
        # Separated here because these allow for additional commands
        # Similar to DataSourcesV2
        "DELTA",  # https://github.com/delta-io/delta
        "CSV",
        "TEXT",
        "BINARYFILE",
    ),
    FileFormatGrammar=OneOf(
        Ref("DataSourcesV2FileTypeGrammar"),
        "SEQUENCEFILE",
        "TEXTFILE",
        "RCFILE",
        "JSONFILE",
        Sequence(
            "INPUTFORMAT",
            Ref("QuotedLiteralSegment"),
            "OUTPUTFORMAT",
            Ref("QuotedLiteralSegment"),
        ),
    ),
    DataSourceFormatGrammar=OneOf(
        Ref("FileFormatGrammar"),
        # NB: JDBC is part of DataSourceV2 but not included
        # there since there are no significant syntax changes
        "JDBC",
    ),
    # Adding Hint related segments so they are not treated as generic comments
    # https://spark.apache.org/docs/latest/sql-ref-syntax-qry-select-hints.html
    StartHintSegment=StringParser("/*+", KeywordSegment, name="start_hint"),
    EndHintSegment=StringParser("*/", KeywordSegment, name="end_hint"),
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
    SortedBySpecGrammar=Sequence(
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
    JoinTypeKeywords=OneOf(
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
    ),
)

# Adding Hint related grammar before comment `block_comment` and
# `single_quote` so they are applied before comment lexer so
# hints are treated as such instead of comments when parsing.
# https://spark.apache.org/docs/latest/sql-ref-syntax-qry-select-hints.html
spark3_dialect.insert_lexer_matchers(
    [
        RegexLexer("start_hint", r"\/\*\+", CodeSegment),
    ],
    before="block_comment",
)

spark3_dialect.insert_lexer_matchers(
    [
        RegexLexer("end_hint", r"\*\/", CodeSegment),
    ],
    before="single_quote",
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
        OptionallyBracketed(Ref("SelectableGrammar")),
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


@spark3_dialect.segment()
class InsertOverwriteDirectoryHiveFmtSegment(BaseSegment):
    """An `INSERT OVERWRITE [LOCAL] DIRECTORY` statement in Hive format.

    https://spark.apache.org/docs/latest/sql-ref-syntax-dml-insert-overwrite-directory-hive.html
    """

    type = "insert_overwrite_directory_hive_fmt_statement"

    match_grammar = Sequence(
        "INSERT",
        "OVERWRITE",
        Ref.keyword("LOCAL", optional=True),
        "DIRECTORY",
        Ref("QuotedLiteralSegment"),
        Ref("RowFormatClauseSegment", optional=True),
        Ref("StoredAsGrammar", optional=True),
        OneOf(
            AnyNumberOf(
                Ref("ValuesClauseSegment"),
                min_times=1,
            ),
            Ref("SelectableGrammar"),
        ),
    )


@spark3_dialect.segment()
class LoadDataSegment(BaseSegment):
    """A `LOAD DATA` statement.

    https://spark.apache.org/docs/latest/sql-ref-syntax-dml-load.html
    """

    type = "load_data_statement"

    match_grammar = Sequence(
        "LOAD",
        "DATA",
        Ref.keyword("LOCAL", optional=True),
        "INPATH",
        Ref("QuotedLiteralSegment"),
        Ref.keyword("OVERWRITE", optional=True),
        "INTO",
        "TABLE",
        Ref("TableReferenceSegment"),
        Ref("PartitionSpecGrammar", optional=True),
    )


# Data Retrieval Statements
@spark3_dialect.segment()
class ClusterByClauseSegment(BaseSegment):
    """A `CLUSTER BY` clause from `SELECT` statement.

    Equivalent to `DISTRIBUTE BY` and `SORT BY` in tandem.
    This clause is mutually exclusive with SORT BY, ORDER BY and DISTRIBUTE BY.
    https://spark.apache.org/docs/latest/sql-ref-syntax-qry-select-clusterby.html
    """

    type = "cluster_by_clause"

    match_grammar = StartsWith(
        Sequence("CLUSTER", "BY"),
        terminator=OneOf(
            "LIMIT",
            "HAVING",
            # For window functions
            "WINDOW",
            Ref("FrameClauseUnitGrammar"),
            "SEPARATOR",
        ),
    )

    parse_grammar = Sequence(
        "CLUSTER",
        "BY",
        Indent,
        Delimited(
            Sequence(
                OneOf(
                    Ref("ColumnReferenceSegment"),
                    # Can `CLUSTER BY 1`
                    Ref("NumericLiteralSegment"),
                    # Can cluster by an expression
                    Ref("ExpressionSegment"),
                ),
            ),
            terminator=OneOf(
                "WINDOW",
                "LIMIT",
                Ref("FrameClauseUnitGrammar"),
            ),
        ),
        Dedent,
    )


@spark3_dialect.segment()
class DistributeByClauseSegment(BaseSegment):
    """A `DISTRIBUTE BY` clause from `SELECT` statement.

    This clause is mutually exclusive with SORT BY, ORDER BY and DISTRIBUTE BY.
    https://spark.apache.org/docs/latest/sql-ref-syntax-qry-select-distribute-by.html
    """

    type = "distribute_by_clause"

    match_grammar = StartsWith(
        Sequence("DISTRIBUTE", "BY"),
        terminator=OneOf(
            "LIMIT",
            "HAVING",
            # For window functions
            "WINDOW",
            Ref("FrameClauseUnitGrammar"),
            "SEPARATOR",
        ),
    )

    parse_grammar = Sequence(
        "DISTRIBUTE",
        "BY",
        Indent,
        Delimited(
            Sequence(
                OneOf(
                    Ref("ColumnReferenceSegment"),
                    # Can `DISTRIBUTE BY 1`
                    Ref("NumericLiteralSegment"),
                    # Can distribute by an expression
                    Ref("ExpressionSegment"),
                ),
            ),
            terminator=OneOf(
                "WINDOW",
                "LIMIT",
                Ref("FrameClauseUnitGrammar"),
            ),
        ),
        Dedent,
    )


@spark3_dialect.segment()
class HintFunctionSegment(BaseSegment):
    """A Function within a SparkSQL Hint.

    https://spark.apache.org/docs/latest/sql-ref-syntax-qry-select-hints.html
    """

    type = "hint_function"

    match_grammar = Sequence(
        Ref("FunctionNameSegment"),
        Bracketed(
            Delimited(
                AnyNumberOf(
                    Ref("SingleIdentifierGrammar"),
                    Ref("NumericLiteralSegment"),
                    min_times=1,
                ),
            ),
            # May be Bare Function unique to Hints, i.e. REBALANCE
            optional=True,
        ),
    )


@spark3_dialect.segment()
class SelectHintSegment(BaseSegment):
    """Spark Select Hints.

    https://spark.apache.org/docs/latest/sql-ref-syntax-qry-select-hints.html
    """

    type = "select_hint"

    match_grammar = Sequence(
        Sequence(
            Ref("StartHintSegment"),
            Delimited(
                AnyNumberOf(
                    Ref("HintFunctionSegment"),
                    # At least function should be supplied
                    min_times=1,
                ),
                terminator=Ref("EndHintSegment"),
            ),
            Ref("EndHintSegment"),
        ),
    )


@spark3_dialect.segment(replace=True)
class LimitClauseSegment(BaseSegment):
    """A `LIMIT` clause like in `SELECT`.

    Enhanced from ANSI dialect.
    :: Spark does not allow explicit or implicit
       `OFFSET` (implicit being 1000, 20 for example)
    :: Spark allows an `ALL` quantifier or a function
       expression as an input to `LIMIT`
    https://spark.apache.org/docs/latest/sql-ref-syntax-qry-select-limit.html
    """

    type = "limit_clause"
    match_grammar = Sequence(
        "LIMIT",
        Indent,
        OneOf(
            Ref("NumericLiteralSegment"),
            "ALL",
            Ref("FunctionSegment"),
        ),
        Dedent,
    )


@spark3_dialect.segment(replace=True)
class SetOperatorSegment(BaseSegment):
    """A set operator such as Union, Minus, Except or Intersect.

    Enhanced from ANSI dialect.
    :: Spark allows the `ALL` keyword to follow Except and Minus.
    :: Distinct allows the `DISTINCT` and `ALL` keywords.

    # https://spark.apache.org/docs/latest/sql-ref-syntax-qry-select-setops.html
    """

    type = "set_operator"

    match_grammar = OneOf(
        Sequence(
            OneOf("EXCEPT", "MINUS"),
            Ref.keyword("ALL", optional=True),
        ),
        Sequence(
            OneOf("UNION", "INTERSECT"),
            OneOf("DISTINCT", "ALL", optional=True),
        ),
    )


@spark3_dialect.segment(replace=True)
class SelectClauseModifierSegment(BaseSegment):
    """Things that come after SELECT but before the columns.

    Enhance `SelectClauseModifierSegment` from Ansi to allow SparkSQL Hints
    https://spark.apache.org/docs/latest/sql-ref-syntax-qry-select-hints.html
    """

    type = "select_clause_modifier"
    match_grammar = Sequence(
        # TODO New Rule warning of Join Hints priority if multiple specified
        #   When different join strategy hints are specified on
        #     both sides of a join, Spark prioritizes the BROADCAST
        #     hint over the MERGE hint over the SHUFFLE_HASH hint
        #     over the SHUFFLE_REPLICATE_NL hint.
        #
        #   Spark will issue Warning in the following example:
        #
        #   SELECT
        #   /*+ BROADCAST(t1), MERGE(t1, t2) */
        #       t1.a,
        #       t1.b,
        #       t2.c
        #   FROM t1 INNER JOIN t2 ON t1.key = t2.key;
        #
        #   Hints should be listed in order of priority in Select
        Ref("SelectHintSegment", optional=True),
        OneOf("DISTINCT", "ALL", optional=True),
    )


@spark3_dialect.segment(replace=True)
class UnorderedSelectStatementSegment(BaseSegment):
    """Enhance unordered `SELECT` statement for valid SparkSQL clauses.

    This is designed for use in the context of set operations,
    for other use cases, we should use the main
    SelectStatementSegment.
    """

    type = "select_statement"

    match_grammar = ansi_dialect.get_segment(
        "UnorderedSelectStatementSegment"
    ).match_grammar.copy()

    parse_grammar = ansi_dialect.get_segment(
        "UnorderedSelectStatementSegment"
    ).parse_grammar.copy(
        # TODO Insert: PIVOT and LATERAL VIEW clauses
        # Removing non-valid clauses that exist in ANSI dialect
        remove=[Ref("OverlapsClauseSegment", optional=True)]
    )


@spark3_dialect.segment(replace=True)
class SelectStatementSegment(BaseSegment):
    """Enhance `SELECT` statement for valid SparkSQL clauses."""

    type = "select_statement"

    match_grammar = ansi_dialect.get_segment(
        "SelectStatementSegment"
    ).match_grammar.copy()

    parse_grammar = ansi_dialect.get_segment(
        "SelectStatementSegment"
    ).parse_grammar.copy(
        # TODO New Rule: Warn of mutual exclusion of following clauses
        #  DISTRIBUTE, SORT, CLUSTER and ORDER BY if multiple specified
        insert=[
            Ref("ClusterByClauseSegment", optional=True),
            Ref("DistributeByClauseSegment", optional=True),
            Ref("SortByClauseSegment", optional=True),
        ],
        before=Ref("LimitClauseSegment"),
    )


@spark3_dialect.segment(replace=True)
class GroupByClauseSegment(BaseSegment):
    """Enhance `GROUP BY` clause like in `SELECT` for 'CUBE' and 'ROLLUP`.

    https://spark.apache.org/docs/latest/sql-ref-syntax-qry-select-groupby.html
    """

    type = "group_by_clause"

    match_grammar = StartsWith(
        Sequence("GROUP", "BY"),
        terminator=OneOf("ORDER", "LIMIT", "HAVING", "WINDOW"),
        enforce_whitespace_preceding_terminator=True,
    )

    parse_grammar = Sequence(
        "GROUP",
        "BY",
        Indent,
        Delimited(
            OneOf(
                Ref("ColumnReferenceSegment"),
                # Can `GROUP BY 1`
                Ref("NumericLiteralSegment"),
                # Can `GROUP BY coalesce(col, 1)`
                Ref("ExpressionSegment"),
                Ref("CubeRollupClauseSegment"),
                Ref("GroupingSetsClauseSegment"),
            ),
            terminator=OneOf("ORDER", "LIMIT", "HAVING", "WINDOW"),
        ),
        # TODO: New Rule
        #  Warn if CubeRollupClauseSegment and
        #  WithCubeRollupClauseSegment used in same query
        Ref("WithCubeRollupClauseSegment", optional=True),
        Dedent,
    )


@spark3_dialect.segment()
class WithCubeRollupClauseSegment(BaseSegment):
    """A `[WITH CUBE | WITH ROLLUP]` clause after the `GROUP BY` clause.

    https://spark.apache.org/docs/latest/sql-ref-syntax-qry-select-groupby.html
    """

    type = "with_cube_rollup_clause"

    match_grammar = Sequence(
        "WITH",
        OneOf("CUBE", "ROLLUP"),
    )


@spark3_dialect.segment()
class CubeRollupClauseSegment(BaseSegment):
    """`[CUBE | ROLLUP]` clause within the `GROUP BY` clause.

    https://spark.apache.org/docs/latest/sql-ref-syntax-qry-select-groupby.html
    """

    type = "cube_rollup_clause"

    match_grammar = StartsWith(
        OneOf("CUBE", "ROLLUP"),
        terminator=OneOf(
            "HAVING",
            Sequence("ORDER", "BY"),
            "LIMIT",
            Ref("SetOperatorSegment"),
        ),
    )

    parse_grammar = Sequence(
        OneOf("CUBE", "ROLLUP"),
        Bracketed(
            Ref("GroupingExpressionList"),
        ),
    )


@spark3_dialect.segment()
class GroupingSetsClauseSegment(BaseSegment):
    """`GROUPING SETS` clause within the `GROUP BY` clause."""

    type = "grouping_sets_clause"

    match_grammar = StartsWith(
        Sequence("GROUPING", "SETS"),
        terminator=OneOf(
            "HAVING",
            Sequence("ORDER", "BY"),
            "LIMIT",
            Ref("SetOperatorSegment"),
        ),
    )

    parse_grammar = Sequence(
        "GROUPING",
        "SETS",
        Bracketed(
            Delimited(
                Ref("CubeRollupClauseSegment"),
                Ref("GroupingExpressionList"),
                Bracketed(),  # Allows empty parentheses
            )
        ),
    )


@spark3_dialect.segment()
class GroupingExpressionList(BaseSegment):
    """Grouping expression list within `CUBE` / `ROLLUP` `GROUPING SETS`."""

    type = "grouping_expression_list"

    match_grammar = Delimited(
        OneOf(
            Bracketed(Delimited(Ref("ExpressionSegment"))),
            Ref("ExpressionSegment"),
        )
    )


@spark3_dialect.segment()
class SortByClauseSegment(BaseSegment):
    """A `SORT BY` clause like in `SELECT`.

    This clause is mutually exclusive with SORT BY, ORDER BY and DISTRIBUTE BY.
    https://spark.apache.org/docs/latest/sql-ref-syntax-qry-select-sortby.html
    """

    type = "sort_by_clause"

    match_grammar = StartsWith(
        Sequence("SORT", "BY"),
        terminator=OneOf(
            "LIMIT",
            "HAVING",
            "QUALIFY",
            # For window functions
            "WINDOW",
            Ref("FrameClauseUnitGrammar"),
            "SEPARATOR",
        ),
    )
    parse_grammar = Sequence(
        "SORT",
        "BY",
        Indent,
        Delimited(
            Sequence(
                OneOf(
                    Ref("ColumnReferenceSegment"),
                    # Can `ORDER BY 1`
                    Ref("NumericLiteralSegment"),
                    # Can order by an expression
                    Ref("ExpressionSegment"),
                ),
                OneOf("ASC", "DESC", optional=True),
                # NB: This isn't really ANSI, and isn't supported in Mysql,
                # but is supported in enough other dialects for it to make
                # sense here for now.
                Sequence("NULLS", OneOf("FIRST", "LAST"), optional=True),
            ),
            terminator=OneOf(
                "LIMIT",
                Ref("FrameClauseUnitGrammar"),
            ),
        ),
        Dedent,
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

    type = "statement"
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
            Ref("InsertOverwriteDirectoryHiveFmtSegment"),
            Ref("LoadDataSegment"),
            # Data Retrieval Statements
            Ref("ClusterByClauseSegment"),
            Ref("DistributeByClauseSegment"),
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

    https://spark.apache.org/docs/latest/sql-ref-syntax-qry-select-join.html
    """

    type = "join_clause"

    match_grammar = StartsWith(
        OneOf(
            Ref("JoinTypeKeywords"),
            Ref("JoinKeywords"),
            Ref("NaturalJoinKeywords"),
        ),
    )

    parse_grammar = OneOf(
        # NB These qualifiers are optional
        # TODO: Allow nested joins like:
        # ....FROM S1.T1 t1 LEFT JOIN ( S2.T2 t2 JOIN S3.T3 t3 ON t2.col1=t3.col1) ON
        # tab1.col1 = tab2.col1
        Sequence(
            Ref("JoinTypeKeywords", optional=True),
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
                            # rather than ObjectReferenceSegment or
                            # ColumnReferenceSegment. This is a) so that we don't
                            # lint it as a reference and b) because the column will
                            # probably be returned anyway during parsing.
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
        ),
        # Note NATURAL joins do not support Join conditions
        Sequence(
            Ref("NaturalJoinKeywords"),
            Ref("JoinKeywords"),
            Indent,
            Ref("FromExpressionElementSegment"),
            Dedent,
        ),
    )

    get_eventual_alias = ansi_dialect.get_segment(
        "JoinClauseSegment"
    ).get_eventual_alias


@spark3_dialect.segment(replace=True)
class AliasExpressionSegment(BaseSegment):
    """A reference to an object with an `AS` clause.

    The optional AS keyword allows both implicit and explicit aliasing.
    Note also that it's possible to specify just column aliases without aliasing the
    table as well:
    .. code-block:: sql

        SELECT * FROM VALUES (1,2) as t (a, b);
        SELECT * FROM VALUES (1,2) as (a, b);
        SELECT * FROM VALUES (1,2) as t;

    Note that in Spark SQL, identifiers are quoted using backticks (`my_table`) rather
    than double quotes ("my_table"). Quoted identifiers are allowed in aliases, but
    unlike ANSI which allows single quoted identifiers ('my_table') in aliases, this is
    not allowed in Spark and so the definition of this segment must depart from ANSI.
    """

    type = "alias_expression"

    match_grammar = Sequence(
        Ref.keyword("AS", optional=True),
        OneOf(
            # maybe table alias and column aliases
            Sequence(
                Ref("SingleIdentifierGrammar", optional=True),
                Bracketed(Ref("SingleIdentifierListSegment")),
            ),
            # just a table alias
            Ref("SingleIdentifierGrammar"),
            exclude=Ref("JoinTypeKeywords"),
        ),
    )


@spark3_dialect.segment()
class DelimitedValues(BaseSegment):
    """A ``VALUES`` clause can be a sequence either of scalar values or tuple values.

    We make no attempt to ensure that all records have the same number of columns
    besides the distinction between all scalar or all tuple, so for instance
    ``VALUES (1,2), (3,4,5)`` will parse but is not legal SQL.
    """

    type = "delimited_values"
    match_grammar = OneOf(Delimited(Ref("ScalarValue")), Delimited(Ref("TupleValue")))


@spark3_dialect.segment()
class ScalarValue(BaseSegment):
    """An element of a ``VALUES`` clause that has a single column.

    Ex: ``VALUES 1,2,3``
    """

    type = "scalar_value"
    match_grammar = OneOf(
        Ref("LiteralGrammar"),
        Ref("BareFunctionSegment"),
        Ref("FunctionSegment"),
    )


@spark3_dialect.segment()
class TupleValue(BaseSegment):
    """An element of a ``VALUES`` clause that has multiple columns.

    Ex: ``VALUES (1,2), (3,4)``
    """

    type = "tuple_value"
    match_grammar = Bracketed(
        Delimited(
            Ref("ScalarValue"),
        )
    )


@spark3_dialect.segment(replace=True)
class ValuesClauseSegment(BaseSegment):
    """A `VALUES` clause, as typically used with `INSERT` or `SELECT`.

    The Spark SQL reference does not mention `VALUES` clauses except in the context
    of `INSERT` statements. However, they appear to behave much the same as in
    `postgres <https://www.postgresql.org/docs/13/sql-values.html>`.

    In short, they can appear anywhere a `SELECT` can, and also as bare `VALUES`
    statements. Here are some examples:
    .. code-block:: sql

        VALUES 1,2 LIMIT 1;
        SELECT * FROM VALUES (1,2) as t (a,b);
        SELECT * FROM (VALUES (1,2) as t (a,b));
        WITH a AS (VALUES 1,2) SELECT * FROM a;

    """

    type = "values_clause"

    match_grammar = Sequence(
        "VALUES",
        Ref("DelimitedValues"),
        AnyNumberOf(
            Ref("AliasExpressionSegment"),
            min_times=0,
            max_times=1,
            exclude=OneOf("LIMIT", "ORDER"),
        ),
        Ref("OrderByClauseSegment", optional=True),
        Ref("LimitClauseSegment", optional=True),
    )


@spark3_dialect.segment(replace=True)
class TableExpressionSegment(BaseSegment):
    """The main table expression e.g. within a FROM clause.

    Enhance to allow for additional clauses allowed in Spark.
    """

    type = "table_expression"
    match_grammar = OneOf(
        Ref("ValuesClauseSegment"),
        Ref("BareFunctionSegment"),
        Ref("FunctionSegment"),
        Ref("FileReferenceSegment"),
        Ref("TableReferenceSegment"),
        # Nested Selects
        Bracketed(Ref("SelectableGrammar")),
    )


@spark3_dialect.segment()
class FileReferenceSegment(BaseSegment):
    """A reference to a file for direct query.

    https://spark.apache.org/docs/latest/sql-ref-syntax-qry-select-file.html
    """

    type = "file_reference"

    match_grammar = Sequence(
        Ref("DataSourcesV2FileTypeGrammar"),
        Ref("DotSegment"),
        # NB: Using `QuotedLiteralSegment` here causes `FileReferenceSegment`
        # to match as a `TableReferenceSegment`
        Ref("QuotedIdentifierSegment"),
    )
