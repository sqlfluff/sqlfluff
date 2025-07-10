"""The Trino dialect.

See https://trino.io/docs/current/language.html
"""

from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.core.parser import (
    AnyNumberOf,
    AnySetOf,
    Anything,
    BaseSegment,
    Bracketed,
    CodeSegment,
    Dedent,
    Delimited,
    IdentifierSegment,
    Indent,
    LiteralSegment,
    Matchable,
    Nothing,
    OneOf,
    OptionallyBracketed,
    Ref,
    RegexLexer,
    Sequence,
    StringLexer,
    StringParser,
    SymbolSegment,
    TypedParser,
)
from sqlfluff.dialects import dialect_ansi as ansi
from sqlfluff.dialects.dialect_trino_keywords import (
    trino_reserved_keywords,
    trino_unreserved_keywords,
)

ansi_dialect = load_raw_dialect("ansi")
trino_dialect = ansi_dialect.copy_as(
    "trino",
    formatted_name="Trino",
    docstring="""**Default Casing**: ``lowercase``, although the case
of a reference is used in the result set column label. If a column is defined
using :code:`CREATE TEMPORARY TABLE foo (COL1 int)`, then :code:`SELECT * FROM foo`
returns a column labelled :code:`col1`, however :code:`SELECT COL1 FROM foo`
returns a column labelled :code:`COL1`.

**Quotes**: String Literals: ``''``, Identifiers: ``""``

The dialect for `Trino <https://trino.io/docs/current/>`_.""",
)

# Set the bare functions: https://trino.io/docs/current/functions/datetime.html
trino_dialect.sets("bare_functions").update(
    ["current_date", "current_time", "current_timestamp", "localtime", "localtimestamp"]
)

# Set keywords
trino_dialect.sets("unreserved_keywords").clear()
trino_dialect.update_keywords_set_from_multiline_string(
    "unreserved_keywords", trino_unreserved_keywords
)

trino_dialect.sets("reserved_keywords").clear()
trino_dialect.update_keywords_set_from_multiline_string(
    "reserved_keywords", trino_reserved_keywords
)

trino_dialect.insert_lexer_matchers(
    # Regexp Replace w/ Lambda: https://trino.io/docs/422/functions/regexp.html
    [
        StringLexer("right_arrow", "->", CodeSegment),
        StringLexer("fat_right_arrow", "=>", CodeSegment),
    ],
    before="like_operator",
)

trino_dialect.add(
    RightArrowOperator=StringParser("->", SymbolSegment, type="binary_operator"),
    LambdaArrowSegment=StringParser("->", SymbolSegment, type="lambda_arrow"),
    ExecuteArrowSegment=StringParser("=>", SymbolSegment, type="execute_arrow"),
    StartAngleBracketSegment=StringParser(
        "<", SymbolSegment, type="start_angle_bracket"
    ),
    EndAngleBracketSegment=StringParser(">", SymbolSegment, type="end_angle_bracket"),
    FormatJsonEncodingGrammar=Sequence(
        "FORMAT",
        "JSON",
        Sequence("ENCODING", OneOf("UTF8", "UTF16", "UTF32"), optional=True),
    ),
)

trino_dialect.bracket_sets("angle_bracket_pairs").update(
    [
        ("angle", "StartAngleBracketSegment", "EndAngleBracketSegment", False),
    ]
)

trino_dialect.patch_lexer_matchers(
    [
        RegexLexer(
            "double_quote",
            r'"([^"]|"")*"',
            CodeSegment,
            segment_kwargs={
                "quoted_value": (r'"((?:[^"]|"")*)"', 1),
                "escape_replacements": [(r'""', '"')],
            },
        ),
    ]
)

