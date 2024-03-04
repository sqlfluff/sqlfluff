"""The MSSQL T-SQL dialect.

https://docs.microsoft.com/en-us/sql/t-sql/language-elements/language-elements-transact-sql
"""

from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.core.parser import (
    AnyNumberOf,
    AnySetOf,
    BaseFileSegment,
    BaseSegment,
    Bracketed,
    CodeSegment,
    CommentSegment,
    CompositeBinaryOperatorSegment,
    CompositeComparisonOperatorSegment,
    Conditional,
    Dedent,
    Delimited,
    IdentifierSegment,
    ImplicitIndent,
    Indent,
    LiteralSegment,
    Matchable,
    MultiStringParser,
    NewlineSegment,
    Nothing,
    OneOf,
    OptionallyBracketed,
    ParseMode,
    Ref,
    RegexLexer,
    RegexParser,
    SegmentGenerator,
    Sequence,
    TypedParser,
    WhitespaceSegment,
    WordSegment,
)
from sqlfluff.dialects import dialect_ansi as ansi
from sqlfluff.dialects.dialect_tsql_keywords import (
    FUTURE_RESERVED_KEYWORDS,
    RESERVED_KEYWORDS,
    UNRESERVED_KEYWORDS,
)

ansi_dialect = load_raw_dialect("ansi")
tsql_dialect = ansi_dialect.copy_as("tsql")

tsql_dialect.sets("reserved_keywords").clear()
tsql_dialect.sets("unreserved_keywords").clear()
tsql_dialect.sets("future_reserved_keywords").clear()
tsql_dialect.sets("reserved_keywords").update(RESERVED_KEYWORDS)
tsql_dialect.sets("unreserved_keywords").update(UNRESERVED_KEYWORDS)
tsql_dialect.sets("future_reserved_keywords").update(FUTURE_RESERVED_KEYWORDS)

# Set the datetime units
tsql_dialect.sets("datetime_units").clear()
tsql_dialect.sets("datetime_units").update(
    [
        "D",
        "DAY",
        "DAYS",
        "DAYOFYEAR",
        "DD",
        "DW",
        "DY",
        "HH",
        "HOUR",
        "INFINITE",
        "M",
        "MCS",
        "MI",
        "MICROSECOND",
        "MILLISECOND",
        "MINUTE",
        "MM",
        "MONTH",
        "MONTHS",
        "MS",
        "N",
        "NANOSECOND",
        "NS",
        "Q",
        "QQ",
        "QUARTER",
        "S",
        "SECOND",
        "SS",
        "W",
        "WEEK",
        "WEEKS",
        "WEEKDAY",
        "WK",
        "WW",
        "YEAR",
        "YEARS",
        "Y",
        "YY",
        "YYYY",
    ]
)

tsql_dialect.sets("date_part_function_name").clear()
tsql_dialect.sets("date_part_function_name").update(
    ["DATEADD", "DATEDIFF", "DATEDIFF_BIG", "DATENAME", "DATEPART"]
)

tsql_dialect.sets("date_format").clear()
tsql_dialect.sets("date_format").update(
    [
        "mdy",
        "dmy",
        "ymd",
        "myd",
        "dym",
    ]
)

tsql_dialect.sets("bare_functions").update(
    ["system_user", "session_user", "current_user"]
)

tsql_dialect.sets("sqlcmd_operators").clear()
tsql_dialect.sets("sqlcmd_operators").update(["r", "setvar"])

tsql_dialect.sets("file_compression").clear()
tsql_dialect.sets("file_compression").update(
    [
        "'org.apache.hadoop.io.compress.GzipCodec'",
        "'org.apache.hadoop.io.compress.DefaultCodec'",
        "'org.apache.hadoop.io.compress.SnappyCodec'",
    ]
)

tsql_dialect.sets("file_encoding").clear()
tsql_dialect.sets("file_encoding").update(
    [
        "'UTF8'",
        "'UTF16'",
    ]
)

tsql_dialect.sets("serde_method").clear()
tsql_dialect.sets("serde_method").update(
    [
        "'org.apache.hadoop.hive.serde2.columnar.LazyBinaryColumnarSerDe'",
        "'org.apache.hadoop.hive.serde2.columnar.ColumnarSerDe'",
    ]
)

tsql_dialect.insert_lexer_matchers(
    [
        RegexLexer(
            "atsign",
            r"[@][a-zA-Z0-9_]+",
            CodeSegment,
        ),
        RegexLexer(
            "var_prefix",
            r"[$][a-zA-Z0-9_]+",
            CodeSegment,
        ),
        RegexLexer(
            "square_quote",
            r"\[([^\[\]]*)*\]",
            CodeSegment,
        ),
        # T-SQL unicode strings
        RegexLexer(
            "single_quote_with_n",
            r"N'([^']|'')*'",
            CodeSegment,
        ),
        RegexLexer(
            "hash_prefix",
            r"[#][#]?[a-zA-Z0-9_]+",
            CodeSegment,
        ),
        RegexLexer(
            "unquoted_relative_sql_file_path",
            # currently there is no way to pass `regex.IGNORECASE` flag to `RegexLexer`
            r"[.\w\\/#-]+\.[sS][qQ][lL]\b",
            CodeSegment,
        ),
    ],
    before="back_quote",
)

tsql_dialect.patch_lexer_matchers(
    [
        # Patching single_quote to allow for TSQL-style escaped quotes
        RegexLexer(
            "single_quote",
            r"'([^']|'')*'",
            CodeSegment,
        ),
        # Patching comments to remove hash comments
        RegexLexer(
            "inline_comment",
            r"(--)[^\n]*",
            CommentSegment,
            segment_kwargs={"trim_start": ("--")},
        ),
        # Patching block comments to account for nested blocks.
        # N.B. this syntax is only possible via the non-standard-library
        # (but still backwards compatible) `regex` package.
        # https://pypi.org/project/regex/
        # Pattern breakdown:
        # /\*                    Match opening slash.
        #   (?>                  Atomic grouping
        #                        (https://www.regular-expressions.info/atomic.html).
        #       [^*/]+           Non forward-slash or asterisk characters.
        #       |\*(?!\/)        Negative lookahead assertion to match
        #                        asterisks not followed by a forward-slash.
        #       |/[^*]           Match lone forward-slashes not followed by an asterisk.
        #   )*                   Match any number of the atomic group contents.
        #   (?>
        #       (?R)             Recursively match the block comment pattern
        #                        to match nested block comments.
        #       (?>
        #           [^*/]+
        #           |\*(?!\/)
        #           |/[^*]
        #       )*
        #   )*
        # \*/                    Match closing slash.
        RegexLexer(
            "block_comment",
            r"/\*(?>[^*/]+|\*(?!\/)|/[^*])*(?>(?R)(?>[^*/]+|\*(?!\/)|/[^*])*)*\*/",
            CommentSegment,
            subdivider=RegexLexer(
                "newline",
                r"\r\n|\n",
                NewlineSegment,
            ),
            trim_post_subdivide=RegexLexer(
                "whitespace",
                r"[^\S\r\n]+",
                WhitespaceSegment,
            ),
        ),
        RegexLexer(
            "word", r"[0-9a-zA-Z_#@]+", WordSegment
        ),  # overriding to allow hash mark and at-sign in code
    ]
)

tsql_dialect.add(
    BracketedIdentifierSegment=TypedParser(
        "square_quote", IdentifierSegment, type="quoted_identifier"
    ),
    HashIdentifierSegment=TypedParser(
        "hash_prefix", IdentifierSegment, type="hash_identifier"
    ),
    VariableIdentifierSegment=TypedParser(
        "var_prefix", IdentifierSegment, type="variable_identifier"
    ),
    BatchDelimiterGrammar=Ref("GoStatementSegment"),
    QuotedLiteralSegmentWithN=TypedParser(
        "single_quote_with_n", LiteralSegment, type="quoted_literal"
    ),
    QuotedLiteralSegmentOptWithN=OneOf(
        Ref("QuotedLiteralSegment"),
        Ref("QuotedLiteralSegmentWithN"),
    ),
    TransactionGrammar=OneOf(
        "TRANSACTION",
        "TRAN",
    ),
    SystemVariableSegment=RegexParser(
        r"@@[A-Za-z0-9_]+", CodeSegment, type="system_variable"
    ),
    StatementAndDelimiterGrammar=Sequence(
        Ref("StatementSegment"),
        Ref("DelimiterGrammar", optional=True),
    ),
    OneOrMoreStatementsGrammar=AnyNumberOf(
        Ref("StatementAndDelimiterGrammar"),
        min_times=1,
    ),
    TopPercentGrammar=Sequence(
        "TOP",
        OptionallyBracketed(Ref("ExpressionSegment")),
        Ref.keyword("PERCENT", optional=True),
    ),
    CursorNameGrammar=OneOf(
        Sequence(Ref.keyword("GLOBAL", optional=True), Ref("NakedIdentifierSegment")),
        Ref("ParameterNameSegment"),
    ),
    CredentialGrammar=Sequence(
        "IDENTITY",
        Ref("EqualsSegment"),
        Ref("QuotedLiteralSegment"),
        Sequence(
            Ref("CommaSegment"),
            "SECRET",
            Ref("EqualsSegment"),
            Ref("QuotedLiteralSegment"),
            optional=True,
        ),
    ),
    AzureBlobStoragePath=RegexParser(
        r"'https://[a-z0-9][a-z0-9-]{1,61}[a-z0-9]\.blob\.core\.windows\.net/[a-z0-9]"
        r"[a-z0-9\.-]{1,61}[a-z0-9](?:/.+)?'",
        CodeSegment,
        type="external_location",
    ),
    AzureDataLakeStorageGen2Path=RegexParser(
        r"'https://[a-z0-9][a-z0-9-]{1,61}[a-z0-9]\.dfs\.core\.windows\.net/[a-z0-9]"
        r"[a-z0-9\.-]{1,61}[a-z0-9](?:/.+)?'",
        CodeSegment,
        type="external_location",
    ),
    SqlcmdOperatorSegment=SegmentGenerator(
        lambda dialect: MultiStringParser(
            dialect.sets("sqlcmd_operators"),
            CodeSegment,
            type="sqlcmd_operator",
        )
    ),
    SqlcmdFilePathSegment=TypedParser(
        "unquoted_relative_sql_file_path",
        CodeSegment,
        type="unquoted_relative_sql_file_path",
    ),
    FileCompressionSegment=SegmentGenerator(
        lambda dialect: MultiStringParser(
            dialect.sets("file_compression"),
            CodeSegment,
            type="file_compression",
        )
    ),
    FileEncodingSegment=SegmentGenerator(
        lambda dialect: MultiStringParser(
            dialect.sets("file_encoding"),
            CodeSegment,
            type="file_encoding",
        )
    ),
    SerdeMethodSegment=SegmentGenerator(
        lambda dialect: MultiStringParser(
            dialect.sets("serde_method"),
            CodeSegment,
            type="serde_method",
        )
    ),
    ProcedureParameterGrammar=Sequence(
        Ref("ParameterNameSegment", optional=True),
        Sequence("AS", optional=True),
        Ref("DatatypeSegment"),
        AnySetOf("VARYING", Sequence("NOT", optional=True), "NULL"),
        Sequence(Ref("EqualsSegment"), Ref("ExpressionSegment"), optional=True),
    ),
    DateFormatSegment=SegmentGenerator(
        lambda dialect: MultiStringParser(
            dialect.sets("date_format"),
            CodeSegment,
            type="date_format",
        )
    ),
)

