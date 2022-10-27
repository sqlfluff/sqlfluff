"""The Hive dialect."""
from typing import Optional

from sqlfluff.core.parser import (
    AnyNumberOf,
    BaseSegment,
    Sequence,
    Ref,
    OneOf,
    Bracketed,
    Delimited,
    TypedParser,
    Nothing,
    SymbolSegment,
    StringParser,
    OptionallyBracketed,
    RegexParser,
    Matchable,
    StartsWith,
    Indent,
    Dedent,
)

from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.core.parser.segments.raw import CodeSegment, KeywordSegment
from sqlfluff.dialects.dialect_hive_keywords import (
    RESERVED_KEYWORDS,
    UNRESERVED_KEYWORDS,
)
from sqlfluff.dialects import dialect_ansi as ansi

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
    StartAngleBracketSegment=StringParser(
        "<", SymbolSegment, type="start_angle_bracket"
    ),
    EndAngleBracketSegment=StringParser(">", SymbolSegment, type="end_angle_bracket"),
    JsonfileKeywordSegment=StringParser("JSONFILE", KeywordSegment, type="file_format"),
    RcfileKeywordSegment=StringParser("RCFILE", KeywordSegment, type="file_format"),
    SequencefileKeywordSegment=StringParser(
        "SEQUENCEFILE", KeywordSegment, type="file_format"
    ),
    TextfileKeywordSegment=StringParser("TEXTFILE", KeywordSegment, type="file_format"),
    LocationGrammar=Sequence("LOCATION", Ref("QuotedLiteralSegment")),
    PropertyGrammar=Sequence(
        Ref("QuotedLiteralSegment"),
        Ref("EqualsSegment"),
        Ref("QuotedLiteralSegment"),
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
        ansi.IdentifierSegment,
        type="quoted_identifier",
    ),
)

# https://cwiki.apache.org/confluence/display/hive/languagemanual+joins
hive_dialect.replace(
    JoinKeywordsGrammar=Sequence(Sequence("SEMI", optional=True), "JOIN"),
    QuotedLiteralSegment=OneOf(
        TypedParser("single_quote", ansi.LiteralSegment, type="quoted_literal"),
        TypedParser("double_quote", ansi.LiteralSegment, type="quoted_literal"),
        TypedParser("back_quote", ansi.LiteralSegment, type="quoted_literal"),
    ),
    SimpleArrayTypeGrammar=Ref.keyword("ARRAY"),
    TrimParametersGrammar=Nothing(),
    SingleIdentifierGrammar=ansi_dialect.get_grammar("SingleIdentifierGrammar").copy(
        insert=[
            Ref("BackQuotedIdentifierSegment"),
        ]
    ),
    SelectClauseElementTerminatorGrammar=ansi_dialect.get_grammar(
        "SelectClauseElementTerminatorGrammar"
    ).copy(
        insert=[
            Sequence("CLUSTER", "BY"),
            Sequence("DISTRIBUTE", "BY"),
            Sequence("SORT", "BY"),
        ],
        before=Sequence("ORDER", "BY"),
    ),
    FromClauseTerminatorGrammar=ansi_dialect.get_grammar(
        "FromClauseTerminatorGrammar"
    ).copy(
        insert=[
            Sequence("CLUSTER", "BY"),
            Sequence("DISTRIBUTE", "BY"),
            Sequence("SORT", "BY"),
        ],
        before=Sequence("ORDER", "BY"),
    ),
    WhereClauseTerminatorGrammar=ansi_dialect.get_grammar(
        "WhereClauseTerminatorGrammar"
    ).copy(
        insert=[
            Sequence("CLUSTER", "BY"),
            Sequence("DISTRIBUTE", "BY"),
            Sequence("SORT", "BY"),
        ],
        before=Sequence("ORDER", "BY"),
    ),
    GroupByClauseTerminatorGrammar=OneOf(
        Sequence(
            OneOf("ORDER", "CLUSTER", "DISTRIBUTE", "SORT"),
            "BY",
        ),
        "LIMIT",
        "HAVING",
        "QUALIFY",
        "WINDOW",
    ),
    HavingClauseTerminatorGrammar=OneOf(
        Sequence(
            OneOf(
                "ORDER",
                "CLUSTER",
                "DISTRIBUTE",
                "SORT",
            ),
            "BY",
        ),
        "LIMIT",
        "QUALIFY",
        "WINDOW",
    ),
    # Full Apache Hive `CREATE ALTER` reference here:
    # https://cwiki.apache.org/confluence/display/Hive/LanguageManual+DDL#LanguageManualDDL-AlterTable
    AlterTableOptionsGrammar=ansi_dialect.get_grammar("AlterTableOptionsGrammar").copy(
        insert=[
            # Exchange
            Sequence(
                "EXCHANGE",
                Ref("PartitionSpecGrammar"),
                "WITH",
                "TABLE",
                Ref("TableReferenceSegment"),
            ),
        ]
    ),
)


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
        Sequence("MANAGEDLOCATION", Ref("QuotedLiteralSegment"), optional=True),
        Sequence(
            "WITH", "DBPROPERTIES", Ref("BracketedPropertyListGrammar"), optional=True
        ),
    )


