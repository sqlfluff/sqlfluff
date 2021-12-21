"""The Hive dialect."""

from sqlfluff.core.parser import (
    BaseSegment,
    Sequence,
    Ref,
    OneOf,
    Bracketed,
    Delimited,
    StartsWith,
    NamedParser,
    SymbolSegment,
    StringParser,
    OptionallyBracketed,
)

from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.core.parser.segments.raw import CodeSegment, KeywordSegment
from sqlfluff.dialects.dialect_hive_keywords import (
    RESERVED_KEYWORDS,
    UNRESERVED_KEYWORDS,
)

ansi_dialect = load_raw_dialect("ansi")
hive_dialect = ansi_dialect.copy_as("hive")

# Clear ANSI Keywords and add all Hive keywords
# Commented clearing for now as some are needed for some statements imported
# from ANSI to work
# hive_dialect.sets("unreserved_keywords").clear()
hive_dialect.sets("unreserved_keywords").update(UNRESERVED_KEYWORDS)
# hive_dialect.sets("reserved_keywords").clear()
hive_dialect.sets("reserved_keywords").update(RESERVED_KEYWORDS)

hive_dialect.sets("angle_bracket_pairs").update(
    [
        ("angle", "StartAngleBracketSegment", "EndAngleBracketSegment", False),
    ]
)

# Hive adds these timeunit aliases for intervals "to aid portability / readability"
# https://cwiki.apache.org/confluence/display/hive/languagemanual+types#LanguageManualTypes-Intervals
hive_dialect.sets("datetime_units").update(
    [
        "NANO",
        "NANOS",
        "SECONDS",
        "MINUTES",
        "HOURS",
        "DAYS",
        "WEEKS",
        "MONTHS",
        "YEARS",
    ]
)

hive_dialect.add(
    DoubleQuotedLiteralSegment=NamedParser(
        "double_quote",
        CodeSegment,
        name="quoted_literal",
        type="literal",
        trim_chars=('"',),
    ),
    SingleOrDoubleQuotedLiteralGrammar=OneOf(
        Ref("QuotedLiteralSegment"), Ref("DoubleQuotedLiteralSegment")
    ),
    StartAngleBracketSegment=StringParser(
        "<", SymbolSegment, name="start_angle_bracket", type="start_angle_bracket"
    ),
    EndAngleBracketSegment=StringParser(
        ">", SymbolSegment, name="end_angle_bracket", type="end_angle_bracket"
    ),
    JsonfileKeywordSegment=StringParser(
        "JSONFILE", KeywordSegment, name="json_file", type="file_format"
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
    LocationGrammar=Sequence("LOCATION", Ref("SingleOrDoubleQuotedLiteralGrammar")),
    PropertyGrammar=Sequence(
        Ref("SingleOrDoubleQuotedLiteralGrammar"),
        Ref("EqualsSegment"),
        Ref("SingleOrDoubleQuotedLiteralGrammar"),
    ),
    BracketedPropertyListGrammar=Bracketed(Delimited(Ref("PropertyGrammar"))),
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
        Sequence(
            "INPUTFORMAT",
            Ref("SingleOrDoubleQuotedLiteralGrammar"),
            "OUTPUTFORMAT",
            Ref("SingleOrDoubleQuotedLiteralGrammar"),
        ),
    ),
    StoredAsGrammar=Sequence("STORED", "AS", Ref("FileFormatGrammar")),
    StoredByGrammar=Sequence(
        "STORED",
        "BY",
        Ref("SingleOrDoubleQuotedLiteralGrammar"),
        Ref("SerdePropertiesGrammar", optional=True),
    ),
    StorageFormatGrammar=OneOf(
        Sequence(
            Ref("RowFormatClauseSegment", optional=True),
            Ref("StoredAsGrammar", optional=True),
        ),
        Ref("StoredByGrammar"),
    ),
    CommentGrammar=Sequence("COMMENT", Ref("SingleOrDoubleQuotedLiteralGrammar")),
    PartitionSpecGrammar=Sequence(
        "PARTITION",
        Bracketed(
            Delimited(
                Sequence(
                    Ref("ColumnReferenceSegment"),
                    Ref("EqualsSegment"),
                    Ref("LiteralGrammar"),
                )
            )
        ),
    ),
)

# https://cwiki.apache.org/confluence/display/hive/languagemanual+joins
hive_dialect.replace(
    JoinKeywords=Sequence(Sequence("SEMI", optional=True), "JOIN"),
)


