"""The Vertica dialect.

https://docs.vertica.com/latest/en/
"""

from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.core.parser import (
    AnyNumberOf,
    AnySetOf,
    BaseSegment,
    Bracketed,
    BracketedSegment,
    CodeSegment,
    CompositeComparisonOperatorSegment,
    Dedent,
    Delimited,
    Indent,
    KeywordSegment,
    LiteralSegment,
    Matchable,
    MultiStringParser,
    OneOf,
    OptionallyBracketed,
    ParseMode,
    Ref,
    RegexParser,
    Sequence,
    StringLexer,
    StringParser,
    SymbolSegment,
    TypedParser,
)
from sqlfluff.dialects import dialect_ansi as ansi
from sqlfluff.dialects.dialect_vertica_keywords import (
    vertica_reserved_keywords,
    vertica_unreserved_keywords,
)

ansi_dialect = load_raw_dialect("ansi")
vertica_dialect = ansi_dialect.copy_as("vertica")

vertica_dialect.insert_lexer_matchers(
    # Allow ::! operator as in
    # https://docs.vertica.com/latest/en/sql-reference/language-elements/operators/data-type-coercion-operators-cast/cast-failures/
    [
        StringLexer("null_casting_operator", "::!", CodeSegment),
    ],
    before="casting_operator",
)

vertica_dialect.insert_lexer_matchers(
    # Allow <==> operator as in
    # https://docs.vertica.com/latest/en/sql-reference/language-elements/operators/comparison-operators/
    [
        StringLexer("null_equals_operator", "<=>", CodeSegment),
    ],
    before="less_than",
)

vertica_dialect.insert_lexer_matchers(
    # Allow additional math operators as in
    # https://docs.vertica.com/latest/en/sql-reference/language-elements/operators/mathematical-operators/
    # TODO: add other math operators
    [
        StringLexer("integer_division", "//", CodeSegment),
    ],
    before="divide",
)

# Set Keywords
vertica_dialect.update_keywords_set_from_multiline_string(
    "unreserved_keywords", vertica_unreserved_keywords
)

vertica_dialect.update_keywords_set_from_multiline_string(
    "reserved_keywords", vertica_reserved_keywords
)
vertica_dialect.sets("reserved_keywords").difference_update(["ROWS"])

vertica_dialect.sets("bare_functions").clear()
vertica_dialect.sets("bare_functions").update(
    [
        "CURRENT_TIMESTAMP",
        "CURRENT_TIME",
        "CURRENT_DATE",
        "LOCALTIME",
        "LOCALTIMESTAMP",
        "SYSDATE",
    ]
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
        "ZSTD_HIGH_COMP",
    ],
)

# Add all Vertica compression types (for COPY statement)
vertica_dialect.sets("compression_types").clear()
vertica_dialect.sets("compression_types").update(
    [
        "UNCOMPRESSED",
        "BZIP",
        "GZIP",
        "LZO",
        "ZSTD",
    ],
)

vertica_dialect.sets("date_part_function_name").update(
    ["DATEADD", "DATEDIFF", "EXTRACT", "DATE_PART"]
)

# Add datetime units
# https://docs.vertica.com/latest/en/sql-reference/functions/data-type-specific-functions/datetime-functions/date-part/
vertica_dialect.sets("datetime_units").update(
    [
        "MILLENNIUM",
        "CENTURY",
        "DECADE",
        "EPOCH",
        "YEAR",
        "ISOYEAR",
        "QUARTER",
        "MONTH",
        "WEEK",
        "ISOWEEK",
        "ISODOW",
        "DOW",
        "DOY",
        "DAY",
        "HOUR",
        "MINUTE",
        "SECOND",
        "MILLISECONDS",
        "MICROSECONDS",
        "TIME ZONE",
        "TIMEZONE_HOUR",
        "TIMEZONE_MINUTE",
    ]
)

vertica_dialect.add(
    EncodingType=Sequence(
        MultiStringParser(
            vertica_dialect.sets("encoding_types"),
            KeywordSegment,
            type="encoding_type",
        ),
    ),
    CompressionType=Sequence(
        MultiStringParser(
            vertica_dialect.sets("compression_types"),
            KeywordSegment,
            type="compression_type",
        )
    ),
    IntegerSegment=RegexParser(
        # An unquoted integer that can be passed as an argument to Snowflake functions.
        r"[0-9]+",
        LiteralSegment,
        type="integer_literal",
    ),
    NullCastOperatorSegment=StringParser(
        "::!", SymbolSegment, type="null_casting_operator"
    ),
    NullEqualsOperatorSegment=StringParser(
        "<=>", SymbolSegment, type="null_equals_operator"
    ),
    IntervalUnitsGrammar=OneOf("YEAR", "MONTH", "DAY", "HOUR", "MINUTE", "SECOND"),
    InterpolateGrammar=Sequence("INTERPOLATE", OneOf("PREVIOUS", "NEXT"), "VALUE"),
    IntervalLiteralGrammar=Sequence(
        Ref("IntervalUnitsGrammar"),
        Sequence(
            "TO",
            Sequence(
                Ref("IntervalUnitsGrammar"),
                Bracketed(Ref("IntegerSegment"), optional=True),
            ),
            optional=True,
        ),
    ),
    IntegerDivideSegment=StringParser("//", SymbolSegment, type="binary_operator"),
)

