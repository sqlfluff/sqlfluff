"""The EXASOL dialect.

https://docs.exasol.com
https://docs.exasol.com/sql_references/sqlstandardcompliance.htm
"""

from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.core.parser import (
    AnyNumberOf,
    Anything,
    BaseFileSegment,
    BaseSegment,
    Bracketed,
    CodeSegment,
    CommentSegment,
    Dedent,
    Delimited,
    Indent,
    LiteralKeywordSegment,
    LiteralSegment,
    MultiStringParser,
    NewlineSegment,
    Nothing,
    OneOf,
    OptionallyBracketed,
    ParseMode,
    Ref,
    RegexLexer,
    RegexParser,
    Sequence,
    StringLexer,
    StringParser,
    SymbolSegment,
    TypedParser,
)
from sqlfluff.core.parser.segments.generator import SegmentGenerator
from sqlfluff.dialects import dialect_ansi as ansi
from sqlfluff.dialects.dialect_exasol_keywords import (
    BARE_FUNCTIONS,
    RESERVED_KEYWORDS,
    SESSION_PARAMETERS,
    SYSTEM_PARAMETERS,
    UNRESERVED_KEYWORDS,
)

ansi_dialect = load_raw_dialect("ansi")
exasol_dialect = ansi_dialect.copy_as("exasol")

# Clear ANSI Keywords and add all EXASOL keywords
exasol_dialect.sets("unreserved_keywords").clear()
exasol_dialect.sets("unreserved_keywords").update(UNRESERVED_KEYWORDS)
exasol_dialect.sets("reserved_keywords").clear()
exasol_dialect.sets("reserved_keywords").update(RESERVED_KEYWORDS)
exasol_dialect.sets("bare_functions").clear()
exasol_dialect.sets("bare_functions").update(BARE_FUNCTIONS)
exasol_dialect.sets("session_parameters").clear()
exasol_dialect.sets("session_parameters").update(SESSION_PARAMETERS)
exasol_dialect.sets("system_parameters").clear()
exasol_dialect.sets("system_parameters").update(SYSTEM_PARAMETERS)

exasol_dialect.sets("date_part_function_name").clear()
exasol_dialect.sets("date_part_function_name").update(
    [
        "ADD_DAYS",
        "ADD_HOURS",
        "ADD_MINUTES",
        "ADD_MONTHS",
        "ADD_SECONDS",
        "ADD_WEEKS",
        "ADD_YEARS",
    ]
)

exasol_dialect.insert_lexer_matchers(
    [
        RegexLexer("lua_nested_quotes", r"\[={1,3}\[.*\]={1,3}\]", CodeSegment),
        RegexLexer("lua_multiline_quotes", r"\[{2}([^[\\]|\\.)*\]{2}", CodeSegment),
        # This matches escaped identifier e.g. [day]. There can be reserved keywords
        # within the square brackets.
        RegexLexer(
            "escaped_identifier",
            r"\[\w+\]",
            CodeSegment,
        ),
        RegexLexer(
            "udf_param_dot_syntax",
            r"\.{3}",
            CodeSegment,
        ),
        RegexLexer(
            "range_operator",
            r"\.{2}",
            SymbolSegment,
        ),
        StringLexer("hash", "#", CodeSegment),
        StringLexer("walrus_operator", ":=", CodeSegment),
        RegexLexer(
            "function_script_terminator",
            r"\n/\n|\n/$",
            SymbolSegment,
            subdivider=RegexLexer(
                "newline",
                r"(\n|\r\n)+",
                NewlineSegment,
            ),
        ),
        RegexLexer("at_sign_literal", r"@[a-zA-Z_][\w]*", CodeSegment),
        RegexLexer("dollar_literal", r"[$][a-zA-Z0-9_.]*", CodeSegment),
    ],
    before="like_operator",
)

exasol_dialect.patch_lexer_matchers(
    [
        # In EXASOL, a double single/double quote resolves as a single/double quote in
        # the string. It's also used for escaping single quotes inside of STATEMENT
        # strings like in the IMPORT function
        # https://docs.exasol.com/sql_references/basiclanguageelements.htm#Delimited_Identifiers
        # https://docs.exasol.com/sql_references/literals.htm
        RegexLexer(
            "single_quote",
            r"'([^']|'')*'",
            CodeSegment,
        ),
        RegexLexer(
            "double_quote",
            r'"([^"]|"")*"',
            CodeSegment,
        ),
        RegexLexer(
            "inline_comment",
            r"--[^\n]*",
            CommentSegment,
            segment_kwargs={"trim_start": ("--")},
        ),
    ]
)

exasol_dialect.add(
    PasswordLiteralSegment=TypedParser(
        "double_quote", CodeSegment, type="password_literal"
    ),
    UDFParameterDotSyntaxSegment=TypedParser(
        "udf_param_dot_syntax", SymbolSegment, type="identifier"
    ),
    RangeOperator=TypedParser("range_operator", SymbolSegment, type="range_operator"),
    UnknownSegment=StringParser(
        "unknown", LiteralKeywordSegment, type="boolean_literal"
    ),
    ForeignKeyReferencesClauseGrammar=Sequence(
        "REFERENCES",
        Ref("TableReferenceSegment"),
        Ref("BracketedColumnReferenceListGrammar", optional=True),
    ),
    ColumnReferenceListGrammar=Delimited(
        Ref("ColumnReferenceSegment"),
    ),
    TableDistributeByGrammar=Sequence(
        "DISTRIBUTE",
        "BY",
        Delimited(
            Ref("ColumnReferenceSegment"),
            terminators=[
                Ref("TablePartitionByGrammar"),
                Ref("DelimiterGrammar"),
            ],
        ),
    ),
    TablePartitionByGrammar=Sequence(
        "PARTITION",
        "BY",
        Delimited(
            Ref("ColumnReferenceSegment"),
            terminators=[
                Ref("TableDistributeByGrammar"),
                Ref("DelimiterGrammar"),
            ],
        ),
    ),
    TableConstraintEnableDisableGrammar=OneOf("ENABLE", "DISABLE"),
    EscapedIdentifierSegment=TypedParser(
        "escaped_identifier", SymbolSegment, type="identifier"
    ),
    SessionParameterSegment=SegmentGenerator(
        lambda dialect: MultiStringParser(
            dialect.sets("session_parameters"),
            CodeSegment,
            type="session_parameter",
        )
    ),
    SystemParameterSegment=SegmentGenerator(
        lambda dialect: MultiStringParser(
            dialect.sets("system_parameters"),
            CodeSegment,
            type="system_parameter",
        )
    ),
    UDFParameterGrammar=OneOf(
        # (A NUMBER, B VARCHAR) or (...)
        Delimited(Ref("ColumnDatatypeSegment")),
        Ref("UDFParameterDotSyntaxSegment"),
    ),
    FunctionScriptTerminatorSegment=TypedParser(
        "function_script_terminator",
        SymbolSegment,
        type="function_script_terminator",
    ),
    WalrusOperatorSegment=StringParser(":=", SymbolSegment, type="assignment_operator"),
    VariableNameSegment=RegexParser(
        r"[A-Z][A-Z0-9_]*",
        CodeSegment,
        type="variable",
    ),
)

exasol_dialect.replace(
    SingleIdentifierGrammar=OneOf(
        Ref("NakedIdentifierSegment"),
        Ref("QuotedIdentifierSegment"),
        Ref("EscapedIdentifierSegment"),
    ),
    ParameterNameSegment=RegexParser(
        r"\"?[A-Z][A-Z0-9_]*\"?",
        CodeSegment,
        type="parameter",
    ),
    LikeGrammar=Ref.keyword("LIKE"),
    NanLiteralSegment=Nothing(),
    SelectClauseTerminatorGrammar=OneOf(
        "FROM",
        "WHERE",
        Sequence("ORDER", "BY"),
        "LIMIT",
        Ref("SetOperatorSegment"),
        Ref("WithDataClauseSegment"),
        Ref("CommentClauseSegment"),
    ),
    FromClauseTerminatorGrammar=OneOf(
        "WHERE",
        "CONNECT",
        "START",
        "PREFERRING",
        "LIMIT",
        Sequence("GROUP", "BY"),
        Sequence("ORDER", "BY"),
        "HAVING",
        "QUALIFY",
        Ref("SetOperatorSegment"),
        Ref("WithDataClauseSegment"),
        Ref("CommentClauseSegment"),
    ),
    WhereClauseTerminatorGrammar=OneOf(
        "CONNECT",
        "START",
        "PREFERRING",
        "LIMIT",
        Sequence("GROUP", "BY"),
        Sequence("ORDER", "BY"),
        "HAVING",
        "QUALIFY",
        Ref("SetOperatorSegment"),
        Ref("WithDataClauseSegment"),
        Ref("CommentClauseSegment"),
    ),
    DateTimeLiteralGrammar=Sequence(
        OneOf("DATE", "TIMESTAMP"),
        TypedParser("single_quote", LiteralSegment, type="date_constructor_literal"),
    ),
    CharCharacterSetGrammar=OneOf(
        "UTF8",
        "ASCII",
    ),
    PreTableFunctionKeywordsGrammar=Ref.keyword("TABLE"),
    BooleanLiteralGrammar=OneOf(
        Ref("TrueSegment"), Ref("FalseSegment"), Ref("UnknownSegment")
    ),
    PostFunctionGrammar=OneOf(
        Ref("EmitsSegment"),  # e.g. JSON_EXTRACT()
        Sequence(
            Sequence(OneOf("IGNORE", "RESPECT"), "NULLS", optional=True),
            Ref("OverClauseSegment"),
        ),
    ),
)


############################
# SELECT
############################


class UnorderedSelectStatementSegment(BaseSegment):
    """A `SELECT` statement without any ORDER clauses or later.

    This is designed for use in the context of set operations,
    for other use cases, we should use the main
    SelectStatementSegment.
    """

    type = "select_statement"

    match_grammar = Sequence(
        Ref("SelectClauseSegment"),
        Ref("FromClauseSegment", optional=True),
        Ref("ReferencingClauseSegment", optional=True),
        Ref("WhereClauseSegment", optional=True),
        Ref("ConnectByClauseSegment", optional=True),
        Ref("PreferringClauseSegment", optional=True),
        Ref("GroupByClauseSegment", optional=True),
        Ref("HavingClauseSegment", optional=True),
        Ref("QualifyClauseSegment", optional=True),
        terminators=[
            Ref("SetOperatorSegment"),
            Ref("WithDataClauseSegment"),
            Ref("CommentClauseSegment"),  # within CREATE TABLE / VIEW statements
            Ref("OrderByClauseSegment"),
            Ref("LimitClauseSegment"),
        ],
        parse_mode=ParseMode.GREEDY_ONCE_STARTED,
    )


class SelectStatementSegment(BaseSegment):
    """A `SELECT` statement.

    https://docs.exasol.com/sql/select.htm
    """

    type = "select_statement"

    # Inherit most of the match grammar from the original.
    match_grammar = UnorderedSelectStatementSegment.match_grammar.copy(
        insert=[
            Ref("OrderByClauseSegment", optional=True),
            Ref("LimitClauseSegment", optional=True),
        ],
        terminators=[
            Ref("SetOperatorSegment"),
            Ref("WithDataClauseSegment"),
            Ref("CommentClauseSegment"),  # within CREATE TABLE / VIEW statements
        ],
        # Replace terminators because we're removing some.
        replace_terminators=True,
    )


class SelectClauseSegment(BaseSegment):
    """A group of elements in a select target statement."""

    type = "select_clause"
    match_grammar = Sequence(
        "SELECT",
        Ref("SelectClauseModifierSegment", optional=True),
        Indent,
        Delimited(
            Ref(
                "SelectClauseElementSegment",
                exclude=OneOf(
                    Sequence(
                        Ref.keyword("WITH", optional=True),
                        "INVALID",
                        OneOf("FOREIGN", "PRIMARY"),
                    ),
                    Sequence("INTO", "TABLE"),
                ),
            ),
            allow_trailing=True,
            optional=True,  # optional in favour of SELECT INVALID....
        ),
        Ref("WithInvalidForeignKeySegment", optional=True),
        Ref("WithInvalidUniquePKSegment", optional=True),
        Ref("IntoTableSegment", optional=True),
        Dedent,
        terminators=[Ref("SelectClauseTerminatorGrammar")],
        parse_mode=ParseMode.GREEDY_ONCE_STARTED,
    )


