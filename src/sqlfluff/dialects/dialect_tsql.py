"""The MSSQL T-SQL dialect.

https://docs.microsoft.com/en-us/sql/t-sql/language-elements/language-elements-transact-sql
"""

from sqlfluff.core.parser import (
    BaseSegment,
    Sequence,
    OneOf,
    Bracketed,
    Ref,
    Anything,
    Nothing,
    RegexLexer,
    CodeSegment,
    RegexParser,
    Delimited,
    Matchable,
    NamedParser,
    OptionallyBracketed,
    Dedent,
    BaseFileSegment,
    Indent,
    AnyNumberOf,
    CommentSegment,
    StringParser,
    SymbolSegment,
    SegmentGenerator,
    StringLexer,
)

from sqlfluff.core.dialects import load_raw_dialect

from sqlfluff.dialects.dialect_tsql_keywords import (
    RESERVED_KEYWORDS,
    UNRESERVED_KEYWORDS,
)

from sqlfluff.core.parser.segments.raw import NewlineSegment, WhitespaceSegment

ansi_dialect = load_raw_dialect("ansi")
tsql_dialect = ansi_dialect.copy_as("tsql")

# Should really clear down the old keywords but some are needed by certain segments
# tsql_dialect.sets("reserved_keywords").clear()
# tsql_dialect.sets("unreserved_keywords").clear()
tsql_dialect.sets("reserved_keywords").update(RESERVED_KEYWORDS)
tsql_dialect.sets("unreserved_keywords").update(UNRESERVED_KEYWORDS)

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
        RegexLexer("single_quote_with_n", r"N'([^']|'')*'", CodeSegment),
        RegexLexer(
            "hash_prefix",
            r"[#][#]?[a-zA-Z0-9_]+",
            CodeSegment,
        ),
        StringLexer("not", "!", CodeSegment),
    ],
    before="back_quote",
)

tsql_dialect.patch_lexer_matchers(
    [
        # Patching single_quote to allow for TSQL-style escaped quotes
        RegexLexer("single_quote", r"'([^']|'')*'", CodeSegment),
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
        #       (?R)             Recusively match the block comment pattern
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
                r"[\t ]+",
                WhitespaceSegment,
            ),
        ),
        # Patching to add !<, !>
        RegexLexer("greater_than_or_equal", ">=|!<", CodeSegment),
        RegexLexer("less_than_or_equal", "<=|!>", CodeSegment),
        RegexLexer(
            "code", r"[0-9a-zA-Z_#@]+", CodeSegment
        ),  # overriding to allow hash mark and at-sign in code
    ]
)

tsql_dialect.add(
    BracketedIdentifierSegment=NamedParser(
        "square_quote", CodeSegment, name="quoted_identifier", type="identifier"
    ),
    HashIdentifierSegment=NamedParser(
        "hash_prefix", CodeSegment, name="hash_identifier", type="identifier"
    ),
    VariableIdentifierSegment=NamedParser(
        "var_prefix", CodeSegment, name="variable_identifier", type="identifier"
    ),
    BatchDelimiterSegment=Ref("GoStatementSegment"),
    QuotedLiteralSegmentWithN=NamedParser(
        "single_quote_with_n", CodeSegment, name="quoted_literal", type="literal"
    ),
    NotSegment=StringParser("!", SymbolSegment, name="not", type="comparison_operator"),
    NotGreaterThanSegment=StringParser(
        "!>", SymbolSegment, name="less_than_equal_to", type="comparison_operator"
    ),
    NotLessThanSegment=StringParser(
        "!<", SymbolSegment, name="greater_than_equal_to", type="comparison_operator"
    ),
)

tsql_dialect.replace(
    # Overriding to cover TSQL allowed identifier name characters
    # https://docs.microsoft.com/en-us/sql/relational-databases/databases/database-identifiers?view=sql-server-ver15
    NakedIdentifierSegment=SegmentGenerator(
        # Generate the anti template from the set of reserved keywords
        lambda dialect: RegexParser(
            r"[A-Z_][A-Z0-9_@$#]*",
            CodeSegment,
            name="naked_identifier",
            type="identifier",
            anti_template=r"^(" + r"|".join(dialect.sets("reserved_keywords")) + r")$",
        )
    ),
    ComparisonOperatorGrammar=OneOf(
        Ref("EqualsSegment"),
        Ref("GreaterThanSegment"),
        Ref("LessThanSegment"),
        Ref("GreaterThanOrEqualToSegment"),
        Ref("LessThanOrEqualToSegment"),
        Ref("NotEqualToSegment_a"),
        Ref("NotEqualToSegment_b"),
        Ref("LikeOperatorSegment"),
        Ref("NotGreaterThanSegment"),
        Ref("NotLessThanSegment"),
        # TSQL allows for whitespace between the parts of a comparison operator
        Sequence(
            Ref("GreaterThanSegment"),
            Ref("EqualsSegment"),
        ),
        Sequence(
            Ref("LessThanSegment"),
            OneOf(
                Ref("EqualsSegment"),
                Ref("GreaterThanSegment"),
            ),
        ),
        Sequence(
            Ref("NotSegment"),
            OneOf(
                Ref("EqualsSegment"),
                Ref("LessThanSegment"),
                Ref("GreaterThanSegment"),
            ),
        ),
    ),
    SingleIdentifierGrammar=OneOf(
        Ref("NakedIdentifierSegment"),
        Ref("QuotedIdentifierSegment"),
        Ref("BracketedIdentifierSegment"),
        Ref("HashIdentifierSegment"),
        Ref("ParameterNameSegment"),
        Ref("VariableIdentifierSegment"),
    ),
    LiteralGrammar=OneOf(
        Ref("QuotedLiteralSegment"),
        Ref("QuotedLiteralSegmentWithN"),
        Ref("NumericLiteralSegment"),
        Ref("BooleanLiteralGrammar"),
        Ref("QualifiedNumericLiteralSegment"),
        # NB: Null is included in the literals, because it is a keyword which
        # can otherwise be easily mistaken for an identifier.
        Ref("NullLiteralSegment"),
        Ref("DateTimeLiteralGrammar"),
    ),
    ParameterNameSegment=RegexParser(
        r"[@][A-Za-z0-9_]+", CodeSegment, name="parameter", type="parameter"
    ),
    FunctionNameIdentifierSegment=RegexParser(
        r"[A-Z][A-Z0-9_]*|\[[A-Z][A-Z0-9_]*\]",
        CodeSegment,
        name="function_name_identifier",
        type="function_name_identifier",
    ),
    DatatypeIdentifierSegment=Ref("SingleIdentifierGrammar"),
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
    # Overriding SelectClauseSegmentGrammar to remove Delimited logic which assumes statements have been delimited
    SelectClauseSegmentGrammar=Sequence(
        "SELECT",
        Ref("SelectClauseModifierSegment", optional=True),
        Indent,
        AnyNumberOf(
            Sequence(
                Ref("SelectClauseElementSegment"),
                Ref("CommaSegment"),
            ),
        ),
        Ref("SelectClauseElementSegment"),
        # NB: The Dedent for the indent above lives in the
        # SelectStatementSegment so that it sits in the right
        # place corresponding to the whitespace.
    ),
    FromClauseTerminatorGrammar=OneOf(
        "WHERE",
        "LIMIT",
        Sequence("GROUP", "BY"),
        Sequence("ORDER", "BY"),
        "HAVING",
        "PIVOT",
        "UNPIVOT",
        Ref("SetOperatorSegment"),
        Ref("WithNoSchemaBindingClauseSegment"),
        Ref("DelimiterSegment"),
    ),
    JoinKeywords=OneOf("JOIN", "APPLY", Sequence("OUTER", "APPLY")),
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
                    ephemeral_name="BracketedExpression",
                ),
            ),
            # Allow potential select statement without brackets
            Ref("SelectStatementSegment"),
            Ref("LiteralGrammar"),
            Ref("IntervalExpressionSegment"),
            Ref("ColumnReferenceSegment"),
            Sequence(
                Ref("SimpleArrayTypeGrammar", optional=True), Ref("ArrayLiteralSegment")
            ),
        ),
        Ref("Accessor_Grammar", optional=True),
        allow_gaps=True,
    ),
)