vertica_dialect.replace(
    FunctionContentsGrammar=AnyNumberOf(
        Ref("ExpressionSegment"),
        OptionallyBracketed(Ref("SetExpressionSegment")),
        # A Cast-like function
        Sequence(
            Ref("ExpressionSegment"),
            "AS",
            OneOf(Ref("DatatypeSegment"), Ref("DateTimeLiteralGrammar")),
        ),
        # Trim function
        Sequence(
            Ref("TrimParametersGrammar"),
            Ref("ExpressionSegment", optional=True, exclude=Ref.keyword("FROM")),
            "FROM",
            Ref("ExpressionSegment"),
        ),
        # An extract-like or substring-like function
        # https://www.postgresql.org/docs/current/functions-string.html
        Sequence(
            OneOf(Ref("DatetimeUnitSegment"), Ref("ExpressionSegment")),
            AnySetOf(
                Sequence("FROM", Ref("ExpressionSegment")),
                Sequence("FOR", Ref("ExpressionSegment")),
                optional=True,
            ),
        ),
        Sequence(
            # Allow an optional distinct keyword here.
            Ref.keyword("DISTINCT", optional=True),
            OneOf(
                # Most functions will be using the delimited route
                # but for COUNT(*) or similar we allow the star segment
                # here.
                Ref("StarSegment"),
                Delimited(Ref("FunctionContentsExpressionGrammar")),
            ),
        ),
        Ref(
            "AggregateOrderByClause"
        ),  # used by string_agg (postgres), group_concat (exasol),listagg (snowflake)..
        Sequence(Ref.keyword("SEPARATOR"), Ref("LiteralGrammar")),
        # like a function call: POSITION ( 'QL' IN 'SQL')
        Sequence(
            Ref("DatatypeSegment", optional=True),
            OneOf(
                Ref("QuotedLiteralSegment"),
                Ref("SingleIdentifierGrammar"),
                Ref("ColumnReferenceSegment"),
            ),
            "IN",
            Ref("DatatypeSegment", optional=True),
            OneOf(
                Ref("QuotedLiteralSegment"),
                Ref("SingleIdentifierGrammar"),
                Ref("ColumnReferenceSegment"),
            ),
        ),
        # used by listagg, explode, unnest
        Sequence(
            Ref.keyword("DISTINCT", optional=True),
            OneOf(
                Ref("QuotedLiteralSegment"),
                Ref("ColumnReferenceSegment"),
                Ref("ExpressionSegment"),
            ),
            Sequence(
                "USING",
                "PARAMETERS",
                Delimited(
                    Sequence(
                        Ref("ParameterNameSegment"),
                        Ref("EqualsSegment"),
                        OneOf(
                            Ref("QuotedLiteralSegment"),
                            Ref("BooleanLiteralGrammar"),
                            Ref("NumericLiteralSegment"),
                        ),
                    ),
                ),
            ),
            Ref("OverClauseSegment", optional=True),
        ),
        Ref("IgnoreRespectNullsGrammar"),
        Ref("EmptyStructLiteralSegment"),
    ),
    ObjectReferenceTerminatorGrammar=OneOf(
        "ON",
        "AS",
        "USING",
        Ref("CommaSegment"),
        Ref("CastOperatorSegment"),
        Ref("NullCastOperatorSegment"),
        Ref("StartSquareBracketSegment"),
        Ref("StartBracketSegment"),
        Ref("BinaryOperatorGrammar"),
        Ref("ColonSegment"),
        Ref("DelimiterGrammar"),
        Ref("JoinLikeClauseGrammar"),
        BracketedSegment,
    ),
    PostFunctionGrammar=OneOf(
        # Optional OVER suffix for window functions.
        # This is supported in bigquery & postgres (and its derivatives)
        # and so is included here for now.
        Ref("OverClauseSegment"),
        # Filter clause supported by both Postgres and SQLite
        Ref("FilterClauseGrammar"),
        # Within group clause supported by some analytic functions in Vertica
        Ref("WithinGroupClauseSegment"),
    ),
    DateTimeLiteralGrammar=Sequence(
        # analog of postgres dialect but with treating expressions like
        # as interval hour TO SECOND(6)
        OneOf("DATE", "TIME", "TIMESTAMP", "INTERVAL"),
        TypedParser(
            "single_quote",
            LiteralSegment,
            type="date_constructor_literal",
            optional=True,
        ),
        Ref("IntervalLiteralGrammar", optional=True),
    ),
    Expression_A_Grammar=Sequence(
        # It's a copy of ansi Expression_A_Grammar
        Ref("Tail_Recurse_Expression_A_Grammar"),
        AnyNumberOf(
            OneOf(
                Sequence(
                    Sequence(
                        Ref.keyword("NOT", optional=True),
                        Ref("LikeGrammar"),
                    ),
                    Ref("Expression_A_Grammar"),
                    Sequence(
                        Ref.keyword("ESCAPE"),
                        Ref("Tail_Recurse_Expression_A_Grammar"),
                        optional=True,
                    ),
                ),
                Sequence(
                    Ref("BinaryOperatorGrammar"),
                    Ref("Tail_Recurse_Expression_A_Grammar"),
                ),
                Ref("InOperatorGrammar"),
                Sequence(
                    "IS",
                    Ref.keyword("NOT", optional=True),
                    Ref("IsClauseGrammar"),
                ),
                Ref("IsNullGrammar"),
                Sequence(
                    Sequence(
                        Ref("InterpolateGrammar"),
                    ),
                    Ref("Expression_A_Grammar"),
                ),
                Ref("NotNullGrammar"),
                Ref("CollateGrammar"),
                Sequence(
                    Ref.keyword("NOT", optional=True),
                    "BETWEEN",
                    Ref("Expression_B_Grammar"),
                    "AND",
                    Ref("Tail_Recurse_Expression_A_Grammar"),
                ),
            )
        ),
    ),
    ComparisonOperatorGrammar=OneOf(
        Ref("EqualsSegment"),
        Ref("NullEqualsSegment"),
        Ref("GreaterThanSegment"),
        Ref("LessThanSegment"),
        Ref("GreaterThanOrEqualToSegment"),
        Ref("LessThanOrEqualToSegment"),
        Ref("NotEqualToSegment"),
        Ref("LikeOperatorSegment"),
        Ref("IsDistinctFromGrammar"),
    ),
    JoinTypeKeywordsGrammar=OneOf(
        "ANTI",
        "SEMIALL",
        "SEMI",
        Sequence("NULLAWARE", "ANTI"),
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
            "NATURAL",
            OneOf(
                "INNER",
                Sequence(OneOf("RIGHT", "LEFT", "FULL"), "OUTER"),
            ),
        ),
    ),
    ArithmeticBinaryOperatorGrammar=OneOf(
        Ref("PlusSegment"),
        Ref("MinusSegment"),
        Ref("DivideSegment"),
        Ref("IntegerDivideSegment"),
        Ref("MultiplySegment"),
        Ref("ModuloSegment"),
        Ref("BitwiseAndSegment"),
        Ref("BitwiseOrSegment"),
        Ref("BitwiseXorSegment"),
        Ref("BitwiseLShiftSegment"),
        Ref("BitwiseRShiftSegment"),
    ),
    # Vertica supports the non-standard ISNULL and NONNULL comparison operators. See
    # https://docs.vertica.com/latest/en/sql-reference/language-elements/operators/null-operators/
    IsNullGrammar=Ref.keyword("ISNULL"),
    NotNullGrammar=Ref.keyword("NOTNULL"),
)