class WithInvalidUniquePKSegment(BaseSegment):
    """`WITH INVALID UNIQUE` or `WITH INVALID PRIMARY KEY` clause within `SELECT`."""

    type = "with_invalid_unique_pk_clause"
    match_grammar = Sequence(
        Ref.keyword("WITH", optional=True),
        "INVALID",
        OneOf("UNIQUE", Ref("PrimaryKeyGrammar")),
        Ref("BracketedColumnReferenceListGrammar"),
    )


class WithInvalidForeignKeySegment(BaseSegment):
    """`WITH INVALID FOREIGN KEY` clause within `SELECT`."""

    type = "with_invalid_foreign_key_clause"
    match_grammar = Sequence(
        Ref.keyword("WITH", optional=True),
        "INVALID",
        Ref("ForeignKeyGrammar"),
        Ref("BracketedColumnReferenceListGrammar"),
    )


class ReferencingClauseSegment(BaseSegment):
    """Part of `WITH INVALID FOREIGN KEY` clause within `SELECT`."""

    type = "referencing_clause"
    match_grammar = Sequence(
        "REFERENCING",
        Ref("TableReferenceSegment"),
        Ref("BracketedColumnReferenceListGrammar", optional=True),
    )


class IntoTableSegment(BaseSegment):
    """`INTO TABLE` clause within `SELECT`."""

    type = "into_table_clause"
    match_grammar = Sequence("INTO", "TABLE", Ref("TableReferenceSegment"))


class TableExpressionSegment(BaseSegment):
    """The main table expression e.g. within a FROM clause."""

    type = "table_expression"
    match_grammar = OneOf(
        Ref("BareFunctionSegment"),
        Ref("FunctionSegment"),
        Ref("TableReferenceSegment"),
        Bracketed(Ref("SelectableGrammar")),
        Ref("ValuesRangeClauseSegment"),
        Ref("ValuesClauseSegment"),
        Ref("ImportStatementSegment"),  # subimport
        Ref("ExplainVirtualSegment"),
    )


class ValuesClauseSegment(BaseSegment):
    """A `VALUES` clause within in `WITH` or `SELECT`."""

    type = "values_clause"
    match_grammar = Sequence(
        "VALUES",
        Delimited(
            OneOf(
                Bracketed(
                    Delimited(
                        "DEFAULT",
                        Ref("LiteralGrammar"),
                        Ref("ExpressionSegment"),
                    ),
                    parse_mode=ParseMode.GREEDY,
                ),
                Delimited(
                    "DEFAULT",
                    Ref("ExpressionSegment"),
                ),
            ),
        ),
        Ref("AliasExpressionSegment", optional=True),
    )


class ValuesRangeClauseSegment(BaseSegment):
    """A `VALUES BETWEEN` clause within a `SELECT` statement.

    Supported since Exasol 7.1!
    """

    type = "values_range_clause"
    match_grammar = Sequence(
        "VALUES",
        "BETWEEN",
        Ref("NumericLiteralSegment"),
        "AND",
        Ref("NumericLiteralSegment"),
        Sequence("WITH", "STEP", Ref("NumericLiteralSegment"), optional=True),
    )


class SetOperatorSegment(BaseSegment):
    """A set operator such as Union, Minus, Except or Intersect."""

    type = "set_operator"
    match_grammar = OneOf(
        Sequence("UNION", Ref.keyword("ALL", optional=True)),
        "INTERSECT",
        OneOf("MINUS", "EXCEPT"),
    )


class ConnectByClauseSegment(BaseSegment):
    """`CONNECT BY` clause within a select statement."""

    type = "connect_by_clause"
    match_grammar = OneOf(
        Sequence(
            "CONNECT",
            "BY",
            Ref.keyword("NOCYCLE", optional=True),
            Delimited(
                Ref("ExpressionSegment"),
                delimiter="AND",
                terminators=["START"],
            ),
            Sequence("START", "WITH", Ref("ExpressionSegment"), optional=True),
        ),
        Sequence(
            "START",
            "WITH",
            Ref("ExpressionSegment"),
            "CONNECT",
            "BY",
            Ref.keyword("NOCYCLE", optional=True),
            Delimited(Ref("ExpressionSegment"), delimiter="AND"),
        ),
    )


class GroupByClauseSegment(BaseSegment):
    """A `GROUP BY` clause like in `SELECT`."""

    type = "groupby_clause"
    match_grammar = Sequence(
        "GROUP",
        "BY",
        Indent,
        Delimited(
            OneOf(
                Ref("ColumnReferenceSegment"),
                # Can `GROUP BY 1`
                Ref("NumericLiteralSegment"),
                # Can `GROUP BY coalesce(col, 1)`
                Ref("CubeRollupClauseSegment"),
                Ref("GroupingSetsClauseSegment"),
                Ref("ExpressionSegment"),
                Bracketed(),  # Allows empty parentheses
            ),
            terminators=[
                Sequence("ORDER", "BY"),
                "LIMIT",
                "HAVING",
                "QUALIFY",
                Ref("SetOperatorSegment"),
            ],
        ),
        Dedent,
    )


class QualifyClauseSegment(BaseSegment):
    """`QUALIFY` clause within `SELECT`."""

    type = "qualify_clause"
    match_grammar = Sequence("QUALIFY", Ref("ExpressionSegment"))


class LimitClauseSegment(BaseSegment):
    """A `LIMIT` clause like in `SELECT`."""

    type = "limit_clause"
    match_grammar = Sequence(
        "LIMIT",
        OneOf(
            Sequence(  # offset, count
                Ref("NumericLiteralSegment"),
                Ref("CommaSegment"),
                Ref("NumericLiteralSegment"),
            ),
            Sequence(  # count [OFFSET offset]
                Ref("NumericLiteralSegment"),
                Sequence("OFFSET", Ref("NumericLiteralSegment"), optional=True),
            ),
        ),
    )


class LocalAliasSegment(BaseSegment):
    """The `LOCAL.ALIAS` syntax allows to use a alias name of a column within clauses.

    E.g.
    `SELECT ABS(x) AS x FROM t WHERE local.x>10`

    This is supported by: `SELECT`, `WHERE`, `GROUP BY`, `ORDER BY`, `HAVING`, `QUALIFY`

    Note: it's not necessary to use `LOCAL` within `ÒRDER BY` and `QUALIFY` because the
    alias could be accessed directly (...but we can).
    """

    type = "local_alias_segment"
    match_grammar = Sequence("LOCAL", Ref("DotSegment"), Ref("SingleIdentifierGrammar"))


############################
# SCHEMA
############################


class CreateSchemaStatementSegment(BaseSegment):
    """A `CREATE SCHEMA` statement.

    https://docs.exasol.com/sql/create_schema.htm
    """

    type = "create_schema_statement"
    is_ddl = True
    is_dml = False
    is_dql = False
    is_dcl = False
    match_grammar = Sequence(
        "CREATE",
        "SCHEMA",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("SchemaReferenceSegment"),
    )


class CreateVirtualSchemaStatementSegment(BaseSegment):
    """A `CREATE VIRTUAL SCHEMA` statement.

    https://docs.exasol.com/sql/create_schema.htm
    """

    type = "create_virtual_schema_statement"
    is_ddl = True
    is_dml = False
    is_dql = False
    is_dcl = False
    match_grammar = Sequence(
        "CREATE",
        "VIRTUAL",
        "SCHEMA",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("SchemaReferenceSegment"),
        "USING",
        Ref("ObjectReferenceSegment"),
        Ref.keyword("WITH", optional=True),
        AnyNumberOf(
            Sequence(
                Ref("ParameterNameSegment"),
                Ref("EqualsSegment"),
                Ref("LiteralGrammar"),
            )
        ),
    )


class AlterSchemaStatementSegment(BaseSegment):
    """A `ALTER VIRTUAL SCHEMA` statement.

    https://docs.exasol.com/sql/alter_schema.htm
    """

    type = "alter_schema_statement"

    is_ddl = True
    is_dml = False
    is_dql = False
    is_dcl = False
    match_grammar = Sequence(
        "ALTER",
        "SCHEMA",
        Ref("SchemaReferenceSegment"),
        OneOf(
            Sequence(
                "SET",
                "RAW_SIZE_LIMIT",
                Ref("EqualsSegment"),
                AnyNumberOf(Ref("NumericLiteralSegment"), Ref("StarSegment")),
            ),
            Sequence("CHANGE", "OWNER", Ref("SingleIdentifierGrammar")),
        ),
    )


class AlterVirtualSchemaStatementSegment(BaseSegment):
    """A `ALTER VIRTUAL SCHEMA` statement.

    https://docs.exasol.com/sql/alter_schema.htm
    """

    type = "alter_virtual_schema_statement"

    is_ddl = True
    is_dml = False
    is_dql = False
    is_dcl = False
    match_grammar = Sequence(
        "ALTER",
        "VIRTUAL",
        "SCHEMA",
        Ref("SchemaReferenceSegment"),
        OneOf(
            Sequence(
                "SET",
                AnyNumberOf(
                    Sequence(
                        Ref("ColumnReferenceSegment"),
                        Ref("EqualsSegment"),
                        Ref("LiteralGrammar"),
                    )
                ),
            ),
            Sequence(
                "REFRESH",
                Sequence(
                    "TABLES",
                    Delimited(Ref("TableReferenceSegment")),
                    optional=True,
                ),
            ),
            Sequence("CHANGE", "OWNER", Ref("SingleIdentifierGrammar")),
        ),
    )


class DropSchemaStatementSegment(BaseSegment):
    """A `DROP SCHEMA` statement for EXASOL schema.

    https://docs.exasol.com/sql/drop_schema.htm
    """

    type = "drop_schema_statement"

    is_ddl = True
    is_dml = False
    is_dql = False
    is_dcl = False

    match_grammar = Sequence(
        "DROP",
        Ref.keyword("FORCE", optional=True),
        Ref.keyword("VIRTUAL", optional=True),
        "SCHEMA",
        Ref("IfExistsGrammar", optional=True),
        Ref("SchemaReferenceSegment"),
        Ref("DropBehaviorGrammar", optional=True),
    )


############################
# VIEW
############################
class ViewReferenceSegment(ansi.ObjectReferenceSegment):
    """A reference to an schema."""

    type = "view_reference"


class CreateViewStatementSegment(BaseSegment):
    """A `CREATE VIEW` statement.

    https://docs.exasol.com/sql/create_view.htm
    """

    type = "create_view_statement"

    is_ddl = True
    is_dml = False
    is_dql = False
    is_dcl = False
    match_grammar = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        Ref.keyword("FORCE", optional=True),
        "VIEW",
        Ref("ViewReferenceSegment"),
        Bracketed(
            Delimited(
                Sequence(
                    Ref("ColumnReferenceSegment"),
                    Ref("CommentClauseSegment", optional=True),
                ),
            ),
            optional=True,
        ),
        "AS",
        OptionallyBracketed(Ref("SelectableGrammar")),
        Ref("CommentClauseSegment", optional=True),
    )


class DropViewStatementSegment(BaseSegment):
    """A `DROP VIEW` statement with CASCADE and RESTRICT option.

    https://docs.exasol.com/sql/drop_view.htm
    """

    type = "drop_view_statement"

    is_ddl = True
    is_dml = False
    is_dql = False
    is_dcl = False

    match_grammar = Sequence(
        "DROP",
        "VIEW",
        Ref("IfExistsGrammar", optional=True),
        Ref("ViewReferenceSegment"),
        Ref("DropBehaviorGrammar", optional=True),
    )