class CreateTableStatementSegment(BaseSegment):
    """A `CREATE TABLE` statement.

    Full Apache Hive `CREATE TABLE` reference here:
    https://cwiki.apache.org/confluence/display/hive/languagemanual+ddl#LanguageManualDDL-CreateTable
    """

    type = "create_table_statement"
    match_grammar = Sequence(
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


class FromExpressionElementSegment(ansi.FromExpressionElementSegment):
    """Modified from ANSI to allow for `LATERAL VIEW` clause."""

    match_grammar = ansi.FromExpressionElementSegment.match_grammar.copy(
        insert=[
            AnyNumberOf(Ref("LateralViewClauseSegment")),
        ],
        after=Ref("SamplingExpressionSegment"),
    )


class LateralViewClauseSegment(BaseSegment):
    """A `LATERAL VIEW` in a `FROM` clause.

    https://cwiki.apache.org/confluence/display/hive/languagemanual+lateralview
    """

    type = "lateral_view_clause"

    match_grammar = Sequence(
        Indent,
        "LATERAL",
        "VIEW",
        Ref.keyword("OUTER", optional=True),
        Ref("FunctionSegment"),
        # NB: AliasExpressionSegment is not used here for table
        # or column alias because `AS` is optional within it
        # (and in most scenarios). Here it's explicitly defined
        # for when it is required and not allowed.
        Ref("SingleIdentifierGrammar", optional=True),
        Sequence(
            "AS",
            Delimited(
                Ref("SingleIdentifierGrammar"),
            ),
        ),
        Dedent,
    )


class PrimitiveTypeSegment(BaseSegment):
    """Primitive data types."""

    type = "primitive_type"
    match_grammar = OneOf(
        "TINYINT",
        "SMALLINT",
        "INT",
        "INTEGER",
        "BIGINT",
        "BOOLEAN",
        "FLOAT",
        Sequence("DOUBLE", Ref.keyword("PRECISION", optional=True)),
        "STRING",
        "BINARY",
        "TIMESTAMP",
        Sequence(
            OneOf("DECIMAL", "DEC", "NUMERIC"),
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
        "JSON",
    )


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
        # array types
        OneOf(
            AnyNumberOf(
                Bracketed(
                    Ref("ExpressionSegment", optional=True), bracket_type="square"
                )
            ),
            Ref("SimpleArrayTypeGrammar"),
            Sequence(Ref("SimpleArrayTypeGrammar"), Ref("ArrayLiteralSegment")),
            optional=True,
        ),
    )


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
                Ref("QuotedLiteralSegment"),
            ),
            Ref("LocationGrammar"),
            Sequence("MANAGEDLOCATION", Ref("QuotedLiteralSegment")),
        ),
    )


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