trino_dialect.replace(
    DateTimeLiteralGrammar=OneOf(
        Sequence(
            OneOf("DATE", "TIME", "TIMESTAMP"),
            TypedParser(
                "single_quote", LiteralSegment, type="date_constructor_literal"
            ),
        ),
        Ref("IntervalExpressionSegment"),
    ),
    LikeGrammar=Sequence("LIKE"),
    # TODO: There are no custom SQL functions in Trino! How to handle this?
    MLTableExpressionSegment=Nothing(),
    FromClauseTerminatorGrammar=OneOf(
        "WHERE",
        "LIMIT",
        Sequence("GROUP", "BY"),
        Sequence("ORDER", "BY"),
        "HAVING",
        "WINDOW",
        Ref("SetOperatorSegment"),
        Ref("WithNoSchemaBindingClauseSegment"),
        Ref("WithDataClauseSegment"),
        "FETCH",
    ),
    OrderByClauseTerminators=OneOf(
        "LIMIT",
        "HAVING",
        # For window functions
        "WINDOW",
        Ref("FrameClauseUnitGrammar"),
        "FETCH",
    ),
    SelectClauseTerminatorGrammar=OneOf(
        "FROM",
        "WHERE",
        Sequence("ORDER", "BY"),
        "LIMIT",
        Ref("SetOperatorSegment"),
        "FETCH",
    ),
    WhereClauseTerminatorGrammar=OneOf(
        "LIMIT",
        Sequence("GROUP", "BY"),
        Sequence("ORDER", "BY"),
        "HAVING",
        "WINDOW",
        "FETCH",
    ),
    HavingClauseTerminatorGrammar=OneOf(
        Sequence("ORDER", "BY"),
        "LIMIT",
        "WINDOW",
        "FETCH",
    ),
    GroupByClauseTerminatorGrammar=OneOf(
        Sequence("ORDER", "BY"),
        "LIMIT",
        "HAVING",
        "WINDOW",
        "FETCH",
    ),
    # NOTE: This block was copy/pasted from dialect_ansi.py with these changes made:
    #  - "PRIOR" keyword removed
    Expression_A_Unary_Operator_Grammar=OneOf(
        Ref(
            "SignedSegmentGrammar",
            exclude=Sequence(Ref("QualifiedNumericLiteralSegment")),
        ),
        Ref("TildeSegment"),
        Ref("NotOperatorGrammar"),
    ),
    PostFunctionGrammar=ansi_dialect.get_grammar("PostFunctionGrammar").copy(
        insert=[
            Ref("WithinGroupClauseSegment"),
            Ref("WithOrdinalityClauseSegment"),
        ],
    ),
    FunctionContentsGrammar=AnyNumberOf(
        Ref("ExpressionSegment"),
        # A Cast-like function
        Sequence(Ref("ExpressionSegment"), "AS", Ref("DatatypeSegment")),
        # Trim function
        Sequence(
            Ref("TrimParametersGrammar"),
            Ref("ExpressionSegment", optional=True, exclude=Ref.keyword("FROM")),
            "FROM",
            Ref("ExpressionSegment"),
        ),
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
        Ref(
            "OrderByClauseSegment"
        ),  # used by string_agg (postgres), group_concat (exasol),listagg (snowflake)..
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
        # For JSON_QUERY function
        # https://trino.io/docs/current/functions/json.html#json-query
        Sequence(
            Ref("ExpressionSegment"),  # json_input
            Ref("FormatJsonEncodingGrammar", optional=True),
            Ref("CommaSegment"),
            Ref("ExpressionSegment"),  # json_path
            OneOf(
                Sequence("WITHOUT", Ref.keyword("ARRAY", optional=True), "WRAPPER"),
                Sequence(
                    "WITH",
                    OneOf("CONDITIONAL", "UNCONDITIONAL", optional=True),
                    Ref.keyword("ARRAY", optional=True),
                    "WRAPPER",
                ),
                optional=True,
            ),
        ),
        Ref("IgnoreRespectNullsGrammar"),
        Ref("IndexColumnDefinitionSegment"),
        Ref("EmptyStructLiteralSegment"),
        Ref("ListaggOverflowClauseSegment"),
    ),
    BinaryOperatorGrammar=OneOf(
        Ref("ArithmeticBinaryOperatorGrammar"),
        Ref("StringBinaryOperatorGrammar"),
        Ref("BooleanBinaryOperatorGrammar"),
        Ref("ComparisonOperatorGrammar"),
        # Add arrow operators for functions (e.g. regexp_replace)
        Ref("RightArrowOperator"),
    ),
    AccessorGrammar=AnyNumberOf(
        Ref("ArrayAccessorSegment"),
        # Add in semi structured expressions
        Ref("SemiStructuredAccessorSegment"),
    ),
    # match ANSI's naked identifier casefold, trino is case-insensitive.
    QuotedIdentifierSegment=TypedParser(
        "double_quote", IdentifierSegment, type="quoted_identifier", casefold=str.upper
    ),
    FunctionContentsExpressionGrammar=OneOf(
        Ref("LambdaExpressionSegment"),
        Ref("ExpressionSegment"),
    ),
    TemporaryTransientGrammar=Nothing(),
    PrimaryKeyGrammar=Nothing(),
    ForeignKeyGrammar=Nothing(),
    UniqueKeyGrammar=Nothing(),
    TemporaryGrammar=Nothing(),
)