############################
# TABLE
############################
class CreateTableStatementSegment(BaseSegment):
    """A `CREATE TABLE` statement.

    https://docs.exasol.com/sql/create_table.htm
    """

    type = "create_table_statement"

    is_ddl = True
    is_dml = False
    is_dql = False
    is_dcl = False
    match_grammar = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        "TABLE",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        OneOf(
            # Columns and comment syntax:
            Bracketed(
                Sequence(
                    Delimited(
                        Ref("TableContentDefinitionSegment"),
                    ),
                    Sequence(
                        Ref("CommaSegment"),
                        Ref("TableDistributionPartitionClause"),
                        optional=True,
                    ),
                ),
            ),
            # Create AS syntax:
            Sequence(
                "AS",
                Ref("SelectableGrammar"),
                Ref("WithDataClauseSegment", optional=True),
            ),
            # Create like syntax
            Ref("CreateTableLikeClauseSegment"),
        ),
        Ref("CommentClauseSegment", optional=True),
    )


class TableContentDefinitionSegment(BaseSegment):
    """The table content definition."""

    type = "table_content_definition"
    match_grammar = OneOf(
        Ref("ColumnDefinitionSegment"),
        Ref("TableOutOfLineConstraintSegment"),
        Ref("CreateTableLikeClauseSegment"),
    )


class ColumnDatatypeSegment(BaseSegment):
    """sequence of column and datatype definition."""

    type = "column_datatype_definition"
    match_grammar = Sequence(
        Ref("SingleIdentifierGrammar"),
        Ref("DatatypeSegment"),
    )


class BracketedArguments(ansi.BracketedArguments):
    """A series of bracketed arguments.

    e.g. the bracketed part of numeric(1, 3)
    """

    match_grammar = Bracketed(
        # The brackets might be empty for some cases...
        Delimited(Ref("NumericLiteralSegment"), optional=True),
        # In exasol, some types offer on optional MAX
        # qualifier of BIT, BYTE or CHAR
        OneOf("BIT", "BYTE", "CHAR", optional=True),
    )


class DatatypeSegment(BaseSegment):
    """A data type segment.

    Supports all Exasol datatypes and their aliases
    https://docs.exasol.com/sql_references/data_types/datatypedetails.htm
    https://docs.exasol.com/sql_references/data_types/datatypealiases.htm
    .
    """

    type = "data_type"
    match_grammar = OneOf(
        # Numeric Data Types
        Sequence(
            OneOf("DECIMAL", "DEC", "NUMBER", "NUMERIC"),
            Ref("BracketedArguments", optional=True),
        ),
        "BIGINT",
        Sequence("DOUBLE", Ref.keyword("PRECISION", optional=True)),
        "FLOAT",
        "INT",
        "INTEGER",
        "REAL",
        "SHORTINT",
        "TINYINT",
        "SMALLINT",
        OneOf("BOOLEAN", "BOOL"),
        OneOf(
            "DATE",
            Sequence(
                "TIMESTAMP", Sequence("WITH", "LOCAL", "TIME", "ZONE", optional=True)
            ),
        ),
        Sequence(
            "INTERVAL",
            "YEAR",
            Ref("BracketedArguments", optional=True),
            "TO",
            "MONTH",
        ),
        Sequence(
            "INTERVAL",
            "DAY",
            Ref("BracketedArguments", optional=True),
            "TO",
            "SECOND",
            Ref("BracketedArguments", optional=True),
        ),
        Sequence(
            "GEOMETRY",
            Ref("BracketedArguments", optional=True),
        ),
        Sequence(
            "HASHTYPE",
            Ref("BracketedArguments", optional=True),
        ),
        Sequence(
            OneOf(
                Sequence(
                    OneOf(
                        Sequence("CHAR", Ref.keyword("VARYING", optional=True)),
                        "VARCHAR",
                        "VARCHAR2",
                        "NCHAR",
                        "NVARCHAR",
                        "NVARCHAR2",
                    ),
                    Ref("BracketedArguments", optional=True),
                ),
                Sequence("LONG", "VARCHAR"),
                Sequence(
                    "CHARACTER",
                    Sequence(
                        OneOf(Sequence("LARGE", "OBJECT"), "VARYING", optional=True),
                        Ref("BracketedArguments", optional=True),
                    ),
                ),
                Sequence(
                    "CLOB",
                    Ref("BracketedArguments", optional=True),
                ),
            ),
            Ref("CharCharacterSetGrammar", optional=True),
        ),
    )


class IntervalExpressionSegment(BaseSegment):
    """An interval expression segment.

    https://docs.exasol.com/db/latest/sql_references/literals.htm
    """

    type = "interval_expression"
    match_grammar = Sequence(
        "INTERVAL",
        Ref("QuotedLiteralSegment"),
        OneOf(
            # INTERVAL '5' MONTH
            # INTERVAL '130' MONTH (3)
            Sequence(
                "MONTH",
                Bracketed(Ref("NumericLiteralSegment"), optional=True),
            ),
            # INTERVAL '27' YEAR
            # INTERVAL '100-1' YEAR(3) TO MONTH
            Sequence(
                "YEAR",
                Bracketed(Ref("NumericLiteralSegment"), optional=True),
                Sequence("TO", "MONTH", optional=True),
            ),
            # INTERVAL '5' DAY
            # INTERVAL '100' HOUR(3)
            # INTERVAL '1.99999' SECOND(2,2)
            # INTERVAL '23:10:59.123' HOUR(2) TO SECOND(3)
            Sequence(
                OneOf(
                    Sequence(
                        OneOf("DAY", "HOUR", "MINUTE"),
                        Bracketed(Ref("NumericLiteralSegment"), optional=True),
                    ),
                    Sequence(
                        "SECOND",
                        Bracketed(
                            Delimited(Ref("NumericLiteralSegment")),
                            optional=True,
                        ),
                    ),
                ),
                Sequence(
                    "TO",
                    OneOf(
                        "HOUR",
                        "MINUTE",
                        Sequence(
                            "SECOND",
                            Bracketed(Ref("NumericLiteralSegment"), optional=True),
                        ),
                    ),
                    optional=True,
                ),
            ),
        ),
    )


class ColumnDefinitionSegment(BaseSegment):
    """Column definition within a `CREATE / ALTER TABLE` statement."""

    type = "column_definition"
    match_grammar = Sequence(
        Ref("ColumnDatatypeSegment"),
        Ref("ColumnConstraintSegment", optional=True),
    )


class ColumnConstraintSegment(ansi.ColumnConstraintSegment):
    """A column option; each CREATE TABLE column can have 0 or more."""

    match_grammar = Sequence(
        OneOf(
            Sequence(
                "DEFAULT", OneOf(Ref("LiteralGrammar"), Ref("BareFunctionSegment"))
            ),
            Sequence(
                # IDENTITY(1000) or IDENTITY 1000 or IDENTITY
                "IDENTITY",
                OptionallyBracketed(Ref("NumericLiteralSegment"), optional=True),
            ),
            optional=True,
        ),
        Ref("TableInlineConstraintSegment", optional=True),
        Ref("CommentClauseSegment", optional=True),
    )


class TableInlineConstraintSegment(BaseSegment):
    """Inline table constraint for CREATE / ALTER TABLE."""

    type = "table_constraint_definition"
    match_grammar = Sequence(
        Sequence(
            "CONSTRAINT",
            Ref(
                "SingleIdentifierGrammar",
                # exclude UNRESERVED_KEYWORDS which could used as NakedIdentifier
                # to make e.g. `id NUMBER CONSTRAINT PRIMARY KEY` work (which is equal
                # to just `id NUMBER PRIMARY KEY`)
                exclude=OneOf("NOT", "NULL", "PRIMARY", "FOREIGN"),
                optional=True,
            ),
            optional=True,
        ),
        OneOf(
            # (NOT) NULL
            Sequence(Ref.keyword("NOT", optional=True), "NULL"),
            # PRIMARY KEY
            Ref("PrimaryKeyGrammar"),
            # FOREIGN KEY
            Ref("ForeignKeyReferencesClauseGrammar"),
        ),
        Ref("TableConstraintEnableDisableGrammar", optional=True),
    )


class TableOutOfLineConstraintSegment(BaseSegment):
    """Out of line table constraint for CREATE / ALTER TABLE."""

    type = "table_constraint_definition"
    match_grammar = Sequence(
        Sequence(
            "CONSTRAINT",
            Ref(
                "SingleIdentifierGrammar",
                # exclude UNRESERVED_KEYWORDS which could used as NakedIdentifier
                # to make e.g. `id NUMBER, CONSTRAINT PRIMARY KEY(id)` work (which is
                # equal to just `id NUMBER, PRIMARY KEY(id)`)
                exclude=OneOf("NOT", "NULL", "PRIMARY", "FOREIGN"),
                optional=True,
            ),
            optional=True,
        ),
        OneOf(
            # PRIMARY KEY
            Sequence(
                Ref("PrimaryKeyGrammar"),
                Ref("BracketedColumnReferenceListGrammar"),
            ),
            # FOREIGN KEY
            Sequence(
                Ref("ForeignKeyGrammar"),
                Ref("BracketedColumnReferenceListGrammar"),
                Ref("ForeignKeyReferencesClauseGrammar"),
            ),
        ),
        Ref("TableConstraintEnableDisableGrammar", optional=True),
    )


class CreateTableLikeClauseSegment(BaseSegment):
    """`CREATE TABLE` LIKE clause."""

    type = "table_like_clause"
    match_grammar = Sequence(
        "LIKE",
        Ref("TableReferenceSegment"),
        Bracketed(
            Delimited(
                Sequence(
                    Ref("SingleIdentifierGrammar"),
                    Ref("AliasExpressionSegment", optional=True),
                ),
            ),
            optional=True,
        ),
        Sequence(OneOf("INCLUDING", "EXCLUDING"), "DEFAULTS", optional=True),
        Sequence(OneOf("INCLUDING", "EXCLUDING"), "IDENTITY", optional=True),
        Sequence(OneOf("INCLUDING", "EXCLUDING"), "COMMENTS", optional=True),
    )


class TableDistributionPartitionClause(BaseSegment):
    """`CREATE / ALTER TABLE` distribution / partition clause.

    DISTRIBUTE/PARTITION clause doesn't except the identifiers in brackets
    """

    type = "table_distribution_partition_clause"
    match_grammar = OneOf(
        Sequence(
            Ref("TableDistributeByGrammar"),
            Ref("CommaSegment", optional=True),
            Ref("TablePartitionByGrammar", optional=True),
        ),
        Sequence(
            Ref("TablePartitionByGrammar"),
            Ref("CommaSegment", optional=True),
            Ref("TableDistributeByGrammar", optional=True),
        ),
    )


class AlterTableStatementSegment(BaseSegment):
    """`ALTER TABLE` statement."""

    type = "alter_table_statement"

    is_ddl = True
    is_dml = False
    is_dql = False
    is_dcl = False
    match_grammar = OneOf(
        Ref("AlterTableColumnSegment"),
        Ref("AlterTableConstraintSegment"),
        Ref("AlterTableDistributePartitionSegment"),
    )


class AlterTableColumnSegment(BaseSegment):
    """A `ALTER TABLE` statement to add, modify, drop or rename columns.

    https://docs.exasol.com/sql/alter_table(column).htm
    """

    type = "alter_table_column_statement"

    is_ddl = True
    is_dml = False
    is_dql = False
    is_dcl = False

    match_grammar = Sequence(
        "ALTER",
        "TABLE",
        Ref("TableReferenceSegment"),
        OneOf(
            Ref("AlterTableAddColumnSegment"),
            Ref("AlterTableDropColumnSegment"),
            Ref("AlterTableModifyColumnSegment"),
            Ref("AlterTableRenameColumnSegment"),
            Ref("AlterTableAlterColumnSegment"),
        ),
    )