@tsql_dialect.segment(replace=True)
class StatementSegment(ansi_dialect.get_segment("StatementSegment")):  # type: ignore
    """Overriding StatementSegment to allow for additional segment parsing."""

    match_grammar = ansi_dialect.get_segment("StatementSegment").parse_grammar.copy(
        insert=[
            Ref("IfExpressionStatement"),
            Ref("DeclareStatementSegment"),
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
            Ref("DropFunctionStatementSegment"),
            Ref("BeginEndSegment"),
            Ref("TryCatchSegment"),
            Ref("MergeStatementSegment"),
        ],
    )

    parse_grammar = match_grammar


@tsql_dialect.segment(replace=True)
class SelectClauseElementSegment(BaseSegment):
    """An element in the targets of a select statement.

    Overriding ANSI to remove GreedyUntil logic which assumes statements have been delimited
    """

    type = "select_clause_element"
    # Important to split elements before parsing, otherwise debugging is really hard.
    match_grammar = OneOf(
        # *, blah.*, blah.blah.*, etc.
        Ref("WildcardExpressionSegment"),
        Sequence(
            Ref("BaseExpressionElementGrammar"),
            Ref("AliasExpressionSegment", optional=True),
        ),
    )


@tsql_dialect.segment(replace=True)
class SelectClauseModifierSegment(BaseSegment):
    """Things that come after SELECT but before the columns."""

    type = "select_clause_modifier"
    match_grammar = OneOf(
        "DISTINCT",
        "ALL",
        Sequence(
            "TOP",
            OptionallyBracketed(Ref("ExpressionSegment")),
            Sequence("PERCENT", optional=True),
            Sequence("WITH", "TIES", optional=True),
        ),
    )


@tsql_dialect.segment(replace=True)
class SelectClauseSegment(BaseSegment):
    """A group of elements in a select target statement.

    Overriding ANSI to remove StartsWith logic which assumes statements have been delimited
    """

    type = "select_clause"
    match_grammar = Ref("SelectClauseSegmentGrammar")


@tsql_dialect.segment(replace=True)
class UnorderedSelectStatementSegment(BaseSegment):
    """A `SELECT` statement without any ORDER clauses or later.

    We need to change ANSI slightly to remove LimitClauseSegment
    and NamedWindowSegment which don't exist in T-SQL.

    We also need to get away from ANSI's use of StartsWith.
    There's not a clean list of terminators that can be used
    to identify the end of a TSQL select statement.  Semi-colon is optional.
    """

    type = "select_statement"
    match_grammar = Sequence(
        Ref("SelectClauseSegment"),
        # Dedent for the indent in the select clause.
        # It's here so that it can come AFTER any whitespace.
        Dedent,
        Ref("IntoTableSegment", optional=True),
        Ref("FromClauseSegment", optional=True),
        Ref("PivotUnpivotStatementSegment", optional=True),
        Ref("WhereClauseSegment", optional=True),
        Ref("GroupByClauseSegment", optional=True),
        Ref("HavingClauseSegment", optional=True),
    )


@tsql_dialect.segment(replace=True)
class InsertStatementSegment(BaseSegment):
    """An `INSERT` statement.

    Overriding ANSI definition to remove StartsWith logic that doesn't handle optional delimitation well.
    """

    type = "insert_statement"
    match_grammar = Sequence(
        "INSERT",
        "INTO",
        Ref("TableReferenceSegment"),
        Ref("BracketedColumnReferenceListGrammar", optional=True),
        Ref("SelectableGrammar"),
    )


@tsql_dialect.segment(replace=True)
class WithCompoundStatementSegment(BaseSegment):
    """A `SELECT` statement preceded by a selection of `WITH` clauses.

    `WITH tab (col1,col2) AS (SELECT a,b FROM x)`

    Overriding ANSI to remove the greedy matching of StartsWith().
    """

    type = "with_compound_statement"
    # match grammar
    match_grammar = Sequence(
        "WITH",
        Ref.keyword("RECURSIVE", optional=True),
        Delimited(
            Ref("CTEDefinitionSegment"),
            terminator=Ref.keyword("SELECT"),
        ),
        OneOf(
            Ref("NonWithSelectableGrammar"),
            Ref("NonWithNonSelectableGrammar"),
            Ref("MergeStatementSegment"),
        ),
    )


@tsql_dialect.segment(replace=True)
class SelectStatementSegment(BaseSegment):
    """A `SELECT` statement.

    We need to change ANSI slightly to remove LimitClauseSegment
    and NamedWindowSegment which don't exist in T-SQL.

    We also need to get away from ANSI's use of StartsWith.
    There's not a clean list of terminators that can be used
    to identify the end of a TSQL select statement.  Semi-colon is optional.
    """

    type = "select_statement"
    # Remove the Limit and Window statements from ANSI
    match_grammar = UnorderedSelectStatementSegment.match_grammar.copy(
        insert=[
            Ref("OrderByClauseSegment", optional=True),
            Ref("OptionClauseSegment", optional=True),
            Ref("DelimiterSegment", optional=True),
        ]
    )


