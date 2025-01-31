"""The Oracle dialect.

This inherits from the ansi dialect.
"""

from typing import cast

from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.core.parser import (
    AnyNumberOf,
    Anything,
    BaseFileSegment,
    BaseSegment,
    Bracketed,
    BracketedSegment,
    CodeSegment,
    CommentSegment,
    CompositeComparisonOperatorSegment,
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
    WordSegment,
)
from sqlfluff.dialects import dialect_ansi as ansi

ansi_dialect = load_raw_dialect("ansi")
oracle_dialect = ansi_dialect.copy_as(
    "oracle",
    formatted_name="Oracle",
    docstring="""The dialect for `Oracle`_ SQL. Note: this does not include PL/SQL.

.. _`Oracle`: https://www.oracle.com/database/technologies/appdev/sql.html""",
)

oracle_dialect.sets("unreserved_keywords").difference_update(["COMMENT"])
oracle_dialect.sets("reserved_keywords").update(
    [
        "COMMENT",
        "ON",
        "UPDATE",
        "INDEXTYPE",
        "PROMPT",
        "FORCE",
        "OVERFLOW",
        "ERROR",
        "PRIVATE",
        "DEFINITION",
        "CONNECT",
        "SIBLINGS",
        "START",
        "CONNECT_BY_ROOT",
        "PIVOT",
        "FOR",
        "UNPIVOT",
        "NOCOPY",
        "SHARING",
        "AUTHID",
        "ACCESSIBLE",
        "PACKAGE",
        "ELSIF",
        "ROWTYPE",
        "REVERSE",
        "CROSSEDITION",
        "FOLLOWS",
        "PRECEDES",
        "INSERTING",
        "UPDATING",
        "DELETING",
        "NESTED",
        "PRAGMA",
        "PARENT",
        "COMPOUND",
        "CONSTANT",
        "MUTABLE",
        "INDICES",
        "FORALL",
        "PAIRS",
        "RAISE",
        "SHARD_ENABLE",
        "PARALLEL_ENABLE",
        "RESULT_CACHE",
        "PIPELINED",
        "SQL_MACRO",
        "COMPILE",
        "DEBUG",
        "REUSE",
    ]
)

oracle_dialect.sets("unreserved_keywords").update(
    ["EDITIONABLE", "EDITIONING", "NONEDITIONABLE", "KEEP"]
)

oracle_dialect.sets("bare_functions").clear()
oracle_dialect.sets("bare_functions").update(
    [
        "current_date",
        "current_timestamp",
        "dbtimezone",
        "localtimestamp",
        "sessiontimestamp",
        "sysdate",
        "systimestamp",
    ]
)


oracle_dialect.patch_lexer_matchers(
    [
        RegexLexer("word", r"[a-zA-Z][0-9a-zA-Z_$#]*", WordSegment),
        RegexLexer(
            "single_quote",
            r"'([^'\\]|\\|\\.|'')*'",
            CodeSegment,
            segment_kwargs={
                "quoted_value": (r"'((?:[^'\\]|\\|\\.|'')*)'", 1),
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
        RegexLexer(
            "numeric_literal",
            r"(?>\d+\.\d+|\d+\.(?![\.\w])|\d+)(\.?[eE][+-]?\d+)?((?<!\.)|(?=\b))",
            LiteralSegment,
        ),
    ]
)

oracle_dialect.insert_lexer_matchers(
    [
        RegexLexer(
            "prompt_command",
            r"PROMPT([^(\r\n)])*((?=\n)|(?=\r\n))?",
            CommentSegment,
        ),
        StringLexer("at_sign", "@", CodeSegment),
    ],
    before="word",
)

oracle_dialect.insert_lexer_matchers(
    # JSON Operators: https://www.postgresql.org/docs/9.5/functions-json.html
    [
        StringLexer("right_arrow", "=>", CodeSegment),
    ],
    before="equals",
)

oracle_dialect.add(
    AtSignSegment=StringParser("@", SymbolSegment, type="at_sign"),
    RightArrowSegment=StringParser("=>", SymbolSegment, type="right_arrow"),
    OnCommitGrammar=Sequence(
        "ON",
        "COMMIT",
        OneOf(
            Sequence(OneOf("DROP", "PRESERVE"), Ref.keyword("DEFINITION")),
            Sequence(OneOf("DELETE", "PRESERVE"), Ref.keyword("ROWS")),
        ),
    ),
    ConnectByRootGrammar=Sequence("CONNECT_BY_ROOT", Ref("NakedIdentifierSegment")),
    PlusJoinSegment=Bracketed(
        StringParser("+", SymbolSegment, type="plus_join_symbol")
    ),
    PlusJoinGrammar=OneOf(
        Sequence(
            OneOf(Ref("ColumnReferenceSegment"), Ref("FunctionSegment")),
            Ref("EqualsSegment"),
            Ref("ColumnReferenceSegment"),
            Ref("PlusJoinSegment"),
        ),
        Sequence(
            Ref("ColumnReferenceSegment"),
            Ref("PlusJoinSegment"),
            Ref("EqualsSegment"),
            OneOf(Ref("ColumnReferenceSegment"), Ref("FunctionSegment")),
        ),
    ),
    IntervalUnitsGrammar=OneOf("YEAR", "MONTH", "DAY", "HOUR", "MINUTE", "SECOND"),
    PivotForInGrammar=Sequence(
        "FOR",
        OptionallyBracketed(Delimited(Ref("ColumnReferenceSegment"))),
        "IN",
        Bracketed(
            Delimited(
                Sequence(
                    Ref("Expression_D_Grammar"),
                    Ref("AliasExpressionSegment", optional=True),
                )
            )
        ),
    ),
    UnpivotNullsGrammar=Sequence(OneOf("INCLUDE", "EXCLUDE"), "NULLS"),
    StatementAndDelimiterGrammar=Sequence(
        Ref("StatementSegment"),
        Ref("DelimiterGrammar", optional=True),
    ),
    OneOrMoreStatementsGrammar=AnyNumberOf(
        Ref("StatementAndDelimiterGrammar"),
        min_times=1,
    ),
    TimingPointGrammar=Sequence(
        OneOf("BEFORE", "AFTER", Sequence("INSTEAD", "OF")),
        OneOf("STATEMENT", Sequence("EACH", "ROW")),
    ),
)

oracle_dialect.replace(
    # https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/DROP-TABLE.html
    DropBehaviorGrammar=Sequence(
        Sequence(
            "CASCADE",
            "CONSTRAINTS",
            optional=True,
        ),
        Ref.keyword("PURGE", optional=True),
        optional=True,
    ),
    NakedIdentifierSegment=SegmentGenerator(
        lambda dialect: RegexParser(
            r"[A-Z0-9_]*[A-Z][A-Z0-9_#$]*",
            IdentifierSegment,
            type="naked_identifier",
            anti_template=r"^(" + r"|".join(dialect.sets("reserved_keywords")) + r")$",
            casefold=str.upper,
        )
    ),
    PostFunctionGrammar=AnyNumberOf(
        Ref("WithinGroupClauseSegment"),
        Ref("FilterClauseGrammar"),
        Ref("OverClauseSegment", optional=True),
    ),
    FunctionContentsExpressionGrammar=OneOf(
        Ref("ExpressionSegment"),
        Ref("NamedArgumentSegment"),
    ),
    FunctionContentsGrammar=ansi_dialect.get_grammar("FunctionContentsGrammar").copy(
        insert=[
            Ref("ListaggOverflowClauseSegment"),
        ]
    ),
    TemporaryGrammar=Sequence(
        OneOf("GLOBAL", "PRIVATE"),
        Ref.keyword("TEMPORARY"),
        optional=True,
    ),
    ParameterNameSegment=RegexParser(
        r'[A-Z_][A-Z0-9_$]*|"[^"]*"', CodeSegment, type="parameter"
    ),
    LiteralGrammar=ansi_dialect.get_grammar("LiteralGrammar").copy(
        insert=[
            Ref("SqlplusVariableGrammar"),
        ],
        before=Ref("ArrayLiteralSegment"),
    ),
    BaseExpressionElementGrammar=ansi_dialect.get_grammar(
        "BaseExpressionElementGrammar"
    ).copy(
        insert=[
            Ref("ConnectByRootGrammar"),
        ]
    ),
    Expression_D_Grammar=Sequence(
        OneOf(
            Ref("PlusJoinGrammar"),
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
                        Ref("LocalAliasSegment"),  # WHERE (LOCAL.a, LOCAL.b) IN (...)
                    ),
                ),
                parse_mode=ParseMode.GREEDY,
            ),
            # Allow potential select statement without brackets
            Ref("SelectStatementSegment"),
            Ref("LiteralGrammar"),
            Ref("IntervalExpressionSegment"),
            Ref("TypedStructLiteralSegment"),
            Ref("ArrayExpressionSegment"),
            Ref("ColumnReferenceSegment"),
            # For triggers, we allow "NEW.*" but not just "*" nor "a.b.*"
            # So can't use WildcardIdentifierSegment nor WildcardExpressionSegment
            Sequence(
                Ref("SingleIdentifierGrammar"),
                Ref("ObjectReferenceDelimiterGrammar"),
                Ref("StarSegment"),
            ),
            Sequence(
                Ref("StructTypeSegment"),
                Bracketed(Delimited(Ref("ExpressionSegment"))),
            ),
            Sequence(
                Ref("DatatypeSegment"),
                # Don't use the full LiteralGrammar here
                # because only some of them are applicable.
                # Notably we shouldn't use QualifiedNumericLiteralSegment
                # here because it looks like an arithmetic operation.
                OneOf(
                    Ref("QuotedLiteralSegment"),
                    Ref("NumericLiteralSegment"),
                    Ref("BooleanLiteralGrammar"),
                    Ref("NullLiteralSegment"),
                    Ref("DateTimeLiteralGrammar"),
                ),
            ),
            Ref("LocalAliasSegment"),
            terminators=[Ref("CommaSegment")],
        ),
        Ref("AccessorGrammar", optional=True),
        allow_gaps=True,
    ),
    DateTimeLiteralGrammar=Sequence(
        OneOf("DATE", "TIME", "TIMESTAMP", "INTERVAL"),
        TypedParser("single_quote", LiteralSegment, type="date_constructor_literal"),
        Sequence(
            Ref("IntervalUnitsGrammar"),
            Sequence("TO", Ref("IntervalUnitsGrammar"), optional=True),
        ),
    ),
    PreTableFunctionKeywordsGrammar=OneOf("LATERAL"),
    ConditionalCrossJoinKeywordsGrammar=Nothing(),
    UnconditionalCrossJoinKeywordsGrammar=Ref.keyword("CROSS"),
    FunctionParameterGrammar=Sequence(
        Ref("ParameterNameSegment"),
        OneOf(
            Sequence(
                Ref.keyword("IN", optional=True),
                OneOf(Ref("DatatypeSegment"), Ref("ColumnTypeReferenceSegment")),
                Sequence(
                    OneOf(
                        Sequence(Ref("ColonSegment"), Ref("EqualsSegment")), "DEFAULT"
                    ),
                    Ref("ExpressionSegment"),
                    optional=True,
                ),
            ),
            Sequence(
                Ref.keyword("IN", optional=True),
                "OUT",
                Ref.keyword("NOCOPY", optional=True),
                OneOf(Ref("DatatypeSegment"), Ref("ColumnTypeReferenceSegment")),
            ),
        ),
    ),
    DelimiterGrammar=Sequence(
        Ref("SemicolonSegment"), Ref("DivideSegment", optional=True)
    ),
    SelectClauseTerminatorGrammar=OneOf(
        "INTO",
        "FROM",
        "WHERE",
        Sequence("ORDER", "BY"),
        "LIMIT",
        "OVERLAPS",
        Ref("SetOperatorSegment"),
        "FETCH",
    ),
)