class TruncateStatementSegment(BaseSegment):
    """`TRUNCATE TABLE` statement."""

    type = "truncate_table"

    match_grammar = Sequence(
        "TRUNCATE",
        Ref.keyword("TABLE", optional=True),
        Ref("TableReferenceSegment"),
        Ref("PartitionSpecGrammar", optional=True),
    )


class StatementSegment(ansi.StatementSegment):
    """Overriding StatementSegment to allow for additional segment parsing."""

    parse_grammar = ansi.StatementSegment.parse_grammar.copy(
        insert=[
            Ref("AlterDatabaseStatementSegment"),
            Ref("MsckRepairTableStatementSegment"),
            Ref("MsckTableStatementSegment"),
        ],
        remove=[
            Ref("TransactionStatementSegment"),
            Ref("CreateSchemaStatementSegment"),
            Ref("SetSchemaStatementSegment"),
            Ref("CreateModelStatementSegment"),
            Ref("DropModelStatementSegment"),
        ],
    )
    match_grammar = ansi.StatementSegment.match_grammar


class InsertStatementSegment(BaseSegment):
    """An `INSERT` statement.

    Full Apache Hive `INSERT` reference here:
    https://cwiki.apache.org/confluence/display/Hive/LanguageManual+DML
    """

    type = "insert_statement"
    match_grammar = Sequence(
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
                        Ref("QuotedLiteralSegment"),
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


class MsckRepairTableStatementSegment(BaseSegment):
    """An `MSCK REPAIR TABLE`statement.

    Updates the Hive metastore to be aware of any changes to partitions on the
    underlying file store.

    The `MSCK TABLE` command, and corresponding class in Hive dialect
    MsckTableStatementSegment, is used to determine mismatches between the Hive
    metastore and file system. Essentially, it is a dry run of the `MSCK REPAIR TABLE`
    command.

    https://cwiki.apache.org/confluence/display/Hive/LanguageManual+DDL#LanguageManualDDL-RecoverPartitions(MSCKREPAIRTABLE)
    """

    type = "msck_repair_table_statement"

    match_grammar = Sequence(
        "MSCK",
        "REPAIR",
        "TABLE",
        Ref("TableReferenceSegment"),
        Sequence(
            OneOf(
                "ADD",
                "DROP",
                "SYNC",
            ),
            "PARTITIONS",
            optional=True,
        ),
    )


class MsckTableStatementSegment(BaseSegment):
    """An `MSCK TABLE`statement.

    Checks for difference between partition metadata in the Hive metastore and
    underlying file system.

    Commonly used prior to `MSCK REPAIR TABLE` command, corresponding with class
    `MsckRepairTableStatementSegment` in Hive dialect, to asses size of updates for
    one-time or irregularly sized file system updates.

    https://cwiki.apache.org/confluence/display/Hive/LanguageManual+DDL#LanguageManualDDL-RecoverPartitions(MSCKREPAIRTABLE)
    """

    type = "msck_table_statement"

    match_grammar = Sequence(
        "MSCK",
        "TABLE",
        Ref("TableReferenceSegment"),
        Sequence(
            OneOf(
                "ADD",
                "DROP",
                "SYNC",
            ),
            "PARTITIONS",
            optional=True,
        ),
    )


class FunctionSegment(BaseSegment):
    """A scalar or aggregate function.

    Extended version of `ansi` to add support of row typecasting
    https://prestodb.io/docs/current/language/types.html#row
    ```
    cast(row(val1, val2) as row(a integer, b integer))
    ```
    """

    type = "function"
    match_grammar = OneOf(
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
                            ephemeral_name="FunctionContentsGrammar",
                        ),
                    )
                ),
            ),
        ),
        Sequence(
            # This unusual syntax is used to cast the Keyword ROW to
            # to the function_name to avoid rule linting exceptions
            StringParser("ROW", KeywordSegment, type="function_name"),
            Bracketed(
                Delimited(
                    Sequence(
                        Ref("BaseExpressionElementGrammar"),
                    ),
                ),
            ),
            "AS",
            "ROW",
            Bracketed(
                Delimited(
                    Sequence(
                        Ref("SingleIdentifierGrammar"),
                        Ref("DatatypeSegment", optional=True),
                    ),
                ),
            ),
        ),
        Sequence(
            Sequence(
                Ref(
                    "FunctionNameSegment",
                    exclude=OneOf(
                        Ref("DatePartFunctionNameSegment"),
                        Ref("ValuesClauseSegment"),
                    ),
                ),
                Bracketed(
                    Ref(
                        "FunctionContentsGrammar",
                        # The brackets might be empty for some functions...
                        optional=True,
                        ephemeral_name="FunctionContentsGrammar",
                    )
                ),
            ),
            Ref("PostFunctionGrammar", optional=True),
        ),
    )