@tsql_dialect.segment()
class IntoTableSegment(BaseSegment):
    """`INTO` clause within `SELECT`.

    https://docs.microsoft.com/en-us/sql/t-sql/queries/select-into-clause-transact-sql?view=sql-server-ver15
    """

    type = "into_table_clause"
    match_grammar = Sequence("INTO", Ref("ObjectReferenceSegment"))


@tsql_dialect.segment(replace=True)
class WhereClauseSegment(BaseSegment):
    """A `WHERE` clause like in `SELECT` or `INSERT`.

    Overriding ANSI in order to get away from the use of
    StartsWith. There's not a clean list of terminators that can be used
    to identify the end of a TSQL select statement.  Semi-colon is optional.
    """

    type = "where_clause"
    match_grammar = Sequence(
        "WHERE",
        Indent,
        OptionallyBracketed(Ref("ExpressionSegment")),
        Dedent,
    )


@tsql_dialect.segment(replace=True)
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
        Ref("DelimiterSegment", optional=True),
    )


@tsql_dialect.segment()
class OnPartitionOrFilegroupOptionSegment(BaseSegment):
    """ON partition scheme or filegroup option in `CREATE INDEX` and 'CREATE TABLE' statements.

    https://docs.microsoft.com/en-us/sql/t-sql/statements/create-index-transact-sql?view=sql-server-ver15
    https://docs.microsoft.com/en-us/sql/t-sql/statements/create-table-transact-sql?view=sql-server-ver15
    """

    type = "on_partition_or_filegroup_statement"
    match_grammar = OneOf(
        Ref("PartitionSchemeClause"),
        Ref("FilegroupClause"),
        Ref("LiteralGrammar"),  # for "default" value
    )


@tsql_dialect.segment()
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


@tsql_dialect.segment()
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


@tsql_dialect.segment()
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
            "DELETE",
            OneOf(
                Sequence("NO", "ACTION"),
                "CASCADE",
                Sequence("SET", "NULL"),
                Sequence("SET", "DEFAULT"),
            ),
            optional=True,
        ),
        Sequence(
            "ON",
            "UPDATE",
            OneOf(
                Sequence("NO", "ACTION"),
                "CASCADE",
                Sequence("SET", "NULL"),
                Sequence("SET", "DEFAULT"),
            ),
            optional=True,
        ),
        Sequence("NOT", "FOR", "REPLICATION", optional=True),
    )


@tsql_dialect.segment()
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


@tsql_dialect.segment()
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
                                                delimiter=Ref("CommaSegment"),
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
                delimiter=Ref("CommaSegment"),
            ),
        ),
    )


@tsql_dialect.segment()
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


@tsql_dialect.segment(replace=True)
class DropIndexStatementSegment(BaseSegment):
    """A `DROP INDEX` statement.

    Overriding ANSI to include required ON clause.
    """

    type = "drop_statement"
    match_grammar = Sequence(
        "DROP",
        "INDEX",
        Ref("IfExistsGrammar", optional=True),
        Ref("IndexReferenceSegment"),
        "ON",
        Ref("TableReferenceSegment"),
        Ref("DelimiterSegment", optional=True),
    )


@tsql_dialect.segment()
class DropStatisticsStatementSegment(BaseSegment):
    """A `DROP STATISTICS` statement."""

    type = "drop_statement"
    # DROP INDEX <Index name> [CONCURRENTLY] [IF EXISTS] {RESTRICT | CASCADE}
    match_grammar = Sequence(
        "DROP",
        OneOf("STATISTICS"),
        Ref("IndexReferenceSegment"),
        Ref("DelimiterSegment", optional=True),
    )


@tsql_dialect.segment()
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
        Ref("DelimiterSegment", optional=True),
    )


@tsql_dialect.segment(replace=True)
class ObjectReferenceSegment(BaseSegment):
    """A reference to an object.

    Update ObjectReferenceSegment to only allow dot separated SingleIdentifierGrammar
    So Square Bracketed identifiers can be matched.
    """

    type = "object_reference"
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

    ObjectReferencePart = ansi_dialect.get_segment(
        "ObjectReferenceSegment"
    ).ObjectReferencePart

    _iter_reference_parts = ansi_dialect.get_segment(
        "ObjectReferenceSegment"
    )._iter_reference_parts

    iter_raw_references = ansi_dialect.get_segment(
        "ObjectReferenceSegment"
    ).iter_raw_references

    is_qualified = ansi_dialect.get_segment("ObjectReferenceSegment").is_qualified

    qualification = ansi_dialect.get_segment("ObjectReferenceSegment").qualification

    ObjectReferenceLevel = ansi_dialect.get_segment(
        "ObjectReferenceSegment"
    ).ObjectReferenceLevel

    extract_possible_references = ansi_dialect.get_segment(
        "ObjectReferenceSegment"
    ).extract_possible_references

    _level_to_int = staticmethod(
        ansi_dialect.get_segment("ObjectReferenceSegment")._level_to_int
    )


@tsql_dialect.segment(replace=True)
class TableReferenceSegment(ObjectReferenceSegment):
    """A reference to an table, CTE, subquery or alias.

    Overriding to capture TSQL's override of ObjectReferenceSegment
    """

    type = "table_reference"


@tsql_dialect.segment(replace=True)
class SchemaReferenceSegment(ObjectReferenceSegment):
    """A reference to a schema.

    Overriding to capture TSQL's override of ObjectReferenceSegment
    """

    type = "schema_reference"


@tsql_dialect.segment(replace=True)
class DatabaseReferenceSegment(ObjectReferenceSegment):
    """A reference to a database.

    Overriding to capture TSQL's override of ObjectReferenceSegment
    """

    type = "database_reference"


@tsql_dialect.segment(replace=True)
class IndexReferenceSegment(ObjectReferenceSegment):
    """A reference to an index.

    Overriding to capture TSQL's override of ObjectReferenceSegment
    """

    type = "index_reference"


@tsql_dialect.segment(replace=True)
class ExtensionReferenceSegment(ObjectReferenceSegment):
    """A reference to an extension.

    Overriding to capture TSQL's override of ObjectReferenceSegment
    """

    type = "extension_reference"


@tsql_dialect.segment(replace=True)
class ColumnReferenceSegment(ObjectReferenceSegment):
    """A reference to column, field or alias.

    Overriding to capture TSQL's override of ObjectReferenceSegment
    """

    type = "column_reference"


