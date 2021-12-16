"""The EXASOL dialect.

https://docs.exasol.com
https://docs.exasol.com/sql_references/sqlstandardcompliance.htm
"""

from sqlfluff.core.parser import (
    AnyNumberOf,
    Anything,
    BaseSegment,
    Bracketed,
    OptionallyBracketed,
    BaseFileSegment,
    Dedent,
    Delimited,
    GreedyUntil,
    Indent,
    KeywordSegment,
    Nothing,
    OneOf,
    Ref,
    Sequence,
    StartsWith,
    RegexLexer,
    StringLexer,
    CodeSegment,
    CommentSegment,
    NamedParser,
    SymbolSegment,
    StringParser,
    RegexParser,
    NewlineSegment,
)
from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.core.parser.segments.generator import SegmentGenerator
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

exasol_dialect.insert_lexer_matchers(
    [
        RegexLexer("lua_nested_quotes", r"\[={1,3}\[.*\]={1,3}\]", CodeSegment),
        RegexLexer("lua_multiline_quotes", r"\[{2}([^[\\]|\\.)*\]{2}", CodeSegment),
        RegexLexer("udf_param_dot_syntax", r"\.{3}", CodeSegment),
        RegexLexer("range_operator", r"\.{2}", CodeSegment),
        StringLexer("hash", "#", CodeSegment),
        StringLexer(
            "walrus_operator",
            ":=",
            CodeSegment,
            segment_kwargs={"type": "walrus_operator"},
        ),
        RegexLexer(
            "function_script_terminator",
            r"\n/\n|\n/$",
            CodeSegment,
            segment_kwargs={"type": "function_script_terminator"},
            subdivider=RegexLexer(
                "newline",
                r"(\n|\r\n)+",
                NewlineSegment,
            ),
        ),
        RegexLexer("atsign_literal", r"@[a-zA-Z_][\w]*", CodeSegment),
        RegexLexer("dollar_literal", r"[$][a-zA-Z0-9_.]*", CodeSegment),
    ],
    before="not_equal",
)

exasol_dialect.patch_lexer_matchers(
    [
        # In EXASOL, a double single/double quote resolves as a single/double quote in the string.
        # It's also used for escaping single quotes inside of STATEMENT strings like in the IMPORT function
        # https://docs.exasol.com/sql_references/basiclanguageelements.htm#Delimited_Identifiers
        # https://docs.exasol.com/sql_references/literals.htm
        RegexLexer("single_quote", r"'([^']|'')*'", CodeSegment),
        RegexLexer("double_quote", r'"([^"]|"")*"', CodeSegment),
        RegexLexer(
            "inline_comment",
            r"--[^\n]*",
            CommentSegment,
            segment_kwargs={"trim_start": ("--")},
        ),
    ]
)

# Access column aliases by using the LOCAL keyword
exasol_dialect.add(
    LocalIdentifierSegment=StringParser(
        "LOCAL", KeywordSegment, name="local_identifier", type="identifier"
    ),
    UDFParameterDotSyntaxSegment=NamedParser(
        "udf_param_dot_syntax", SymbolSegment, type="identifier"
    ),
    RangeOperator=NamedParser("range_operator", SymbolSegment, type="range_operator"),
    UnknownSegment=StringParser(
        "unknown", KeywordSegment, name="boolean_literal", type="literal"
    ),
    ForeignKeyReferencesClauseGrammar=Sequence(
        "REFERENCES",
        Ref("TableReferenceSegment"),
        Ref("BracketedColumnReferenceListGrammar", optional=True),
    ),
    ColumnReferenceListGrammar=Delimited(
        Ref("ColumnReferenceSegment"),
        ephemeral_name="ColumnReferenceList",
    ),
    CommentIsGrammar=Sequence("COMMENT", "IS", Ref("QuotedLiteralSegment")),
    # delimiter doesn't work for DISTRIBUTE and PARTITION BY
    # expression because both expressions are splitted by comma
    # as well as n columns within each expression
    TableDistributeByGrammar=StartsWith(
        Sequence(
            "DISTRIBUTE",
            "BY",
            AnyNumberOf(
                Sequence(
                    Ref("CommaSegment", optional=True),
                    Ref("ColumnReferenceSegment"),
                ),
                min_times=1,
            ),
        ),
        terminator=OneOf(
            Ref("TablePartitionByGrammar"),
            Ref("DelimiterSegment"),
        ),
        enforce_whitespace_preceding_terminator=True,
    ),
    TablePartitionByGrammar=StartsWith(
        Sequence(
            "PARTITION",
            "BY",
            AnyNumberOf(
                Sequence(
                    Ref("CommaSegment", optional=True),
                    Ref("ColumnReferenceSegment"),
                ),
                min_times=1,
            ),
        ),
        terminator=OneOf(
            Ref("TableDistributeByGrammar"),
            Ref("DelimiterSegment"),
        ),
        enforce_whitespace_preceding_terminator=True,
    ),
    TableConstraintEnableDisableGrammar=OneOf("ENABLE", "DISABLE"),
    EscapedIdentifierSegment=RegexParser(
        # This matches escaped identifier e.g. [day]. There can be reserved keywords
        # within the square brackets.
        r"\[[A-Z]\]",
        CodeSegment,
        name="escaped_identifier",
        type="identifier",
    ),
    SessionParameterSegment=SegmentGenerator(
        lambda dialect: RegexParser(
            r"^(" + r"|".join(dialect.sets("session_parameters")) + r")$",
            CodeSegment,
            name="session_parameter",
            type="session_parameter",
        )
    ),
    SystemParameterSegment=SegmentGenerator(
        lambda dialect: RegexParser(
            r"^(" + r"|".join(dialect.sets("system_parameters")) + r")$",
            CodeSegment,
            name="system_parameter",
            type="system_parameter",
        )
    ),
    UDFParameterGrammar=OneOf(
        # (A NUMBER, B VARCHAR) or (...)
        Delimited(Ref("ColumnDatatypeSegment")),
        Ref("UDFParameterDotSyntaxSegment"),
    ),
    EmitsGrammar=Sequence(
        "EMITS",
        Bracketed(Ref("UDFParameterGrammar")),
    ),
    FunctionScriptTerminatorSegment=NamedParser(
        "function_script_terminator", CodeSegment, type="function_script_terminator"
    ),
    WalrusOperatorSegment=NamedParser(
        "walrus_operator", SymbolSegment, type="assignment_operator"
    ),
    VariableNameSegment=RegexParser(
        r"[A-Z][A-Z0-9_]*",
        CodeSegment,
        name="function_variable",
        type="variable",
    ),
)

exasol_dialect.replace(
    SingleIdentifierGrammar=OneOf(
        Ref("LocalIdentifierSegment"),
        Ref("NakedIdentifierSegment"),
        Ref("QuotedIdentifierSegment"),
        Ref("EscapedIdentifierSegment"),
    ),
    ParameterNameSegment=RegexParser(
        r"\"?[A-Z][A-Z0-9_]*\"?",
        CodeSegment,
        name="parameter",
        type="parameter",
    ),
    LikeGrammar=Ref.keyword("LIKE"),
    IsClauseGrammar=OneOf(
        "NULL",
        Ref("BooleanLiteralGrammar"),
    ),
    SelectClauseSegmentGrammar=Sequence(
        "SELECT",
        Ref("SelectClauseModifierSegment", optional=True),
        Indent,
        Delimited(
            Ref("SelectClauseElementSegment"),
            allow_trailing=True,
            optional=True,  # optional in favor of SELECT INVALID....
        ),
        OneOf(Ref("WithInvalidUniquePKSegment"), Ref("IntoTableSegment"), optional=True)
        # NB: The Dedent for the indent above lives in the
        # SelectStatementSegment so that it sits in the right
        # place corresponding to the whitespace.
    ),
    SelectClauseElementTerminatorGrammar=OneOf(
        Sequence(
            Ref.keyword("WITH", optional=True),
            "INVALID",
            OneOf("UNIQUE", Ref("PrimaryKeyGrammar"), Ref("ForeignKeyGrammar")),
        ),
        Sequence("INTO", "TABLE"),
        "FROM",
        "WHERE",
        Sequence("ORDER", "BY"),
        "LIMIT",
        Ref("CommaSegment"),
        Ref("SetOperatorSegment"),
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
    ),
    DateTimeLiteralGrammar=Sequence(
        OneOf("DATE", "TIMESTAMP"), Ref("QuotedLiteralSegment")
    ),
    CharCharacterSetSegment=OneOf(
        Ref.keyword("UTF8"),
        Ref.keyword("ASCII"),
    ),
    PreTableFunctionKeywordsGrammar=Ref.keyword("TABLE"),
    BooleanLiteralGrammar=OneOf(
        Ref("TrueSegment"), Ref("FalseSegment"), Ref("UnknownSegment")
    ),
    PostFunctionGrammar=OneOf(
        Ref("EmitsGrammar"),  # e.g. JSON_EXTRACT()
        Sequence(
            Sequence(OneOf("IGNORE", "RESPECT"), "NULLS", optional=True),
            Ref("OverClauseSegment"),
        ),
    ),
)