tsql_dialect.replace(
    # Overriding to cover TSQL allowed identifier name characters
    # https://docs.microsoft.com/en-us/sql/relational-databases/databases/database-identifiers?view=sql-server-ver15
    NakedIdentifierSegment=SegmentGenerator(
        # Generate the anti template from the set of reserved keywords
        lambda dialect: RegexParser(
            r"[A-Z_][A-Z0-9_@$#]*",
            IdentifierSegment,
            type="naked_identifier",
            anti_template=r"^("
            + r"|".join(
                dialect.sets("reserved_keywords")
                | dialect.sets("future_reserved_keywords")
            )
            + r")$",
        )
    ),
    # Overring ANSI BaseExpressionElement to remove Interval Expression Segment
    BaseExpressionElementGrammar=ansi_dialect.get_grammar(
        "BaseExpressionElementGrammar"
    ).copy(
        remove=[
            Ref("IntervalExpressionSegment"),
        ]
    ),
    SingleIdentifierGrammar=OneOf(
        Ref("NakedIdentifierSegment"),
        Ref("QuotedIdentifierSegment"),
        Ref("BracketedIdentifierSegment"),
        Ref("HashIdentifierSegment"),
        Ref("ParameterNameSegment"),
        Ref("VariableIdentifierSegment"),
    ),
    LiteralGrammar=ansi_dialect.get_grammar("LiteralGrammar")
    .copy(
        insert=[
            Ref("QuotedLiteralSegmentWithN"),
        ],
        before=Ref("NumericLiteralSegment"),
        remove=[
            Ref("ArrayLiteralSegment"),
            Ref("ObjectLiteralSegment"),
        ],
    )
    .copy(
        insert=[
            Ref("ParameterNameSegment"),
            Ref("SystemVariableSegment"),
        ],
    ),
    ParameterNameSegment=RegexParser(r"@[A-Za-z0-9_]+", CodeSegment, type="parameter"),
    FunctionParameterGrammar=Sequence(
        Ref("ParameterNameSegment", optional=True),
        Sequence("AS", optional=True),
        Ref("DatatypeSegment"),
        Sequence("NULL", optional=True),
        Sequence(Ref("EqualsSegment"), Ref("ExpressionSegment"), optional=True),
    ),
    FunctionNameIdentifierSegment=SegmentGenerator(
        # Generate the anti template from the set of reserved keywords
        # minus the function names that are reserved words.
        lambda dialect: RegexParser(
            r"[A-Z][A-Z0-9_]*|\[[A-Z][A-Z0-9_]*\]",
            CodeSegment,
            type="function_name_identifier",
            anti_template=r"^("
            + r"|".join(
                dialect.sets("reserved_keywords")
                | dialect.sets("future_reserved_keywords")
            )
            + r")$",
        )
    ),
    NanLiteralSegment=Nothing(),
    DatatypeIdentifierSegment=SegmentGenerator(
        # Generate the anti template reserved keywords
        lambda dialect: OneOf(
            RegexParser(
                r"[A-Z][A-Z0-9_]*|\[[A-Z][A-Z0-9_]*\]",
                CodeSegment,
                type="data_type_identifier",
                # anti_template=r"^(NOT)$",
                anti_template=r"^("
                + r"|".join(
                    dialect.sets("reserved_keywords")
                    | dialect.sets("future_reserved_keywords")
                )
                + r")$",
                # TODO - this is a stopgap until we implement explicit data types
            ),
            Ref("SingleIdentifierGrammar", exclude=Ref("NakedIdentifierSegment")),
        ),
    ),
    PrimaryKeyGrammar=Sequence(
        OneOf(
            Sequence(
                "PRIMARY",
                "KEY",
            ),
            "UNIQUE",
        ),
        OneOf(
            "CLUSTERED",
            "NONCLUSTERED",
            optional=True,
        ),
    ),
    FromClauseTerminatorGrammar=OneOf(
        "WHERE",
        Sequence("GROUP", "BY"),
        Sequence("ORDER", "BY"),
        "HAVING",
        Ref("SetOperatorSegment"),
        Ref("WithNoSchemaBindingClauseSegment"),
        Ref("DelimiterGrammar"),
    ),
    # Replace ANSI LikeGrammar to remove TSQL non-keywords RLIKE and ILIKE
    LikeGrammar=Sequence(
        "LIKE",
    ),
    # Replace ANSI FunctionContentsGrammar to remove TSQL non-keyword Separator
    # TODO: fully represent TSQL functionality
    FunctionContentsGrammar=AnyNumberOf(
        Ref("ExpressionSegment"),
        # A Cast-like function
        Sequence(Ref("ExpressionSegment"), "AS", Ref("DatatypeSegment")),
        # An extract-like or substring-like function
        Sequence(
            OneOf(Ref("DatetimeUnitSegment"), Ref("ExpressionSegment")),
            "FROM",
            Ref("ExpressionSegment"),
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
        Ref("OrderByClauseSegment"),
        # used by string_agg (postgres), group_concat (exasol),listagg (snowflake)...
        # like a function call: POSITION ( 'QL' IN 'SQL')
        Sequence(
            OneOf(
                Ref("QuotedLiteralSegment"),
                Ref("SingleIdentifierGrammar"),
                Ref("ColumnReferenceSegment"),
            ),
            "IN",
            OneOf(
                Ref("QuotedLiteralSegment"),
                Ref("SingleIdentifierGrammar"),
                Ref("ColumnReferenceSegment"),
            ),
        ),
        Sequence(OneOf("IGNORE", "RESPECT"), "NULLS"),
    ),
    JoinTypeKeywordsGrammar=Sequence(
        OneOf(
            "INNER",
            Sequence(
                OneOf(
                    "FULL",
                    "LEFT",
                    "RIGHT",
                ),
                Ref.keyword("OUTER", optional=True),
            ),
        ),
        OneOf(
            "LOOP",
            "HASH",
            "MERGE",
            optional=True,
        ),
        optional=True,
    ),
    JoinKeywordsGrammar=OneOf("JOIN", "APPLY"),
    ConditionalCrossJoinKeywordsGrammar=Nothing(),
    NaturalJoinKeywordsGrammar=Ref.keyword("CROSS"),
    ExtendedNaturalJoinKeywordsGrammar=Sequence("OUTER", "APPLY"),
    NestedJoinGrammar=Sequence(
        Indent,
        Ref("JoinClauseSegment"),
        Dedent,
    ),
    # Replace Expression_D_Grammar to remove casting syntax invalid in TSQL
    Expression_D_Grammar=Sequence(
        OneOf(
            Ref("BareFunctionSegment"),
            Ref("FunctionSegment"),
            Bracketed(
                OneOf(
                    # We're using the expression segment here rather than the grammar so
                    # that in the parsed structure we get nested elements.
                    Ref("ExpressionSegment"),
                    Ref("SelectableGrammar"),
                    Delimited(
                        Ref(
                            "ColumnReferenceSegment"
                        ),  # WHERE (a,b,c) IN (select a,b,c FROM...)
                        Ref(
                            "FunctionSegment"
                        ),  # WHERE (a, substr(b,1,3)) IN (select c,d FROM...)
                        Ref("LiteralGrammar"),  # WHERE (a, 2) IN (SELECT b, c FROM ...)
                    ),
                ),
                parse_mode=ParseMode.GREEDY,
            ),
            # Allow potential select statement without brackets
            Ref("SelectStatementSegment"),
            Ref("LiteralGrammar"),
            Ref("ColumnReferenceSegment"),
            Ref("TypedArrayLiteralSegment"),
            Ref("ArrayLiteralSegment"),
        ),
        Ref("AccessorGrammar", optional=True),
        allow_gaps=True,
    ),
    MergeIntoLiteralGrammar=Sequence(
        "MERGE",
        Ref("TopPercentGrammar", optional=True),
        Ref.keyword("INTO", optional=True),
    ),
    TrimParametersGrammar=Nothing(),
    TemporaryGrammar=Nothing(),
    JoinLikeClauseGrammar=AnySetOf(
        Ref("PivotUnpivotStatementSegment"),
        min_times=1,
    ),
    CollateGrammar=Sequence("COLLATE", Ref("CollationReferenceSegment")),
)


class StatementSegment(ansi.StatementSegment):
    """Overriding StatementSegment to allow for additional segment parsing."""

    match_grammar = ansi.StatementSegment.match_grammar.copy(
        insert=[
            Ref("IfExpressionStatement"),
            Ref("DeclareStatementSegment"),
            Ref("DeclareCursorStatementSegment"),
            Ref("SetStatementSegment"),
            Ref("AlterTableSwitchStatementSegment"),
            Ref("PrintStatementSegment"),
            Ref(
                "CreateTableAsSelectStatementSegment"
            ),  # Azure Synapse Analytics specific
            Ref("RenameStatementSegment"),  # Azure Synapse Analytics specific
            Ref("ExecuteScriptSegment"),
            Ref("DropStatisticsStatementSegment"),
            Ref("DropProcedureStatementSegment"),
            Ref("UpdateStatisticsStatementSegment"),
            Ref("BeginEndSegment"),
            Ref("TryCatchSegment"),
            Ref("MergeStatementSegment"),
            Ref("ThrowStatementSegment"),
            Ref("RaiserrorStatementSegment"),
            Ref("ReturnStatementSegment"),
            Ref("GotoStatement"),
            Ref("LabelStatementSegment"),
            Ref("DisableTriggerStatementSegment"),
            Ref("WhileExpressionStatement"),
            Ref("BreakStatement"),
            Ref("ContinueStatement"),
            Ref("WaitForStatementSegment"),
            Ref("OpenCursorStatementSegment"),
            Ref("CloseCursorStatementSegment"),
            Ref("DeallocateCursorStatementSegment"),
            Ref("FetchCursorStatementSegment"),
            Ref("CreateTypeStatementSegment"),
            Ref("CreateSynonymStatementSegment"),
            Ref("DropSynonymStatementSegment"),
            Ref("BulkInsertStatementSegment"),
            Ref("AlterIndexStatementSegment"),
            Ref("CreateDatabaseScopedCredentialStatementSegment"),
            Ref("CreateExternalDataSourceStatementSegment"),
            Ref("SqlcmdCommandSegment"),
            Ref("CreateExternalFileFormat"),
            Ref("CreateExternalTableStatementSegment"),
            Ref("DropExternalTableStatementSegment"),
            Ref("CopyIntoTableStatementSegment"),
            Ref("CreateFullTextIndexStatementSegment"),
            Ref("AtomicBeginEndSegment"),
        ],
        remove=[
            Ref("CreateModelStatementSegment"),
            Ref("DropModelStatementSegment"),
            Ref("DescribeStatementSegment"),
        ],
    )


class GreaterThanOrEqualToSegment(CompositeComparisonOperatorSegment):
    """Greater than or equal to operator.

    N.B. Patching to add !< and
    to allow spaces between operators.
    """

    match_grammar = OneOf(
        Sequence(
            Ref("RawGreaterThanSegment"),
            Ref("RawEqualsSegment"),
        ),
        Sequence(
            Ref("RawNotSegment"),
            Ref("RawLessThanSegment"),
        ),
    )


class LessThanOrEqualToSegment(CompositeComparisonOperatorSegment):
    """Greater than or equal to operator.

    N.B. Patching to add !> and
    to allow spaces between operators.
    """

    match_grammar = OneOf(
        Sequence(
            Ref("RawLessThanSegment"),
            Ref("RawEqualsSegment"),
        ),
        Sequence(
            Ref("RawNotSegment"),
            Ref("RawGreaterThanSegment"),
        ),
    )


class NotEqualToSegment(CompositeComparisonOperatorSegment):
    """Not equal to operator.

    N.B. Patching to allow spaces between operators.
    """

    match_grammar = OneOf(
        Sequence(Ref("RawNotSegment"), Ref("RawEqualsSegment")),
        Sequence(Ref("RawLessThanSegment"), Ref("RawGreaterThanSegment")),
    )


class SelectClauseElementSegment(ansi.SelectClauseElementSegment):
    """An element in the targets of a select statement.

    Overriding ANSI to remove greedy logic which assumes statements have been
    delimited
    """

    # Important to split elements before parsing, otherwise debugging is really hard.
    match_grammar = OneOf(
        # *, blah.*, blah.blah.*, etc.
        Ref("WildcardExpressionSegment"),
        Sequence(
            Ref("AltAliasExpressionSegment"),
            Ref("BaseExpressionElementGrammar"),
        ),
        Sequence(
            Ref("BaseExpressionElementGrammar"),
            Ref("AliasExpressionSegment", optional=True),
        ),
    )


class AltAliasExpressionSegment(BaseSegment):
    """An alternative alias clause as used by tsql using `=`."""

    type = "alias_expression"
    match_grammar = Sequence(
        OneOf(
            Ref("SingleIdentifierGrammar"),
            Ref("SingleQuotedIdentifierSegment"),
        ),
        Ref("RawEqualsSegment"),
    )


class SelectClauseModifierSegment(BaseSegment):
    """Things that come after SELECT but before the columns."""

    type = "select_clause_modifier"
    match_grammar = AnyNumberOf(
        "DISTINCT",
        "ALL",
        Sequence(
            # https://docs.microsoft.com/en-us/sql/t-sql/queries/top-transact-sql?view=sql-server-ver15
            "TOP",
            OptionallyBracketed(Ref("ExpressionSegment")),
            Sequence("PERCENT", optional=True),
            Sequence("WITH", "TIES", optional=True),
        ),
    )


class SelectClauseSegment(BaseSegment):
    """A group of elements in a select target statement.

    Overriding ANSI to remove greedy logic which assumes statements have been
    delimited
    """

    type = "select_clause"
    match_grammar: Matchable = Sequence(
        "SELECT",
        Ref("SelectClauseModifierSegment", optional=True),
        Indent,
        # NOTE: Don't allow trailing.
        Delimited(Ref("SelectClauseElementSegment")),
        Dedent,
        # NOTE: In TSQL - this grammar is NOT greedy.
    )


class UnorderedSelectStatementSegment(BaseSegment):
    """A `SELECT` statement without any ORDER clauses or later.

    We need to change ANSI slightly to remove LimitClauseSegment
    and NamedWindowSegment which don't exist in T-SQL.

    We also need to get away from ANSI's use of terminators.
    There's not a clean list of terminators that can be used
    to identify the end of a TSQL select statement.  Semi-colon is optional.
    """

    type = "select_statement"
    match_grammar = Sequence(
        Ref("SelectClauseSegment"),
        Ref("IntoTableSegment", optional=True),
        Ref("FromClauseSegment", optional=True),
        Ref("WhereClauseSegment", optional=True),
        Ref("GroupByClauseSegment", optional=True),
        Ref("HavingClauseSegment", optional=True),
    )


class InsertStatementSegment(BaseSegment):
    """An `INSERT` statement.

    Overriding ANSI definition to remove terminator logic that doesn't handle optional
    delimitation well.
    """

    type = "insert_statement"
    match_grammar = Sequence(
        "INSERT",
        Ref.keyword("INTO", optional=True),
        Ref("TableReferenceSegment"),
        Ref("PostTableExpressionGrammar", optional=True),
        Ref("BracketedColumnReferenceListGrammar", optional=True),
        Ref("OutputClauseSegment", optional=True),
        OneOf(
            Ref("SelectableGrammar"),
            Ref("ExecuteScriptSegment"),
            Ref("DefaultValuesGrammar"),
        ),
    )


class BulkInsertStatementSegment(BaseSegment):
    """A `BULK INSERT` statement.

    https://learn.microsoft.com/en-us/sql/t-sql/statements/bulk-insert-transact-sql?view=sql-server-ver16
    """

    type = "bulk_insert_statement"
    match_grammar = Sequence(
        "BULK",
        "INSERT",
        Ref("TableReferenceSegment"),
        "FROM",
        Ref("QuotedLiteralSegment"),
        Ref("BulkInsertStatementWithSegment", optional=True),
    )


class BulkInsertStatementWithSegment(BaseSegment):
    """A `WITH` segment in the BULK INSERT statement.

    https://learn.microsoft.com/en-us/sql/t-sql/statements/bulk-insert-transact-sql?view=sql-server-ver16
    """

    type = "bulk_insert_with_segment"
    match_grammar = Sequence(
        "WITH",
        Bracketed(
            Delimited(
                AnyNumberOf(
                    Sequence(
                        OneOf(
                            "BATCHSIZE",
                            "FIRSTROW",
                            "KILOBYTES_PER_BATCH",
                            "LASTROW",
                            "MAXERRORS",
                            "ROWS_PER_BATCH",
                        ),
                        Ref("EqualsSegment"),
                        Ref("NumericLiteralSegment"),
                    ),
                    Sequence(
                        OneOf(
                            "CODEPAGE",
                            "DATAFILETYPE",
                            "DATA_SOURCE",
                            "ERRORFILE",
                            "ERRORFILE_DATA_SOURCE",
                            "FORMATFILE_DATA_SOURCE",
                            "ROWTERMINATOR",
                            "FORMAT",
                            "FIELDQUOTE",
                            "FORMATFILE",
                            "FIELDTERMINATOR",
                        ),
                        Ref("EqualsSegment"),
                        Ref("QuotedLiteralSegment"),
                    ),
                    Sequence(
                        "ORDER",
                        Bracketed(
                            Delimited(
                                Sequence(
                                    Ref("ColumnReferenceSegment"),
                                    OneOf("ASC", "DESC", optional=True),
                                ),
                            ),
                        ),
                    ),
                    "CHECK_CONSTRAINTS",
                    "FIRE_TRIGGERS",
                    "KEEPIDENTITY",
                    "KEEPNULLS",
                    "TABLOCK",
                )
            )
        ),
    )


class WithCompoundStatementSegment(BaseSegment):
    """A `SELECT` statement preceded by a selection of `WITH` clauses.

    `WITH tab (col1,col2) AS (SELECT a,b FROM x)`

    Overriding ANSI to remove the greedy use of terminators.
    """

    type = "with_compound_statement"
    # match grammar
    match_grammar = Sequence(
        "WITH",
        Ref.keyword("RECURSIVE", optional=True),
        Conditional(Indent, indented_ctes=True),
        Delimited(
            Ref("CTEDefinitionSegment"),
            terminators=["SELECT"],
        ),
        Conditional(Dedent, indented_ctes=True),
        OneOf(
            Ref("NonWithSelectableGrammar"),
            Ref("NonWithNonSelectableGrammar"),
            Ref("MergeStatementSegment"),
        ),
    )


class SelectStatementSegment(BaseSegment):
    """A `SELECT` statement.

    We need to change ANSI slightly to remove LimitClauseSegment
    and NamedWindowSegment which don't exist in T-SQL.

    We also need to get away from ANSI's use of terminators.
    There's not a clean list of terminators that can be used
    to identify the end of a TSQL select statement.  Semi-colon is optional.
    """

    type = "select_statement"
    # Remove the Limit and Window statements from ANSI
    match_grammar = UnorderedSelectStatementSegment.match_grammar.copy(
        insert=[
            Ref("OrderByClauseSegment", optional=True),
            Ref("OptionClauseSegment", optional=True),
            Ref("DelimiterGrammar", optional=True),
            Ref("ForClauseSegment", optional=True),
        ]
    )


class IntoTableSegment(BaseSegment):
    """`INTO` clause within `SELECT`.

    https://docs.microsoft.com/en-us/sql/t-sql/queries/select-into-clause-transact-sql?view=sql-server-ver15
    """

    type = "into_table_clause"
    match_grammar = Sequence("INTO", Ref("ObjectReferenceSegment"))


class WhereClauseSegment(BaseSegment):
    """A `WHERE` clause like in `SELECT` or `INSERT`.

    Overriding ANSI in order to get away from the use of
    terminators. There's not a clean list of terminators that can be used
    to identify the end of a TSQL select statement.  Semi-colon is optional.
    """

    type = "where_clause"
    match_grammar = Sequence(
        "WHERE",
        ImplicitIndent,
        OptionallyBracketed(Ref("ExpressionSegment")),
        Dedent,
    )


class CreateIndexStatementSegment(BaseSegment):
    """A `CREATE INDEX` or `CREATE STATISTICS` statement.

    https://docs.microsoft.com/en-us/sql/t-sql/statements/create-index-transact-sql?view=sql-server-ver15
    https://docs.microsoft.com/en-us/sql/t-sql/statements/create-statistics-transact-sql?view=sql-server-ver15
    """

    type = "create_index_statement"
    match_grammar = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        Sequence("UNIQUE", optional=True),
        OneOf("CLUSTERED", "NONCLUSTERED", optional=True),
        OneOf("INDEX", "STATISTICS"),
        Ref("IfNotExistsGrammar", optional=True),
        Ref("IndexReferenceSegment"),
        Indent,
        "ON",
        Ref("TableReferenceSegment"),
        Ref("BracketedIndexColumnListGrammar"),
        Sequence(
            "INCLUDE",
            Ref("BracketedColumnReferenceListGrammar"),
            optional=True,
        ),
        Ref("WhereClauseSegment", optional=True),
        Ref("RelationalIndexOptionsSegment", optional=True),
        Ref("OnPartitionOrFilegroupOptionSegment", optional=True),
        Ref("FilestreamOnOptionSegment", optional=True),
        Ref("DelimiterGrammar", optional=True),
        Dedent,
    )


class CreateFullTextIndexStatementSegment(BaseSegment):
    """A `CREATE FULLTEXT INDEX` statement.

    https://learn.microsoft.com/fr-fr/sql/t-sql/statements/create-fulltext-index-transact-sql?view=sql-server-ver16
    """

    type = "create_fulltext_index_statement"

    _catalog_filegroup_option = Sequence(
        "ON",
        Delimited(
            AnySetOf(
                Ref("ObjectReferenceSegment"),
                Sequence(
                    "FILEGROUP",
                    Ref("ObjectReferenceSegment"),
                ),
            ),
            allow_trailing=True,
        ),
        optional=True,
    )

    _with_option = Sequence(
        "WITH",
        Bracketed(
            OneOf(
                Sequence(
                    "CHANGE_TRACKING",
                    Ref("EqualsSegment", optional=True),
                    OneOf(
                        "MANUAL",
                        "AUTO",
                        Delimited(
                            "OFF",
                            Sequence(
                                "NO",
                                "POPULATION",
                                optional=True,
                            ),
                        ),
                    ),
                ),
                Sequence(
                    "STOPLIST",
                    Ref("EqualsSegment", optional=True),
                    OneOf(
                        "OFF",
                        "SYSTEM",
                        Ref("ObjectReferenceSegment"),
                    ),
                ),
                Sequence(
                    "SEARCH",
                    "PROPERTY",
                    "LIST",
                    Ref("EqualsSegment", optional=True),
                    Ref("ObjectReferenceSegment"),
                ),
            ),
        ),
        optional=True,
    )

    match_grammar = Sequence(
        "CREATE",
        "FULLTEXT",
        "INDEX",
        "ON",
        Ref("TableReferenceSegment"),
        Bracketed(
            Delimited(
                Sequence(
                    Ref("ColumnReferenceSegment"),
                    AnySetOf(
                        Sequence(
                            "TYPE",
                            "COLUMN",
                            Ref("DatatypeSegment"),
                        ),
                        Sequence(
                            "LANGUAGE",
                            OneOf(
                                Ref("NumericLiteralSegment"),
                                Ref("QuotedLiteralSegment"),
                                optional=True,
                            ),
                        ),
                        "STATISTICAL_SEMANTICS",
                    ),
                ),
            ),
        ),
        Sequence(
            "KEY",
            "INDEX",
            Ref("ObjectReferenceSegment"),
            _catalog_filegroup_option,
        ),
        _with_option,
    )


class AlterIndexStatementSegment(BaseSegment):
    """An ALTER INDEX statement.

    As per.
    https://learn.microsoft.com/en-us/sql/t-sql/statements/alter-index-transact-sql?view=sql-server-ver15
    """

    type = "alter_index_statement"

    _low_priority_lock_wait = Sequence(
        "WAIT_AT_LOW_PRIORITY",
        Bracketed(
            Sequence(
                "MAX_DURATION",
                Ref("EqualsSegment"),
                Ref("NumericLiteralSegment"),
                Ref.keyword("MINUTES", optional=True),
            ),
            Ref("CommaSegment"),
            Sequence(
                "ABORT_AFTER_WAIT",
                Ref("EqualsSegment"),
                OneOf(
                    "NONE",
                    "SELF",
                    "BLOCKERS",
                ),
            ),
        ),
    )

    _on_partitions = Sequence(
        Sequence(
            "ON",
            "PARTITIONS",
        ),
        Bracketed(
            Delimited(
                Ref("NumericLiteralSegment"),
            ),
            Sequence(
                "TO",
                Ref("NumericLiteralSegment"),
                optional=True,
            ),
        ),
        optional=True,
    )

    _rebuild_index_option = AnyNumberOf(
        Sequence(
            OneOf(
                "PAD_INDEX",
                "SORT_IN_TEMPDB",
                "IGNORE_DUP_KEY",
                "STATISTICS_NORECOMPUTE",
                "STATISTICS_INCREMENTAL",
                "RESUMABLE",
                "ALLOW_ROW_LOCKS",
                "ALLOW_PAGE_LOCKS",
            ),
            Ref("EqualsSegment"),
            OneOf(
                "ON",
                "OFF",
            ),
        ),
        Sequence(
            OneOf(
                "MAXDOP",
                "FILLFACTOR",
                "MAX_DURATION",
            ),
            Ref("EqualsSegment"),
            Ref("NumericLiteralSegment"),
            Ref.keyword("MINUTES", optional=True),
        ),
        Sequence(
            "ONLINE",
            Ref("EqualsSegment"),
            OneOf(
                Sequence(
                    "ON",
                    Bracketed(
                        _low_priority_lock_wait,
                        optional=True,
                    ),
                ),
                "OFF",
            ),
        ),
        Sequence(
            "DATA_COMPRESSION",
            Ref("EqualsSegment"),
            OneOf(
                "NONE",
                "ROW",
                "PAGE",
                "COLUMNSTORE",
                "COLUMNSTORE_ARCHIVE",
            ),
            _on_partitions,
        ),
        Sequence(
            "XML_COMPRESSION",
            Ref("EqualsSegment"),
            OneOf(
                "ON",
                "OFF",
            ),
            _on_partitions,
        ),
    )

    _single_partition_rebuild_index_option = AnyNumberOf(
        Sequence(
            OneOf(
                "XML_COMPRESSION",
                "SORT_IN_TEMPDB",
                "RESUMABLE",
            ),
            Ref("EqualsSegment"),
            OneOf(
                "ON",
                "OFF",
            ),
        ),
        Sequence(
            OneOf(
                "MAXDOP",
                "MAX_DURATION",
            ),
            Ref("EqualsSegment"),
            Ref("NumericLiteralSegment"),
            Ref.keyword("MINUTES", optional=True),
        ),
        Sequence(
            "DATA_COMPRESSION",
            Ref("EqualsSegment"),
            OneOf(
                "NONE",
                "ROW",
                "PAGE",
                "COLUMNSTORE",
                "COLUMNSTORE_ARCHIVE",
            ),
        ),
        Sequence(
            "ONLINE",
            Ref("EqualsSegment"),
            OneOf(
                Sequence(
                    "ON",
                    Bracketed(
                        _low_priority_lock_wait,
                        optional=True,
                    ),
                ),
                "OFF",
            ),
        ),
    )

    match_grammar = Sequence(
        "ALTER",
        "INDEX",
        OneOf(
            Ref("ObjectReferenceSegment"),
            "ALL",
        ),
        "ON",
        Ref("TableReferenceSegment"),
        OneOf(
            Sequence(
                "REBUILD",
                OneOf(
                    Sequence(
                        Sequence(
                            "PARTITION",
                            Ref("EqualsSegment"),
                            "ALL",
                            optional=True,
                        ),
                        Sequence(
                            "WITH",
                            Bracketed(
                                Delimited(
                                    _rebuild_index_option,
                                )
                            ),
                            optional=True,
                        ),
                    ),
                    Sequence(
                        Sequence(
                            "PARTITION",
                            Ref("EqualsSegment"),
                            Ref("NumericLiteralSegment"),
                            optional=True,
                        ),
                        Sequence(
                            "WITH",
                            Bracketed(
                                Delimited(
                                    _single_partition_rebuild_index_option,
                                ),
                            ),
                            optional=True,
                        ),
                    ),
                    optional=True,
                ),
            ),
            "DISABLE",
            Sequence(
                "REORGANIZE",
                Sequence(
                    "PARTITION",
                    Ref("EqualsSegment"),
                    Ref("NumericLiteralSegment"),
                    optional=True,
                ),
                Sequence(
                    "WITH",
                    Bracketed(
                        Sequence(
                            OneOf(
                                "LOB_COMPACTION",
                                "COMPRESS_ALL_ROW_GROUPS",
                            ),
                            Ref("EqualsSegment"),
                            OneOf(
                                "ON",
                                "OFF",
                            ),
                        ),
                    ),
                    optional=True,
                ),
            ),
            Sequence(
                "SET",
                Bracketed(
                    Delimited(
                        AnyNumberOf(
                            Sequence(
                                OneOf(
                                    "ALLOW_ROW_LOCKS",
                                    "ALLOW_PAGE_LOCKS",
                                    "OPTIMIZE_FOR_SEQUENTIAL_KEY",
                                    "IGNORE_DUP_KEY",
                                    "STATISTICS_NORECOMPUTE",
                                ),
                                Ref("EqualsSegment"),
                                OneOf(
                                    "ON",
                                    "OFF",
                                ),
                            ),
                            Sequence(
                                "COMPRESSION_DELAY",
                                Ref("EqualsSegment"),
                                Ref("NumericLiteralSegment"),
                                Ref.keyword("MINUTES", optional=True),
                            ),
                        ),
                    ),
                ),
            ),
            Sequence(
                "RESUME",
                Sequence(
                    "WITH",
                    Bracketed(
                        Delimited(
                            Sequence(
                                OneOf(
                                    "MAX_DURATION",
                                    "MAXDOP",
                                ),
                                Ref("EqualsSegment"),
                                Ref("NumericLiteralSegment"),
                                Ref.keyword("MINUTES", optional=True),
                            ),
                            _low_priority_lock_wait,
                        ),
                    ),
                    optional=True,
                ),
            ),
            "PAUSE",
            "ABORT",
        ),
    )


class OnPartitionOrFilegroupOptionSegment(BaseSegment):
    """ON partition scheme or filegroup option.

    https://docs.microsoft.com/en-us/sql/t-sql/statements/create-index-transact-sql?view=sql-server-ver15
    https://docs.microsoft.com/en-us/sql/t-sql/statements/create-table-transact-sql?view=sql-server-ver15
    """

    type = "on_partition_or_filegroup_statement"
    match_grammar = OneOf(
        Ref("PartitionSchemeClause"),
        Ref("FilegroupClause"),
        Ref("LiteralGrammar"),  # for "default" value
    )


class FilestreamOnOptionSegment(BaseSegment):
    """FILESTREAM_ON index option in `CREATE INDEX` and 'CREATE TABLE' statements.

    https://docs.microsoft.com/en-us/sql/t-sql/statements/create-index-transact-sql?view=sql-server-ver15
    https://docs.microsoft.com/en-us/sql/t-sql/statements/create-table-transact-sql?view=sql-server-ver15
    """

    type = "filestream_on_option_statement"
    match_grammar = Sequence(
        "FILESTREAM_ON",
        OneOf(
            Ref("FilegroupNameSegment"),
            Ref("PartitionSchemeNameSegment"),
            OneOf(
                "NULL",
                Ref("LiteralGrammar"),  # for "default" value
            ),
        ),
    )