@tsql_dialect.segment(replace=True)
class SequenceReferenceSegment(ObjectReferenceSegment):
    """A reference to a sequence.

    Overriding to capture TSQL's override of ObjectReferenceSegment
    """

    type = "sequence_reference"


@tsql_dialect.segment()
class PivotColumnReferenceSegment(ObjectReferenceSegment):
    """A reference to a PIVOT column to differentiate it from a regular column reference."""

    type = "pivot_column_reference"


@tsql_dialect.segment()
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


@tsql_dialect.segment()
class DeclareStatementSegment(BaseSegment):
    """Declaration of a variable.

    https://docs.microsoft.com/en-us/sql/t-sql/language-elements/declare-local-variable-transact-sql?view=sql-server-ver15
    """

    type = "declare_segment"
    match_grammar = Sequence(
        "DECLARE",
        Ref("ParameterNameSegment"),
        Sequence("AS", optional=True),
        Ref("DatatypeSegment"),
        Sequence(
            Ref("EqualsSegment"),
            Ref("ExpressionSegment"),
            optional=True,
        ),
        AnyNumberOf(
            Ref("CommaSegment"),
            Ref("ParameterNameSegment"),
            Ref("DatatypeSegment"),
            Sequence(
                Ref("EqualsSegment"),
                Ref("ExpressionSegment"),
                optional=True,
            ),
        ),
        Ref("DelimiterSegment", optional=True),
    )


@tsql_dialect.segment()
class GoStatementSegment(BaseSegment):
    """GO signals the end of a batch of Transact-SQL statements to the SQL Server utilities.

    GO statements are not part of the TSQL language. They are used to signal batch statements
    so that clients know in how batches of statements can be executed.
    """

    type = "go_statement"
    match_grammar = Sequence("GO")


@tsql_dialect.segment(replace=True)
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
        Bracketed(
            OneOf(
                Delimited(Ref("ExpressionSegment")),
                # The brackets might be empty for some cases...
                optional=True,
            ),
            # There may be no brackets for some data types
            optional=True,
        ),
        Ref("CharCharacterSetSegment", optional=True),
    )


@tsql_dialect.segment()
class NextValueSequenceSegment(BaseSegment):
    """Segment to get next value from a sequence."""

    type = "sequence_next_value"
    match_grammar = Sequence(
        "NEXT",
        "VALUE",
        "FOR",
        Ref("ObjectReferenceSegment"),
    )


@tsql_dialect.segment()
class IfExpressionStatement(BaseSegment):
    """IF-ELSE statement.

    https://docs.microsoft.com/en-us/sql/t-sql/language-elements/if-else-transact-sql?view=sql-server-ver15
    """

    type = "if_then_statement"

    match_grammar = Sequence(
        OneOf(
            Sequence(Ref("IfNotExistsGrammar"), Ref("SelectStatementSegment")),
            Sequence(Ref("IfExistsGrammar"), Ref("SelectStatementSegment")),
            Sequence("IF", Ref("ExpressionSegment")),
        ),
        Indent,
        Sequence(
            Ref("StatementSegment"),
            Ref("DelimiterSegment", optional=True),
        ),
        Dedent,
        Sequence(
            "ELSE",
            Indent,
            Sequence(
                Ref("StatementSegment"),
                Ref("DelimiterSegment", optional=True),
            ),
            Dedent,
            optional=True,
        ),
    )


@tsql_dialect.segment(replace=True)
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
                "COLLATE", Ref("ObjectReferenceSegment")
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
                        # ?? Ref('IntervalExpressionSegment')
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
            "AUTO_INCREMENT",  # AUTO_INCREMENT (MySQL) #can be removed as related to mysql and included in ANSI?
            "UNSIGNED",  # UNSIGNED
            Ref("ForeignKeyGrammar"),
            Ref("ReferencesConstraintGrammar"),
            Ref("CheckConstraintGrammar"),
            Ref("CommentClauseSegment"),
            Ref("FilestreamOnOptionSegment", optional=True),
            # column_index
            Sequence(
                "INDEX",
                Ref("ObjectReferenceSegment"),  # index name
                OneOf("CLUSTERED", "NONCLUSTERED", optional=True),
                # other optional blocks (RelationalIndexOptionsSegment, OnIndexOptionSegment,
                # FilestreamOnOptionSegment) are mentioned above
            ),
            # computed_column_definition
            Sequence("AS", Ref("ExpressionSegment")),
            Sequence("PERSISTED", Sequence("NOT", "NULL", optional=True))
            # other optional blocks (RelationalIndexOptionsSegment, OnIndexOptionSegment,
            # ReferencesConstraintGrammar, CheckConstraintGrammar) are mentioned above
        ),
    )


@tsql_dialect.segment(replace=True)
class FunctionParameterListGrammar(BaseSegment):
    """The parameters for a function ie. `(@city_name NVARCHAR(30), @postal_code NVARCHAR(15))`.

    Overriding ANSI (1) to optionally bracket and (2) remove Delimited
    """

    type = "function_parameter_list"
    # Function parameter list
    match_grammar = OptionallyBracketed(
        Ref("FunctionParameterGrammar"),
        AnyNumberOf(
            Ref("CommaSegment"),
            Ref("FunctionParameterGrammar"),
        ),
    )


@tsql_dialect.segment(replace=True)
class CreateFunctionStatementSegment(BaseSegment):
    """A `CREATE FUNCTION` statement.

    This version in the TSQL dialect should be a "common subset" of the
    structure of the code for those dialects.

    Updated to include AS after declaration of RETURNS. Might be integrated in ANSI though.

    postgres: https://www.postgresql.org/docs/9.1/sql-createfunction.html
    snowflake: https://docs.snowflake.com/en/sql-reference/sql/create-function.html
    bigquery: https://cloud.google.com/bigquery/docs/reference/standard-sql/user-defined-functions
    tsql/mssql : https://docs.microsoft.com/en-us/sql/t-sql/statements/create-function-transact-sql?view=sql-server-ver15
    """

    type = "create_function_statement"

    match_grammar = Sequence(
        "CREATE",
        Sequence("OR", "ALTER", optional=True),
        "FUNCTION",
        Anything(),
    )
    parse_grammar = Sequence(
        "CREATE",
        Sequence("OR", "ALTER", optional=True),
        "FUNCTION",
        Ref("ObjectReferenceSegment"),
        Ref("FunctionParameterListGrammar"),
        Sequence(  # Optional function return type
            "RETURNS",
            Ref("DatatypeSegment"),
            optional=True,
        ),
        Ref("FunctionDefinitionGrammar"),
    )