@hive_dialect.segment(replace=True)
class CreateDatabaseStatementSegment(BaseSegment):
    """A `CREATE DATABASE` statement."""

    type = "create_database_statement"
    match_grammar = Sequence(
        "CREATE",
        OneOf("DATABASE", "SCHEMA"),
        Ref("IfNotExistsGrammar", optional=True),
        Ref("DatabaseReferenceSegment"),
        Ref("CommentGrammar", optional=True),
        Ref("LocationGrammar", optional=True),
        Sequence(
            "MANAGEDLOCATION", Ref("SingleOrDoubleQuotedLiteralGrammar"), optional=True
        ),
        Sequence(
            "WITH", "DBPROPERTIES", Ref("BracketedPropertyListGrammar"), optional=True
        ),
    )


@hive_dialect.segment(replace=True)
class CreateTableStatementSegment(BaseSegment):
    """A `CREATE TABLE` statement.

    Full Apache Hive `CREATE TABLE` reference here:
    https://cwiki.apache.org/confluence/display/hive/languagemanual+ddl#LanguageManualDDL-CreateTable
    """

    type = "create_table_statement"
    match_grammar = StartsWith(
        Sequence(
            "CREATE",
            Ref.keyword("TEMPORARY", optional=True),
            Ref.keyword("EXTERNAL", optional=True),
            "TABLE",
        )
    )

    parse_grammar = Sequence(
        "CREATE",
        Ref.keyword("TEMPORARY", optional=True),
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
                            # TODO: support all constraints
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
                # `STORED AS` can be called before or after the additional table properties below
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
                    Sequence(
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
                    "INTO",
                    Ref("NumericLiteralSegment"),
                    "BUCKETS",
                    optional=True,
                ),
                # Second call of `STORED AS` to match when appears after
                Ref("StoredAsGrammar", optional=True),
                Ref("SkewedByClauseSegment", optional=True),
                Ref("StorageFormatGrammar", optional=True),
                Ref("LocationGrammar", optional=True),
                Ref("TablePropertiesGrammar", optional=True),
                Ref("CommentGrammar", optional=True),
                Sequence(
                    "AS",
                    OptionallyBracketed(Ref("SelectableGrammar")),
                    optional=True,
                ),
            ),
            # Create like syntax
            Sequence(
                "LIKE",
                Ref("TableReferenceSegment"),
                Ref("LocationGrammar", optional=True),
                Ref("TablePropertiesGrammar", optional=True),
            ),
        ),
    )


@hive_dialect.segment()
class PrimitiveTypeSegment(BaseSegment):
    """Primitive data types."""

    type = "primitive_type"
    match_grammar = OneOf(
        "TINYINT",
        "SMALLINT",
        "INT",
        "BIGINT",
        "BOOLEAN",
        "FLOAT",
        Sequence("DOUBLE", Ref.keyword("PRECISION", optional=True)),
        "STRING",
        "BINARY",
        "TIMESTAMP",
        Sequence(
            "DECIMAL",
            Bracketed(
                Ref("NumericLiteralSegment"),
                Ref("CommaSegment"),
                Ref("NumericLiteralSegment"),
                optional=True,
            ),
        ),
        "DATE",
        "VARCHAR",
        "CHAR",
    )


@hive_dialect.segment(replace=True)
class DatatypeSegment(BaseSegment):
    """Data types."""

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
        Sequence(
            "UNIONTYPE",
            Bracketed(
                Delimited(
                    Ref("DatatypeSegment"), bracket_pairs_set="angle_bracket_pairs"
                ),
                bracket_pairs_set="angle_bracket_pairs",
                bracket_type="angle",
            ),
        ),
    )


@hive_dialect.segment()
class SkewedByClauseSegment(BaseSegment):
    """`SKEWED BY` clause in a CREATE / ALTER statement."""

    type = "skewed_by_clause"
    match_grammar = Sequence(
        "SKEWED",
        "BY",
        Ref("BracketedColumnReferenceListGrammar"),
        "ON",
        Bracketed(
            Delimited(
                OneOf(
                    Ref("LiteralGrammar"), Bracketed(Delimited(Ref("LiteralGrammar")))
                )
            )
        ),
        Sequence("STORED", "AS", "DIRECTORIES", optional=True),
    )


@hive_dialect.segment()
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
                Ref("SingleOrDoubleQuotedLiteralGrammar"),
                Ref("SerdePropertiesGrammar", optional=True),
            ),
        ),
    )