class TextimageOnOptionSegment(BaseSegment):
    """TEXTIMAGE ON option in `CREATE TABLE` statement.

    https://docs.microsoft.com/en-us/sql/t-sql/statements/create-table-transact-sql?view=sql-server-ver15
    """

    type = "textimage_on_option_statement"
    match_grammar = Sequence(
        "TEXTIMAGE_ON",
        OneOf(
            Ref("FilegroupNameSegment"),
            Ref("LiteralGrammar"),  # for "default" value
        ),
    )


class TableOptionSegment(BaseSegment):
    """TABLE option in `CREATE TABLE` statement.

    https://learn.microsoft.com/en-us/sql/t-sql/statements/create-table-transact-sql?view=sql-server-ver15
    """

    _ledger_view_option = Delimited(
        Sequence(
            OneOf(
                "TRANSACTION_ID_COLUMN_NAME",
                "SEQUENCE_NUMBER_COLUMN_NAME",
                "OPERATION_TYPE_COLUMN_NAME",
                "OPERATION_TYPE_DESC_COLUMN_NAME",
            ),
            Ref("EqualsSegment"),
            Ref("ColumnReferenceSegment"),
            optional=True,
        ),
    )

    _on_partitions = Sequence(
        Sequence(
            "ON",
            "PARTITIONS",
        ),
        Bracketed(
            Delimited(
                Ref("NumericLiteralSegment"),
            ),
            Sequence(
                "TO",
                Ref("NumericLiteralSegment"),
                optional=True,
            ),
        ),
        optional=True,
    )

    type = "table_option_statement"

    match_grammar = Sequence(
        "WITH",
        Bracketed(
            Delimited(
                AnyNumberOf(
                    Sequence("MEMORY_OPTIMIZED", Ref("EqualsSegment"), "ON"),
                    Sequence(
                        "DURABILITY",
                        Ref("EqualsSegment"),
                        OneOf("SCHEMA_ONLY", "SCHEMA_AND_DATA"),
                    ),
                    Sequence(
                        "SYSTEM_VERSIONING",
                        Ref("EqualsSegment"),
                        "ON",
                        Bracketed(
                            Delimited(
                                AnyNumberOf(
                                    Sequence(
                                        "HISTORY_TABLE",
                                        Ref("EqualsSegment"),
                                        Ref("TableReferenceSegment"),
                                    ),
                                    Sequence(
                                        "HISTORY_RETENTION_PERIOD",
                                        Ref("EqualsSegment"),
                                        OneOf(
                                            "INFINITE",
                                            Sequence(
                                                Ref(
                                                    "NumericLiteralSegment",
                                                    optional=True,
                                                ),
                                                OneOf(
                                                    "DAYS",
                                                    "WEEKS",
                                                    "MONTHS",
                                                    "YEARS",
                                                ),
                                                optional=True,
                                            ),
                                        ),
                                    ),
                                    Sequence(
                                        Ref("CommaSegment"),
                                        "DATA_CONSISTENCY_CHECK",
                                        Ref("EqualsSegment"),
                                        OneOf("ON", "OFF"),
                                    ),
                                ),
                            ),
                        ),
                    ),
                    Sequence(
                        "DATA_COMPRESSION",
                        Ref("EqualsSegment"),
                        OneOf(
                            "NONE",
                            "ROW",
                            "PAGE",
                        ),
                        _on_partitions,
                    ),
                    Sequence(
                        "XML_COMPRESSION",
                        Ref("EqualsSegment"),
                        OneOf("ON", "OFF"),
                        _on_partitions,
                    ),
                    Sequence(
                        "FILETABLE_DIRECTORY",
                        Ref("EqualsSegment"),
                        Ref("LiteralGrammar"),
                    ),
                    Sequence(
                        OneOf(
                            "FILETABLE_COLLATE_FILENAME",
                            "FILETABLE_PRIMARY_KEY_CONSTRAINT_NAME",
                            "FILETABLE_STREAMID_UNIQUE_CONSTRAINT_NAME",
                            "FILETABLE_FULLPATH_UNIQUE_CONSTRAINT_NAME",
                        ),
                        Ref("EqualsSegment"),
                        Ref("ObjectReferenceSegment"),
                    ),
                    Sequence(
                        "REMOTE_DATA_ARCHIVE",
                        Ref("EqualsSegment"),
                        OneOf(
                            Sequence(
                                "ON",
                                Bracketed(
                                    Delimited(
                                        Sequence(
                                            "FILTER_PREDICATE",
                                            Ref("EqualsSegment"),
                                            OneOf(
                                                "NULL",
                                                Ref("FunctionNameSegment"),
                                            ),
                                            optional=True,
                                        ),
                                        Sequence(
                                            "MIGRATION_STATE",
                                            Ref("EqualsSegment"),
                                            OneOf("OUTBOUND", "INBOUND", "PAUSED"),
                                        ),
                                    ),
                                    optional=True,
                                ),
                            ),
                            Sequence(
                                "OFF",
                                Bracketed(
                                    "MIGRATION_STATE",
                                    Ref("EqualsSegment"),
                                    "PAUSED",
                                ),
                            ),
                        ),
                    ),
                    Sequence(
                        "DATA_DELETION",
                        Ref("EqualsSegment"),
                        "ON",
                        Bracketed(
                            "FILTER_COLUMN",
                            Ref("EqualsSegment"),
                            Ref("ColumnReferenceSegment"),
                            Ref("CommaSegment"),
                            "RETENTION_PERIOD",
                            Ref("EqualsSegment"),
                            Ref("NumericLiteralSegment", optional=True),
                            Ref("DatetimeUnitSegment"),
                        ),
                    ),
                    Sequence(
                        "LEDGER",
                        Ref("EqualsSegment"),
                        OneOf(
                            Sequence(
                                "ON",
                                Bracketed(
                                    Delimited(
                                        Sequence(
                                            "LEDGER_VIEW",
                                            Ref("EqualsSegment"),
                                            Ref("TableReferenceSegment"),
                                            Bracketed(
                                                _ledger_view_option, optional=True
                                            ),
                                            optional=True,
                                        ),
                                        Sequence(
                                            "APPEND_ONLY",
                                            Ref("EqualsSegment"),
                                            OneOf("ON", "OFF"),
                                            optional=True,
                                        ),
                                    ),
                                    optional=True,
                                ),
                            ),
                            "OFF",
                        ),
                    ),
                )
            )
        ),
    )


class ReferencesConstraintGrammar(BaseSegment):
    """REFERENCES constraint option in `CREATE TABLE` statement.

    https://docs.microsoft.com/en-us/sql/t-sql/statements/create-table-transact-sql?view=sql-server-ver15
    """

    type = "references_constraint_grammar"
    match_grammar = Sequence(
        # REFERENCES reftable [ ( refcolumn) ]
        "REFERENCES",
        Ref("TableReferenceSegment"),
        # Foreign columns making up FOREIGN KEY constraint
        Ref("BracketedColumnReferenceListGrammar", optional=True),
        Sequence(
            "ON",
            OneOf("DELETE", "UPDATE"),
            Ref("ReferentialActionGrammar"),
            optional=True,
        ),
        Sequence("NOT", "FOR", "REPLICATION", optional=True),
    )


class CheckConstraintGrammar(BaseSegment):
    """CHECK constraint option in `CREATE TABLE` statement.

    https://docs.microsoft.com/en-us/sql/t-sql/statements/create-table-transact-sql?view=sql-server-ver15
    """

    type = "check_constraint_grammar"
    match_grammar = Sequence(
        "CHECK",
        Sequence("NOT", "FOR", "REPLICATION", optional=True),
        Bracketed(
            Ref("ExpressionSegment"),
        ),
    )


class RelationalIndexOptionsSegment(BaseSegment):
    """A relational index options in `CREATE INDEX` statement.

    https://docs.microsoft.com/en-us/sql/t-sql/statements/create-index-transact-sql?view=sql-server-ver15
    """

    type = "relational_index_options"
    match_grammar = Sequence(
        "WITH",
        OptionallyBracketed(
            Delimited(
                AnyNumberOf(
                    Sequence(
                        OneOf(
                            "PAD_INDEX",
                            "FILLFACTOR",
                            "SORT_IN_TEMPDB",
                            "IGNORE_DUP_KEY",
                            "STATISTICS_NORECOMPUTE",
                            "STATISTICS_INCREMENTAL",
                            "DROP_EXISTING",
                            "RESUMABLE",
                            "ALLOW_ROW_LOCKS",
                            "ALLOW_PAGE_LOCKS",
                            "OPTIMIZE_FOR_SEQUENTIAL_KEY",
                            "MAXDOP",
                        ),
                        Ref("EqualsSegment"),
                        OneOf(
                            "ON",
                            "OFF",
                            Ref("LiteralGrammar"),
                        ),
                    ),
                    Ref("MaxDurationSegment"),
                    Sequence(
                        "ONLINE",
                        Ref("EqualsSegment"),
                        OneOf(
                            "OFF",
                            Sequence(
                                "ON",
                                Bracketed(
                                    Sequence(
                                        "WAIT_AT_LOW_PRIORITY",
                                        Bracketed(
                                            Delimited(
                                                Ref("MaxDurationSegment"),
                                                Sequence(
                                                    "ABORT_AFTER_WAIT",
                                                    Ref("EqualsSegment"),
                                                    OneOf(
                                                        "NONE",
                                                        "SELF",
                                                        "BLOCKERS",
                                                    ),
                                                ),
                                            ),
                                        ),
                                    ),
                                    optional=True,
                                ),
                            ),
                        ),
                    ),
                    # for table constrains
                    Sequence(
                        "COMPRESSION_DELAY",
                        Ref("EqualsSegment"),
                        Ref("NumericLiteralSegment"),
                        Sequence(
                            "MINUTES",
                            optional=True,
                        ),
                    ),
                    Sequence(
                        "DATA_COMPRESSION",
                        Ref("EqualsSegment"),
                        OneOf(
                            "NONE",
                            "ROW",
                            "PAGE",
                            "COLUMNSTORE",  # for table constrains
                            "COLUMNSTORE_ARCHIVE",  # for table constrains
                        ),
                        Ref("OnPartitionsSegment", optional=True),
                    ),
                    min_times=1,
                ),
            ),
        ),
    )


class MaxDurationSegment(BaseSegment):
    """A `MAX DURATION` clause.

    https://docs.microsoft.com/en-us/sql/t-sql/statements/create-index-transact-sql?view=sql-server-ver15
    """

    type = "max_duration"
    match_grammar = Sequence(
        "MAX_DURATION",
        Ref("EqualsSegment"),
        Ref("NumericLiteralSegment"),
        Sequence(
            "MINUTES",
            optional=True,
        ),
    )


class DropIndexStatementSegment(ansi.DropIndexStatementSegment):
    """A `DROP INDEX` statement.

    Overriding ANSI to include required ON clause.
    """

    match_grammar = Sequence(
        "DROP",
        "INDEX",
        Ref("IfExistsGrammar", optional=True),
        Ref("IndexReferenceSegment"),
        "ON",
        Ref("TableReferenceSegment"),
        Ref("DelimiterGrammar", optional=True),
    )


class DropStatisticsStatementSegment(BaseSegment):
    """A `DROP STATISTICS` statement."""

    type = "drop_statement"
    # DROP INDEX <Index name> [CONCURRENTLY] [IF EXISTS] {RESTRICT | CASCADE}
    match_grammar = Sequence(
        "DROP",
        OneOf("STATISTICS"),
        Ref("IndexReferenceSegment"),
        Ref("DelimiterGrammar", optional=True),
    )


class UpdateStatisticsStatementSegment(BaseSegment):
    """An `UPDATE STATISTICS` statement.

    https://docs.microsoft.com/en-us/sql/t-sql/statements/update-statistics-transact-sql?view=sql-server-ver15
    """

    type = "update_statistics_statement"
    match_grammar = Sequence(
        "UPDATE",
        "STATISTICS",
        Ref("ObjectReferenceSegment"),
        OneOf(
            Ref("SingleIdentifierGrammar"),
            Bracketed(
                Delimited(
                    Ref("SingleIdentifierGrammar"),
                ),
            ),
            optional=True,
        ),
        Ref("DelimiterGrammar", optional=True),
        Sequence("WITH", OneOf("FULLSCAN", "RESAMPLE"), optional=True),
    )


class ObjectReferenceSegment(ansi.ObjectReferenceSegment):
    """A reference to an object.

    Update ObjectReferenceSegment to only allow dot separated SingleIdentifierGrammar
    So Square Bracketed identifiers can be matched.
    """

    # match grammar (allow whitespace)
    match_grammar: Matchable = Sequence(
        Ref("SingleIdentifierGrammar"),
        AnyNumberOf(
            Sequence(
                Ref("DotSegment"),
                Ref("SingleIdentifierGrammar", optional=True),
            ),
            min_times=0,
            max_times=3,
        ),
    )


class TableReferenceSegment(ObjectReferenceSegment):
    """A reference to an table, CTE, subquery or alias.

    Overriding to capture TSQL's override of ObjectReferenceSegment
    """

    type = "table_reference"


class SchemaReferenceSegment(ObjectReferenceSegment):
    """A reference to a schema.

    Overriding to capture TSQL's override of ObjectReferenceSegment
    """

    type = "schema_reference"


class DatabaseReferenceSegment(ObjectReferenceSegment):
    """A reference to a database.

    Overriding to capture TSQL's override of ObjectReferenceSegment
    """

    type = "database_reference"


class IndexReferenceSegment(ObjectReferenceSegment):
    """A reference to an index.

    Overriding to capture TSQL's override of ObjectReferenceSegment
    """

    type = "index_reference"


class ExtensionReferenceSegment(ObjectReferenceSegment):
    """A reference to an extension.

    Overriding to capture TSQL's override of ObjectReferenceSegment
    """

    type = "extension_reference"


class ColumnReferenceSegment(ObjectReferenceSegment):
    """A reference to column, field or alias.

    Overriding to capture TSQL's override of ObjectReferenceSegment
    """

    type = "column_reference"


class SequenceReferenceSegment(ObjectReferenceSegment):
    """A reference to a sequence.

    Overriding to capture TSQL's override of ObjectReferenceSegment
    """

    type = "sequence_reference"


class PivotColumnReferenceSegment(ObjectReferenceSegment):
    """A reference to a PIVOT column.

    Used to differentiate it from a regular column reference.
    """

    type = "pivot_column_reference"


class PivotUnpivotStatementSegment(BaseSegment):
    """Declaration of a variable.

    https://docs.microsoft.com/en-us/sql/t-sql/queries/from-using-pivot-and-unpivot?view=sql-server-ver15
    """

    type = "from_pivot_expression"
    match_grammar = Sequence(
        OneOf(
            Sequence(
                "PIVOT",
                OptionallyBracketed(
                    Sequence(
                        OptionallyBracketed(Ref("FunctionSegment")),
                        "FOR",
                        Ref("ColumnReferenceSegment"),
                        "IN",
                        Bracketed(Delimited(Ref("PivotColumnReferenceSegment"))),
                    )
                ),
            ),
            Sequence(
                "UNPIVOT",
                OptionallyBracketed(
                    Sequence(
                        OptionallyBracketed(Ref("ColumnReferenceSegment")),
                        "FOR",
                        Ref("ColumnReferenceSegment"),
                        "IN",
                        Bracketed(Delimited(Ref("PivotColumnReferenceSegment"))),
                    )
                ),
            ),
        ),
        Sequence("AS", optional=True),
        Ref("TableReferenceSegment"),
    )


class DeclareStatementSegment(BaseSegment):
    """Declaration of a variable.

    https://docs.microsoft.com/en-us/sql/t-sql/language-elements/declare-local-variable-transact-sql?view=sql-server-ver15
    """

    type = "declare_segment"
    match_grammar = Sequence(
        "DECLARE",
        Indent,
        Delimited(
            Sequence(
                Ref("ParameterNameSegment"),
                Sequence("AS", optional=True),
                OneOf(
                    Sequence(
                        Ref("DatatypeSegment"),
                        Sequence(
                            Ref("EqualsSegment"),
                            Ref("ExpressionSegment"),
                            optional=True,
                        ),
                    ),
                    Sequence(
                        "TABLE",
                        Bracketed(
                            Delimited(
                                OneOf(
                                    Ref("TableConstraintSegment"),
                                    Ref("ColumnDefinitionSegment"),
                                ),
                                allow_trailing=True,
                            )
                        ),
                    ),
                ),
            ),
        ),
        Dedent,
        Ref("DelimiterGrammar", optional=True),
    )


class DeclareCursorStatementSegment(BaseSegment):
    """Declaration of a cursor.

    https://docs.microsoft.com/en-us/sql/t-sql/language-elements/declare-cursor-transact-sql?view=sql-server-ver15
    """

    type = "declare_segment"
    match_grammar = Sequence(
        "DECLARE",
        Ref("NakedIdentifierSegment"),
        "CURSOR",
        OneOf("LOCAL", "GLOBAL", optional=True),
        OneOf("FORWARD_ONLY", "SCROLL", optional=True),
        OneOf("STATIC", "KEYSET", "DYNAMIC", "FAST_FORWARD", optional=True),
        OneOf("READ_ONLY", "SCROLL_LOCKS", "OPTIMISTIC", optional=True),
        Sequence("TYPE_WARNING", optional=True),
        "FOR",
        Ref("SelectStatementSegment"),
    )


class GoStatementSegment(BaseSegment):
    """GO signals the end of a batch of Transact-SQL statements.

    GO statements are not part of the TSQL language. They are used to signal batch
    statements so that clients know in how batches of statements can be executed.
    """

    type = "go_statement"
    match_grammar = Ref.keyword("GO")


class BracketedArguments(ansi.BracketedArguments):
    """A series of bracketed arguments.

    e.g. the bracketed part of numeric(1, 3)
    """

    match_grammar = Bracketed(
        Delimited(
            OneOf(
                # TSQL allows optional MAX in some data types
                "MAX",
                Ref("ExpressionSegment"),
            ),
            # The brackets might be empty for some cases...
            optional=True,
        ),
    )


class DatatypeSegment(BaseSegment):
    """A data type segment.

    Updated for Transact-SQL to allow bracketed data types with bracketed schemas.
    """

    type = "data_type"
    match_grammar = Sequence(
        # Some dialects allow optional qualification of data types with schemas
        Sequence(
            Ref("SingleIdentifierGrammar"),
            Ref("DotSegment"),
            allow_gaps=False,
            optional=True,
        ),
        OneOf(
            Ref("DatatypeIdentifierSegment"),
            Bracketed(Ref("DatatypeIdentifierSegment"), bracket_type="square"),
        ),
        # Stop Gap until explicit Data Types as only relevent for character
        Ref.keyword("VARYING", optional=True),
        Ref("BracketedArguments", optional=True),
        Ref("CharCharacterSetGrammar", optional=True),
    )


class CreateSequenceOptionsSegment(BaseSegment):
    """Options for Create Sequence statement.

    https://docs.microsoft.com/en-us/sql/t-sql/statements/create-sequence-transact-sql?view=sql-server-ver15
    """

    type = "create_sequence_options_segment"

    match_grammar = OneOf(
        Sequence(
            "AS",
            Ref("DatatypeSegment"),
        ),
        Sequence("START", "WITH", Ref("NumericLiteralSegment")),
        Sequence("INCREMENT", "BY", Ref("NumericLiteralSegment")),
        Sequence("MINVALUE", Ref("NumericLiteralSegment")),
        Sequence("NO", "MINVALUE"),
        Sequence("MAXVALUE", Ref("NumericLiteralSegment")),
        Sequence("NO", "MAXVALUE"),
        Sequence(
            Sequence("NO", optional=True),
            "CYCLE",
        ),
        Sequence(
            "CACHE",
            Ref("NumericLiteralSegment"),
        ),
        Sequence(
            "NO",
            "CACHE",
        ),
    )


class NextValueSequenceSegment(BaseSegment):
    """Segment to get next value from a sequence."""

    type = "sequence_next_value"
    match_grammar = Sequence(
        "NEXT",
        "VALUE",
        "FOR",
        Ref("ObjectReferenceSegment"),
    )


class IfExpressionStatement(BaseSegment):
    """IF-ELSE statement.

    https://docs.microsoft.com/en-us/sql/t-sql/language-elements/if-else-transact-sql?view=sql-server-ver15
    """

    type = "if_then_statement"

    match_grammar = Sequence(
        Ref("IfClauseSegment"),
        Indent,
        Ref("StatementAndDelimiterGrammar"),
        Dedent,
        AnyNumberOf(
            # ELSE IF included explicitly to allow for correct indentation
            Sequence(
                "ELSE",
                Ref("IfClauseSegment"),
                Indent,
                Ref("StatementAndDelimiterGrammar"),
                Dedent,
            ),
        ),
        Sequence(
            "ELSE",
            Indent,
            Ref("StatementAndDelimiterGrammar"),
            Dedent,
            optional=True,
        ),
    )


class IfClauseSegment(BaseSegment):
    """IF clause."""

    type = "if_clause"

    match_grammar = Sequence(
        "IF",
        Indent,
        Ref("ExpressionSegment"),
        Dedent,
    )


class WhileExpressionStatement(BaseSegment):
    """WHILE statement.

    https://docs.microsoft.com/en-us/sql/t-sql/language-elements/while-transact-sql?view=sql-server-ver15
    """

    type = "while_statement"

    match_grammar = Sequence(
        "WHILE",
        Ref("ExpressionSegment"),
        Indent,
        Ref("StatementAndDelimiterGrammar"),
        Dedent,
    )