@tsql_dialect.segment()
class DropFunctionStatementSegment(BaseSegment):
    """A `DROP FUNCTION` statement.

    As per specification https://docs.microsoft.com/en-us/sql/t-sql/statements/drop-function-transact-sql?view=sql-server-ver15
    """

    type = "drop_function_statement"

    match_grammar = Sequence(
        "DROP",
        "FUNCTION",
        Ref("IfExistsGrammar", optional=True),
        Delimited(Ref("FunctionNameSegment")),
        Ref("DelimiterSegment", optional=True),
    )


@tsql_dialect.segment()
class SetStatementSegment(BaseSegment):
    """A Set statement.

    Setting an already declared variable or global variable.
    https://docs.microsoft.com/en-us/sql/t-sql/statements/set-statements-transact-sql?view=sql-server-ver15

    https://docs.microsoft.com/en-us/sql/t-sql/language-elements/set-local-variable-transact-sql?view=sql-server-ver15
    """

    type = "set_segment"
    match_grammar = Sequence(
        "SET",
        OneOf(
            Ref("ParameterNameSegment"),
            "DATEFIRST",
            "DATEFORMAT",
            "DEADLOCK_PRIORITY",
            "LOCK_TIMEOUT",
            "CONCAT_NULL_YIELDS_NULL",
            "CURSOR_CLOSE_ON_COMMIT",
            "FIPS_FLAGGER",
            "IDENTITY_INSERT",
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
            Sequence(
                "TRANSACTION",
                "ISOLATION",
                "LEVEL",
            ),
            "XACT_ABORT",
        ),
        OneOf(
            "ON",
            "OFF",
            Sequence(
                Ref("EqualsSegment"),
                Ref("ExpressionSegment"),
            ),
        ),
        Ref("DelimiterSegment", optional=True),
    )


@tsql_dialect.segment(replace=True)
class FunctionDefinitionGrammar(BaseSegment):
    """This is the body of a `CREATE FUNCTION AS` statement.

    Adjusted from ansi as Transact SQL does not seem to have the QuotedLiteralSegmentand Language.
    Futhermore the body can contain almost anything like a function with table output.
    """

    type = "function_statement"
    name = "function_statement"

    match_grammar = Sequence("AS", Sequence(Anything()))


@tsql_dialect.segment()
class CreateProcedureStatementSegment(BaseSegment):
    """A `CREATE OR ALTER PROCEDURE` statement.

    https://docs.microsoft.com/en-us/sql/t-sql/statements/create-procedure-transact-sql?view=sql-server-ver15
    """

    type = "create_procedure_statement"

    match_grammar = Sequence(
        "CREATE",
        Sequence("OR", "ALTER", optional=True),
        OneOf("PROCEDURE", "PROC"),
        Ref("ObjectReferenceSegment"),
        Ref("FunctionParameterListGrammar", optional=True),
        "AS",
        Ref("ProcedureDefinitionGrammar"),
    )


@tsql_dialect.segment()
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
        Ref("DelimiterSegment", optional=True),
    )


@tsql_dialect.segment()
class ProcedureDefinitionGrammar(BaseSegment):
    """This is the body of a `CREATE OR ALTER PROCEDURE AS` statement."""

    type = "procedure_statement"
    name = "procedure_statement"

    match_grammar = AnyNumberOf(
        Sequence(
            Ref("StatementSegment"),
            Ref("DelimiterSegment", optional=True),
        ),
        min_times=1,
    )


@tsql_dialect.segment(replace=True)
class CreateViewStatementSegment(BaseSegment):
    """A `CREATE VIEW` statement.

    Adjusted to allow CREATE OR ALTER instead of CREATE OR REPLACE.
    # https://docs.microsoft.com/en-us/sql/t-sql/statements/create-view-transact-sql?view=sql-server-ver15#examples
    """

    type = "create_view_statement"
    match_grammar = Sequence(
        "CREATE",
        Sequence("OR", "ALTER", optional=True),
        "VIEW",
        Ref("ObjectReferenceSegment"),
        Sequence(
            "WITH",
            Delimited("ENCRYPTION", "SCHEMABINDING", "VIEW_METADATA"),
            optional=True,
        ),
        "AS",
        Ref("SelectableGrammar"),
        Sequence("WITH", "CHECK", "OPTION", optional=True),
        Ref("DelimiterSegment", optional=True),
    )


@tsql_dialect.segment(replace=True)
class IntervalExpressionSegment(BaseSegment):
    """An interval expression segment.

    Not present in T-SQL.
    """

    type = "interval_expression"
    match_grammar = Nothing()


@tsql_dialect.segment(replace=True)
class CreateExtensionStatementSegment(BaseSegment):
    """A `CREATE EXTENSION` statement.

    Not present in T-SQL.
    """

    type = "create_extension_statement"
    match_grammar = Nothing()


@tsql_dialect.segment(replace=True)
class CreateModelStatementSegment(BaseSegment):
    """A BigQuery `CREATE MODEL` statement.

    Not present in T-SQL.
    """

    type = "create_model_statement"
    match_grammar = Nothing()


@tsql_dialect.segment(replace=True)
class DropModelStatementSegment(BaseSegment):
    """A `DROP MODEL` statement.

    Not present in T-SQL.
    """

    type = "drop_MODELstatement"
    match_grammar = Nothing()


@tsql_dialect.segment(replace=True)
class OverlapsClauseSegment(BaseSegment):
    """An `OVERLAPS` clause like in `SELECT.

    Not present in T-SQL.
    """

    type = "overlaps_clause"
    match_grammar = Nothing()


@tsql_dialect.segment()
class ConvertFunctionNameSegment(BaseSegment):
    """CONVERT function name segment.

    Need to be able to specify this as type function_name
    so that linting rules identify it properly
    """

    type = "function_name"
    match_grammar = Sequence("CONVERT")


@tsql_dialect.segment()
class CastFunctionNameSegment(BaseSegment):
    """CAST function name segment.

    Need to be able to specify this as type function_name
    so that linting rules identify it properly
    """

    type = "function_name"
    match_grammar = Sequence("CAST")


@tsql_dialect.segment()
class RankFunctionNameSegment(BaseSegment):
    """Rank function name segment.

    Need to be able to specify this as type function_name
    so that linting rules identify it properly
    """

    type = "function_name"
    match_grammar = OneOf("DENSE_RANK", "NTILE", "RANK", "ROW_NUMBER")


@tsql_dialect.segment()
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


@tsql_dialect.segment()
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
            Bracketed(Ref("PartitionByClause")),
            optional=True,
        ),
    )


