"""The EXASOL dialect.

https://docs.exasol.com
https://docs.exasol.com/sql_references/sqlstandardcompliance.htm
"""

from ..parser import (
    OneOf,
    Ref,
    Sequence,
    Bracketed,
    BaseSegment,
    AnyNumberOf,
    GreedyUntil,
    Delimited,
    KeywordSegment,
    ReSegment,
    Anything,
    Matchable,
    SymbolSegment,
    StartsWith,
    NamedSegment,
    Indent,
    Dedent,
)

from .exasol_keywords import RESERVED_KEYWORDS, UNRESERVED_KEYWORDS
from .dialect_ansi import ObjectReferenceSegment, ansi_dialect

exasol_dialect = ansi_dialect.copy_as("exasol")

# Clear ANSI Keywords and add all EXASOL keywords
exasol_dialect.sets("unreserved_keywords").clear()
exasol_dialect.sets("unreserved_keywords").update(UNRESERVED_KEYWORDS)
exasol_dialect.sets("reserved_keywords").clear()
exasol_dialect.sets("reserved_keywords").update(RESERVED_KEYWORDS)

exasol_dialect.set_lexer_struct(
    [
        (
            "consumer_group",
            "regex",
            r"\bCONSUMER\s+\bGROUP",
            dict(
                is_code=True,
                type="keyword",
            ),
        )
    ]
    + exasol_dialect.get_lexer_struct()
)

