"""The Vertica dialect.
"""

from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.core.parser import (
    AnyNumberOf,
    BaseSegment,
    Bracketed,
    Dedent,
    Delimited,
    Indent,
    KeywordSegment,
    Matchable,
    MultiStringParser,
    OneOf,
    OptionallyBracketed,
    Ref,
    Sequence,
    RegexParser,
    LiteralSegment,
)
from sqlfluff.dialects import dialect_ansi as ansi
from sqlfluff.dialects.dialect_vertica_keywords import (
    vertica_reserved_keywords,
    vertica_unreserved_keywords,
)

from sqlfluff.dialects.dialect_ansi_keywords import (
    ansi_reserved_keywords,
    ansi_unreserved_keywords,
)

ansi_dialect = load_raw_dialect("ansi")
vertica_dialect = ansi_dialect.copy_as("vertica")

# Set Keywords
vertica_dialect.sets("unreserved_keywords").clear()
vertica_dialect.update_keywords_set_from_multiline_string(
    "unreserved_keywords", vertica_unreserved_keywords
)
vertica_dialect.update_keywords_set_from_multiline_string(
    "unreserved_keywords", ansi_unreserved_keywords
)

vertica_dialect.sets("reserved_keywords").clear()
vertica_dialect.update_keywords_set_from_multiline_string(
    "reserved_keywords", vertica_reserved_keywords
)
vertica_dialect.update_keywords_set_from_multiline_string(
    "reserved_keywords", ansi_reserved_keywords
)

vertica_dialect.sets("bare_functions").clear()
vertica_dialect.sets("bare_functions").update(
    ["CURRENT_TIMESTAMP", "CURRENT_TIME", "CURRENT_DATE", "LOCALTIME", "LOCALTIMESTAMP", "SYSDATE"]
)

# Add all Vertica encoding types
vertica_dialect.sets("encoding_types").clear()
vertica_dialect.sets("encoding_types").update(
    [
        "AUTO",
        "BLOCK_DICT",
        "BLOCKDICT_COMP",
        "BZIP_COMP",
        "COMMONDELTA_COMP",
        "DELTARANGE_COMP",
        "DELTAVAL",
        "GCDDELTA",
        "GZIP_COMP",
        "RLE",
        "ZSTD_COMP",
        "ZSTD_FAST_COMP",
        "ZSTD_HIGH_COMP"
    ],
)

vertica_dialect.sets("date_part_function_name").update(
    ["DATEADD", "DATEDIFF", "EXTRACT", "DATE_PART"]
)

# Add datetime units
# https://docs.vertica.com/latest/en/sql-reference/functions/data-type-specific-functions/datetime-functions/date-part/
vertica_dialect.sets("datetime_units").update(
    [
        # millennium
        "MILLENNIUM",
        # century
        "CENTURY",
        # decade
        "DECADE",
        # epoch
        "EPOCH",
        # year
        "YEAR",
        "ISOYEAR",
        # quarter
        "QUARTER",
        # month
        "MONTH",
        # week
        "WEEK",
        "ISOWEEK",
        # day of week
        "ISODOW",
        "DOW",
        # day of year
        "DOY",
        # day
        "DAY",
        # hour
        "HOUR",
        # minute
        "MINUTE",
        # second
        "SECOND",
        # millisec
        "MILLISECONDS",
        # microsec
        "MICROSECONDS",
        # timezone
        "TIME ZONE",
        "TIMEZONE_HOUR",
        "TIMEZONE_MINUTE",
    ]
)

vertica_dialect.add(
    EncodingType=OneOf(
        MultiStringParser(
            vertica_dialect.sets("encoding_types"),
            KeywordSegment,
            type="encoding_type",
        ),
        MultiStringParser(
            [
                f"'{compression}'"
                for compression in vertica_dialect.sets("encoding_types")
            ],
            KeywordSegment,
            type="encoding_type",
        ),
    ),
    IntegerSegment=RegexParser(
        # An unquoted integer that can be passed as an argument to Snowflake functions.
        r"[0-9]+",
        LiteralSegment,
        type="integer_literal",
    ),
)