@tsql_dialect.segment()
class PartitionByClause(BaseSegment):
    """PARTITION BY clause.

    https://docs.microsoft.com/en-us/sql/t-sql/queries/select-over-clause-transact-sql?view=sql-server-ver15#partition-by
    """

    type = "partition_by_clause"
    match_grammar = Sequence(
        "PARTITION",
        "BY",
        Delimited(
            Ref("ColumnReferenceSegment"),
        ),
    )


@tsql_dialect.segment()
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


@tsql_dialect.segment()
class PartitionSchemeNameSegment(BaseSegment):
    """Partition Scheme Name."""

    type = "partition_scheme_name"
    match_grammar = Ref("SingleIdentifierGrammar")


@tsql_dialect.segment()
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


@tsql_dialect.segment(replace=True)
class FunctionSegment(BaseSegment):
    """A scalar or aggregate function.

    Maybe in the future we should distinguish between
    aggregate functions and other functions. For now
    we treat them the same because they look the same
    for our purposes.
    """

    type = "function"
    match_grammar = OneOf(
        Sequence(
            Ref("DatePartFunctionNameSegment"),
            Bracketed(
                Delimited(
                    Ref("DatePartClause"),
                    Ref(
                        "FunctionContentsGrammar",
                        # The brackets might be empty for some functions...
                        optional=True,
                        ephemeral_name="FunctionContentsGrammar",
                    ),
                )
            ),
        ),
        Sequence(
            Ref("RankFunctionNameSegment"),
            Bracketed(
                Ref("NumericLiteralSegment", optional=True),
            ),
            "OVER",
            Bracketed(
                Ref("PartitionByClause", optional=True),
                Ref("OrderByClauseSegment"),
            ),
        ),
        Sequence(
            Ref("ConvertFunctionNameSegment"),
            Bracketed(
                Delimited(
                    Ref("DatatypeSegment"),
                    Ref(
                        "FunctionContentsGrammar",
                        # The brackets might be empty for some functions...
                        optional=True,
                        ephemeral_name="FunctionContentsGrammar",
                    ),
                )
            ),
        ),
        Sequence(
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
                        ephemeral_name="FunctionContentsGrammar",
                    ),
                ),
            ),
            Ref("WithinGroupClause", optional=True),
        ),
        Sequence(
            OneOf(
                Ref("FunctionNameSegment"),
                exclude=OneOf(
                    # List of special functions handled differently
                    Ref("CastFunctionNameSegment"),
                    Ref("ConvertFunctionNameSegment"),
                    Ref("DatePartFunctionNameSegment"),
                    Ref("WithinGroupFunctionNameSegment"),
                    Ref("RankFunctionNameSegment"),
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
            Ref("PostFunctionGrammar", optional=True),
        ),
    )


@tsql_dialect.segment(replace=True)
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
                        ),
                        allow_trailing=True,
                    )
                ),
                Ref("CommentClauseSegment", optional=True),
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
        # need to add table options here
        Ref("DelimiterSegment", optional=True),
    )

    parse_grammar = match_grammar


@tsql_dialect.segment(replace=True)
class TableConstraintSegment(BaseSegment):
    """A table constraint, e.g. for CREATE TABLE."""

    # https://docs.microsoft.com/en-us/sql/t-sql/statements/create-table-transact-sql?view=sql-server-ver15

    type = "table_constraint_segment"
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


@tsql_dialect.segment()
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


@tsql_dialect.segment()
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


@tsql_dialect.segment()
class FilegroupNameSegment(BaseSegment):
    """Filegroup Name Segment."""

    type = "filegroup_name"
    match_grammar = Ref("SingleIdentifierGrammar")


@tsql_dialect.segment()
class FilegroupClause(BaseSegment):
    """Filegroup Clause segment.

    https://docs.microsoft.com/en-us/sql/relational-databases/databases/database-files-and-filegroups?view=sql-server-ver15
    """

    type = "filegroup_clause"
    match_grammar = Sequence(
        "ON",
        Ref("FilegroupNameSegment"),
    )


@tsql_dialect.segment()
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


@tsql_dialect.segment()
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


@tsql_dialect.segment()
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


@tsql_dialect.segment()
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


@tsql_dialect.segment()
class TableIndexClause(BaseSegment):
    """`CREATE TABLE` table index clause.

    This is specific to Azure Synapse Analytics.
    """

    type = "table_index_clause"

    match_grammar = Sequence(
        OneOf(
            "HEAP",
            Sequence(
                "CLUSTERED",
                "COLUMNSTORE",
                "INDEX",
            ),
        ),
    )


@tsql_dialect.segment()
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
            Ref("QuotedLiteralSegment"),  # External Table
        ),
    )


@tsql_dialect.segment()
class AlterTableSwitchStatementSegment(BaseSegment):
    """An `ALTER TABLE SWITCH` statement."""

    type = "alter_table_switch_statement"
    # https://docs.microsoft.com/en-us/sql/t-sql/statements/alter-table-transact-sql?view=sql-server-ver15
    # T-SQL's ALTER TABLE SWITCH grammar is different enough to core ALTER TABLE grammar to merit its own definition
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
        Ref("DelimiterSegment", optional=True),
    )


@tsql_dialect.segment()
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
        Ref("DelimiterSegment", optional=True),
    )


@tsql_dialect.segment(replace=True)
class DatePartClause(BaseSegment):
    """DatePart clause for use within DATEADD() or related functions."""

    type = "date_part"

    match_grammar = OneOf(
        "D",
        "DAY",
        "DAYOFYEAR",
        "DD",
        "DW",
        "DY",
        "HH",
        "HOUR",
        "M",
        "MCS",
        "MI",
        "MICROSECOND",
        "MILLISECOND",
        "MINUTE",
        "MM",
        "MONTH",
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
        "WEEKDAY",
        "WK",
        "WW",
        "YEAR",
        "Y",
        "YY",
        "YYYY",
    )


@tsql_dialect.segment(replace=True)
class TransactionStatementSegment(BaseSegment):
    """A `COMMIT`, `ROLLBACK` or `TRANSACTION` statement."""

    type = "transaction_statement"
    match_grammar = OneOf(
        # BEGIN | SAVE TRANSACTION
        # COMMIT [ TRANSACTION | WORK ]
        # ROLLBACK [ TRANSACTION | WORK ]
        # https://docs.microsoft.com/en-us/sql/t-sql/language-elements/begin-transaction-transact-sql?view=sql-server-ver15
        Sequence(
            "BEGIN",
            Sequence("DISTRIBUTED", optional=True),
            "TRANSACTION",
            Ref("SingleIdentifierGrammar", optional=True),
            Sequence("WITH", "MARK", Ref("QuotedIdentifierSegment"), optional=True),
            Ref("DelimiterSegment", optional=True),
        ),
        Sequence(
            OneOf("COMMIT", "ROLLBACK"),
            OneOf("TRANSACTION", "WORK", optional=True),
            Ref("DelimiterSegment", optional=True),
        ),
        Sequence("SAVE", "TRANSACTION", Ref("DelimiterSegment", optional=True)),
    )


