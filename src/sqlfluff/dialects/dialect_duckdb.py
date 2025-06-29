"""The DuckDB dialect.

https://duckdb.org/docs/
"""

from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.core.parser import (
    AnyNumberOf,
    BaseSegment,
    BinaryOperatorSegment,
    Bracketed,
    CodeSegment,
    ComparisonOperatorSegment,
    Dedent,
    Delimited,
    IdentifierSegment,
    ImplicitIndent,
    Indent,
    Matchable,
    Nothing,
    OneOf,
    OptionallyBracketed,
    Ref,
    RegexLexer,
    RegexParser,
    Sequence,
    StringLexer,
    StringParser,
    SymbolSegment,
    TypedParser,
)
from sqlfluff.dialects import dialect_ansi as ansi
from sqlfluff.dialects import dialect_postgres as postgres

ansi_dialect = load_raw_dialect("ansi")
postgres_dialect = load_raw_dialect("postgres")
duckdb_dialect = postgres_dialect.copy_as(
    "duckdb",
    formatted_name="DuckDB",
    docstring="""**Default Casing**: DuckDB stores all identifiers in the case
they were defined, however all identifier resolution is case-insensitive (when
unquoted, and more unusually, *also when quoted*). See the
`DuckDB Identifiers Documentation`_ for more details.

**Quotes**: String Literals: ``''``, Identifiers: ``""`` or ``''``

The dialect for `DuckDB <https://duckdb.org/>`_.

.. _`DuckDB Identifiers Documentation`: https://duckdb.org/docs/sql/dialect/keywords_and_identifiers
""",  # noqa: E501
)

duckdb_dialect.sets("reserved_keywords").update(
    [
        "PIVOT",
        "PIVOT_LONGER",
        "PIVOT_WIDER",
        "UNPIVOT",
    ]
)

duckdb_dialect.sets("unreserved_keywords").update(
    [
        "ANTI",
        "ASOF",
        "GLOB",
        "MACRO",
        "MAP",
        "POSITIONAL",
        "SEMI",
        "STRUCT",
        "VIRTUAL",
    ]
)

duckdb_dialect.add(
    LambdaArrowSegment=StringParser("->", SymbolSegment, type="lambda_arrow"),
    OrIgnoreGrammar=Sequence("OR", "IGNORE"),
    EqualsSegment_a=StringParser("==", ComparisonOperatorSegment),
    UnpackingOperatorSegment=TypedParser("star", SymbolSegment, "unpacking_operator"),
)