class StatementSegment(ansi.StatementSegment):
    """A generic segment, to any of its child subsegments."""

    match_grammar = ansi.StatementSegment.match_grammar.copy(
        insert=[
            Ref("CreateExternalTableSegment"),
            Ref("CreateTableLikeStatementSegment"),
            Ref("CreateTableAsStatementSegment")
        ],
    )


class ExtendedCastOperatorSegment(BaseSegment):
    """Allow ::! operator as in
    https://docs.vertica.com/latest/en/sql-reference/language-elements/operators/data-type-coercion-operators-cast/cast-failures/"""

    type = "extended_cast_operator"
    match_grammar: Matchable = OneOf(
        Sequence(Ref("CastOperatorSegment"), Ref("RawNotSegment"), allow_gaps=False),
        Ref("CastOperatorSegment"),
    )


class ShorthandCastSegment(BaseSegment):
    """A casting operation using '::' or '::!'."""

    type = "cast_expression"
    match_grammar: Matchable = Sequence(
        OneOf(
            Ref("Expression_D_Grammar"),
            Ref("CaseExpressionSegment"),
        ),
        AnyNumberOf(
            Sequence(
                Ref("ExtendedCastOperatorSegment"),
                Ref("DatatypeSegment"),
                Ref("TimeZoneGrammar", optional=True),
            ),
            min_times=1,
        ),
    )


class LimitClauseSegment(ansi.LimitClauseSegment):
    """
    A vertica `LIMIT` clause.
    https://docs.vertica.com/latest/en/sql-reference/statements/select/limit-clause/
    """
    match_grammar: Matchable = Sequence(
        "LIMIT",
        Indent,
        OptionallyBracketed(
            OneOf(
                # Allow a number by itself OR
                Ref("NumericLiteralSegment"),
                # An arbitrary expression
                Ref("ExpressionSegment"),
                "ALL",
            )
        ),
        OneOf(
            Sequence(
                "OFFSET",
                OneOf(
                    # Allow a number by itself OR
                    Ref("NumericLiteralSegment"),
                    # An arbitrary expression
                    Ref("ExpressionSegment"),
                ),
            ),
            Sequence(
                Ref("CommaSegment"),
                Ref("NumericLiteralSegment"),
            ),
            Ref("OverClauseSegment"),
            optional=True,
        ),
        Dedent,
    )


class ColumnEncodingSegment(BaseSegment):
    """The `ENCODING` clause within a `CREATE TABLE` statement for a column."""
    type = "column_encoding"
    match_grammar: Matchable = Sequence(
        "ENCODING",
        Ref("EncodingType"),
    )


class TableConstraintSegment(ansi.TableConstraintSegment):
    """A table constraint, e.g. for CREATE TABLE.

    As specified in
    https://docs.vertica.com/latest/en/sql-reference/statements/create-statements/create-table/table-constraint/
    """

    match_grammar = Sequence(
        Sequence(  # [ CONSTRAINT <Constraint name> ]
            "CONSTRAINT", Ref("ObjectReferenceSegment"), optional=True
        ),
        OneOf(
            Sequence(  # PRIMARY KEY (column[,...]) [ ENABLED | DISABLED]
                Ref("PrimaryKeyGrammar"),
                # Columns making up PRIMARY KEY constraint
                Ref("BracketedColumnReferenceListGrammar"),
                OneOf("ENABLED", "DISABLED", optional=True),
            ),
            Sequence(
                "CHECK",
                Bracketed(Ref("ExpressionSegment")),
                OneOf("ENABLED", "DISABLED", optional=True),
            ),
            Sequence(  # UNIQUE (column[,...]) [ENABLED | DISABLED]
                "UNIQUE",
                Ref("BracketedColumnReferenceListGrammar"),
                OneOf("ENABLED", "DISABLED", optional=True),
            ),
            Sequence(  # FOREIGN KEY ( column_name [, ... ] )
                # REFERENCES reftable [ ( refcolumn [, ... ] ) ]
                "FOREIGN",
                "KEY",
                # Local columns making up FOREIGN KEY constraint
                Ref("BracketedColumnReferenceListGrammar"),
                Ref(
                    "ReferenceDefinitionGrammar"
                ),  # REFERENCES reftable [ ( refcolumn) ]
            ),
        )
    )


