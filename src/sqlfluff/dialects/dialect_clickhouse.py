"""The clickhouse dialect.

https://clickhouse.com/
"""

from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.core.parser import (
    AnyNumberOf,
    AnySetOf,
    BaseSegment,
    Bracketed,
    CodeSegment,
    Conditional,
    Dedent,
    Delimited,
    IdentifierSegment,
    ImplicitIndent,
    Indent,
    LiteralSegment,
    Matchable,
    Nothing,
    OneOf,
    OptionallyBracketed,
    ParseMode,
    Ref,
    RegexLexer,
    RegexParser,
    SegmentGenerator,
    Sequence,
    StringLexer,
    StringParser,
    SymbolSegment,
    TypedParser,
)
from sqlfluff.dialects import dialect_ansi as ansi
from sqlfluff.dialects.dialect_clickhouse_keywords import (
    FORMAT_KEYWORDS,
    UNRESERVED_KEYWORDS,
)

ansi_dialect = load_raw_dialect("ansi")

clickhouse_dialect = ansi_dialect.copy_as(
    "clickhouse",
    formatted_name="ClickHouse",
    docstring="""**Default Casing**: Clickhouse is case sensitive throughout,
regardless of quoting. An unquoted reference to an object using the wrong
case will raise an :code:`UNKNOWN_IDENTIFIER` error.

**Quotes**: String Literals: ``''``, Identifiers: ``""`` or |back_quotes|.
Note as above, that because identifiers are always resolved case sensitively, the
only reason for quoting identifiers is when they contain invalid characters or
reserved keywords.

The dialect for `ClickHouse <https://clickhouse.com/>`_.""",
)
clickhouse_dialect.sets("unreserved_keywords").update(UNRESERVED_KEYWORDS)

clickhouse_dialect.insert_lexer_matchers(
    # https://clickhouse.com/docs/en/sql-reference/functions#higher-order-functions---operator-and-lambdaparams-expr-function
    [StringLexer("lambda", r"->", SymbolSegment)],
    before="newline",
)

clickhouse_dialect.patch_lexer_matchers(
    [
        RegexLexer(
            "double_quote",
            r'"([^"\\]|""|\\.)*"',
            CodeSegment,
            segment_kwargs={
                "quoted_value": (r'"((?:[^"\\]|""|\\.)*)"', 1),
                "escape_replacements": [(r'(""|\\")', '"')],
            },
        ),
        RegexLexer(
            "back_quote",
            r"`(?:[^`\\]|``|\\.)*`",
            CodeSegment,
            segment_kwargs={
                "quoted_value": (r"`((?:[^`\\]|``|\\.)*)`", 1),
                "escape_replacements": [(r"(``|\\`)", "`")],
            },
        ),
    ]
)

clickhouse_dialect.add(
    BackQuotedIdentifierSegment=TypedParser(
        "back_quote",
        IdentifierSegment,
        type="quoted_identifier",
    ),
    LambdaFunctionSegment=TypedParser("lambda", SymbolSegment, type="lambda"),
)

clickhouse_dialect.replace(
    BinaryOperatorGrammar=OneOf(
        Ref("ArithmeticBinaryOperatorGrammar"),
        Ref("StringBinaryOperatorGrammar"),
        Ref("BooleanBinaryOperatorGrammar"),
        Ref("ComparisonOperatorGrammar"),
        # Add Lambda Function
        Ref("LambdaFunctionSegment"),
    ),
    # https://clickhouse.com/docs/en/sql-reference/statements/select/join/#supported-types-of-join
    JoinTypeKeywordsGrammar=Sequence(
        Ref.keyword("GLOBAL", optional=True),
        OneOf(
            # This case INNER [ANY,ALL] JOIN
            Sequence("INNER", OneOf("ALL", "ANY", optional=True)),
            # This case [ANY,ALL] INNER JOIN
            Sequence(OneOf("ALL", "ANY", optional=True), "INNER"),
            # This case FULL ALL OUTER JOIN
            Sequence(
                "FULL",
                Ref.keyword("ALL", optional=True),
                Ref.keyword("OUTER", optional=True),
            ),
            # This case ALL FULL OUTER JOIN
            Sequence(
                Ref.keyword("ALL", optional=True),
                "FULL",
                Ref.keyword("OUTER", optional=True),
            ),
            # This case LEFT [OUTER,ANTI,SEMI,ANY,ASOF] JOIN
            Sequence(
                "LEFT",
                OneOf(
                    "ANTI",
                    "SEMI",
                    OneOf("ANY", "ALL", optional=True),
                    "ASOF",
                    optional=True,
                ),
                Ref.keyword("OUTER", optional=True),
            ),
            # This case [ANTI,SEMI,ANY,ASOF] LEFT JOIN
            Sequence(
                OneOf(
                    "ANTI",
                    "SEMI",
                    OneOf("ANY", "ALL", optional=True),
                    "ASOF",
                ),
                "LEFT",
            ),
            # This case RIGHT [OUTER,ANTI,SEMI,ANY,ASOF] JOIN
            Sequence(
                "RIGHT",
                OneOf(
                    "OUTER",
                    "ANTI",
                    "SEMI",
                    OneOf("ANY", "ALL", optional=True),
                    optional=True,
                ),
                Ref.keyword("OUTER", optional=True),
            ),
            # This case [OUTER,ANTI,SEMI,ANY] RIGHT JOIN
            Sequence(
                OneOf(
                    "ANTI",
                    "SEMI",
                    OneOf("ANY", "ALL", optional=True),
                    optional=True,
                ),
                "RIGHT",
            ),
            # This case ASOF JOIN
            "ASOF",
            # This case ANY JOIN
            "ANY",
            # This case ALL JOIN
            "ALL",
        ),
    ),
    JoinUsingConditionGrammar=Sequence(
        "USING",
        Conditional(Indent, indented_using_on=False),
        Delimited(
            OneOf(
                Bracketed(
                    Delimited(Ref("SingleIdentifierGrammar")),
                    parse_mode=ParseMode.GREEDY,
                ),
                Delimited(Ref("SingleIdentifierGrammar")),
            ),
        ),
        Conditional(Dedent, indented_using_on=False),
    ),
    ConditionalCrossJoinKeywordsGrammar=Nothing(),
    UnconditionalCrossJoinKeywordsGrammar=Sequence(
        Ref.keyword("GLOBAL", optional=True),
        Ref.keyword("CROSS"),
    ),
    HorizontalJoinKeywordsGrammar=Sequence(
        Ref.keyword("GLOBAL", optional=True),
        Ref.keyword("PASTE"),
    ),
    NaturalJoinKeywordsGrammar=Nothing(),
    JoinLikeClauseGrammar=Sequence(
        AnyNumberOf(
            Ref("ArrayJoinClauseSegment"),
            min_times=1,
        ),
        Ref("AliasExpressionSegment", optional=True),
    ),
    QuotedLiteralSegment=OneOf(
        TypedParser(
            "single_quote",
            LiteralSegment,
            type="quoted_literal",
        ),
        TypedParser(
            "dollar_quote",
            LiteralSegment,
            type="quoted_literal",
        ),
    ),
    # Drop casefold from ANSI, clickhouse is always case sensitive, even when
    # unquoted.
    NakedIdentifierSegment=SegmentGenerator(
        # Generate the anti template from the set of reserved keywords
        lambda dialect: RegexParser(
            r"[a-zA-Z_][0-9a-zA-Z_]*",
            IdentifierSegment,
            type="naked_identifier",
            anti_template=r"^(" + r"|".join(dialect.sets("reserved_keywords")) + r")$",
        )
    ),
    SingleIdentifierGrammar=OneOf(
        Ref("NakedIdentifierSegment"),
        Ref("QuotedIdentifierSegment"),
        Ref("SingleQuotedIdentifierSegment"),
        Ref("BackQuotedIdentifierSegment"),
    ),
    InOperatorGrammar=Sequence(
        Ref.keyword("GLOBAL", optional=True),
        Ref.keyword("NOT", optional=True),
        "IN",
        OneOf(
            Ref("FunctionSegment"),  # E.g. IN tuple(1, 2)
            Ref("ArrayLiteralSegment"),  # E.g. IN [1, 2]
            Ref("TupleSegment"),  # E.g. IN (1, 2)
            Ref("SingleIdentifierGrammar"),  # E.g. IN TABLE, IN CTE
            Bracketed(
                OneOf(
                    Delimited(
                        Ref("Expression_A_Grammar"),
                    ),
                    Ref("SelectableGrammar"),
                ),
                parse_mode=ParseMode.GREEDY,
            ),
        ),
    ),
    SelectClauseTerminatorGrammar=ansi_dialect.get_grammar(
        "SelectClauseTerminatorGrammar"
    ).copy(
        insert=[
            Ref.keyword("PREWHERE"),
            Ref.keyword("INTO"),
            Ref.keyword("FORMAT"),
        ],
        before=Ref.keyword("WHERE"),
    ),
    FromClauseTerminatorGrammar=ansi_dialect.get_grammar("FromClauseTerminatorGrammar")
    .copy(
        insert=[
            Ref.keyword("PREWHERE"),
            Ref.keyword("INTO"),
            Ref.keyword("FORMAT"),
        ],
        before=Ref.keyword("WHERE"),
    )
    .copy(insert=[Ref("SettingsClauseSegment")]),
    DateTimeLiteralGrammar=Sequence(
        OneOf("DATE", "TIME", "TIMESTAMP"),
        TypedParser("single_quote", LiteralSegment, type="date_constructor_literal"),
    ),
    AlterTableDropColumnGrammar=Sequence(
        Ref("OnClusterClauseSegment", optional=True),
        "DROP",
        Ref.keyword("COLUMN"),
        Ref("IfExistsGrammar", optional=True),
        Ref("SingleIdentifierGrammar"),
    ),
)