class DatatypeSegment(BaseSegment):
    """Data type segment.

    See https://trino.io/docs/current/language/types.html
    """

    type = "data_type"
    match_grammar = OneOf(
        # Boolean
        "BOOLEAN",
        # Integer
        "TINYINT",
        "SMALLINT",
        "INTEGER",
        "INT",
        "BIGINT",
        # Floating-point
        "REAL",
        "DOUBLE",
        # Fixed-precision
        Sequence(
            "DECIMAL",
            Ref("BracketedArguments", optional=True),
        ),
        # String
        Sequence(
            OneOf("CHAR", "VARCHAR"),
            Ref("BracketedArguments", optional=True),
        ),
        "VARBINARY",
        "JSON",
        # Date and time
        "DATE",
        Ref("TimeWithTZGrammar"),
        # Structural
        Ref("ArrayTypeSegment"),
        "MAP",
        Ref("RowTypeSegment"),
        # Others
        "IPADDRESS",
        "UUID",
    )


class RowTypeSegment(ansi.StructTypeSegment):
    """Expression to construct a ROW datatype."""

    match_grammar = Sequence(
        "ROW",
        Ref("RowTypeSchemaSegment", optional=True),
    )


class RowTypeSchemaSegment(BaseSegment):
    """Expression to construct the schema of a ROW datatype."""

    type = "struct_type_schema"
    match_grammar = Bracketed(
        Delimited(  # Comma-separated list of field names/types
            Sequence(
                OneOf(
                    # ParameterNames can look like Datatypes so can't use
                    # Optional=True here and instead do a OneOf in order
                    # with DataType only first, followed by both.
                    Ref("DatatypeSegment"),
                    Sequence(
                        Ref("ParameterNameSegment"),
                        Ref("DatatypeSegment"),
                    ),
                )
            )
        )
    )


class SemiStructuredAccessorSegment(BaseSegment):
    """A semi-structured data accessor segment."""

    type = "semi_structured_expression"
    match_grammar = Sequence(
        Ref("DotSegment"),
        Ref("SingleIdentifierGrammar"),
        Ref("ArrayAccessorSegment", optional=True),
        AnyNumberOf(
            Sequence(
                Ref("DotSegment"),
                Ref("SingleIdentifierGrammar"),
                allow_gaps=True,
            ),
            Ref("ArrayAccessorSegment", optional=True),
            allow_gaps=True,
        ),
        allow_gaps=True,
    )


class OverlapsClauseSegment(BaseSegment):
    """An `OVERLAPS` clause like in `SELECT."""

    type = "overlaps_clause"
    match_grammar: Matchable = Nothing()


class UnorderedSelectStatementSegment(ansi.UnorderedSelectStatementSegment):
    """A `SELECT` statement without any ORDER clauses or later."""

    match_grammar: Matchable = Sequence(
        Ref("SelectClauseSegment"),
        Ref("FromClauseSegment", optional=True),
        Ref("WhereClauseSegment", optional=True),
        Ref("GroupByClauseSegment", optional=True),
        Ref("HavingClauseSegment", optional=True),
        Ref("NamedWindowSegment", optional=True),
    )


class ValuesClauseSegment(ansi.ValuesClauseSegment):
    """A `VALUES` clause within in `WITH`, `SELECT`, `INSERT`."""

    match_grammar = Sequence(
        "VALUES",
        Delimited(Ref("ExpressionSegment")),
    )


class IntervalExpressionSegment(BaseSegment):
    """An interval representing a span of time.

    https://trino.io/docs/current/language/types.html#interval-year-to-month
    https://trino.io/docs/current/functions/datetime.html#date-and-time-operators
    """

    type = "interval_expression"
    match_grammar = Sequence(
        "INTERVAL",
        Ref("QuotedLiteralSegment"),
        OneOf("YEAR", "MONTH", "DAY", "HOUR", "MINUTE", "SECOND"),
    )


class FrameClauseSegment(BaseSegment):
    """A frame clause for window functions.

    https://trino.io/blog/2021/03/10/introducing-new-window-features.html
    """

    type = "frame_clause"

    _frame_extent = OneOf(
        Sequence("CURRENT", "ROW"),
        Sequence(
            OneOf(
                Ref("NumericLiteralSegment"), Ref("DateTimeLiteralGrammar"), "UNBOUNDED"
            ),
            OneOf("PRECEDING", "FOLLOWING"),
        ),
    )

    match_grammar: Matchable = Sequence(
        Ref("FrameClauseUnitGrammar"),
        OneOf(_frame_extent, Sequence("BETWEEN", _frame_extent, "AND", _frame_extent)),
    )