############################
# SELECT
############################


@exasol_dialect.segment(replace=True)
class SelectStatementSegment(BaseSegment):
    """A `SELECT` statement.

    https://docs.exasol.com/sql/select.htm
    """

    type = "select_statement"
    match_grammar = StartsWith(
        "SELECT",
        terminator=Ref("SetOperatorSegment"),
        enforce_whitespace_preceding_terminator=True,
    )

    parse_grammar = Sequence(
        OneOf(
            Sequence(
                # to allow SELECT INVALID FOREIGN KEY
                "SELECT",
                Ref("SelectClauseModifierSegment", optional=True),
                Indent,
                Delimited(
                    Ref("SelectClauseElementSegment", optional=True),
                    allow_trailing=True,
                    optional=True,
                ),
                Ref("WithInvalidForeignKeySegment"),
            ),
            Sequence(
                Ref("SelectClauseSegment"),
                #     # Dedent for the indent in the select clause.
                #     # It's here so that it can come AFTER any whitespace.
                Dedent,
                Ref("FromClauseSegment", optional=True),
            ),
        ),
        Ref("WhereClauseSegment", optional=True),
        Ref("ConnectByClauseSegment", optional=True),
        Ref("PreferringClauseSegment", optional=True),
        Ref("GroupByClauseSegment", optional=True),
        Ref("HavingClauseSegment", optional=True),
        Ref("QualifyClauseSegment", optional=True),
        Ref("OrderByClauseSegment", optional=True),
        Ref("LimitClauseSegment", optional=True),
    )


@exasol_dialect.segment()
class WithInvalidUniquePKSegment(BaseSegment):
    """`WITH INVALID UNIQUE` or `WITH INVALID PRIMARY KEY` clause within `SELECT`."""

    type = "with_invalid_unique_pk_clause"
    match_grammar = StartsWith(
        Sequence(
            Ref.keyword("WITH", optional=True),
            "INVALID",
            OneOf("UNIQUE", Ref("PrimaryKeyGrammar")),
        ),
        terminator="FROM",
    )
    parse_grammar = Sequence(
        Ref.keyword("WITH", optional=True),
        "INVALID",
        OneOf("UNIQUE", Ref("PrimaryKeyGrammar")),
        Ref("BracketedColumnReferenceListGrammar"),
    )


@exasol_dialect.segment()
class WithInvalidForeignKeySegment(BaseSegment):
    """`WITH INVALID FOREIGN KEY` clause within `SELECT`."""

    type = "with_invalid_foreign_key_clause"
    match_grammar = StartsWith(
        Sequence(
            Ref.keyword("WITH", optional=True), "INVALID", Ref("ForeignKeyGrammar")
        ),
        terminator=Ref("FromClauseTerminatorGrammar"),
    )
    parse_grammar = Sequence(
        Ref.keyword("WITH", optional=True),
        "INVALID",
        Ref("ForeignKeyGrammar"),
        Ref("BracketedColumnReferenceListGrammar"),
        Dedent,  # dedent for the indent in the select clause
        "FROM",
        Ref("TableReferenceSegment"),
        "REFERENCING",
        Ref("TableReferenceSegment"),
        Ref("BracketedColumnReferenceListGrammar", optional=True),
    )


@exasol_dialect.segment()
class IntoTableSegment(BaseSegment):
    """`INTO TABLE` clause within `SELECT`."""

    type = "into_table_clause"
    match_grammar = StartsWith(Sequence("INTO", "TABLE"), terminator="FROM")
    parse_grammar = Sequence("INTO", "TABLE", Ref("TableReferenceSegment"))


@exasol_dialect.segment(replace=True)
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


@exasol_dialect.segment(replace=True)
class ValuesClauseSegment(BaseSegment):
    """A `VALUES` clause within in `WITH` or `SELECT`."""

    type = "values_clause"
    match_grammar = Sequence(
        "VALUES",
        Delimited(
            OneOf(
                Bracketed(
                    Delimited(
                        Ref("LiteralGrammar"),
                        Ref("IntervalExpressionSegment"),
                        Ref("BareFunctionSegment"),
                        Ref("FunctionSegment"),
                        ephemeral_name="ValuesClauseElements",
                    )
                ),
                Delimited(
                    # e.g. SELECT * FROM (VALUES 1,2,3);
                    Ref("LiteralGrammar"),
                    Ref("BareFunctionSegment"),
                    Ref("FunctionSegment"),
                ),
            ),
        ),
        Ref("AliasExpressionSegment", optional=True),
    )


@exasol_dialect.segment()
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


@exasol_dialect.segment(replace=True)
class SetOperatorSegment(BaseSegment):
    """A set operator such as Union, Minus, Except or Intersect."""

    type = "set_operator"
    match_grammar = OneOf(
        Sequence("UNION", Ref.keyword("ALL", optional=True)),
        "INTERSECT",
        OneOf("MINUS", "EXCEPT"),
    )