class ShorthandCastSegment(ansi.ShorthandCastSegment):
    """A casting operation using '::' or '::!'."""

    match_grammar: Matchable = Sequence(
        OneOf(
            Ref("Expression_D_Grammar"),
            Ref("CaseExpressionSegment"),
        ),
        AnyNumberOf(
            Sequence(
                OneOf(Ref("CastOperatorSegment"), Ref("NullCastOperatorSegment")),
                Ref("DatatypeSegment"),
                Ref("TimeZoneGrammar", optional=True),
                allow_gaps=True,
            ),
            min_times=1,
        ),
    )


class StatementSegment(ansi.StatementSegment):
    """A generic segment, to any of its child subsegments."""

    match_grammar = ansi.StatementSegment.match_grammar.copy(
        insert=[
            Ref("CreateExternalTableSegment"),
            Ref("CreateTableLikeStatementSegment"),
            Ref("CreateTableAsStatementSegment"),
            Ref("CreateProjectionStatementSegment"),
            Ref("AlterDefaultPrivilegesGrantSegment"),
            Ref("DropProjectionStatementSegment"),
            Ref("AlterViewStatementSegment"),
            Ref("SetStatementSegment"),
            Ref("CommentOnStatementSegment"),
            Ref("TransactionalStatements"),
            Ref("AlterSessionStatements"),
            Ref("CopyStatementSegment"),
            Ref("AlterSchemaStatementSegment"),
        ],
    )


class ArrayTypeSegment(ansi.ArrayTypeSegment):
    """Prefix for array literals specifying the type."""

    type = "array_type"
    match_grammar = Ref.keyword("ARRAY")


class LimitClauseSegment(ansi.LimitClauseSegment):
    """A vertica `LIMIT` clause.

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
        ),
    )


class LikeOptionSegment(BaseSegment):
    """Like Option Segment.

    As specified in
    https://docs.vertica.com/latest/en/admin/working-with-native-tables/creating-table-from-other-tables/replicating-table/
    """

    type = "like_option_segment"

    match_grammar = Sequence(
        OneOf(
            Sequence(OneOf("INCLUDING", "EXCLUDING"), "PROJECTIONS"),
            Ref("SchemaPrivilegesSegment"),
        ),
    )


class DiskQuotaSegment(BaseSegment):
    """Disk Quota Segment.

    https://docs.vertica.com/latest/en/admin/working-with-native-tables/disk-quotas/
    Available from Vertica 12.x
    """

    type = "disk_quota_segment"

    match_grammar = Sequence("DISK_QUOTA", Ref("QuotedLiteralSegment"))


class KsafeSegment(BaseSegment):
    """Ksafe Segment.

    https://docs.vertica.com/latest/en/sql-reference/statements/create-statements/create-table/
    https://docs.vertica.com/latest/en/architecture/enterprise-concepts/k-safety-an-enterprise-db/
    """

    type = "ksafe_segment"

    match_grammar = Sequence(
        "KSAFE",
        Ref("NumericLiteralSegment", optional=True),
    )


class SchemaPrivilegesSegment(BaseSegment):
    """Schema Privileges Segment.

    https://docs.vertica.com/latest/en/sql-reference/statements/create-statements/create-table/
    """

    type = "schema_privileges_segment"
    match_grammar: Matchable = Sequence(
        # MATERIALIZE available only in ALTER TABLE statement,
        # but we keep it here to not duplicate the code
        OneOf("INCLUDE", "EXCLUDE", "MATERIALIZE"),
        Ref.keyword("SCHEMA", optional=True),
        "PRIVILEGES",
    )


class SegmentedByClauseSegment(BaseSegment):
    """A `SEGMENTED BY` or `UNSEGMENTED` clause.

    As specified in
    https://docs.vertica.com/latest/en/sql-reference/statements/
    create-statements/create-projection/hash-segmentation-clause/
    Vertica allows different expressions in segmented by clause,
    but using hash function is recommended one
    As specified in
    https://docs.vertica.com/latest/en/sql-reference/statements/
    create-statements/create-projection/unsegmented-clause/
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
                        Ref("ExpressionSegment"),
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
        Ref.keyword("REORGANIZE", optional=True),
    )