class SetOperatorSegment(BaseSegment):
    """A set operator such as Union, Intersect or Except."""

    type = "set_operator"
    match_grammar: Matchable = OneOf(
        Sequence("UNION", OneOf("DISTINCT", "ALL", optional=True)),
        Sequence(
            OneOf(
                "INTERSECT",
                "EXCEPT",
            ),
            Ref.keyword("ALL", optional=True),
        ),
        exclude=Sequence("EXCEPT", Bracketed(Anything())),
    )


class StatementSegment(ansi.StatementSegment):
    """A generic segment, to any of its child subsegments."""

    type = "statement"
    match_grammar: Matchable = OneOf(
        Ref("AlterTableStatementSegment"),
        Ref("AnalyzeStatementSegment"),
        Ref("CommentOnStatementSegment"),
        Ref("CreateFunctionStatementSegment"),
        Ref("CreateRoleStatementSegment"),
        Ref("CreateSchemaStatementSegment"),
        Ref("CreateTableStatementSegment"),
        Ref("CreateViewStatementSegment"),
        Ref("DeleteStatementSegment"),
        Ref("DescribeStatementSegment"),
        Ref("DropFunctionStatementSegment"),
        Ref("DropRoleStatementSegment"),
        Ref("DropSchemaStatementSegment"),
        Ref("DropTableStatementSegment"),
        Ref("DropViewStatementSegment"),
        Ref("ExplainStatementSegment"),
        Ref("InsertStatementSegment"),
        Ref("MergeStatementSegment"),
        Ref("SelectableGrammar"),
        Ref("SetSchemaStatementSegment"),
        Ref("TransactionStatementSegment"),
        Ref("UpdateStatementSegment"),
        Ref("UseStatementSegment"),
        Ref("SetSessionStatementSegment"),
        terminators=[Ref("DelimiterGrammar")],
    )


class AnalyzeStatementSegment(BaseSegment):
    """An 'ANALYZE' statement.

    As per docs https://trino.io/docs/current/sql/analyze.html
    """

    type = "analyze_statement"
    match_grammar = Sequence(
        "ANALYZE",
        Ref("TableReferenceSegment"),
        Sequence(
            "WITH",
            Bracketed(
                Delimited(
                    Sequence(
                        Ref("ParameterNameSegment"),
                        Ref("EqualsSegment"),
                        Ref("ExpressionSegment"),
                    ),
                ),
            ),
            optional=True,
        ),
    )


class WithOrdinalityClauseSegment(BaseSegment):
    """A WITH ORDINALITY AS t(name1, name2) clause for CROSS JOIN UNNEST(...).

    https://trino.io/docs/current/sql/select.html#unnest

    Trino supports an optional WITH ORDINALITY clause on UNNEST, which
    adds a numerical ordinality column to the UNNEST result.
    """

    type = "withordinality_clause"
    match_grammar = Sequence(
        "WITH",
        "ORDINALITY",
    )


class WithinGroupClauseSegment(BaseSegment):
    """An WITHIN GROUP clause for window functions.

    https://trino.io/docs/current/functions/aggregate.html#array_agg

    Trino supports an optional FILTER during aggregation that comes
    immediately after the WITHIN GROUP clause.

    https://trino.io/docs/current/functions/aggregate.html#filtering-during-aggregation
    """

    type = "withingroup_clause"
    match_grammar = Sequence(
        "WITHIN",
        "GROUP",
        Bracketed(Ref("OrderByClauseSegment", optional=False)),
        Ref("FilterClauseGrammar", optional=True),
    )


class ListaggOverflowClauseSegment(BaseSegment):
    """ON OVERFLOW clause of listagg function.

    https://trino.io/docs/current/functions/aggregate.html#array_agg
    """

    type = "listagg_overflow_clause"
    match_grammar = Sequence(
        "ON",
        "OVERFLOW",
        OneOf(
            "ERROR",
            Sequence(
                "TRUNCATE",
                Ref("QuotedLiteralSegment", optional=True),
                OneOf("WITH", "WITHOUT", optional=True),
                Ref.keyword("COUNT", optional=True),
            ),
        ),
    )