class AlterTableAddColumnSegment(BaseSegment):
    """ALTER TABLE ADD.."""

    type = "alter_table_add_column"
    match_grammar = Sequence(
        "ADD",
        Ref.keyword("COLUMN", optional=True),
        Ref("IfNotExistsGrammar", optional=True),
        OptionallyBracketed(Ref("ColumnDefinitionSegment")),
    )


class AlterTableDropColumnSegment(BaseSegment):
    """ALTER TABLE DROP.."""

    type = "alter_table_drop_column"
    match_grammar = Sequence(
        "DROP",
        Ref.keyword("COLUMN", optional=True),
        Ref("IfExistsGrammar", optional=True),
        Ref("SingleIdentifierGrammar"),
        Sequence("CASCADE", "CONSTRAINTS", optional=True),
    )


class AlterTableModifyColumnSegment(BaseSegment):
    """ALTER TABLE MODIFY.."""

    type = "alter_table_modify_column"
    match_grammar = Sequence(
        "MODIFY",
        Ref.keyword("COLUMN", optional=True),
        OptionallyBracketed(
            Ref("SingleIdentifierGrammar"),
            Ref("DatatypeSegment", optional=True),
            Ref("ColumnConstraintSegment", optional=True),
        ),
    )


class AlterTableRenameColumnSegment(BaseSegment):
    """ALTER TABLE RENAME.."""

    type = "alter_table_rename_column"
    match_grammar = Sequence(
        "RENAME",
        "COLUMN",
        Ref("SingleIdentifierGrammar"),
        "TO",
        Ref("SingleIdentifierGrammar"),
    )


class AlterTableAlterColumnSegment(BaseSegment):
    """ALTER TABLE ALTER.."""

    type = "alter_table_alter_column"
    match_grammar = Sequence(
        "ALTER",
        Ref.keyword("COLUMN", optional=True),
        Ref("SingleIdentifierGrammar"),
        OneOf(
            Sequence(
                "SET",
                OneOf(
                    Sequence(
                        # IDENTITY(1000) or IDENTITY 1000
                        "IDENTITY",
                        OptionallyBracketed(Ref("NumericLiteralSegment")),
                    ),
                    Sequence(
                        "DEFAULT",
                        OneOf(Ref("LiteralGrammar"), Ref("BareFunctionSegment")),
                    ),
                ),
            ),
            Sequence("DROP", OneOf("IDENTITY", "DEFAULT")),
        ),
    )


class AlterTableConstraintSegment(BaseSegment):
    """A `ALTER TABLE` statement to add, modify, drop or rename constraints.

    https://docs.exasol.com/sql/alter_table(constraints).htm
    """

    type = "alter_table_constraint_statement"

    is_ddl = True
    is_dml = False
    is_dql = False
    is_dcl = False

    match_grammar = Sequence(
        "ALTER",
        "TABLE",
        Ref("TableReferenceSegment"),
        OneOf(
            Sequence("ADD", Ref("TableOutOfLineConstraintSegment")),
            Sequence(
                "MODIFY",
                OneOf(
                    Sequence("CONSTRAINT", Ref("SingleIdentifierGrammar")),
                    Ref("PrimaryKeyGrammar"),
                ),
                Ref("TableConstraintEnableDisableGrammar"),
            ),
            Sequence(
                "DROP",
                OneOf(
                    Sequence(
                        "CONSTRAINT",
                        Ref("IfExistsGrammar", optional=True),
                        Ref("SingleIdentifierGrammar"),
                    ),
                    Ref("PrimaryKeyGrammar"),
                ),
            ),
            Sequence(
                "RENAME",
                "CONSTRAINT",
                Ref("SingleIdentifierGrammar"),
                "TO",
                Ref("SingleIdentifierGrammar"),
            ),
        ),
    )


class AlterTableDistributePartitionSegment(BaseSegment):
    """A `ALTER TABLE` statement to add or drop distribution / partition keys.

    https://docs.exasol.com/sql/alter_table(distribution_partitioning).htm
    """

    type = "alter_table_distribute_partition_statement"

    is_ddl = True
    is_dml = False
    is_dql = False
    is_dcl = False

    match_grammar = Sequence(
        "ALTER",
        "TABLE",
        Ref("TableReferenceSegment"),
        OneOf(
            Ref("TableDistributionPartitionClause"),
            Sequence(
                "DROP",
                OneOf(
                    Sequence(
                        Ref.keyword("DISTRIBUTION"),
                        Ref.keyword("AND", optional=True),
                        Ref.keyword("PARTITION", optional=True),
                    ),
                    Sequence(
                        Ref.keyword("PARTITION"),
                        Ref.keyword("AND", optional=True),
                        Ref.keyword("DISTRIBUTION", optional=True),
                    ),
                ),
                "KEYS",
            ),
        ),
    )