# Access column aliases by using the LOCAL keyword
exasol_dialect.add(
    LocalIdentifierSegment=KeywordSegment.make(
        "LOCAL", name="local_identifier", type="identifier"
    ),
    ConsumerGroupSegment=NamedSegment.make(
        "consumer_group",
        type="keyword",  # not a real keyword, but some statements use it as one
    ),
    ForeignKeyReferencesClauseGrammar=Sequence(
        "REFERENCES",
        Ref("TableReferenceSegment"),
        Ref("BracketedColumnReferenceListGrammar", optional=True),
    ),  # TODO Test Fails
    ColumnReferenceListGrammar=Delimited(
        Ref("ColumnReferenceSegment"),
        delimiter=Ref("CommaSegment"),
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
    CharCharacterSetSegment=OneOf(
        Ref.keyword("UTF8"),
        Ref.keyword("ASCII"),
    ),
)

exasol_dialect.replace(  # TODO: SingleIdentifierGrammar -> Column
    SingleIdentifierGrammar=OneOf(
        Ref("LocalIdentifierSegment"),
        Ref("NakedIdentifierSegment"),
        Ref("QuotedIdentifierSegment"),
    ),
)
exasol_dialect.replace(
    BareFunctionSegment=ReSegment.make(
        (
            r"current_timestamp|systimestamp|now|localtimestamp|"
            r"curdate|current_date|sysdate|"
            r"current_user|user|"
            r"current_session|sessiontimezone|dbtimezone|"
            r"current_schema|current_statement|"
            r"rowid|rownum|level"
        ),
        name="bare_function",
        type="bare_function",
    ),
)
exasol_dialect.replace(
    SemicolonSegment=SymbolSegment.make(";", name="semicolon", type="semicolon"),
)
exasol_dialect.replace(
    ParameterNameSegment=ReSegment.make(
        r"\"?[A-Z][A-Z0-9_]*\"?",
        name="parameter",
        type="parameter",
    ),
)
exasol_dialect.replace(LikeGrammar=Ref.keyword("LIKE"))
exasol_dialect.replace(
    IsClauseGrammar=OneOf(
        "NULL",
        Ref("BooleanLiteralGrammar"),
    ),
)
exasol_dialect.replace(
    WhereClauseTerminatorGrammar=OneOf(
        "CONNECT",
        "PREFERRING",
        "LIMIT",
        "GROUP",
        "ORDER",
        "QUALIFY",
        "CUBE",
        "ROLLUP",
        "GROUPING",
    )
)


@exasol_dialect.segment()
class ColumnDatatypeSegment(BaseSegment):
    """sequence of column and datatype definition."""

    type = "column_datatype_definition"
    match_grammar = Sequence(
        Ref(
            "SingleIdentifierGrammar"
        ),  # TODO: SingleIdentifierGrammar = SingleColumnSegment??
        Ref("DatatypeSegment"),
    )


@exasol_dialect.segment()
class OnlyColumnListSegment(BaseSegment):
    """"""

    type = "column_list"
    match_grammar = (
        Delimited(
            Ref("SingleIdentifierGrammar"),
            delimiter=Ref("CommaSegment"),
        ),
    )


@exasol_dialect.segment(replace=True)
class DatatypeSegment(BaseSegment):
    """A data type segment."""

    type = "data_type"
    match_grammar = Sequence(
        Ref("DatatypeIdentifierSegment"),
        Bracketed(
            OneOf(
                Delimited(Ref("NumericLiteralSegment"), delimiter=Ref("CommaSegment")),
                # The brackets might be empty for some cases...
                optional=True,
            ),
            # There may be no brackets for some data types
            optional=True,
        ),
        Ref("CharCharacterSetSegment", optional=True),
    )


@exasol_dialect.segment(replace=True)
class WithCompoundStatementSegment(BaseSegment):
    """A `SELECT` statement preceded by a selection of `WITH` clauses.

    `WITH tab (col1,col2) AS (SELECT a,b FROM x)`
    """

    type = "with_compound_statement"
    # match grammar
    match_grammar = StartsWith("WITH")
    parse_grammar = Sequence(
        "WITH",
        Delimited(
            Sequence(
                Ref("SingleIdentifierGrammar"),
                Bracketed(
                    Ref("OnlyColumnListSegment"),
                    optional=True,
                ),
                "AS",
                Bracketed(
                    # Checkpoint here to subdivide the query.
                    Ref("SelectableGrammar", ephemeral_name="SelectableGrammar")
                ),
            ),
            delimiter=Ref("CommaSegment"),
            terminator=Ref.keyword("SELECT"),  # TODO: wichtig??
        ),
        Ref("NonWithSelectableGrammar"),
    )


@exasol_dialect.segment(replace=True)
class SelectClauseModifierSegment(BaseSegment):
    """Things that come after SELECT but before the columns."""

    type = "select_clause_modifier"
    match_grammar = OneOf(  # TODO: ANY?
        Sequence(
            "DISTINCT",
            Bracketed(
                Ref("OnlyColumnListSegment"),
                optional=True,
            ),
        ),
        "ALL",
    )


@exasol_dialect.segment(replace=True)
class DropStatementSegment(BaseSegment):
    """A `DROP` statement without any options."""

    type = "drop_statement"
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

    type = "drop_statement"
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

    type = "drop_statement"
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
class SchemaReferenceSegment(BaseSegment):
    """A reference to an schema."""

    # TODO: SCHEMA ist ein einzel identifier...
    type = "schema_reference"
    match_grammar: Matchable = Ref("SingleIdentifierGrammar")


@exasol_dialect.segment()
class CreateSchemaStatementSegment(BaseSegment):
    """A `CREATE SCHEMA` statement.

    https://docs.exasol.com/sql/create_schema.htm
    """

    type = "create_schema_statement"
    match_grammar = Sequence(
        "CREATE",
        "SCHEMA",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("SchemaReferenceSegment"),
    )


@exasol_dialect.segment()
class VirtualSchemaAdapterSegment(ObjectReferenceSegment):
    """A adapter segment for virtual schemas."""

    type = "virtual_schema_adapter"


@exasol_dialect.segment()
class CreateVirtualSchemaStatementSegment(BaseSegment):
    """A `CREATE VIRUTAL SCHEMA` statement.

    https://docs.exasol.com/sql/create_schema.htm
    """

    type = "create_virtual_schema_statement"
    match_grammar = Sequence(
        "CREATE",
        "VIRTUAL",
        "SCHEMA",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("SchemaReferenceSegment"),
        "USING",
        Ref("VirtualSchemaAdapterSegment"),
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
            Sequence("CHANGE", "OWNER", Ref("SchemaReferenceSegment")),
        ),
    )