class ArrayTypeSegment(ansi.ArrayTypeSegment):
    """Prefix for array literals optionally specifying the type."""

    type = "array_type"
    match_grammar = Sequence(
        "ARRAY",
        Ref("ArrayTypeSchemaSegment", optional=True),
    )


class ArrayTypeSchemaSegment(ansi.ArrayTypeSegment):
    """Data type segment of the array.

    Trino supports ARRAY(DATA_TYPE) and ARRAY<DATA_TYPE>
    """

    type = "array_type_schema"
    match_grammar = OneOf(
        Bracketed(
            Ref("DatatypeSegment"),
            bracket_pairs_set="angle_bracket_pairs",
            bracket_type="angle",
        ),
        Bracketed(
            Ref("DatatypeSegment"),
            bracket_pairs_set="bracket_pairs",
            bracket_type="round",
        ),
    )


class GroupByClauseSegment(BaseSegment):
    """A `GROUP BY` clause like in `SELECT`."""

    type = "groupby_clause"

    match_grammar: Matchable = Sequence(
        "GROUP",
        "BY",
        Indent,
        OneOf(
            "ALL",
            Ref("CubeRollupClauseSegment"),
            # Add GROUPING SETS support
            Ref("GroupingSetsClauseSegment"),
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
        ),
        Dedent,
    )