class AlterTableStatementSegment(ansi.AlterTableStatementSegment):
    """An `ALTER TABLE` statement.

    https://docs.oracle.com/en/database/oracle/oracle-database/21/sqlrf/ALTER-TABLE.html
    If possible, please keep the order below the same as Oracle's doc:
    """

    match_grammar: Matchable = Sequence(
        "ALTER",
        "TABLE",
        Ref("TableReferenceSegment"),
        OneOf(
            # @TODO all stuff inside this "Delimited" is not validated for Oracle
            Delimited(
                OneOf(
                    # Table options
                    Sequence(
                        Ref("ParameterNameSegment"),
                        Ref("EqualsSegment", optional=True),
                        OneOf(Ref("LiteralGrammar"), Ref("NakedIdentifierSegment")),
                    ),
                ),
            ),
            Ref("AlterTablePropertiesSegment"),
            Ref("AlterTableColumnClausesSegment"),
            Ref("AlterTableConstraintClauses"),
        ),
    )


class AlterTablePropertiesSegment(BaseSegment):
    """ALTER TABLE `alter_table_properties` per defined in Oracle's grammar.

    https://docs.oracle.com/en/database/oracle/oracle-database/21/sqlrf/ALTER-TABLE.html

    If possible, please match the order of this sequence with what's defined in
    Oracle's alter_table_properties grammar.
    """

    type = "alter_table_properties"

    # TODO: There are many more alter_table_properties to implement
    match_grammar = OneOf(
        # Rename
        Sequence(
            "RENAME",
            "TO",
            Ref("TableReferenceSegment"),
        ),
    )


class AlterTableColumnClausesSegment(BaseSegment):
    """ALTER TABLE `column_clauses` per defined in Oracle's grammar.

    https://docs.oracle.com/en/database/oracle/oracle-database/21/sqlrf/ALTER-TABLE.html

    If possible, please match the order of this sequence with what's defined in
    Oracle's column_clauses grammar.
    """

    type = "alter_table_column_clauses"

    match_grammar = OneOf(
        # add_column_clause
        # modify_column_clause
        Sequence(
            OneOf(
                "ADD",
                "MODIFY",
            ),
            OneOf(
                Ref("ColumnDefinitionSegment"),
                Bracketed(Delimited(Ref("ColumnDefinitionSegment"))),
            ),
        ),
        # drop_column_clause
        # @TODO: extend drop_column_clause
        Sequence(
            "DROP",
            OneOf(
                Sequence("COLUMN", Ref("ColumnReferenceSegment")),
                Bracketed(Delimited(Ref("ColumnReferenceSegment"))),
            ),
        ),
        # @TODO: add_period_clause
        # @TODO: drop_period_clause
        # rename_column_clause
        Sequence(
            "RENAME",
            "COLUMN",
            Ref("ColumnReferenceSegment"),
            "TO",
            Ref("ColumnReferenceSegment"),
        ),
        # @TODO: modify_collection_retrieval
        # @TODO: modify_LOB_storage_clause
        # @TODO: alter_varray_col_properties
    )