class BreakStatement(BaseSegment):
    """BREAK statement.

    https://docs.microsoft.com/en-us/sql/t-sql/language-elements/break-transact-sql?view=sql-server-ver15
    """

    type = "break_statement"

    match_grammar = Sequence(
        "BREAK",
    )


class ContinueStatement(BaseSegment):
    """CONTINUE statement.

    https://docs.microsoft.com/en-us/sql/t-sql/language-elements/continue-transact-sql?view=sql-server-ver15
    """

    type = "continue_statement"

    match_grammar = Sequence(
        "CONTINUE",
    )


class WaitForStatementSegment(BaseSegment):
    """WAITFOR statement.

    https://docs.microsoft.com/en-us/sql/t-sql/language-elements/waitfor-transact-sql?view=sql-server-ver15
    Partially implemented, lacking Receive and Get Conversation Group statements for
    now.
    """

    type = "waitfor_statement"

    match_grammar = Sequence(
        "WAITFOR",
        OneOf(
            Sequence("DELAY", Ref("ExpressionSegment")),
            Sequence("TIME", Ref("ExpressionSegment")),
        ),
        Sequence("TIMEOUT", Ref("NumericLiteralSegment"), optional=True),
    )


class ColumnConstraintSegment(BaseSegment):
    """A column option; each CREATE TABLE column can have 0 or more."""

    type = "column_constraint_segment"
    # Column constraint from
    # https://docs.microsoft.com/en-us/sql/t-sql/statements/create-table-transact-sql?view=sql-server-ver15
    match_grammar = Sequence(
        Sequence(
            "CONSTRAINT",
            Ref("ObjectReferenceSegment"),  # Constraint name
            optional=True,
        ),
        OneOf(
            "FILESTREAM",
            Sequence(
                "COLLATE", Ref("CollationReferenceSegment")
            ),  # [COLLATE collation_name]
            "SPARSE",
            Sequence(
                "MASKED",
                "WITH",
                Bracketed("FUNCTION", Ref("EqualsSegment"), Ref("LiteralGrammar")),
            ),
            Sequence(
                Sequence(
                    "CONSTRAINT",
                    Ref("ObjectReferenceSegment"),  # Constraint name
                    optional=True,
                ),
                # DEFAULT <value>
                "DEFAULT",
                OptionallyBracketed(
                    OneOf(
                        OptionallyBracketed(Ref("LiteralGrammar")),  # ((-1))
                        Ref("FunctionSegment"),
                        Ref("NextValueSequenceSegment"),
                    ),
                ),
            ),
            Ref("IdentityGrammar"),
            Sequence("NOT", "FOR", "REPLICATION"),
            Sequence(
                Sequence("GENERATED", "ALWAYS", "AS"),
                OneOf("ROW", "TRANSACTION_ID", "SEQUENCE_NUMBER"),
                OneOf("START", "END"),
                Ref.keyword("HIDDEN", optional=True),
            ),
            Sequence(Ref.keyword("NOT", optional=True), "NULL"),  # NOT NULL or NULL
            "ROWGUIDCOL",
            Ref("EncryptedWithGrammar"),
            Ref("PrimaryKeyGrammar"),
            Ref("RelationalIndexOptionsSegment"),
            Ref("OnPartitionOrFilegroupOptionSegment"),
            "UNIQUE",  # UNIQUE #can be removed as included in PrimaryKeyGrammar?
            Ref("ForeignKeyGrammar"),
            Ref("ReferencesConstraintGrammar"),
            Ref("CheckConstraintGrammar"),
            Ref("FilestreamOnOptionSegment", optional=True),
            # column_index
            Sequence(
                "INDEX",
                Ref("ObjectReferenceSegment"),  # index name
                OneOf("CLUSTERED", "NONCLUSTERED", optional=True),
                # other optional blocks (RelationalIndexOptionsSegment,
                # OnIndexOptionSegment,FilestreamOnOptionSegment) are mentioned above
            ),
            # computed_column_definition
            Sequence("AS", Ref("ExpressionSegment")),
            Sequence("PERSISTED", Sequence("NOT", "NULL", optional=True)),
            # other optional blocks (RelationalIndexOptionsSegment,
            # OnIndexOptionSegment, ReferencesConstraintGrammar, CheckConstraintGrammar)
            # are mentioned above
        ),
    )


class FunctionParameterListGrammar(BaseSegment):
    """The parameters for a function ie.

    `(@city_name NVARCHAR(30), @postal_code NVARCHAR(15))`.

    Overriding ANSI (1) to optionally bracket and (2) remove Delimited
    """

    type = "function_parameter_list"
    # Function parameter list
    match_grammar = Bracketed(
        Delimited(
            Sequence(
                Ref("FunctionParameterGrammar"),
                Sequence("READONLY", optional=True),
            ),
            optional=True,
        ),
    )


class CreateFunctionStatementSegment(BaseSegment):
    """A `CREATE FUNCTION` statement.

    This version in the TSQL dialect should be a "common subset" of the
    structure of the code for those dialects.

    Updated to include AS after declaration of RETURNS. Might be integrated in ANSI
    though.

    https://www.postgresql.org/docs/9.1/sql-createfunction.html
    https://docs.snowflake.com/en/sql-reference/sql/create-function.html
    https://cloud.google.com/bigquery/docs/reference/standard-sql/user-defined-functions
    https://docs.microsoft.com/en-us/sql/t-sql/statements/create-function-transact-sql?view=sql-server-ver15
    https://learn.microsoft.com/en-us/sql/t-sql/statements/alter-function-transact-sql?view=sql-server-ver15
    """

    type = "create_function_statement"

    match_grammar = Sequence(
        OneOf("CREATE", "ALTER", Sequence("CREATE", "OR", "ALTER")),
        "FUNCTION",
        Ref("ObjectReferenceSegment"),
        Ref("FunctionParameterListGrammar"),
        Sequence(  # Optional function return type
            "RETURNS",
            OneOf(
                Ref("DatatypeSegment"),
                "TABLE",
                Sequence(
                    Ref("ParameterNameSegment"),
                    "TABLE",
                    Bracketed(
                        Delimited(
                            OneOf(
                                Ref("TableConstraintSegment"),
                                Ref("ColumnDefinitionSegment"),
                            ),
                        ),
                    ),
                ),
            ),
            optional=True,
        ),
        Ref("FunctionOptionSegment", optional=True),
        "AS",
        Ref("ProcedureDefinitionGrammar"),
    )


class FunctionOptionSegment(BaseSegment):
    """A function option segment."""

    type = "function_option_segment"
    match_grammar = Sequence(
        "WITH",
        AnyNumberOf(
            "ENCRYPTION",
            "SCHEMABINDING",
            Sequence(
                OneOf(
                    Sequence(
                        "RETURNS",
                        "NULL",
                    ),
                    "CALLED",
                ),
                "ON",
                "NULL",
                "INPUT",
            ),
            Ref("ExecuteAsClauseSegment"),
            Sequence(
                "INLINE",
                Ref("EqualsSegment"),
                OneOf(
                    "ON",
                    "OFF",
                ),
            ),
            min_times=1,
        ),
    )


class DropFunctionStatementSegment(BaseSegment):
    """A `DROP FUNCTION` statement.

    https://docs.microsoft.com/en-us/sql/t-sql/statements/drop-function-transact-sql?view=sql-server-ver15
    """

    type = "drop_function_statement"

    match_grammar = Sequence(
        "DROP",
        "FUNCTION",
        Ref("IfExistsGrammar", optional=True),
        Delimited(Ref("FunctionNameSegment")),
        Ref("DelimiterGrammar", optional=True),
    )


class ReturnStatementSegment(BaseSegment):
    """A RETURN statement."""

    type = "return_segment"
    match_grammar = Sequence(
        "RETURN",
        Ref("ExpressionSegment", optional=True),
        Ref("DelimiterGrammar", optional=True),
    )


class ExecuteAsClauseSegment(BaseSegment):
    """An EXECUTE AS clause.

    https://docs.microsoft.com/en-us/sql/t-sql/statements/execute-as-clause-transact-sql?view=sql-server-ver15
    """

    type = "execute_as_clause"
    match_grammar = Sequence(
        OneOf("EXEC", "EXECUTE"),
        "AS",
        OneOf(
            "CALLER",
            "SELF",
            "OWNER",
            Ref("QuotedLiteralSegment"),
        ),
    )


class SetStatementSegment(BaseSegment):
    """A Set statement.

    Setting an already declared variable or global variable.
    https://docs.microsoft.com/en-us/sql/t-sql/statements/set-statements-transact-sql?view=sql-server-ver15

    https://docs.microsoft.com/en-us/sql/t-sql/language-elements/set-local-variable-transact-sql?view=sql-server-ver15
    """

    type = "set_segment"
    match_grammar = Sequence(
        "SET",
        Indent,
        Delimited(
            OneOf(
                Sequence(
                    "TRANSACTION",
                    "ISOLATION",
                    "LEVEL",
                    OneOf(
                        "SNAPSHOT",
                        "SERIALIZABLE",
                        Sequence(
                            "REPEATABLE",
                            "READ",
                        ),
                        Sequence(
                            "READ",
                            OneOf(
                                "COMMITTED",
                                "UNCOMMITTED",
                            ),
                        ),
                    ),
                ),
                Sequence(
                    OneOf(
                        "DATEFIRST",
                        "DATEFORMAT",
                        "DEADLOCK_PRIORITY",
                        "LOCK_TIMEOUT",
                        "CONCAT_NULL_YIELDS_NULL",
                        "CURSOR_CLOSE_ON_COMMIT",
                        "FIPS_FLAGGER",
                        Sequence("IDENTITY_INSERT", Ref("TableReferenceSegment")),
                        "LANGUAGE",
                        "OFFSETS",
                        "QUOTED_IDENTIFIER",
                        "ARITHABORT",
                        "ARITHIGNORE",
                        "FMTONLY",
                        "NOCOUNT",
                        "NOEXEC",
                        "NUMERIC_ROUNDABORT",
                        "PARSEONLY",
                        "QUERY_GOVERNOR_COST_LIMIT",
                        "RESULT_SET_CACHING",  # Azure Synapse Analytics specific
                        "ROWCOUNT",
                        "TEXTSIZE",
                        "ANSI_DEFAULTS",
                        "ANSI_NULL_DFLT_OFF",
                        "ANSI_NULL_DFLT_ON",
                        "ANSI_NULLS",
                        "ANSI_PADDING",
                        "ANSI_WARNINGS",
                        "FORCEPLAN",
                        "SHOWPLAN_ALL",
                        "SHOWPLAN_TEXT",
                        "SHOWPLAN_XML",
                        Sequence(
                            "STATISTICS",
                            OneOf(
                                "IO",
                                "PROFILE",
                                "TIME",
                                "XML",
                            ),
                        ),
                        "IMPLICIT_TRANSACTIONS",
                        "REMOTE_PROC_TRANSACTIONS",
                        "XACT_ABORT",
                    ),
                    OneOf(
                        "ON",
                        "OFF",
                        Sequence(
                            Ref("EqualsSegment"),
                            Ref("ExpressionSegment"),
                        ),
                        # The below for https://learn.microsoft.com/en-us/sql/t-sql/statements/set-deadlock-priority-transact-sql?view=sql-server-ver16 # noqa
                        "LOW",
                        "NORMAL",
                        "HIGH",
                        Ref("ParameterNameSegment"),
                        Ref("NumericLiteralSegment"),
                        Ref("QualifiedNumericLiteralSegment"),
                    ),
                ),
                Sequence(
                    Ref("ParameterNameSegment"),
                    Ref("AssignmentOperatorSegment"),
                    OneOf(
                        Ref("ExpressionSegment"),
                        Ref("SelectableGrammar"),
                    ),
                ),
            ),
        ),
        Dedent,
        Ref("DelimiterGrammar", optional=True),
    )


class AssignmentOperatorSegment(BaseSegment):
    """One of the assignment operators.

    Includes simpler equals but also +=, -=, etc.
    """

    type = "assignment_operator"
    match_grammar = OneOf(
        Ref("RawEqualsSegment"),
        Sequence(
            OneOf(
                Ref("PlusSegment"),
                Ref("MinusSegment"),
                Ref("DivideSegment"),
                Ref("MultiplySegment"),
                Ref("ModuloSegment"),
                Ref("BitwiseAndSegment"),
                Ref("BitwiseOrSegment"),
                Ref("BitwiseXorSegment"),
            ),
            Ref("RawEqualsSegment"),
            allow_gaps=False,
        ),
    )


class ProcedureParameterListGrammar(BaseSegment):
    """The parameters for a procedure ie.

    `@city_name NVARCHAR(30), @postal_code NVARCHAR(15)`.
    """

    type = "procedure_parameter_list"
    # Function parameter list
    match_grammar = OptionallyBracketed(
        Delimited(
            Sequence(
                Ref("ProcedureParameterGrammar"),
                OneOf("OUT", "OUTPUT", optional=True),
                Sequence("READONLY", optional=True),
            ),
            optional=True,
        ),
    )


class CreateProcedureStatementSegment(BaseSegment):
    """A `CREATE OR ALTER PROCEDURE` statement.

    https://docs.microsoft.com/en-us/sql/t-sql/statements/create-procedure-transact-sql?view=sql-server-ver15
    https://learn.microsoft.com/en-us/sql/t-sql/statements/alter-procedure-transact-sql?view=sql-server-ver15
    """

    type = "create_procedure_statement"

    _procedure_option = Sequence(
        "WITH",
        Delimited(
            AnySetOf(
                "ENCRYPTION",
                "RECOMPILE",
                "NATIVE_COMPILATION",  # natively compiled stored procedure
                "SCHEMABINDING",  # natively compiled stored procedure
                Ref("ExecuteAsClauseSegment", optional=True),
            ),
        ),
        optional=True,
    )

    match_grammar = Sequence(
        OneOf("CREATE", "ALTER", Sequence("CREATE", "OR", "ALTER")),
        OneOf("PROC", "PROCEDURE"),
        Ref("ObjectReferenceSegment"),
        # Not for natively compiled stored procedures
        Sequence(
            Ref("SemicolonSegment"),
            Ref("NumericLiteralSegment"),
            optional=True,
        ),
        Indent,
        Ref("ProcedureParameterListGrammar", optional=True),
        _procedure_option,
        Sequence("FOR", "REPLICATION", optional=True),
        Dedent,
        "AS",
        Ref("ProcedureDefinitionGrammar"),
    )


class DropProcedureStatementSegment(BaseSegment):
    """A `DROP PROCEDURE` statement.

    https://docs.microsoft.com/en-us/sql/t-sql/statements/drop-procedure-transact-sql?view=sql-server-ver15
    """

    type = "drop_procedure_statement"

    match_grammar = Sequence(
        "DROP",
        OneOf("PROCEDURE", "PROC"),
        Ref("IfExistsGrammar", optional=True),
        Delimited(Ref("ObjectReferenceSegment")),
        Ref("DelimiterGrammar", optional=True),
    )


class ProcedureDefinitionGrammar(BaseSegment):
    """This is the body of a `CREATE OR ALTER PROCEDURE AS` statement.

    This also handles the body of a `CREATE FUNCTION AS` statement.
    """

    type = "procedure_statement"
    name = "procedure_statement"

    match_grammar = OneOf(
        Ref("OneOrMoreStatementsGrammar"),
        Ref("AtomicBeginEndSegment"),
        Sequence(
            "EXTERNAL",
            "NAME",
            Ref("ObjectReferenceSegment"),
        ),
    )


class CreateViewStatementSegment(BaseSegment):
    """A `CREATE VIEW` statement.

    Adjusted to allow CREATE OR ALTER instead of CREATE OR REPLACE.
    https://docs.microsoft.com/en-us/sql/t-sql/statements/create-view-transact-sql?view=sql-server-ver15#examples
    https://learn.microsoft.com/en-us/sql/t-sql/statements/alter-view-transact-sql?view=sql-server-ver15#examples
    """

    type = "create_view_statement"
    match_grammar = Sequence(
        OneOf("CREATE", "ALTER", Sequence("CREATE", "OR", "ALTER")),
        "VIEW",
        Ref("ObjectReferenceSegment"),
        Bracketed(
            Delimited(
                Ref("IndexColumnDefinitionSegment"),
            ),
            optional=True,
        ),
        Sequence(
            "WITH",
            Delimited("ENCRYPTION", "SCHEMABINDING", "VIEW_METADATA"),
            optional=True,
        ),
        "AS",
        OptionallyBracketed(Ref("SelectableGrammar")),
        Sequence("WITH", "CHECK", "OPTION", optional=True),
        Ref("DelimiterGrammar", optional=True),
    )


class MLTableExpressionSegment(BaseSegment):
    """An ML table expression.

    Not present in T-SQL.
    TODO: Consider whether this segment can be used to represent a PREDICT statement.
    """

    type = "ml_table_expression"
    match_grammar = Nothing()


class ConvertFunctionNameSegment(BaseSegment):
    """CONVERT function name segment.

    Need to be able to specify this as type function_name
    so that linting rules identify it properly
    """

    type = "function_name"
    match_grammar = OneOf("CONVERT", "TRY_CONVERT")


class CastFunctionNameSegment(BaseSegment):
    """CAST function name segment.

    Need to be able to specify this as type function_name
    so that linting rules identify it properly
    """

    type = "function_name"
    match_grammar = Sequence("CAST")


class RankFunctionNameSegment(BaseSegment):
    """Rank function name segment.

    Need to be able to specify this as type function_name
    so that linting rules identify it properly
    """

    type = "function_name"
    match_grammar = OneOf("DENSE_RANK", "NTILE", "RANK", "ROW_NUMBER")


class ReservedKeywordFunctionNameSegment(BaseSegment):
    """Reserved keywords that are also functions.

    Need to be able to specify this as type function_name
    so that linting rules identify it properly
    """

    type = "function_name"
    match_grammar = OneOf(
        "COALESCE",
        "LEFT",
        "NULLIF",
        "RIGHT",
    )


class ReservedKeywordBareFunctionNameSegment(BaseSegment):
    """Reserved keywords that are functions without parentheses.

    Need to be able to specify this as type function_name
    so that linting rules identify it properly
    """

    type = "function_name"
    match_grammar = OneOf(
        "CURRENT_TIMESTAMP",
        "CURRENT_USER",
        "SESSION_USER",
        "SYSTEM_USER",
    )


class WithinGroupFunctionNameSegment(BaseSegment):
    """WITHIN GROUP function name segment.

    For aggregation functions that use the WITHIN GROUP clause.
    https://docs.microsoft.com/en-us/sql/t-sql/functions/string-agg-transact-sql?view=sql-server-ver15
    https://docs.microsoft.com/en-us/sql/t-sql/functions/percentile-cont-transact-sql?view=sql-server-ver15
    https://docs.microsoft.com/en-us/sql/t-sql/functions/percentile-disc-transact-sql?view=sql-server-ver15

    Need to be able to specify this as type function_name
    so that linting rules identify it properly
    """

    type = "function_name"
    match_grammar = OneOf(
        "STRING_AGG",
        "PERCENTILE_CONT",
        "PERCENTILE_DISC",
    )


class WithinGroupClause(BaseSegment):
    """WITHIN GROUP clause.

    For a small set of aggregation functions.
    https://docs.microsoft.com/en-us/sql/t-sql/functions/string-agg-transact-sql?view=sql-server-ver15
    https://docs.microsoft.com/en-us/sql/t-sql/functions/percentile-cont-transact-sql?view=sql-server-ver15
    """

    type = "within_group_clause"
    match_grammar = Sequence(
        "WITHIN",
        "GROUP",
        Bracketed(
            Ref("OrderByClauseSegment"),
        ),
        Sequence(
            "OVER",
            Bracketed(Ref("PartitionClauseSegment")),
            optional=True,
        ),
    )


class PartitionClauseSegment(ansi.PartitionClauseSegment):
    """PARTITION BY clause.

    https://docs.microsoft.com/en-us/sql/t-sql/queries/select-over-clause-transact-sql?view=sql-server-ver15#partition-by
    """

    type = "partitionby_clause"
    match_grammar = Sequence(
        "PARTITION",
        "BY",
        Delimited(
            OptionallyBracketed(
                OneOf(
                    Ref("ColumnReferenceSegment"),
                    Ref("ExpressionSegment"),
                )
            )
        ),
    )


class OnPartitionsSegment(BaseSegment):
    """ON PARTITIONS clause.

    https://docs.microsoft.com/en-us/sql/t-sql/statements/create-index-transact-sql?view=sql-server-ver15
    """

    type = "on_partitions_clause"
    match_grammar = Sequence(
        "ON",
        "PARTITIONS",
        Bracketed(
            Delimited(
                OneOf(
                    Ref("NumericLiteralSegment"),
                    Sequence(
                        Ref("NumericLiteralSegment"), "TO", Ref("NumericLiteralSegment")
                    ),
                )
            )
        ),
    )


class PartitionSchemeNameSegment(BaseSegment):
    """Partition Scheme Name."""

    type = "partition_scheme_name"
    match_grammar = Ref("SingleIdentifierGrammar")


class PartitionSchemeClause(BaseSegment):
    """Partition Scheme Clause segment.

    https://docs.microsoft.com/en-us/sql/t-sql/statements/create-index-transact-sql?view=sql-server-ver15
    """

    type = "partition_scheme_clause"
    match_grammar = Sequence(
        "ON",
        Ref("PartitionSchemeNameSegment"),
        Bracketed(Ref("ColumnReferenceSegment")),
    )


