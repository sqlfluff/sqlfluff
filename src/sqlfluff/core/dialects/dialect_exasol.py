"""The EXASOL dialect.

https://docs.exasol.com
https://docs.exasol.com/sql_references/sqlstandardcompliance.htm
"""

from sqlfluff.core.parser import (
    AnyNumberOf,
    BaseSegment,
    Bracketed,
    Dedent,
    Delimited,
    GreedyUntil,
    Indent,
    KeywordSegment,
    NamedSegment,
    Nothing,
    OneOf,
    Ref,
    ReSegment,
    Sequence,
    StartsWith,
)
from sqlfluff.core.dialects.dialect_ansi import ObjectReferenceSegment, ansi_dialect
from sqlfluff.core.dialects.exasol_keywords import (
    BARE_FUNCTIONS,
    RESERVED_KEYWORDS,
    UNRESERVED_KEYWORDS,
)

exasol_dialect = ansi_dialect.copy_as("exasol")

# Clear ANSI Keywords and add all EXASOL keywords
exasol_dialect.sets("unreserved_keywords").clear()
exasol_dialect.sets("unreserved_keywords").update(UNRESERVED_KEYWORDS)
exasol_dialect.sets("reserved_keywords").clear()
exasol_dialect.sets("reserved_keywords").update(RESERVED_KEYWORDS)
exasol_dialect.sets("bare_functions").clear()
exasol_dialect.sets("bare_functions").update(BARE_FUNCTIONS)

exasol_dialect.set_lexer_struct(
    [
        ("range_operator", "regex", r"\.{2}", dict(is_code=True)),
        ("hash", "singleton", "#", dict(is_code=True)),
    ]
    + exasol_dialect.get_lexer_struct()
)

exasol_dialect.patch_lexer_struct(
    [
        # In EXASOL, a double single/double quote resolves as a single/double quote in the string.
        # It's also used for escaping single quotes inside of STATEMENT strings like in the IMPORT function
        # https://docs.exasol.com/sql_references/basiclanguageelements.htm#Delimited_Identifiers
        # https://docs.exasol.com/sql_references/literals.htm
        ("single_quote", "regex", r"'([^']|'')*'", dict(is_code=True)),
        ("double_quote", "regex", r'"([^"]|"")*"', dict(is_code=True)),
        (
            "inline_comment",
            "regex",
            r"--[^\n]*",
            dict(is_comment=True, type="comment", trim_start=("--")),
        ),
    ]
)

# Access column aliases by using the LOCAL keyword
exasol_dialect.add(
    LocalIdentifierSegment=KeywordSegment.make(
        "LOCAL", name="local_identifier", type="identifier"
    ),
    RangeOperator=NamedSegment.make("range_operator", type="range_operator"),
    UnknownSegment=KeywordSegment.make(
        "unknown", name="boolean_literal", type="literal"
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
            Ref("SemicolonSegment"),
        ),
        enforce_whitespace_preceeding_terminator=True,
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
            Ref("SemicolonSegment"),
        ),
        enforce_whitespace_preceeding_terminator=True,
    ),
    TableConstraintEnableDisableGrammar=OneOf("ENABLE", "DISABLE"),
    EscapedIdentifierSegment=ReSegment.make(
        # This matches escaped identifier e.g. [day]. There can be reserved keywords
        # within the square brackets.
        r"\[[A-Z]\]",
        name="escaped_identifier",
        type="identifier",
    ),
)