class SamplingExpressionSegment(BaseSegment):
    """A sampling expression."""

    type = "sample_expression"
    match_grammar = Sequence(
        "TABLESAMPLE",
        Bracketed(
            OneOf(
                Sequence(
                    "BUCKET",
                    Ref("NumericLiteralSegment"),
                    "OUT",
                    "OF",
                    Ref("NumericLiteralSegment"),
                    Sequence(
                        "ON",
                        OneOf(
                            Ref("SingleIdentifierGrammar"),
                            Ref("FunctionSegment"),
                        ),
                        optional=True,
                    ),
                ),
                Sequence(
                    Ref("NumericLiteralSegment"),
                    OneOf("PERCENT", "ROWS", optional=True),
                ),
                RegexParser(
                    r"\d+[bBkKmMgG]",
                    CodeSegment,
                    type="byte_length_literal",
                ),
            ),
        ),
        Ref(
            "AliasExpressionSegment",
            optional=True,
        ),
    )


class UnorderedSelectStatementSegment(ansi.UnorderedSelectStatementSegment):
    """Enhance unordered SELECT statement to include CLUSTER, DISTRIBUTE, SORT BY."""

    match_grammar = ansi.UnorderedSelectStatementSegment.match_grammar.copy()
    match_grammar.terminator = match_grammar.terminator.copy(  # type: ignore
        insert=[
            Ref("ClusterByClauseSegment"),
            Ref("DistributeByClauseSegment"),
            Ref("SortByClauseSegment"),
        ],
        before=Ref("LimitClauseSegment"),
    )

    parse_grammar = ansi.UnorderedSelectStatementSegment.parse_grammar.copy()


class SelectStatementSegment(ansi.SelectStatementSegment):
    """Overriding SelectStatementSegment to allow for additional segment parsing."""

    match_grammar = ansi.SelectStatementSegment.match_grammar.copy()
    parse_grammar = ansi.SelectStatementSegment.parse_grammar.copy(
        insert=[
            Ref("ClusterByClauseSegment", optional=True),
            Ref("DistributeByClauseSegment", optional=True),
            Ref("SortByClauseSegment", optional=True),
        ],
        before=Ref("LimitClauseSegment", optional=True),
    )


class SelectClauseSegment(ansi.SelectClauseSegment):
    """Overriding SelectClauseSegment to allow for additional segment parsing."""

    match_grammar = ansi.SelectClauseSegment.match_grammar.copy()
    match_grammar.terminator = match_grammar.terminator.copy(  # type: ignore
        insert=[
            Sequence("CLUSTER", "BY"),
            Sequence("DISTRIBUTE", "BY"),
            Sequence("SORT", "BY"),
        ],
        before=Ref.keyword("LIMIT"),
    )
    parse_grammar = ansi.SelectClauseSegment.parse_grammar.copy()


class SetExpressionSegment(ansi.SetExpressionSegment):
    """Overriding SetExpressionSegment to allow for additional segment parsing."""

    match_grammar = ansi.SetExpressionSegment.match_grammar.copy(
        insert=[
            Ref("ClusterByClauseSegment", optional=True),
            Ref("DistributeByClauseSegment", optional=True),
            Ref("SortByClauseSegment", optional=True),
        ],
        before=Ref("LimitClauseSegment", optional=True),
    )