class AlterTableConstraintClauses(BaseSegment):
    """ALTER TABLE `constraint_clauses` per defined in Oracle's grammar.

    https://docs.oracle.com/en/database/oracle/oracle-database/21/sqlrf/ALTER-TABLE.html

    If possible, please match the order of this sequence with what's defined in
    Oracle's constraint_clauses grammar.
    """

    type = "alter_table_constraint_clauses"

    match_grammar = OneOf(
        Sequence(
            "ADD",
            Ref("TableConstraintSegment"),
        ),
        # @TODO MODIFY
        # @TODO RENAME
        # @TODO DROP
        # drop_constraint_clause
        Sequence(
            "DROP",
            OneOf(
                Sequence(
                    "PRIMARY",
                    "KEY",
                ),
                Sequence(
                    "UNIQUE",
                    Bracketed(Ref("ColumnReferenceSegment")),
                ),
                Sequence("CONSTRAINT", Ref("ObjectReferenceSegment")),
            ),
            Ref.keyword("CASCADE", optional=True),
            Sequence(
                OneOf(
                    "KEEP",
                    "DROP",
                ),
                "INDEX",
                optional=True,
            ),
            Ref.keyword("ONLINE", optional=True),
        ),
    )


class ExecuteFileSegment(BaseSegment):
    """A reference to an indextype."""

    type = "execute_file_statement"

    match_grammar = Sequence(
        OneOf(
            Sequence(
                Ref("AtSignSegment"),
                Ref("AtSignSegment", optional=True),
            ),
            "START",
        ),
        # Probably should have a better file definition but this will do for now
        AnyNumberOf(
            Ref("SingleIdentifierGrammar"),
            Ref("DotSegment"),
            Ref("DivideSegment"),
        ),
    )


class IndexTypeReferenceSegment(BaseSegment):
    """A reference to an indextype."""

    type = "indextype_reference"

    match_grammar = ansi.ObjectReferenceSegment.match_grammar.copy()


# Adding Oracle specific statements.
class StatementSegment(ansi.StatementSegment):
    """A generic segment, to any of its child subsegments.

    Override ANSI to allow exclusion of ExecuteFileSegment.
    """

    type = "statement"

    match_grammar = ansi.StatementSegment.match_grammar.copy(
        insert=[
            Ref("CommentStatementSegment"),
            Ref("BeginEndSegment"),
            Ref("CreateProcedureStatementSegment"),
            Ref("AssignmentStatementSegment"),
            Ref("FunctionSegment"),
            Ref("IfExpressionStatement"),
            Ref("ReturnStatementSegment"),
            Ref("CreateTriggerStatementSegment"),
            Ref("CaseExpressionSegment"),
            Ref("CompoundTriggerBlock"),
            Ref("ForLoopStatementSegment"),
            Ref("ForAllStatementSegment"),
            Ref("RaiseStatementSegment"),
            Ref("CreateFunctionStatementSegment"),
            Ref("AlterFunctionStatementSegment"),
            Ref("AlterTriggerStatementSegment"),
        ],
    )


class FileSegment(BaseFileSegment):
    """A segment representing a whole file or script.

    This is also the default "root" segment of the dialect,
    and so is usually instantiated directly. It therefore
    has no match_grammar.

    Override ANSI to allow addition of ExecuteFileSegment without
    ending in DelimiterGrammar
    """

    match_grammar = AnyNumberOf(
        Ref("ExecuteFileSegment"),
        Delimited(
            Ref("StatementSegment"),
            delimiter=AnyNumberOf(Ref("DelimiterGrammar"), min_times=1),
            allow_gaps=True,
            allow_trailing=True,
        ),
    )


class CommentStatementSegment(BaseSegment):
    """A `Comment` statement.

    COMMENT [text]
    https://docs.oracle.com/cd/B19306_01/server.102/b14200/statements_4009.htm
    """

    type = "comment_statement"

    match_grammar = Sequence(
        "COMMENT",
        "ON",
        Sequence(
            OneOf(
                Sequence(
                    "TABLE",
                    Ref("TableReferenceSegment"),
                ),
                Sequence(
                    "COLUMN",
                    Ref("ColumnReferenceSegment"),
                ),
                Sequence(
                    "OPERATOR",
                    Ref("ObjectReferenceSegment"),
                ),
                Sequence(
                    "INDEXTYPE",
                    Ref("IndexTypeReferenceSegment"),
                ),
                Sequence(
                    "MATERIALIZED",
                    "VIEW",
                    Ref("TableReferenceSegment"),
                ),
            ),
            Sequence("IS", OneOf(Ref("QuotedLiteralSegment"), "NULL")),
        ),
    )


# need to ignore type due to mypy rules on type variables
# see https://mypy.readthedocs.io/en/stable/common_issues.html#variables-vs-type-aliases
# for details
class TableReferenceSegment(ansi.ObjectReferenceSegment):
    """A reference to an table, CTE, subquery or alias.

    Extended from ANSI to allow Database Link syntax using AtSignSegment
    """

    type = "table_reference"
    match_grammar: Matchable = Delimited(
        Ref("SingleIdentifierGrammar"),
        delimiter=OneOf(
            Ref("DotSegment"),
            Sequence(Ref("DotSegment"), Ref("DotSegment")),
            Ref("AtSignSegment"),
        ),
        terminators=[
            "ON",
            "AS",
            "USING",
            Ref("CommaSegment"),
            Ref("CastOperatorSegment"),
            Ref("StartSquareBracketSegment"),
            Ref("StartBracketSegment"),
            Ref("BinaryOperatorGrammar"),
            Ref("ColonSegment"),
            Ref("DelimiterGrammar"),
            Ref("JoinLikeClauseGrammar"),
            BracketedSegment,
        ],
        allow_gaps=False,
    )


class CreateViewStatementSegment(ansi.CreateViewStatementSegment):
    """A `CREATE VIEW` statement."""

    type = "create_view_statement"
    # https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/CREATE-VIEW.html
    match_grammar: Matchable = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        Sequence(Ref.keyword("NO", optional=True), "FORCE", optional=True),
        OneOf(
            "EDITIONING",
            Sequence("EDITIONABLE", Ref.keyword("EDITIONING", optional=True)),
            "NONEDITIONABLE",
            optional=True,
        ),
        Ref.keyword("MATERIALIZED", optional=True),
        "VIEW",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        # Optional list of column names
        Ref("BracketedColumnReferenceListGrammar", optional=True),
        "AS",
        OptionallyBracketed(Ref("SelectableGrammar")),
        Ref("WithNoSchemaBindingClauseSegment", optional=True),
    )


class WithinGroupClauseSegment(BaseSegment):
    """An WITHIN GROUP clause for window functions."""

    type = "withingroup_clause"
    match_grammar = Sequence(
        "WITHIN",
        "GROUP",
        Bracketed(Ref("OrderByClauseSegment", optional=False)),
    )