@exasol_dialect.segment()
class AlterVirtualSchemaStatementSegment(BaseSegment):
    """A `ALTER VIRUTAL SCHEMA` statement.

    https://docs.exasol.com/sql/alter_schema.htm
    """

    type = "alter_virtual_schema_statement"
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
                    AnyNumberOf(Ref("TableReferenceSegment"), Ref("CommaSegment")),
                    optional=True,
                ),
            ),
            Sequence("CHANGE", "OWNER", Ref("SchemaReferenceSegment")),
        ),
    )


@exasol_dialect.segment()
class DropSchemaStatementSegment(BaseSegment):
    """A `DROP` statement for EXASOL schema.

    https://docs.exasol.com/sql/drop_schema.htm
    """

    type = "drop_schema_statement"
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
                    Ref("CommentIsGrammar", optional=True),
                ),
                delimiter=Ref("CommaSegment"),
            ),
            optional=True,
        ),
        # Ref("BracketedColumnDefinitionSegment", optional=True),
        "AS",
        OneOf(
            Bracketed(Ref("SelectableGrammar")),
            Ref("SelectableGrammar"),
        ),
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
                    AnyNumberOf(
                        Ref("TableColumnDefinitionSegment"),
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
                Sequence("WITH", Sequence("NO", optional=True), "DATA", optional=True),
            ),
            # Create like syntax
            Ref("CreateTableLikeClauseSegment"),
        ),
        Ref("CommentIsGrammar", optional=True),
    )


@exasol_dialect.segment()
class TableColumnDefinitionSegment(
    BaseSegment
):  # TODO: ColumnDefinitionSegment ueberschreiben?
    """Column definition within a `CREATE / ALTER TABLE` statement."""

    type = "column_definition"
    match_grammar = Sequence(
        Ref("ColumnDatatypeSegment"),
        Ref("TableColumnOptionSegment", optional=True),
    )


@exasol_dialect.segment()
class TableColumnOptionSegment(
    BaseSegment
):  # TODO: ColumnOptionSegment ueberschreiben?
    """A column option; each CREATE TABLE column can have 0 or more."""

    type = "column_constraint"
    # Column constraint from
    # https://www.postgresql.org/docs/12/sql-createtable.html
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
    # Later add support for CHECK constraint, others?
    # e.g. CONSTRAINT constraint_1 PRIMARY KEY(column_1)
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
    # Later add support for CHECK constraint, others?
    # e.g. CONSTRAINT constraint_1 PRIMARY KEY(column_1)
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
    match_grammar = OneOf(
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
        Ref("TableColumnDefinitionSegment"),
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
        Ref("TableColumnOptionSegment", optional=True),
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

    type = "drop_table_statement"
    match_grammar = Sequence(
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
            Ref("ConsumerGroupSegment"),
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
                        delimiter=Ref("CommaSegment"),
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
                    Ref("ConsumerGroupSegment"),
                ),
                Ref("ObjectReferenceSegment"),
                "IS",
                Ref("QuotedLiteralSegment"),
            ),
        ),
    )


############################
# SELECT
############################
@exasol_dialect.segment(replace=True)
class SetOperatorSegment(BaseSegment):
    """A set operator such as Union, Minus, Except or Intersect."""

    type = "set_operator"
    match_grammar = OneOf(
        Sequence("UNION", Ref.keyword("ALL", optional=True)),
        "INTERSECT",
        OneOf("MINUS", "EXCEPT"),
    )