# Set the datetime units
clickhouse_dialect.sets("datetime_units").clear()
clickhouse_dialect.sets("datetime_units").update(
    [
        # https://github.com/ClickHouse/ClickHouse/blob/1cdccd527f0cbf5629b21d29970e28d5156003dc/src/Parsers/parseIntervalKind.cpp#L8
        "NANOSECOND",
        "NANOSECONDS",
        "SQL_TSI_NANOSECOND",
        "NS",
        "MICROSECOND",
        "MICROSECONDS",
        "SQL_TSI_MICROSECOND",
        "MCS",
        "MILLISECOND",
        "MILLISECONDS",
        "SQL_TSI_MILLISECOND",
        "MS",
        "SECOND",
        "SECONDS",
        "SQL_TSI_SECOND",
        "SS",
        "S",
        "MINUTE",
        "MINUTES",
        "SQL_TSI_MINUTE",
        "MI",
        "N",
        "HOUR",
        "HOURS",
        "SQL_TSI_HOUR",
        "HH",
        "H",
        "DAY",
        "DAYS",
        "SQL_TSI_DAY",
        "DD",
        "D",
        "WEEK",
        "WEEKS",
        "SQL_TSI_WEEK",
        "WK",
        "WW",
        "MONTH",
        "MONTHS",
        "SQL_TSI_MONTH",
        "MM",
        "M",
        "QUARTER",
        "QUARTERS",
        "SQL_TSI_QUARTER",
        "QQ",
        "Q",
        "YEAR",
        "YEARS",
        "SQL_TSI_YEAR",
        "YYYY",
        "YY",
    ]
)


class IntoOutfileClauseSegment(BaseSegment):
    """An `INTO OUTFILE` clause like in `SELECT`."""

    type = "into_outfile_clause"
    match_grammar: Matchable = Sequence(
        "INTO",
        "OUTFILE",
        Ref("QuotedLiteralSegment"),
        Ref("FormatClauseSegment", optional=True),
    )


class FormatClauseSegment(BaseSegment):
    """A `FORMAT` clause like in `SELECT`."""

    type = "format_clause"
    match_grammar: Matchable = Sequence(
        "FORMAT",
        OneOf(*[Ref.keyword(allowed_format) for allowed_format in FORMAT_KEYWORDS]),
        Ref("SettingsClauseSegment", optional=True),
    )


class MergeTreesOrderByClauseSegment(BaseSegment):
    """A `ORDER BY` clause for the MergeTree family engine."""

    type = "merge_tree_order_by_clause"
    match_grammar: Matchable = Sequence(
        "ORDER",
        "BY",
        OneOf(
            Sequence(
                "TUPLE",
                Bracketed(),  # tuple() not tuple
            ),
            Bracketed(
                Delimited(
                    Ref("ColumnReferenceSegment"),
                    Ref("ExpressionSegment"),
                ),
            ),
            Ref("ColumnReferenceSegment"),
        ),
    )


class PreWhereClauseSegment(BaseSegment):
    """A `PREWHERE` clause like in `SELECT` or `INSERT`."""

    type = "prewhere_clause"
    match_grammar: Matchable = Sequence(
        "PREWHERE",
        # NOTE: The indent here is implicit to allow
        # constructions like:
        #
        #    PREWHERE a
        #        AND b
        #
        # to be valid without forcing an indent between
        # "PREWHERE" and "a".
        ImplicitIndent,
        OptionallyBracketed(Ref("ExpressionSegment")),
        Dedent,
    )


class SettingsClauseSegment(BaseSegment):
    """A `SETTINGS` clause for engines or query-level settings."""

    type = "settings_clause"
    match_grammar: Matchable = Sequence(
        "SETTINGS",
        Delimited(
            Sequence(
                Ref("NakedIdentifierSegment"),
                Ref("EqualsSegment"),
                OneOf(
                    Ref("NakedIdentifierSegment"),
                    Ref("NumericLiteralSegment"),
                    Ref("QuotedLiteralSegment"),
                    Ref("BooleanLiteralGrammar"),
                ),
                optional=True,
            ),
        ),
        optional=True,
    )


class SelectStatementSegment(ansi.SelectStatementSegment):
    """Enhance `SELECT` statement to include QUALIFY."""

    match_grammar = ansi.SelectStatementSegment.match_grammar.copy(
        insert=[Ref("PreWhereClauseSegment", optional=True)],
        before=Ref("WhereClauseSegment", optional=True),
    ).copy(
        insert=[
            Ref("FormatClauseSegment", optional=True),
            Ref("IntoOutfileClauseSegment", optional=True),
            Ref("SettingsClauseSegment", optional=True),
        ],
    )


class UnorderedSelectStatementSegment(ansi.UnorderedSelectStatementSegment):
    """Enhance unordered `SELECT` statement to include QUALIFY."""

    match_grammar = ansi.UnorderedSelectStatementSegment.match_grammar.copy(
        insert=[Ref("PreWhereClauseSegment", optional=True)],
        before=Ref("WhereClauseSegment", optional=True),
    )


class WithFillSegment(ansi.WithFillSegment):
    """Enhances `ORDER BY` clauses to include WITH FILL.

    https://clickhouse.com/docs/en/sql-reference/statements/select/order-by#order-by-expr-with-fill-modifier
    """

    match_grammar: Matchable = Sequence(
        "WITH",
        "FILL",
        Sequence("FROM", Ref("ExpressionSegment"), optional=True),
        Sequence("TO", Ref("ExpressionSegment"), optional=True),
        Sequence(
            "STEP",
            OneOf(
                Ref("NumericLiteralSegment"),
                Ref("IntervalExpressionSegment"),
            ),
            optional=True,
        ),
    )


class BracketedArguments(ansi.BracketedArguments):
    """A series of bracketed arguments.

    e.g. the bracketed part of numeric(1, 3)
    """

    match_grammar = Bracketed(
        Delimited(
            OneOf(
                # Dataypes like Nullable allow optional datatypes here.
                Ref("DatatypeSegment"),
            ),
            # The brackets might be empty for some cases...
            optional=True,
        ),
    )