class CommentOnStatementSegment(BaseSegment):
    """`COMMENT ON` statement.

    https://trino.io/docs/current/sql/comment.html
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
                        # TODO: Create a ViewReferenceSegment
                        "VIEW",
                    ),
                    Ref("TableReferenceSegment"),
                ),
                Sequence(
                    "COLUMN",
                    # TODO: Does this correctly emit a Table Reference?
                    Ref("ColumnReferenceSegment"),
                ),
            ),
            Sequence("IS", OneOf(Ref("QuotedLiteralSegment"), "NULL")),
        ),
    )


class LambdaExpressionSegment(BaseSegment):
    """Lambda function used in a function."""

    type = "lambda_function"
    match_grammar = Sequence(
        OneOf(
            Ref("ParameterNameSegment"),
            Bracketed(Delimited(Ref("ParameterNameSegment"))),
        ),
        Ref("LambdaArrowSegment"),
        Ref("ExpressionSegment"),
    )


class CreateTableStatementSegment(ansi.CreateTableStatementSegment):
    """A `CREATE TABLE` statement."""

    type = "create_table_statement"
    match_grammar: Matchable = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        "TABLE",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        # Columns and comment syntax:
        Bracketed(
            Delimited(
                Ref("ColumnReferenceSegment"),
                Ref("ColumnDefinitionSegment"),
                Sequence(
                    "LIKE",
                    Ref("TableReferenceSegment"),
                    Sequence(
                        OneOf("INCLUDING", "EXCLUDING"),
                        "PROPERTIES",
                        optional=True,
                    ),
                ),
            ),
            optional=True,
        ),
        Ref("CommentClauseSegment", optional=True),
        Sequence(
            "WITH",
            Bracketed(
                Delimited(
                    Ref("ParameterNameSegment"),
                    Ref("EqualsSegment"),
                    Ref("ExpressionSegment"),
                ),
            ),
            optional=True,
        ),
        # Create AS syntax:
        Sequence(
            "AS",
            OptionallyBracketed(Ref("SelectableGrammar")),
            optional=True,
        ),
        # Create like syntax
        Sequence("WITH", Ref.keyword("NO", optional=True), "DATA", optional=True),
    )


class ColumnDefinitionSegment(ansi.ColumnDefinitionSegment):
    """A column definition, e.g. for CREATE TABLE or ALTER TABLE."""

    type = "column_definition"
    match_grammar: Matchable = Sequence(
        Ref("SingleIdentifierGrammar"),  # Column name
        Ref("DatatypeSegment"),  # Column type
        AnySetOf(
            Sequence(
                "NOT",
                "NULL",
            ),
            Ref("CommentClauseSegment"),
            Sequence(
                "WITH",
                Bracketed(
                    Delimited(
                        Ref("ParameterNameSegment"),
                        Ref("EqualsSegment"),
                        Ref("ExpressionSegment"),
                    ),
                ),
            ),
        ),
    )


class TransactionStatementSegment(ansi.TransactionStatementSegment):
    """A `COMMIT`, `ROLLBACK` or `TRANSACTION` statement.

    https://trino.io/docs/current/sql/commit.html
    https://trino.io/docs/current/sql/rollback.html
    https://trino.io/docs/current/sql/start-transaction.html
    """

    type = "transaction_statement"
    match_grammar: Matchable = OneOf(
        Sequence(
            "COMMIT",
            Ref.keyword("WORK", optional=True),
        ),
        Sequence(
            "ROLLBACK",
            Ref.keyword("WORK", optional=True),
        ),
        Sequence(
            "START",
            "TRANSACTION",
            Delimited(
                Sequence(
                    "ISOLATION",
                    "LEVEL",
                    OneOf(
                        Sequence("READ", "UNCOMMITTED"),
                        Sequence("READ", "COMMITTED"),
                        Sequence("REPEATABLE", "READ"),
                        "SERIALIZABLE",
                    ),
                ),
                Sequence(
                    "READ",
                    OneOf("ONLY", "WRITE"),
                ),
                optional=True,
            ),
        ),
    )


class InsertStatementSegment(ansi.InsertStatementSegment):
    """An `INSERT` statement.

    https://trino.io/docs/current/sql/insert.html
    """

    type = "insert_statement"
    match_grammar: Matchable = Sequence(
        "INSERT",
        "INTO",
        Ref("TableReferenceSegment"),
        OneOf(
            Ref("SelectableGrammar"),
            Sequence(
                Ref("BracketedColumnReferenceListGrammar"),
                Ref("SelectableGrammar"),
            ),
            Ref("DefaultValuesGrammar"),
        ),
    )


class SetSessionStatementSegment(BaseSegment):
    """A `SET SESSION` statement.

    https://trino.io/docs/current/sql/set-session.html
    """

    type = "set_session_statement"
    match_grammar: Matchable = Sequence(
        "SET",
        "SESSION",
        Sequence(
            Ref("ParameterNameSegment"),
            Ref("DotSegment"),
            optional=True,
        ),
        Ref("ParameterNameSegment"),
        Ref("EqualsSegment"),
        Ref("ExpressionSegment"),
    )


class AlterTableStatementSegment(ansi.AlterTableStatementSegment):
    """A `ALTER TABLE` statement.

    https://trino.io/docs/current/sql/alter-table.html
    """

    match_grammar = Sequence(
        "ALTER",
        "TABLE",
        Ref("IfExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        OneOf(
            Sequence(
                "RENAME",
                "TO",
                Ref("TableReferenceSegment"),
            ),
            Sequence(
                "ADD",
                "COLUMN",
                Ref("IfNotExistsGrammar", optional=True),
                Ref("ColumnDefinitionSegment"),
                OneOf(
                    "FIRST",
                    "LAST",
                    Sequence(
                        "AFTER",
                        Ref("ColumnReferenceSegment"),
                    ),
                    optional=True,
                ),
            ),
            Sequence(
                "DROP",
                "COLUMN",
                Ref("IfExistsGrammar", optional=True),
                Ref("ColumnReferenceSegment"),
            ),
            Sequence(
                "RENAME",
                "COLUMN",
                Ref("IfExistsGrammar", optional=True),
                Ref("ColumnReferenceSegment"),
                "TO",
                Ref("ColumnReferenceSegment"),
            ),
            Sequence(
                "ALTER",
                "COLUMN",
                Ref("ColumnReferenceSegment"),
                OneOf(
                    Sequence(
                        "SET",
                        "DATA",
                        "TYPE",
                        Ref("DatatypeSegment"),
                    ),
                    Sequence(
                        "DROP",
                        "NOT",
                        "NULL",
                    ),
                ),
            ),
            Sequence(
                "SET",
                "AUTHORIZATION",
                OneOf(
                    Ref("RoleReferenceSegment"),
                    Sequence(
                        "USER",
                        Ref("RoleReferenceSegment"),
                    ),
                    Sequence(
                        "ROLE",
                        Ref("RoleReferenceSegment"),
                    ),
                ),
            ),
            Sequence(
                "SET",
                "PROPERTIES",
                Delimited(
                    Sequence(
                        Ref("ParameterNameSegment"),
                        Ref("EqualsSegment"),
                        Ref("ExpressionSegment"),
                    ),
                ),
            ),
            Sequence(
                "EXECUTE",
                Ref("FunctionNameSegment"),
                Bracketed(
                    Delimited(
                        Sequence(
                            Ref("ParameterNameSegment"),
                            Ref("ExecuteArrowSegment"),
                            Ref("ExpressionSegment"),
                        ),
                    ),
                    optional=True,
                ),
                Sequence(
                    "WHERE",
                    Ref("ExpressionSegment"),
                    optional=True,
                ),
            ),
        ),
    )