@tsql_dialect.segment()
class BeginEndSegment(BaseSegment):
    """A `BEGIN/END` block.

    Encloses multiple statements into a single statement object.
    https://docs.microsoft.com/en-us/sql/t-sql/language-elements/begin-end-transact-sql?view=sql-server-ver15
    """

    type = "begin_end_block"
    match_grammar = Sequence(
        "BEGIN",
        Ref("DelimiterSegment", optional=True),
        Indent,
        AnyNumberOf(
            Ref("StatementSegment"),
            Ref("DelimiterSegment", optional=True),
            min_times=1,
        ),
        Dedent,
        "END",
    )


@tsql_dialect.segment()
class TryCatchSegment(BaseSegment):
    """A `TRY/CATCH` block pair.

    https://docs.microsoft.com/en-us/sql/t-sql/language-elements/try-catch-transact-sql?view=sql-server-ver15
    """

    type = "try_catch"
    match_grammar = Sequence(
        "BEGIN",
        "TRY",
        Ref("DelimiterSegment", optional=True),
        Indent,
        AnyNumberOf(
            Sequence(
                Ref("StatementSegment"),
                Ref("DelimiterSegment", optional=True),
            ),
            min_times=1,
        ),
        Dedent,
        "END",
        "TRY",
        "BEGIN",
        "CATCH",
        Ref("DelimiterSegment", optional=True),
        Indent,
        AnyNumberOf(
            Sequence(
                Ref("StatementSegment"),
                Ref("DelimiterSegment", optional=True),
            ),
            min_times=1,
        ),
        Dedent,
        "END",
        "CATCH",
    )


@tsql_dialect.segment()
class BatchSegment(BaseSegment):
    """A segment representing a GO batch within a file or script."""

    type = "batch"
    match_grammar = OneOf(
        # Things that can be bundled
        AnyNumberOf(
            Sequence(
                Ref("StatementSegment"),
                Ref("DelimiterSegment", optional=True),
            ),
            min_times=1,
        ),
        # Things that can't be bundled
        Ref("CreateProcedureStatementSegment"),
    )


@tsql_dialect.segment(replace=True)
class FileSegment(BaseFileSegment):
    """A segment representing a whole file or script.

    We override default as T-SQL allows concept of several
    batches of commands separated by GO as well as usual
    semicolon-separated statement lines.

    This is also the default "root" segment of the dialect,
    and so is usually instantiated directly. It therefore
    has no match_grammar.
    """

    # NB: We don't need a match_grammar here because we're
    # going straight into instantiating it directly usually.
    parse_grammar = Delimited(
        Ref("BatchSegment"),
        delimiter=AnyNumberOf(Ref("BatchDelimiterSegment"), min_times=1),
        allow_gaps=True,
        allow_trailing=True,
    )


@tsql_dialect.segment(replace=True)
class DeleteStatementSegment(BaseSegment):
    """A `DELETE` statement.

    https://docs.microsoft.com/en-us/sql/t-sql/statements/delete-transact-sql?view=sql-server-ver15
    Overriding ANSI to remove StartsWith logic which assumes statements have been delimited
    and to allow for Azure Synapse Analytics-specific DELETE statements
    """

    type = "delete_statement"
    # match grammar. This one makes sense in the context of knowing that it's
    # definitely a statement, we just don't know what type yet.
    match_grammar = Sequence(
        "DELETE",
        Ref("TableReferenceSegment", optional=True),  # Azure Synapse Analytics-specific
        Ref("FromClauseSegment"),
        Ref("WhereClauseSegment", optional=True),
        Ref("DelimiterSegment", optional=True),
    )


@tsql_dialect.segment(replace=True)
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

    Overriding ANSI to remove Delimited logic which assumes statements have been delimited
    """

    type = "from_clause"
    match_grammar = Sequence(
        "FROM",
        AnyNumberOf(
            Sequence(
                Ref("FromExpressionSegment"),
                Ref("CommaSegment"),
            ),
        ),
        Ref("FromExpressionSegment"),
        Ref("DelimiterSegment", optional=True),
    )

    get_eventual_aliases = ansi_dialect.get_segment(
        "FromClauseSegment"
    ).get_eventual_aliases


@tsql_dialect.segment(replace=True)
class GroupByClauseSegment(BaseSegment):
    """A `GROUP BY` clause like in `SELECT`.

    Overriding ANSI to remove Delimited logic which assumes statements have been delimited
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


@tsql_dialect.segment(replace=True)
class HavingClauseSegment(BaseSegment):
    """A `HAVING` clause like in `SELECT`.

    Overriding ANSI to remove StartsWith with greedy terminator
    """

    type = "having_clause"
    match_grammar = Sequence(
        "HAVING",
        Indent,
        OptionallyBracketed(Ref("ExpressionSegment")),
        Dedent,
    )


@tsql_dialect.segment(replace=True)
class OrderByClauseSegment(BaseSegment):
    """A `ORDER BY` clause like in `SELECT`.

    Overriding ANSI to remove StartsWith logic which assumes statements have been delimited
    """

    type = "orderby_clause"
    match_grammar = Sequence(
        "ORDER",
        "BY",
        Indent,
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
        AnyNumberOf(
            Sequence(
                Ref("CommaSegment"),
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
        ),
        Dedent,
    )


@tsql_dialect.segment()
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
        Ref("DelimiterSegment", optional=True),
    )


@tsql_dialect.segment(replace=True)
class DropStatementSegment(BaseSegment):
    """A `DROP` statement.

    Overriding ANSI to add optional delimiter.
    """

    type = "drop_statement"
    match_grammar = ansi_dialect.get_segment("DropStatementSegment").match_grammar.copy(
        insert=[
            Ref("DelimiterSegment", optional=True),
        ],
    )


@tsql_dialect.segment(replace=True)
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
        Ref("FromClauseSegment", optional=True),
        Ref("WhereClauseSegment", optional=True),
        Ref("DelimiterSegment", optional=True),
    )


@tsql_dialect.segment(replace=True)
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


@tsql_dialect.segment(replace=True)
class SetClauseSegment(BaseSegment):
    """Set clause.

    Overriding ANSI to allow for ExpressionSegment on the right
    """

    type = "set_clause"

    match_grammar = Sequence(
        Ref("ColumnReferenceSegment"),
        Ref("EqualsSegment"),
        Ref("ExpressionSegment"),
    )