class PartitionClauseSegment(ansi.PartitionClauseSegment):
    """Overriding SetExpressionSegment to allow for additional segment parsing."""

    match_grammar = ansi.PartitionClauseSegment.match_grammar.copy()
    match_grammar.terminator = match_grammar.terminator.copy(  # type: ignore
        insert=[
            Sequence("CLUSTER", "BY"),
            Sequence("DISTRIBUTE", "BY"),
            Sequence("SORT", "BY"),
        ],
        before=Ref("FrameClauseUnitGrammar"),
    )
    parse_grammar = ansi.PartitionClauseSegment.parse_grammar


class OrderByClauseSegment(ansi.OrderByClauseSegment):
    """A `ORDER BY` clause like in `SELECT`."""

    match_grammar = ansi.OrderByClauseSegment.match_grammar.copy()
    match_grammar.terminator = OneOf(  # type: ignore
        "CLUSTER",
        "DISTRIBUTE",
        "SORT",
        "LIMIT",
        "HAVING",
        "QUALIFY",
        # For window functions
        "WINDOW",
        Ref("FrameClauseUnitGrammar"),
        "SEPARATOR",
    )
    parse_grammar = ansi.OrderByClauseSegment.parse_grammar


class ClusterByClauseSegment(ansi.OrderByClauseSegment):
    """A `CLUSTER BY` clause like in `SELECT`."""

    type = "clusterby_clause"
    match_grammar: Matchable = StartsWith(
        Sequence("CLUSTER", "BY"),
        terminator=ansi.OrderByClauseSegment.match_grammar.terminator,  # type: ignore
    )
    parse_grammar: Optional[Matchable] = Sequence(
        "CLUSTER",
        "BY",
        Indent,
        Delimited(
            Sequence(
                OneOf(
                    Ref("ColumnReferenceSegment"),
                    Ref("NumericLiteralSegment"),
                    Ref("ExpressionSegment"),
                ),
            ),
            terminator=OneOf(Ref.keyword("LIMIT"), Ref("FrameClauseUnitGrammar")),
        ),
        Dedent,
    )


class DistributeByClauseSegment(ansi.OrderByClauseSegment):
    """A `DISTRIBUTE BY` clause like in `SELECT`."""

    type = "distributeby_clause"
    match_grammar: Matchable = StartsWith(
        Sequence("DISTRIBUTE", "BY"),
        terminator=OneOf(
            "SORT",
            "LIMIT",
            "HAVING",
            "QUALIFY",
            # For window functions
            "WINDOW",
            Ref("FrameClauseUnitGrammar"),
            "SEPARATOR",
        ),
    )
    parse_grammar: Optional[Matchable] = Sequence(
        "DISTRIBUTE",
        "BY",
        Indent,
        Delimited(
            Sequence(
                OneOf(
                    Ref("ColumnReferenceSegment"),
                    Ref("NumericLiteralSegment"),
                    Ref("ExpressionSegment"),
                ),
            ),
            terminator=OneOf(
                Ref.keyword("LIMIT"), Ref("FrameClauseUnitGrammar"), Ref.keyword("SORT")
            ),
        ),
        Dedent,
    )


class SortByClauseSegment(ansi.OrderByClauseSegment):
    """A `SORT BY` clause like in `SELECT`."""

    type = "sortby_clause"
    match_grammar: Matchable = StartsWith(
        Sequence("SORT", "BY"),
        terminator=ansi.OrderByClauseSegment.match_grammar.terminator,  # type: ignore
    )
    parse_grammar: Optional[Matchable] = Sequence(
        "SORT",
        "BY",
        Indent,
        Delimited(
            Sequence(
                OneOf(
                    Ref("ColumnReferenceSegment"),
                    Ref("NumericLiteralSegment"),
                    Ref("ExpressionSegment"),
                ),
                OneOf("ASC", "DESC", optional=True),
                Sequence("NULLS", OneOf("FIRST", "LAST"), optional=True),
            ),
            terminator=OneOf(Ref.keyword("LIMIT"), Ref("FrameClauseUnitGrammar")),
        ),
        Dedent,
    )