duckdb_dialect.replace(
    FunctionNameIdentifierSegment=RegexParser(
        r"[A-Z_][A-Z0-9_$]*",
        CodeSegment,
        type="function_name_identifier",
        anti_template=r"^(STRUCT|UNION|ENUM)$",
    ),
    DivideSegment=OneOf(
        StringParser("//", BinaryOperatorSegment),
        StringParser("/", BinaryOperatorSegment),
    ),
    CreateTableAsStatementSegment=Nothing(),
    UnionGrammar=ansi_dialect.get_grammar("UnionGrammar").copy(
        insert=[
            Sequence("BY", "NAME", optional=True),
        ]
    ),
    JoinLikeClauseGrammar=Sequence(
        AnyNumberOf(
            Ref("FromPivotExpressionSegment"),
            Ref("FromUnpivotExpressionSegment"),
            min_times=1,
        ),
        Ref("AliasExpressionSegment", optional=True),
    ),
    NonSetSelectableGrammar=postgres_dialect.get_grammar(
        "NonSetSelectableGrammar"
    ).copy(
        insert=[
            Ref("SimplifiedPivotExpressionSegment"),
            Ref("SimplifiedUnpivotExpressionSegment"),
        ],
    ),
    NonStandardJoinTypeKeywordsGrammar=OneOf(
        "ANTI",
        "SEMI",
        Sequence(
            "ASOF",
            OneOf(
                Ref("JoinTypeKeywordsGrammar"),
                "ANTI",
                "SEMI",
                optional=True,
            ),
        ),
    ),
    HorizontalJoinKeywordsGrammar=Ref.keyword("POSITIONAL"),
    FunctionContentsExpressionGrammar=OneOf(
        Ref("LambdaExpressionSegment"),
        Ref("NamedArgumentSegment"),
        Ref("ExpressionSegment"),
    ),
    ColumnsExpressionNameGrammar=Sequence(
        Ref("UnpackingOperatorSegment", optional=True), "COLUMNS"
    ),
    # Uses grammar for LT06 support
    ColumnsExpressionGrammar=Sequence(
        Ref("ColumnsExpressionFunctionNameSegment"),
        Ref("ColumnsExpressionFunctionContentsSegment"),
    ),
    # Matching postgres lower casefold, as it is case-insensitive
    QuotedIdentifierSegment=TypedParser(
        "double_quote", IdentifierSegment, type="quoted_identifier", casefold=str.lower
    ),
    SingleQuotedIdentifierSegment=TypedParser(
        "single_quote", IdentifierSegment, type="quoted_identifier", casefold=str.lower
    ),
    ListComprehensionGrammar=Ref("ListComprehensionExpressionSegment"),
    ComparisonOperatorGrammar=ansi_dialect.get_grammar(
        "ComparisonOperatorGrammar"
    ).copy(
        insert=[
            Ref("EqualsSegment_a"),
            Ref("GlobOperatorSegment"),
        ]
    ),
    LikeGrammar=postgres_dialect.get_grammar("LikeGrammar").copy(
        insert=[Ref.keyword("GLOB")],
    ),
)

duckdb_dialect.insert_lexer_matchers(
    [
        StringLexer("double_divide", "//", CodeSegment),
    ],
    before="divide",
)

duckdb_dialect.patch_lexer_matchers(
    [
        # In DuckDB, a double single/double quote resolves as a single/double quote in
        # the string.
        RegexLexer(
            "single_quote",
            r"'([^']|'')*'",
            CodeSegment,
            segment_kwargs={
                "quoted_value": (r"'((?:[^']|'')*)'", 1),
                "escape_replacements": [(r"''", "'")],
            },
        ),
        RegexLexer(
            "double_quote",
            r'"([^"]|"")*"',
            CodeSegment,
            segment_kwargs={
                "quoted_value": (r'"((?:[^"]|"")*)"', 1),
                "escape_replacements": [(r'""', '"')],
            },
        ),
        RegexLexer("equals", r"==?", CodeSegment),
    ]
)


class StructTypeSegment(ansi.StructTypeSegment):
    """Expression to construct a STRUCT datatype."""

    match_grammar = Sequence(
        "STRUCT",
        Ref("StructTypeSchemaSegment", optional=True),
    )


class StructTypeSchemaSegment(BaseSegment):
    """Expression to construct the schema of a STRUCT datatype."""

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
                ),
            ),
        ),
    )


class MapTypeSegment(ansi.MapTypeSegment):
    """Expression to construct a MAP datatype."""

    match_grammar = Sequence(
        "MAP",
        Ref("MapTypeSchemaSegment", optional=True),
    )


class MapTypeSchemaSegment(BaseSegment):
    """Expression to construct the schema of a MAP datatype."""

    type = "map_type_schema"
    match_grammar = Bracketed(
        Delimited(
            Ref("DatatypeSegment"),
        ),
    )