class FunctionSegment(BaseSegment):
    """A scalar or aggregate function.

    Maybe in the future we should distinguish between
    aggregate functions and other functions. For now
    we treat them the same because they look the same
    for our purposes.
    """

    type = "function"
    match_grammar = OneOf(
        Ref("ReservedKeywordBareFunctionNameSegment"),
        Sequence(
            # Treat functions which take date parts separately
            # So those functions parse date parts as DatetimeUnitSegment
            # rather than identifiers.
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
        Sequence(
            Ref("RankFunctionNameSegment"),
            Bracketed(
                Ref("NumericLiteralSegment", optional=True),
            ),
            "OVER",
            Bracketed(
                Ref("PartitionClauseSegment", optional=True),
                Ref("OrderByClauseSegment"),
            ),
        ),
        Sequence(
            # https://docs.microsoft.com/en-us/sql/t-sql/functions/cast-and-convert-transact-sql?view=sql-server-ver15
            Ref("ConvertFunctionNameSegment"),
            Bracketed(
                Ref("DatatypeSegment"),
                Bracketed(Ref("NumericLiteralSegment"), optional=True),
                Ref("CommaSegment"),
                Ref("ExpressionSegment"),
                Sequence(
                    Ref("CommaSegment"), Ref("NumericLiteralSegment"), optional=True
                ),
            ),
        ),
        Sequence(
            # https://docs.microsoft.com/en-us/sql/t-sql/functions/cast-and-convert-transact-sql?view=sql-server-ver15
            Ref("CastFunctionNameSegment"),
            Bracketed(
                Ref("ExpressionSegment"),
                "AS",
                Ref("DatatypeSegment"),
            ),
        ),
        Sequence(
            Ref("WithinGroupFunctionNameSegment"),
            Bracketed(
                Delimited(
                    Ref(
                        "FunctionContentsGrammar",
                        # The brackets might be empty for some functions...
                        optional=True,
                    ),
                ),
                parse_mode=ParseMode.GREEDY,
            ),
            Ref("WithinGroupClause", optional=True),
        ),
        Sequence(
            OneOf(
                Ref(
                    "FunctionNameSegment",
                    exclude=OneOf(
                        Ref("ValuesClauseSegment"),
                        # List of special functions handled differently
                        Ref("CastFunctionNameSegment"),
                        Ref("ConvertFunctionNameSegment"),
                        Ref("DatePartFunctionNameSegment"),
                        Ref("WithinGroupFunctionNameSegment"),
                        Ref("RankFunctionNameSegment"),
                    ),
                ),
                Ref("ReservedKeywordFunctionNameSegment"),
            ),
            Bracketed(
                Ref(
                    "FunctionContentsGrammar",
                    # The brackets might be empty for some functions...
                    optional=True,
                ),
                parse_mode=ParseMode.GREEDY,
            ),
            Ref("PostFunctionGrammar", optional=True),
        ),
    )


class CreateTableStatementSegment(BaseSegment):
    """A `CREATE TABLE` statement."""

    type = "create_table_statement"
    # https://docs.microsoft.com/en-us/sql/t-sql/statements/create-table-transact-sql?view=sql-server-ver15
    # https://docs.microsoft.com/en-us/sql/t-sql/statements/create-table-azure-sql-data-warehouse?view=aps-pdw-2016-au7
    match_grammar = Sequence(
        "CREATE",
        "TABLE",
        Ref("TableReferenceSegment"),
        OneOf(
            # Columns and comment syntax:
            Sequence(
                Bracketed(
                    Delimited(
                        OneOf(
                            Ref("TableConstraintSegment"),
                            Ref("ColumnDefinitionSegment"),
                            Ref("TableIndexSegment"),
                            Ref("PeriodSegment"),
                        ),
                        allow_trailing=True,
                    )
                ),
            ),
            # Create AS syntax:
            Sequence(
                "AS",
                OptionallyBracketed(Ref("SelectableGrammar")),
            ),
            # Create like syntax
            Sequence("LIKE", Ref("TableReferenceSegment")),
        ),
        Ref(
            "TableDistributionIndexClause", optional=True
        ),  # Azure Synapse Analytics specific
        Ref("OnPartitionOrFilegroupOptionSegment", optional=True),
        Ref("FilestreamOnOptionSegment", optional=True),
        Ref("TextimageOnOptionSegment", optional=True),
        Ref("TableOptionSegment", optional=True),
        Ref("DelimiterGrammar", optional=True),
    )


class AlterTableStatementSegment(BaseSegment):
    """An `ALTER TABLE` statement.

    https://docs.microsoft.com/en-us/sql/t-sql/statements/alter-table-transact-sql?view=sql-server-ver15
    Overriding ANSI to remove TSQL non-keywords MODIFY, FIRST
    TODO: Flesh out TSQL-specific functionality
    """

    type = "alter_table_statement"
    match_grammar = Sequence(
        "ALTER",
        "TABLE",
        Ref("TableReferenceSegment"),
        Delimited(
            OneOf(
                # Table options
                Sequence(
                    Ref("ParameterNameSegment"),
                    Ref("EqualsSegment", optional=True),
                    OneOf(Ref("LiteralGrammar"), Ref("NakedIdentifierSegment")),
                ),
                Sequence(
                    "ALTER",
                    "COLUMN",
                    Ref("ColumnDefinitionSegment"),
                ),
                Sequence(
                    "ADD",
                    Delimited(
                        Ref("ColumnDefinitionSegment"),
                    ),
                ),
                Sequence(
                    "DROP",
                    "COLUMN",
                    Ref("IfExistsGrammar", optional=True),
                    Ref("ColumnReferenceSegment"),
                ),
                Sequence(
                    "ADD",
                    Ref("ColumnConstraintSegment"),
                    "FOR",
                    Ref("ColumnReferenceSegment"),
                ),
                Sequence(
                    Sequence(
                        "WITH",
                        "CHECK",
                        optional=True,
                    ),
                    "ADD",
                    Ref("TableConstraintSegment"),
                ),
                Sequence(
                    OneOf(
                        "CHECK",
                        "DROP",
                    ),
                    "CONSTRAINT",
                    Ref("ObjectReferenceSegment"),
                ),
                # Rename
                Sequence(
                    "RENAME",
                    OneOf("AS", "TO", optional=True),
                    Ref("TableReferenceSegment"),
                ),
                Sequence(
                    "SET",
                    OneOf(
                        Bracketed(
                            Sequence(
                                "FILESTREAM_ON",
                                Ref("EqualsSegment"),
                                OneOf(
                                    Ref("FilegroupNameSegment"),
                                    Ref("PartitionSchemeNameSegment"),
                                    OneOf(
                                        "NULL",
                                        Ref("LiteralGrammar"),  # for "default" value
                                    ),
                                ),
                            )
                        ),
                        Bracketed(
                            Sequence(
                                "SYSTEM_VERSIONING",
                                Ref("EqualsSegment"),
                                OneOf("ON", "OFF"),
                                Sequence(
                                    Bracketed(
                                        "HISTORY_TABLE",
                                        Ref("EqualsSegment"),
                                        Ref("TableReferenceSegment"),
                                        Sequence(
                                            Ref("CommaSegment"),
                                            "DATA_CONSISTENCY_CHECK",
                                            Ref("EqualsSegment"),
                                            OneOf("ON", "OFF"),
                                            optional=True,
                                        ),
                                        Sequence(
                                            Ref("CommaSegment"),
                                            "HISTORY_RETENTION_PERIOD",
                                            Ref("EqualsSegment"),
                                            Ref("NumericLiteralSegment", optional=True),
                                            Ref("DatetimeUnitSegment"),
                                            optional=True,
                                        ),
                                    ),
                                    optional=True,
                                ),
                            )
                        ),
                        Bracketed(
                            Sequence(
                                "DATA_DELETION",
                                Ref("EqualsSegment"),
                                OneOf("ON", "OFF"),
                                Sequence(
                                    Bracketed(
                                        "FILTER_COLUMN",
                                        Ref("EqualsSegment"),
                                        Ref("ColumnReferenceSegment"),
                                        Sequence(
                                            Ref("CommaSegment"),
                                            "RETENTION_PERIOD",
                                            Ref("EqualsSegment"),
                                            Ref("NumericLiteralSegment", optional=True),
                                            Ref("DatetimeUnitSegment"),
                                            optional=True,
                                        ),
                                    ),
                                    optional=True,
                                ),
                            ),
                        ),
                    ),
                ),
            )
        ),
    )


class TableConstraintSegment(BaseSegment):
    """A table constraint, e.g. for CREATE TABLE."""

    # https://docs.microsoft.com/en-us/sql/t-sql/statements/create-table-transact-sql?view=sql-server-ver15

    type = "table_constraint"
    match_grammar = Sequence(
        Sequence(  # [ CONSTRAINT <Constraint name> ]
            "CONSTRAINT", Ref("ObjectReferenceSegment"), optional=True
        ),
        OneOf(
            Sequence(
                Ref("PrimaryKeyGrammar"),
                Ref("BracketedIndexColumnListGrammar"),
                Ref("RelationalIndexOptionsSegment", optional=True),
                Ref("OnPartitionOrFilegroupOptionSegment", optional=True),
            ),
            Sequence(  # FOREIGN KEY ( column_name [, ... ] )
                # REFERENCES reftable [ ( refcolumn [, ... ] ) ]
                Ref("ForeignKeyGrammar"),
                # Local columns making up FOREIGN KEY constraint
                Ref("BracketedColumnReferenceListGrammar"),
                # REFERENCES reftable [ ( refcolumn) ] + ON DELETE/ON UPDATE
                Ref("ReferencesConstraintGrammar"),
            ),
            Ref("CheckConstraintGrammar", optional=True),
        ),
    )


class TableIndexSegment(BaseSegment):
    """A table index, e.g. for CREATE TABLE."""

    # https://docs.microsoft.com/en-us/sql/t-sql/statements/create-table-transact-sql?view=sql-server-ver15

    type = "table_index_segment"
    match_grammar = Sequence(
        Sequence("INDEX", Ref("ObjectReferenceSegment"), optional=True),
        OneOf(
            Sequence(
                Sequence("UNIQUE", optional=True),
                OneOf("CLUSTERED", "NONCLUSTERED", optional=True),
                Ref("BracketedIndexColumnListGrammar"),
            ),
            Sequence("CLUSTERED", "COLUMNSTORE"),
            Sequence(
                Sequence("NONCLUSTERED", optional=True),
                "COLUMNSTORE",
                Ref("BracketedColumnReferenceListGrammar"),
            ),
        ),
        Ref("RelationalIndexOptionsSegment", optional=True),
        Ref("OnPartitionOrFilegroupOptionSegment", optional=True),
        Ref("FilestreamOnOptionSegment", optional=True),
    )


class BracketedIndexColumnListGrammar(BaseSegment):
    """list of columns used for CREATE INDEX, constraints."""

    type = "bracketed_index_column_list_grammar"
    match_grammar = Sequence(
        Bracketed(
            Delimited(
                Ref("IndexColumnDefinitionSegment"),
            )
        )
    )


class FilegroupNameSegment(BaseSegment):
    """Filegroup Name Segment."""

    type = "filegroup_name"
    match_grammar = Ref("SingleIdentifierGrammar")


class FilegroupClause(BaseSegment):
    """Filegroup Clause segment.

    https://docs.microsoft.com/en-us/sql/relational-databases/databases/database-files-and-filegroups?view=sql-server-ver15
    """

    type = "filegroup_clause"
    match_grammar = Sequence(
        "ON",
        Ref("FilegroupNameSegment"),
    )


class IdentityGrammar(BaseSegment):
    """`IDENTITY (1,1)` in table schemas.

    https://docs.microsoft.com/en-us/sql/t-sql/statements/create-table-transact-sql-identity-property?view=sql-server-ver15
    """

    type = "identity_grammar"
    match_grammar = Sequence(
        "IDENTITY",
        # optional (seed, increment) e.g. (1, 1)
        Bracketed(
            Sequence(
                Ref("NumericLiteralSegment"),
                Ref("CommaSegment"),
                Ref("NumericLiteralSegment"),
            ),
            optional=True,
        ),
    )


class EncryptedWithGrammar(BaseSegment):
    """ENCRYPTED WITH in table schemas.

    https://docs.microsoft.com/en-us/sql/t-sql/statements/create-table-transact-sql-identity-property?view=sql-server-ver15
    """

    type = "encrypted_with_grammar"
    match_grammar = Sequence(
        "ENCRYPTED",
        "WITH",
        Bracketed(
            Delimited(
                Sequence(
                    "COLUMN_ENCRYPTION_KEY",
                    Ref("EqualsSegment"),
                    Ref("SingleIdentifierGrammar"),
                ),
                Sequence(
                    "ENCRYPTION_TYPE",
                    Ref("EqualsSegment"),
                    OneOf("DETERMINISTIC", "RANDOMIZED"),
                ),
                Sequence(
                    "ALGORITHM",
                    Ref("EqualsSegment"),
                    Ref("QuotedLiteralSegment"),
                ),
            )
        ),
    )


class TableDistributionIndexClause(BaseSegment):
    """`CREATE TABLE` distribution / index clause.

    This is specific to Azure Synapse Analytics.
    """

    type = "table_distribution_index_clause"

    match_grammar = Sequence(
        "WITH",
        Bracketed(
            Delimited(
                Ref("TableDistributionClause"),
                Ref("TableIndexClause"),
                Ref("TableLocationClause"),
            ),
        ),
    )


class TableDistributionClause(BaseSegment):
    """`CREATE TABLE` distribution clause.

    This is specific to Azure Synapse Analytics.
    """

    type = "table_distribution_clause"

    match_grammar = Sequence(
        "DISTRIBUTION",
        Ref("EqualsSegment"),
        OneOf(
            "REPLICATE",
            "ROUND_ROBIN",
            Sequence(
                "HASH",
                Bracketed(Ref("ColumnReferenceSegment")),
            ),
        ),
    )


class TableIndexClause(BaseSegment):
    """`CREATE TABLE` table index clause.

    This is specific to Azure Synapse Analytics.
    https://docs.microsoft.com/en-us/sql/t-sql/statements/create-table-azure-sql-data-warehouse?view=aps-pdw-2016-au7#TableOptions
    """

    type = "table_index_clause"

    match_grammar = Sequence(
        OneOf(
            "HEAP",
            Sequence(
                "CLUSTERED",
                "COLUMNSTORE",
                "INDEX",
                Sequence(
                    "ORDER",
                    Bracketed(
                        Delimited(
                            Ref("ColumnReferenceSegment"),
                        ),
                    ),
                    optional=True,
                ),
            ),
            Sequence(
                "CLUSTERED",
                "INDEX",
                Bracketed(
                    Delimited(
                        Sequence(
                            Ref("ColumnReferenceSegment"),
                            OneOf(
                                "ASC",
                                "DESC",
                                optional=True,
                            ),
                        ),
                    ),
                ),
            ),
        ),
    )


class TableLocationClause(BaseSegment):
    """`CREATE TABLE` location clause.

    This is specific to Azure Synapse Analytics (deprecated) or to an external table.
    """

    type = "table_location_clause"

    match_grammar = Sequence(
        "LOCATION",
        Ref("EqualsSegment"),
        OneOf(
            "USER_DB",  # Azure Synapse Analytics specific
            Ref("QuotedLiteralSegmentOptWithN"),  # External Table
        ),
    )


class AlterTableSwitchStatementSegment(BaseSegment):
    """An `ALTER TABLE SWITCH` statement."""

    type = "alter_table_switch_statement"
    # https://docs.microsoft.com/en-us/sql/t-sql/statements/alter-table-transact-sql?view=sql-server-ver15
    # T-SQL's ALTER TABLE SWITCH grammar is different enough to core ALTER TABLE grammar
    # to merit its own definition
    match_grammar = Sequence(
        "ALTER",
        "TABLE",
        Ref("ObjectReferenceSegment"),
        "SWITCH",
        Sequence("PARTITION", Ref("NumericLiteralSegment"), optional=True),
        "TO",
        Ref("ObjectReferenceSegment"),
        Sequence(  # Azure Synapse Analytics specific
            "WITH",
            Bracketed("TRUNCATE_TARGET", Ref("EqualsSegment"), OneOf("ON", "OFF")),
            optional=True,
        ),
        Ref("DelimiterGrammar", optional=True),
    )


class CreateTableAsSelectStatementSegment(BaseSegment):
    """A `CREATE TABLE AS SELECT` statement.

    This is specific to Azure Synapse Analytics.
    """

    type = "create_table_as_select_statement"
    # https://docs.microsoft.com/en-us/sql/t-sql/statements/create-table-as-select-azure-sql-data-warehouse?toc=/azure/synapse-analytics/sql-data-warehouse/toc.json&bc=/azure/synapse-analytics/sql-data-warehouse/breadcrumb/toc.json&view=azure-sqldw-latest&preserve-view=true
    match_grammar = Sequence(
        "CREATE",
        "TABLE",
        Ref("TableReferenceSegment"),
        Ref("TableDistributionIndexClause"),
        "AS",
        OptionallyBracketed(Ref("SelectableGrammar")),
        Ref("OptionClauseSegment", optional=True),
        Ref("DelimiterGrammar", optional=True),
    )


class TransactionStatementSegment(BaseSegment):
    """A `COMMIT`, `ROLLBACK` or `TRANSACTION` statement."""

    type = "transaction_statement"
    match_grammar = OneOf(
        # [ BEGIN | SAVE ] [ TRANSACTION | TRAN ] [ <Name> | <Variable> ]
        # COMMIT [ TRANSACTION | TRAN | WORK ]
        # ROLLBACK [ TRANSACTION | TRAN | WORK ] [ <Name> | <Variable> ]
        # https://docs.microsoft.com/en-us/sql/t-sql/language-elements/begin-transaction-transact-sql?view=sql-server-ver15
        Sequence(
            "BEGIN",
            Sequence("DISTRIBUTED", optional=True),
            Ref("TransactionGrammar"),
            Ref("SingleIdentifierGrammar", optional=True),
            Sequence("WITH", "MARK", Ref("QuotedIdentifierSegment"), optional=True),
            Ref("DelimiterGrammar", optional=True),
        ),
        Sequence(
            OneOf("COMMIT", "ROLLBACK"),
            Ref("TransactionGrammar", optional=True),
            OneOf(
                Ref("SingleIdentifierGrammar"),
                Ref("VariableIdentifierSegment"),
                optional=True,
            ),
            Ref("DelimiterGrammar", optional=True),
        ),
        Sequence(
            OneOf("COMMIT", "ROLLBACK"),
            Sequence("WORK", optional=True),
            Ref("DelimiterGrammar", optional=True),
        ),
        Sequence(
            "SAVE",
            Ref("TransactionGrammar"),
            OneOf(
                Ref("SingleIdentifierGrammar"),
                Ref("VariableIdentifierSegment"),
                optional=True,
            ),
            Ref("DelimiterGrammar", optional=True),
        ),
    )


class BeginEndSegment(BaseSegment):
    """A `BEGIN/END` block.

    Encloses multiple statements into a single statement object.
    https://docs.microsoft.com/en-us/sql/t-sql/language-elements/begin-end-transact-sql?view=sql-server-ver15
    """

    type = "begin_end_block"
    match_grammar = Sequence(
        "BEGIN",
        Ref("DelimiterGrammar", optional=True),
        Indent,
        Ref("OneOrMoreStatementsGrammar"),
        Dedent,
        "END",
    )


class AtomicBeginEndSegment(BaseSegment):
    """A special `BEGIN/END` block with atomic options.

    This is only dedicated to natively compiled stored procedures.

    Encloses multiple statements into a single statement object.
    https://docs.microsoft.com/en-us/sql/t-sql/language-elements/begin-end-transact-sql?view=sql-server-ver15
    https://learn.microsoft.com/en-us/sql/t-sql/statements/create-procedure-transact-sql?view=sql-server-ver16#syntax
    """

    type = "atomic_begin_end_block"
    match_grammar = Sequence(
        "BEGIN",
        Sequence(
            "ATOMIC",
            "WITH",
            Bracketed(
                Delimited(
                    Sequence(
                        "LANGUAGE",
                        Ref("EqualsSegment"),
                        Ref("QuotedLiteralSegmentOptWithN"),
                    ),
                    Sequence(
                        "TRANSACTION",
                        "ISOLATION",
                        "LEVEL",
                        Ref("EqualsSegment"),
                        OneOf(
                            "SNAPSHOT",
                            Sequence("REPEATABLE", "READ"),
                            "SERIALIZABLE",
                        ),
                    ),
                    Sequence(
                        "DATEFIRST",
                        Ref("EqualsSegment"),
                        Ref("NumericLiteralSegment"),
                        optional=True,
                    ),
                    Sequence(
                        "DATEFORMAT",
                        Ref("EqualsSegment"),
                        Ref("DateFormatSegment"),
                        optional=True,
                    ),
                    Sequence(
                        "DELAYED_DURABILITY",
                        Ref("EqualsSegment"),
                        OneOf("ON", "OFF"),
                        optional=True,
                    ),
                ),
            ),
        ),
        Ref("DelimiterGrammar", optional=True),
        Indent,
        Ref("OneOrMoreStatementsGrammar"),
        Dedent,
        Sequence("END", optional=True),
    )


class TryCatchSegment(BaseSegment):
    """A `TRY/CATCH` block pair.

    https://docs.microsoft.com/en-us/sql/t-sql/language-elements/try-catch-transact-sql?view=sql-server-ver15
    """

    type = "try_catch"
    match_grammar = Sequence(
        "BEGIN",
        "TRY",
        Ref("DelimiterGrammar", optional=True),
        Indent,
        Ref("OneOrMoreStatementsGrammar"),
        Dedent,
        "END",
        "TRY",
        "BEGIN",
        "CATCH",
        Ref("DelimiterGrammar", optional=True),
        Indent,
        Ref("OneOrMoreStatementsGrammar"),
        Dedent,
        "END",
        "CATCH",
    )


class BatchSegment(BaseSegment):
    """A segment representing a GO batch within a file or script."""

    type = "batch"
    match_grammar = OneOf(
        # Things that can be bundled
        Ref("OneOrMoreStatementsGrammar"),
        # Things that can't be bundled
        Ref("CreateProcedureStatementSegment"),
    )


class FileSegment(BaseFileSegment):
    """A segment representing a whole file or script.

    We override default as T-SQL allows concept of several
    batches of commands separated by GO as well as usual
    semicolon-separated statement lines.

    This is also the default "root" segment of the dialect,
    and so is usually instantiated directly. It therefore
    has no match_grammar.
    """

    match_grammar = Sequence(
        AnyNumberOf(Ref("BatchDelimiterGrammar")),
        Delimited(
            Ref("BatchSegment"),
            delimiter=AnyNumberOf(
                Sequence(
                    Ref("DelimiterGrammar", optional=True), Ref("BatchDelimiterGrammar")
                ),
                min_times=1,
            ),
            allow_gaps=True,
            allow_trailing=True,
        ),
    )


class OpenRowSetSegment(BaseSegment):
    """A `OPENROWSET` segment.

    https://docs.microsoft.com/en-us/sql/t-sql/functions/openrowset-transact-sql?view=sql-server-ver15
    """

    type = "openrowset_segment"
    match_grammar = Sequence(
        "OPENROWSET",
        Bracketed(
            OneOf(
                Sequence(
                    Ref("QuotedLiteralSegment"),
                    Ref("CommaSegment"),
                    OneOf(
                        Sequence(
                            Ref("QuotedLiteralSegment"),
                            Ref("DelimiterGrammar"),
                            Ref("QuotedLiteralSegment"),
                            Ref("DelimiterGrammar"),
                            Ref("QuotedLiteralSegment"),
                        ),
                        Ref("QuotedLiteralSegment"),
                    ),
                    Ref("CommaSegment"),
                    OneOf(
                        Ref("TableReferenceSegment"),
                        Ref("QuotedLiteralSegment"),
                    ),
                ),
                Sequence(
                    "BULK",
                    Ref("QuotedLiteralSegmentOptWithN"),
                    Ref("CommaSegment"),
                    OneOf(
                        Sequence(
                            "FORMATFILE",
                            Ref("EqualsSegment"),
                            Ref("QuotedLiteralSegmentOptWithN"),
                            Ref("CommaSegment"),
                            Delimited(
                                AnyNumberOf(
                                    Sequence(
                                        "DATASOURCE",
                                        Ref("EqualsSegment"),
                                        Ref("QuotedLiteralSegmentOptWithN"),
                                    ),
                                    Sequence(
                                        "ERRORFILE",
                                        Ref("EqualsSegment"),
                                        Ref("QuotedLiteralSegmentOptWithN"),
                                    ),
                                    Sequence(
                                        "ERRORFILE_DATA_SOURCE",
                                        Ref("EqualsSegment"),
                                        Ref("QuotedLiteralSegmentOptWithN"),
                                    ),
                                    Sequence(
                                        "MAXERRORS",
                                        Ref("EqualsSegment"),
                                        Ref("NumericLiteralSegment"),
                                    ),
                                    Sequence(
                                        "FIRSTROW",
                                        Ref("EqualsSegment"),
                                        Ref("NumericLiteralSegment"),
                                    ),
                                    Sequence(
                                        "LASTROW",
                                        Ref("EqualsSegment"),
                                        Ref("NumericLiteralSegment"),
                                    ),
                                    Sequence(
                                        "CODEPAGE",
                                        Ref("EqualsSegment"),
                                        Ref("QuotedLiteralSegment"),
                                    ),
                                    Sequence(
                                        "FORMAT",
                                        Ref("EqualsSegment"),
                                        Ref("QuotedLiteralSegment"),
                                    ),
                                    Sequence(
                                        "FIELDQUOTE",
                                        Ref("EqualsSegment"),
                                        Ref("QuotedLiteralSegmentOptWithN"),
                                    ),
                                    Sequence(
                                        "FORMATFILE",
                                        Ref("EqualsSegment"),
                                        Ref("QuotedLiteralSegmentOptWithN"),
                                    ),
                                    Sequence(
                                        "FORMATFILE_DATA_SOURCE",
                                        Ref("EqualsSegment"),
                                        Ref("QuotedLiteralSegmentOptWithN"),
                                    ),
                                ),
                                optional=True,
                            ),
                        ),
                        "SINGLE_BLOB",
                        "SINGLE_CLOB",
                        "SINGLE_NCLOB",
                    ),
                ),
            ),
        ),
    )


class DeleteStatementSegment(BaseSegment):
    """A `DELETE` statement.

    https://docs.microsoft.com/en-us/sql/t-sql/statements/delete-transact-sql?view=sql-server-ver15
    Overriding ANSI to remove greedy logic which assumes statements have been
    delimited and to allow for Azure Synapse Analytics-specific DELETE statements
    """

    type = "delete_statement"
    # match grammar. This one makes sense in the context of knowing that it's
    # definitely a statement, we just don't know what type yet.
    match_grammar = Sequence(
        "DELETE",
        OneOf(
            Sequence(
                Ref("TopPercentGrammar", optional=True),
                Ref.keyword("FROM", optional=True),
                OneOf(
                    Sequence(
                        Sequence(
                            "OPENDATASOURCE",
                            Bracketed(
                                Ref("QuotedLiteralSegment"),
                                Ref("CommaSegment"),
                                Ref("QuotedLiteralSegment"),
                            ),
                            Ref("DotSegment"),
                            optional=True,
                        ),
                        Ref("TableReferenceSegment"),
                        Ref("PostTableExpressionGrammar", optional=True),
                    ),
                    Sequence(
                        "OPENQUERY",
                        Bracketed(
                            Ref("NakedIdentifierSegment"),
                            Ref("CommaSegment"),
                            Ref("QuotedLiteralSegment"),
                        ),
                    ),
                    Ref("OpenRowSetSegment"),
                ),
                Ref("OutputClauseSegment", optional=True),
                Ref("FromClauseSegment", optional=True),
                OneOf(
                    Ref("WhereClauseSegment"),
                    Sequence(
                        "WHERE",
                        "CURRENT",
                        "OF",
                        Ref("CursorNameGrammar"),
                    ),
                    optional=True,
                ),
            ),
            # Azure Synapse Analytics-specific
            Sequence(
                "FROM",
                Ref("TableReferenceSegment"),
                "JOIN",
                Ref("TableReferenceSegment"),
                Ref("JoinOnConditionSegment"),
                Ref("WhereClauseSegment", optional=True),
            ),
        ),
        Ref("OptionClauseSegment", optional=True),
        Ref("DelimiterGrammar", optional=True),
    )


class FromClauseSegment(BaseSegment):
    """A `FROM` clause like in `SELECT`.

    NOTE: this is a delimited set of table expressions, with a variable
    number of optional join clauses with those table expressions. The
    delmited aspect is the higher of the two such that the following is
    valid (albeit unusual):

    ```
    SELECT *
    FROM a JOIN b, c JOIN d
    ```

    Overriding ANSI to remove Delimited logic which assumes statements have been
    delimited
    """

    type = "from_clause"
    match_grammar = Sequence(
        "FROM",
        Delimited(Ref("FromExpressionSegment")),
        Ref("DelimiterGrammar", optional=True),
    )

    get_eventual_aliases = ansi.FromClauseSegment.get_eventual_aliases


class FromExpressionElementSegment(ansi.FromExpressionElementSegment):
    """FROM Expression Element Segment.

    Overriding ANSI to add Temporal Query.
    """

    match_grammar = (
        ansi.FromExpressionElementSegment._base_from_expression_element.copy(
            insert=[
                Ref("TemporalQuerySegment", optional=True),
            ],
            before=Ref(
                "AliasExpressionSegment",
                exclude=OneOf(
                    Ref("SamplingExpressionSegment"),
                    Ref("JoinLikeClauseGrammar"),
                ),
                optional=True,
            ),
        )
    )


class TableExpressionSegment(BaseSegment):
    """The main table expression e.g. within a FROM clause.

    In SQL standard, as well as T-SQL, table expressions (`table reference` in SQL
    standard) can also be join tables, optionally bracketed, allowing for nested joins.
    """

    type = "table_expression"
    match_grammar: Matchable = OneOf(
        Ref("ValuesClauseSegment"),
        Ref("BareFunctionSegment"),
        Ref("FunctionSegment"),
        Ref("OpenRowSetSegment"),
        Ref("OpenJsonSegment"),
        Ref("TableReferenceSegment"),
        Ref("StorageLocationSegment"),
        # Nested Selects
        Bracketed(Ref("SelectableGrammar")),
        Bracketed(Ref("MergeStatementSegment")),
        Bracketed(
            Sequence(
                Ref("TableExpressionSegment"),
                # TODO: Revisit this to make sure it's sensible.
                Conditional(Dedent, indented_joins=False),
                Conditional(Indent, indented_joins=True),
                OneOf(Ref("JoinClauseSegment"), Ref("JoinLikeClauseGrammar")),
                Conditional(Dedent, indented_joins=True),
                Conditional(Indent, indented_joins=True),
            )
        ),
    )


class GroupByClauseSegment(BaseSegment):
    """A `GROUP BY` clause like in `SELECT`.

    Overriding ANSI to remove Delimited logic which assumes statements have been
    delimited
    """

    type = "groupby_clause"
    match_grammar = Sequence(
        "GROUP",
        "BY",
        Indent,
        OneOf(
            Ref("ColumnReferenceSegment"),
            # Can `GROUP BY 1`
            Ref("NumericLiteralSegment"),
            # Can `GROUP BY coalesce(col, 1)`
            Ref("ExpressionSegment"),
        ),
        AnyNumberOf(
            Ref("CommaSegment"),
            OneOf(
                Ref("ColumnReferenceSegment"),
                # Can `GROUP BY 1`
                Ref("NumericLiteralSegment"),
                # Can `GROUP BY coalesce(col, 1)`
                Ref("ExpressionSegment"),
            ),
        ),
        Dedent,
    )


class HavingClauseSegment(BaseSegment):
    """A `HAVING` clause like in `SELECT`.

    Overriding ANSI to remove greedy terminator
    """

    type = "having_clause"
    match_grammar = Sequence(
        "HAVING",
        Indent,
        OptionallyBracketed(Ref("ExpressionSegment")),
        Dedent,
    )


class OrderByClauseSegment(BaseSegment):
    """A `ORDER BY` clause like in `SELECT`.

    Overriding ANSI to remove Greedy logic which assumes statements have been
    delimited
    """

    type = "orderby_clause"
    match_grammar = Sequence(
        "ORDER",
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
            ),
        ),
        Dedent,
    )