@exasol_dialect.segment()
class ConnectByClauseSegment(BaseSegment):
    """`CONNECT BY` clause within a select statement."""

    type = "connect_by_clause"
    match_grammar = StartsWith(
        OneOf(
            Sequence("CONNECT", "BY"),
            Sequence("START", "WITH"),
        ),
        terminator=OneOf(
            "PREFERRING",
            Sequence("GROUP", "BY"),
            "QUALIFY",
            Sequence("ORDER", "BY"),
            "LIMIT",
            Ref("SetOperatorSegment"),
        ),
        enforce_whitespace_preceding_terminator=True,
    )
    parse_grammar = OneOf(
        Sequence(
            "CONNECT",
            "BY",
            Ref.keyword("NOCYCLE", optional=True),
            Delimited(
                Ref("ExpressionSegment"),
                delimiter="AND",
                terminator="START",
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


@exasol_dialect.segment(replace=True)
class GroupByClauseSegment(BaseSegment):
    """A `GROUP BY` clause like in `SELECT`."""

    type = "groupby_clause"
    match_grammar = StartsWith(
        Sequence("GROUP", "BY"),
        terminator=OneOf(
            Sequence("ORDER", "BY"),
            "LIMIT",
            "HAVING",
            "QUALIFY",
            Ref("SetOperatorSegment"),
        ),
        enforce_whitespace_preceding_terminator=True,
    )
    parse_grammar = Sequence(
        "GROUP",
        "BY",
        Indent,
        Delimited(
            OneOf(
                Ref("ColumnReferenceSegment"),
                # Can `GROUP BY 1`
                Ref("NumericLiteralSegment"),
                # Can `GROUP BY coalesce(col, 1)`
                Ref("ExpressionSegment"),
                Ref("CubeRollupClauseSegment"),
                Ref("GroupingSetsClauseSegment"),
                Bracketed(),  # Allows empty parentheses
            ),
            terminator=OneOf(
                Sequence("ORDER", "BY"),
                "LIMIT",
                "HAVING",
                "QUALIFY",
                Ref("SetOperatorSegment"),
            ),
        ),
        Dedent,
    )


@exasol_dialect.segment()
class CubeRollupClauseSegment(BaseSegment):
    """`CUBE` / `ROLLUP` clause within the `GROUP BY` clause."""

    type = "cube_rollup_clause"
    match_grammar = StartsWith(
        OneOf("CUBE", "ROLLUP"),
        terminator=OneOf(
            "HAVING",
            "QUALIFY",
            Sequence("ORDER", "BY"),
            "LIMIT",
            Ref("SetOperatorSegment"),
        ),
    )
    parse_grammar = Sequence(
        OneOf("CUBE", "ROLLUP"),
        Bracketed(
            Ref("GroupingExpressionList"),
        ),
    )


@exasol_dialect.segment()
class GroupingSetsClauseSegment(BaseSegment):
    """`GROUPING SETS` clause within the `GROUP BY` clause."""

    type = "grouping_sets_clause"
    match_grammar = StartsWith(
        Sequence("GROUPING", "SETS"),
        terminator=OneOf(
            "HAVING",
            "QUALIFY",
            Sequence("ORDER", "BY"),
            "LIMIT",
            Ref("SetOperatorSegment"),
        ),
    )
    parse_grammar = Sequence(
        "GROUPING",
        "SETS",
        Bracketed(
            Delimited(
                Ref("CubeRollupClauseSegment"),
                Ref("GroupingExpressionList"),
                Bracketed(),  # Allows empty parentheses
            )
        ),
    )


@exasol_dialect.segment()
class GroupingExpressionList(BaseSegment):
    """Grouping expression list within `CUBE` / `ROLLUP` `GROUPING SETS`."""

    type = "grouping_expression_list"
    match_grammar = Delimited(
        OneOf(
            Bracketed(Delimited(Ref("ExpressionSegment"))),
            Ref("ExpressionSegment"),
        )
    )


@exasol_dialect.segment()
class QualifyClauseSegment(BaseSegment):
    """`QUALIFY` clause within `SELECT`."""

    type = "qualify_clause"
    match_grammar = StartsWith(
        "QUALIFY",
        terminator=OneOf(
            Sequence("ORDER", "BY"),
            "LIMIT",
            Ref("SetOperatorSegment"),
        ),
    )
    parse_grammar = Sequence("QUALIFY", Ref("ExpressionSegment"))


@exasol_dialect.segment(replace=True)
class LimitClauseSegment(BaseSegment):
    """A `LIMIT` clause like in `SELECT`."""

    type = "limit_clause"
    match_grammar = StartsWith("LIMIT")
    parse_grammar = Sequence(
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


############################
# DROP
############################


@exasol_dialect.segment(replace=True)
class DropStatementSegment(BaseSegment):
    """A `DROP` statement without any options."""

    type = "drop_statement"
    is_ddl = False
    is_dml = False
    is_dql = False
    is_dcl = True
    match_grammar = StartsWith("DROP")
    parse_grammar = OneOf(
        Ref("DropWithouOptionsStatementSegment"),
        Ref("DropCascadeStatementSegment"),
        Ref("DropCascadeRestrictStatementSegment"),
        Ref("DropSchemaStatementSegment"),
        Ref("DropTableStatementSegment"),
    )


@exasol_dialect.segment()
class DropWithouOptionsStatementSegment(BaseSegment):
    """A `DROP` statement without any options."""

    type = "drop_wo_options"
    is_ddl = False
    is_dml = False
    is_dql = False
    is_dcl = True
    match_grammar = Sequence(
        "DROP",
        OneOf(
            "CONNECTION",
            Sequence(
                Ref.keyword("ADAPTER", optional=True),
                "SCRIPT",
            ),
            Sequence("CONSUMER", "GROUP"),
        ),
        Ref("IfExistsGrammar", optional=True),
        Ref("ObjectReferenceSegment"),
    )


@exasol_dialect.segment()
class DropCascadeStatementSegment(BaseSegment):
    """A `DROP` statement with CASCADE option.

    https://docs.exasol.com/sql/drop_role.htm
    https://docs.exasol.com/sql/drop_user.htm
    """

    type = "drop_cascade"

    is_ddl = False
    is_dml = False
    is_dql = False
    is_dcl = True

    match_grammar = Sequence(
        "DROP",
        OneOf(
            "USER",
            "ROLE",
        ),
        Ref("IfExistsGrammar", optional=True),
        Ref("ObjectReferenceSegment"),
        Ref.keyword("CASCADE", optional=True),
    )


@exasol_dialect.segment()
class DropCascadeRestrictStatementSegment(BaseSegment):
    """A `DROP` statement with CASCADE and RESTRICT option.

    https://docs.exasol.com/sql/drop_view.htm
    https://docs.exasol.com/sql/drop_function.htm
    """

    type = "drop_cascade_restrict"

    is_ddl = True
    is_dml = False
    is_dql = False
    is_dcl = False

    match_grammar = Sequence(
        "DROP",
        OneOf(
            "VIEW",
            "FUNCTION",
        ),
        Ref("IfExistsGrammar", optional=True),
        Ref("ObjectReferenceSegment"),
        OneOf("RESTRICT", "CASCADE", optional=True),
    )


############################
# SCHEMA
############################


@exasol_dialect.segment(replace=True)
class CreateSchemaStatementSegment(BaseSegment):
    """A `CREATE SCHEMA` statement.

    https://docs.exasol.com/sql/create_schema.htm
    """

    type = "create_schema_statement"
    is_ddl = True
    is_dml = False
    is_dql = False
    is_dcl = False
    match_grammar = StartsWith(Sequence("CREATE", "SCHEMA"))
    parse_grammar = Sequence(
        "CREATE",
        "SCHEMA",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("SchemaReferenceSegment"),
    )


@exasol_dialect.segment()
class CreateVirtualSchemaStatementSegment(BaseSegment):
    """A `CREATE VIRUTAL SCHEMA` statement.

    https://docs.exasol.com/sql/create_schema.htm
    """

    type = "create_virtual_schema_statement"
    is_ddl = True
    is_dml = False
    is_dql = False
    is_dcl = False
    match_grammar = StartsWith(Sequence("CREATE", "VIRTUAL", "SCHEMA"))
    parse_grammar = Sequence(
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


@exasol_dialect.segment()
class AlterSchemaStatementSegment(BaseSegment):
    """A `ALTER VIRUTAL SCHEMA` statement.

    https://docs.exasol.com/sql/alter_schema.htm
    """

    type = "alter_schema_statement"

    is_ddl = True
    is_dml = False
    is_dql = False
    is_dcl = False
    match_grammar = StartsWith(Sequence("ALTER", "SCHEMA"))
    parse_grammar = Sequence(
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
            Sequence("CHANGE", "OWNER", Ref("SchemaReferenceSegment")),
        ),
    )


@exasol_dialect.segment()
class AlterVirtualSchemaStatementSegment(BaseSegment):
    """A `ALTER VIRUTAL SCHEMA` statement.

    https://docs.exasol.com/sql/alter_schema.htm
    """

    type = "alter_virtual_schema_statement"

    is_ddl = True
    is_dml = False
    is_dql = False
    is_dcl = False
    match_grammar = StartsWith(Sequence("ALTER", "VIRTUAL", "SCHEMA"))
    parse_grammar = Sequence(
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
            Sequence("CHANGE", "OWNER", Ref("NakedIdentifierSegment")),
        ),
    )


@exasol_dialect.segment(replace=True)
class DropSchemaStatementSegment(BaseSegment):
    """A `DROP` statement for EXASOL schema.

    https://docs.exasol.com/sql/drop_schema.htm
    """

    type = "drop_schema"

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
        OneOf("RESTRICT", Ref.keyword("CASCADE", optional=True), optional=True),
    )


############################
# VIEW
############################
@exasol_dialect.segment()
class ViewReferenceSegment(ansi_dialect.get_segment("ObjectReferenceSegment")):  # type: ignore
    """A reference to an schema."""

    type = "view_reference"


@exasol_dialect.segment(replace=True)
class CreateViewStatementSegment(BaseSegment):
    """A `CREATE VIEW` statement.

    https://docs.exasol.com/sql/create_view.htm
    """

    type = "create_view_statement"

    is_ddl = True
    is_dml = False
    is_dql = False
    is_dcl = False
    match_grammar = StartsWith(
        Sequence(
            "CREATE",
            Ref("OrReplaceGrammar", optional=True),
            Ref.keyword("FORCE", optional=True),
            "VIEW",
        )
    )
    parse_grammar = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        Ref.keyword("FORCE", optional=True),
        "VIEW",
        Ref("ViewReferenceSegment"),
        Bracketed(
            Delimited(
                Sequence(
                    Ref("ColumnReferenceSegment"),
                    Ref("CommentIsGrammar", optional=True),
                ),
            ),
            optional=True,
        ),
        "AS",
        OneOf(
            Bracketed(Ref("SelectableGrammar")),
            Ref("SelectableGrammar"),
        ),
        Ref("CommentIsGrammar", optional=True),
        # TODO: (...) COMMENT IS '...' works, without brackets doesn't work
        # COMMENT is matched as an identifier...
    )


############################
# TABLE
############################
@exasol_dialect.segment(replace=True)
class CreateTableStatementSegment(BaseSegment):
    """A `CREATE TABLE` statement.

    https://docs.exasol.com/sql/create_table.htm
    """

    type = "create_table_statement"

    is_ddl = True
    is_dml = False
    is_dql = False
    is_dcl = False
    match_grammar = StartsWith(
        Sequence("CREATE", Ref("OrReplaceGrammar", optional=True), "TABLE")
    )
    parse_grammar = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        "TABLE",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        OneOf(
            # Columns and comment syntax:
            Bracketed(
                Sequence(
                    Ref("TableContentDefinitionSegment"),
                    AnyNumberOf(
                        Sequence(
                            Ref("CommaSegment"),
                            Ref("TableContentDefinitionSegment"),
                        ),
                    ),
                    Sequence(
                        Ref("CommaSegment"),
                        Ref("TableDistributionPartitonClause"),
                        optional=True,
                    ),
                ),
            ),
            # Create AS syntax:
            Sequence(
                "AS",
                Ref("SelectableGrammar"),
                Sequence(
                    # TODO: this only works if there are brackets
                    # around the selectable grammar. this should even
                    # work without brackets
                    "WITH",
                    Ref.keyword("NO", optional=True),
                    "DATA",
                    optional=True,
                ),
            ),
            # Create like syntax
            Ref("CreateTableLikeClauseSegment"),
        ),
        Ref("CommentIsGrammar", optional=True),
    )