class LikeOptionSegment(BaseSegment):
    """Like Option Segment.

    As specified in
    https://docs.vertica.com/latest/en/admin/working-with-native-tables/creating-table-from-other-tables/replicating-table/
    """

    type = "like_option_segment"

    match_grammar = Sequence(
        OneOf(
            Sequence(
                OneOf("INCLUDING", "EXCLUDING"),
                "PROJECTIONS"
            ),
            Ref("SchemaPrivilegesSegment")
        ),
    )


class DiskQuotaSegment(BaseSegment):
    """Disk Quota Segment.

    As specified in https://docs.vertica.com/latest/en/admin/working-with-native-tables/disk-quotas/
    Available from Vertica 12.x
    """

    type = "disk_quota_segment"

    match_grammar = Sequence(
        "DISK",
        "QUOTA",
        Ref("QuotedLiteralSegment")
    )


class KsafeSegment(BaseSegment):
    """Ksafe Segment.

    As specified in https://docs.vertica.com/latest/en/sql-reference/statements/create-statements/create-table/
    More details in https://docs.vertica.com/latest/en/architecture/enterprise-concepts/k-safety-an-enterprise-db/
    """

    type = "ksafe_segment"

    match_grammar = Sequence(
        "KSAFE",
        Ref("NumericLiteralSegment", optional=True),
    )


class SchemaPrivilegesSegment(BaseSegment):
    """Schema Privileges Segment.
    As specified in https://docs.vertica.com/latest/en/sql-reference/statements/create-statements/create-table/
    """

    type = "schema_privileges_segment"
    match_grammar: Matchable = Sequence(
        OneOf("INCLUDE", "EXCLUDE"),
        Sequence("SCHEMA", optional=True),
        "PRIVILEGES",
    )


class SegmentedByClauseSegment(BaseSegment):
    """A `SEGMENTED BY` or `UNSEGMENTED` clause.

    As specified in
    https://docs.vertica.com/latest/en/sql-reference/statements/create-statements/create-projection/hash-segmentation-clause/
    Vertica allows different expressions in segmented by clause but using hash function is recommended one
    As specified in
    https://docs.vertica.com/latest/en/sql-reference/statements/create-statements/create-projection/unsegmented-clause/
    """

    type = "segmentedby_clause"
    match_grammar: Matchable = Sequence(
        OneOf(
            Sequence("UNSEGMENTED", "ALL", "NODES"),
            Sequence(
                "SEGMENTED",
                "BY",
                OneOf(
                    Ref("FunctionSegment"),
                    Bracketed(
                        Delimited(
                            Sequence(
                                OneOf(
                                    Ref("ColumnReferenceSegment"),
                                    Ref("NumericLiteralSegment"),
                                    Ref("ExpressionSegment"),
                                    Ref("ShorthandCastSegment"),
                                ),
                            ),
                        ),
                    ),
                ),
                "ALL",
                "NODES",
            ),
        ),
    )


class PartitionByClauseSegment(BaseSegment):
    """A `PARTITION BY` clause.

    As specified in
    https://docs.vertica.com/latest/en/sql-reference/statements/create-statements/create-table/partition-clause/
    """

    type = "partitionby_clause"
    match_grammar: Matchable = Sequence(
        "PARTITION",
        "BY",
        AnyNumberOf(
            Delimited(
                Sequence(
                    AnyNumberOf(
                        Ref("ColumnReferenceSegment"),
                        Ref("FunctionSegment"),
                        Ref("ShorthandCastSegment"),
                    ),
                ),
            ),
            Bracketed(
                Delimited(
                    Sequence(
                        AnyNumberOf(
                            Ref("ColumnReferenceSegment"),
                            Ref("FunctionSegment"),
                            Ref("ShorthandCastSegment"),
                        ),
                    ),
                ),
            ),
        ),
        Sequence(
            "GROUP",
            "BY",
            OneOf(
                Ref("FunctionSegment"),
                Bracketed(
                    Delimited(
                        Sequence(
                            OneOf(
                                Ref("ColumnReferenceSegment"),
                                Ref("NumericLiteralSegment"),
                                Ref("ExpressionSegment"),
                                Ref("ShorthandCastSegment"),
                            ),
                        ),
                    ),
                ),
            ),
            optional=True,
        ),
    )