class DropTableStatementSegment(BaseSegment):
    """A `DROP` table statement.

    https://docs.exasol.com/sql/drop_table.htm
    """

    type = "drop_table_statement"

    is_ddl = True
    is_dml = False
    is_dql = False
    is_dcl = False

    match_grammar = Sequence(
        "DROP",
        "TABLE",
        Ref("IfExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        Ref("DropBehaviorGrammar", optional=True),
        Sequence("CASCADE", "CONSTRAINTS", optional=True),
    )


class CommentClauseSegment(BaseSegment):
    """A comment clause within `CREATE TABLE` / `CREATE VIEW` statements.

    e.g. COMMENT IS 'view/table/column description'
    """

    type = "comment_clause"
    match_grammar = Sequence("COMMENT", "IS", Ref("QuotedLiteralSegment"))


############################
# RENAME
############################
class RenameStatementSegment(BaseSegment):
    """`RENAME` statement.

    https://docs.exasol.com/sql/rename.htm
    """

    type = "rename_statement"

    is_ddl = True
    is_dml = False
    is_dql = False
    is_dcl = False
    match_grammar = Sequence(
        "RENAME",
        OneOf(
            "SCHEMA",
            "TABLE",
            "VIEW",
            "FUNCTION",
            "SCRIPT",
            "USER",
            "ROLE",
            "CONNECTION",
            Sequence("CONSUMER", "GROUP"),
            optional=True,
        ),
        Ref("ObjectReferenceSegment"),
        "TO",
        Ref("ObjectReferenceSegment"),
    )


############################
# COMMENT
############################


class CommentStatementSegment(BaseSegment):
    """`COMMENT` statement.

    https://docs.exasol.com/sql/comment.htm
    """

    type = "comment_statement"

    is_ddl = True
    is_dml = False
    is_dql = False
    is_dcl = False
    match_grammar = Sequence(
        "COMMENT",
        "ON",
        OneOf(
            Sequence(
                Ref.keyword("TABLE", optional=True),
                Ref("TableReferenceSegment"),
                Sequence("IS", Ref("QuotedLiteralSegment"), optional=True),
                Bracketed(
                    Delimited(
                        Sequence(
                            Ref("SingleIdentifierGrammar"),
                            "IS",
                            Ref("QuotedLiteralSegment"),
                        ),
                    ),
                    optional=True,
                ),
            ),
            Sequence(
                OneOf(
                    "COLUMN",
                    "SCHEMA",
                    "FUNCTION",
                    "SCRIPT",
                    "USER",
                    "ROLE",
                    "CONNECTION",
                    Sequence("CONSUMER", "GROUP"),
                ),
                Ref("ObjectReferenceSegment"),
                "IS",
                Ref("QuotedLiteralSegment"),
            ),
        ),
    )


############################
# INSERT
############################
class InsertStatementSegment(BaseSegment):
    """A `INSERT` statement."""

    type = "insert_statement"

    is_ddl = False
    is_dml = True
    is_dql = False
    is_dcl = False

    match_grammar = Sequence(
        "INSERT",
        Ref.keyword("INTO", optional=True),
        Ref("TableReferenceSegment"),
        AnyNumberOf(
            Ref("ValuesInsertClauseSegment"),
            Ref("ValuesRangeClauseSegment"),
            Sequence("DEFAULT", "VALUES"),
            Ref("SelectableGrammar"),
            Ref("BracketedColumnReferenceListGrammar", optional=True),
        ),
    )


class ValuesInsertClauseSegment(BaseSegment):
    """A `VALUES` clause like in `INSERT`."""

    type = "values_insert_clause"
    match_grammar = Sequence(
        "VALUES",
        Delimited(
            Bracketed(
                Delimited(
                    Ref("LiteralGrammar"),
                    Ref("IntervalExpressionSegment"),
                    Ref("FunctionSegment"),
                    Ref("BareFunctionSegment"),
                    "DEFAULT",
                    Ref("SelectableGrammar"),
                ),
                parse_mode=ParseMode.GREEDY,
            ),
        ),
    )


############################
# UPDATE
############################


class UpdateStatementSegment(BaseSegment):
    """A `Update` statement.

    UPDATE <table name> SET <set clause list> [ WHERE <search condition> ]
    https://docs.exasol.com/sql/update.htm
    """

    type = "update_statement"

    is_ddl = False
    is_dml = True
    is_dql = False
    is_dcl = False

    match_grammar = Sequence(
        "UPDATE",
        OneOf(Ref("TableReferenceSegment"), Ref("AliasedTableReferenceGrammar")),
        Ref("SetClauseListSegment"),
        Ref("FromClauseSegment", optional=True),
        Ref("WhereClauseSegment", optional=True),
        Ref("PreferringClauseSegment", optional=True),
    )


class SetClauseListSegment(BaseSegment):
    """Overwritten from ANSI."""

    type = "set_clause_list"
    match_grammar = Sequence(
        "SET",
        Indent,
        Delimited(
            Ref("SetClauseSegment"),
            terminators=["FROM"],
        ),
        Dedent,
    )


class SetClauseSegment(BaseSegment):
    """Overwritten from ANSI."""

    type = "set_clause"

    match_grammar = Sequence(
        Ref("ColumnReferenceSegment"),
        Ref("EqualsSegment"),
        OneOf(
            Ref("ExpressionSegment"),  # Maybe add this to ANSI to match math x=x+1
            Ref("LiteralGrammar"),
            Ref("BareFunctionSegment"),
            Ref("FunctionSegment"),
            Ref("ColumnReferenceSegment"),
            "NULL",
            "DEFAULT",
        ),
    )


############################
# MERGE
############################
class MergeMatchSegment(BaseSegment):
    """Contains dialect specific merge operations."""

    type = "merge_match"
    match_grammar = OneOf(
        Sequence(
            Ref("MergeMatchedClauseSegment"),
            Ref("MergeNotMatchedClauseSegment", optional=True),
        ),
        Sequence(
            Ref("MergeNotMatchedClauseSegment"),
            Ref("MergeMatchedClauseSegment", optional=True),
        ),
    )


class MergeMatchedClauseSegment(BaseSegment):
    """The `WHEN MATCHED` clause within a `MERGE` statement."""

    type = "merge_when_matched_clause"
    match_grammar = Sequence(
        "WHEN",
        "MATCHED",
        "THEN",
        OneOf(
            Ref("MergeUpdateClauseSegment"),
            Ref("MergeDeleteClauseSegment"),
        ),
    )


class MergeNotMatchedClauseSegment(BaseSegment):
    """The `WHEN NOT MATCHED` clause within a `MERGE` statement."""

    type = "merge_when_not_matched_clause"
    match_grammar = Sequence(
        "WHEN",
        "NOT",
        "MATCHED",
        "THEN",
        Ref("MergeInsertClauseSegment"),
    )


class MergeUpdateClauseSegment(BaseSegment):
    """`UPDATE` clause within the `MERGE` statement."""

    type = "merge_update_clause"
    match_grammar = Sequence(
        "UPDATE",
        Ref("SetClauseListSegment"),
        Ref("WhereClauseSegment", optional=True),
    )


class MergeDeleteClauseSegment(BaseSegment):
    """`DELETE` clause within the `MERGE` statement."""

    type = "merge_delete_clause"
    match_grammar = Sequence(
        "DELETE",
        Ref("WhereClauseSegment", optional=True),
    )


class MergeInsertClauseSegment(BaseSegment):
    """`INSERT` clause within the `MERGE` statement."""

    type = "merge_insert_clause"
    match_grammar = Sequence(
        "INSERT",
        Indent,
        Ref("BracketedColumnReferenceListGrammar", optional=True),
        Dedent,
        Ref("ValuesClauseSegment", optional=True),
        Ref("WhereClauseSegment", optional=True),
    )


############################
# DELETE
############################
class DeleteStatementSegment(BaseSegment):
    """`DELETE` statement.

    https://docs.exasol.com/sql/delete.htm
    """

    type = "delete_statement"

    is_ddl = False
    is_dml = True
    is_dql = False
    is_dcl = False

    match_grammar = Sequence(
        "DELETE",
        Ref("StarSegment", optional=True),
        "FROM",
        OneOf(Ref("TableReferenceSegment"), Ref("AliasedTableReferenceGrammar")),
        Ref("WhereClauseSegment", optional=True),
        Ref("PreferringClauseSegment", optional=True),
    )


############################
# TRUNCATE
############################
class TruncateStatementSegment(BaseSegment):
    """`TRUNCATE TABLE` statement.

    https://docs.exasol.com/sql/truncate.htm
    """

    type = "truncate_table"

    is_ddl = False
    is_dml = True
    is_dql = False
    is_dcl = False

    match_grammar = Sequence(
        "TRUNCATE",
        "TABLE",
        Ref("TableReferenceSegment"),
    )


############################
# IMPORT
############################
class ImportStatementSegment(BaseSegment):
    """`IMPORT` statement.

    https://docs.exasol.com/sql/import.htm
    """

    type = "import_statement"

    is_ddl = False
    is_dml = True
    is_dql = False
    is_dcl = False

    match_grammar = Sequence(
        "IMPORT",
        Sequence(
            "INTO",
            OneOf(
                Sequence(
                    Ref("TableReferenceSegment"),
                    Bracketed(
                        Ref("SingleIdentifierListSegment"),
                        optional=True,
                    ),
                ),
                Bracketed(
                    Delimited(Ref("ImportColumnsSegment")),
                ),
            ),
            optional=True,
        ),
        Ref("ImportFromClauseSegment"),
    )


class ExportStatementSegment(BaseSegment):
    """`EXPORT` statement.

    https://docs.exasol.com/sql/export.htm
    """

    type = "export_statement"
    is_ddl = False
    is_dml = True
    is_dql = False
    is_dcl = False
    match_grammar = Sequence(
        "EXPORT",
        OneOf(
            Sequence(
                Ref("TableReferenceSegment"),
                Bracketed(
                    Ref("SingleIdentifierListSegment"),
                    optional=True,
                ),
            ),
            Bracketed(
                Ref("SelectableGrammar"),
            ),
        ),
        Ref("ExportIntoClauseSegment"),
    )


class ExportIntoClauseSegment(BaseSegment):
    """EXPORT INTO CLAUSE."""

    type = "export_into_clause"
    match_grammar = Sequence(
        "INTO",
        OneOf(
            Sequence(
                OneOf(
                    Ref("ImportFromExportIntoDbSrcSegment"),
                    Ref("ImportFromExportIntoFileSegment"),
                ),
                Ref("RejectClauseSegment", optional=True),
            ),
            Ref("ImportFromExportIntoScriptSegment"),
        ),
    )


class ImportColumnsSegment(BaseSegment):
    """IMPORT COLUMNS."""

    type = "import_columns"
    match_grammar = Sequence(
        OneOf(
            Ref("ColumnDatatypeSegment"),
            Ref("CreateTableLikeClauseSegment"),
        )
    )


class ImportFromClauseSegment(BaseSegment):
    """IMPORT FROM CLAUSE."""

    type = "import_from_clause"
    match_grammar = Sequence(
        "FROM",
        OneOf(
            Sequence(
                OneOf(
                    Ref("ImportFromExportIntoDbSrcSegment"),
                    Ref("ImportFromExportIntoFileSegment"),
                ),
                Ref("ImportErrorsClauseSegment", optional=True),
            ),
            Ref("ImportFromExportIntoScriptSegment"),
        ),
    )


class ImportFromExportIntoDbSrcSegment(BaseSegment):
    """`IMPORT` from or `EXPORT` to a external database source (EXA,ORA,JDBC)."""

    type = "import_export_dbsrc"
    match_grammar = Sequence(
        OneOf(
            "EXA",
            "ORA",
            Sequence(
                "JDBC",
                Sequence(
                    "DRIVER",
                    Ref("EqualsSegment"),
                    Ref("QuotedLiteralSegment"),
                ),
            ),
        ),
        Sequence("AT", Ref("ConnectionDefinition")),
        OneOf(
            Sequence(
                "TABLE",
                Ref("TableReferenceSegment"),
                Bracketed(
                    Ref("SingleIdentifierListSegment"),
                    optional=True,
                ),
                Sequence(
                    # EXPORT only
                    AnyNumberOf(
                        OneOf("REPLACE", "TRUNCATE"),
                        Sequence(
                            "CREATED",
                            "BY",
                            Ref("QuotedLiteralSegment"),
                        ),
                        max_times=2,
                    ),
                    optional=True,
                ),
            ),
            AnyNumberOf(
                Sequence(
                    "STATEMENT",
                    Ref("QuotedLiteralSegment"),
                ),
                min_times=1,
            ),
        ),
    )


class ImportFromExportIntoFileSegment(BaseSegment):
    """`IMPORT` from or `EXPORT` to a file source (FBV,CSV)."""

    type = "import_file"
    match_grammar = Sequence(
        OneOf(
            Sequence(
                OneOf(
                    "CSV",
                    "FBV",
                ),
                AnyNumberOf(
                    Sequence(
                        "AT",
                        Ref("ConnectionDefinition"),
                    ),
                    AnyNumberOf(
                        "FILE",
                        Ref("QuotedLiteralSegment"),
                        min_times=1,
                    ),
                    min_times=1,
                ),
            ),
            Sequence(
                "LOCAL",
                Ref.keyword("SECURE", optional=True),
                OneOf(
                    "CSV",
                    "FBV",
                ),
                AnyNumberOf(
                    "FILE",
                    Ref("QuotedLiteralSegment"),
                    min_times=1,
                ),
            ),
        ),
        OneOf(
            Ref("CSVColumnDefinitionSegment"),
            Ref("FBVColumnDefinitionSegment"),
            optional=True,
        ),
        Ref("FileOptionSegment", optional=True),
    )


class ImportFromExportIntoScriptSegment(BaseSegment):
    """`IMPORT` from / `EXPORT` to a executed database script."""

    type = "import_script"
    match_grammar = Sequence(
        "SCRIPT",
        Ref("ObjectReferenceSegment"),
        Sequence("AT", Ref("ConnectionDefinition"), optional=True),
        Sequence(
            "WITH",
            AnyNumberOf(
                Sequence(
                    Ref("ParameterNameSegment"),
                    Ref("EqualsSegment"),
                    Ref("LiteralGrammar"),
                ),
                min_times=1,
            ),
            optional=True,
        ),
    )


class ImportErrorsClauseSegment(BaseSegment):
    """`ERRORS` clause."""

    type = "import_errors_clause"
    match_grammar = Sequence(
        "ERRORS",
        "INTO",
        Ref("ImportErrorDestinationSegment"),
        Bracketed(
            Ref("ExpressionSegment"),  # maybe wrong implementation?
            optional=True,
        ),
        OneOf(
            "REPLACE",
            "TRUNCATE",
            optional=True,
        ),
        Ref("RejectClauseSegment", optional=True),
    )


class ImportErrorDestinationSegment(BaseSegment):
    """Error destination (csv file or table)."""

    type = "import_error_destination"
    match_grammar = OneOf(
        Sequence(
            "CSV",
            Sequence("AT", Ref("ConnectionDefinition")),
            "FILE",
            Ref("QuotedLiteralSegment"),
        ),
        Sequence(
            "LOCAL",
            Ref.keyword("SECURE", optional=True),
            "CSV",
            "FILE",
            Ref("QuotedLiteralSegment"),
        ),
        Sequence(
            Ref("TableReferenceSegment"),
        ),
    )


class RejectClauseSegment(BaseSegment):
    """`REJECT` clause within an import / export statement."""

    type = "reject_clause"
    match_grammar = Sequence(
        "REJECT",
        "LIMIT",
        OneOf(
            Ref("NumericLiteralSegment"),
            "UNLIMITED",
        ),
        Ref.keyword("ERRORS", optional=True),
    )


class CSVColumnDefinitionSegment(BaseSegment):
    """Definition of csv columns within an `IMPORT` / `EXPORT` statement."""

    type = "csv_cols"
    match_grammar = Bracketed(
        Delimited(
            Sequence(
                OneOf(
                    Ref("NumericLiteralSegment"),
                    Sequence(
                        # Expression 1..3, for col 1, 2 and 3
                        Ref("NumericLiteralSegment"),
                        Ref("RangeOperator"),
                        Ref("NumericLiteralSegment"),
                    ),
                ),
                Sequence(
                    "FORMAT",
                    Ref("EqualsSegment"),
                    Ref("QuotedLiteralSegment"),
                    optional=True,
                ),
                Sequence(
                    # EXPORT only
                    "DELIMIT",
                    Ref("EqualsSegment"),
                    OneOf("ALWAYS", "NEVER", "AUTO"),
                    optional=True,
                ),
            ),
        )
    )


class FBVColumnDefinitionSegment(BaseSegment):
    """Definition of fbv columns within an `IMPORT` / `EXPORT` statement."""

    type = "fbv_cols"
    match_grammar = Bracketed(
        Delimited(
            AnyNumberOf(
                # IMPORT valid: SIZE ,START, FORMAT, PADDING, ALIGN
                # EXPORT valid: SIZE, FORMAT, ALIGN, PADDING
                Sequence(
                    OneOf("SIZE", "START"),
                    Ref("EqualsSegment"),
                    Ref("NumericLiteralSegment"),
                ),
                Sequence(
                    OneOf("FORMAT", "PADDING"),
                    Ref("EqualsSegment"),
                    Ref("QuotedLiteralSegment"),
                ),
                Sequence(
                    "ALIGN",
                    Ref("EqualsSegment"),
                    OneOf("LEFT", "RIGHT"),
                ),
            ),
        )
    )


class FileOptionSegment(BaseSegment):
    """File options."""

    type = "file_opts"
    match_grammar = AnyNumberOf(
        OneOf(
            # IMPORT valid: ENCODING, NULL, ROW SEPARATOR, COLUMN SEPARATOR / DELIMITER
            #               TRIM, LTRIM, RTRIM, SKIP, ROW SIZE
            # EXPORT valid: REPLACE, TRUNCATE, ENCODING, NULL, BOOLEAN, ROW SEPARATOR
            #               COLUMN SEPARATOR / DELIMITER, DELIMIT, WITH COLUMN NAMES
            "ENCODING",
            "NULL",
            "BOOLEAN",
            Sequence("ROW", "SEPARATOR"),
            Sequence(
                "COLUMN",
                OneOf("SEPARATOR", "DELIMITER"),
            ),
            Ref("EqualsSegment"),
            Ref("QuotedLiteralSegment"),
        ),
        OneOf("TRIM", "LTRIM", "RTRIM"),
        Sequence(
            OneOf(
                "SKIP",
                Sequence("ROW", "SIZE"),
            ),
            Ref("EqualsSegment"),
            Ref("NumericLiteralSegment"),
        ),
        "REPLACE",
        "TRUNCATE",
        Sequence(
            "WITH",
            "COLUMN",
            "NAMES",
        ),
        Sequence(
            # EXPORT only
            "DELIMIT",
            Ref("EqualsSegment"),
            OneOf("ALWAYS", "NEVER", "AUTO"),
        ),
    )


############################
# USER
############################
class CreateUserStatementSegment(ansi.CreateUserStatementSegment):
    """`CREATE USER` statement.

    https://docs.exasol.com/sql/create_user.htm
    """

    is_ddl = False
    is_dml = False
    is_dql = False
    is_dcl = True

    match_grammar = Sequence(
        "CREATE",
        "USER",
        Ref("RoleReferenceSegment"),
        "IDENTIFIED",
        OneOf(
            Ref("UserPasswordAuthSegment"),
            Ref("UserKerberosAuthSegment"),
            Ref("UserLDAPAuthSegment"),
            Ref("UserOpenIDAuthSegment"),
        ),
    )


class AlterUserStatementSegment(BaseSegment):
    """`ALTER USER` statement.

    https://docs.exasol.com/sql/alter_user.htm
    """

    type = "alter_user_statement"

    is_ddl = False
    is_dml = False
    is_dql = False
    is_dcl = True

    match_grammar = Sequence(
        "ALTER",
        "USER",
        Ref("RoleReferenceSegment"),
        OneOf(
            Sequence(
                "IDENTIFIED",
                OneOf(
                    Sequence(
                        Ref("UserPasswordAuthSegment"),
                        Sequence(
                            "REPLACE",
                            Ref("PasswordLiteralSegment"),
                            optional=True,
                        ),
                    ),
                    Ref("UserLDAPAuthSegment"),
                    Ref("UserKerberosAuthSegment"),
                    Ref("UserOpenIDAuthSegment"),
                ),
            ),
            Sequence(
                "PASSWORD_EXPIRY_POLICY",
                Ref("EqualsSegment"),
                Ref("QuotedLiteralSegment"),
            ),
            Sequence("PASSWORD", "EXPIRE"),
            Sequence("RESET", "FAILED", "LOGIN", "ATTEMPTS"),
            Sequence(
                "SET",
                "CONSUMER_GROUP",
                Ref("EqualsSegment"),
                OneOf(Ref("SingleIdentifierGrammar"), "NULL"),
            ),
        ),
    )


class UserPasswordAuthSegment(BaseSegment):
    """user password authentication."""

    type = "password_auth"
    match_grammar = Sequence(
        # password
        "BY",
        Ref("PasswordLiteralSegment"),
    )


class UserKerberosAuthSegment(BaseSegment):
    """user kerberos authentication."""

    type = "kerberos_auth"
    match_grammar = Sequence(
        "BY",
        "KERBEROS",
        "PRINCIPAL",
        Ref("QuotedLiteralSegment"),
    )


class UserLDAPAuthSegment(BaseSegment):
    """user ldap authentication."""

    type = "ldap_auth"
    match_grammar = Sequence(
        "AT",
        "LDAP",
        "AS",
        Ref("QuotedLiteralSegment"),
        Ref.keyword("FORCE", optional=True),
    )


class UserOpenIDAuthSegment(BaseSegment):
    """User OpenID authentication."""

    type = "openid_auth"
    match_grammar = Sequence(
        "BY",
        "OPENID",
        "SUBJECT",
        Ref("QuotedLiteralSegment"),
    )


class DropUserStatementSegment(ansi.DropUserStatementSegment):
    """A `DROP USER` statement with CASCADE option.

    https://docs.exasol.com/sql/drop_user.htm
    """

    is_ddl = False
    is_dml = False
    is_dql = False
    is_dcl = True

    match_grammar = Sequence(
        "DROP",
        "USER",
        Ref("IfExistsGrammar", optional=True),
        Ref("RoleReferenceSegment"),
        Ref.keyword("CASCADE", optional=True),
    )


############################
# CONSUMER GROUP
############################


class CreateConsumerGroupSegment(BaseSegment):
    """`CREATE CONSUMER GROUP` statement."""

    type = "create_consumer_group_statement"
    match_grammar = Sequence(
        "CREATE",
        "CONSUMER",
        "GROUP",
        Ref("SingleIdentifierGrammar"),
        "WITH",
        Delimited(Ref("ConsumerGroupParameterSegment")),
    )


class AlterConsumerGroupSegment(BaseSegment):
    """`ALTER CONSUMER GROUP` statement."""

    type = "alter_consumer_group_statement"
    match_grammar = Sequence(
        "ALTER",
        "CONSUMER",
        "GROUP",
        Ref("SingleIdentifierGrammar"),
        "SET",
        Delimited(Ref("ConsumerGroupParameterSegment")),
    )


class ConsumerGroupParameterSegment(BaseSegment):
    """Consumer Group Parameters."""

    type = "consumer_group_parameter"
    match_grammar = Sequence(
        OneOf(
            "CPU_WEIGHT",
            "PRECEDENCE",
            "GROUP_TEMP_DB_RAM_LIMIT",
            "USER_TEMP_DB_RAM_LIMIT",
            "SESSION_TEMP_DB_RAM_LIMIT",
            "QUERY_TIMEOUT",
            "IDLE_TIMEOUT",
        ),
        Ref("EqualsSegment"),
        OneOf(Ref("QuotedLiteralSegment"), Ref("NumericLiteralSegment")),
    )


class DropConsumerGroupSegment(BaseSegment):
    """A `DROP CONSUMER GROUP` statement.

    https://docs.exasol.com/sql/consumer_group.htm
    """

    type = "drop_consumer_group_statement"

    match_grammar = Sequence(
        "DROP", Sequence("CONSUMER", "GROUP"), Ref("SingleIdentifierGrammar")
    )


############################
# ROLE
############################
class CreateRoleStatementSegment(ansi.CreateRoleStatementSegment):
    """`CREATE ROLE` statement.

    https://docs.exasol.com/sql/create_role.htm
    """

    is_ddl = False
    is_dml = False
    is_dql = False
    is_dcl = True

    match_grammar = Sequence(
        "CREATE",
        "ROLE",
        Ref("RoleReferenceSegment"),
    )


class AlterRoleStatementSegment(BaseSegment):
    """`ALTER ROLE` statement.

    Only allowed to alter CONSUMER GROUPs
    """

    type = "alter_role_statement"

    is_ddl = False
    is_dml = False
    is_dql = False
    is_dcl = True

    match_grammar = Sequence(
        "ALTER",
        "ROLE",
        Ref("RoleReferenceSegment"),
        "SET",
        Sequence(
            "CONSUMER_GROUP",
            Ref("EqualsSegment"),
            OneOf(Ref("SingleIdentifierGrammar"), "NULL"),
        ),
    )


class DropRoleStatementSegment(ansi.DropRoleStatementSegment):
    """A `DROP ROLE` statement with CASCADE option.

    https://docs.exasol.com/sql/drop_role.htm
    """

    is_ddl = False
    is_dml = False
    is_dql = False
    is_dcl = True

    match_grammar = Sequence(
        "DROP",
        "ROLE",
        Ref("IfExistsGrammar", optional=True),
        Ref("RoleReferenceSegment"),
        Ref.keyword("CASCADE", optional=True),
    )


############################
# CONNECTION
############################
class CreateConnectionSegment(BaseSegment):
    """`CREATE CONNECTION` statement.

    https://docs.exasol.com/sql/create_connection.htm
    """

    type = "create_connection"

    is_ddl = False
    is_dml = False
    is_dql = False
    is_dcl = True

    match_grammar = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        "CONNECTION",
        Ref("NakedIdentifierSegment"),
        "TO",
        Ref("ConnectionDefinition"),
    )