class InsertStatementSegment(ansi.InsertStatementSegment):
    """An `INSERT` Statement.

    https://duckdb.org/docs/stable/sql/statements/insert.html
    """

    type = "insert_statement"
    match_grammar: Matchable = Sequence(
        "INSERT",
        OneOf(Ref("OrReplaceGrammar"), Ref("OrIgnoreGrammar"), optional=True),
        "INTO",
        Ref("TableReferenceSegment"),
        Ref("AsAliasExpressionSegment", optional=True),
        OneOf(
            Ref("BracketedColumnReferenceListGrammar"),
            Sequence("BY", "POSITION"),
            Sequence("BY", "NAME"),
            optional=True,
        ),
        OneOf(
            Sequence("DEFAULT", "VALUES"),
            Ref("SelectStatementSegment"),
            Sequence(
                Ref("BracketedColumnReferenceListGrammar", optional=True),
                OneOf(
                    Ref("ValuesClauseSegment"),
                    OptionallyBracketed(Ref("SelectStatementSegment")),
                ),
            ),
        ),
        Sequence(
            "ON",
            "CONFLICT",
            Ref("ConflictTargetSegment", optional=True),
            Ref("ConflictActionSegment"),
            optional=True,
        ),
        Sequence(
            "RETURNING",
            OneOf(
                Ref("StarSegment"),
                Delimited(
                    Sequence(
                        Ref("ExpressionSegment"),
                        Ref("AsAliasExpressionSegment", optional=True),
                    ),
                ),
            ),
            optional=True,
        ),
    )


class ColumnConstraintSegment(ansi.ColumnConstraintSegment):
    """A column option; each CREATE TABLE column can have 0 or more.

    https://duckdb.org/docs/sql/statements/create_table
    https://duckdb.org/docs/sql/statements/alter_table
    """

    # Column constraint from
    # https://duckdb.org/docs/sql/statements/create_table
    match_grammar = Sequence(
        OneOf(
            Sequence(Ref.keyword("NOT", optional=True), "NULL"),  # NOT NULL or NULL
            Sequence(
                "CHECK",
                Bracketed(Ref("ExpressionSegment")),
            ),
            Sequence(  # DEFAULT <value>
                "DEFAULT",
                OneOf(
                    Ref("LiteralGrammar"),
                    Ref("ExpressionSegment"),
                ),
            ),
            "UNIQUE",
            Sequence(
                "PRIMARY",
                "KEY",
            ),
            Ref("ReferenceDefinitionGrammar"),
            Sequence(
                "COLLATE",
                Ref("CollationReferenceSegment"),
            ),
        ),
    )


class CreateTableStatementSegment(ansi.CreateTableStatementSegment):
    """A `CREATE TABLE` statement.

    As specified in https://duckdb.org/docs/sql/statements/create_table.html
    """

    match_grammar = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        Ref("TemporaryGrammar", optional=True),
        "TABLE",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        OneOf(
            Sequence(
                "AS",
                OptionallyBracketed(Ref("SelectableGrammar")),
            ),
            # Columns and comment syntax:
            Bracketed(
                Delimited(
                    Sequence(
                        Ref("ColumnReferenceSegment"),
                        OneOf(
                            Sequence(
                                Ref("DatatypeSegment"),
                                AnyNumberOf(
                                    OneOf(
                                        Ref("ColumnConstraintSegment"),
                                    ),
                                ),
                            ),
                            Sequence(
                                Ref(
                                    "DatatypeSegment",
                                    optional=True,
                                    exclude=Ref.keyword("AS"),
                                ),
                                Sequence("GENERATED", "ALWAYS", optional=True),
                                "AS",
                                Bracketed(Ref("ExpressionSegment")),
                                OneOf("STORED", "VIRTUAL", optional=True),
                            ),
                        ),
                    ),
                    Ref("TableConstraintSegment"),
                )
            ),
        ),
    )


class WildcardExcludeExpressionSegment(BaseSegment):
    """An `EXCLUDE` clause within a wildcard expression."""

    type = "wildcard_exclude"
    match_grammar = Sequence(
        "EXCLUDE",
        OneOf(
            Ref("ColumnReferenceSegment"),
            Bracketed(Delimited(Ref("ColumnReferenceSegment"))),
        ),
    )