class CreateTableStatementSegment(ansi.CreateTableStatementSegment):
    """A `CREATE TABLE` statement.

    https://docs.vertica.com/latest/en/sql-reference/statements/create-statements/create-table/
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
                            Sequence(
                                "ACCESSRANK", Ref("IntegerSegment"), optional=True
                            ),
                        ),
                    ),
                    Ref("TableConstraintSegment"),
                ),
            ),
        ),
        AnySetOf(
            Ref("OrderByClauseSegment"),
            Ref("SegmentedByClauseSegment"),
            Ref("KsafeSegment"),
            Ref("SchemaPrivilegesSegment"),
            Ref("DiskQuotaSegment"),
            Ref("PartitionByClauseSegment"),
        ),
        AnySetOf(
            # these options are available only for temp table, so it's kind of a hack
            Sequence("ON", "COMMIT", OneOf("DELETE", "PRESERVE"), "ROWS"),
            Sequence("NO", "PROJECTION"),
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
        AnySetOf(
            # these options are available only for temp table, so it's kind of a hack
            Sequence("ON", "COMMIT", OneOf("DELETE", "PRESERVE"), "ROWS"),
            Sequence("NO", "PROJECTION"),
        ),
        AnyNumberOf(
            Bracketed(
                Delimited(
                    Sequence(
                        Ref("ColumnReferenceSegment"),
                        Ref("ColumnEncodingSegment", optional=True),
                        Sequence("ACCESSRANK", Ref("IntegerSegment"), optional=True),
                        # TODO: need to add GROUPED clause
                        # https://docs.vertica.com/latest/en/sql-reference/statements/
                        # create-statements/create-projection/grouped-clause/
                    ),
                ),
                optional=True,
            ),
            Ref("SchemaPrivilegesSegment", optional=True),
        ),
        "AS",
        # TODO: need to add LABEL clause
        # https://docs.vertica.com/latest/en/admin/
        # working-with-native-tables/creating-table-from-other-tables/creating-table-from-query/
        Sequence(
            "AT",
            OneOf("LATEST", Ref("NumericLiteralSegment"), Ref("DatetimeUnitSegment")),
            optional=True,
        ),
        Ref(
            "SelectableGrammar",
            terminators=[Ref("SegmentedByClauseSegment"), Ref("OrderByClauseSegment")],
        ),
        Ref("OrderByClauseSegment", optional=True),
        Ref("SegmentedByClauseSegment", optional=True),
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


class CopyOptionsForColumnsSegment(BaseSegment):
    """A vertica options for columns in COPY.

    https://docs.vertica.com/latest/en/sql-reference/statements/copy/
    """

    type = "copy_options_for_columns"

    match_grammar = Sequence(
        AnySetOf(
            Sequence(
                "DELIMITER", Sequence("AS", optional=True), Ref("QuotedLiteralSegment")
            ),
            Sequence(
                "ENCLOSED", Sequence("BY", optional=True), Ref("QuotedLiteralSegment")
            ),
            "ENFORCELENGTH",
            OneOf(
                Sequence(
                    "ESCAPE", Sequence("AS", optional=True), Ref("QuotedLiteralSegment")
                ),
                Sequence("NO", "ESCAPE"),
            ),
            Sequence("FILLER", Ref("DatatypeSegment")),
            Sequence("FORMAT", Ref("QuotedLiteralSegment")),
            Sequence(
                "NULL", Sequence("AS", optional=True), Ref("QuotedLiteralSegment")
            ),
            Sequence("TRIM", Ref("QuotedLiteralSegment")),
        ),
    )


class CopyColumnOptionsSegment(BaseSegment):
    """A vertica column description in COPY.

    https://docs.vertica.com/latest/en/sql-reference/statements/copy/
    """

    type = "copy_column_options"

    match_grammar = Sequence(
        Ref("ColumnReferenceSegment"),
        Ref("CopyOptionsForColumnsSegment", optional=True),
    )


class CopyOptionsSegment(BaseSegment):
    """A vertica options for COPY.

    https://docs.vertica.com/latest/en/sql-reference/statements/copy/
    """

    type = "copy_options"

    match_grammar = Sequence(
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
            Ref("CopyOptionsForColumnsSegment", optional=True),
        ),
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
                            Sequence(
                                "ACCESSRANK", Ref("IntegerSegment"), optional=True
                            ),
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
            optional=True,
        ),
        "FROM",
        Ref("QuotedLiteralSegment"),
        OneOf("NATIVE", Sequence("NATIVE", "VARCHAR"), "ORC", "PARQUET", optional=True),
        Ref("CopyOptionsSegment", optional=True),
    )


class GroupByClauseSegment(BaseSegment):
    """A `GROUP BY` clause like in `SELECT`."""

    type = "groupby_clause"

    match_grammar: Matchable = Sequence(
        "GROUP",
        "BY",
        Indent,
        Sequence(
            Delimited(
                OneOf(
                    Ref("ColumnReferenceSegment"),
                    # Can `GROUP BY 1`
                    Ref("NumericLiteralSegment"),
                    # Can `GROUP BY coalesce(col, 1)`
                    Ref("ExpressionSegment"),
                ),
                terminators=[Ref("GroupByClauseTerminatorGrammar")],
            ),
        ),
        Dedent,
    )


class CreateProjectionStatementSegment(BaseSegment):
    """A `CREATE PROJECTION` statement.

    As specified in
    https://docs.vertica.com/latest/en/sql-reference/statements/
    create-statements/create-projection/standard-projection/
    """

    type = "create_projection_statement"

    match_grammar = Sequence(
        "CREATE",
        "PROJECTION",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        Bracketed(
            Delimited(
                Sequence(
                    Ref("ColumnReferenceSegment"),
                    Ref("ColumnEncodingSegment", optional=True),
                    Sequence("ACCESSRANK", Ref("IntegerSegment"), optional=True),
                    # TODO: need to add GROUPED clause
                    # https://docs.vertica.com/latest/en/sql-reference/statements/
                    # create-statements/create-projection/grouped-clause/
                ),
            ),
            optional=True,
        ),
        "AS",
        Ref(
            "SelectableGrammar",
            terminators=[
                Ref("SegmentedByClauseSegment"),
                Ref("OrderByClauseSegment"),
                Ref("LimitClauseSegment"),
                Ref("GroupByClauseSegment"),
                "ON",
            ],
        ),
        OneOf(
            # TODO: add udtf projection type
            AnyNumberOf(
                Ref("OrderByClauseSegment"),
                Ref("SegmentedByClauseSegment"),
                Sequence(
                    "ON",
                    "PARTITION",
                    "RANGE",
                    "BETWEEN",
                    Ref("QuotedLiteralSegment"),
                    "AND",
                    Ref("QuotedLiteralSegment"),
                ),
            ),
            Ref("GroupByClauseSegment"),
            Ref("LimitClauseSegment"),
        ),
        Ref("KsafeSegment", optional=True),
    )


class AlterTableStatementSegment(ansi.AlterTableStatementSegment):
    """An `ALTER TABLE` statement.

    https://docs.vertica.com/latest/en/sql-reference/statements/alter-statements/alter-table/
    """

    match_grammar = Sequence(
        "ALTER",
        "TABLE",
        Delimited(Ref("TableReferenceSegment")),
        OneOf(
            Sequence(
                Delimited(Ref("AlterTableActionSegment")),
            ),
            Sequence(
                "ADD",
                Ref.keyword("COLUMN"),
                Ref("IfNotExistsGrammar", optional=True),
                Ref("ColumnReferenceSegment"),
                Ref("DatatypeSegment"),
                AnyNumberOf(Ref("ColumnConstraintSegment")),
                Ref("ColumnEncodingSegment", optional=True),
                OneOf(
                    Sequence(
                        "PROJECTIONS",
                        Bracketed(Delimited(Ref("TableReferenceSegment"))),
                    ),
                    Sequence("ALL", "PROJECTIONS"),
                    optional=True,
                ),
                Ref("ColumnConstraintSegment", optional=True),
            ),
            Sequence(
                "ALTER",
                Ref.keyword("COLUMN"),
                Ref("ColumnReferenceSegment"),
                OneOf(
                    Sequence(
                        Ref("ColumnEncodingSegment"),
                        "PROJECTIONS",
                        Bracketed(Delimited(Ref("TableReferenceSegment"))),
                    ),
                    Sequence("SET", Ref("ColumnSetSegment")),
                    Sequence("SET", "NOT", "NULL"),
                    Sequence("SET", "DATA", "TYPE", Ref("DatatypeSegment")),
                    Sequence(
                        "DROP",
                        OneOf(
                            "DEFAULT",
                            Sequence("SET", "USING"),
                            Sequence("DEFAULT", "USING"),
                            Sequence("NOT", "NULL"),
                        ),
                    ),
                ),
            ),
            Sequence(
                "DROP",
                "CONSTRAINT",
                Ref("ParameterNameSegment"),
                OneOf("CASCADE", "RESTRICT", optional=True),
            ),
            Sequence(
                "DROP",
                Ref.keyword("COLUMN", optional=True),
                Ref("IfExistsGrammar", optional=True),
                Ref("ColumnReferenceSegment"),
                Ref("DropBehaviorGrammar", optional=True),
            ),
            Ref("PartitionByClauseSegment"),
            Sequence("REMOVE", "PARTITIONING"),
            Sequence(
                "RENAME",
                Ref.keyword("COLUMN", optional=True),
                Ref("ColumnReferenceSegment"),
                "TO",
                Ref("ColumnReferenceSegment"),
            ),
            Sequence(
                "RENAME",
                "TO",
                Delimited(Ref("TableReferenceSegment")),
            ),
            "REORGANIZE",
            Sequence("SET", "SCHEMA", Ref("SchemaReferenceSegment")),
        ),
    )


class AlterTableActionSegment(BaseSegment):
    """Alter Table Action Segment.

    https://docs.vertica.com/latest/en/sql-reference/statements/alter-statements/alter-table/
    """

    type = "alter_table_action_segment"

    match_grammar = OneOf(
        Sequence("ADD", Ref("TableConstraintSegment")),
        Sequence(
            "ALTER",
            "CONSTRAINT",
            Ref("ParameterNameSegment"),
            OneOf("ENABLED", "DISABLED"),
        ),
        Ref("DiskQuotaSegment"),
        Sequence("FORCE", "OUTER", Ref("IntegerSegment")),
        Ref("SchemaPrivilegesSegment"),
        Sequence(
            "OWNER",
            "TO",
            Ref("ParameterNameSegment"),
        ),
        Sequence(
            "SET",
            OneOf(
                Sequence(
                    "ActivePartitionCount", OneOf(Ref("IntegerSegment"), "DEFAULT")
                ),
                Sequence("IMMUTABLE", "ROWS"),
                Sequence("MERGEOUT", OneOf("1", "2")),
            ),
        ),
    )


class AlterDefaultPrivilegesObjectPrivilegesSegment(BaseSegment):
    """`ALTER DEFAULT PRIVILEGES` object privileges.

    https://docs.vertica.com/latest/en/sql-reference/statements/grant-statements/grant-table/
    """

    type = "alter_default_privileges_object_privilege"
    match_grammar = OneOf(
        Sequence(
            "ALL",
            Ref.keyword("PRIVILEGES", optional=True),
            Ref.keyword("EXTEND", optional=True),
        ),
        Delimited(
            "SELECT",
            "INSERT",
            "UPDATE",
            "DELETE",
            "REFERENCES",
            "TRUNCATE",
            "ALTER",
            "DROP",
            terminators=["ON"],
        ),
    )


class AlterDefaultPrivilegesGrantSegment(BaseSegment):
    """`GRANT` for `ALTER DEFAULT PRIVILEGES`.

    https://docs.vertica.com/latest/en/sql-reference/statements/grant-statements/grant-table/
    """

    type = "alter_default_privileges_grant"
    match_grammar = Sequence(
        "GRANT",
        Ref("AlterDefaultPrivilegesObjectPrivilegesSegment"),
        "ON",
        OneOf(
            Delimited(
                Sequence(
                    Ref.keyword("TABLE", optional=True), Ref("TableReferenceSegment")
                )
            ),
            Delimited(
                Sequence(
                    "ALL", "TABLES", "IN", "SCHEMA", Ref("SchemaReferenceSegment")
                ),
            ),
            terminators=["WITH"],
        ),
        "TO",
        Delimited(
            Ref("RoleReferenceSegment"),
            terminators=["WITH"],
        ),
        Sequence("WITH", "GRANT", "OPTION", optional=True),
    )


class ColumnConstraintSegment(ansi.ColumnConstraintSegment):
    """A column option; each CREATE TABLE column can have 0 or more.

    https://docs.vertica.com/latest/en/sql-reference/statements/create-statements/create-table/column-constraint/
    """

    match_grammar = Sequence(
        # TODO: add auto increment
        OneOf(
            Sequence(
                Sequence(
                    "CONSTRAINT",
                    Ref("ObjectReferenceSegment"),  # Constraint name
                    optional=True,
                ),
                OneOf(
                    Sequence(
                        Ref.keyword("NOT", optional=True), "NULL"
                    ),  # NOT NULL or NULL
                    Sequence(
                        "CHECK",
                        Bracketed(Ref("ExpressionSegment")),
                        OneOf("ENABLED", "DISABLED", optional=True),
                    ),
                    Sequence(
                        "UNIQUE",
                        OneOf("ENABLED", "DISABLED", optional=True),
                    ),
                    Sequence(
                        "PRIMARY",
                        "KEY",
                        OneOf("ENABLED", "DISABLED", optional=True),
                    ),
                    # REFERENCES reftable [ ( refcolumn) ]
                    Ref("ReferenceDefinitionGrammar"),
                ),
            ),
            Ref("ColumnSetSegment"),
        ),
    )


class ColumnSetSegment(BaseSegment):
    """A SET DEFAULT | USING | DEFAULT USING.

    https://docs.vertica.com/latest/en/sql-reference/statements/alter-statements/alter-table/
    """

    type = "column_set_segment"

    match_grammar = Sequence(  # DEFAULT <value>
        OneOf(
            "DEFAULT",
            # Depends on the place where we use it (in alter table or create table)
            # we need or don't need set keyword
            Sequence(Ref.keyword("SET", optional=True), "USING"),
            Sequence("DEFAULT", "USING"),
        ),
        OneOf(
            Ref("ShorthandCastSegment"),
            Ref("LiteralGrammar"),
            Ref("FunctionSegment"),
            Ref("BareFunctionSegment"),
            Ref("ExpressionSegment"),
            Bracketed(Ref("SelectableGrammar")),
        ),
    )


class DropProjectionStatementSegment(BaseSegment):
    """A `DROP PROJECTION` statement.

    https://docs.vertica.com/latest/en/sql-reference/statements/drop-statements/drop-projection/
    """

    type = "drop_projection_statement"

    match_grammar: Matchable = Sequence(
        "DROP",
        "PROJECTION",
        Ref("IfExistsGrammar", optional=True),
        Delimited(Ref("TableReferenceSegment")),
        Ref("DropBehaviorGrammar", optional=True),
    )


class AlterViewStatementSegment(BaseSegment):
    """A `ALTER VIEW` statement.

    https://docs.vertica.com/latest/en/sql-reference/statements/alter-statements/alter-view/
    """

    type = "alter_view_statement"

    match_grammar: Matchable = Sequence(
        "ALTER",
        "VIEW",
        Delimited(Ref("TableReferenceSegment")),
        AnyNumberOf(
            Sequence("OWNER", "TO", Ref("ParameterNameSegment")),
            Sequence("SET", "SCHEMA", Ref("SchemaReferenceSegment")),
            Ref("SchemaPrivilegesSegment"),
            Sequence("RENAME", "TO", Delimited(Ref("ParameterNameSegment"))),
        ),
    )


class SetStatementSegment(BaseSegment):
    """Set Statement.

    https://docs.vertica.com/latest/en/sql-reference/statements/set-statements/
    """

    type = "set_statement"

    match_grammar = Sequence(
        "SET",
        OneOf(
            Sequence(
                OneOf(
                    "DATESTYLE",
                    "ESCAPE_STRING_WARNING",
                    "INTERVALSTYLE",
                    "LOCALE",
                    "STANDARD_CONFORMING_STRINGS",
                ),
                "TO",
                Ref("ParameterNameSegment"),
            ),
            Sequence(
                "SEARCH_PATH",
                OneOf("TO", Ref("EqualsSegment")),
                OneOf(Delimited(Ref("ParameterNameSegment")), "DEFAULT"),
            ),
            Sequence(
                "ROLE",
                OneOf(
                    "NONE",
                    "DEFAULT",
                    Sequence(
                        "ALL",
                        Sequence(
                            "EXCEPT",
                            Delimited(Ref("ParameterNameSegment")),
                            optional=True,
                        ),
                    ),
                    Delimited(Ref("ParameterNameSegment")),
                ),
            ),
            Sequence(
                "TIME",
                "ZONE",
                Ref.keyword("TO", optional=True),
                OneOf(Ref("ParameterNameSegment"), Ref("QuotedLiteralSegment")),
            ),
            Sequence(
                Ref.keyword("SESSION", optional=True),
                "RESOURCE_POOL",
                Ref("EqualsSegment"),
                OneOf(
                    Ref("QuotedLiteralSegment"), Ref("ParameterNameSegment"), "DEFAULT"
                ),
            ),
            Sequence(
                "SESSION",
                OneOf(
                    Sequence(
                        "AUTHORIZATION", OneOf(Ref("ParameterNameSegment"), "DEFAULT")
                    ),
                    Sequence("AUTOCOMMIT", "TO", OneOf("ON", "OFF")),
                    Sequence(
                        "CHARACTERISTICS",
                        "AS",
                        "TRANSACTION",
                        Ref("ParameterNameSegment"),
                    ),
                    Sequence(
                        OneOf("GRACEPERIOD", "IDLESESSIONTIMEOUT", "RUNTIMECAP"),
                        OneOf(
                            "NONE",
                            Sequence(Ref("EqualsSegment"), "DEFAULT"),
                            Ref("QuotedLiteralSegment"),
                        ),
                    ),
                    Sequence(
                        OneOf("MEMORYCAP", "TEMPSPACECAP"),
                        OneOf(
                            "NONE",
                            Sequence(Ref("EqualsSegment"), "DEFAULT"),
                            Ref("QuotedLiteralSegment"),
                        ),
                    ),
                    Sequence("MULTIPLEACTIVERESULTSETS", "TO", OneOf("ON", "OFF")),
                    Sequence(
                        "WORKLOAD",
                        Ref.keyword("TO", optional=True),
                        OneOf(Ref("ParameterNameSegment"), "DEFAULT", "NONE"),
                    ),
                ),
            ),
        ),
    )


class CommentOnStatementSegment(BaseSegment):
    """`COMMENT ON` statement.

    https://www.postgresql.org/docs/13/sql-comment.html
    """

    type = "comment_clause"

    match_grammar = Sequence(
        "COMMENT",
        "ON",
        Sequence(
            OneOf(
                Sequence(
                    OneOf(
                        "TABLE",
                        "VIEW",
                        "PROJECTION",
                    ),
                    Ref("TableReferenceSegment"),
                ),
                Sequence(
                    "COLUMN",
                    Ref("ColumnReferenceSegment"),
                ),
                Sequence(
                    "CONSTRAINT",
                    Ref("ObjectReferenceSegment"),
                    Sequence(
                        "ON",
                        Ref("ObjectReferenceSegment"),
                    ),
                ),
                Sequence(
                    OneOf("AGGREGATE", "ANALYTIC", "TRANSFORM", optional=True),
                    "FUNCTION",
                    Ref("FunctionNameSegment"),
                    Sequence(Ref("FunctionParameterListGrammar"), optional=True),
                ),
                Sequence(
                    "SCHEMA",
                    Ref("SchemaReferenceSegment"),
                ),
                Sequence(
                    "NODE",
                    Ref("ParameterNameSegment"),
                ),
                Sequence(
                    OneOf("SEQUENCE", "LIBRARY"),
                    Ref("ObjectReferenceSegment"),
                ),
            ),
            Sequence("IS", OneOf(Ref("QuotedLiteralSegment"), "NULL")),
        ),
    )


class TransactionalStatements(BaseSegment):
    """DML commands wrapped by BEGIN and END.

    As in https://docs.vertica.com/latest/en/sql-reference/statements/begin/
    https://docs.vertica.com/latest/en/sql-reference/statements/end/
    """

    type = "transactional_statement"
    match_grammar: Matchable = Sequence(
        # TODO add rollback, commit logic and optional keywords
        "BEGIN",
        AnyNumberOf(
            Sequence(
                Ref("InsertStatementSegment"),
                Ref("SemicolonSegment"),
            ),
            Sequence(
                Ref("UpdateStatementSegment"),
                Ref("SemicolonSegment"),
            ),
            Sequence(
                Ref("DeleteStatementSegment"),
                Ref("SemicolonSegment"),
            ),
            Sequence(
                Ref("SelectStatementSegment"),
                Ref("SemicolonSegment"),
            ),
        ),
        "END",
    )


class DatatypeSegment(ansi.DatatypeSegment):
    """A data type segment."""

    match_grammar: Matchable = Sequence(
        OneOf(
            # Date / Datetime
            Sequence(
                OneOf("TIME", "TIMESTAMP"),
                Bracketed(Ref("NumericLiteralSegment"), optional=True),
                Sequence(OneOf("WITH", "WITHOUT"), "TIME", "ZONE", optional=True),
            ),
            "DATE",
            "DATETIME",
            "SMALLDATETIME",
            Sequence("INTERVAL", Ref("IntervalLiteralGrammar", optional=True)),
            # Approximate Numeric
            Sequence(
                "DOUBLE",
                "PRECISION",
            ),
            Sequence("FLOAT", Bracketed(Ref("NumericLiteralSegment"), optional=True)),
            "FLOAT8",
            "REAL",
            # Exact Numeric
            "INTEGER",
            "INT",
            "BIGINT",
            "INT8",
            "SMALLINT",
            "TINYINT",
            Sequence(
                OneOf("DECIMAL", "NUMERIC", "NUMBER", "MONEY"),
                Bracketed(
                    Ref("IntegerSegment"),
                    Sequence(Ref("CommaSegment"), Ref("IntegerSegment"), optional=True),
                    optional=True,
                ),
            ),
            # Spatial
            Sequence(
                OneOf("GEOMETRY", "GEOGRAPHY"),
                Bracketed(Ref("NumericLiteralSegment"), optional=True),
            ),
            # UUID
            "UUID",
            # Text
            Sequence(
                Ref.keyword("LONG", optional=True),
                "VARCHAR",
                Ref("BracketedArguments", optional=True),
            ),
            Sequence("CHAR", Ref("BracketedArguments", optional=True)),
            # Binary types
            OneOf(
                "BINARY",
                Sequence(Ref.keyword("LONG", optional=True), "VARBINARY"),
                "BYTEA",
                "RAW",
            ),
            "BOOLEAN",
            # array types
            OneOf(
                # TODO: need to add an opportunity to specify size of array
                AnyNumberOf(
                    Bracketed(
                        Ref("ExpressionSegment", optional=True), bracket_type="square"
                    )
                ),
                Ref("ArrayTypeSegment"),
                Ref("SizedArrayTypeSegment"),
                optional=True,
            ),
            # TODO: add row data type support
            Sequence(
                OneOf(
                    Sequence(
                        OneOf("CHARACTER", "BINARY"),
                        OneOf("VARYING", Sequence("LARGE", "OBJECT")),
                    ),
                    Sequence(
                        # Some dialects allow optional qualification of data types with
                        # schemas
                        Sequence(
                            Ref("SingleIdentifierGrammar"),
                            Ref("DotSegment"),
                            allow_gaps=False,
                            optional=True,
                        ),
                        Ref("DatatypeIdentifierSegment"),
                        allow_gaps=False,
                    ),
                ),
                # There may be no brackets for some data types
                Ref("BracketedArguments", optional=True),
            ),
        ),
    )


class AlterSessionStatements(BaseSegment):
    """An ALTER SESSION statement.

    https://docs.vertica.com/latest/en/sql-reference/statements/alter-statements/alter-session/
    """

    type = "alter_session_statement"
    match_grammar: Matchable = Sequence(
        "ALTER",
        "SESSION",
        OneOf(
            Sequence(
                "SET",
                Ref.keyword("PARAMETER", optional=True),
                OptionallyBracketed(
                    Sequence(
                        Ref("ParameterNameSegment"),
                        Ref("EqualsSegment"),
                        Ref("QuotedLiteralSegment"),
                    ),
                ),
            ),
            Sequence(
                "CLEAR",
                Ref.keyword("PARAMETER", optional=True),
                OneOf(
                    Bracketed(
                        Sequence(
                            Ref("ParameterNameSegment"),
                            Ref("EqualsSegment"),
                            Ref("QuotedLiteralSegment"),
                        ),
                    ),
                    Sequence("PARAMETER", "ALL"),
                ),
            ),
            Sequence(
                "SET",
                "UDPARAMETER",
                Sequence("FOR", Ref("ParameterNameSegment"), optional=True),
                Bracketed(
                    Sequence(
                        Ref("ParameterNameSegment"),
                        Ref("EqualsSegment"),
                        Ref("QuotedLiteralSegment"),
                    ),
                ),
            ),
            Sequence(
                "CLEAR",
                "UDPARAMETER",
                Sequence("FOR", Ref("ParameterNameSegment"), optional=True),
                OneOf(
                    "ALL",
                    Bracketed(Ref("ParameterNameSegment")),
                ),
            ),
        ),
    )


class CopyStatementSegment(BaseSegment):
    """A `COPY` statement.

    As Specified in https://docs.vertica.com/latest/en/sql-reference/statements/copy/
    """

    # TODO: it's not full and requires additional improvements

    type = "copy_statement"

    match_grammar = Sequence(
        "COPY",
        Ref("TableReferenceSegment"),
        OneOf(
            Bracketed(
                Delimited(Ref("CopyColumnOptionsSegment")),
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
            optional=True,
        ),
        "FROM",
        OneOf(
            Sequence(
                Ref.keyword("LOCAL", optional=True),
                "STDIN",
                Ref("CompressionType", optional=True),
                Ref("QuotedLiteralSegment", optional=True),
            ),
            Sequence(
                "LOCAL",
                Ref("QuotedLiteralSegment"),
                Ref("CompressionType", optional=True),
            ),
            Sequence(
                "VERTICA",
                Ref("TableReferenceSegment"),
                Bracketed(Delimited(Ref("ColumnReferenceSegment")), optional=True),
            ),
            Sequence(Delimited(Ref("QuotedLiteralSegment"))),
        ),
        OneOf("NATIVE", Sequence("NATIVE", "VARCHAR"), "ORC", "PARQUET", optional=True),
        Ref("CopyOptionsSegment", optional=True),
    )


class FunctionSegment(ansi.FunctionSegment):
    """A scalar or aggregate function.

    https://docs.vertica.com/latest/en/sql-reference/functions/aggregate-functions/
    """

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
        Ref("ColumnsExpressionGrammar"),
        Sequence(
            Sequence(
                Ref(
                    "FunctionNameSegment",
                    exclude=OneOf(
                        Ref("DatePartFunctionNameSegment"),
                        Ref("ColumnsExpressionFunctionNameSegment"),
                        Ref("ValuesClauseSegment"),
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
            AnyNumberOf(Ref("PostFunctionGrammar")),
            # Allow AS clause for some functions at the end
            Sequence(
                "AS", Bracketed(Delimited(Ref("ColumnReferenceSegment"))), optional=True
            ),
        ),
    )


class WithinGroupClauseSegment(BaseSegment):
    """A `WITHIN GROUP` clause for some analytic functions.

    https://docs.vertica.com/latest/en/sql-reference/functions/analytic-functions/percentile-cont-analytic/
    """

    type = "within_group_clause_statement"

    match_grammar = Sequence("WITHIN", "GROUP", Bracketed(Ref("OrderByClauseSegment")))


class TimeseriesClauseSegment(BaseSegment):
    """A vertica `TIMESERIES` clause.

    https://docs.vertica.com/latest/en/sql-reference/statements/select/timeseries-clause/
    """

    type = "timeseries_clause_statement"

    match_grammar: Matchable = Sequence(
        "TIMESERIES",
        Ref("AliasExpressionSegment"),
        Ref.keyword("AS"),
        Ref("QuotedLiteralSegment"),
        Indent,
        Ref("OverClauseSegment"),
        # TODO: add optional ORDER BY
        Dedent,
    )


class UnorderedSelectStatementSegment(ansi.UnorderedSelectStatementSegment):
    """A `SELECT` statement without any ORDER clauses or later.

    Copy of ansi class except additional terminator TimeseriesClauseSegment
    """

    match_grammar: Matchable = Sequence(
        Ref("SelectClauseSegment"),
        Ref("FromClauseSegment", optional=True),
        Ref("WhereClauseSegment", optional=True),
        Ref("GroupByClauseSegment", optional=True),
        Ref("HavingClauseSegment", optional=True),
        Ref("OverlapsClauseSegment", optional=True),
        Ref("NamedWindowSegment", optional=True),
        terminators=[
            Ref("SetOperatorSegment"),
            Ref("WithNoSchemaBindingClauseSegment"),
            Ref("WithDataClauseSegment"),
            Ref("OrderByClauseSegment"),
            Ref("LimitClauseSegment"),
            Ref("TimeseriesClauseSegment"),
        ],
        parse_mode=ParseMode.GREEDY_ONCE_STARTED,
    )


class SelectStatementSegment(ansi.SelectStatementSegment):
    """A `SELECT` statement.

    Copy of ansi class except additional TimeseriesClauseSegment grammar
    """

    match_grammar = UnorderedSelectStatementSegment.match_grammar.copy(
        insert=[
            Ref("OrderByClauseSegment", optional=True),
            Ref("FetchClauseSegment", optional=True),
            Ref("LimitClauseSegment", optional=True),
            Ref("TimeseriesClauseSegment", optional=True),
            Ref("NamedWindowSegment", optional=True),
        ],
        # Overwrite the terminators, because we want to remove some.
        replace_terminators=True,
        terminators=[
            Ref("SetOperatorSegment"),
            Ref("WithNoSchemaBindingClauseSegment"),
            Ref("WithDataClauseSegment"),
        ],
    )


class NullEqualsSegment(CompositeComparisonOperatorSegment):
    """Null Equals operator."""

    match_grammar: Matchable = Ref("NullEqualsOperatorSegment")


class PartitionClauseSegment(ansi.PartitionClauseSegment):
    """A `PARTITION BY` for window functions.

    https://docs.vertica.com/latest/en/sql-reference/language-elements/window-clauses/window-partition-clause/
    """

    match_grammar: Matchable = Sequence(
        "PARTITION",
        OneOf(
            Sequence(
                "BY",
                Indent,
                # Brackets are optional in a partition by statement
                OptionallyBracketed(Delimited(Ref("ExpressionSegment"))),
                Dedent,
            ),
            "BEST",
            "NODES",
            "ROW",
            Sequence("LEFT", "JOIN"),
        ),
    )


class FrameClauseSegment(ansi.FrameClauseSegment):
    """A frame clause for window functions.

    https://docs.vertica.com/latest/en/sql-reference/language-elements/window-clauses/window-partition-clause/
    """

    type = "frame_clause"

    _frame_extent = OneOf(
        Sequence("CURRENT", "ROW"),
        Sequence(
            OneOf(
                Ref("NumericLiteralSegment"),
                OneOf(
                    Sequence(
                        Ref("QuotedLiteralSegment"),
                        Ref("CastOperatorSegment"),
                        "INTERVAL",
                    ),
                    Sequence(
                        # TODO maybe this logic should be in an additional segment?
                        # because there are so many options
                        # for the interval representation.
                        Ref.keyword("INTERVAL", optional=True),
                        OneOf(
                            Ref("IntervalLiteralGrammar"), Ref("QuotedLiteralSegment")
                        ),
                        Ref("DatetimeUnitSegment", optional=True),
                    ),
                ),
                "UNBOUNDED",
            ),
            OneOf("PRECEDING", "FOLLOWING"),
        ),
    )

    match_grammar: Matchable = Sequence(
        Ref("FrameClauseUnitGrammar"),
        OneOf(_frame_extent, Sequence("BETWEEN", _frame_extent, "AND", _frame_extent)),
    )


class AlterSchemaStatementSegment(BaseSegment):
    """An `ALTER SCHEMA` statement.

    https://docs.vertica.com/latest/en/sql-reference/statements/alter-statements/alter-schema/
    """

    type = "alter_schema_statement"
    match_grammar = Sequence(
        "ALTER",
        "SCHEMA",
        Delimited(Ref("SchemaReferenceSegment")),
        OneOf(
            Sequence("DEFAULT", Ref("SchemaPrivilegesSegment")),
            Sequence(
                "RENAME",
                "TO",
                Delimited(Ref("SchemaReferenceSegment")),
            ),
            Sequence(
                "OWNER",
                "TO",
                Ref("RoleReferenceSegment"),
                Ref.keyword("CASCADE", optional=True),
            ),
            Ref("DiskQuotaSegment"),
        ),
    )


class CreateSchemaStatementSegment(ansi.CreateSchemaStatementSegment):
    """A `CREATE SCHEMA` statement.

    https://docs.vertica.com/latest/en/sql-reference/statements/create-statements/create-schema/
    """

    match_grammar: Matchable = Sequence(
        "CREATE",
        "SCHEMA",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("SchemaReferenceSegment"),
        AnySetOf(
            Sequence("AUTHORIZATION", Ref("RoleReferenceSegment")),
            Sequence("DEFAULT", Ref("SchemaPrivilegesSegment")),
            Ref("DiskQuotaSegment"),
        ),
    )