@hive_dialect.segment()
class AlterDatabaseStatementSegment(BaseSegment):
    """An `ALTER DATABASE/SCHEMA` statement."""

    type = "alter_database_statement"
    match_grammar = Sequence(
        "ALTER",
        OneOf("DATABASE", "SCHEMA"),
        Ref("DatabaseReferenceSegment"),
        "SET",
        OneOf(
            Sequence("DBPROPERTIES", Ref("BracketedPropertyListGrammar")),
            Sequence(
                "OWNER",
                OneOf("USER", "ROLE"),
                Ref("SingleOrDoubleQuotedLiteralGrammar"),
            ),
            Ref("LocationGrammar"),
            Sequence("MANAGEDLOCATION", Ref("SingleOrDoubleQuotedLiteralGrammar")),
        ),
    )


@hive_dialect.segment(replace=True)
class DropStatementSegment(BaseSegment):
    """A `DROP` statement."""

    type = "drop_statement"
    match_grammar = StartsWith("DROP")
    parse_grammar = OneOf(
        Ref("DropDatabaseStatementSegment"),
        Ref("DropTableStatementSegment"),
        # TODO: add other drops
    )


@hive_dialect.segment()
class DropDatabaseStatementSegment(BaseSegment):
    """A `DROP DATEBASE/SCHEMA` statement."""

    type = "drop_table_statement"
    match_grammar = Sequence(
        "DROP",
        OneOf("DATABASE", "SCHEMA"),
        Ref("IfExistsGrammar", optional=True),
        Ref("DatabaseReferenceSegment"),
        OneOf("RESTRICT", "CASCADE", optional=True),
    )


@hive_dialect.segment()
class DropTableStatementSegment(BaseSegment):
    """A `DROP TABLE` statement."""

    type = "drop_table_statement"
    match_grammar = Sequence(
        "DROP",
        "TABLE",
        Ref("IfExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        Ref.keyword("PURGE", optional=True),
    )


@hive_dialect.segment(replace=True)
class TruncateStatementSegment(BaseSegment):
    """`TRUNCATE TABLE` statement."""

    type = "truncate_table"

    match_grammar = StartsWith("TRUNCATE")
    parse_grammar = Sequence(
        "TRUNCATE",
        Ref.keyword("TABLE", optional=True),
        Ref("TableReferenceSegment"),
        Ref("PartitionSpecGrammar", optional=True),
    )


@hive_dialect.segment(replace=True)
class UseStatementSegment(BaseSegment):
    """An `USE` statement."""

    type = "use_statement"
    match_grammar = Sequence(
        "USE",
        Ref("DatabaseReferenceSegment"),
    )


@hive_dialect.segment(replace=True)
class StatementSegment(ansi_dialect.get_segment("StatementSegment")):  # type: ignore
    """Overriding StatementSegment to allow for additional segment parsing."""

    parse_grammar = ansi_dialect.get_segment("StatementSegment").parse_grammar.copy(
        insert=[Ref("AlterDatabaseStatementSegment")],
        remove=[
            Ref("TransactionStatementSegment"),
            Ref("CreateSchemaStatementSegment"),
            Ref("SetSchemaStatementSegment"),
            Ref("DropSchemaStatementSegment"),
            Ref("CreateExtensionStatementSegment"),
            Ref("CreateModelStatementSegment"),
            Ref("DropModelStatementSegment"),
        ],
    )


@hive_dialect.segment(replace=True)
class InsertStatementSegment(BaseSegment):
    """An `INSERT` statement.

    Full Apache Hive `INSERT` reference here:
    https://cwiki.apache.org/confluence/display/Hive/LanguageManual+DML
    """

    type = "insert_statement"
    match_grammar = StartsWith("INSERT")
    parse_grammar = Sequence(
        "INSERT",
        OneOf(
            Sequence(
                "OVERWRITE",
                OneOf(
                    Sequence(
                        "TABLE",
                        Ref("TableReferenceSegment"),
                        Ref("PartitionSpecGrammar", optional=True),
                        Ref("IfNotExistsGrammar", optional=True),
                        Ref("SelectableGrammar"),
                    ),
                    Sequence(
                        Sequence("LOCAL", optional=True),
                        "DIRECTORY",
                        Ref("SingleOrDoubleQuotedLiteralGrammar"),
                        Ref("RowFormatClauseSegment", optional=True),
                        Ref("StoredAsGrammar", optional=True),
                        Ref("SelectableGrammar"),
                    ),
                ),
            ),
            Sequence(
                "INTO",
                "TABLE",
                Ref("TableReferenceSegment"),
                Ref("PartitionSpecGrammar", optional=True),
                OneOf(
                    Ref("SelectableGrammar"),
                    Ref("ValuesClauseSegment"),
                ),
            ),
        ),
    )


@hive_dialect.segment(replace=True)
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