class WildcardReplaceExpressionSegment(BaseSegment):
    """A `REPLACE` clause within a wildcard expression."""

    type = "wildcard_replace"
    match_grammar = Sequence(
        "REPLACE",
        OneOf(
            Bracketed(
                Delimited(
                    Sequence(
                        Ref("BaseExpressionElementGrammar"),
                        Ref("AliasExpressionSegment", optional=True),
                    ),
                )
            ),
            Sequence(
                Ref("BaseExpressionElementGrammar"),
                Ref("AliasExpressionSegment", optional=True),
            ),
        ),
    )


class WildcardRenameExpressionSegment(BaseSegment):
    """A `RENAME` clause within a wildcard expression."""

    type = "wildcard_rename"
    match_grammar = Sequence(
        "RENAME",
        OneOf(
            Bracketed(
                Delimited(
                    Sequence(
                        Ref("BaseExpressionElementGrammar"),
                        Ref("AliasExpressionSegment", optional=True),
                    ),
                )
            ),
            Sequence(
                Ref("BaseExpressionElementGrammar"),
                Ref("AliasExpressionSegment", optional=True),
            ),
        ),
    )


class WildcardPatternMatchingSegment(BaseSegment):
    """A pattern matching operator clause within a wildcard expression."""

    type = "wildcard_pattern_matching"
    match_grammar = OneOf(
        Ref("LikeExpressionGrammar"),
        Sequence(
            OneOf(
                Ref("LikeOperatorSegment"),
                Ref("GlobOperatorSegment"),
            ),
            Ref("QuotedLiteralSegment"),
        ),
    )


class WildcardExpressionSegment(ansi.WildcardExpressionSegment):
    """An extension of the star expression for DuckDB."""

    match_grammar = Sequence(
        # *, blah.*, blah.blah.*, etc.
        Ref("WildcardIdentifierSegment"),
        # Optional EXCLUDE or REPLACE clause
        Ref("WildcardExcludeExpressionSegment", optional=True),
        OneOf(
            Sequence(
                Ref("WildcardReplaceExpressionSegment", optional=True),
                Ref("WildcardRenameExpressionSegment", optional=True),
            ),
            Ref("WildcardPatternMatchingSegment"),
            optional=True,
        ),
    )


class SelectClauseElementSegment(ansi.SelectClauseElementSegment):
    """An element in the targets of a select statement."""

    type = "select_clause_element"

    match_grammar = OneOf(
        Sequence(
            Ref("WildcardExpressionSegment"),
        ),
        Sequence(
            Ref(
                "BaseExpressionElementGrammar",
            ),
            Ref("AliasExpressionSegment", optional=True),
        ),
    )


class ColumnsExpressionFunctionContentsSegment(
    ansi.ColumnsExpressionFunctionContentsSegment
):
    """Columns expression in a select statement.

    https://duckdb.org/docs/sql/expressions/star#columns-expression
    """

    type = "function_contents"
    match_grammar = Sequence(
        Bracketed(
            OneOf(
                Ref("WildcardExpressionSegment"),
                Ref("LambdaExpressionSegment"),
                Ref("BaseExpressionElementGrammar"),
            ),
        ),
    )


class LambdaExpressionSegment(BaseSegment):
    """Lambda function used in a function or columns expression.

    https://duckdb.org/docs/sql/functions/lambda
    https://duckdb.org/docs/sql/expressions/star#columns-lambda-function
    """

    type = "lambda_function"
    match_grammar = Sequence(
        OneOf(
            Ref("ParameterNameSegment"),
            Bracketed(Delimited(Ref("ParameterNameSegment"))),
        ),
        Ref("LambdaArrowSegment"),
        Ref("ExpressionSegment"),
    )