class ListaggOverflowClauseSegment(BaseSegment):
    """ON OVERFLOW clause of listagg function."""

    type = "listagg_overflow_clause"
    match_grammar = Sequence(
        "ON",
        "OVERFLOW",
        OneOf(
            "ERROR",
            Sequence(
                "TRUNCATE",
                Ref("SingleQuotedIdentifierSegment", optional=True),
                OneOf("WITH", "WITHOUT", optional=True),
                Ref.keyword("COUNT", optional=True),
            ),
        ),
    )


class NamedArgumentSegment(BaseSegment):
    """Named argument to a function.

    https://docs.oracle.com/en/database/oracle/oracle-database/21/lnpls/plsql-subprograms.html#GUID-A7D51201-1711-4F33-827F-70042700801F
    """

    type = "named_argument"
    match_grammar = Sequence(
        Ref("NakedIdentifierSegment"),
        Ref("RightArrowSegment"),
        Ref("ExpressionSegment"),
    )


class CreateTableStatementSegment(BaseSegment):
    """A CREATE TABLE statement.

    https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/CREATE-TABLE.html
    https://oracle-base.com/articles/misc/temporary-tables
    https://oracle-base.com/articles/18c/private-temporary-tables-18c
    """

    type = "create_table_statement"
    match_grammar: Matchable = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        Ref("TemporaryGrammar", optional=True),
        "TABLE",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        OneOf(
            # Columns and comment syntax:
            Sequence(
                Bracketed(
                    Delimited(
                        OneOf(
                            Ref("TableConstraintSegment"),
                            Ref("ColumnDefinitionSegment"),
                        ),
                    )
                ),
                Ref("CommentClauseSegment", optional=True),
                Ref("OnCommitGrammar", optional=True),
            ),
            # Create AS syntax:
            Sequence(
                Ref("OnCommitGrammar", optional=True),
                "AS",
                OptionallyBracketed(Ref("SelectableGrammar")),
            ),
            # Create like syntax
            Sequence("LIKE", Ref("TableReferenceSegment")),
        ),
        Ref("TableEndClauseSegment", optional=True),
    )


class ColumnDefinitionSegment(BaseSegment):
    """A column definition, e.g. for CREATE TABLE or ALTER TABLE."""

    type = "column_definition"
    match_grammar: Matchable = Sequence(
        Ref("SingleIdentifierGrammar"),  # Column name
        OneOf(
            AnyNumberOf(
                Sequence(
                    Ref("ColumnConstraintSegment"),
                    Ref.keyword("ENABLE", optional=True),
                )
            ),
            Sequence(
                Ref("DatatypeSegment"),  # Column type
                # For types like VARCHAR(100), VARCHAR(100 BYTE), VARCHAR (100 CHAR)
                Bracketed(
                    Sequence(
                        Anything(),
                        OneOf(
                            "BYTE",
                            "CHAR",
                            optional=True,
                        ),
                    ),
                    optional=True,
                ),
                AnyNumberOf(
                    Ref("ColumnConstraintSegment", optional=True),
                ),
            ),
        ),
    )


class SqlplusVariableGrammar(BaseSegment):
    """SQLPlus Bind Variables :thing.

    https://docs.oracle.com/en/database/oracle/oracle-database/21/sqpug/using-substitution-variables-sqlplus.html
    """

    type = "sqlplus_variable"

    match_grammar = Sequence(
        OptionallyBracketed(
            Ref("ColonSegment"),
            Ref("ParameterNameSegment"),
            Sequence(Ref("DotSegment"), Ref("ParameterNameSegment"), optional=True),
        )
    )


class ConnectByClauseSegment(BaseSegment):
    """`CONNECT BY` clause used in Hierarchical Queries.

    https://docs.oracle.com/en/database/oracle/oracle-database/21/sqlrf/Hierarchical-Queries.html
    """

    type = "connectby_clause"

    match_grammar: Matchable = Sequence(
        "CONNECT",
        "BY",
        Ref.keyword("NOCYCLE", optional=True),
        Ref("ExpressionSegment"),
    )


class StartWithClauseSegment(BaseSegment):
    """`START WITH` clause used in Hierarchical Queries.

    https://docs.oracle.com/en/database/oracle/oracle-database/21/sqlrf/Hierarchical-Queries.html
    """

    type = "startwith_clause"

    match_grammar: Matchable = Sequence(
        "START",
        "WITH",
        Ref("ExpressionSegment"),
    )


class HierarchicalQueryClauseSegment(BaseSegment):
    """Hierarchical Query.

    https://docs.oracle.com/en/database/oracle/oracle-database/21/sqlrf/Hierarchical-Queries.html
    """

    type = "hierarchical_query_clause"

    match_grammar: Matchable = OneOf(
        Sequence(
            Ref("ConnectByClauseSegment"),
            Ref("StartWithClauseSegment", optional=True),
        ),
        Sequence(
            Ref("StartWithClauseSegment"),
            Ref("ConnectByClauseSegment"),
        ),
    )


class OrderByClauseSegment(ansi.OrderByClauseSegment):
    """A `ORDER BY` clause like in `SELECT`."""

    match_grammar: Matchable = ansi.OrderByClauseSegment.match_grammar.copy(
        insert=[Ref.keyword("SIBLINGS", optional=True)], before=Ref("ByKeywordSegment")
    )


class UnorderedSelectStatementSegment(ansi.UnorderedSelectStatementSegment):
    """A `SELECT` statement without any ORDER clauses or later.

    This is designed for use in the context of set operations,
    for other use cases, we should use the main
    SelectStatementSegment.
    """

    match_grammar = ansi.UnorderedSelectStatementSegment.match_grammar.copy(
        insert=[
            Ref("HierarchicalQueryClauseSegment", optional=True),
            Ref("PivotSegment", optional=True),
            Ref("UnpivotSegment", optional=True),
        ],
        before=Ref("GroupByClauseSegment", optional=True),
        terminators=[
            Ref("HierarchicalQueryClauseSegment"),
            Ref("PivotSegment", optional=True),
            Ref("UnpivotSegment", optional=True),
        ],
    ).copy(
        insert=[
            Ref("IntoClauseSegment", optional=True),
        ],
        before=Ref("FromClauseSegment", optional=True),
    )


class SelectStatementSegment(ansi.SelectStatementSegment):
    """A `SELECT` statement."""

    match_grammar: Matchable = UnorderedSelectStatementSegment.match_grammar.copy(
        insert=[
            Ref("IntoClauseSegment", optional=True),
            Ref("OrderByClauseSegment", optional=True),
            Ref("FetchClauseSegment", optional=True),
            Ref("LimitClauseSegment", optional=True),
            Ref("NamedWindowSegment", optional=True),
        ],
        replace_terminators=True,
        terminators=cast(
            Sequence, ansi.SelectStatementSegment.match_grammar
        ).terminators,
    )


class GreaterThanOrEqualToSegment(CompositeComparisonOperatorSegment):
    """Allow spaces between operators."""

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
    """Allow spaces between operators."""

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
    """Allow spaces between operators."""

    match_grammar = OneOf(
        Sequence(Ref("RawNotSegment"), Ref("RawEqualsSegment")),
        Sequence(Ref("RawLessThanSegment"), Ref("RawGreaterThanSegment")),
    )