class AlterConnectionSegment(BaseSegment):
    """`ALTER CONNECTION` statement.

    https://docs.exasol.com/sql/alter_connection.htm
    """

    type = "alter_connection"

    is_ddl = False
    is_dml = False
    is_dql = False
    is_dcl = True

    match_grammar = Sequence(
        "ALTER",
        "CONNECTION",
        Ref("NakedIdentifierSegment"),
        "TO",
        Ref("ConnectionDefinition"),
    )


class ConnectionDefinition(BaseSegment):
    """Definition of a connection."""

    type = "connection_definition"
    match_grammar = Sequence(
        OneOf(
            # string or identifier
            Ref("SingleIdentifierGrammar"),
            Ref("QuotedLiteralSegment"),
        ),
        Sequence(
            "USER",
            Ref("QuotedLiteralSegment"),
            "IDENTIFIED",
            "BY",
            Ref("QuotedLiteralSegment"),
            optional=True,
        ),
    )


class DropConnectionStatementSegment(BaseSegment):
    """A `DROP CONNECTION` statement.

    https://docs.exasol.com/sql/drop_connection.htm
    """

    type = "drop_connection_statement"

    is_ddl = False
    is_dml = False
    is_dql = False
    is_dcl = True

    match_grammar = Sequence(
        "DROP",
        "CONNECTION",
        Ref("IfExistsGrammar", optional=True),
        Ref("SingleIdentifierGrammar"),
    )


############################
# GRANT / REVOKE
############################
class AccessStatementSegment(BaseSegment):
    """`GRANT` / `REVOKE` statement.

    https://docs.exasol.com/sql/grant.htm
    https://docs.exasol.com/sql/revoke.htm
    """

    type = "access_statement"

    is_ddl = False
    is_dml = False
    is_dql = False
    is_dcl = True

    match_grammar = Sequence(
        OneOf("GRANT", "REVOKE"),
        OneOf(
            Ref("GrantRevokeSystemPrivilegesSegment"),
            Ref("GrantRevokeObjectPrivilegesSegment"),
            Ref("GrantRevokeRolesSegment"),
            Ref("GrantRevokeImpersonationSegment"),
            Ref("GrantRevokeConnectionSegment"),
            Ref("GrantRevokeConnectionRestrictedSegment"),
        ),
    )


class GrantRevokeSystemPrivilegesSegment(BaseSegment):
    """`GRANT` / `REVOKE` system privileges."""

    type = "grant_revoke_system_privileges"
    match_grammar = Sequence(
        OneOf(
            Sequence(
                "ALL",
                Ref.keyword(
                    "PRIVILEGES",
                    optional=True,
                ),
            ),
            Delimited(
                Ref("SystemPrivilegesSegment"),
                terminators=["TO", "FROM"],
            ),
        ),
        OneOf("TO", "FROM"),
        Delimited(
            Ref("NakedIdentifierSegment"),
        ),
        Sequence("WITH", "ADMIN", "OPTION", optional=True),  # Grant only
    )


class GrantRevokeObjectPrivilegesSegment(BaseSegment):
    """`GRANT` / `REVOKE` object privileges."""

    type = "grant_revoke_object_privileges"
    match_grammar = Sequence(
        OneOf(
            Sequence("ALL", Ref.keyword("PRIVILEGES", optional=True)),
            Delimited(Ref("ObjectPrivilegesSegment"), terminators=["ON"]),
        ),
        "ON",
        OneOf(
            OneOf("SCHEMA", "TABLE", "VIEW", "FUNCTION", "SCRIPT"),
            Sequence("ALL", Ref.keyword("OBJECTS", optional=True)),  # Revoke only
            optional=True,
        ),
        Ref("ObjectReferenceSegment"),
        OneOf(
            Sequence(  # Grant only
                "TO",
                Delimited(Ref("SingleIdentifierGrammar")),
            ),
            Sequence(  # Revoke only
                "FROM",
                Delimited(Ref("SingleIdentifierGrammar")),
                Sequence("CASCADE", "CONSTRAINTS", optional=True),
            ),
        ),
    )


class GrantRevokeRolesSegment(BaseSegment):
    """`GRANT` / `REVOKE` roles."""

    type = "grant_revoke_roles"
    match_grammar = Sequence(
        OneOf(
            Sequence("ALL", "ROLES"),  # Revoke only
            Delimited(Ref("RoleReferenceSegment"), terminators=["TO", "FROM"]),
        ),
        OneOf("TO", "FROM"),
        Delimited(Ref("RoleReferenceSegment")),
        Sequence("WITH", "ADMIN", "OPTION", optional=True),  # Grant only
    )