class ListComprehensionExpressionSegment(BaseSegment):
    """A list comprehension expression in duckdb.

    https://duckdb.org/docs/sql/functions/list#list-comprehension
    """

    type = "list_comprehension"
    match_grammar = Bracketed(
        Ref("ExpressionSegment"),
        "FOR",
        Ref("ParameterNameSegment"),
        "IN",
        Ref("ExpressionSegment"),
        Sequence("IF", Ref("ExpressionSegment"), optional=True),
        bracket_type="square",
    )


class SelectStatementSegment(ansi.SelectStatementSegment):
    """A duckdb `SELECT` statement including optional Qualify.

    https://duckdb.org/docs/sql/query_syntax/qualify
    """

    type = "select_statement"

    match_grammar = ansi.SelectStatementSegment.match_grammar.copy(
        insert=[Ref("QualifyClauseSegment", optional=True)],
        before=Ref("OrderByClauseSegment", optional=True),
        replace_terminators=True,
        terminators=[
            Ref("SetOperatorSegment"),
            Ref("WithNoSchemaBindingClauseSegment"),
            Ref("WithDataClauseSegment"),
            Sequence("ON", "CONFLICT"),
            "RETURNING",
            Ref("WithCheckOptionSegment"),
            Ref("MetaCommandQueryBufferSegment"),
        ],
    )


class UnorderedSelectStatementSegment(ansi.UnorderedSelectStatementSegment):
    """A `SELECT` statement without any ORDER clauses or later.

    This is designed for use in the context of set operations,
    for other use cases, we should use the main
    SelectStatementSegment.
    """

    type = "select_statement"

    match_grammar: Matchable = Sequence(
        OneOf(
            Sequence(
                Ref("SelectClauseSegment"),
                Ref("FromClauseSegment", optional=True),
            ),
            Sequence(
                # From-First Syntax:
                # https://duckdb.org/docs/sql/query_syntax/from
                Ref("FromClauseSegment"),
                Ref("SelectClauseSegment", optional=True),
            ),
        ),
        Ref("WhereClauseSegment", optional=True),
        Ref("GroupByClauseSegment", optional=True),
        Ref("HavingClauseSegment", optional=True),
        Ref("NamedWindowSegment", optional=True),
        Ref("QualifyClauseSegment", optional=True),
        terminators=[
            Ref("SetOperatorSegment"),
            Ref("OrderByClauseSegment"),
            Ref("LimitClauseSegment"),
            Sequence("ON", "CONFLICT"),
            "RETURNING",
        ],
    )


class TableReferenceSegment(ansi.TableReferenceSegment):
    """A reference to an table, CTE, subquery or alias.

    Overload for DuckDB as only tables can be single quoted identifiers
    when used by the httpfs extension.
    """

    match_grammar = ansi.TableReferenceSegment.match_grammar.copy(
        insert=[Ref("SingleQuotedIdentifierSegment")],
    )


class AliasExpressionSegment(ansi.AliasExpressionSegment):
    """A reference to an object with an `AS` clause.

    The optional AS keyword allows both implicit and explicit aliasing.
    Inherit from ANSI instead of Postgres.
    """


class OrderByClauseSegment(ansi.OrderByClauseSegment):
    """A `ORDER BY` clause like in `SELECT`."""

    match_grammar: Matchable = Sequence(
        "ORDER",
        "BY",
        Indent,
        Delimited(
            Sequence(
                OneOf(
                    "ALL",
                    Ref("ColumnReferenceSegment"),
                    Ref("NumericLiteralSegment"),
                    Ref("ExpressionSegment"),
                ),
                OneOf("ASC", "DESC", optional=True),
                Sequence("NULLS", OneOf("FIRST", "LAST"), optional=True),
            ),
            allow_trailing=True,
            terminators=[Ref("OrderByClauseTerminators")],
        ),
        Dedent,
    )