class RenameStatementSegment(BaseSegment):
    """`RENAME` statement.

    https://docs.microsoft.com/en-us/sql/t-sql/statements/rename-transact-sql?view=aps-pdw-2016-au7
    Azure Synapse Analytics-specific.
    """

    type = "rename_statement"
    match_grammar = Sequence(
        "RENAME",
        "OBJECT",
        Ref("ObjectReferenceSegment"),
        "TO",
        Ref("SingleIdentifierGrammar"),
        Ref("DelimiterGrammar", optional=True),
    )


class DropTableStatementSegment(ansi.DropTableStatementSegment):
    """A `DROP TABLE` statement.

    Overriding ANSI to add optional delimiter.
    """

    match_grammar = ansi.DropTableStatementSegment.match_grammar.copy(
        insert=[
            Ref("DelimiterGrammar", optional=True),
        ],
    )


class DropViewStatementSegment(ansi.DropViewStatementSegment):
    """A `DROP VIEW` statement.

    Overriding ANSI to add optional delimiter.
    """

    match_grammar = ansi.DropViewStatementSegment.match_grammar.copy(
        insert=[
            Ref("DelimiterGrammar", optional=True),
        ],
    )


class DropUserStatementSegment(ansi.DropUserStatementSegment):
    """A `DROP USER` statement.

    Overriding ANSI to add optional delimiter.
    """

    match_grammar = ansi.DropUserStatementSegment.match_grammar.copy(
        insert=[
            Ref("DelimiterGrammar", optional=True),
        ],
    )


class UpdateStatementSegment(BaseSegment):
    """An `Update` statement.

    UPDATE <table name> SET <set clause list> [ WHERE <search condition> ]
    Overriding ANSI in order to allow for PostTableExpressionGrammar (table hints)
    """

    type = "update_statement"
    match_grammar = Sequence(
        "UPDATE",
        OneOf(Ref("TableReferenceSegment"), Ref("AliasedTableReferenceGrammar")),
        Ref("PostTableExpressionGrammar", optional=True),
        Ref("SetClauseListSegment"),
        Ref("OutputClauseSegment", optional=True),
        Ref("FromClauseSegment", optional=True),
        Ref("WhereClauseSegment", optional=True),
        Ref("OptionClauseSegment", optional=True),
        Ref("DelimiterGrammar", optional=True),
    )


class SetClauseListSegment(BaseSegment):
    """set clause list.

    Overriding ANSI to remove Delimited
    """

    type = "set_clause_list"
    match_grammar = Sequence(
        "SET",
        Indent,
        Ref("SetClauseSegment"),
        AnyNumberOf(
            Ref("CommaSegment"),
            Ref("SetClauseSegment"),
        ),
        Dedent,
    )


class SetClauseSegment(BaseSegment):
    """Set clause.

    Overriding ANSI to allow for ExpressionSegment on the right
    """

    type = "set_clause"

    match_grammar = Sequence(
        Ref("ColumnReferenceSegment"),
        Ref("AssignmentOperatorSegment"),
        Ref("ExpressionSegment"),
    )


class PrintStatementSegment(BaseSegment):
    """PRINT statement segment."""

    type = "print_statement"
    match_grammar = Sequence(
        "PRINT",
        Ref("ExpressionSegment"),
        Ref("DelimiterGrammar", optional=True),
    )


class OptionClauseSegment(BaseSegment):
    """Query Hint clause.

    https://docs.microsoft.com/en-us/sql/t-sql/queries/hints-transact-sql-query?view=sql-server-ver15
    """

    type = "option_clause"
    match_grammar = Sequence(
        "OPTION",
        Bracketed(
            Delimited(Ref("QueryHintSegment")),
        ),
    )


class QueryHintSegment(BaseSegment):
    """Query Hint segment.

    https://docs.microsoft.com/en-us/sql/t-sql/queries/hints-transact-sql-query?view=sql-server-ver15
    """

    type = "query_hint_segment"
    match_grammar = OneOf(
        Sequence(  # Azure Synapse Analytics specific
            "LABEL",
            Ref("EqualsSegment"),
            Ref("QuotedLiteralSegmentOptWithN"),
        ),
        Sequence(
            OneOf("HASH", "ORDER"),
            "GROUP",
        ),
        Sequence(OneOf("MERGE", "HASH", "CONCAT"), "UNION"),
        Sequence(OneOf("LOOP", "MERGE", "HASH"), "JOIN"),
        Sequence("EXPAND", "VIEWS"),
        Sequence(
            OneOf(
                "FAST",
                "MAXDOP",
                "MAXRECURSION",
                "QUERYTRACEON",
                Sequence(
                    OneOf(
                        "MAX_GRANT_PERCENT",
                        "MIN_GRANT_PERCENT",
                    ),
                    Ref("EqualsSegment"),
                ),
            ),
            Ref("NumericLiteralSegment"),
        ),
        Sequence("FORCE", "ORDER"),
        Sequence(
            OneOf("FORCE", "DISABLE"),
            OneOf("EXTERNALPUSHDOWN", "SCALEOUTEXECUTION"),
        ),
        Sequence(
            OneOf(
                "KEEP",
                "KEEPFIXED",
                "ROBUST",
            ),
            "PLAN",
        ),
        "IGNORE_NONCLUSTERED_COLUMNSTORE_INDEX",
        "NO_PERFORMANCE_SPOOL",
        Sequence(
            "OPTIMIZE",
            "FOR",
            OneOf(
                "UNKNOWN",
                Bracketed(
                    Ref("ParameterNameSegment"),
                    OneOf(
                        "UNKNOWN", Sequence(Ref("EqualsSegment"), Ref("LiteralGrammar"))
                    ),
                    AnyNumberOf(
                        Ref("CommaSegment"),
                        Ref("ParameterNameSegment"),
                        OneOf(
                            "UNKNOWN",
                            Sequence(Ref("EqualsSegment"), Ref("LiteralGrammar")),
                        ),
                    ),
                ),
            ),
        ),
        Sequence("PARAMETERIZATION", OneOf("SIMPLE", "FORCED")),
        "RECOMPILE",
        Sequence(
            "USE",
            "HINT",
            Bracketed(
                Ref("QuotedLiteralSegment"),
                AnyNumberOf(Ref("CommaSegment"), Ref("QuotedLiteralSegment")),
            ),
        ),
        Sequence(
            "USE",
            "PLAN",
            Ref("QuotedLiteralSegmentOptWithN"),
        ),
        Sequence(
            "TABLE",
            "HINT",
            Ref("ObjectReferenceSegment"),
            Delimited(Ref("TableHintSegment")),
        ),
    )


class PostTableExpressionGrammar(BaseSegment):
    """Table Hint clause.  Overloading the PostTableExpressionGrammar to implement.

    https://docs.microsoft.com/en-us/sql/t-sql/queries/hints-transact-sql-table?view=sql-server-ver15
    """

    type = "post_table_expression"
    match_grammar = Sequence(
        Sequence("WITH", optional=True),
        Bracketed(
            Ref("TableHintSegment"),
            AnyNumberOf(
                Ref("CommaSegment"),
                Ref("TableHintSegment"),
            ),
        ),
    )


class TableHintSegment(BaseSegment):
    """Table Hint segment.

    https://docs.microsoft.com/en-us/sql/t-sql/queries/hints-transact-sql-table?view=sql-server-ver15
    """

    type = "query_hint_segment"
    match_grammar = OneOf(
        "NOEXPAND",
        Sequence(
            "INDEX",
            Bracketed(
                Delimited(
                    OneOf(Ref("IndexReferenceSegment"), Ref("NumericLiteralSegment")),
                ),
            ),
        ),
        Sequence(
            "INDEX",
            Ref("EqualsSegment"),
            Bracketed(
                OneOf(Ref("IndexReferenceSegment"), Ref("NumericLiteralSegment")),
            ),
        ),
        "KEEPIDENTITY",
        "KEEPDEFAULTS",
        Sequence(
            "FORCESEEK",
            Bracketed(
                Ref("IndexReferenceSegment"),
                Bracketed(
                    Ref("SingleIdentifierGrammar"),
                    AnyNumberOf(Ref("CommaSegment"), Ref("SingleIdentifierGrammar")),
                ),
                optional=True,
            ),
        ),
        "FORCESCAN",
        "HOLDLOCK",
        "IGNORE_CONSTRAINTS",
        "IGNORE_TRIGGERS",
        "NOLOCK",
        "NOWAIT",
        "PAGLOCK",
        "READCOMMITTED",
        "READCOMMITTEDLOCK",
        "READPAST",
        "READUNCOMMITTED",
        "REPEATABLEREAD",
        "ROWLOCK",
        "SERIALIZABLE",
        "SNAPSHOT",
        Sequence(
            "SPATIAL_WINDOW_MAX_CELLS",
            Ref("EqualsSegment"),
            Ref("NumericLiteralSegment"),
        ),
        "TABLOCK",
        "TABLOCKX",
        "UPDLOCK",
        "XLOCK",
    )


class SetOperatorSegment(BaseSegment):
    """A set operator such as Union, Except or Intersect.

    Override ANSI to remove TSQL non-keyword MINUS.
    """

    type = "set_operator"
    match_grammar = OneOf(
        Sequence("UNION", OneOf("DISTINCT", "ALL", optional=True)),
        "INTERSECT",
        "EXCEPT",
    )


class SetExpressionSegment(BaseSegment):
    """A set expression with either Union, Minus, Except or Intersect.

    Overriding ANSI to include OPTION clause.
    """

    type = "set_expression"
    # match grammar
    match_grammar = Sequence(
        Ref("NonSetSelectableGrammar"),
        AnyNumberOf(
            Sequence(
                Ref("SetOperatorSegment"),
                Ref("NonSetSelectableGrammar"),
            ),
            min_times=1,
        ),
        Ref("OrderByClauseSegment", optional=True),
        Ref("OptionClauseSegment", optional=True),
        Ref("DelimiterGrammar", optional=True),
    )