@exasol_dialect.segment()
class TableContentDefinitionSegment(BaseSegment):
    """The table content definition."""

    type = "table_content_definition"
    match_grammar = OneOf(
        Ref("ColumnDefinitionSegment"),
        Ref("TableOutOfLineConstraintSegment"),
        Ref("CreateTableLikeClauseSegment"),
    )


@exasol_dialect.segment()
class ColumnDatatypeSegment(BaseSegment):
    """sequence of column and datatype definition."""

    type = "column_datatype_definition"
    match_grammar = Sequence(
        Ref("SingleIdentifierGrammar"),
        Ref("DatatypeSegment"),
    )


@exasol_dialect.segment(replace=True)
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
            Bracketed(
                Ref("NumericLiteralSegment"),
                Sequence(
                    Ref("CommaSegment"), Ref("NumericLiteralSegment"), optional=True
                ),
                optional=True,
            ),
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
            Bracketed(Ref("NumericLiteralSegment"), optional=True),
            "TO",
            "MONTH",
        ),
        Sequence(
            "INTERVAL",
            "DAY",
            Bracketed(Ref("NumericLiteralSegment"), optional=True),
            "TO",
            "SECOND",
            Bracketed(Ref("NumericLiteralSegment"), optional=True),
        ),
        Sequence(
            "GEOMETRY",
            Bracketed(Ref("NumericLiteralSegment"), optional=True),
        ),
        Sequence(
            "HASHTYPE",
            Bracketed(
                Ref("NumericLiteralSegment"),
                OneOf("BIT", "BYTE", optional=True),
                optional=True,
            ),
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
                    Bracketed(
                        Ref("NumericLiteralSegment"),
                        OneOf("CHAR", "BYTE", optional=True),
                        optional=True,
                    ),
                ),
                Sequence("LONG", "VARCHAR"),
                Sequence(
                    "CHARACTER",
                    Sequence(
                        OneOf(Sequence("LARGE", "OBJECT"), "VARYING", optional=True),
                        Bracketed(Ref("NumericLiteralSegment"), optional=True),
                    ),
                ),
                Sequence(
                    "CLOB",
                    Bracketed(Ref("NumericLiteralSegment"), optional=True),
                ),
            ),
            Ref("CharCharacterSetSegment", optional=True),
        ),
    )


@exasol_dialect.segment(replace=True)
class ColumnDefinitionSegment(BaseSegment):
    """Column definition within a `CREATE / ALTER TABLE` statement."""

    type = "column_definition"
    match_grammar = Sequence(
        Ref("ColumnDatatypeSegment"),
        Ref("ColumnConstraintSegment", optional=True),
    )


@exasol_dialect.segment(replace=True)
class ColumnConstraintSegment(BaseSegment):
    """A column option; each CREATE TABLE column can have 0 or more."""

    type = "column_option"
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
        Ref("CommentIsGrammar", optional=True),
    )