class GroupByClauseSegment(ansi.GroupByClauseSegment):
    """A `GROUP BY` clause like in `SELECT`."""

    match_grammar: Matchable = Sequence(
        "GROUP",
        "BY",
        Indent,
        Delimited(
            OneOf(
                "ALL",
                Ref("ColumnReferenceSegment"),
                Ref("NumericLiteralSegment"),
                Ref("ExpressionSegment"),
            ),
            allow_trailing=True,
            terminators=[Ref("GroupByClauseTerminatorGrammar")],
        ),
        Dedent,
    )


class QualifyClauseSegment(BaseSegment):
    """A `QUALIFY` clause like in `SELECT`.

    https://duckdb.org/docs/sql/query_syntax/qualify.html
    """

    type = "qualify_clause"
    match_grammar = Sequence(
        "QUALIFY",
        ImplicitIndent,
        OptionallyBracketed(Ref("ExpressionSegment")),
        Dedent,
    )


class ObjectLiteralElementSegment(ansi.ObjectLiteralElementSegment):
    """An object literal element segment."""

    match_grammar: Matchable = Sequence(
        OneOf(
            Ref("NakedIdentifierSegment"),
            Ref("QuotedLiteralSegment"),
        ),
        Ref("ColonSegment"),
        Ref("BaseExpressionElementGrammar"),
    )


class StatementSegment(postgres.StatementSegment):
    """An element in the targets of a select statement."""

    match_grammar = postgres.StatementSegment.match_grammar.copy(
        insert=[
            Ref("SimplifiedPivotExpressionSegment"),
            Ref("SimplifiedUnpivotExpressionSegment"),
        ]
    )


class FromPivotExpressionSegment(BaseSegment):
    """A PIVOT expression."""

    type = "from_pivot_expression"
    match_grammar = Sequence(
        "PIVOT",
        Bracketed(
            Delimited(
                Sequence(
                    Ref("FunctionSegment"),
                    Ref("AliasExpressionSegment", optional=True),
                )
            ),
            "FOR",
            AnyNumberOf(
                Sequence(
                    Ref("SingleIdentifierGrammar"),
                    "IN",
                    Bracketed(Delimited(Ref("LiteralGrammar"))),
                ),
            ),
            Ref("GroupByClauseSegment", optional=True),
            Ref("OrderByClauseSegment", optional=True),
            Ref("LimitClauseSegment", optional=True),
        ),
        reset_terminators=True,
    )


class SimplifiedPivotExpressionSegment(BaseSegment):
    """The DuckDB simplified PIVOT syntax.

    https://duckdb.org/docs/sql/statements/pivot#simplified-pivot-full-syntax-diagram
    """

    type = "simplified_pivot"
    match_grammar = Sequence(
        OneOf("PIVOT", "PIVOT_WIDER"),
        Ref("TableExpressionSegment"),
        Sequence(
            "ON",
            Delimited(
                OneOf(
                    Ref("ColumnReferenceSegment"),
                    Ref("ExpressionSegment"),
                ),
                Sequence(
                    "IN",
                    Bracketed(Delimited(Ref("LiteralGrammar"))),
                    optional=True,
                ),
            ),
            optional=True,
        ),
        Sequence(
            "USING",
            Delimited(
                Sequence(
                    Ref("FunctionSegment"),
                    Ref("AliasExpressionSegment", optional=True),
                ),
            ),
            optional=True,
        ),
        Ref("GroupByClauseSegment", optional=True),
        Ref("OrderByClauseSegment", optional=True),
        Ref("LimitClauseSegment", optional=True),
    )


class FromUnpivotExpressionSegment(BaseSegment):
    """An UNPIVOT expression."""

    type = "from_unpivot_expression"
    match_grammar = Sequence(
        "UNPIVOT",
        Sequence("INCLUDE", "NULLS", optional=True),
        Bracketed(
            OneOf(
                Ref("SingleIdentifierGrammar"),
                Bracketed(Delimited(Ref("SingleIdentifierGrammar"))),
            ),
            "FOR",
            AnyNumberOf(
                Sequence(
                    Ref("SingleIdentifierGrammar"),
                    "IN",
                    Bracketed(
                        Delimited(
                            Sequence(
                                OptionallyBracketed(
                                    Delimited(Ref("SingleIdentifierGrammar"))
                                ),
                                Ref("AliasExpressionSegment", optional=True),
                            ),
                            Ref("ColumnsExpressionGrammar"),
                        ),
                    ),
                ),
                min_times=1,
            ),
        ),
    )