class DatatypeSegment(BaseSegment):
    """Support complex Clickhouse data types.

    Complex data types are typically used in either DDL statements or as
    the target type in casts.
    """

    type = "data_type"
    match_grammar = OneOf(
        # Nullable(Type)
        Sequence(
            StringParser("NULLABLE", CodeSegment, type="data_type_identifier"),
            Bracketed(Ref("DatatypeSegment")),
        ),
        # LowCardinality(Type)
        Sequence(
            StringParser("LOWCARDINALITY", CodeSegment, type="data_type_identifier"),
            Bracketed(Ref("DatatypeSegment")),
        ),
        # DateTime64(precision, 'timezone')
        Sequence(
            StringParser("DATETIME64", CodeSegment, type="data_type_identifier"),
            Bracketed(
                Delimited(
                    OneOf(
                        Ref("NumericLiteralSegment"),  # precision
                        Ref("QuotedLiteralSegment"),  # timezone
                    ),
                    delimiter=Ref("CommaSegment"),
                    optional=True,
                )
            ),
        ),
        # DateTime('timezone')
        Sequence(
            StringParser("DATETIME", CodeSegment, type="data_type_identifier"),
            Bracketed(
                Ref("QuotedLiteralSegment"),  # timezone
                optional=True,
            ),
        ),
        # FixedString(length)
        Sequence(
            StringParser("FIXEDSTRING", CodeSegment, type="data_type_identifier"),
            Bracketed(Ref("NumericLiteralSegment")),  # length
        ),
        # Array(Type)
        Sequence(
            StringParser("ARRAY", CodeSegment, type="data_type_identifier"),
            Bracketed(Ref("DatatypeSegment")),
        ),
        # Map(KeyType, ValueType)
        Sequence(
            StringParser("MAP", CodeSegment, type="data_type_identifier"),
            Bracketed(
                Delimited(
                    Ref("DatatypeSegment"),
                    delimiter=Ref("CommaSegment"),
                )
            ),
        ),
        # Tuple(Type1, Type2) or Tuple(name1 Type1, name2 Type2)
        Sequence(
            StringParser("TUPLE", CodeSegment, type="data_type_identifier"),
            Bracketed(
                Delimited(
                    OneOf(
                        # Named tuple element: name Type
                        Sequence(
                            OneOf(
                                Ref("SingleIdentifierGrammar"),
                                Ref("QuotedIdentifierSegment"),
                            ),
                            Ref("DatatypeSegment"),
                        ),
                        # Regular tuple element: just Type
                        Ref("DatatypeSegment"),
                    ),
                    delimiter=Ref("CommaSegment"),
                )
            ),
        ),
        # Nested(name1 Type1, name2 Type2)
        Sequence(
            StringParser("NESTED", CodeSegment, type="data_type_identifier"),
            Bracketed(
                Delimited(
                    Sequence(
                        Ref("SingleIdentifierGrammar"),
                        Ref("DatatypeSegment"),
                    ),
                    delimiter=Ref("CommaSegment"),
                )
            ),
        ),
        # JSON data type
        StringParser("JSON", CodeSegment, type="data_type_identifier"),
        # Enum8('val1' = 1, 'val2' = 2)
        Sequence(
            OneOf(
                StringParser("ENUM8", CodeSegment, type="data_type_identifier"),
                StringParser("ENUM16", CodeSegment, type="data_type_identifier"),
            ),
            Bracketed(
                Delimited(
                    Sequence(
                        Ref("QuotedLiteralSegment"),
                        Ref("EqualsSegment"),
                        Ref("NumericLiteralSegment"),
                    ),
                    delimiter=Ref("CommaSegment"),
                )
            ),
        ),
        # double args
        Sequence(
            OneOf(
                StringParser("DECIMAL", CodeSegment, type="data_type_identifier"),
                StringParser("NUMERIC", CodeSegment, type="data_type_identifier"),
            ),
            Ref("BracketedArguments", optional=True),
        ),
        # single args
        Sequence(
            OneOf(
                StringParser("DECIMAL32", CodeSegment, type="data_type_identifier"),
                StringParser("DECIMAL64", CodeSegment, type="data_type_identifier"),
                StringParser("DECIMAL128", CodeSegment, type="data_type_identifier"),
                StringParser("DECIMAL256", CodeSegment, type="data_type_identifier"),
            ),
            Bracketed(Ref("NumericLiteralSegment")),  # scale
        ),
        Ref("TupleTypeSegment"),
        Ref("DatatypeIdentifierSegment"),
        Ref("NumericLiteralSegment"),
        Sequence(
            StringParser("DATETIME64", CodeSegment, type="data_type_identifier"),
            Bracketed(
                Delimited(
                    Ref("NumericLiteralSegment"),  # precision
                    Ref("QuotedLiteralSegment", optional=True),  # timezone
                    # The brackets might be empty as well
                    optional=True,
                ),
                optional=True,
            ),
        ),
        Sequence(
            StringParser("ARRAY", CodeSegment, type="data_type_identifier"),
            Bracketed(Ref("DatatypeSegment")),
        ),
    )


class TupleTypeSegment(ansi.StructTypeSegment):
    """Expression to construct a Tuple datatype."""

    match_grammar = Sequence(
        "TUPLE",
        Ref("TupleTypeSchemaSegment"),  # Tuple() can't be empty
    )


class TupleTypeSchemaSegment(BaseSegment):
    """Expression to construct the schema of a Tuple datatype."""

    type = "tuple_type_schema"
    match_grammar = Bracketed(
        Delimited(
            Sequence(
                Ref("SingleIdentifierGrammar"),
                Ref("DatatypeSegment"),
            ),
            bracket_pairs_set="bracket_pairs",
        ),
        bracket_pairs_set="bracket_pairs",
        bracket_type="round",
    )


class ArrayJoinClauseSegment(BaseSegment):
    """[LEFT] ARRAY JOIN does not support Join conditions and doesn't work as real JOIN.

    https://clickhouse.com/docs/en/sql-reference/statements/select/array-join
    """

    type = "array_join_clause"

    match_grammar: Matchable = Sequence(
        Ref.keyword("LEFT", optional=True),
        "ARRAY",
        Ref("JoinKeywordsGrammar"),
        Indent,
        Delimited(
            Ref("SelectClauseElementSegment"),
        ),
        Dedent,
    )


class CTEDefinitionSegment(ansi.CTEDefinitionSegment):
    """A CTE Definition from a WITH statement.

    Overridden from ANSI to allow expression CTEs.
    https://clickhouse.com/docs/en/sql-reference/statements/select/with/
    """

    type = "common_table_expression"
    match_grammar: Matchable = OneOf(
        Sequence(
            Ref("SingleIdentifierGrammar"),
            Ref("CTEColumnList", optional=True),
            "AS",
            Bracketed(
                # Ephemeral here to subdivide the query.
                Ref("SelectableGrammar"),
                parse_mode=ParseMode.GREEDY,
            ),
        ),
        Sequence(
            Ref("ExpressionSegment"),
            "AS",
            Ref("SingleIdentifierGrammar"),
        ),
    )


class AliasExpressionSegment(ansi.AliasExpressionSegment):
    """A reference to an object with an `AS` clause."""

    type = "alias_expression"
    match_grammar: Matchable = Sequence(
        Indent,
        Ref("AsAliasOperatorSegment", optional=True),
        OneOf(
            Sequence(
                Ref("SingleIdentifierGrammar"),
                # Column alias in VALUES clause
                Bracketed(Ref("SingleIdentifierListSegment"), optional=True),
            ),
            Ref("SingleQuotedIdentifierSegment"),
            exclude=OneOf(
                "LATERAL",
                "WINDOW",
                "KEYS",
            ),
        ),
        Dedent,
    )