class PivotSegment(BaseSegment):
    """Pivot clause.

    https://docs.oracle.com/en/database/oracle/oracle-database/21/sqlrf/SELECT.html
    """

    type = "pivot_clause"

    match_grammar: Matchable = Sequence(
        "PIVOT",
        Ref.keyword("XML", optional=True),
        Bracketed(
            Delimited(
                Ref("FunctionSegment"), Ref("AliasExpressionSegment", optional=True)
            ),
            Ref("PivotForInGrammar"),
        ),
    )


class UnpivotSegment(BaseSegment):
    """Unpivot clause.

    https://docs.oracle.com/en/database/oracle/oracle-database/21/sqlrf/SELECT.html
    """

    type = "unpivot_clause"

    match_grammar: Matchable = Sequence(
        "UNPIVOT",
        Ref("UnpivotNullsGrammar", optional=True),
        Bracketed(
            OptionallyBracketed(Delimited(Ref("ColumnReferenceSegment"))),
            Ref("PivotForInGrammar"),
        ),
    )


class ObjectReferenceSegment(ansi.ObjectReferenceSegment):
    """A reference to an object."""

    # Allow whitespace
    match_grammar: Matchable = Delimited(
        Ref("SingleIdentifierGrammar"),
        delimiter=Ref("ObjectReferenceDelimiterGrammar"),
        terminators=[Ref("ObjectReferenceTerminatorGrammar")],
        allow_gaps=True,
    )


class ColumnReferenceSegment(ObjectReferenceSegment):
    """A reference to column, field or alias."""

    type = "column_reference"


class FunctionNameSegment(BaseSegment):
    """Function name, including any prefix bits, e.g. project or schema."""

    type = "function_name"
    match_grammar: Matchable = Sequence(
        # Project name, schema identifier, etc.
        AnyNumberOf(
            Sequence(
                Ref("SingleIdentifierGrammar"),
                Ref("DotSegment"),
            ),
            terminators=[Ref("BracketedSegment")],
        ),
        # Base function name
        Delimited(
            OneOf(
                Ref("FunctionNameIdentifierSegment"),
                Ref("QuotedIdentifierSegment"),
                terminators=[Ref("BracketedSegment")],
            ),
            delimiter=Ref("AtSignSegment"),
        ),
        allow_gaps=False,
    )


class TransactionStatementSegment(BaseSegment):
    """A `COMMIT`, `ROLLBACK` or `TRANSACTION` statement."""

    type = "transaction_statement"
    match_grammar: Matchable = Sequence(
        # COMMIT [ WORK ] [ AND [ NO ] CHAIN ]
        # ROLLBACK [ WORK ] [ AND [ NO ] CHAIN ]
        # BEGIN | END TRANSACTION | WORK
        # NOTE: "TO SAVEPOINT" is not yet supported
        # https://docs.snowflake.com/en/sql-reference/sql/begin.html
        # https://www.postgresql.org/docs/current/sql-end.html
        OneOf("START", "COMMIT", "ROLLBACK"),
        OneOf("TRANSACTION", "WORK", optional=True),
        Sequence("NAME", Ref("SingleIdentifierGrammar"), optional=True),
        Sequence("AND", Ref.keyword("NO", optional=True), "CHAIN", optional=True),
    )


class BeginEndSegment(BaseSegment):
    """A `BEGIN/END` block.

    Encloses multiple statements into a single statement object.
    """

    type = "begin_end_block"
    match_grammar = Sequence(
        Ref("DeclareStatementSegment", optional=True),
        "BEGIN",
        Indent,
        Ref("OneOrMoreStatementsGrammar"),
        Sequence(
            "EXCEPTION",
            "WHEN",
            OneOf(
                "OTHERS",
                Sequence(
                    Ref("SingleIdentifierGrammar"),
                    AnyNumberOf(
                        Sequence(
                            "OR",
                            Ref("SingleIdentifierGrammar"),
                        )
                    ),
                ),
            ),
            "THEN",
            Ref("OneOrMoreStatementsGrammar"),
            optional=True,
        ),
        Dedent,
        "END",
        Ref("ObjectReferenceSegment", optional=True),
        Ref("DelimiterGrammar"),
    )


class CreateProcedureStatementSegment(BaseSegment):
    """A `CREATE OR ALTER PROCEDURE` statement.

    https://docs.oracle.com/en/database/oracle/oracle-database/23/lnpls/CREATE-PROCEDURE-statement.html
    """

    type = "create_procedure_statement"

    match_grammar = Sequence(
        Ref.keyword("CREATE", optional=True),
        Sequence("OR", "REPLACE", optional=True),
        OneOf("EDITIONABLE", "NONEDITIONABLE", optional=True),
        "PROCEDURE",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("FunctionNameSegment"),
        Delimited(Ref("FunctionParameterListGrammar"), optional=True),
        Sequence("SHARING", OneOf("METADATA", "NONE"), optional=True),
        AnyNumberOf(
            Sequence("DEFAULT", "COLLATION", Ref("NakedIdentifierSegment")),
            Sequence("AUTHID", OneOf("CURRENT_USER", "DEFINER")),
            Sequence(
                "ACCESSIBLE",
                "BY",
                Delimited(
                    Bracketed(
                        Sequence(
                            OneOf(
                                "FUNCTION",
                                "PROCEDURE",
                                "PACKAGE",
                                "TRIGGER",
                                "TYPE",
                                optional=True,
                            ),
                            Ref("FunctionNameSegment"),
                        )
                    )
                ),
            ),
            optional=True,
        ),
        OneOf("IS", "AS"),
        AnyNumberOf(Ref("DeclareStatementSegment"), optional=True),
        Ref("BeginEndSegment", optional=True),
    )


class DeclareStatementSegment(BaseSegment):
    """A declaration segment in PL/SQL.

    https://docs.oracle.com/en/database/oracle/oracle-database/23/lnpls/block.html#GUID-9ACEB9ED-567E-4E1A-A16A-B8B35214FC9D__CJAIABJJ
    """

    type = "declare_segment"

    match_grammar = Sequence(
        Ref.keyword("DECLARE", optional=True),
        AnyNumberOf(
            Delimited(
                OneOf(
                    Sequence(
                        OneOf(
                            Sequence(
                                Ref("SingleIdentifierGrammar"),
                                Ref.keyword("CONSTANT", optional=True),
                                OneOf(
                                    Ref("DatatypeSegment"),
                                    Ref("ColumnTypeReferenceSegment"),
                                    Ref("RowTypeReferenceSegment"),
                                ),
                            ),
                            Sequence(
                                "PRAGMA",
                                Ref("FunctionSegment"),
                            ),
                            Ref("CollectionTypeDefinitionSegment"),
                        ),
                        Sequence("NOT", "NULL", optional=True),
                        Sequence(
                            OneOf(
                                Sequence(Ref("ColonSegment"), Ref("EqualsSegment")),
                                "DEFAULT",
                            ),
                            Ref("ExpressionSegment"),
                            optional=True,
                        ),
                        Ref("DelimiterGrammar"),
                    ),
                    Ref("CreateProcedureStatementSegment"),
                    Ref("CreateFunctionStatementSegment"),
                ),
                delimiter=Ref("DelimiterGrammar"),
                terminators=["BEGIN"],
            )
        ),
    )