class SimplifiedUnpivotExpressionSegment(BaseSegment):
    """The DuckDB simplified UNPIVOT syntax.

    https://duckdb.org/docs/sql/statements/unpivot#simplified-unpivot-full-syntax-diagram
    """

    type = "simplified_unpivot"
    match_grammar = Sequence(
        OneOf("UNPIVOT", "PIVOT_LONGER"),
        Ref("TableExpressionSegment"),
        "ON",
        Delimited(
            Sequence(
                OneOf(
                    Bracketed(
                        Delimited(
                            Ref("ColumnReferenceSegment"),
                        ),
                    ),
                    Ref("ColumnReferenceSegment"),
                ),
                Ref("AliasExpressionSegment", optional=True),
            ),
            Ref("ColumnsExpressionGrammar"),
        ),
        "INTO",
        "NAME",
        Ref("SingleIdentifierGrammar"),
        "VALUE",
        Delimited(
            Ref("SingleIdentifierGrammar"),
        ),
        Ref("OrderByClauseSegment", optional=True),
        Ref("LimitClauseSegment", optional=True),
    )


class CreateViewStatementSegment(postgres.CreateViewStatementSegment):
    """An `Create VIEW` statement.

    https://duckdb.org/docs/sql/statements/create_view.html
    """

    type = "create_view_statement"

    match_grammar = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        Ref("TemporaryGrammar", optional=True),
        "VIEW",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        Ref("BracketedColumnReferenceListGrammar", optional=True),
        "AS",
        OneOf(
            OptionallyBracketed(Ref("SelectableGrammar")),
            Ref("ValuesClauseSegment"),
        ),
    )


class CreateFunctionStatementSegment(postgres.CreateFunctionStatementSegment):
    """A `CREATE MACRO` or `CREATE FUNCTION` statement.

    https://duckdb.org/docs/sql/statements/create_macro
    """

    match_grammar = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        Ref("TemporaryGrammar", optional=True),
        OneOf("MACRO", "FUNCTION"),
        Ref("FunctionNameSegment"),
        Ref("FunctionParameterListGrammar"),
        "AS",
        OneOf(
            Sequence("TABLE", Indent, Ref("SelectableGrammar"), Dedent),
            Ref("ExpressionSegment"),
        ),
    )


class DropFunctionStatementSegment(postgres.DropFunctionStatementSegment):
    """A `DROP MACRO` or `DROP FUNCTION` statement.

    https://duckdb.org/docs/sql/statements/drop.html
    """

    match_grammar = Sequence(
        "DROP",
        OneOf("MACRO", "FUNCTION"),
        Ref.keyword("TABLE", optional=True),
        Ref("IfExistsGrammar", optional=True),
        Ref("FunctionNameSegment"),
        Ref("DropBehaviorGrammar", optional=True),
    )


class CreateTypeStatementSegment(postgres.CreateTypeStatementSegment):
    """A `CREATE TYPE` statement.

    https://duckdb.org/docs/sql/statements/create_type.html
    """

    match_grammar = Sequence(
        "CREATE",
        "TYPE",
        Ref("DatatypeSegment"),
        "AS",
        OneOf(
            Ref("DatatypeSegment"),
            Sequence("ENUM", Bracketed(Delimited(Ref("QuotedLiteralSegment")))),
            Ref("StructTypeSegment"),
            Sequence("UNION", Ref("StructTypeSchemaSegment")),
        ),
    )