class WildcardExpressionSegment(ansi.WildcardExpressionSegment):
    """An extension of the star expression for Clickhouse."""

    match_grammar = ansi.WildcardExpressionSegment.match_grammar.copy(
        insert=[
            Ref("ExceptClauseSegment", optional=True),
        ]
    )


class ExceptClauseSegment(BaseSegment):
    """A Clickhouse SELECT EXCEPT clause.

    https://clickhouse.com/docs/en/sql-reference/statements/select#except
    """

    type = "select_except_clause"
    match_grammar = Sequence(
        "EXCEPT",
        OneOf(
            Bracketed(Delimited(Ref("SingleIdentifierGrammar"))),
            Ref("SingleIdentifierGrammar"),
        ),
    )


class SelectClauseModifierSegment(ansi.SelectClauseModifierSegment):
    """Things that come after SELECT but before the columns.

    Overridden from ANSI to allow DISTINCT ON ()
    https://clickhouse.com/docs/en/sql-reference/statements/select/distinct
    """

    match_grammar = OneOf(
        Sequence(
            "DISTINCT",
            Sequence(
                "ON",
                Bracketed(Delimited(Ref("ExpressionSegment"))),
                optional=True,
            ),
        ),
        "ALL",
    )


class FromExpressionElementSegment(ansi.FromExpressionElementSegment):
    """A table expression.

    Overridden from ANSI to allow FINAL modifier.
    https://clickhouse.com/docs/en/sql-reference/statements/select/from#final-modifier
    """

    type = "from_expression_element"
    match_grammar: Matchable = Sequence(
        Ref("PreTableFunctionKeywordsGrammar", optional=True),
        OptionallyBracketed(Ref("TableExpressionSegment")),
        Ref(
            "AliasExpressionSegment",
            exclude=OneOf(
                Ref("FromClauseTerminatorGrammar"),
                Ref("SamplingExpressionSegment"),
                Ref("JoinLikeClauseGrammar"),
                "FINAL",
                Ref("JoinClauseSegment"),
            ),
            optional=True,
        ),
        Ref.keyword("FINAL", optional=True),
        # https://cloud.google.com/bigquery/docs/reference/standard-sql/arrays#flattening_arrays
        Sequence("WITH", "OFFSET", Ref("AliasExpressionSegment"), optional=True),
        Ref("SamplingExpressionSegment", optional=True),
        Ref("PostTableExpressionGrammar", optional=True),
    )


class TableEngineFunctionSegment(BaseSegment):
    """A ClickHouse `ENGINE` clause function.

    With this segment we attempt to match all possible engines.
    """

    type = "table_engine_function"
    match_grammar: Matchable = Sequence(
        Sequence(
            Ref(
                "FunctionNameSegment",
                exclude=OneOf(
                    Ref("DatePartFunctionNameSegment"),
                    Ref("ValuesClauseSegment"),
                ),
            ),
            Ref("FunctionContentsSegment", optional=True),
        ),
    )


class OnClusterClauseSegment(BaseSegment):
    """A `ON CLUSTER` clause."""

    type = "on_cluster_clause"
    match_grammar = Sequence(
        "ON",
        "CLUSTER",
        OneOf(
            Ref("SingleIdentifierGrammar"),
            # Support for placeholders like '{cluster}'
            Ref("QuotedLiteralSegment"),
        ),
    )


class TableEngineSegment(BaseSegment):
    """An `ENGINE` used in `CREATE TABLE`."""

    type = "engine"
    match_grammar = Sequence(
        "ENGINE",
        Ref("EqualsSegment", optional=True),
        Sequence(
            Ref("TableEngineFunctionSegment"),
            AnySetOf(
                Ref("MergeTreesOrderByClauseSegment"),
                Sequence(
                    "PARTITION",
                    "BY",
                    Ref("ExpressionSegment"),
                ),
                Sequence(
                    "PRIMARY",
                    "KEY",
                    Ref("ExpressionSegment"),
                ),
                Sequence(
                    "SAMPLE",
                    "BY",
                    Ref("ExpressionSegment"),
                ),
            ),
            Ref("SettingsClauseSegment", optional=True),
        ),
    )


class DatabaseEngineFunctionSegment(BaseSegment):
    """A ClickHouse `ENGINE` clause function.

    With this segment we attempt to match all possible engines.
    """

    type = "engine_function"
    match_grammar: Matchable = Sequence(
        Sequence(
            OneOf(
                "ATOMIC",
                "MYSQL",
                "MATERIALIZEDMYSQL",
                "LAZY",
                "POSTGRESQL",
                "MATERIALIZEDPOSTGRESQL",
                "REPLICATED",
                "SQLITE",
            ),
            Ref("FunctionContentsSegment", optional=True),
        ),
    )


class DatabaseEngineSegment(BaseSegment):
    """An `ENGINE` used in `CREATE TABLE`."""

    type = "database_engine"

    match_grammar = Sequence(
        "ENGINE",
        Ref("EqualsSegment"),
        Sequence(
            Ref("DatabaseEngineFunctionSegment"),
            AnySetOf(
                Ref("MergeTreesOrderByClauseSegment"),
                Sequence(
                    "PARTITION",
                    "BY",
                    Ref("ExpressionSegment"),
                    optional=True,
                ),
                Sequence(
                    "PRIMARY",
                    "KEY",
                    Ref("ExpressionSegment"),
                    optional=True,
                ),
                Sequence(
                    "SAMPLE",
                    "BY",
                    Ref("ExpressionSegment"),
                    optional=True,
                ),
            ),
            Ref("SettingsClauseSegment", optional=True),
        ),
    )


class ColumnTTLSegment(BaseSegment):
    """A TTL clause for columns as used in CREATE TABLE.

    Specified in
    https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/mergetree/#mergetree-column-ttl
    """

    type = "column_ttl_segment"

    match_grammar = Sequence(
        "TTL",
        Ref("ExpressionSegment"),
    )


class TableTTLSegment(BaseSegment):
    """A TTL clause for tables as used in CREATE TABLE.

    Specified in
    https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/mergetree/#mergetree-table-ttl
    """

    type = "table_ttl_segment"

    match_grammar = Sequence(
        "TTL",
        Delimited(
            Sequence(
                Ref("ExpressionSegment"),
                OneOf(
                    "DELETE",
                    Sequence(
                        "TO",
                        "VOLUME",
                        Ref("QuotedLiteralSegment"),
                    ),
                    Sequence(
                        "TO",
                        "DISK",
                        Ref("QuotedLiteralSegment"),
                    ),
                    optional=True,
                ),
                Ref("WhereClauseSegment", optional=True),
                Ref("GroupByClauseSegment", optional=True),
            )
        ),
    )


class ColumnConstraintSegment(BaseSegment):
    """ClickHouse specific column constraints.

    As specified in
    https://clickhouse.com/docs/en/sql-reference/statements/create/table#constraints
    """

    type = "column_constraint_segment"

    match_grammar = AnySetOf(
        Sequence(
            Sequence(
                "CONSTRAINT",
                Ref("ObjectReferenceSegment"),
                optional=True,
            ),
            OneOf(
                Sequence(Ref.keyword("NOT", optional=True), "NULL"),
                Sequence("CHECK", Bracketed(Ref("ExpressionSegment"))),
                Sequence(
                    OneOf(
                        "DEFAULT",
                        "MATERIALIZED",
                        "ALIAS",
                    ),
                    OneOf(
                        Ref("LiteralGrammar"),
                        Ref("FunctionSegment"),
                        Ref("BareFunctionSegment"),
                    ),
                ),
                Sequence(
                    "EPHEMERAL",
                    OneOf(
                        Ref("LiteralGrammar"),
                        Ref("FunctionSegment"),
                        Ref("BareFunctionSegment"),
                        optional=True,
                    ),
                ),
                Ref("PrimaryKeyGrammar"),
                Sequence(
                    "CODEC",
                    Ref("FunctionContentsGrammar"),
                    optional=True,
                ),
                Ref("ColumnTTLSegment"),
            ),
        )
    )