class ForClauseSegment(BaseSegment):
    """A For Clause segment for TSQL.

    This is used to format results into XML or JSON
    """

    type = "for_clause"

    _common_directives_for_xml = Sequence(
        Sequence(
            "BINARY",
            "BASE64",
        ),
        "TYPE",
        Sequence(
            "ROOT",
            Bracketed(
                Ref("LiteralGrammar"),
                optional=True,
            ),
        ),
        optional=True,
    )

    _elements = Sequence("ELEMENTS", OneOf("XSINIL", "ABSENT", optional=True))

    match_grammar = Sequence(
        "FOR",
        OneOf(
            "BROWSE",
            Sequence(
                "JSON",
                Delimited(
                    OneOf(
                        "AUTO",
                        "PATH",
                    ),
                    Sequence(
                        "ROOT",
                        Bracketed(
                            Ref("LiteralGrammar"),
                            optional=True,
                        ),
                        optional=True,
                    ),
                    Ref.keyword("INCLUDE_NULL_VALUES", optional=True),
                    Ref.keyword("WITHOUT_ARRAY_WRAPPER", optional=True),
                ),
            ),
            Sequence(
                "XML",
                OneOf(
                    Delimited(
                        Sequence(
                            "PATH",
                            Bracketed(
                                Ref("LiteralGrammar"),
                                optional=True,
                            ),
                        ),
                        _common_directives_for_xml,
                        _elements,
                    ),
                    Delimited(
                        "EXPLICIT",
                        _common_directives_for_xml,
                        Ref.keyword("XMLDATA", optional=True),
                    ),
                    Delimited(
                        OneOf(
                            "AUTO",
                            Sequence(
                                "RAW",
                                Bracketed(
                                    Ref("LiteralGrammar"),
                                    optional=True,
                                ),
                            ),
                        ),
                        _common_directives_for_xml,
                        _elements,
                        Sequence(
                            OneOf(
                                "XMLDATA",
                                Sequence(
                                    "XMLSCHEMA",
                                    Bracketed(
                                        Ref("LiteralGrammar"),
                                        optional=True,
                                    ),
                                ),
                            ),
                            optional=True,
                        ),
                    ),
                ),
            ),
        ),
    )


class ExecuteScriptSegment(BaseSegment):
    """`EXECUTE` statement.

    Matching segment name and type from exasol.
    https://docs.microsoft.com/en-us/sql/t-sql/language-elements/execute-transact-sql?view=sql-server-ver15
    """

    type = "execute_script_statement"
    match_grammar = Sequence(
        OneOf("EXEC", "EXECUTE"),
        Sequence(Ref("ParameterNameSegment"), Ref("EqualsSegment"), optional=True),
        OptionallyBracketed(
            OneOf(Ref("ObjectReferenceSegment"), Ref("QuotedLiteralSegment"))
        ),
        Indent,
        Sequence(
            Sequence(Ref("ParameterNameSegment"), Ref("EqualsSegment"), optional=True),
            OneOf(
                "DEFAULT",
                Ref("LiteralGrammar"),
                Ref("ParameterNameSegment"),
                Ref("SingleIdentifierGrammar"),
            ),
            Sequence("OUTPUT", optional=True),
            AnyNumberOf(
                Ref("CommaSegment"),
                Sequence(
                    Ref("ParameterNameSegment"), Ref("EqualsSegment"), optional=True
                ),
                OneOf(
                    "DEFAULT",
                    Ref("LiteralGrammar"),
                    Ref("ParameterNameSegment"),
                    Ref("SingleIdentifierGrammar"),
                ),
                Sequence("OUTPUT", optional=True),
            ),
            optional=True,
        ),
        Dedent,
        Ref("DelimiterGrammar", optional=True),
    )


class CreateSchemaStatementSegment(BaseSegment):
    """A `CREATE SCHEMA` statement.

    Overriding ANSI to allow for AUTHORIZATION clause
    https://docs.microsoft.com/en-us/sql/t-sql/statements/create-schema-transact-sql?view=sql-server-ver15

    Not yet implemented: proper schema_element parsing.
    Once we have an AccessStatementSegment that works for TSQL, this definition should
    be tweaked to include schema elements.
    """

    type = "create_schema_statement"
    match_grammar = Sequence(
        "CREATE",
        "SCHEMA",
        Ref("SchemaReferenceSegment"),
        Sequence(
            "AUTHORIZATION",
            Ref("RoleReferenceSegment"),
            optional=True,
        ),
        Ref(
            "DelimiterGrammar",
            optional=True,
        ),
    )


class MergeStatementSegment(ansi.MergeStatementSegment):
    """Contains dialect specific `MERGE` statement."""

    type = "merge_statement"

    match_grammar = Sequence(
        Ref("MergeIntoLiteralGrammar"),
        Indent,
        Ref("TableReferenceSegment"),
        Sequence(
            "WITH",
            Bracketed(
                Delimited(
                    Ref("TableHintSegment", optional=True),
                )
            ),
            optional=True,
        ),
        Ref("AliasExpressionSegment", optional=True),
        Dedent,
        "USING",
        Indent,
        OneOf(
            Ref("TableReferenceSegment"),
            Ref("AliasedTableReferenceGrammar"),
            Sequence(
                Bracketed(
                    Ref("SelectableGrammar"),
                ),
                Ref("AliasExpressionSegment", optional=True),
            ),
        ),
        Dedent,
        Conditional(Indent, indented_using_on=True),
        Ref("JoinOnConditionSegment"),
        Conditional(Dedent, indented_using_on=True),
        Ref("MergeMatchSegment"),
    )


class MergeMatchSegment(BaseSegment):
    """Contains dialect specific merge operations."""

    type = "merge_match"
    match_grammar = Sequence(
        AnyNumberOf(
            Ref("MergeMatchedClauseSegment"),
            Ref("MergeNotMatchedClauseSegment"),
            min_times=1,
        ),
        Ref("OutputClauseSegment", optional=True),
        Ref("OptionClauseSegment", optional=True),
    )


class MergeMatchedClauseSegment(BaseSegment):
    """The `WHEN MATCHED` clause within a `MERGE` statement."""

    type = "merge_when_matched_clause"

    match_grammar = Sequence(
        "WHEN",
        "MATCHED",
        Sequence(
            "AND",
            Ref("ExpressionSegment"),
            optional=True,
        ),
        Indent,
        "THEN",
        OneOf(
            Ref("MergeUpdateClauseSegment"),
            Ref("MergeDeleteClauseSegment"),
        ),
        Dedent,
    )


class MergeNotMatchedClauseSegment(BaseSegment):
    """The `WHEN NOT MATCHED` clause within a `MERGE` statement."""

    type = "merge_when_not_matched_clause"

    match_grammar = OneOf(
        Sequence(
            "WHEN",
            "NOT",
            "MATCHED",
            Sequence("BY", "TARGET", optional=True),
            Sequence("AND", Ref("ExpressionSegment"), optional=True),
            Indent,
            "THEN",
            Ref("MergeInsertClauseSegment"),
            Dedent,
        ),
        Sequence(
            "WHEN",
            "NOT",
            "MATCHED",
            "BY",
            "SOURCE",
            Sequence("AND", Ref("ExpressionSegment"), optional=True),
            Indent,
            "THEN",
            OneOf(
                Ref("MergeUpdateClauseSegment"),
                Ref("MergeDeleteClauseSegment"),
            ),
            Dedent,
        ),
    )


class MergeInsertClauseSegment(BaseSegment):
    """`INSERT` clause within the `MERGE` statement."""

    type = "merge_insert_clause"
    match_grammar = Sequence(
        "INSERT",
        Indent,
        Ref("BracketedColumnReferenceListGrammar", optional=True),
        Dedent,
        "VALUES",
        Indent,
        OneOf(
            Bracketed(
                Delimited(
                    AnyNumberOf(
                        Ref("ExpressionSegment"),
                    ),
                ),
            ),
            Sequence(
                "DEFAULT",
                "VALUES",
            ),
        ),
        Dedent,
    )


class OutputClauseSegment(BaseSegment):
    """OUTPUT Clause used within DELETE, INSERT, UPDATE, MERGE.

    https://docs.microsoft.com/en-us/sql/t-sql/queries/output-clause-transact-sql?view=sql-server-ver15
    """

    type = "output_clause"
    match_grammar = AnyNumberOf(
        Sequence(
            "OUTPUT",
            Indent,
            Delimited(
                AnyNumberOf(
                    Ref("WildcardExpressionSegment"),
                    Sequence(
                        Ref("BaseExpressionElementGrammar"),
                        Ref("AliasExpressionSegment", optional=True),
                    ),
                    Ref("SingleIdentifierGrammar"),
                    terminators=[Ref.keyword("INTO")],
                ),
            ),
            Dedent,
            Sequence(
                "INTO",
                Indent,
                Ref("TableReferenceSegment"),
                Bracketed(
                    Delimited(
                        Ref("ColumnReferenceSegment"),
                    ),
                    optional=True,
                ),
                Dedent,
                optional=True,
            ),
        ),
    )


class ThrowStatementSegment(BaseSegment):
    """A THROW statement.

    https://docs.microsoft.com/en-us/sql/t-sql/language-elements/throw-transact-sql?view=sql-server-ver15
    """

    type = "throw_statement"
    match_grammar = Sequence(
        "THROW",
        Sequence(
            OneOf(
                # error_number
                Ref("NumericLiteralSegment"),
                Ref("ParameterNameSegment"),
            ),
            Ref("CommaSegment"),
            OneOf(
                # message
                Ref("QuotedLiteralSegment"),
                Ref("QuotedLiteralSegmentWithN"),
                Ref("ParameterNameSegment"),
            ),
            Ref("CommaSegment"),
            OneOf(
                # state
                Ref("NumericLiteralSegment"),
                Ref("ParameterNameSegment"),
            ),
            optional=True,
        ),
    )


class RaiserrorStatementSegment(BaseSegment):
    """RAISERROR statement.

    https://docs.microsoft.com/en-us/sql/t-sql/language-elements/raiserror-transact-sql?view=sql-server-ver15
    """

    type = "raiserror_statement"
    match_grammar = Sequence(
        "RAISERROR",
        Bracketed(
            Delimited(
                OneOf(
                    Ref("NumericLiteralSegment"),
                    Ref("QuotedLiteralSegment"),
                    Ref("QuotedLiteralSegmentWithN"),
                    Ref("ParameterNameSegment"),
                ),
                OneOf(
                    Ref("NumericLiteralSegment"),
                    Ref("QualifiedNumericLiteralSegment"),
                    Ref("ParameterNameSegment"),
                ),
                OneOf(
                    Ref("NumericLiteralSegment"),
                    Ref("QualifiedNumericLiteralSegment"),
                    Ref("ParameterNameSegment"),
                ),
                AnyNumberOf(
                    Ref("LiteralGrammar"),
                    Ref("ParameterNameSegment"),
                    min_times=0,
                    max_times=20,
                ),
            ),
        ),
        Sequence(
            "WITH",
            Delimited(
                "LOG",
                "NOWAIT",
                "SETERROR",
            ),
            optional=True,
        ),
    )


class WindowSpecificationSegment(BaseSegment):
    """Window specification within OVER(...).

    Overriding ANSI to remove window name option not supported by TSQL
    """

    type = "window_specification"
    match_grammar = Sequence(
        Ref("PartitionClauseSegment", optional=True),
        Ref("OrderByClauseSegment", optional=True),
        Ref("FrameClauseSegment", optional=True),
        optional=True,
    )


class GotoStatement(BaseSegment):
    """GOTO statement.

    https://docs.microsoft.com/en-us/sql/t-sql/language-elements/goto-transact-sql?view=sql-server-ver15
    """

    type = "goto_statement"
    match_grammar = Sequence("GOTO", Ref("SingleIdentifierGrammar"))


class ExecuteAsClause(BaseSegment):
    """EXECUTE AS Clause.

    https://learn.microsoft.com/en-us/sql/t-sql/statements/execute-as-clause-transact-sql?view=sql-server-ver16
    """

    type = "execute_as_clause"
    match_grammar = Sequence(
        "EXECUTE",
        "AS",
        Ref("SingleQuotedIdentifierSegment"),
    )


class CreateTriggerStatementSegment(BaseSegment):
    """Create Trigger Statement.

    https://docs.microsoft.com/en-us/sql/t-sql/statements/create-trigger-transact-sql?view=sql-server-ver15
    """

    type = "create_trigger"

    match_grammar: Matchable = Sequence(
        "CREATE",
        "TRIGGER",
        Ref("TriggerReferenceSegment"),
        "ON",
        OneOf(
            Ref("TableReferenceSegment"),
            Sequence("ALL", "SERVER"),
            "DATABASE",
        ),
        Sequence(
            "WITH",
            AnySetOf(
                # NOTE: Techincally, ENCRYPTION can't be combined with the other two,
                # but this slightly more generous parsing is ok for SQLFluff.
                Ref.keyword("ENCRYPTION"),
                Ref.keyword("NATIVE_COMPILATION"),
                Ref.keyword("SCHEMABINDING"),
            ),
            Ref("ExecuteAsClause", optional=True),
            optional=True,
        ),
        OneOf(
            Sequence("FOR", Delimited(Ref("SingleIdentifierGrammar"), optional=True)),
            "AFTER",
            Sequence("INSTEAD", "OF"),
            optional=True,
        ),
        Delimited(
            "INSERT",
            "UPDATE",
            "DELETE",
            optional=True,
        ),
        Sequence("WITH", "APPEND", optional=True),
        Sequence("NOT", "FOR", "REPLICATION", optional=True),
        "AS",
        Ref("OneOrMoreStatementsGrammar"),
        # TODO: EXTERNAL NAME
    )


class DropTriggerStatementSegment(BaseSegment):
    """Drop Trigger Statement.

    https://docs.microsoft.com/en-us/sql/t-sql/statements/drop-trigger-transact-sql?view=sql-server-ver15
    """

    type = "drop_trigger"

    match_grammar: Matchable = Sequence(
        "DROP",
        "TRIGGER",
        Ref("IfExistsGrammar", optional=True),
        Delimited(Ref("TriggerReferenceSegment")),
        Sequence("ON", OneOf("DATABASE", Sequence("ALL", "SERVER")), optional=True),
    )


class DisableTriggerStatementSegment(BaseSegment):
    """Disable Trigger Statement.

    https://docs.microsoft.com/en-us/sql/t-sql/statements/disable-trigger-transact-sql?view=sql-server-ver15
    """

    type = "disable_trigger"

    match_grammar: Matchable = Sequence(
        "DISABLE",
        "TRIGGER",
        OneOf(
            Delimited(Ref("TriggerReferenceSegment")),
            "ALL",
        ),
        Sequence(
            "ON",
            OneOf(Ref("ObjectReferenceSegment"), "DATABASE", Sequence("ALL", "SERVER")),
            optional=True,
        ),
    )


class LabelStatementSegment(BaseSegment):
    """Label Statement, for a GOTO statement.

    https://docs.microsoft.com/en-us/sql/t-sql/language-elements/goto-transact-sql?view=sql-server-ver15
    """

    type = "label_segment"

    match_grammar: Matchable = Sequence(
        Ref("NakedIdentifierSegment"), Ref("ColonSegment"), allow_gaps=False
    )


class AccessStatementSegment(BaseSegment):
    """A `GRANT` or `REVOKE` statement.

    https://docs.microsoft.com/en-us/sql/t-sql/statements/grant-transact-sql?view=sql-server-ver15
    https://docs.microsoft.com/en-us/sql/t-sql/statements/deny-transact-sql?view=sql-server-ver15
    https://docs.microsoft.com/en-us/sql/t-sql/statements/revoke-transact-sql?view=sql-server-ver15
    """

    type = "access_statement"

    # Privileges that can be set on the account (specific to snowflake)
    _global_permissions = OneOf(
        Sequence(
            "CREATE",
            OneOf(
                "ROLE",
                "USER",
                "WAREHOUSE",
                "DATABASE",
                "INTEGRATION",
            ),
        ),
        Sequence("APPLY", "MASKING", "POLICY"),
        "EXECUTE",
    )

    _schema_object_names = [
        "TABLE",
        "VIEW",
        "FUNCTION",
        "PROCEDURE",
        "SEQUENCE",
    ]

    _schema_object_types = OneOf(
        *_schema_object_names,
        Sequence("EXTERNAL", "TABLE"),
        Sequence("FILE", "FORMAT"),
    )

    # We reuse the object names above and simply append an `S` to the end of them to get
    # plurals
    _schema_object_types_plural = OneOf(
        *[f"{object_name}S" for object_name in _schema_object_names]
    )

    _permissions = Sequence(
        OneOf(
            "ALTER",
            "CONTROL",
            "DELETE",
            "EXECUTE",
            "INSERT",
            "RECEIVE",
            "REFERENCES",
            "SELECT",
            Sequence("TAKE", "OWNERSHIP"),
            "UPDATE",
            Sequence("VIEW", "CHANGE", "TRACKING"),
            Sequence("VIEW", "DEFINITION"),
        ),
        Ref("BracketedColumnReferenceListGrammar", optional=True),
    )

    # All of the object types that we can grant permissions on.
    # This list will contain ansi sql objects as well as dialect specific ones.
    _objects = Sequence(
        OneOf(
            "DATABASE",
            "LANGUAGE",
            "SCHEMA",
            "ROLE",
            "TYPE",
            Sequence(
                "FOREIGN",
                OneOf("SERVER", Sequence("DATA", "WRAPPER")),
            ),
            Sequence("ALL", "SCHEMAS", "IN", "DATABASE"),
            _schema_object_types,
            Sequence("ALL", _schema_object_types_plural, "IN", "SCHEMA"),
            optional=True,
        ),
        Delimited(Ref("ObjectReferenceSegment"), terminators=["TO", "FROM"]),
        Ref("FunctionParameterListGrammar", optional=True),
    )

    match_grammar: Matchable = OneOf(
        # Based on https://www.postgresql.org/docs/13/sql-grant.html
        # and https://docs.snowflake.com/en/sql-reference/sql/grant-privilege.html
        Sequence(
            "GRANT",
            OneOf(
                Sequence(
                    Delimited(
                        OneOf(_global_permissions, _permissions),
                        terminators=["ON"],
                    ),
                ),
                Sequence("ALL", Ref.keyword("PRIVILEGES", optional=True)),
            ),
            "ON",
            Sequence(
                OneOf("LOGIN", "DATABASE", "OBJECT", "ROLE", "SCHEMA", "USER"),
                Ref("CastOperatorSegment"),
                optional=True,
            ),
            _objects,
            "TO",
            Delimited(
                OneOf(Ref("RoleReferenceSegment"), Ref("FunctionSegment")),
            ),
            OneOf(
                Sequence("WITH", "GRANT", "OPTION"),
                optional=True,
            ),
            Sequence(
                "AS",
                Ref("ObjectReferenceSegment"),
                optional=True,
            ),
        ),
        Sequence(
            "DENY",
            OneOf(
                Delimited(
                    OneOf(_global_permissions, _permissions),
                    terminators=["ON"],
                ),
                Sequence("ALL", Ref.keyword("PRIVILEGES", optional=True)),
            ),
            "ON",
            Sequence(
                OneOf("LOGIN", "DATABASE", "OBJECT", "ROLE", "SCHEMA", "USER"),
                Ref("CastOperatorSegment"),
                optional=True,
            ),
            _objects,
            OneOf("TO"),
            Delimited(
                Ref("RoleReferenceSegment"),
            ),
            Sequence(
                Ref.keyword("CASCADE", optional=True),
                Ref("ObjectReferenceSegment", optional=True),
                optional=True,
            ),
        ),
        Sequence(
            "REVOKE",
            Sequence("GRANT", "OPTION", "FOR", optional=True),
            OneOf(
                Delimited(
                    OneOf(_global_permissions, _permissions),
                    terminators=["ON"],
                ),
                Sequence("ALL", Ref.keyword("PRIVILEGES", optional=True)),
            ),
            "ON",
            Sequence(
                OneOf("LOGIN", "DATABASE", "OBJECT", "ROLE", "SCHEMA", "USER"),
                Ref("CastOperatorSegment"),
                optional=True,
            ),
            _objects,
            OneOf("TO", "FROM"),
            Delimited(
                Ref("RoleReferenceSegment"),
            ),
            Sequence(
                Ref.keyword("CASCADE", optional=True),
                Ref("ObjectReferenceSegment", optional=True),
                optional=True,
            ),
        ),
    )


class CreateTypeStatementSegment(BaseSegment):
    """A `CREATE TYPE` statement.

    https://docs.microsoft.com/en-us/sql/t-sql/statements/create-type-transact-sql?view=sql-server-ver15
    """

    type = "create_type_statement"
    match_grammar: Matchable = Sequence(
        "CREATE",
        "TYPE",
        Ref("ObjectReferenceSegment"),
        OneOf(
            Sequence("FROM", Ref("ObjectReferenceSegment")),
            Sequence(
                "AS",
                "TABLE",
                Sequence(
                    Bracketed(
                        Delimited(
                            OneOf(
                                Ref("TableConstraintSegment"),
                                Ref("ColumnDefinitionSegment"),
                                Ref("TableIndexSegment"),
                            ),
                            allow_trailing=True,
                        )
                    ),
                ),
            ),
        ),
    )


class OpenCursorStatementSegment(BaseSegment):
    """An `OPEN` cursor statement.

    https://docs.microsoft.com/en-us/sql/t-sql/language-elements/open-transact-sql?view=sql-server-ver15
    """

    type = "open_cursor_statement"
    match_grammar: Matchable = Sequence(
        "OPEN",
        Ref("CursorNameGrammar"),
    )


class CloseCursorStatementSegment(BaseSegment):
    """A `CLOSE` cursor statement.

    https://docs.microsoft.com/en-us/sql/t-sql/language-elements/close-transact-sql?view=sql-server-ver15
    """

    type = "close_cursor_statement"
    match_grammar: Matchable = Sequence(
        "CLOSE",
        Ref("CursorNameGrammar"),
    )