class GrantRevokeImpersonationSegment(BaseSegment):
    """`GRANT` / `REVOKE` impersonation."""

    type = "grant_revoke_impersonation"
    match_grammar = Sequence(
        "IMPERSONATION",
        "ON",
        Delimited(
            Ref("SingleIdentifierGrammar"),
            terminators=["TO", "FROM"],
        ),
        OneOf("TO", "FROM"),
        Delimited(Ref("SingleIdentifierGrammar")),
    )


class GrantRevokeConnectionSegment(BaseSegment):
    """`GRANT` / `REVOKE` connection."""

    type = "grant_revoke_connection"
    match_grammar = Sequence(
        "CONNECTION",
        Delimited(
            Ref("SingleIdentifierGrammar"),
            terminators=["TO", "FROM"],
        ),
        OneOf("TO", "FROM"),
        Delimited(Ref("SingleIdentifierGrammar")),
        Sequence("WITH", "ADMIN", "OPTION", optional=True),
    )


class GrantRevokeConnectionRestrictedSegment(BaseSegment):
    """`GRANT` / `REVOKE` connection restricted."""

    type = "grant_revoke_connection_restricted"
    match_grammar = Sequence(
        "ACCESS",
        "ON",
        "CONNECTION",
        Ref("SingleIdentifierGrammar"),
        Sequence(
            "FOR",
            OneOf("SCRIPT", "SCHEMA", optional=True),
            Ref("SingleIdentifierGrammar"),
        ),
        OneOf("TO", "FROM"),
        Delimited(Ref("SingleIdentifierGrammar")),
    )


class SystemPrivilegesSegment(BaseSegment):
    """System privileges.

    https://docs.exasol.com/database_concepts/privileges/details_rights_management.htm#System_Privileges
    """

    type = "system_privilege"
    match_grammar = OneOf(
        Sequence("GRANT", "ANY", "OBJECT", "PRIVILEGE"),
        Sequence("GRANT", "ANY", "PRIVILEGE"),
        Sequence("SET", "ANY", "CONSUMER", "GROUP"),
        Sequence("MANAGE", "CONSUMER", "GROUPS"),
        Sequence("KILL", "ANY", "SESSION"),
        Sequence("ALTER", "SYSTEM"),
        Sequence(OneOf("CREATE", "ALTER", "DROP"), "USER"),
        Sequence("IMPERSONATE", "ANY", "USER"),
        Sequence(OneOf("DROP", "GRANT"), "ANY", "ROLE"),
        Sequence(OneOf("ALTER", "DROP", "GRANT", "USE", "ACCESS"), "ANY", "CONNECTION"),
        Sequence("CREATE", Ref.keyword("VIRTUAL", optional=True), "SCHEMA"),
        Sequence(
            OneOf("ALTER", "DROP", "USE"),
            "ANY",
            Ref.keyword("VIRTUAL", optional=True),
            "SCHEMA",
            Ref.keyword("REFRESH", optional=True),
        ),
        Sequence(
            "CREATE",
            OneOf(
                "TABLE", "VIEW", "CONNECTION", "ROLE", "SESSION", "FUNCTION", "SCRIPT"
            ),
        ),
        Sequence(
            OneOf("CREATE", "ALTER", "DELETE", "DROP", "INSERT", "SELECT", "UPDATE"),
            "ANY",
            "TABLE",
        ),
        Sequence("SELECT", "ANY", "DICTIONARY"),
        Sequence(OneOf("CREATE", "DROP"), "ANY", "VIEW"),
        Sequence(
            OneOf("CREATE", "DROP", "EXECUTE"), "ANY", OneOf("SCRIPT", "FUNCTION")
        ),
        "IMPORT",
        "EXPORT",
    )


class ObjectPrivilegesSegment(BaseSegment):
    """Object privileges.

    https://docs.exasol.com/database_concepts/privileges/details_rights_management.htm#System_Privileges
    """

    type = "object_privilege"
    match_grammar = OneOf(
        "ALTER",
        "SELECT",
        "INSERT",
        "UPDATE",
        "DELETE",
        "REFERENCES",
        "EXECUTE",
        # Revoke only
        "IMPORT",
        "EXPORT",
    )


############################
# SKYLINE
############################
class PreferringClauseSegment(BaseSegment):
    """`PREFERRING` clause of the Exasol Skyline extension.

    https://docs.exasol.com/advanced_analytics/skyline.htm#preferring_clause
    """

    type = "preferring_clause"
    match_grammar = Sequence(
        "PREFERRING",
        OptionallyBracketed(Ref("PreferringPreferenceTermSegment")),
        Ref("PartitionClauseSegment", optional=True),
    )


class PreferringPreferenceTermSegment(BaseSegment):
    """The preference term of a `PREFERRING` clause."""

    type = "preference_term"
    match_grammar = Sequence(
        OneOf(
            Sequence(
                OneOf("HIGH", "LOW"),
                OneOf(
                    Ref("LiteralGrammar"),
                    Ref("BareFunctionSegment"),
                    Ref("FunctionSegment"),
                    Ref("ColumnReferenceSegment"),
                    Ref("LocalAliasSegment"),
                ),
            ),
            OneOf(
                Ref("LiteralGrammar"),
                Ref("BareFunctionSegment"),
                Ref("FunctionSegment"),
                Ref("ColumnReferenceSegment"),
                Ref("LocalAliasSegment"),
            ),
        ),
        Ref("PreferringPlusPriorTermSegment", optional=True),
    )


class PreferringPlusPriorTermSegment(BaseSegment):
    """The preferring preference term expression."""

    type = "plus_prior_inverse"
    match_grammar = OneOf(
        Sequence(
            Sequence(
                OneOf(
                    "PLUS",
                    Sequence("PRIOR", "TO"),
                ),
                Ref("PreferringPreferenceTermSegment"),
                optional=True,
            ),
        ),
        Sequence(
            "INVERSE",
            Ref("PreferringPreferenceTermSegment"),
        ),
    )


class MLTableExpressionSegment(ansi.MLTableExpressionSegment):
    """Not supported."""

    match_grammar = Nothing()


############################
# SYSTEM
############################
class AlterSessionSegment(BaseSegment):
    """`ALTER SESSION` statement."""

    type = "alter_session_statement"
    match_grammar = Sequence(
        "ALTER",
        "SESSION",
        "SET",
        Ref("SessionParameterSegment"),
        Ref("EqualsSegment"),
        OneOf(Ref("QuotedLiteralSegment"), Ref("NumericLiteralSegment")),
    )


class AlterSystemSegment(BaseSegment):
    """`ALTER SYSTEM` statement."""

    type = "alter_system_statement"
    match_grammar = Sequence(
        "ALTER",
        "SYSTEM",
        "SET",
        Ref("SystemParameterSegment"),
        Ref("EqualsSegment"),
        OneOf(Ref("QuotedLiteralSegment"), Ref("NumericLiteralSegment")),
    )


class OpenSchemaSegment(BaseSegment):
    """`OPEN SCHEMA` statement."""

    type = "open_schema_statement"
    match_grammar = Sequence("OPEN", "SCHEMA", Ref("SchemaReferenceSegment"))


class CloseSchemaSegment(BaseSegment):
    """`CLOSE SCHEMA` statement."""

    type = "close_schema_statement"
    match_grammar = Sequence("CLOSE", "SCHEMA")


class FlushStatisticsSegment(BaseSegment):
    """`FLUSH STATISTICS` statement."""

    type = "flush_statistics_statement"
    match_grammar = Sequence("FLUSH", "STATISTICS")


class RecompressReorganizeSegment(BaseSegment):
    """`RECOMPRESS` and `REOGRANIZE` statement."""

    type = "recompress_reorganize_statement"
    match_grammar = Sequence(
        OneOf("RECOMPRESS", "REORGANIZE"),
        OneOf(
            Sequence(
                "TABLE",
                Ref("TableReferenceSegment"),
                Ref("BracketedColumnReferenceListGrammar"),
            ),
            Sequence("TABLES", Delimited(Ref("TableReferenceSegment"))),
            Sequence("SCHEMA", Ref("SchemaReferenceSegment")),
            Sequence("SCHEMAS", Delimited(Ref("SchemaReferenceSegment"))),
            "DATABASE",
        ),
        Ref.keyword("ENFORCE", optional=True),
    )


class PreloadSegment(BaseSegment):
    """`PRELOAD` statement."""

    type = "preload_statement"
    match_grammar = Sequence(
        "PRELOAD",
        OneOf(
            Sequence(
                "TABLE",
                Ref("TableReferenceSegment"),
                Ref("BracketedColumnReferenceListGrammar"),
            ),
            Sequence("TABLES", Delimited(Ref("TableReferenceSegment"))),
            Sequence("SCHEMA", Ref("SchemaReferenceSegment")),
            Sequence("SCHEMAS", Delimited(Ref("SchemaReferenceSegment"))),
            "DATABASE",
        ),
    )


class ImpersonateSegment(BaseSegment):
    """`IMPERSONATE` statement."""

    type = "impersonate_statement"
    match_grammar = Sequence("IMPERSONATE", Ref("SingleIdentifierGrammar"))


class KillSegment(BaseSegment):
    """`KILL` statement."""

    type = "kill_statement"
    match_grammar = Sequence(
        "KILL",
        OneOf(
            Sequence("SESSION", OneOf("CURRENT_SESSION", Ref("NumericLiteralSegment"))),
            Sequence(
                "STATEMENT",
                Ref("NumericLiteralSegment", optional=True),
                "IN",
                "SESSION",
                Ref("NumericLiteralSegment"),
                Sequence("WITH", "MESSAGE", Ref("QuotedLiteralSegment"), optional=True),
            ),
        ),
    )


class TruncateAuditLogsSegment(BaseSegment):
    """`TRUNCATE AUDIT LOGS` statement."""

    type = "truncate_audit_logs_statement"
    match_grammar = Sequence(
        "TRUNCATE",
        "AUDIT",
        "LOGS",
        Sequence(
            "KEEP",
            OneOf(
                Sequence("LAST", OneOf("DAY", "MONTH", "YEAR")),
                Sequence("FROM", Ref("QuotedLiteralSegment")),
            ),
            optional=True,
        ),
    )


############################
# OTHERS
############################


class TransactionStatementSegment(BaseSegment):
    """A `COMMIT` or `ROLLBACK` statement."""

    type = "transaction_statement"
    match_grammar = Sequence(
        OneOf("COMMIT", "ROLLBACK"), Ref.keyword("WORK", optional=True)
    )


class ExecuteScriptSegment(BaseSegment):
    """`EXECUTE SCRIPT` statement."""

    type = "execute_script_statement"
    match_grammar = Sequence(
        "EXECUTE",
        "SCRIPT",
        Ref("ScriptReferenceSegment"),
        Bracketed(
            Delimited(Ref.keyword("ARRAY", optional=True), Ref("ExpressionSegment")),
            optional=True,
        ),
        Sequence("WITH", "OUTPUT", optional=True),
    )


class ExplainVirtualSegment(BaseSegment):
    """`EXPLAIN VIRTUAL` statement."""

    type = "explain_virtual_statement"
    match_grammar = Sequence("EXPLAIN", "VIRTUAL", Ref("SelectableGrammar"))


############################
# FUNCTION
############################


class FunctionReferenceSegment(ansi.ObjectReferenceSegment):
    """A reference to a function."""

    type = "function_reference"