class CreateDatabaseStatementSegment(ansi.CreateDatabaseStatementSegment):
    """A `CREATE DATABASE` statement.

    As specified in
    https://clickhouse.com/docs/en/sql-reference/statements/create/database
    """

    type = "create_database_statement"

    match_grammar = Sequence(
        "CREATE",
        "DATABASE",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("DatabaseReferenceSegment"),
        AnySetOf(
            Ref("OnClusterClauseSegment", optional=True),
            Ref("DatabaseEngineSegment", optional=True),
            Sequence(
                "COMMENT",
                Ref("SingleIdentifierGrammar"),
                optional=True,
            ),
        ),
        AnyNumberOf(
            "TABLE",
            "OVERRIDE",
            Ref("TableReferenceSegment"),
            Bracketed(
                Delimited(
                    Ref("TableConstraintSegment"),
                    Ref("ColumnDefinitionSegment"),
                    Ref("ColumnConstraintSegment"),
                ),
                optional=True,
            ),
            optional=True,
        ),
    )


class RenameStatementSegment(BaseSegment):
    """A `RENAME TABLE` statement.

    As specified in
    https://clickhouse.com/docs/en/sql-reference/statements/rename/
    """

    type = "rename_table_statement"

    match_grammar = Sequence(
        "RENAME",
        OneOf(
            Sequence(
                "TABLE",
                Delimited(
                    Sequence(
                        Ref("TableReferenceSegment"),
                        "TO",
                        Ref("TableReferenceSegment"),
                    )
                ),
            ),
            Sequence(
                "DATABASE",
                Delimited(
                    Sequence(
                        Ref("DatabaseReferenceSegment"),
                        "TO",
                        Ref("DatabaseReferenceSegment"),
                    )
                ),
            ),
            Sequence(
                "DICTIONARY",
                Delimited(
                    Sequence(
                        Ref("ObjectReferenceSegment"),
                        "TO",
                        Ref("ObjectReferenceSegment"),
                    )
                ),
            ),
        ),
        Ref("OnClusterClauseSegment", optional=True),
    )


class CreateTableStatementSegment(ansi.CreateTableStatementSegment):
    """A `CREATE TABLE` statement.

    As specified in
    https://clickhouse.com/docs/en/sql-reference/statements/create/table/
    """

    type = "create_table_statement"

    match_grammar: Matchable = OneOf(
        Sequence(
            "CREATE",
            Ref("OrReplaceGrammar", optional=True),
            "TABLE",
            Ref("IfNotExistsGrammar", optional=True),
            Ref("TableReferenceSegment"),
            Ref("OnClusterClauseSegment", optional=True),
            OneOf(
                # CREATE TABLE (...):
                Sequence(
                    Bracketed(
                        Delimited(
                            OneOf(
                                Ref("TableConstraintSegment"),
                                Ref("ColumnDefinitionSegment"),
                                Ref("ColumnConstraintSegment"),
                            ),
                        ),
                        # Column definition may be missing if using AS SELECT
                        optional=True,
                    ),
                    Ref("TableEngineSegment"),
                    # CREATE TABLE (...) AS SELECT:
                    Sequence(
                        "AS",
                        Ref("SelectableGrammar"),
                        optional=True,
                    ),
                ),
                # CREATE TABLE AS other_table:
                Sequence(
                    "AS",
                    Ref("TableReferenceSegment"),
                    Ref("TableEngineSegment", optional=True),
                ),
                # CREATE TABLE AS table_function():
                Sequence(
                    "AS",
                    Ref("FunctionSegment"),
                ),
            ),
            AnySetOf(
                Sequence(
                    "COMMENT",
                    OneOf(
                        Ref("SingleIdentifierGrammar"),
                        Ref("QuotedIdentifierSegment"),
                    ),
                ),
                Ref("TableTTLSegment"),
                optional=True,
            ),
            Ref("TableEndClauseSegment", optional=True),
        ),
        # CREATE TEMPORARY TABLE
        Sequence(
            "CREATE",
            Ref.keyword("TEMPORARY"),
            "TABLE",
            Ref("IfNotExistsGrammar", optional=True),
            Ref("TableReferenceSegment"),
            OneOf(
                # CREATE TEMPORARY TABLE (...):
                Sequence(
                    Bracketed(
                        Delimited(
                            OneOf(
                                Ref("TableConstraintSegment"),
                                Ref("ColumnDefinitionSegment"),
                                Ref("ColumnConstraintSegment"),
                            ),
                        ),
                        # Column definition may be missing if using AS SELECT
                        optional=True,
                    ),
                    Ref("TableEngineSegment"),
                    # CREATE TEMPORARY TABLE (...) AS SELECT:
                    Sequence(
                        "AS",
                        Ref("SelectableGrammar"),
                        optional=True,
                    ),
                ),
                # CREATE TEMPORARY TABLE AS other_table:
                Sequence(
                    "AS",
                    Ref("TableReferenceSegment"),
                    Ref("TableEngineSegment", optional=True),
                ),
                # CREATE TEMPORARY TABLE AS table_function():
                Sequence(
                    "AS",
                    Ref("FunctionSegment"),
                ),
                # CREATE TEMPORARY TABLE AS
                Sequence(
                    "AS",
                    Ref("SelectableGrammar"),
                    optional=True,
                ),
            ),
            AnySetOf(
                Sequence(
                    "COMMENT",
                    OneOf(
                        Ref("SingleIdentifierGrammar"),
                        Ref("QuotedIdentifierSegment"),
                    ),
                ),
                Ref("TableTTLSegment"),
                optional=True,
            ),
            Ref("TableEndClauseSegment", optional=True),
        ),
    )


class CreateViewStatementSegment(BaseSegment):
    """A `CREATE VIEW` statement.

    https://clickhouse.com/docs/en/sql-reference/statements/create/view
    """

    type = "create_view_statement"

    match_grammar = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        "VIEW",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        Ref("OnClusterClauseSegment", optional=True),
        "AS",
        Ref("SelectableGrammar"),
        Ref("TableEndClauseSegment", optional=True),
    )


class CreateMaterializedViewStatementSegment(BaseSegment):
    """A `CREATE MATERIALIZED VIEW` statement.

    https://clickhouse.com/docs/en/sql-reference/statements/create/table/
    """

    type = "create_materialized_view_statement"

    match_grammar = Sequence(
        "CREATE",
        "MATERIALIZED",
        "VIEW",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        Ref("OnClusterClauseSegment", optional=True),
        OneOf(
            Sequence(
                "TO",
                Ref("TableReferenceSegment"),
                # Add support for column list in TO clause
                Bracketed(
                    Delimited(
                        Ref("SingleIdentifierGrammar"),
                    ),
                    optional=True,
                ),
                Ref("TableEngineSegment", optional=True),
            ),
            Sequence(
                Ref("TableEngineSegment", optional=True),
                # Add support for PARTITION BY clause
                Sequence(
                    "PARTITION",
                    "BY",
                    Ref("ExpressionSegment"),
                    optional=True,
                ),
                # Add support for ORDER BY clause
                Ref("MergeTreesOrderByClauseSegment", optional=True),
                # Add support for TTL clause
                Ref("TableTTLSegment", optional=True),
                # Add support for SETTINGS clause
                Ref("SettingsClauseSegment", optional=True),
                Sequence("POPULATE", optional=True),
            ),
        ),
        "AS",
        Ref("SelectableGrammar"),
        Ref("TableEndClauseSegment", optional=True),
    )