@exasol_dialect.segment()
class TableInlineConstraintSegment(BaseSegment):
    """Inline table constraint for CREATE / ALTER TABLE."""

    type = "table_constraint_definition"
    match_grammar = StartsWith(
        OneOf("CONSTRAINT", "NOT", "NULL", "PRIMARY", "FOREIGN"),
        terminator=OneOf("COMMENT", Ref("CommaSegment"), Ref("EndBracketSegment")),
    )
    parse_grammar = Sequence(
        Sequence(
            "CONSTRAINT",
            AnyNumberOf(
                Ref("NakedIdentifierSegment"),
                max_times=1,
                min_times=0,
                # exclude UNRESERVED_KEYWORDS which could used as NakedIdentifier
                # to make e.g. `id NUMBER CONSTRAINT PRIMARY KEY` work (which is equal to just
                # `id NUMBER PRIMARY KEY`)
                exclude=OneOf("NOT", "NULL", "PRIMARY", "FOREIGN"),
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


@exasol_dialect.segment()
class TableOutOfLineConstraintSegment(BaseSegment):
    """Out of line table constraint for CREATE / ALTER TABLE."""

    type = "table_constraint_definition"
    match_grammar = StartsWith(
        OneOf("CONSTRAINT", "PRIMARY", "FOREIGN"),
        terminator=OneOf(Ref("CommaSegment"), "DISTRIBUTE", "PARTITION"),
    )
    parse_grammar = Sequence(
        Sequence(
            "CONSTRAINT",
            AnyNumberOf(
                Ref("NakedIdentifierSegment"),
                max_times=1,
                min_times=0,
                # exclude UNRESERVED_KEYWORDS which could used as NakedIdentifier
                # to make e.g. `id NUMBER, CONSTRAINT PRIMARY KEY(id)` work (which is equal to just
                # `id NUMBER, PRIMARY KEY(id)`)
                exclude=OneOf("NOT", "NULL", "PRIMARY", "FOREIGN"),
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


@exasol_dialect.segment()
class CreateTableLikeClauseSegment(BaseSegment):
    """`CREATE TABLE` LIKE clause."""

    type = "table_like_clause"
    match_grammar = Sequence(
        "LIKE",
        Ref("TableReferenceSegment"),
        Bracketed(
            AnyNumberOf(
                Sequence(
                    Ref("SingleIdentifierGrammar"),
                    Ref("AliasExpressionSegment", optional=True),
                ),
                Ref("CommaSegment", optional=True),
                min_times=1,
            ),
            optional=True,
        ),
        Sequence(OneOf("INCLUDING", "EXCLUDING"), "DEFAULTS", optional=True),
        Sequence(OneOf("INCLUDING", "EXCLUDING"), "IDENTITY", optional=True),
        Sequence(OneOf("INCLUDING", "EXCLUDING"), "COMMENTS", optional=True),
    )


@exasol_dialect.segment()
class TableDistributionPartitonClause(BaseSegment):
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


@exasol_dialect.segment(replace=True)
class AlterTableStatementSegment(BaseSegment):
    """`ALTER TABLE` statement."""

    type = "alter_table_statement"

    is_ddl = True
    is_dml = False
    is_dql = False
    is_dcl = False
    match_grammar = StartsWith(Sequence("ALTER", "TABLE"))
    parse_grammar = OneOf(
        Ref("AlterTableColumnSegment"),
        Ref("AlterTableConstraintSegment"),
        Ref("AlterTableDistributePartitionSegment"),
    )


@exasol_dialect.segment()
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


@exasol_dialect.segment()
class AlterTableAddColumnSegment(BaseSegment):
    """ALTER TABLE ADD.."""

    type = "alter_table_add_column"
    match_grammar = Sequence(
        "ADD",
        Ref.keyword("COLUMN", optional=True),
        Ref("IfNotExistsGrammar", optional=True),
        OptionallyBracketed(Ref("ColumnDefinitionSegment")),
    )


@exasol_dialect.segment()
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


@exasol_dialect.segment()
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


@exasol_dialect.segment()
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


@exasol_dialect.segment()
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


@exasol_dialect.segment()
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


@exasol_dialect.segment()
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
            Ref("TableDistributionPartitonClause"),
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


@exasol_dialect.segment()
class DropTableStatementSegment(BaseSegment):
    """A `DROP` table statement.

    https://docs.exasol.com/sql/drop_table.htm
    """

    type = "drop_table"
    match_grammar = StartsWith(Sequence("DROP", "TABLE"))
    parse_grammar = Sequence(
        "DROP",
        "TABLE",
        Ref("IfExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        OneOf("RESTRICT", Ref.keyword("CASCADE", optional=True), optional=True),
        Sequence("CASCADE", "CONSTRAINTS", optional=True),
    )


############################
# RENAME
############################
@exasol_dialect.segment()
class RenameStatementSegment(BaseSegment):
    """`RENAME` statement.

    https://docs.exasol.com/sql/rename.htm
    """

    type = "rename_statement"

    is_ddl = True
    is_dml = False
    is_dql = False
    is_dcl = False
    match_grammar = StartsWith("RENAME")
    parse_grammar = Sequence(
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


@exasol_dialect.segment()
class CommentStatementSegment(BaseSegment):
    """`COMMENT` statement.

    https://docs.exasol.com/sql/comment.htm
    """

    type = "comment_statement"

    is_ddl = True
    is_dml = False
    is_dql = False
    is_dcl = False
    match_grammar = StartsWith(Sequence("COMMENT", "ON"))
    parse_grammar = Sequence(
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
@exasol_dialect.segment(replace=True)
class InsertStatementSegment(BaseSegment):
    """A `INSERT` statement."""

    type = "insert_statement"

    is_ddl = False
    is_dml = True
    is_dql = False
    is_dcl = False

    match_grammar = StartsWith("INSERT")
    parse_grammar = Sequence(
        "INSERT",
        Ref.keyword("INTO", optional=True),
        Ref("TableReferenceSegment"),
        AnyNumberOf(
            Ref("ValuesInsertClauseSegment"),
            Sequence("DEFAULT", "VALUES"),
            Ref("SelectableGrammar"),
            Ref("BracketedColumnReferenceListGrammar", optional=True),
        ),
    )


@exasol_dialect.segment()
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
                    ephemeral_name="ValuesClauseElements",
                )
            ),
        ),
    )


############################
# UPDATE
############################


@exasol_dialect.segment(replace=True)
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

    match_grammar = StartsWith("UPDATE")
    parse_grammar = Sequence(
        "UPDATE",
        OneOf(Ref("TableReferenceSegment"), Ref("AliasedTableReferenceGrammar")),
        Ref("SetClauseListSegment"),
        Ref("FromClauseSegment", optional=True),
        Ref("WhereClauseSegment", optional=True),
        Ref("PreferringClauseSegment", optional=True),
    )


@exasol_dialect.segment(replace=True)
class SetClauseListSegment(BaseSegment):
    """Overwritten from ANSI."""

    type = "set_clause_list"
    match_grammar = Sequence(
        "SET",
        Indent,
        Delimited(
            Ref("SetClauseSegment"),
            terminator="FROM",
        ),
        Dedent,
    )


@exasol_dialect.segment(replace=True)
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
@exasol_dialect.segment()
class MergeStatementSegment(BaseSegment):
    """`MERGE` statement.

    https://docs.exasol.com/sql/merge.htm
    """

    type = "merge_statement"

    is_ddl = False
    is_dml = True
    is_dql = False
    is_dcl = False

    match_grammar = StartsWith(
        Sequence("MERGE", "INTO"),
    )
    parse_grammar = Sequence(
        "MERGE",
        "INTO",
        OneOf(Ref("TableReferenceSegment"), Ref("AliasedTableReferenceGrammar")),
        "USING",
        OneOf(
            Ref("TableReferenceSegment"),  # tables/views
            Bracketed(
                Ref("SelectableGrammar"),
            ),  # subquery
        ),
        Ref("AliasExpressionSegment", optional=True),
        Ref("JoinOnConditionSegment"),
        OneOf(
            Sequence(
                Ref("MergeMatchedClauseSegment"),
                Ref("MergeNotMatchedClauseSegment", optional=True),
            ),
            Sequence(
                Ref("MergeNotMatchedClauseSegment"),
                Ref("MergeMatchedClauseSegment", optional=True),
            ),
        ),
    )


@exasol_dialect.segment()
class MergeMatchedClauseSegment(BaseSegment):
    """The `WHEN MATCHED` clause within a `MERGE` statement."""

    type = "merge_when_matched_clause"
    match_grammar = StartsWith(
        Sequence("WHEN", "MATCHED", "THEN", OneOf("UPDATE", "DELETE")),
        terminator=Ref("MergeNotMatchedClauseSegment"),
    )
    parse_grammar = Sequence(
        "WHEN",
        "MATCHED",
        "THEN",
        OneOf(
            Ref("MergeUpdateClauseSegment"),
            Ref("MergeDeleteClauseSegment"),
        ),
    )


@exasol_dialect.segment()
class MergeNotMatchedClauseSegment(BaseSegment):
    """The `WHEN NOT MATCHED` clause within a `MERGE` statement."""

    type = "merge_when_not_matched_clause"
    match_grammar = StartsWith(
        Sequence(
            "WHEN",
            "NOT",
            "MATCHED",
            "THEN",
        ),
        terminator=Ref("MergeMatchedClauseSegment"),
    )
    parse_grammar = Sequence(
        "WHEN",
        "NOT",
        "MATCHED",
        "THEN",
        Ref("MergeInsertClauseSegment"),
    )


@exasol_dialect.segment()
class MergeUpdateClauseSegment(BaseSegment):
    """`UPDATE` clause within the `MERGE` statement."""

    type = "merge_update_clause"
    match_grammar = Sequence(
        "UPDATE",
        Ref("SetClauseListSegment"),
        Ref("WhereClauseSegment", optional=True),
    )


@exasol_dialect.segment()
class MergeDeleteClauseSegment(BaseSegment):
    """`DELETE` clause within the `MERGE` statement."""

    type = "merge_delete_clause"
    match_grammar = Sequence(
        "DELETE",
        Ref("WhereClauseSegment", optional=True),
    )


@exasol_dialect.segment()
class MergeInsertClauseSegment(BaseSegment):
    """`INSERT` clause within the `MERGE` statement."""

    type = "merge_insert_clause"
    match_grammar = Sequence(
        "INSERT",
        Ref("BracketedColumnReferenceListGrammar", optional=True),
        "VALUES",
        Bracketed(
            Delimited(
                OneOf(
                    "DEFAULT",
                    Ref("ExpressionSegment"),
                ),
            )
        ),
        Ref("WhereClauseSegment", optional=True),
    )


############################
# DELETE
############################
@exasol_dialect.segment(replace=True)
class DeleteStatementSegment(BaseSegment):
    """`DELETE` statement.

    https://docs.exasol.com/sql/delete.htm
    """

    type = "delete_statement"

    is_ddl = False
    is_dml = True
    is_dql = False
    is_dcl = False

    match_grammar = StartsWith("DELETE")
    parse_grammar = Sequence(
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
@exasol_dialect.segment(replace=True)
class TruncateStatementSegment(BaseSegment):
    """`TRUNCATE TABLE` statement.

    https://docs.exasol.com/sql/truncate.htm
    """

    type = "truncate_table"

    is_ddl = False
    is_dml = True
    is_dql = False
    is_dcl = False

    match_grammar = StartsWith(Sequence("TRUNCATE", "TABLE"))
    parse_grammar = Sequence(
        "TRUNCATE",
        "TABLE",
        Ref("TableReferenceSegment"),
    )


############################
# IMPORT
############################
@exasol_dialect.segment()
class ImportStatementSegment(BaseSegment):
    """`IMPORT` statement.

    https://docs.exasol.com/sql/import.htm
    """

    type = "import_statement"

    is_ddl = False
    is_dml = True
    is_dql = False
    is_dcl = False

    match_grammar = StartsWith("IMPORT")
    parse_grammar = Sequence(
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


@exasol_dialect.segment()
class ExportStatementSegment(BaseSegment):
    """`EXPORT` statement.

    https://docs.exasol.com/sql/export.htm
    """

    type = "export_statement"
    is_ddl = False
    is_dml = True
    is_dql = False
    is_dcl = False
    match_grammar = StartsWith("EXPORT")
    parse_grammar = Sequence(
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


@exasol_dialect.segment()
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


@exasol_dialect.segment()
class ImportColumnsSegment(BaseSegment):
    """IMPORT COLUMNS."""

    type = "import_columns"
    match_grammar = Sequence(
        OneOf(
            Ref("ColumnDatatypeSegment"),
            Ref("CreateTableLikeClauseSegment"),
        )
    )


@exasol_dialect.segment()
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


@exasol_dialect.segment()
class ImportFromExportIntoDbSrcSegment(BaseSegment):
    """`IMPORT` from or `EXPORT` to a external database source (EXA,ORA,JDBC)."""

    type = "import_export_dbsrc"
    match_grammar = StartsWith(
        OneOf("EXA", "ORA", "JDBC"),
        terminator=OneOf(Ref("ImportErrorsClauseSegment"), Ref("RejectClauseSegment")),
    )
    parse_grammar = Sequence(
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


@exasol_dialect.segment()
class ImportFromExportIntoFileSegment(BaseSegment):
    """`IMPORT` from or `EXPORT` to a file source (FBV,CSV)."""

    type = "import_file"
    match_grammar = StartsWith(
        OneOf("CSV", "FBV", "LOCAL"),
        terminator=Ref("ImportErrorsClauseSegment"),
    )
    parse_grammar = Sequence(
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


@exasol_dialect.segment()
class ImportFromExportIntoScriptSegment(BaseSegment):
    """`IMPORT` from / `EXPORT` to a executed database script."""

    type = "import_script"
    match_grammar = StartsWith("SCRIPT")
    parse_grammar = Sequence(
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


@exasol_dialect.segment()
class ImportErrorsClauseSegment(BaseSegment):
    """`ERRORS` clause."""

    type = "import_errors_clause"
    match_grammar = StartsWith(
        "ERRORS",
    )
    parse_grammar = Sequence(
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


@exasol_dialect.segment()
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


@exasol_dialect.segment()
class RejectClauseSegment(BaseSegment):
    """`REJECT` clause within an import / export statement."""

    type = "reject_clause"
    match_grammar = StartsWith("REJECT")
    parse_grammar = Sequence(
        "REJECT",
        "LIMIT",
        OneOf(
            Ref("NumericLiteralSegment"),
            "UNLIMITED",
        ),
        Ref.keyword("ERRORS", optional=True),
    )


@exasol_dialect.segment()
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


@exasol_dialect.segment()
class FBVColumnDefinitionSegment(BaseSegment):
    """Definition of fbv columns within an `IMPORT` / `EXPORT` statement."""

    type = "fbv_cols"
    match_grammar = Bracketed(
        Delimited(
            AnyNumberOf(
                # IMPORT vaild: SIZE ,START, FORMAT, PADDING, ALIGN
                # EXPORT vaild: SIZE, FORMAT, ALIGN, PADDING
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


@exasol_dialect.segment()
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
@exasol_dialect.segment()
class CreateUserSegment(BaseSegment):
    """`CREATE USER` statement.

    https://docs.exasol.com/sql/create_user.htm
    """

    type = "create_user"

    is_ddl = False
    is_dml = False
    is_dql = False
    is_dcl = True

    match_grammar = StartsWith(
        Sequence("CREATE", "USER"),
    )
    parse_grammar = Sequence(
        "CREATE",
        "USER",
        Ref("NakedIdentifierSegment"),
        "IDENTIFIED",
        OneOf(
            Ref("UserPasswordAuthSegment"),
            Ref("UserKerberosAuthSegment"),
            Ref("UserLDAPAuthSegment"),
        ),
    )


@exasol_dialect.segment()
class AlterUserSegment(BaseSegment):
    """`ALTER USER` statement.

    https://docs.exasol.com/sql/alter_user.htm
    """

    type = "alter_user"

    is_ddl = False
    is_dml = False
    is_dql = False
    is_dcl = True

    match_grammar = StartsWith(
        Sequence("ALTER", "USER"),
    )
    parse_grammar = Sequence(
        "ALTER",
        "USER",
        Ref("NakedIdentifierSegment"),
        OneOf(
            Sequence(
                "IDENTIFIED",
                OneOf(
                    Sequence(
                        Ref("UserPasswordAuthSegment"),
                        Sequence(
                            "REPLACE",
                            Ref("QuotedIdentifierSegment"),
                            optional=True,
                        ),
                    ),
                    Ref("UserLDAPAuthSegment"),
                    Ref("UserKerberosAuthSegment"),
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
                OneOf(Ref("NakedIdentifierSegment"), "NULL"),
            ),
        ),
    )


@exasol_dialect.segment()
class UserPasswordAuthSegment(BaseSegment):
    """user password authentification."""

    type = "password_auth"
    match_grammar = Sequence(
        # password
        "BY",
        Ref("QuotedIdentifierSegment"),
    )


@exasol_dialect.segment()
class UserKerberosAuthSegment(BaseSegment):
    """user kerberos authentification."""

    type = "kerberos_auth"
    match_grammar = StartsWith(Sequence("BY", "KERBEROS"))
    parse_grammar = Sequence(
        "BY",
        "KERBEROS",
        "PRINCIPAL",
        Ref("QuotedLiteralSegment"),
    )


@exasol_dialect.segment()
class UserLDAPAuthSegment(BaseSegment):
    """user ldap authentification."""

    type = "ldap_auth"
    match_grammar = StartsWith(Sequence("AT", "LDAP"))
    parse_grammar = Sequence(
        "AT",
        "LDAP",
        "AS",
        Ref("QuotedLiteralSegment"),
        Ref.keyword("FORCE", optional=True),
    )


############################
# CONSUMER GROUP
############################


@exasol_dialect.segment()
class CreateConsumerGroupSegment(BaseSegment):
    """`CREATE CONSUMER GROUP` statement."""

    type = "create_consumer_group_statement"
    match_grammar = Sequence(
        "CREATE",
        "CONSUMER",
        "GROUP",
        Ref("NakedIdentifierSegment"),
        "WITH",
        Delimited(Ref("ConsumerGroupParameterSegment")),
    )


@exasol_dialect.segment()
class AlterConsumerGroupSegment(BaseSegment):
    """`ALTER CONSUMER GROUP` statement."""

    type = "alter_consumer_group_statement"
    match_grammar = Sequence(
        "ALTER",
        "CONSUMER",
        "GROUP",
        Ref("NakedIdentifierSegment"),
        "SET",
        Delimited(Ref("ConsumerGroupParameterSegment")),
    )


@exasol_dialect.segment()
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
        ),
        Ref("EqualsSegment"),
        OneOf(Ref("QuotedLiteralSegment"), Ref("NumericLiteralSegment")),
    )


############################
# ROLE
############################
@exasol_dialect.segment()
class CreateRoleSegment(BaseSegment):
    """`CREATE ROLE` statement.

    https://docs.exasol.com/sql/create_role.htm
    """

    type = "create_role"

    is_ddl = False
    is_dml = False
    is_dql = False
    is_dcl = True

    match_grammar = StartsWith(
        Sequence("CREATE", "ROLE"),
    )
    parse_grammar = Sequence(
        "CREATE",
        "ROLE",
        Ref("NakedIdentifierSegment"),
    )


@exasol_dialect.segment()
class AlterRoleSegment(BaseSegment):
    """`ALTER ROLE` statement.

    Only allowed to alter CONSUMER GROUPs
    """

    type = "alter_role"

    is_ddl = False
    is_dml = False
    is_dql = False
    is_dcl = True

    match_grammar = StartsWith(
        Sequence("ALTER", "ROLE"),
    )
    parse_grammar = Sequence(
        "ALTER",
        "ROLE",
        Ref("NakedIdentifierSegment"),
        "SET",
        Sequence(
            "CONSUMER_GROUP",
            Ref("EqualsSegment"),
            OneOf(Ref("NakedIdentifierSegment"), "NULL"),
        ),
    )


############################
# CONNECTION
############################
@exasol_dialect.segment()
class CreateConnectionSegment(BaseSegment):
    """`CREATE CONNECTION` statement.

    https://docs.exasol.com/sql/create_connection.htm
    """

    type = "create_connection"

    is_ddl = False
    is_dml = False
    is_dql = False
    is_dcl = True

    match_grammar = StartsWith(
        Sequence("CREATE", Ref("OrReplaceGrammar", optional=True), "CONNECTION"),
    )
    parse_grammar = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        "CONNECTION",
        Ref("NakedIdentifierSegment"),
        "TO",
        Ref("ConnectionDefinition"),
    )


@exasol_dialect.segment()
class AlterConnectionSegment(BaseSegment):
    """`ALTER CONNECTION` statement.

    https://docs.exasol.com/sql/alter_connection.htm
    """

    type = "alter_connection"

    is_ddl = False
    is_dml = False
    is_dql = False
    is_dcl = True

    match_grammar = StartsWith(
        Sequence("ALTER", "CONNECTION"),
    )
    parse_grammar = Sequence(
        "ALTER",
        "CONNECTION",
        Ref("NakedIdentifierSegment"),
        "TO",
        Ref("ConnectionDefinition"),
    )


@exasol_dialect.segment()
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


############################
# GRANT / REVOKE
############################
@exasol_dialect.segment(replace=True)
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

    match_grammar = StartsWith(
        OneOf("GRANT", "REVOKE"),
    )
    parse_grammar = Sequence(
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


@exasol_dialect.segment()
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
                terminator=OneOf("TO", "FROM"),
            ),
        ),
        OneOf("TO", "FROM"),
        Delimited(
            Ref("NakedIdentifierSegment"),
        ),
        Sequence("WITH", "ADMIN", "OPTION", optional=True),  # Grant only
    )


@exasol_dialect.segment()
class GrantRevokeObjectPrivilegesSegment(BaseSegment):
    """`GRANT` / `REVOKE` object privileges."""

    type = "grant_revoke_object_privileges"
    match_grammar = Sequence(
        OneOf(
            Sequence("ALL", Ref.keyword("PRIVILEGES", optional=True)),
            Delimited(Ref("ObjectPrivilegesSegment"), terminator="ON"),
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
                Delimited(Ref("NakedIdentifierSegment")),
            ),
            Sequence(  # Revoke only
                "FROM",
                Delimited(Ref("NakedIdentifierSegment")),
                Sequence("CASCADE", "CONSTRAINTS", optional=True),
            ),
        ),
    )


@exasol_dialect.segment()
class GrantRevokeRolesSegment(BaseSegment):
    """`GRANT` / `REVOKE` roles."""

    type = "grant_revoke_roles"
    match_grammar = Sequence(
        OneOf(
            Sequence("ALL", "ROLES"),  # Revoke only
            Delimited(Ref("NakedIdentifierSegment"), terminator=OneOf("TO", "FROM")),
        ),
        OneOf("TO", "FROM"),
        Delimited(Ref("NakedIdentifierSegment")),
        Sequence("WITH", "ADMIN", "OPTION", optional=True),  # Grant only
    )


@exasol_dialect.segment()
class GrantRevokeImpersonationSegment(BaseSegment):
    """`GRANT` / `REVOKE` impersonation."""

    type = "grant_revoke_impersonation"
    match_grammar = Sequence(
        "IMPERSONATION",
        "ON",
        Delimited(
            Ref("NakedIdentifierSegment"),
            terminator=OneOf("TO", "FROM"),
        ),
        OneOf("TO", "FROM"),
        Delimited(Ref("NakedIdentifierSegment")),
    )


@exasol_dialect.segment()
class GrantRevokeConnectionSegment(BaseSegment):
    """`GRANT` / `REVOKE` connection."""

    type = "grant_revoke_connection"
    match_grammar = Sequence(
        "CONNECTION",
        Delimited(
            Ref("NakedIdentifierSegment"),
            terminator=OneOf("TO", "FROM"),
        ),
        OneOf("TO", "FROM"),
        Delimited(Ref("NakedIdentifierSegment")),
        Sequence("WITH", "ADMIN", "OPTION", optional=True),
    )


@exasol_dialect.segment()
class GrantRevokeConnectionRestrictedSegment(BaseSegment):
    """`GRANT` / `REVOKE` connection restricted."""

    type = "grant_revoke_connection_restricted"
    match_grammar = Sequence(
        "ACCESS",
        "ON",
        "CONNECTION",
        Ref("NakedIdentifierSegment"),
        Sequence(
            "FOR",
            OneOf("SCRIPT", "SCHEMA", optional=True),
            Ref("NakedIdentifierSegment"),
        ),
        OneOf("TO", "FROM"),
        Delimited(Ref("NakedIdentifierSegment")),
    )


@exasol_dialect.segment()
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


@exasol_dialect.segment()
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
@exasol_dialect.segment()
class PreferringClauseSegment(BaseSegment):
    """`PREFERRING` clause of the Exasol Skyline extension.

    https://docs.exasol.com/advanced_analytics/skyline.htm#preferring_clause
    """

    type = "preferring_clause"
    match_grammar = StartsWith(
        "PREFERRING",
        terminator=OneOf(
            "LIMIT",
            Sequence("GROUP", "BY"),
            Sequence("ORDER", "BY"),
            "HAVING",
            "QUALIFY",
            Ref("SetOperatorSegment"),
        ),
    )
    parse_grammar = Sequence(
        "PREFERRING",
        OptionallyBracketed(Ref("PreferringPreferenceTermSegment")),
        Ref("PartitionClauseSegment", optional=True),
    )


@exasol_dialect.segment()
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
                ),
            ),
            OneOf(
                Ref("LiteralGrammar"),
                Ref("BareFunctionSegment"),
                Ref("FunctionSegment"),
                Ref("ColumnReferenceSegment"),
            ),
        ),
        Ref("PreferringPlusPriorTermSegment", optional=True),
    )


@exasol_dialect.segment()
class PreferringPlusPriorTermSegment(BaseSegment):
    """The `PLUS` / `PRIOR TO` or `INVERSE` term within a preferring preference term expression."""

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


@exasol_dialect.segment(replace=True)
class MLTableExpressionSegment(BaseSegment):
    """Not supported."""

    match_grammar = Nothing()


############################
# SYSTEM
############################
@exasol_dialect.segment()
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


@exasol_dialect.segment()
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


@exasol_dialect.segment()
class OpenSchemaSegment(BaseSegment):
    """`OPEN SCHEMA` statement."""

    type = "open_schema_statement"
    match_grammar = Sequence("OPEN", "SCHEMA", Ref("SchemaReferenceSegment"))


@exasol_dialect.segment()
class CloseSchemaSegment(BaseSegment):
    """`CLOSE SCHEMA` statement."""

    type = "close_schema_statement"
    match_grammar = Sequence("CLOSE", "SCHEMA")


@exasol_dialect.segment()
class FlushStatisticsSegment(BaseSegment):
    """`FLUSH STATISTICS` statement."""

    type = "flush_statistics_statement"
    match_grammar = Sequence("FLUSH", "STATISTICS")


@exasol_dialect.segment()
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


@exasol_dialect.segment()
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


@exasol_dialect.segment()
class ImpersonateSegment(BaseSegment):
    """`IMPERSONATE` statement."""

    type = "impersonate_statement"
    match_grammar = Sequence("IMPERSONATE", Ref("SingleIdentifierGrammar"))


@exasol_dialect.segment()
class KillSegment(BaseSegment):
    """`KILL` statement."""

    type = "kill_statement"
    match_grammar = StartsWith("KILL")
    parse_grammar = Sequence(
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


@exasol_dialect.segment()
class TruncateAuditLogsSegment(BaseSegment):
    """`TRUNCATE AUDIT LOGS` statement."""

    type = "truncate_audit_logs_statement"
    match_grammar = StartsWith(Sequence("TRUNCATE", "AUDIT", "LOGS"))
    parse_grammar = Sequence(
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


@exasol_dialect.segment(replace=True)
class TransactionStatementSegment(BaseSegment):
    """A `COMMIT` or `ROLLBACK` statement."""

    type = "transaction_statement"
    match_grammar = Sequence(
        OneOf("COMMIT", "ROLLBACK"), Ref.keyword("WORK", optional=True)
    )


@exasol_dialect.segment()
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


@exasol_dialect.segment()
class ExplainVirtualSegment(BaseSegment):
    """`EXPLAIN VIRTUAL` statement."""

    type = "explain_virtual_statement"
    match_grammar = Sequence("EXPLAIN", "VIRTUAL", Ref("SelectableGrammar"))


############################
# FUNCTION
############################


@exasol_dialect.segment()
class FunctionReferenceSegment(exasol_dialect.get_segment("ObjectReferenceSegment")):  # type: ignore
    """A reference to a function."""

    type = "function_reference"


@exasol_dialect.segment(replace=True)
class CreateFunctionStatementSegment(BaseSegment):
    """A `CREATE FUNCTION` statement."""

    type = "create_function_statement"

    is_ddl = True
    is_dml = False
    is_dql = False
    is_dcl = False

    match_grammar = StartsWith(
        Sequence(
            "CREATE",
            Ref("OrReplaceGrammar", optional=True),
            "FUNCTION",
        ),
        terminator=Ref("FunctionScriptTerminatorSegment"),
    )
    parse_grammar = Sequence(
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
        AnyNumberOf(
            Sequence(
                Ref("VariableNameSegment"),
                Ref("DatatypeSegment"),
                Ref("DelimiterSegment"),
            ),
            optional=True,
        ),
        "BEGIN",
        AnyNumberOf(Ref("FunctionBodySegment")),
        "RETURN",
        Ref("FunctionContentsExpressionGrammar"),
        Ref("DelimiterSegment"),
        "END",
        Ref("FunctionReferenceSegment", optional=True),
        Ref("SemicolonSegment", optional=True),
    )


@exasol_dialect.segment()
class FunctionBodySegment(BaseSegment):
    """The definition of the function body."""

    type = "function_body"
    match_grammar = OneOf(
        Ref("FunctionAssignmentSegment"),
        Ref("FunctionIfBranchSegment"),
        Ref("FunctionForLoopSegment"),
        Ref("FunctionWhileLoopSegment"),
    )


@exasol_dialect.segment()
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


@exasol_dialect.segment()
class FunctionIfBranchSegment(BaseSegment):
    """The definition of a if branch within a function body."""

    type = "function_if_branch"
    match_grammar = Sequence(
        "IF",
        AnyNumberOf(Ref("ExpressionSegment")),
        "THEN",
        AnyNumberOf(Ref("FunctionBodySegment"), min_times=1),
        AnyNumberOf(
            Sequence(
                OneOf("ELSIF", "ELSEIF"),
                Ref("ExpressionSegment"),
                "THEN",
                AnyNumberOf(Ref("FunctionBodySegment"), min_times=1),
            ),
            optional=True,
        ),
        Sequence(
            "ELSE", AnyNumberOf(Ref("FunctionBodySegment"), min_times=1), optional=True
        ),
        "END",
        "IF",
        Ref("SemicolonSegment"),
    )


@exasol_dialect.segment()
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


@exasol_dialect.segment()
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


@exasol_dialect.segment(replace=True)
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
            Sequence(
                Ref("DatePartFunctionNameSegment"),
                Bracketed(
                    Ref(
                        "FunctionContentsGrammar",
                        # The brackets might be empty for some functions...
                        optional=True,
                        ephemeral_name="FunctionContentsGrammar",
                    ),
                ),
            ),
            Ref("PostFunctionGrammar", optional=True),
        ),
        Sequence(
            Sequence(
                AnyNumberOf(
                    Ref("FunctionNameSegment"),
                    max_times=1,
                    min_times=1,
                    exclude=Ref("DatePartFunctionNameSegment"),
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


@exasol_dialect.segment(replace=True)
class DatePartFunctionNameSegment(BaseSegment):
    """DATEADD function name segment.

    Need to be able to specify this as type function_name
    so that linting rules identify it properly
    """

    type = "function_name"
    match_grammar = OneOf(
        "ADD_DAYS",
        "ADD_HOURS",
        "ADD_MINUTES",
        "ADD_MONTHS",
        "ADD_SECONDS",
        "ADD_WEEKS",
        "ADD_YEARS",
    )


############################
# SCRIPT
############################
@exasol_dialect.segment()
class ScriptReferenceSegment(exasol_dialect.get_segment("ObjectReferenceSegment")):  # type: ignore
    """A reference to a script."""

    type = "script_reference"


@exasol_dialect.segment()
class ScriptContentSegment(BaseSegment):
    """This represents the script content.

    Because the script content could be written in
    LUA, PYTHON, JAVA or R there is no further verification.
    """

    type = "script_content"
    match_grammar = Anything()


@exasol_dialect.segment()
class CreateScriptingLuaScriptStatementSegment(BaseSegment):
    """`CREATE SCRIPT` statement to create a Lua scripting script.

    https://docs.exasol.com/sql/create_script.htm
    """

    type = "create_scripting_lua_script"

    is_ddl = True
    is_dml = False
    is_dql = False
    is_dcl = False

    match_grammar = StartsWith(
        Sequence(
            "CREATE",
            Ref("OrReplaceGrammar", optional=True),
            Ref.keyword("LUA", optional=True),
            "SCRIPT",
        ),
        terminator=Ref("FunctionScriptTerminatorSegment"),
    )
    parse_grammar = Sequence(
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


@exasol_dialect.segment()
class CreateUDFScriptStatementSegment(BaseSegment):
    """`CREATE SCRIPT` statement create a UDF script.

    https://docs.exasol.com/sql/create_script.htm
    """

    type = "create_udf_script"

    is_ddl = True
    is_dml = False
    is_dql = False
    is_dcl = False

    match_grammar = StartsWith(
        Sequence(
            "CREATE",
            Ref("OrReplaceGrammar", optional=True),
            OneOf(
                "JAVA",
                "PYTHON",
                "LUA",
                "R",
                Ref("SingleIdentifierGrammar"),
                optional=True,
            ),
            OneOf("SCALAR", "SET"),
            "SCRIPT",
        )
    )
    parse_grammar = Sequence(
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
        OneOf(Sequence("RETURNS", Ref("DatatypeSegment")), Ref("EmitsGrammar")),
        "AS",
        Indent,
        Ref("ScriptContentSegment"),
        Dedent,
    )


@exasol_dialect.segment()
class CreateAdapterScriptStatementSegment(BaseSegment):
    """`CREATE SCRIPT` statement create a adapter script.

    https://docs.exasol.com/sql/create_script.htm
    """

    type = "create_adapter_script"

    is_ddl = True
    is_dml = False
    is_dql = False
    is_dcl = False

    match_grammar = StartsWith(
        Sequence(
            "CREATE",
            Ref("OrReplaceGrammar", optional=True),
            OneOf("JAVA", "PYTHON", Ref("SingleIdentifierGrammar"), optional=True),
            "ADAPTER",
            "SCRIPT",
        )
    )
    parse_grammar = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        OneOf("JAVA", "PYTHON", Ref("SingleIdentifierGrammar"), optional=True),
        "ADAPTER",
        "SCRIPT",
        Ref("ScriptReferenceSegment"),
        "AS",
        Indent,
        Ref("ScriptContentSegment"),
        Dedent,
    )


############################
# DIALECT
############################
@exasol_dialect.segment()
class FunctionScriptStatementSegment(BaseSegment):
    """A generic segment, to any of its child subsegments."""

    type = "statement"
    match_grammar = OneOf(
        Ref("CreateFunctionStatementSegment"),
        Ref("CreateScriptingLuaScriptStatementSegment"),
        Ref("CreateUDFScriptStatementSegment"),
        Ref("CreateAdapterScriptStatementSegment"),
    )


@exasol_dialect.segment(replace=True)
class StatementSegment(BaseSegment):
    """A generic segment, to any of its child subsegments."""

    type = "statement"
    match_grammar = GreedyUntil(Ref("SemicolonSegment"))

    parse_grammar = OneOf(
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
        Ref("DropStatementSegment"),
        Ref("RenameStatementSegment"),
        # Access Control Language (DCL)
        Ref("AccessStatementSegment"),
        Ref("AlterConnectionSegment"),
        Ref("AlterUserSegment"),
        Ref("CreateConnectionSegment"),
        Ref("CreateRoleSegment"),
        Ref("CreateUserSegment"),
        # System
        Ref("CreateConsumerGroupSegment"),
        Ref("AlterConsumerGroupSegment"),
        Ref("AlterRoleSegment"),
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
    )


@exasol_dialect.segment(replace=True)
class FileSegment(BaseFileSegment):
    """This overwrites the FileSegment from ANSI.

    The reason is because SCRIPT and FUNCTION statements
    are terminated by a trailing / at the end.
    A semicolon is the terminator of the statement within the function / script
    """

    parse_grammar = AnyNumberOf(
        Delimited(
            Ref("FunctionScriptStatementSegment"),
            delimiter=Ref("FunctionScriptTerminatorSegment"),
            allow_gaps=True,
            allow_trailing=True,
        ),
        Delimited(
            Ref("StatementSegment"),
            delimiter=Ref("DelimiterSegment"),
            allow_gaps=True,
            allow_trailing=True,
        ),
    )