class CreateTableStatementSegment(ansi.CreateTableStatementSegment):
    """A `CREATE TABLE` statement.

    As specified in https://docs.vertica.com/latest/en/sql-reference/statements/create-statements/create-table/
    """

    match_grammar = Sequence(
        "CREATE",
        OneOf(
            Sequence(
                OneOf("GLOBAL", "LOCAL", optional=True),
                Ref("TemporaryGrammar", optional=True),
            ),
            optional=True,
        ),
        "TABLE",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        Sequence(
            Bracketed(
                Delimited(
                    Sequence(
                        Ref("ColumnReferenceSegment"),
                        Ref("DatatypeSegment"),
                        AnyNumberOf(
                            Ref("ColumnConstraintSegment"),
                            Ref("ColumnEncodingSegment"),
                            Sequence("ACCESSRANK", Ref("IntegerSegment"))
                        ),
                    ),
                    Ref("TableConstraintSegment"),
                ),
            ),
        ),
        AnyNumberOf(
            Ref("OrderByClauseSegment"),
            Ref("SegmentedByClauseSegment"),
            Ref("KsafeSegment"),
            Ref("SchemaPrivilegesSegment"),
            Ref("DiskQuotaSegment"),
            Ref("PartitionByClauseSegment"),
        ),
    )


class CreateTableAsStatementSegment(BaseSegment):
    """A `CREATE TABLE AS` statement.

    As specified in
    https://docs.vertica.com/latest/en/admin/working-with-native-tables/creating-table-from-other-tables/creating-table-from-query/
    """

    type = "create_table_as_statement"

    match_grammar = Sequence(
        "CREATE",
        "TABLE",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        AnyNumberOf(
            Bracketed(
                Delimited(
                    Sequence(
                        Ref("ColumnReferenceSegment"),
                        Ref("ColumnEncodingSegment", optional=True),
                        Sequence("ACCESSRANK", Ref("IntegerSegment")),
                        # TODO: need to add GROUPED clause
                        #  https://docs.vertica.com/latest/en/sql-reference/statements/create-statements/create-projection/grouped-clause/
                    ),
                ),
                optional=True,
            ),
            Ref("SchemaPrivilegesSegment", optional=True),
        ),
        "AS",
        # TODO: need to add LABEL clause
        #  https://docs.vertica.com/latest/en/admin/working-with-native-tables/creating-table-from-other-tables/creating-table-from-query/
        Sequence("AT", OneOf("LATEST", Ref("NumericLiteralSegment"), Ref("DatetimeUnitSegment")), optional=True),
        OneOf(
            OptionallyBracketed(Ref("SelectableGrammar")),
            OptionallyBracketed(Sequence("TABLE", Ref("TableReferenceSegment"))),
            Ref("ValuesClauseSegment"),
            OptionallyBracketed(Sequence("EXECUTE", Ref("FunctionSegment"))),
        ),
        Ref("SegmentedByClauseSegment", optional=True)
    )


class CreateTableLikeStatementSegment(BaseSegment):
    """A `CREATE TABLE LIKE` statement.

    As specified in
    https://docs.vertica.com/latest/en/admin/working-with-native-tables/creating-table-from-other-tables/replicating-table/
    """

    type = "create_table_like_statement"

    match_grammar = Sequence(
        "CREATE",
        "TABLE",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        Sequence(
            "LIKE",
            Ref("TableReferenceSegment"),
            AnyNumberOf(Ref("LikeOptionSegment"), optional=True),
        ),
        Ref("DiskQuotaSegment", optional=True),
    )