class ReturnStatementSegment(BaseSegment):
    """A RETURN statement.

    https://docs.oracle.com/en/database/oracle/oracle-database/23/lnpls/RETURN-statement.html
    """

    type = "return_segment"

    match_grammar = Sequence(
        "RETURN",
        Ref("ExpressionSegment", optional=True),
        Ref("DelimiterGrammar"),
    )


class AssignmentStatementSegment(BaseSegment):
    """A assignment segment in PL/SQL.

    https://docs.oracle.com/en/database/oracle/oracle-database/23/lnpls/assignment-statement.html
    """

    type = "assignment_segment"

    match_grammar = Sequence(
        AnyNumberOf(
            Ref("ObjectReferenceSegment"),
            Bracketed(Ref("ObjectReferenceSegment"), optional=True),
            Ref("DotSegment", optional=True),
        ),
        Ref("ColonSegment"),
        Ref("EqualsSegment"),
        Ref("ExpressionSegment"),
        Ref("DelimiterGrammar"),
    )


class IfExpressionStatement(BaseSegment):
    """IF-ELSE statement.

    https://docs.oracle.com/en/database/oracle/oracle-database/23/lnpls/IF-statement.html
    """

    type = "if_then_statement"

    match_grammar = Sequence(
        Ref("IfClauseSegment"),
        Ref("OneOrMoreStatementsGrammar"),
        AnyNumberOf(
            Sequence(
                "ELSIF",
                Ref("ExpressionSegment"),
                "THEN",
                Ref("OneOrMoreStatementsGrammar"),
            ),
        ),
        Sequence(
            "ELSE",
            Ref("OneOrMoreStatementsGrammar"),
            optional=True,
        ),
        "END",
        "IF",
    )


class IfClauseSegment(BaseSegment):
    """IF clause."""

    type = "if_clause"

    match_grammar = Sequence("IF", Ref("ExpressionSegment"), "THEN")


class ColumnTypeReferenceSegment(BaseSegment):
    """A column type reference segment (e.g. `table_name.column_name%type`)."""

    type = "column_type_reference"

    match_grammar = Sequence(
        Ref("ColumnReferenceSegment"), Ref("ModuloSegment"), "TYPE"
    )


class RowTypeReferenceSegment(BaseSegment):
    """A column type reference segment (e.g. `table_name%rowtype`)."""

    type = "row_type_reference"

    match_grammar = Sequence(
        Ref("TableReferenceSegment"), Ref("ModuloSegment"), "ROWTYPE"
    )


class IntoClauseSegment(BaseSegment):
    """Into Clause Segment.

    https://docs.oracle.com/en/database/oracle/oracle-database/21/lnpls/RETURNING-INTO-clause.html#GUID-38F735B9-1100-45AF-AE71-18FB74A899BE__CJAJDJHC
    """

    type = "into_clause"

    match_grammar = Sequence(
        "INTO",
        Delimited(Ref("SingleIdentifierGrammar")),
    )


class MergeUpdateClauseSegment(BaseSegment):
    """`UPDATE` clause within the `MERGE` statement."""

    type = "merge_update_clause"
    match_grammar: Matchable = Sequence(
        "UPDATE",
        Indent,
        Ref("SetClauseListSegment"),
        Dedent,
        Ref("WhereClauseSegment", optional=True),
    )


class InsertStatementSegment(BaseSegment):
    """An `INSERT` statement."""

    type = "insert_statement"
    match_grammar: Matchable = Sequence(
        "INSERT",
        Ref.keyword("OVERWRITE", optional=True),
        "INTO",
        Ref("TableReferenceSegment"),
        OneOf(
            Ref("SelectableGrammar"),
            Sequence(
                Ref("BracketedColumnReferenceListGrammar"),
                Ref("SelectableGrammar"),
            ),
            Ref("DefaultValuesGrammar"),
            Sequence(
                "VALUES",
                Ref("SingleIdentifierGrammar"),
                Bracketed(Ref("SingleIdentifierGrammar"), optional=True),
                optional=True,
            ),
        ),
    )


class CreateTriggerStatementSegment(BaseSegment):
    """Create Trigger Statement.

    https://docs.oracle.com/en/database/oracle/oracle-database/23/lnpls/CREATE-TRIGGER-statement.html
    """

    type = "create_trigger"

    match_grammar: Matchable = Sequence(
        "CREATE",
        Sequence("OR", "REPLACE", optional=True),
        OneOf("EDITIONABLE", "NONEDITIONABLE", optional=True),
        "TRIGGER",
        Sequence("IF", "NOT", "EXISTS", optional=True),
        Ref("TriggerReferenceSegment"),
        Sequence("SHARING", OneOf("METADATA", "NONE"), optional=True),
        Sequence("DEFAULT", "COLLATION", Ref("NakedIdentifierSegment"), optional=True),
        Sequence(
            OneOf(OneOf("BEFORE", "AFTER"), Sequence("INSTEAD", "OF"), "FOR"),
            Ref("DmlEventClauseSegment"),
        ),
        Ref("ReferencingClauseSegment", optional=True),
        Sequence("FOR", "EACH", "ROW", optional=True),
        Sequence(
            OneOf("FORWARD", "REVERSE", optional=True), "CROSSEDITION", optional=True
        ),
        Sequence(
            OneOf("FOLLOWS", "PRECEDES"),
            Delimited(Ref("TriggerReferenceSegment")),
            optional=True,
        ),
        OneOf("ENABLE", "DISABLE", optional=True),
        Sequence("WHEN", Bracketed(Ref("ExpressionSegment")), optional=True),
        OneOf(Ref("CompoundTriggerBlock"), Ref("OneOrMoreStatementsGrammar")),
        Ref.keyword("END", optional=True),
        Ref("ObjectReferenceSegment", optional=True),
    )


class DmlEventClauseSegment(BaseSegment):
    """DML event clause.

    https://docs.oracle.com/en/database/oracle/oracle-database/23/lnpls/CREATE-TRIGGER-statement.html#GUID-AF9E33F1-64D1-4382-A6A4-EC33C36F237B__BABGDFBI
    """

    type = "dml_event_clause"

    match_grammar: Matchable = Sequence(
        OneOf(
            "DELETE",
            "INSERT",
            Sequence(
                "UPDATE",
                Sequence("OF", Delimited(Ref("ColumnReferenceSegment")), optional=True),
            ),
        ),
        AnyNumberOf(
            Sequence(
                "OR",
                OneOf(
                    "DELETE",
                    "INSERT",
                    Sequence(
                        "UPDATE",
                        Sequence(
                            "OF",
                            Delimited(Ref("ColumnReferenceSegment")),
                            optional=True,
                        ),
                    ),
                ),
            )
        ),
        "ON",
        Sequence("NESTED", "TABLE", Ref("ColumnReferenceSegment"), "OF", optional=True),
        Ref("TableReferenceSegment"),
    )


class ReferencingClauseSegment(BaseSegment):
    """`REFERENCING` clause.

    https://docs.oracle.com/en/database/oracle/oracle-database/23/lnpls/CREATE-TRIGGER-statement.html#GUID-AF9E33F1-64D1-4382-A6A4-EC33C36F237B__BABEBAAB
    """

    type = "referencing_clause"

    match_grammar: Matchable = Sequence(
        "REFERENCING",
        AnyNumberOf(
            Sequence(
                OneOf("OLD", "NEW", "PARENT"),
                Ref.keyword("AS", optional=True),
                Ref("NakedIdentifierSegment"),
            )
        ),
    )


