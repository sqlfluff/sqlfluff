"""The Oracle dialect.

This inherits from the ansi dialect.
"""
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
    Delimited,
    GreedyUntil,
    Matchable,
    OneOf,
    OptionallyBracketed,
    Ref,
    RegexLexer,
    RegexParser,
    SegmentGenerator,
    Sequence,
    StringLexer,
    StringParser,
    SymbolSegment,
)
from sqlfluff.dialects import dialect_ansi as ansi

ansi_dialect = load_raw_dialect("ansi")
oracle_dialect = ansi_dialect.copy_as("oracle")

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
    ]
)

oracle_dialect.sets("unreserved_keywords").update(
    ["EDITIONABLE", "EDITIONING", "NONEDITIONABLE"]
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
        RegexLexer(
            "code",
            r"[a-zA-Z][0-9a-zA-Z_$#]*",
            CodeSegment,
            segment_kwargs={"type": "code"},
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
    before="code",
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
            ansi.IdentifierSegment,
            type="naked_identifier",
            anti_template=r"^(" + r"|".join(dialect.sets("reserved_keywords")) + r")$",
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
        )
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

    match_grammar = OneOf(
        GreedyUntil(Ref("DelimiterGrammar")), exclude=Ref("ExecuteFileSegment")
    )
    parse_grammar = ansi.StatementSegment.parse_grammar.copy(
        insert=[
            Ref("CommentStatementSegment"),
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

    # NB: We don't need a match_grammar here because we're
    # going straight into instantiating it directly usually.
    parse_grammar = AnyNumberOf(
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


# Inherit from the ANSI ObjectReferenceSegment this way so we can inherit
# other segment types from it.
class ObjectReferenceSegment(ansi.ObjectReferenceSegment):
    """A reference to an object."""

    pass


# need to ignore type due to mypy rules on type variables
# see https://mypy.readthedocs.io/en/stable/common_issues.html#variables-vs-type-aliases
# for details
class TableReferenceSegment(ObjectReferenceSegment):
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
                Bracketed(Anything(), optional=True),  # For types like VARCHAR(100)
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
    """Hiearchical Query.

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
        terminators=[Ref("HierarchicalQueryClauseSegment")],
    )
    parse_grammar: Matchable = ansi.UnorderedSelectStatementSegment.parse_grammar.copy(
        insert=[Ref("HierarchicalQueryClauseSegment", optional=True)],
        before=Ref("GroupByClauseSegment", optional=True),
    )


class SelectStatementSegment(ansi.SelectStatementSegment):
    """A `SELECT` statement."""

    match_grammar: Matchable = ansi.SelectStatementSegment.match_grammar.copy()
    parse_grammar: Matchable = UnorderedSelectStatementSegment.parse_grammar.copy(
        insert=[
            Ref("OrderByClauseSegment", optional=True),
            Ref("FetchClauseSegment", optional=True),
            Ref("LimitClauseSegment", optional=True),
            Ref("NamedWindowSegment", optional=True),
        ]
    )


class GreaterThanOrEqualToSegment(ansi.CompositeComparisonOperatorSegment):
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


class LessThanOrEqualToSegment(ansi.CompositeComparisonOperatorSegment):
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


class NotEqualToSegment(ansi.CompositeComparisonOperatorSegment):
    """Allow spaces between operators."""

    match_grammar = OneOf(
        Sequence(Ref("RawNotSegment"), Ref("RawEqualsSegment")),
        Sequence(Ref("RawLessThanSegment"), Ref("RawGreaterThanSegment")),
    )