class CopyOptionsSegment(BaseSegment):
    """A vertica options for columns in COPY
    https://docs.vertica.com/latest/en/sql-reference/statements/copy/
    """

    type = "copy_options"

    match_grammar = Sequence(
        AnyNumberOf(
            Sequence(
                "DELIMITER",
                Sequence("AS", optional=True),
                Ref("QuotedLiteralSegment")
            ),
            Sequence(
                "ENCLOSED",
                Sequence("BY", optional=True),
                Ref("QuotedLiteralSegment")
            ),
            "ENFORCELENGTH",
            OneOf(
                Sequence(
                    "ESCAPE",
                    Sequence("AS", optional=True),
                    Ref("QuotedLiteralSegment")
                ),
                Sequence("NO", "ESCAPE")
            ),
            Sequence("FILLER", Ref("DatatypeSegment")),
            Sequence("FORMAT", OneOf("OCTAL", "HEX", "BITSTREAM")),
            Sequence(
                "NULL",
                Sequence("AS", optional=True),
                Ref("QuotedLiteralSegment")
            ),
            Sequence("TRIM", Ref("QuotedLiteralSegment"))
        )
    )


class CopyColumnOptionsSegment(BaseSegment):
    """A vertica options for columns in COPY
    https://docs.vertica.com/latest/en/sql-reference/statements/copy/
    """

    type = "copy_column_options"

    match_grammar = Sequence(
        Ref("ColumnReferenceSegment"),
        Ref("CopyOptionsSegment", optional=True)
    )


class CreateExternalTableSegment(BaseSegment):
    """A vertica `CREATE EXTERNAL TABLE` statement.

    https://docs.vertica.com/latest/en/sql-reference/statements/create-statements/create-external-table-as-copy/
    """

    type = "create_external_table_statement"

    match_grammar = Sequence(
        "CREATE",
        "EXTERNAL",
        "TABLE",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        # Columns:
        Sequence(
            Bracketed(
                Delimited(
                    Sequence(
                        Ref("ColumnReferenceSegment"),
                        Ref("DatatypeSegment"),
                        AnyNumberOf(
                            Ref("ColumnConstraintSegment"),
                            Ref("ColumnEncodingSegment"),
                            Sequence("ACCESSRANK", Ref("IntegerSegment"))
                        ),
                    ),
                    Ref("TableConstraintSegment"),
                ),
            ),
        ),
        Ref("SchemaPrivilegesSegment", optional=True),
        "AS",
        "COPY",
        OneOf(
            Bracketed(
                Delimited(
                    Sequence(
                        Ref("ColumnReferenceSegment"),
                        Ref("CopyColumnOptionsSegment", optional=True),
                    ),
                ),
            ),
            Sequence(
                "COLUMN",
                "OPTION",
                Bracketed(
                    Delimited(
                        Sequence(
                            Ref("ColumnReferenceSegment"),
                            Ref("CopyColumnOptionsSegment", optional=True),
                        ),
                    ),
                ),
            ),
            optional=True
        ),
        "FROM",
        Ref("QuotedLiteralSegment"),
        OneOf(
            "NATIVE",
            Sequence("NATIVE", "VARCHAR"),
            "ORC",
            "PARQUET",
        ),
        AnyNumberOf(
            # TODO: add WITH FILTER, WITH PARSER, and on nodename support
            Sequence("ABORT", "ON", "ERROR"),
            Sequence("ERROR", "TOLERANCE"),
            Sequence("EXCEPTION", Ref("QuotedLiteralSegment")),
            Sequence("RECORD", "TERMINATOR", Ref("QuotedLiteralSegment")),
            Sequence("REJECTED", "DATA", Ref("QuotedLiteralSegment")),
            Sequence("REJECTMAX", Ref("IntegerSegment")),
            Sequence("SKIP", Ref("IntegerSegment")),
            Sequence("SKIP", "BYTES", Ref("IntegerSegment")),
            Sequence("TRAILING", "NULLCOLS"),
            Ref("CopyOptionsSegment", optional=True)
        ),
    )