class CreateFunctionStatementSegment(BaseSegment):
    """A `CREATE FUNCTION` statement."""

    type = "create_function_statement"

    is_ddl = True
    is_dml = False
    is_dql = False
    is_dcl = False

    match_grammar = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        "FUNCTION",
        Ref("FunctionReferenceSegment"),
        Bracketed(
            Delimited(
                Sequence(
                    Ref("SingleIdentifierGrammar"),  # Column name
                    Ref.keyword("IN", optional=True),
                    Ref("DatatypeSegment"),  # Column type
                ),
                optional=True,
            ),
        ),
        "RETURN",
        Ref("DatatypeSegment"),
        OneOf("IS", "AS", optional=True),
        Indent,
        AnyNumberOf(
            Sequence(
                Ref("VariableNameSegment"),
                Ref("DatatypeSegment"),
                Ref("DelimiterGrammar"),
            ),
            optional=True,
        ),
        Dedent,
        "BEGIN",
        Indent,
        AnyNumberOf(Ref("FunctionBodySegment")),
        "RETURN",
        Ref("FunctionContentsExpressionGrammar"),
        Ref("DelimiterGrammar"),
        Dedent,
        "END",
        Ref("FunctionReferenceSegment", optional=True),
        Ref("SemicolonSegment", optional=True),
    )


class FunctionBodySegment(BaseSegment):
    """The definition of the function body."""

    type = "function_body"
    match_grammar = Sequence(
        OneOf(
            Ref("FunctionAssignmentSegment"),
            Ref("FunctionIfBranchSegment"),
            Ref("FunctionForLoopSegment"),
            Ref("FunctionWhileLoopSegment"),
        ),
    )


class FunctionAssignmentSegment(BaseSegment):
    """The definition of a assignment within a function body."""

    type = "function_assignment"
    match_grammar = Sequence(
        # assignment
        Ref("VariableNameSegment"),
        Ref("WalrusOperatorSegment"),
        OneOf(
            Ref("FunctionSegment"),
            Ref("VariableNameSegment"),
            Ref("LiteralGrammar"),
            Ref("ExpressionSegment"),
        ),
        Ref("SemicolonSegment"),
    )


class FunctionIfBranchSegment(BaseSegment):
    """The definition of a if branch within a function body."""

    type = "function_if_branch"
    match_grammar = Sequence(
        "IF",
        AnyNumberOf(Ref("ExpressionSegment")),
        "THEN",
        Indent,
        AnyNumberOf(Ref("FunctionBodySegment"), min_times=1),
        Dedent,
        AnyNumberOf(
            Sequence(
                OneOf("ELSIF", "ELSEIF"),
                Ref("ExpressionSegment"),
                "THEN",
                Indent,
                AnyNumberOf(Ref("FunctionBodySegment"), min_times=1),
                Dedent,
            ),
            optional=True,
        ),
        Sequence(
            "ELSE",
            Indent,
            AnyNumberOf(Ref("FunctionBodySegment"), min_times=1),
            Dedent,
            optional=True,
        ),
        "END",
        "IF",
        Ref("SemicolonSegment"),
    )


class FunctionForLoopSegment(BaseSegment):
    """The definition of a for loop within a function body."""

    type = "function_for_loop"
    match_grammar = Sequence(
        "FOR",
        Ref("NakedIdentifierSegment"),
        OneOf(
            #     # for x := 1 to 10 do...
            Sequence(
                Ref("WalrusOperatorSegment"),
                Ref("ExpressionSegment"),  # could be a variable
                "TO",
                Ref("ExpressionSegment"),  # could be a variable
                "DO",
                AnyNumberOf(Ref("FunctionBodySegment"), min_times=1),
                "END",
                "FOR",
            ),
            # for x IN 1..10...
            Sequence(
                "IN",
                Ref("ExpressionSegment"),  # could be a variable
                Ref("RangeOperator"),
                Ref("ExpressionSegment"),  # could be a variable
                "LOOP",
                AnyNumberOf(Ref("FunctionBodySegment"), min_times=1),
                "END",
                "LOOP",
            ),
        ),
        Ref("SemicolonSegment"),
    )


class FunctionWhileLoopSegment(BaseSegment):
    """The definition of a while loop within a function body."""

    type = "function_while_loop"
    match_grammar = Sequence(
        "WHILE",
        Ref("ExpressionSegment"),
        "DO",
        AnyNumberOf(Ref("FunctionBodySegment"), min_times=1),
        "END",
        "WHILE",
        Ref("SemicolonSegment"),
    )


class DropFunctionStatementSegment(BaseSegment):
    """A `DROP FUNCTION` statement with CASCADE and RESTRICT option.

    https://docs.exasol.com/sql/drop_function.htm
    """

    type = "drop_function_statement"

    is_ddl = True
    is_dml = False
    is_dql = False
    is_dcl = False

    match_grammar = Sequence(
        "DROP",
        "FUNCTION",
        Ref("IfExistsGrammar", optional=True),
        Ref("FunctionNameSegment"),
        Ref("DropBehaviorGrammar", optional=True),
    )


############################
# SCRIPT
############################
class ScriptReferenceSegment(ansi.ObjectReferenceSegment):
    """A reference to a script."""

    type = "script_reference"


class ScriptContentSegment(BaseSegment):
    """This represents the script content.

    Because the script content could be written in
    LUA, PYTHON, JAVA or R there is no further verification.
    """

    type = "script_content"
    match_grammar = Anything(
        terminators=[Ref("FunctionScriptTerminatorSegment")],
        # Within the script we should _only_ look for the script
        # terminator segment.
        reset_terminators=True,
    )


class CreateScriptingLuaScriptStatementSegment(BaseSegment):
    """`CREATE SCRIPT` statement to create a Lua scripting script.

    https://docs.exasol.com/sql/create_script.htm
    """

    type = "create_scripting_lua_script"

    is_ddl = True
    is_dml = False
    is_dql = False
    is_dcl = False

    match_grammar = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        Ref.keyword("LUA", optional=True),
        "SCRIPT",
        Ref("ScriptReferenceSegment"),
        Bracketed(
            Delimited(
                Sequence(
                    Ref.keyword("ARRAY", optional=True), Ref("SingleIdentifierGrammar")
                ),
                optional=True,
            ),
            optional=True,
        ),
        Sequence(Ref.keyword("RETURNS"), OneOf("TABLE", "ROWCOUNT"), optional=True),
        "AS",
        Indent,
        Ref("ScriptContentSegment"),
        Dedent,
    )


class CreateUDFScriptStatementSegment(BaseSegment):
    """`CREATE SCRIPT` statement create a UDF script.

    https://docs.exasol.com/sql/create_script.htm
    """

    type = "create_udf_script"

    is_ddl = True
    is_dml = False
    is_dql = False
    is_dcl = False

    match_grammar = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        OneOf(
            "JAVA", "PYTHON", "LUA", "R", Ref("SingleIdentifierGrammar"), optional=True
        ),
        OneOf("SCALAR", "SET"),
        "SCRIPT",
        Ref("ScriptReferenceSegment"),
        Bracketed(
            Sequence(
                Ref("UDFParameterGrammar"),
                Ref("OrderByClauseSegment", optional=True),
                optional=True,
            ),
        ),
        OneOf(Sequence("RETURNS", Ref("DatatypeSegment")), Ref("EmitsSegment")),
        "AS",
        Indent,
        Ref("ScriptContentSegment"),
        Dedent,
    )


class CreateAdapterScriptStatementSegment(BaseSegment):
    """`CREATE SCRIPT` statement create a adapter script.

    https://docs.exasol.com/sql/create_script.htm
    """

    type = "create_adapter_script"

    is_ddl = True
    is_dml = False
    is_dql = False
    is_dcl = False

    match_grammar = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        OneOf("JAVA", "PYTHON", "LUA", Ref("SingleIdentifierGrammar")),
        "ADAPTER",
        "SCRIPT",
        Ref("ScriptReferenceSegment"),
        "AS",
        Indent,
        Ref("ScriptContentSegment"),
        Dedent,
    )


class DropScriptStatementSegment(BaseSegment):
    """A `DROP SCRIPT` statement.

    https://docs.exasol.com/sql/drop_script.htm
    """

    type = "drop_script_statement"

    is_ddl = True
    is_dml = False
    is_dql = False
    is_dcl = False

    match_grammar = Sequence(
        "DROP",
        Sequence(
            Ref.keyword("ADAPTER", optional=True),
            "SCRIPT",
        ),
        Ref("IfExistsGrammar", optional=True),
        Ref("ScriptReferenceSegment"),
    )


############################
# DIALECT
############################
class FunctionScriptStatementSegment(BaseSegment):
    """A generic segment, to any of its child subsegments."""

    type = "statement"
    match_grammar = OneOf(
        Ref("CreateFunctionStatementSegment"),
        Ref("CreateScriptingLuaScriptStatementSegment"),
        Ref("CreateUDFScriptStatementSegment"),
        Ref("CreateAdapterScriptStatementSegment"),
    )


class StatementSegment(ansi.StatementSegment):
    """A generic segment, to any of its child subsegments."""

    type = "statement"

    match_grammar = OneOf(
        # Data Query Language (DQL)
        Ref("SelectableGrammar"),
        # Data Modifying Language (DML)
        Ref("DeleteStatementSegment"),
        Ref("ExportStatementSegment"),
        Ref("ImportStatementSegment"),
        Ref("InsertStatementSegment"),
        Ref("MergeStatementSegment"),
        Ref("TruncateStatementSegment"),
        Ref("UpdateStatementSegment"),
        # Data Definition Language (DDL)
        Ref("AlterTableStatementSegment"),
        Ref("AlterSchemaStatementSegment"),
        Ref("AlterVirtualSchemaStatementSegment"),
        Ref("CommentStatementSegment"),
        Ref("CreateSchemaStatementSegment"),
        Ref("CreateTableStatementSegment"),
        Ref("CreateViewStatementSegment"),
        Ref("CreateVirtualSchemaStatementSegment"),
        Ref("DropViewStatementSegment"),
        Ref("DropFunctionStatementSegment"),
        Ref("DropScriptStatementSegment"),
        Ref("DropSchemaStatementSegment"),
        Ref("DropTableStatementSegment"),
        Ref("RenameStatementSegment"),
        # Access Control Language (DCL)
        Ref("AccessStatementSegment"),
        Ref("AlterConnectionSegment"),
        Ref("AlterUserStatementSegment"),
        Ref("CreateConnectionSegment"),
        Ref("CreateRoleStatementSegment"),
        Ref("CreateUserStatementSegment"),
        Ref("DropRoleStatementSegment"),
        Ref("DropUserStatementSegment"),
        Ref("DropConnectionStatementSegment"),
        # System
        Ref("CreateConsumerGroupSegment"),
        Ref("AlterConsumerGroupSegment"),
        Ref("DropConsumerGroupSegment"),
        Ref("AlterRoleStatementSegment"),
        Ref("AlterSessionSegment"),
        Ref("AlterSystemSegment"),
        Ref("OpenSchemaSegment"),
        Ref("CloseSchemaSegment"),
        Ref("FlushStatisticsSegment"),
        Ref("ImpersonateSegment"),
        Ref("RecompressReorganizeSegment"),
        Ref("KillSegment"),
        Ref("PreloadSegment"),
        Ref("TruncateAuditLogsSegment"),
        Ref("ExplainVirtualSegment"),
        # Others
        Ref("TransactionStatementSegment"),
        Ref("ExecuteScriptSegment"),
        terminators=[Ref("DelimiterGrammar")],
    )


class FileSegment(BaseFileSegment):
    """This overwrites the FileSegment from ANSI.

    The reason is because SCRIPT and FUNCTION statements
    are terminated by a trailing / at the end.
    A semicolon is the terminator of the statement within the function / script
    """

    match_grammar = Delimited(
        Ref("FunctionScriptStatementSegment"),
        Ref("StatementSegment"),
        delimiter=OneOf(
            Ref("DelimiterGrammar"),
            Ref("FunctionScriptTerminatorSegment"),
        ),
        allow_gaps=True,
        allow_trailing=True,
    )


class EmitsSegment(BaseSegment):
    """EMITS Segment for JSON_EXTRACT for example.

    In it's own segment to give it a type to allow AL03 to find it easily.
    """

    type = "emits_segment"
    match_grammar = Sequence(
        "EMITS",
        Bracketed(Ref("UDFParameterGrammar")),
    )