class DropTableStatementSegment(ansi.DropTableStatementSegment):
    """A `DROP TABLE` statement.

    As specified in
    https://clickhouse.com/docs/en/sql-reference/statements/drop/
    """

    type = "drop_table_statement"

    match_grammar = Sequence(
        "DROP",
        Ref.keyword("TEMPORARY", optional=True),
        "TABLE",
        Ref("IfExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        Ref("OnClusterClauseSegment", optional=True),
        Ref.keyword("SYNC", optional=True),
    )


class DropDatabaseStatementSegment(ansi.DropDatabaseStatementSegment):
    """A `DROP DATABASE` statement.

    As specified in
    https://clickhouse.com/docs/en/sql-reference/statements/drop/
    """

    type = "drop_database_statement"

    match_grammar = Sequence(
        "DROP",
        "DATABASE",
        Ref("IfExistsGrammar", optional=True),
        Ref("DatabaseReferenceSegment"),
        Ref("OnClusterClauseSegment", optional=True),
        Ref.keyword("SYNC", optional=True),
    )


class DropDictionaryStatementSegment(BaseSegment):
    """A `DROP DICTIONARY` statement.

    As specified in
    https://clickhouse.com/docs/en/sql-reference/statements/drop/
    """

    type = "drop_dictionary_statement"

    match_grammar = Sequence(
        "DROP",
        "DICTIONARY",
        Ref("IfExistsGrammar", optional=True),
        Ref("SingleIdentifierGrammar"),
        Ref.keyword("SYNC", optional=True),
    )


class DropUserStatementSegment(ansi.DropUserStatementSegment):
    """A `DROP USER` statement.

    As specified in
    https://clickhouse.com/docs/en/sql-reference/statements/drop/
    """

    type = "drop_user_statement"

    match_grammar = Sequence(
        "DROP",
        "USER",
        Ref("IfExistsGrammar", optional=True),
        Ref("SingleIdentifierGrammar"),
        Ref("OnClusterClauseSegment", optional=True),
    )


class DropRoleStatementSegment(ansi.DropRoleStatementSegment):
    """A `DROP ROLE` statement.

    As specified in
    https://clickhouse.com/docs/en/sql-reference/statements/drop/
    """

    type = "drop_user_statement"

    match_grammar = Sequence(
        "DROP",
        "ROLE",
        Ref("IfExistsGrammar", optional=True),
        Ref("SingleIdentifierGrammar"),
        Ref("OnClusterClauseSegment", optional=True),
    )


class DropQuotaStatementSegment(BaseSegment):
    """A `DROP QUOTA` statement.

    As specified in
    https://clickhouse.com/docs/en/sql-reference/statements/drop/
    """

    type = "drop_quota_statement"

    match_grammar = Sequence(
        "DROP",
        "QUOTA",
        Ref("IfExistsGrammar", optional=True),
        Ref("SingleIdentifierGrammar"),
        Ref("OnClusterClauseSegment", optional=True),
    )


class DropSettingProfileStatementSegment(BaseSegment):
    """A `DROP setting PROFILE` statement.

    As specified in
    https://clickhouse.com/docs/en/sql-reference/statements/drop/
    """

    type = "drop_setting_profile_statement"

    match_grammar = Sequence(
        "DROP",
        Delimited(
            Ref("NakedIdentifierSegment"),
            min_delimiters=0,
        ),
        "PROFILE",
        Ref("IfExistsGrammar", optional=True),
        Ref("SingleIdentifierGrammar"),
        Ref("OnClusterClauseSegment", optional=True),
    )


class DropViewStatementSegment(ansi.DropViewStatementSegment):
    """A `DROP VIEW` statement.

    As specified in
    https://clickhouse.com/docs/en/sql-reference/statements/drop/
    """

    type = "drop_view_statement"

    match_grammar = Sequence(
        "DROP",
        "VIEW",
        Ref("IfExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        Ref("OnClusterClauseSegment", optional=True),
        Ref.keyword("SYNC", optional=True),
    )


class DropFunctionStatementSegment(ansi.DropFunctionStatementSegment):
    """A `DROP FUNCTION` statement.

    As specified in
    https://clickhouse.com/docs/en/sql-reference/statements/drop/
    """

    type = "drop_function_statement"

    match_grammar = Sequence(
        "DROP",
        "FUNCTION",
        Ref("IfExistsGrammar", optional=True),
        Ref("SingleIdentifierGrammar"),
        Ref("OnClusterClauseSegment", optional=True),
    )


class SystemMergesSegment(BaseSegment):
    """A `SYSTEM ... MERGES` statement.

    https://clickhouse.com/docs/en/sql-reference/statements/system
    """

    type = "system_merges_segment"

    match_grammar = Sequence(
        OneOf(
            "START",
            "STOP",
        ),
        "MERGES",
        OneOf(
            Sequence(
                "ON",
                "VOLUME",
                Ref("ObjectReferenceSegment"),
            ),
            Ref("TableReferenceSegment"),
        ),
    )


class SystemTTLMergesSegment(BaseSegment):
    """A `SYSTEM ... TTL MERGES` statement.

    https://clickhouse.com/docs/en/sql-reference/statements/system
    """

    type = "system_ttl_merges_segment"

    match_grammar = Sequence(
        OneOf(
            "START",
            "STOP",
        ),
        "TTL",
        "MERGES",
        Ref("TableReferenceSegment", optional=True),
    )


class SystemMovesSegment(BaseSegment):
    """A `SYSTEM ... MOVES` statement.

    https://clickhouse.com/docs/en/sql-reference/statements/system
    """

    type = "system_moves_segment"

    match_grammar = Sequence(
        OneOf(
            "START",
            "STOP",
        ),
        "MOVES",
        Ref("TableReferenceSegment", optional=True),
    )


class SystemReplicaSegment(BaseSegment):
    """A `SYSTEM ... REPLICA` statement.

    https://clickhouse.com/docs/en/sql-reference/statements/system
    """

    type = "system_replica_segment"

    match_grammar = OneOf(
        Sequence(
            "SYNC",
            "REPLICA",
            Ref("OnClusterClauseSegment", optional=True),
            Ref("TableReferenceSegment"),
            Sequence("STRICT", optional=True),
        ),
        Sequence(
            "DROP",
            "REPLICA",
            Ref("SingleIdentifierGrammar"),
            Sequence(
                "FROM",
                OneOf(
                    Sequence(
                        "DATABASE",
                        Ref("ObjectReferenceSegment"),
                    ),
                    Sequence(
                        "TABLE",
                        Ref("TableReferenceSegment"),
                    ),
                    Sequence(
                        "ZKPATH",
                        Ref("PathSegment"),
                    ),
                ),
                optional=True,
            ),
        ),
        Sequence(
            "RESTART",
            "REPLICA",
            Ref("TableReferenceSegment"),
        ),
        Sequence(
            "RESTORE",
            "REPLICA",
            Ref("TableReferenceSegment"),
            Ref("OnClusterClauseSegment", optional=True),
        ),
    )


class SystemFilesystemSegment(BaseSegment):
    """A `SYSTEM ... FILESYSTEM` statement.

    https://clickhouse.com/docs/en/sql-reference/statements/system
    """

    type = "system_filesystem_segment"

    match_grammar = Sequence(
        "DROP",
        "FILESYSTEM",
        "CACHE",
    )


class SystemReplicatedSegment(BaseSegment):
    """A `SYSTEM ... REPLICATED` statement.

    https://clickhouse.com/docs/en/sql-reference/statements/system
    """

    type = "system_replicated_segment"

    match_grammar = Sequence(
        OneOf(
            "START",
            "STOP",
        ),
        "REPLICATED",
        "SENDS",
        Ref("TableReferenceSegment", optional=True),
    )


class SystemReplicationSegment(BaseSegment):
    """A `SYSTEM ... REPLICATION` statement.

    https://clickhouse.com/docs/en/sql-reference/statements/system
    """

    type = "system_replication_segment"

    match_grammar = Sequence(
        OneOf(
            "START",
            "STOP",
        ),
        "REPLICATION",
        "QUEUES",
        Ref("TableReferenceSegment", optional=True),
    )


class SystemFetchesSegment(BaseSegment):
    """A `SYSTEM ... FETCHES` statement.

    https://clickhouse.com/docs/en/sql-reference/statements/system
    """

    type = "system_fetches_segment"

    match_grammar = Sequence(
        OneOf(
            "START",
            "STOP",
        ),
        "FETCHES",
        Ref("TableReferenceSegment", optional=True),
    )


class SystemDistributedSegment(BaseSegment):
    """A `SYSTEM ... DISTRIBUTED` statement.

    https://clickhouse.com/docs/en/sql-reference/statements/system
    """

    type = "system_distributed_segment"

    match_grammar = Sequence(
        OneOf(
            Sequence(
                OneOf(
                    "START",
                    "STOP",
                ),
                "DISTRIBUTED",
                "SENDS",
                Ref("TableReferenceSegment"),
            ),
            Sequence(
                "FLUSH",
                "DISTRIBUTED",
                Ref("TableReferenceSegment"),
            ),
        ),
        # Ref("TableReferenceSegment"),
    )


class SystemModelSegment(BaseSegment):
    """A `SYSTEM ... MODEL` statement.

    https://clickhouse.com/docs/en/sql-reference/statements/system
    """

    type = "system_model_segment"

    match_grammar = Sequence(
        "RELOAD",
        OneOf(
            Sequence(
                "MODELS",
                Ref("OnClusterClauseSegment", optional=True),
            ),
            Sequence(
                "MODEL",
                AnySetOf(
                    Ref("OnClusterClauseSegment", optional=True),
                    Ref("PathSegment"),
                ),
            ),
        ),
    )


class SystemFileSegment(BaseSegment):
    """A `SYSTEM ... FILE` statement.

    https://clickhouse.com/docs/en/sql-reference/statements/system
    """

    type = "system_file_segment"

    match_grammar = Sequence(
        "SYNC",
        "FILE",
        "CACHE",
    )


class SystemUnfreezeSegment(BaseSegment):
    """A `SYSTEM ... UNFREEZE` statement.

    https://clickhouse.com/docs/en/sql-reference/statements/system
    """

    type = "system_unfreeze_segment"

    match_grammar = Sequence(
        "UNFREEZE",
        "WITH",
        "NAME",
        Ref("ObjectReferenceSegment"),
    )


class SystemStatementSegment(BaseSegment):
    """A `SYSTEM ...` statement.

    https://clickhouse.com/docs/en/sql-reference/statements/system
    """

    type = "system_statement"

    match_grammar: Matchable = Sequence(
        "SYSTEM",
        OneOf(
            Ref("SystemMergesSegment"),
            Ref("SystemTTLMergesSegment"),
            Ref("SystemMovesSegment"),
            Ref("SystemReplicaSegment"),
            Ref("SystemReplicatedSegment"),
            Ref("SystemReplicationSegment"),
            Ref("SystemFetchesSegment"),
            Ref("SystemDistributedSegment"),
            Ref("SystemFileSegment"),
            Ref("SystemFilesystemSegment"),
            Ref("SystemUnfreezeSegment"),
            Ref("SystemModelSegment"),
        ),
    )


class AlterTableStatementSegment(BaseSegment):
    """An `ALTER TABLE` statement for ClickHouse.

    As specified in
    https://clickhouse.com/docs/en/sql-reference/statements/alter/
    """

    type = "alter_table_statement"

    match_grammar = Sequence(
        "ALTER",
        "TABLE",
        Ref("IfExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        Ref("OnClusterClauseSegment", optional=True),
        OneOf(
            # ALTER TABLE ... DROP COLUMN [IF EXISTS] name
            Sequence(
                "DROP",
                "COLUMN",
                Ref("IfExistsGrammar", optional=True),
                Ref("SingleIdentifierGrammar"),  # Column name
            ),
            # ALTER TABLE ... ADD COLUMN [IF NOT EXISTS] name [type]
            Sequence(
                "ADD",
                "COLUMN",
                Ref("IfNotExistsGrammar", optional=True),
                Ref("SingleIdentifierGrammar"),  # Column name
                OneOf(
                    # Regular column with type
                    Sequence(
                        Ref("DatatypeSegment"),  # Data type
                        Sequence(
                            "DEFAULT",
                            Ref("ExpressionSegment"),
                            optional=True,
                        ),
                        Sequence(
                            "MATERIALIZED",
                            Ref("ExpressionSegment"),
                            optional=True,
                        ),
                        Sequence(
                            "CODEC",
                            Bracketed(
                                Delimited(
                                    OneOf(
                                        Ref("FunctionSegment"),
                                        Ref("SingleIdentifierGrammar"),
                                    ),
                                ),
                            ),
                            optional=True,
                        ),
                    ),
                    # Alias column with type
                    Sequence(
                        Ref("DatatypeSegment"),  # Data type
                        "ALIAS",
                        Ref("ExpressionSegment"),
                    ),
                    # Alias column without type
                    Sequence(
                        "ALIAS",
                        Ref("ExpressionSegment"),
                    ),
                    # Default could also be used without type
                    Sequence(
                        "DEFAULT",
                        Ref("ExpressionSegment"),
                    ),
                    # Materialized could also be used without type
                    Sequence(
                        "MATERIALIZED",
                        Ref("ExpressionSegment"),
                    ),
                ),
                OneOf(
                    Sequence(
                        "AFTER",
                        Ref("SingleIdentifierGrammar"),  # Column name
                    ),
                    "FIRST",
                    optional=True,
                ),
            ),
            # ALTER TABLE ... ADD ALIAS name FOR column_name
            Sequence(
                "ADD",
                "ALIAS",
                Ref("IfNotExistsGrammar", optional=True),
                Ref("SingleIdentifierGrammar"),  # Alias name
                "FOR",
                Ref("SingleIdentifierGrammar"),  # Column name
            ),
            # ALTER TABLE ... RENAME COLUMN [IF EXISTS] name to new_name
            Sequence(
                "RENAME",
                "COLUMN",
                Ref("IfExistsGrammar", optional=True),
                Ref("SingleIdentifierGrammar"),  # Column name
                "TO",
                Ref("SingleIdentifierGrammar"),  # New column name
            ),
            # ALTER TABLE ... COMMENT COLUMN [IF EXISTS] name 'Text comment'
            Sequence(
                "COMMENT",
                "COLUMN",
                Ref("IfExistsGrammar", optional=True),
                Ref("SingleIdentifierGrammar"),  # Column name
                Ref("QuotedLiteralSegment"),  # Comment text
            ),
            # ALTER TABLE ... COMMENT 'Text comment'
            Sequence(
                "COMMENT",
                Ref("QuotedLiteralSegment"),  # Comment text
            ),
            # ALTER TABLE ... MODIFY COMMENT 'Text comment'
            Sequence(
                "MODIFY",
                "COMMENT",
                Ref("QuotedLiteralSegment"),  # Comment text
            ),
            # ALTER TABLE ... MODIFY COLUMN [IF EXISTS] name [TYPE] [type]
            Sequence(
                "MODIFY",
                "COLUMN",
                Ref("IfExistsGrammar", optional=True),
                Ref("SingleIdentifierGrammar"),  # Column name
                OneOf(
                    # Type modification with explicit TYPE keyword
                    Sequence(
                        "TYPE",
                        Ref("DatatypeSegment"),  # Data type
                        Sequence(
                            "DEFAULT",
                            Ref("ExpressionSegment"),
                            optional=True,
                        ),
                        Sequence(
                            "MATERIALIZED",
                            Ref("ExpressionSegment"),
                            optional=True,
                        ),
                        Sequence(
                            "ALIAS",
                            Ref("ExpressionSegment"),
                            optional=True,
                        ),
                        Sequence(
                            "CODEC",
                            Bracketed(
                                Delimited(
                                    OneOf(
                                        Ref("FunctionSegment"),
                                        Ref("SingleIdentifierGrammar"),
                                    ),
                                    delimiter=Ref("CommaSegment"),
                                ),
                            ),
                            optional=True,
                        ),
                    ),
                    # Type modification without TYPE keyword
                    Sequence(
                        Ref("DatatypeSegment", optional=True),  # Data type
                        Sequence(
                            "DEFAULT",
                            Ref("ExpressionSegment"),
                            optional=True,
                        ),
                        Sequence(
                            "MATERIALIZED",
                            Ref("ExpressionSegment"),
                            optional=True,
                        ),
                        Sequence(
                            "ALIAS",
                            Ref("ExpressionSegment"),
                            optional=True,
                        ),
                        Sequence(
                            "CODEC",
                            Bracketed(
                                Delimited(
                                    OneOf(
                                        Ref("FunctionSegment"),
                                        Ref("SingleIdentifierGrammar"),
                                    ),
                                    delimiter=Ref("CommaSegment"),
                                ),
                            ),
                            optional=True,
                        ),
                    ),
                    # Alias modification
                    Sequence(
                        "ALIAS",
                        Ref("ExpressionSegment"),
                    ),
                    # Remove alias
                    Sequence(
                        "REMOVE",
                        "ALIAS",
                    ),
                    # Remove property
                    Sequence(
                        "REMOVE",
                        OneOf(
                            "ALIAS",
                            "DEFAULT",
                            "MATERIALIZED",
                            "CODEC",
                            "COMMENT",
                            "TTL",
                        ),
                    ),
                    # Modify setting
                    Sequence(
                        "MODIFY",
                        "SETTING",
                        Ref("SingleIdentifierGrammar"),  # Setting name
                        Ref("EqualsSegment"),
                        Ref("LiteralGrammar"),  # Setting value
                    ),
                    # Reset setting
                    Sequence(
                        "RESET",
                        "SETTING",
                        Ref("SingleIdentifierGrammar"),  # Setting name
                    ),
                    optional=True,
                ),
                OneOf(
                    Sequence(
                        "AFTER",
                        Ref("SingleIdentifierGrammar"),  # Column name
                    ),
                    "FIRST",
                    optional=True,
                ),
            ),
            # ALTER TABLE ... ALTER COLUMN name [TYPE] [type]
            Sequence(
                "ALTER",
                "COLUMN",
                Ref("IfExistsGrammar", optional=True),
                Ref("SingleIdentifierGrammar"),  # Column name
                OneOf(
                    # With TYPE keyword
                    Sequence(
                        "TYPE",
                        Ref("DatatypeSegment"),  # Data type
                    ),
                    # Without TYPE keyword
                    Ref("DatatypeSegment"),  # Data type
                ),
                OneOf(
                    Sequence(
                        "AFTER",
                        Ref("SingleIdentifierGrammar"),  # Column name
                    ),
                    "FIRST",
                    optional=True,
                ),
            ),
            # ALTER TABLE ... REMOVE TTL
            Sequence(
                "REMOVE",
                "TTL",
            ),
            # ALTER TABLE ... MODIFY TTL expression
            Sequence(
                "MODIFY",
                "TTL",
                Ref("ExpressionSegment"),
            ),
            # ALTER TABLE ... MODIFY QUERY select_statement
            Sequence(
                "MODIFY",
                "QUERY",
                Ref("SelectStatementSegment"),
            ),
            # ALTER TABLE ... MATERIALIZE COLUMN col
            Sequence(
                "MATERIALIZE",
                "COLUMN",
                Ref("SingleIdentifierGrammar"),  # Column name
                OneOf(
                    Sequence(
                        "IN",
                        "PARTITION",
                        Ref("SingleIdentifierGrammar"),
                    ),
                    Sequence(
                        "IN",
                        "PARTITION",
                        "ID",
                        Ref("QuotedLiteralSegment"),
                    ),
                    optional=True,
                ),
            ),
        ),
    )


class StatementSegment(ansi.StatementSegment):
    """Overriding StatementSegment to allow for additional segment parsing."""

    match_grammar = ansi.StatementSegment.match_grammar.copy(
        insert=[
            Ref("CreateMaterializedViewStatementSegment"),
            Ref("DropDictionaryStatementSegment"),
            Ref("DropQuotaStatementSegment"),
            Ref("DropSettingProfileStatementSegment"),
            Ref("SystemStatementSegment"),
            Ref("RenameStatementSegment"),
            Ref("AlterTableStatementSegment"),
        ]
    )


class LimitClauseComponentSegment(BaseSegment):
    """A component of a `LIMIT` clause.

    https://clickhouse.com/docs/en/sql-reference/statements/select/limit
    """

    type = "limit_clause_component"

    match_grammar = OptionallyBracketed(
        OneOf(
            # Allow a number by itself OR
            Ref("NumericLiteralSegment"),
            # An arbitrary expression
            Ref("ExpressionSegment"),
        )
    )


class LimitClauseSegment(ansi.LimitClauseSegment):
    """Overriding LimitClauseSegment to allow for additional segment parsing."""

    match_grammar: Matchable = Sequence(
        "LIMIT",
        Indent,
        Sequence(
            Ref("LimitClauseComponentSegment"),
            OneOf(
                Sequence(
                    "OFFSET",
                    Ref("LimitClauseComponentSegment"),
                ),
                Sequence(
                    # LIMIT 1,2 only accepts constants
                    # and can't be bracketed like that LIMIT (1, 2)
                    # but can be bracketed like that LIMIT (1), (2)
                    Ref("CommaSegment"),
                    Ref("LimitClauseComponentSegment"),
                ),
                optional=True,
            ),
            Sequence(
                "BY",
                OneOf(
                    Ref("BracketedColumnReferenceListGrammar"),
                    Ref("ColumnReferenceSegment"),
                ),
                optional=True,
            ),
        ),
        Dedent,
    )


class IntervalExpressionSegment(BaseSegment):
    """An interval expression segment.

    https://clickhouse.com/docs/en/sql-reference/data-types/special-data-types/interval
    https://clickhouse.com/docs/en/sql-reference/operators#operator-interval
    """

    type = "interval_expression"
    match_grammar: Matchable = Sequence(
        "INTERVAL",
        OneOf(
            # The Numeric Version
            Sequence(
                Ref("NumericLiteralSegment"),
                Ref("DatetimeUnitSegment"),
            ),
            # The String version
            Ref("QuotedLiteralSegment"),
            # Combine version
            Sequence(
                Ref("QuotedLiteralSegment"),
                Ref("DatetimeUnitSegment"),
            ),
            # With expression as value
            Sequence(
                Ref("ExpressionSegment"),
                Ref("DatetimeUnitSegment"),
            ),
        ),
    )


class ColumnDefinitionSegment(BaseSegment):
    """A column definition, e.g. for CREATE TABLE or ALTER TABLE.

    Supports ClickHouse specific options like CODEC, ALIAS, MATERIALIZED, etc.
    """

    type = "column_definition"
    match_grammar = Sequence(
        OneOf(
            Ref("SingleIdentifierGrammar"),
            Ref("QuotedIdentifierSegment"),
        ),
        Ref("DatatypeSegment"),
        AnyNumberOf(
            OneOf(
                # DEFAULT expression
                Sequence(
                    "DEFAULT",
                    OneOf(
                        Ref("LiteralGrammar"),
                        Ref("FunctionSegment"),
                        Ref("ExpressionSegment"),
                    ),
                ),
                # ALIAS expression
                Sequence(
                    "ALIAS",
                    Ref("ExpressionSegment"),
                ),
                # MATERIALIZED expression
                Sequence(
                    "MATERIALIZED",
                    Ref("ExpressionSegment"),
                ),
                # CODEC(...)
                Sequence(
                    "CODEC",
                    Bracketed(
                        Delimited(
                            OneOf(
                                Ref("FunctionSegment"),
                                Ref("SingleIdentifierGrammar"),
                            ),
                            delimiter=Ref("CommaSegment"),
                        ),
                    ),
                ),
                # COMMENT 'text'
                Sequence(
                    "COMMENT",
                    Ref("QuotedLiteralSegment"),
                ),
                # Column constraint
                Ref("ColumnConstraintSegment"),
            ),
            optional=True,
        ),
    )