class CaseExpressionSegment(BaseSegment):
    """A `CASE WHEN` clause."""

    type = "case_expression"
    match_grammar: Matchable = OneOf(
        Sequence(
            "CASE",
            ImplicitIndent,
            AnyNumberOf(
                Ref("WhenClauseSegment"),
                reset_terminators=True,
                terminators=[Ref.keyword("ELSE"), Ref.keyword("END")],
            ),
            Ref(
                "ElseClauseSegment",
                optional=True,
                reset_terminators=True,
                terminators=[Ref.keyword("END")],
            ),
            Dedent,
            "END",
            Ref.keyword("CASE", optional=True),
            Ref("SingleIdentifierGrammar", optional=True),
        ),
        Sequence(
            "CASE",
            OneOf(
                Ref("ExpressionSegment"),
                "INSERTING",
                Sequence(
                    "UPDATING", Bracketed(Ref("QuotedLiteralSegment"), optional=True)
                ),
                "DELETING",
            ),
            ImplicitIndent,
            AnyNumberOf(
                Ref("WhenClauseSegment"),
                reset_terminators=True,
                terminators=[Ref.keyword("ELSE"), Ref.keyword("END")],
            ),
            Ref(
                "ElseClauseSegment",
                optional=True,
                reset_terminators=True,
                terminators=[Ref.keyword("END")],
            ),
            Dedent,
            "END",
            Ref.keyword("CASE", optional=True),
            Ref("SingleIdentifierGrammar", optional=True),
        ),
        terminators=[
            Ref("ComparisonOperatorGrammar"),
            Ref("CommaSegment"),
            Ref("BinaryOperatorGrammar"),
        ],
    )


class WhenClauseSegment(BaseSegment):
    """A 'WHEN' clause for a 'CASE' statement."""

    type = "when_clause"
    match_grammar: Matchable = Sequence(
        "WHEN",
        # NOTE: The nested sequence here is to ensure the correct
        # placement of the meta segments when templated elements
        # are present.
        # https://github.com/sqlfluff/sqlfluff/issues/3988
        Sequence(
            ImplicitIndent,
            OneOf(
                Ref("ExpressionSegment"),
                "INSERTING",
                Sequence(
                    "UPDATING", Bracketed(Ref("QuotedLiteralSegment"), optional=True)
                ),
                "DELETING",
            ),
            Dedent,
        ),
        Conditional(Indent, indented_then=True),
        "THEN",
        Conditional(ImplicitIndent, indented_then_contents=True),
        OneOf(Ref("ExpressionSegment"), Ref("OneOrMoreStatementsGrammar")),
        Conditional(Dedent, indented_then_contents=True),
        Conditional(Dedent, indented_then=True),
    )


class ElseClauseSegment(BaseSegment):
    """An 'ELSE' clause for a 'CASE' statement."""

    type = "else_clause"
    match_grammar: Matchable = Sequence(
        "ELSE",
        ImplicitIndent,
        OneOf(Ref("ExpressionSegment"), Ref("OneOrMoreStatementsGrammar")),
        Dedent,
    )


class CompoundTriggerBlock(BaseSegment):
    """A compound trigger block.

    https://docs.oracle.com/en/database/oracle/oracle-database/23/lnpls/CREATE-TRIGGER-statement.html#GUID-AF9E33F1-64D1-4382-A6A4-EC33C36F237B__CJACFCDJ
    """

    type = "compound_trigger_statement"

    match_grammar: Matchable = Sequence(
        "COMPOUND",
        "TRIGGER",
        Ref("DeclareStatementSegment", optional=True),
        AnyNumberOf(Ref("TimingPointSectionSegment")),
    )


class TimingPointSectionSegment(BaseSegment):
    """A timing point section.

    https://docs.oracle.com/en/database/oracle/oracle-database/23/lnpls/CREATE-TRIGGER-statement.html#GUID-AF9E33F1-64D1-4382-A6A4-EC33C36F237B__GUID-2CD49225-7507-458B-8BDF-21C56AFC3527
    """

    type = "timing_point_section"

    match_grammar: Matchable = Sequence(
        Ref("TimingPointGrammar"),
        "IS",
        "BEGIN",
        Ref("OneOrMoreStatementsGrammar"),
        Sequence("END", Ref("TimingPointGrammar")),
        Ref("DelimiterGrammar"),
    )


class CollectionTypeDefinitionSegment(BaseSegment):
    """A collection type definition.

    https://docs.oracle.com/en/database/oracle/oracle-database/23/lnpls/collection-variable.html
    """

    type = "collection_type"

    match_grammar = Sequence(
        "TYPE",
        Ref("SingleIdentifierGrammar"),
        "IS",
        Sequence("TABLE", "OF", optional=True),
        OneOf(
            Ref("DatatypeSegment"),
            Ref("ColumnTypeReferenceSegment"),
            Ref("RowTypeReferenceSegment"),
        ),
        Sequence("OF", Ref("DatatypeSegment"), optional=True),
        Sequence("NOT", "NULL", optional=True),
        Sequence("INDEX", "BY", Ref("DatatypeSegment"), optional=True),
    )


class ForLoopStatementSegment(BaseSegment):
    """A `FOR LOOP` statement.

    https://docs.oracle.com/en/database/oracle/oracle-database/23/lnpls/FOR-LOOP-statement.html
    """

    type = "for_loop_statement"

    match_grammar: Matchable = Sequence(
        "FOR",
        Delimited(
            Sequence(
                Ref("SingleIdentifierGrammar"),
                OneOf("MUTABLE", "IMMUTABLE", optional=True),
            )
        ),
        "IN",
        Delimited(
            Sequence(
                Ref.keyword("REVERSE", optional=True),
                OneOf(
                    Sequence(
                        OneOf(
                            Ref("NumericLiteralSegment"),
                            Ref("SingleIdentifierGrammar"),
                            Sequence(
                                Ref("SingleIdentifierGrammar"),
                                Ref("DotSegment"),
                                Ref("SingleIdentifierGrammar"),
                            ),
                        ),
                        Ref("DotSegment"),
                        Ref("DotSegment"),
                        OneOf(
                            Ref("NumericLiteralSegment"),
                            Ref("SingleIdentifierGrammar"),
                            Sequence(
                                Ref("SingleIdentifierGrammar"),
                                Ref("DotSegment"),
                                Ref("SingleIdentifierGrammar"),
                            ),
                        ),
                    ),
                    Sequence(
                        "VALUES",
                        "OF",
                        Ref("SingleIdentifierGrammar"),
                    ),
                    Sequence(
                        "INDICES",
                        "OF",
                        Ref("SingleIdentifierGrammar"),
                    ),
                    Sequence(
                        "PAIRS",
                        "OF",
                        Ref("SingleIdentifierGrammar"),
                    ),
                    Bracketed(Ref("SelectStatementSegment")),
                ),
            )
        ),
        "LOOP",
        Ref("OneOrMoreStatementsGrammar"),
        "END",
        "LOOP",
        Ref("SingleIdentifierGrammar", optional=True),
    )