############################
# INSERT
############################
@exasol_dialect.segment(replace=True)
class InsertStatementSegment(BaseSegment):
    """A `INSERT` statement."""

    type = "insert_statement"
    match_grammar = StartsWith("INSERT")
    parse_grammar = Sequence(
        "INSERT",
        Ref.keyword("INTO", optional=True),
        Ref("TableReferenceSegment"),
        Ref("BracketedColumnReferenceListGrammar", optional=True),
        OneOf(
            Sequence(
                "VALUES",
                Delimited(
                    Bracketed(
                        Delimited(
                            OneOf("DEFAULT", Ref("ExpressionSegment")),
                            delimiter=Ref("CommaSegment"),
                            terminator=Ref("EndBracketSegment"),
                        ),
                    ),
                    delimiter=Ref("CommaSegment"),
                ),
            ),
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
    match_grammar = StartsWith("UPDATE")
    parse_grammar = Sequence(
        "UPDATE",
        Ref("AliasedTableReferenceSegment"),
        Ref("SetClauseListSegment"),
        Ref("UpdateFromClauseSegment", optional=True),
        Ref("WhereClauseSegment", optional=True),
        Sequence(
            # TODO: works:                  PARTITION BY (shop_id, order_id)
            #       fails, but should work: PARTITION BY shop_id, order_id
            Ref(
                "PreferringClauseSegment",
            ),
            Ref("PartitionClauseSegment", optional=True),
            optional=True,
        ),
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
            allow_trailing=True,
            delimiter=Ref("CommaSegment"),
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
            delimiter=Ref("CommaSegment"),
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
        Ref("JoinOnCondition"),
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
                delimiter=Ref("CommaSegment"),
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
    match_grammar = StartsWith("DELETE")
    parse_grammar = Sequence(
        "DELETE",
        Ref("StarSegment", optional=True),
        "FROM",
        Ref("AliasedTableReferenceSegment"),
        Ref("WhereClauseSegment", optional=True),
        Sequence(
            # TODO: works:                  PARTITION BY (shop_id, order_id)
            #       fails, but should work: PARTITION BY shop_id, order_id
            Ref(
                "PreferringClauseSegment",
            ),
            Ref("PartitionClauseSegment", optional=True),
            optional=True,
        ),
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
    match_grammar = StartsWith("IMPORT")
    parse_grammar = Sequence(
        "IMPORT",
        Sequence(
            "INTO",
            OneOf(
                Sequence(
                    Ref("TableReferenceSegment"),
                    Bracketed(
                        Ref("OnlyColumnListSegment")
                        # Delimited(
                        #     Ref("SingleIdentifierGrammar"),
                        #     delimiter=Ref("CommaSegment"),
                        # )
                        ,
                        optional=True,
                    ),
                ),
                Bracketed(
                    Delimited(
                        Ref("ImportColumnsSegment"),
                        delimiter=Ref("CommaSegment"),
                    ),
                ),
            ),
            optional=True,
        ),
        Ref("ImportFromClauseSegment"),
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
        Ref("ImportFromDbSrcSegment"),
        Ref("ImportErrorsClauseSegment", optional=True)
        # OneOf(
        #     Sequence(
        #         OneOf(
        #             Ref("ImportFromDbSrcSegment"),
        #             Ref("ImportFromFileSegment"),
        #         ),
        #         Ref("ImportErrorsClauseSegment", optional=True),
        #     ),
        #     Ref("ImportFromScriptSegment"),
        # ),
    )


@exasol_dialect.segment()
class ImportFromDbSrcSegment(BaseSegment):
    """"""

    # TODO: JDBC Support
    type = "import_dbsrc"
    match_grammar = StartsWith(OneOf("EXA", "ORA"))  # , "JDBC"))
    parse_grammar = Sequence(
        OneOf(
            "EXA",
            "ORA",
            # Sequence(
            #     "JDBC",
            #     Sequence(
            #         "DRIVER",
            #         Ref("EqualsSegment"),
            #         Ref("QuotedLiteralSegment"),
            #     ),
            # ),
        ),
        Ref("ImportConnectionDefinition"),
        OneOf(
            Sequence(
                "TABLE",
                Ref("TableReferenceSegment"),
                Bracketed(
                    Ref("OnlyColumnListSegment"),
                    # Delimited(
                    #     Ref("SingleIdentifierGrammar"),
                    #     delimiter=Ref("CommaSegment"),
                    # ),
                    optional=True,
                ),
            ),
            AnyNumberOf(
                Sequence(
                    "STATEMENT",
                    AnyNumberOf(
                        Ref("QuotedLiteralSegment"),
                        # AnyNumberOf to match escaped single quotes
                        # e.g STATEMENT ' SELECT * FROM orders WHERE order_state=''OK'' '
                        min_times=1,
                    ),
                ),
                min_times=1,
            ),
        ),
    )


@exasol_dialect.segment()
class ImportConnectionDefinition(BaseSegment):
    """"""

    type = "import_connection_definition"
    match_grammar = Sequence(
        "AT",
        Ref("ObjectReferenceSegment"),
        Sequence(
            "USER",
            Ref("QuotedLiteralSegment"),
            "IDENTIFIED",
            "BY",
            Ref("QuotedLiteralSegment"),
            optional=True,
        ),
    )


@exasol_dialect.segment()
class ImportFromFileSegment(BaseSegment):
    """"""

    type = "import_file"
    match_grammar = StartsWith(OneOf("CSV", "FBV", "LOCAL"))
    parse_grammar = Sequence()


@exasol_dialect.segment()
class ImportFromScriptSegment(BaseSegment):
    """"""

    type = "import_script"
    match_grammar = StartsWith("SCRIPT")
    parse_grammar = Sequence()


@exasol_dialect.segment()
class ImportErrorsClauseSegment(BaseSegment):
    """"""

    type = "import_errors_clause"
    match_grammar = Sequence(
        "ERRORS",
        "INTO",
        # Ref("ImportErrorDestinationSegment"),
    )


@exasol_dialect.segment()
class ImportErrorDestinationSegment(BaseSegment):
    """"""

    type = "import_error_destination"
    match_grammar = OneOf(
        Sequence(
            "CSV",
            Ref("ImportConnectionDefinition"),
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
            Bracketed(
                Ref.keyword("CURRENT_TIMESTAMP"),  # maybe wrong implementation?
            ),
        ),
    )


############################
# EXPORT
############################
@exasol_dialect.segment()
class ExportStatementSegment(BaseSegment):
    pass


############################
# SKYLINE
############################
@exasol_dialect.segment()
class PreferringClauseSegment(BaseSegment):
    """`PREFERRING` clause of the Exasol Skyline extension.

    https://docs.exasol.com/advanced_analytics/skyline.htm#preferring_clause
    """

    type = "preferring_clause"
    match_grammar = StartsWith("PREFERRING", terminator=Ref("PartitionClauseSegment"))
    parse_grammar = Sequence(
        "PREFERRING",
        OneOf(
            Ref("PreferringPlusPriorTermSegment"),
            Bracketed(
                Ref("PreferringPlusPriorTermSegment"),
            ),
        ),
    )


@exasol_dialect.segment()
class PreferringPlusPriorTermSegment(BaseSegment):
    type = "preference_term"
    match_grammar = AnyNumberOf(
        Sequence(
            Ref("PreferringPreferenceTermSegment"),
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


@exasol_dialect.segment()
class PreferringPreferenceTermSegment(BaseSegment):
    """The preference term of a `PREFERRING` clause."""

    type = "preference_term"
    match_grammar = OneOf(
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
    )


@exasol_dialect.segment(replace=True)
class MLTableExpressionSegment(BaseSegment):
    """Not supported!"""

    # TODO: Warum wird das hier ueberhaupt angesprochen??
    match_grammar = Anything()


@exasol_dialect.segment(replace=True)
class StatementSegment(BaseSegment):
    """A generic segment, to any of its child subsegments."""

    type = "statement"
    match_grammar = GreedyUntil(Ref("SemicolonSegment"))

    parse_grammar = OneOf(
        Ref("SelectableGrammar"),
        Ref("InsertStatementSegment"),
        Ref("TransactionStatementSegment"),
        Ref("DropCascadeRestrictStatementSegment"),
        Ref("DropCascadeStatementSegment"),
        Ref("CreateSchemaStatementSegment"),
        Ref("CreateVirtualSchemaStatementSegment"),
        Ref("AlterSchemaStatementSegment"),
        Ref("AlterVirtualSchemaStatementSegment"),
        Ref("DropSchemaStatementSegment"),
        Ref("DropStatementSegment"),
        Ref("AccessStatementSegment"),
        Ref("CreateTableStatementSegment"),
        Ref("AlterTableStatementSegment"),
        Ref("DropTableStatementSegment"),
        Ref("CreateViewStatementSegment"),
        Ref("DeleteStatementSegment"),
        Ref("UpdateStatementSegment"),
        Ref("RenameStatementSegment"),
        Ref("CommentStatementSegment"),
        Ref("MergeStatementSegment"),
        Ref("TruncateStatmentSegement"),
        Ref("ImportStatementSegment"),
    )