exasol_dialect.replace(
    SingleIdentifierGrammar=OneOf(
        Ref("LocalIdentifierSegment"),
        Ref("NakedIdentifierSegment"),
        Ref("QuotedIdentifierSegment"),
        Ref("EscapedIdentifierSegment"),
    ),
    # TODO: Remove?
    # exasol_dialect.replace(
    #     SemicolonSegment=SymbolSegment.make(";", name="semicolon", type="semicolon"),
    # )
    ParameterNameSegment=ReSegment.make(
        r"\"?[A-Z][A-Z0-9_]*\"?",
        name="parameter",
        type="parameter",
    ),
    LikeGrammar=Ref.keyword("LIKE"),
    IsClauseGrammar=OneOf(
        "NULL",
        Ref("BooleanLiteralGrammar"),
    ),
    FromClauseTerminatorGrammar=OneOf(
        "WHERE",
        "CONNECT",
        "START",
        "PREFERRING",
        "LIMIT",
        "GROUP",
        "ORDER",
        "HAVING",
        "QUALIFY",
        Ref("SetOperatorSegment"),
        "WITH",
    ),
    WhereClauseTerminatorGrammar=OneOf(
        "CONNECT",
        "START",
        "PREFERRING",
        "LIMIT",
        "GROUP",
        "ORDER",
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
        Ref("SelectClauseSegment"),
        terminator=Ref("SetOperatorSegment"),
        enforce_whitespace_preceeding_terminator=True,
    )

    parse_grammar = Sequence(
        Ref("SelectClauseSegment"),
        # Dedent for the indent in the select clause.
        # It's here so that it can come AFTER any whitespace.
        Dedent,
        Ref("FromClauseSegment", optional=True),
        Ref("WhereClauseSegment", optional=True),
        Ref("ConnectByClauseSegment", optional=True),
        Ref("PreferringClauseSegment", optional=True),
        Ref("GroupByClauseSegment", optional=True),
        Ref("HavingClauseSegment", optional=True),
        Ref("QualifyClauseSegment", optional=True),
        Ref("OrderByClauseSegment", optional=True),
        Ref("LimitClauseSegment", optional=True),
    )


@exasol_dialect.segment(replace=True)
class MainTableExpressionSegment(BaseSegment):
    """The main table expression e.g. within a FROM clause."""

    type = "main_table_expression"
    match_grammar = OneOf(
        Ref("BareFunctionSegment"),
        Ref("FunctionSegment"),
        Ref("TableReferenceSegment"),
        Bracketed(Ref("SelectableGrammar")),
        Ref("ValuesClauseSegment"),
        Ref("ImportStatementSegment"),  # subimport
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
            "GROUP",
            "QUALIFY",
            "ORDER",
            "LIMIT",
            Ref("SetOperatorSegment"),
        ),
        enforce_whitespace_preceeding_terminator=True,
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

    type = "group_by_clause"
    match_grammar = StartsWith(
        Sequence("GROUP", "BY"),
        terminator=OneOf(
            "ORDER",
            "LIMIT",
            "HAVING",
            "QUALIFY",
            Ref("SetOperatorSegment"),
        ),
        enforce_whitespace_preceeding_terminator=True,
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
                Sequence(
                    Ref("StartBracketSegment"), Ref("EndBracketSegment")
                ),  # () possible
            ),
            terminator=OneOf(
                "ORDER",
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
            "ORDER",
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
            "ORDER",
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
                Sequence(
                    Ref("StartBracketSegment"), Ref("EndBracketSegment")
                ),  # () possible
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
            "ORDER",
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


@exasol_dialect.segment()
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
class ViewReferenceSegment(ObjectReferenceSegment):
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
                    AnyNumberOf(
                        Ref("ColumnDefinitionSegment"),
                        Ref("TableOutOfLineConstraintSegment"),
                        Ref("CreateTableLikeClauseSegment"),
                        Ref("CommaSegment", optional=True),
                        Ref("TableDistributionPartitonClause", optional=True),
                        min_times=1,
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
class ColumnDatatypeSegment(BaseSegment):
    """sequence of column and datatype definition."""

    type = "column_datatype_definition"
    match_grammar = Sequence(
        Ref("SingleIdentifierGrammar"),
        Ref("DatatypeSegment"),
    )


@exasol_dialect.segment(replace=True)
class ColumnDefinitionSegment(BaseSegment):
    """Column definition within a `CREATE / ALTER TABLE` statement."""

    type = "column_definition"
    match_grammar = Sequence(
        Ref("ColumnDatatypeSegment"),
        Ref("ColumnOptionSegment", optional=True),
    )


@exasol_dialect.segment(replace=True)
class ColumnOptionSegment(BaseSegment):
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
                Ref("StartBracketSegment", optional=True),
                Ref("NumericLiteralSegment", optional=True),
                Ref("EndBracketSegment", optional=True),
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
    match_grammar = Sequence(
        Sequence("CONSTRAINT", Ref("SingleIdentifierGrammar"), optional=True),
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
    match_grammar = Sequence(
        Sequence("CONSTRAINT", Ref("SingleIdentifierGrammar"), optional=True),
        OneOf(
            # PRIMARY KEY
            Sequence(
                Ref("PrimaryKeyGrammar"),
                Ref("BracketedColumnReferenceListGrammar"),
            ),
            # FOREIGN KEY
            Sequence(
                "FOREIGN",
                "KEY",
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

    type = "alter_table_statment"

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

    type = "alter_table_statement"

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
        Ref("StartBracketSegment", optional=True),
        Ref("ColumnDefinitionSegment"),
        Ref("EndBracketSegment", optional=True),
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
        Ref("StartBracketSegment", optional=True),
        Ref("SingleIdentifierGrammar"),
        Ref("DatatypeSegment", optional=True),
        Ref("ColumnOptionSegment", optional=True),
        Ref("EndBracketSegment", optional=True),
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
                        Ref("StartBracketSegment", optional=True),
                        Ref("NumericLiteralSegment"),
                        Ref("EndBracketSegment", optional=True),
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

    type = "alter_table_statement"

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
                    Sequence("CONSTRAINT", Ref("SingleIdentifierGrammar")),
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

    type = "alter_table_statement"

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
        Ref("BracketedColumnReferenceListGrammar", optional=True),
        OneOf(
            Ref("ValuesClauseSegment"),
            Sequence("DEFAULT", "VALUES"),
            Ref("SelectableGrammar"),
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
        Ref("AliasedTableReferenceSegment"),
        Ref("SetClauseListSegment"),
        Ref("UpdateFromClauseSegment", optional=True),
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


@exasol_dialect.segment()
class UpdateFromClauseSegment(BaseSegment):
    """`FROM` clause within an `UPDATE` statement."""

    type = "update_from_clause"
    match_grammar = Sequence(
        "FROM",
        Delimited(
            Ref("AliasedTableReferenceSegment"),
            terminator="WHERE",
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
        Ref("AliasedTableReferenceSegment"),
        "USING",
        OneOf(
            Ref("TableReferenceSegment"),  # tables/views
            Bracketed(
                Ref("SelectableGrammar"),
            ),  # subquery
        ),
        Ref("AliasExpressionSegment", optional=True),
        Ref("JoinOnConditionSegment"),
        Ref("MergeMatchedClauseSegment", optional=True),
        Ref("MergeNotMatchedClauseSegment", optional=True),
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
        Ref("AliasedTableReferenceSegment"),
        Ref("WhereClauseSegment", optional=True),
        Ref("PreferringClauseSegment", optional=True),
    )


############################
# TRUNCATE
############################
@exasol_dialect.segment()
class TruncateStatmentSegement(BaseSegment):
    """`TRUNCATE TABLE` statement.

    https://docs.exasol.com/sql/truncate.htm
    """

    type = "truncate_table"

    is_ddl = False
    is_dml = True
    is_dql = False
    is_dcl = False

    match_grammar = StartsWith("TRUNCATE")
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

    type = "obejct_privilege"
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
            "GROUP",
            "ORDER",
            "HAVING",
            "QUALIFY",
            Ref("SetOperatorSegment"),
        ),
    )
    parse_grammar = Sequence(
        "PREFERRING",
        OneOf(
            Ref("PreferringPreferenceTermSegment"),
            Bracketed(Ref("PreferringPreferenceTermSegment")),
        ),
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
    """Not supported!"""

    match_grammar = Nothing()


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
        Ref("TruncateStatmentSegement"),
        Ref("UpdateStatementSegment"),
        # Data Definition Language (DDL)
        Ref("AlterTableStatementSegment"),
        Ref("AlterSchemaStatementSegment"),
        Ref("AlterVirtualSchemaStatementSegment"),
        Ref("CommentStatementSegment"),
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
        # Others
        Ref("TransactionStatementSegment"),
    )