@tsql_dialect.segment(replace=True)
class DatePartFunctionNameSegment(BaseSegment):
    """DATEADD function name segment.

    Override to support DATEDIFF as well
    """

    type = "function_name"
    match_grammar = OneOf("DATEADD", "DATEDIFF", "DATEDIFF_BIG", "DATENAME")


@tsql_dialect.segment()
class PrintStatementSegment(BaseSegment):
    """PRINT statement segment."""

    type = "print_statement"
    match_grammar = Sequence(
        "PRINT",
        Ref("ExpressionSegment"),
        Ref("DelimiterSegment", optional=True),
    )


@tsql_dialect.segment()
class OptionClauseSegment(BaseSegment):
    """Query Hint clause.

    https://docs.microsoft.com/en-us/sql/t-sql/queries/hints-transact-sql-query?view=sql-server-ver15
    """

    type = "option_clause"
    match_grammar = Sequence(
        Sequence("OPTION", optional=True),
        Bracketed(
            Ref("QueryHintSegment"),
            AnyNumberOf(
                Ref("CommaSegment"),
                Ref("QueryHintSegment"),
            ),
        ),
    )


@tsql_dialect.segment()
class QueryHintSegment(BaseSegment):
    """Query Hint segment.

    https://docs.microsoft.com/en-us/sql/t-sql/queries/hints-transact-sql-query?view=sql-server-ver15
    """

    type = "query_hint_segment"
    match_grammar = OneOf(
        Sequence(  # Azure Synapse Analytics specific
            "LABEL",
            Ref("EqualsSegment"),
            Ref("QuotedLiteralSegment"),
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
            OneOf(Ref("QuotedLiteralSegment"), Ref("QuotedLiteralSegmentWithN")),
        ),
        Sequence(
            "TABLE",
            "HINT",
            Ref("ObjectReferenceSegment"),
            Ref("TableHintSegment"),
            AnyNumberOf(
                Ref("CommaSegment"),
                Ref("TableHintSegment"),
            ),
        ),
    )


@tsql_dialect.segment(replace=True)
class PostTableExpressionGrammar(BaseSegment):
    """Table Hint clause.  Overloading the PostTableExpressionGrammar to implement.

    https://docs.microsoft.com/en-us/sql/t-sql/queries/hints-transact-sql-table?view=sql-server-ver15
    """

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


@tsql_dialect.segment()
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
                OneOf(Ref("IndexReferenceSegment"), Ref("NumericLiteralSegment")),
                AnyNumberOf(
                    Ref("CommaSegment"),
                    OneOf(
                        Ref("IndexReferenceSegment"),
                        Ref("NumericLiteralSegment"),
                    ),
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


@tsql_dialect.segment(replace=True)
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
        Ref("DelimiterSegment", optional=True),
    )


@tsql_dialect.segment()
class ExecuteScriptSegment(BaseSegment):
    """`EXECUTE` statement.

    Matching segment name and type from exasol.
    https://docs.microsoft.com/en-us/sql/t-sql/language-elements/execute-transact-sql?view=sql-server-ver15
    """

    type = "execute_script_statement"
    match_grammar = Sequence(
        OneOf("EXEC", "EXECUTE"),
        Ref("ObjectReferenceSegment"),
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
        Ref("DelimiterSegment", optional=True),
    )


@tsql_dialect.segment(replace=True)
class CreateSchemaStatementSegment(BaseSegment):
    """A `CREATE SCHEMA` statement.

    Overriding ANSI to allow for AUTHORIZATION clause
    https://docs.microsoft.com/en-us/sql/t-sql/statements/create-schema-transact-sql?view=sql-server-ver15

    Not yet implemented: proper schema_element parsing.
    Once we have an AccessStatementSegment that works for TSQL, this definition should be tweaked to include schema elements.
    """

    type = "create_schema_statement"
    match_grammar = Sequence(
        "CREATE",
        "SCHEMA",
        Ref("SchemaReferenceSegment"),
        Sequence(
            "AUTHORIZATION",
            Ref("SingleIdentifierGrammar"),
            optional=True,
        ),
        Ref(
            "DelimiterSegment",
            optional=True,
        ),
    )


@tsql_dialect.segment()
class MergeStatementSegment(BaseSegment):
    """`MERGE` statement.

    https://docs.microsoft.com/en-us/sql/t-sql/statements/merge-transact-sql?view=sql-server-ver15
    """

    type = "merge_statement"

    match_grammar = Sequence(
        "MERGE",
        Sequence(
            "TOP",
            OptionallyBracketed(Ref("ExpressionSegment")),
            Sequence("PERCENT", optional=True),
            optional=True,
        ),
        Sequence("INTO", optional=True),
        Indent,
        OneOf(
            Ref("TableReferenceSegment"),
            Ref("AliasedTableReferenceGrammar"),
            Sequence(
                Ref("TableReferenceSegment"),
                Ref("PostTableExpressionGrammar", optional=True),
                Ref("AliasExpressionSegment", optional=True),
            ),
        ),
        Dedent,
        "USING",
        Indent,
        OneOf(
            Sequence(
                Ref("TableReferenceSegment"),
                Ref("AliasExpressionSegment", optional=True),
            ),
            Sequence(
                OptionallyBracketed(
                    Ref("UnorderedSelectStatementSegment"),
                ),
                Ref("AliasExpressionSegment", optional=True),
                Ref("BracketedColumnReferenceListGrammar", optional=True),
            ),
        ),
        Dedent,
        Ref("JoinOnConditionSegment"),
        AnyNumberOf(
            Ref("MergeMatchedClauseSegment"),
            Ref("MergeNotMatchedClauseSegment"),
            min_times=1,
        ),
        Ref("OutputClauseSegment", optional=True),
        Ref("OptionClauseSegment", optional=True),
        AnyNumberOf(Ref("DelimiterSegment"), optional=True),
    )


@tsql_dialect.segment()
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


@tsql_dialect.segment()
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


@tsql_dialect.segment()
class MergeUpdateClauseSegment(BaseSegment):
    """`UPDATE` clause within the `MERGE` statement."""

    type = "merge_update_clause"
    match_grammar = Sequence(
        "UPDATE",
        Ref("SetClauseListSegment"),
    )


@tsql_dialect.segment()
class MergeDeleteClauseSegment(BaseSegment):
    """`DELETE` clause within the `MERGE` statement."""

    type = "merge_delete_clause"
    match_grammar = Sequence(
        "DELETE",
    )


@tsql_dialect.segment()
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


@tsql_dialect.segment()
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
