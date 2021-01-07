"""The EXASOL dialect.

https://docs.exasol.com
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
        "DISTRIBUTE",
        "BY",
        AnyNumberOf(
            Sequence(Ref("CommaSegment", optional=True), Ref("ColumnReferenceSegment")),
            min_times=1,
        ),
        terminator=OneOf(Ref("TablePartitionByGrammar"), Ref("SemicolonSegment")),
        enforce_whitespace_preceeding_terminator=True,
    ),
    TablePartitionByGrammar=StartsWith(
        "PARTITION",
        "BY",
        AnyNumberOf(
            Sequence(Ref("CommaSegment", optional=True), Ref("ColumnReferenceSegment")),
            min_times=1,
        ),
        terminator=OneOf(Ref("TableDistributeByGrammar"), Ref("SemicolonSegment")),
        enforce_whitespace_preceeding_terminator=True,
    ),
    TableConstraintEnableDisableGrammar=OneOf("ENABLE", "DISABLE"),
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
        r"current_timestamp|curdate|current_date|current_user|current_session|current_schema|current_statement",
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
        Ref("SelectableGrammar"),
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
                        Ref("CreateTableColumnDefinitionSegment"),
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
class TableColumnDefinitionSegment(BaseSegment):
    """Column definition within a `CREATE / ALTER TABLE` statement."""

    type = "column_definition"
    match_grammar = Sequence(
        Ref(
            "SingleIdentifierGrammar"
        ),  # TODO: SingleIdentifierGrammar = SingleColumnSegment??
        Ref("DatatypeSegment"),
        Ref("TableColumnOptionSegment", optional=True),
    )


@exasol_dialect.segment()
class TableColumnOptionSegment(BaseSegment):
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
            Sequence(
                "PRIMARY",
                "KEY",
            ),
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
                "PRIMARY",
                "KEY",
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
    """`CREATE / ALTER TABLE` distribution / partition clause."""

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
            Sequence(
                "ADD",
                Ref.keyword("COLUMN", optional=True),
                Ref("IfNotExistsGrammar", optional=True),
                Ref("StartBracketSegment", optional=True),
                Ref("TableColumnDefinitionSegment"),
                Ref("EndBracketSegment", optional=True),
            ),
            Sequence(
                "DROP",
                Ref.keyword("COLUMN", optional=True),
                Ref("IfExistsGrammar", optional=True),
                Ref("SingleIdentifierGrammar"),
                Sequence("CASCADE", "CONSTRAINTS", optional=True),
            ),
            Sequence(
                "MODIFY",
                Ref.keyword("COLUMN", optional=True),
                Ref("StartBracketSegment", optional=True),
                Ref("SingleIdentifierGrammar"),
                Ref("DatatypeSegment", optional=True),
                Ref("TableColumnOptionSegment", optional=True),
                Ref("EndBracketSegment", optional=True),
            ),
            Sequence(
                "RENAME",
                "COLUMN",
                Ref("SingleIdentifierGrammar"),
                "TO",
                Ref("SingleIdentifierGrammar"),
            ),
            Sequence(
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
                                OneOf(
                                    Ref("LiteralGrammar"), Ref("BareFunctionSegment")
                                ),
                            ),
                        ),
                    ),
                    Sequence("DROP", OneOf("IDENTITY", "DEFAULT")),
                ),
            ),
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
                    Sequence("PRIMARY", "KEY"),
                ),
                Ref("TableConstraintEnableDisableGrammar"),
            ),
            Sequence(
                "DROP",
                OneOf(
                    Sequence("CONSTRAINT", Ref("SingleIdentifierGrammar")),
                    Sequence("PRIMARY", "KEY"),
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
    )
