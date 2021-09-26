"""The Spark SQL dialect for ANSI Compliant Spark3.

Inherits from ANSI.
  Spark SQL ANSI Mode is more restrictive regarding
  keywords than the Default Mode.

Based on:
- https://spark.apache.org/docs/latest/sql-ref.html
- https://spark.apache.org/docs/latest/sql-ref-ansi-compliance.html
https://github.com/apache/spark/blob/master/sql/catalyst/src/main/antlr4/org/apache/spark/sql/catalyst/parser/SqlBase.g4
"""

from sqlfluff.core.parser import (
    AnyNumberOf,
    BaseSegment,
    Bracketed,
    Delimited,
    CommentSegment,
    NamedParser,
    OneOf,
    OptionallyBracketed,
    Ref,
    RegexLexer,
    RegexParser,
    StringLexer,
    Sequence,
    StartsWith,
    StringParser,
    SymbolSegment,
)

from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.core.parser.segments.raw import CodeSegment
from sqlfluff.dialects.spark3_keywords import (
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
    ]
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
ansi_dialect.sets("datetime_units").clear()
ansi_dialect.sets("datetime_units").update(
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

# Real Segments
spark3_dialect.add(
    # Add Hive Segments TODO : Is there a way to retrive this w/o redefining?
    DoubleQuotedLiteralSegment=NamedParser(
        "double_quote",
        CodeSegment,
        name="quoted_literal",
        type="literal",
        trim_chars=('"',),
    ),
    # Add Spark Segments
    EqualsSegment_a=StringParser(
        "==", SymbolSegment, name="equals", type="comparison_operator"
    ),
    EqualsSegment_b=StringParser(
        "<=>", SymbolSegment, name="equals", type="comparison_operator"
    ),
    # Add relevant Hive Grammar
    SingleOrDoubleQuotedLiteralGrammar=hive_dialect.get_grammar("SingleOrDoubleQuotedLiteralGrammar"),
    PropertyGrammar=hive_dialect.get_grammar("PropertyGrammar"),
    BracketedPropertyListGrammar=hive_dialect.get_grammar("BracketedPropertyListGrammar"),
    PartitionSpecGrammar=hive_dialect.get_grammar("PartitionSpecGrammar"),
    SerdePropertiesGrammar=hive_dialect.get_grammar("SerdePropertiesGrammar"),
    LocationGrammar=hive_dialect.get_grammar("LocationGrammar"),
    # Add Spark Grammar
    DatabasePropertiesGrammar=Sequence("DBPROPERTIES", Ref("BracketedPropertyListGrammar")),
    SetTablePropertiesGrammar=Sequence(
        "SET", "TBLPROPERTIES", Ref("BracketedPropertyListGrammar")
    ),
    UnsetTablePropertiesGrammar=Sequence(
        "UNSET",
        "TBLPROPERTIES",
        Ref("IfExistsGrammar", optional=True),
        Ref("SingleOrDoubleQuotedLiteralGrammar"),
    ),
    FileFormatGrammar=OneOf(
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
)
spark3_dialect.replace(
    ComparisonOperatorGrammar=OneOf(
        Ref("EqualsSegment"),
        Ref("EqualsSegment_a"),
        Ref("EqualsSegment_b"),
        Ref("GreaterThanSegment"),
        Ref("LessThanSegment"),
        Ref("GreaterThanOrEqualToSegment"),
        Ref("LessThanOrEqualToSegment"),
        Ref("NotEqualToSegment_a"),
        Ref("NotEqualToSegment_b"),
        Ref("LikeOperatorSegment"),
    ),
)


# Primitive Data Types
@spark3_dialect.segment()
class PrimitiveTypeSegment(BaseSegment):
    """
        Spark SQL Primitive data types.
        https://spark.apache.org/docs/latest/sql-ref-datatypes.html
    """

    type = "primitive_type"
    match_grammar = OneOf(
        "BOOLEAN",
        "TINYINT",
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
            Bracketed(
                Ref("NumericLiteralSegment"),
                optional=True
            ),
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
class DatatypeSegment(BaseSegment):
    """
        Spark SQL Data types.
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
                    bracket_pairs_set="angle_bracket_pairs",
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
    """
        An `ALTER DATABASE/SCHEMA` statement.
        http://spark.apache.org/docs/latest/sql-ref-syntax-ddl-alter-database.html
    """

    type = "alter_database_statement"

    match_grammar = Sequence(
        "ALTER",
        OneOf("DATABASE", "SCHEMA"),
        Ref("DatabaseReferenceSegment"),
        "SET",
        Ref("DatabasePropertiesGrammar")
    )


@spark3_dialect.segment(replace=True)
class AlterTableStatementSegment(BaseSegment):
    """
        A `ALTER TABLE` statement to change the table/view schema or properties.
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
            # Sequence(
                # OneOf("ALTER", "CHANGE"),
                # "COLUMN",
                # Ref("ColumnReferenceSegment"),
                # Sequence(
                #     "TYPE", Ref("DatatypeSegment"), optional=True
                # ),
                # Ref("CommentClauseSegment", optional=True),
                # # TODO : Add to Spark dialect - ColPositionGrammar
                # OneOf(
                #     "FIRST",
                #     Sequence(
                #         "AFTER", Ref("ColumnReferenceSegment")
                #     ),
                #     optional=True
                # ),
                # Sequence(
                #     OneOf("SET", "DROP"), "NOT NULL", optional=True
                # ),
            # ),
    #         # ALTER TABLE - ADD PARTITION
    #         Sequence(
    #             "ADD",
    #             Ref("IfNotExistsGrammar", optional=True),
    #             Ref("PartitionSpecGrammar")
    #         ),
    #         # ALTER TABLE - DROP PARTITION
    #         Sequence(
    #             "DROP",
    #             Ref("IfExistsGrammar", optional=True),
    #             Ref("PartitionSpecGrammar"),
    #             Sequence("PURGE", optional=True),
    #         ),
    #         # ALTER TABLE - SET PROPERTIES
    #         Ref("SetTablePropertiesGrammar"),
    #         # ALTER TABLE - UNSET PROPERTIES
    #         Ref("UnsetTablePropertiesGrammar"),
    #         # ALTER TABLE - SET SERDE
    #         Sequence(
    #             Ref("PartitionSpecGrammar"),
    #             "SET",
    #             OneOf(
    #                 Sequence(
    #                     "SERDEPROPERTIES",
    #                     Ref("BracketedPropertyListGrammar"),
    #                 ),
    #                 Sequence(
    #                     "SERDE",
    #                     Ref("ParameterNameSegment"),
    #                     Ref("SerdePropertiesGrammar", optional=True),
    #                 ),
    #             ),
    #
    #         ),
    #         # ALTER TABLE - SET FILE FORMAT
    #         Sequence(
    #             Ref("PartitionSpecGrammar"),
    #             "SET",
    #             "FILEFORMAT",
    #             Ref("FileFormatGrammar"),
    #         ),
    #         # ALTER TABLE - CHANGE FILE LOCATION
    #         Sequence(
    #             Ref("PartitionSpecGrammar"),
    #             "SET",
    #             Ref("LocationGrammar"),
    #         ),
        ),
    )


# @spark_dialect.segment(replace=True)
# class CreateTableStatementSegment(ansi_dialect.get_segment("CreateTableStatementSegment")):
#     """
#         A `CREATE TABLE` statement using a Data Source.
#         http://spark.apache.org/docs/latest/sql-ref-syntax-ddl-create-table-datasource.html
#     """
#
#     match_grammar = Sequence(
#         "CREATE",
#         "TABLE",
#         Ref("IfNotExistsGrammar", optional=True),
#         Ref("TableReferenceSegment"),
#         # Columns and comment syntax:
#         Sequence(
#             Bracketed(
#                 Delimited(
#                     Ref("ColumnDefinitionSegment"),
#                 ),
#             ),
#             Ref("CommentClauseSegment", optional=True),
#         ),
#         # Create AS syntax:
#         Sequence(
#             "AS",
#             OptionallyBracketed(Ref("SelectableGrammar")),
#         ),
#     )
#
#
# @spark_dialect.segment()
# class CreateHiveFormatTableStatementSegment(hive_dialect.get_segment("CreateTableStatementSegment")):
#     """
#         A `CREATE TABLE` statement using Hive format.
#         https://spark.apache.org/docs/latest/sql-ref-syntax-ddl-create-table-hiveformat.html
#     """
#
#
# @spark_dialect.segment()
# class CreateTableLikeStatement(BaseSegment):
#     """
#         A 'CREATE TABLE` statement using the definition/metadata of an existing table or view.
#         http://spark.apache.org/docs/latest/sql-ref-syntax-ddl-create-table-like.html
#     """


@spark3_dialect.segment(replace=True)
class StatementSegment(ansi_dialect.get_segment("StatementSegment")):  # type: ignore
    """Overriding StatementSegment to allow for additional segment parsing."""

    parse_grammar = ansi_dialect.get_segment("StatementSegment").parse_grammar.copy(
        insert=[
            # Data Definition Statements
            Ref("AlterDatabaseStatementSegment"),
            Ref("AlterTableStatementSegment"),
        ],
        # remove=[
        #     Ref("TransactionStatementSegment"),
        #     Ref("CreateSchemaStatementSegment"),
        #     Ref("SetSchemaStatementSegment"),
        #     Ref("DropSchemaStatementSegment"),
        #     Ref("CreateExtensionStatementSegment"),
        #     Ref("CreateModelStatementSegment"),
        #     Ref("DropModelStatementSegment"),
        # ],
    )