class ForAllStatementSegment(BaseSegment):
    """A `FORALL` statement.

    https://docs.oracle.com/en/database/oracle/oracle-database/23/lnpls/FORALL-statement.html
    """

    type = "forall_statement"

    match_grammar = Sequence(
        "FORALL",
        Ref("NakedIdentifierSegment"),
        "IN",
        OneOf(
            Sequence(
                OneOf(
                    Ref("NumericLiteralSegment"),
                    Ref("SingleIdentifierGrammar"),
                    Sequence(
                        Ref("SingleIdentifierGrammar"),
                        Ref("DotSegment"),
                        Ref("SingleIdentifierGrammar"),
                    ),
                ),
                Ref("DotSegment"),
                Ref("DotSegment"),
                OneOf(
                    Ref("NumericLiteralSegment"),
                    Ref("SingleIdentifierGrammar"),
                    Sequence(
                        Ref("SingleIdentifierGrammar"),
                        Ref("DotSegment"),
                        Ref("SingleIdentifierGrammar"),
                    ),
                ),
            ),
            Sequence(
                "VALUES",
                "OF",
                Ref("SingleIdentifierGrammar"),
            ),
        ),
        Sequence("SAVE", "EXCEPTIONS", optional=True),
        OneOf(
            Ref("DeleteStatementSegment"),
            Ref("InsertStatementSegment"),
            Ref("SelectStatementSegment"),
            Ref("UpdateStatementSegment"),
        ),
    )


class RaiseStatementSegment(BaseSegment):
    """A `RAISE` statement.

    https://docs.oracle.com/en/database/oracle/oracle-database/23/lnpls/RAISE-statement.html
    """

    type = "raise_segment"

    match_grammar = Sequence(
        "RAISE",
        Ref("SingleIdentifierGrammar", optional=True),
        Ref("DelimiterGrammar"),
    )


class CreateFunctionStatementSegment(BaseSegment):
    """A `CREATE OR ALTER FUNCTION` statement.

    https://docs.oracle.com/en/database/oracle/oracle-database/23/lnpls/CREATE-FUNCTION-statement.html
    """

    type = "create_function_statement"

    match_grammar = Sequence(
        Ref.keyword("CREATE", optional=True),
        Sequence("OR", "REPLACE", optional=True),
        OneOf("EDITIONABLE", "NONEDITIONABLE", optional=True),
        "FUNCTION",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("FunctionNameSegment"),
        Delimited(Ref("FunctionParameterListGrammar"), optional=True),
        "RETURN",
        Ref("DatatypeSegment"),
        Sequence("SHARING", OneOf("METADATA", "NONE"), optional=True),
        AnyNumberOf(
            Sequence("DEFAULT", "COLLATION", Ref("NakedIdentifierSegment")),
            Sequence("AUTHID", OneOf("CURRENT_USER", "DEFINER")),
            Sequence(
                "ACCESSIBLE",
                "BY",
                Delimited(
                    Bracketed(
                        Sequence(
                            OneOf(
                                "FUNCTION",
                                "PROCEDURE",
                                "PACKAGE",
                                "TRIGGER",
                                "TYPE",
                                optional=True,
                            ),
                            Ref("FunctionNameSegment"),
                        )
                    )
                ),
            ),
            "DETERMINISTIC",
            "SHARD_ENABLE",
            Sequence(
                "PARALLEL_ENABLE",
                Sequence(
                    Bracketed(
                        "PARTITION",
                        Ref("SingleIdentifierGrammar"),
                        "BY",
                        OneOf(
                            "ANY",
                            Sequence(
                                OneOf("HASH", "RANGE"),
                                Bracketed(Delimited(Ref("ColumnReferenceSegment"))),
                                Sequence(
                                    OneOf("ORDER", "CLUSTER"),
                                    Ref("ExpressionSegment"),
                                    "BY",
                                    Bracketed(Delimited(Ref("ColumnReferenceSegment"))),
                                    optional=True,
                                ),
                            ),
                            Sequence("VALUE", Bracketed(Ref("ColumnReferenceSegment"))),
                        ),
                    ),
                    optional=True,
                ),
            ),
            Sequence(
                "RESULT_CACHE",
                Sequence(
                    "RELIES_ON",
                    Bracketed(Delimited(Ref("SingleIdentifierGrammar"))),
                    optional=True,
                ),
            ),
            Sequence("AGGREGATE", "USING", Ref("ObjectReferenceSegment")),
            Sequence(
                "PIPELINED",
                OneOf(
                    Sequence("USING", Ref("ObjectReferenceSegment"), optional=True),
                    Sequence(
                        OneOf("ROW", "TABLE"),
                        "POLYMORPHIC",
                        Sequence("USING", Ref("ObjectReferenceSegment"), optional=True),
                    ),
                ),
            ),
            Sequence(
                "SQL_MACRO",
                Bracketed(
                    Sequence("TYPE", Ref("RightArrowSegment")),
                    OneOf("SCALAR", "TABLE"),
                    optional=True,
                ),
            ),
            optional=True,
        ),
        OneOf("IS", "AS"),
        AnyNumberOf(Ref("DeclareStatementSegment"), optional=True),
        Ref("BeginEndSegment", optional=True),
    )


class AlterFunctionStatementSegment(BaseSegment):
    """An `ALTER FUNCTION` or `ALTER PROCEDURE` statement.

    https://docs.oracle.com/en/database/oracle/oracle-database/23/lnpls/ALTER-FUNCTION-statement.html
    https://docs.oracle.com/en/database/oracle/oracle-database/23/lnpls/ALTER-PROCEDURE-statement.html
    """

    type = "alter_function"

    match_grammar = Sequence(
        "ALTER",
        OneOf("FUNCTION", "PROCEDURE"),
        Sequence("IF", "EXISTS", optional=True),
        Ref("FunctionNameSegment"),
        OneOf(
            Sequence(
                "COMPILE",
                Ref.keyword("DEBUG", optional=True),
                Delimited(
                    Ref("ParameterNameSegment"),
                    Ref("EqualsSegment"),
                    Ref("NakedIdentifierSegment"),
                    optional=True,
                ),
                Sequence("REUSE", "SETTINGS", optional=True),
            ),
            OneOf("EDITIONABLE", "NONEDITIONABLE"),
        ),
        Ref("DelimiterGrammar"),
    )


class AlterTriggerStatementSegment(BaseSegment):
    """An `ALTER TRIGGER` statement.

    https://docs.oracle.com/en/database/oracle/oracle-database/23/lnpls/ALTER-TRIGGER-statement.html
    """

    type = "alter_trigger"

    match_grammar = Sequence(
        "ALTER",
        "TRIGGER",
        Sequence("IF", "EXISTS", optional=True),
        Ref("FunctionNameSegment"),
        OneOf(
            Sequence(
                "COMPILE",
                Ref.keyword("DEBUG", optional=True),
                Delimited(
                    Ref("ParameterNameSegment"),
                    Ref("EqualsSegment"),
                    Ref("NakedIdentifierSegment"),
                    optional=True,
                ),
                Sequence("REUSE", "SETTINGS", optional=True),
            ),
            OneOf("ENABLE", "DISABLE"),
            Sequence("RENAME", "TO", Ref("FunctionNameSegment")),
            OneOf("EDITIONABLE", "NONEDITIONABLE"),
        ),
        Ref("DelimiterGrammar"),
    )