class DeallocateCursorStatementSegment(BaseSegment):
    """A `DEALLOCATE` cursor statement.

    https://docs.microsoft.com/en-us/sql/t-sql/language-elements/deallocate-transact-sql?view=sql-server-ver15
    """

    type = "deallocate_cursor_statement"
    match_grammar: Matchable = Sequence(
        "DEALLOCATE",
        Ref("CursorNameGrammar"),
    )


class FetchCursorStatementSegment(BaseSegment):
    """A `FETCH` cursor statement.

    https://docs.microsoft.com/en-us/sql/t-sql/language-elements/fetch-transact-sql?view=sql-server-ver15
    """

    type = "fetch_cursor_statement"
    match_grammar: Matchable = Sequence(
        "FETCH",
        OneOf("NEXT", "PRIOR", "FIRST", "LAST", optional=True),
        "FROM",
        Ref("CursorNameGrammar"),
        Sequence("INTO", Delimited(Ref("ParameterNameSegment")), optional=True),
    )


class ConcatSegment(CompositeBinaryOperatorSegment):
    """Concat operator."""

    match_grammar: Matchable = Ref("PlusSegment")


class CreateSynonymStatementSegment(BaseSegment):
    """A `CREATE SYNONYM` statement."""

    type = "create_synonym_statement"
    # https://learn.microsoft.com/en-us/sql/t-sql/statements/create-synonym-transact-sql
    match_grammar: Matchable = Sequence(
        "CREATE",
        "SYNONYM",
        Ref("SynonymReferenceSegment"),
        "FOR",
        Ref("ObjectReferenceSegment"),
    )


class DropSynonymStatementSegment(BaseSegment):
    """A `DROP SYNONYM` statement."""

    type = "drop_synonym_statement"
    # https://learn.microsoft.com/en-us/sql/t-sql/statements/drop-synonym-transact-sql
    match_grammar: Matchable = Sequence(
        "DROP",
        "SYNONYM",
        Ref("IfExistsGrammar", optional=True),
        Ref("SynonymReferenceSegment"),
    )


class SynonymReferenceSegment(ansi.ObjectReferenceSegment):
    """A reference to a synonym.

    A synonym may only (optionally) specify a schema. It may not specify a server
    or database name.
    """

    type = "synonym_reference"
    # match grammar (allow whitespace)
    match_grammar: Matchable = Sequence(
        Ref("SingleIdentifierGrammar"),
        AnyNumberOf(
            Sequence(
                Ref("DotSegment"),
                Ref("SingleIdentifierGrammar", optional=True),
            ),
            min_times=0,
            max_times=1,
        ),
    )


class SamplingExpressionSegment(ansi.SamplingExpressionSegment):
    """Override ANSI to use TSQL TABLESAMPLE expression."""

    type = "sample_expression"
    match_grammar: Matchable = Sequence(
        "TABLESAMPLE",
        Sequence("SYSTEM", optional=True),
        Bracketed(
            Sequence(
                Ref("NumericLiteralSegment"), OneOf("PERCENT", "ROWS", optional=True)
            )
        ),
        Sequence(
            OneOf("REPEATABLE"),
            Bracketed(Ref("NumericLiteralSegment")),
            optional=True,
        ),
    )


class TemporalQuerySegment(BaseSegment):
    """A segment that allows Temporal Queries to be run.

    https://learn.microsoft.com/en-us/sql/relational-databases/tables/temporal-tables?view=sql-server-ver16
    """

    type = "temporal_query"

    match_grammar: Matchable = Sequence(
        "FOR",
        "SYSTEM_TIME",
        OneOf(
            "ALL",
            Sequence(
                "AS",
                "OF",
                Ref("QuotedLiteralSegment"),
            ),
            Sequence(
                "FROM",
                Ref("QuotedLiteralSegment"),
                "TO",
                Ref("QuotedLiteralSegment"),
            ),
            Sequence(
                "BETWEEN",
                Ref("QuotedLiteralSegment"),
                "AND",
                Ref("QuotedLiteralSegment"),
            ),
            Sequence(
                "CONTAINED",
                "IN",
                Bracketed(
                    Delimited(
                        Ref("QuotedLiteralSegment"),
                    )
                ),
            ),
        ),
    )


class CreateDatabaseScopedCredentialStatementSegment(BaseSegment):
    """A statement to create a database scoped credential.

    https://learn.microsoft.com/en-us/sql/t-sql/statements/create-database-scoped-credential-transact-sql?view=sql-server-ver16
    """

    type = "create_database_scoped_credential_statement"

    match_grammar: Matchable = Sequence(
        "CREATE",
        "DATABASE",
        "SCOPED",
        "CREDENTIAL",
        Ref("ObjectReferenceSegment"),
        "WITH",
        Ref("CredentialGrammar"),
    )


class CreateExternalDataSourceStatementSegment(BaseSegment):
    """A statement to create an external data source.

    https://learn.microsoft.com/en-us/sql/t-sql/statements/create-external-data-source-transact-sql?view=sql-server-ver16&tabs=dedicated#syntax
    """

    type = "create_external_data_source_statement"

    match_grammar: Matchable = Sequence(
        "CREATE",
        "EXTERNAL",
        "DATA",
        "SOURCE",
        Ref("ObjectReferenceSegment"),
        "WITH",
        Bracketed(
            Delimited(
                Ref("TableLocationClause"),
                Sequence(
                    "CONNECTION_OPTIONS",
                    Ref("EqualsSegment"),
                    AnyNumberOf(Ref("QuotedLiteralSegmentOptWithN")),
                ),
                Sequence(
                    "CREDENTIAL",
                    Ref("EqualsSegment"),
                    Ref("ObjectReferenceSegment"),
                ),
                Sequence(
                    "PUSHDOWN",
                    Ref("EqualsSegment"),
                    OneOf("ON", "OFF"),
                ),
            ),
        ),
    )


class PeriodSegment(BaseSegment):
    """A `PERIOD FOR SYSTEM_TIME` for `CREATE TABLE` of temporal tables.

    https://docs.microsoft.com/en-us/sql/t-sql/statements/create-table-transact-sql?view=sql-server-ver15
    https://learn.microsoft.com/en-us/sql/t-sql/statements/create-table-transact-sql?view=sql-server-ver16#generated-always-as--row--transaction_id--sequence_number----start--end---hidden---not-null-
    """

    type = "period_segment"
    match_grammar = Sequence(
        "PERIOD",
        "FOR",
        "SYSTEM_TIME",
        Bracketed(
            Delimited(
                Ref("ColumnReferenceSegment"),
                Ref("ColumnReferenceSegment"),
            ),
        ),
    )


class SqlcmdCommandSegment(BaseSegment):
    """A `sqlcmd` command.

    Microsoft allows professional CI/CD deployment through so called 'SQL Database
    Projects'.
    There are propietary `sqlcmd Commands` that can be part of an SQL file.
    https://learn.microsoft.com/en-us/sql/tools/sqlcmd/sqlcmd-utility?view=sql-server-ver16#sqlcmd-commands
    """

    type = "sqlcmd_command_segment"

    match_grammar: Matchable = OneOf(
        Sequence(
            Sequence(
                Ref("ColonSegment"),
                Ref("SqlcmdOperatorSegment"),  # `:r`
                allow_gaps=False,
            ),
            Ref("SqlcmdFilePathSegment"),
        ),
        Sequence(
            Sequence(
                Ref("ColonSegment"),
                Ref("SqlcmdOperatorSegment"),  # `:setvar`
                allow_gaps=False,
            ),
            Ref("ObjectReferenceSegment"),
            Ref("CodeSegment"),
        ),
    )


class ExternalFileFormatDelimitedTextFormatOptionClause(BaseSegment):
    """`CREATE EXTERNAL FILE FORMAT` Delimited text `FORMAT_OPTIONS` clause."""

    type = "external_file_delimited_text_format_options_clause"

    match_grammar = OneOf(
        Sequence(
            OneOf(
                "FIELD_TERMINATOR", "STRING_DELIMITER", "DATE_FORMAT", "PARSER_VERSION"
            ),
            Ref("EqualsSegment"),
            Ref("QuotedLiteralSegment"),
        ),
        Sequence(
            "FIRST_ROW",
            Ref("EqualsSegment"),
            Ref("NumericLiteralSegment"),
        ),
        Sequence(
            "USE_TYPE_DEFAULT",
            Ref("EqualsSegment"),
            Ref("BooleanLiteralGrammar"),
        ),
        Sequence(
            "ENCODING",
            Ref("EqualsSegment"),
            Ref("FileEncodingSegment"),
        ),
    )


class ExternalFileFormatDelimitedTextClause(BaseSegment):
    """`CREATE EXTERNAL FILE FORMAT` *Delimited text* clause.

    https://learn.microsoft.com/en-us/sql/t-sql/statements/create-external-file-format-transact-sql?view=sql-server-ver16&tabs=delimited#syntax
    """

    type = "external_file_delimited_text_clause"

    match_grammar = Delimited(
        Sequence(
            "FORMAT_TYPE",
            Ref("EqualsSegment"),
            "DELIMITEDTEXT",
        ),
        Sequence(
            "FORMAT_OPTIONS",
            Bracketed(
                Delimited(
                    Ref("ExternalFileFormatDelimitedTextFormatOptionClause"),
                ),
            ),
            optional=True,
        ),
        Sequence(
            "DATA_COMPRESSION",
            Ref("EqualsSegment"),
            Ref("FileCompressionSegment"),
            optional=True,
        ),
    )


class ExternalFileFormatRcClause(BaseSegment):
    """`CREATE EXTERNAL FILE FORMAT` *Record Columnar file format (RcFile)* clause.

    https://learn.microsoft.com/en-us/sql/t-sql/statements/create-external-file-format-transact-sql?view=sql-server-ver16&tabs=rc#syntax
    """

    type = "external_file_rc_clause"

    match_grammar = Delimited(
        Sequence(
            "FORMAT_TYPE",
            Ref("EqualsSegment"),
            "RCFILE",
        ),
        Sequence(
            "SERDE_METHOD",
            Ref("EqualsSegment"),
            Ref("SerdeMethodSegment"),
        ),
        Sequence(
            "DATA_COMPRESSION",
            Ref("EqualsSegment"),
            Ref("FileCompressionSegment"),
            optional=True,
        ),
    )


class ExternalFileFormatOrcClause(BaseSegment):
    """`CREATE EXTERNAL FILE FORMAT` *Optimized Row Columnar (ORC)* format clause.

    https://learn.microsoft.com/en-us/sql/t-sql/statements/create-external-file-format-transact-sql?view=sql-server-ver16&tabs=orc#syntax
    """

    type = "external_file_orc_clause"

    match_grammar = Delimited(
        Sequence(
            "FORMAT_TYPE",
            Ref("EqualsSegment"),
            "ORC",
        ),
        Sequence(
            "DATA_COMPRESSION",
            Ref("EqualsSegment"),
            Ref("FileCompressionSegment"),
            optional=True,
        ),
    )


class ExternalFileFormatParquetClause(BaseSegment):
    """`CREATE EXTERNAL FILE FORMAT` *PARQUET* format clause.

    https://learn.microsoft.com/en-us/sql/t-sql/statements/create-external-file-format-transact-sql?view=sql-server-ver16&tabs=parquet#syntax
    """

    type = "external_file_parquet_clause"

    match_grammar = Delimited(
        Sequence(
            "FORMAT_TYPE",
            Ref("EqualsSegment"),
            "PARQUET",
        ),
        Sequence(
            "DATA_COMPRESSION",
            Ref("EqualsSegment"),
            Ref("FileCompressionSegment"),
            optional=True,
        ),
    )


class ExternalFileFormatJsonClause(BaseSegment):
    """`CREATE EXTERNAL FILE FORMAT` *JSON* format clause.

    https://learn.microsoft.com/en-us/sql/t-sql/statements/create-external-file-format-transact-sql?view=sql-server-ver16&tabs=json#syntax
    """

    type = "external_file_json_clause"

    match_grammar = Delimited(
        Sequence(
            "FORMAT_TYPE",
            Ref("EqualsSegment"),
            "JSON",
        ),
        Sequence(
            "DATA_COMPRESSION",
            Ref("EqualsSegment"),
            Ref("FileCompressionSegment"),
            optional=True,
        ),
    )


class ExternalFileFormatDeltaClause(BaseSegment):
    """`CREATE EXTERNAL FILE FORMAT` *Delta Lake* format clause.

    https://learn.microsoft.com/en-us/sql/t-sql/statements/create-external-file-format-transact-sql?view=sql-server-ver16&tabs=delta#syntax
    """

    type = "external_file_delta_clause"

    match_grammar = Sequence(
        "FORMAT_TYPE",
        Ref("EqualsSegment"),
        "DELTA",
    )


class CreateExternalFileFormat(BaseSegment):
    """A statement to create an `EXTERNAL FILE FORMAT` object.

    https://learn.microsoft.com/en-us/sql/t-sql/statements/create-external-file-format-transact-sql?view=sql-server-ver16&tabs=delta#syntax
    """

    type = "create_external_file_format"

    match_grammar: Matchable = Sequence(
        "CREATE",
        "EXTERNAL",
        "FILE",
        "FORMAT",
        Ref("ObjectReferenceSegment"),
        "WITH",
        Bracketed(
            OneOf(
                Ref("ExternalFileFormatDelimitedTextClause"),
                Ref("ExternalFileFormatRcClause"),
                Ref("ExternalFileFormatOrcClause"),
                Ref("ExternalFileFormatParquetClause"),
                Ref("ExternalFileFormatJsonClause"),
                Ref("ExternalFileFormatDeltaClause"),
            ),
        ),
    )


class OpenJsonWithClauseSegment(BaseSegment):
    """A `WITH` clause of an `OPENJSON()` table-valued function.

    https://learn.microsoft.com/en-us/sql/t-sql/functions/openjson-transact-sql?view=sql-server-ver16#with_clause
    """

    type = "openjson_with_clause"

    match_grammar = Sequence(
        "WITH",
        Bracketed(
            Delimited(
                Sequence(
                    Ref("ColumnReferenceSegment"),
                    Ref("DatatypeSegment"),
                    Ref("QuotedLiteralSegment", optional=True),  # column_path
                    Sequence(
                        "AS",
                        "JSON",
                        optional=True,
                    ),
                ),
            ),
        ),
    )


class OpenJsonSegment(BaseSegment):
    """An `OPENJSON()` table-valued function.

    https://learn.microsoft.com/en-us/sql/t-sql/functions/openjson-transact-sql?view=sql-server-ver16#syntax
    """

    type = "openjson_segment"

    match_grammar = Sequence(
        "OPENJSON",
        Bracketed(
            Delimited(
                Ref("QuotedLiteralSegmentOptWithN"),  # jsonExpression
                Ref("ColumnReferenceSegment"),
                Ref("ParameterNameSegment"),
                Ref("QuotedLiteralSegment"),  # path
            ),
        ),
        Ref("OpenJsonWithClauseSegment", optional=True),
    )


class CreateExternalTableStatementSegment(BaseSegment):
    """A `CREATE EXTERNAL TABLE` statement.

    https://learn.microsoft.com/en-us/sql/t-sql/statements/create-external-table-transact-sql?view=sql-server-ver16&tabs=dedicated
    """

    type = "create_external_table_statement"

    match_grammar = Sequence(
        "CREATE",
        "EXTERNAL",
        "TABLE",
        Ref("ObjectReferenceSegment"),
        Bracketed(
            Delimited(
                Ref("ColumnDefinitionSegment"),
            ),
        ),
        "WITH",
        Bracketed(
            Delimited(
                Ref("TableLocationClause"),
                Sequence(
                    "DATA_SOURCE",
                    Ref("EqualsSegment"),
                    Ref("ObjectReferenceSegment"),
                ),
                Sequence(
                    "FILE_FORMAT",
                    Ref("EqualsSegment"),
                    Ref("ObjectReferenceSegment"),
                ),
                Sequence(
                    "REJECT_TYPE",
                    Ref("EqualsSegment"),
                    OneOf("value", "percentage"),
                ),
                Sequence(
                    "REJECT_VALUE",
                    Ref("EqualsSegment"),
                    Ref("NumericLiteralSegment"),
                ),
                Sequence(
                    "REJECT_SAMPLE_VALUE",
                    Ref("EqualsSegment"),
                    Ref("NumericLiteralSegment"),
                ),
                Sequence(
                    "REJECTED_ROW_LOCATION",
                    Ref("EqualsSegment"),
                    Ref("QuotedLiteralSegment"),
                ),
            ),
        ),
    )


class CreateRoleStatementSegment(ansi.CreateRoleStatementSegment):
    """A `CREATE ROLE` statement.

    https://learn.microsoft.com/en-us/sql/t-sql/statements/create-role-transact-sql?view=sql-server-ver16
    """

    type = "create_role_statement"

    match_grammar = Sequence(
        "CREATE",
        "ROLE",
        Ref("RoleReferenceSegment"),
        Sequence(
            "AUTHORIZATION",
            Ref("RoleReferenceSegment"),
            optional=True,
        ),
    )


class DropExternalTableStatementSegment(BaseSegment):
    """A `DROP EXTERNAL TABLE ...` statement.

    https://learn.microsoft.com/en-us/sql/t-sql/statements/drop-external-table-transact-sql
    """

    type = "drop_external_table_statement"
    match_grammar = Sequence(
        "DROP",
        "EXTERNAL",
        "TABLE",
        Ref("TableReferenceSegment"),
    )


class StorageLocationSegment(BaseSegment):
    """A tsql external storage location.

    https://learn.microsoft.com/en-us/sql/t-sql/statements/copy-into-transact-sql?view=azure-sqldw-latest#external-locations
    """

    type = "storage_location"

    match_grammar = OneOf(
        Ref("AzureBlobStoragePath"),
        Ref("AzureDataLakeStorageGen2Path"),
    )


class CopyIntoTableStatementSegment(BaseSegment):
    """A tsql `COPY INTO <table>` statement.

    https://learn.microsoft.com/en-us/sql/t-sql/statements/copy-into-transact-sql?view=azure-sqldw-latest
    """

    type = "copy_into_table_statement"

    match_grammar = Sequence(
        "COPY",
        "INTO",
        Ref("TableReferenceSegment"),
        Bracketed(Delimited(Ref("ColumnDefinitionSegment")), optional=True),
        Ref("FromClauseSegment"),
        Sequence(
            "WITH",
            Bracketed(
                Delimited(
                    AnySetOf(
                        Sequence(
                            "FILE_TYPE",
                            Ref("EqualsSegment"),
                            Ref("QuotedLiteralSegment"),
                        ),
                        Sequence(
                            "FILE_FORMAT",
                            Ref("EqualsSegment"),
                            Ref("ObjectReferenceSegment"),
                        ),
                        Sequence(
                            "CREDENTIAL",
                            Ref("EqualsSegment"),
                            Bracketed(Ref("CredentialGrammar")),
                        ),
                        Sequence(
                            "ERRORFILE",
                            Ref("EqualsSegment"),
                            Ref("QuotedLiteralSegment"),
                        ),
                        Sequence(
                            "ERRORFILE_CREDENTIAL",
                            Ref("EqualsSegment"),
                            Bracketed(Ref("CredentialGrammar")),
                        ),
                        Sequence(
                            "MAXERRORS",
                            Ref("EqualsSegment"),
                            Ref("NumericLiteralSegment"),
                        ),
                        Sequence(
                            "COMPRESSION",
                            Ref("EqualsSegment"),
                            Ref("QuotedLiteralSegment"),
                        ),
                        Sequence(
                            "FIELDQUOTE",
                            Ref("EqualsSegment"),
                            Ref("QuotedLiteralSegment"),
                        ),
                        Sequence(
                            "FIELDTERMINATOR",
                            Ref("EqualsSegment"),
                            Ref("QuotedLiteralSegment"),
                        ),
                        Sequence(
                            "ROWTERMINATOR",
                            Ref("EqualsSegment"),
                            Ref("QuotedLiteralSegment"),
                        ),
                        Sequence(
                            "FIRSTROW",
                            Ref("EqualsSegment"),
                            Ref("NumericLiteralSegment"),
                        ),
                        Sequence(
                            "DATEFORMAT",
                            Ref("EqualsSegment"),
                            Ref("QuotedLiteralSegment"),
                        ),
                        Sequence(
                            "ENCODING",
                            Ref("EqualsSegment"),
                            Ref("FileEncodingSegment"),
                        ),
                        Sequence(
                            "IDENTITY_INSERT",
                            Ref("EqualsSegment"),
                            Ref("QuotedLiteralSegment"),
                        ),
                        Sequence(
                            "AUTO_CREATE_TABLE",
                            Ref("EqualsSegment"),
                            Ref("QuotedLiteralSegment"),
                        ),
                    )
                )
            ),
            optional=True,
        ),
    )


class CreateUserStatementSegment(ansi.CreateUserStatementSegment):
    """`CREATE USER` statement.

    https://learn.microsoft.com/en-us/sql/t-sql/statements/create-user-transact-sql?view=sql-server-ver16#syntax
    """

    match_grammar = Sequence(
        "CREATE",
        "USER",
        Ref("RoleReferenceSegment"),
        Sequence(
            OneOf("FROM", "FOR"),
            "LOGIN",
            Ref("ObjectReferenceSegment"),
            optional=True,
        ),
    )
