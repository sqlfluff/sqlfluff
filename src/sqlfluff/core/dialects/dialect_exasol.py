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
)

from .exasol_keywords import RESERVED_KEYWORDS, UNRESERVED_KEYWORDS
from .dialect_ansi import ObjectReferenceSegment, ansi_dialect

exasol_dialect = ansi_dialect.copy_as("exasol")

# Clear ANSI Keywords and add all EXASOL keywords
exasol_dialect.sets("unreserved_keywords").clear()
exasol_dialect.sets("unreserved_keywords").update(UNRESERVED_KEYWORDS)
exasol_dialect.sets("reserved_keywords").clear()
exasol_dialect.sets("reserved_keywords").update(RESERVED_KEYWORDS)

# Access column aliases by using the LOCAL keyword
exasol_dialect.add(
    LocalIdentifierSegment=KeywordSegment.make(
        "LOCAL", name="local_identifier", type="identifier"
    ),
    ForeignKeyReferencesClauseGrammar=Sequence(
        "REFERENCES",
        Ref("ColumnReferenceSegment"),
        Ref("BracketedColumnReferenceListGrammar", optional=True),
    ),
    ColumnReferenceListGrammar=Delimited(
        Ref("ColumnReferenceSegment"),
        delimiter=Ref("CommaSegment"),
        ephemeral_name="ColumnReferenceList",
    ),
    CommentIsGrammar=Sequence("COMMENT", "IS", Ref("QuotedLiteralSegment")),
    DistributeByGrammar=Sequence("DISTRIBUTE", "BY", Ref("ColumnReferenceListGrammar")),
    PartitionByGrammar=Sequence("PARTITION", "BY", Ref("ColumnReferenceListGrammar")),
)

exasol_dialect.replace(
    SingleIdentifierGrammar=OneOf(
        Ref("LocalIdentifierSegment"),
        Ref("NakedIdentifierSegment"),
        Ref("QuotedIdentifierSegment"),
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
class DropStatementCascadeSegment(BaseSegment):
    """A `DROP` statement with cascade option.

    https://docs.exasol.com/sql/drop_role.htm
    https://docs.exasol.com/sql/drop_user.htm
    """

    type = "drop_statement_cascade"
    match_grammar = Sequence(
        "DROP",
        OneOf(
            "USER",
            "ROLE",
        ),
        Ref("IfExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        Ref.keyword("CASCADE", optional=True),
    )


@exasol_dialect.segment()
class DropSimpleStatementSegment(BaseSegment):
    """A simple `DROP` statement without any options."""

    type = "drop_simple_statement"
    match_grammar = Sequence(
        "DROP",
        "CONNECTION",
        Ref("IfExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
    )


@exasol_dialect.segment(replace=True)
class DropStatementSegment(BaseSegment):
    """A `DROP` statement."""

    type = "drop_statement"
    match_grammar = Sequence(
        "DROP",
        OneOf(
            "VIEW",
            "FUNCTION",
        ),
        Ref("IfExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        OneOf("RESTRICT", Ref.keyword("CASCADE", optional=True), optional=True),
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
                        Ref("CreateTableOutOfLineConstraintSegment"),
                        Ref("CreateTableLikeClauseSegment"),
                        Ref("DistributeByGrammar", optional=True),
                        Ref("PartitionByGrammar", optional=True),
                        Ref("CommaSegment", optional=True),
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
class CreateTableColumnDefinitionSegment(BaseSegment):
    """Column definition within a `CREATE TABLE` statement."""

    type = "column_definition"
    match_grammar = Sequence(
        Ref("ColumnReferenceSegment"),
        Ref("DatatypeSegment"),
        Ref("CreateTableColumnOptionSegment", optional=True),
    )


@exasol_dialect.segment()
class CreateTableColumnOptionSegment(BaseSegment):
    """A column option; each CREATE TABLE column can have 0 or more."""

    type = "column_constraint"
    # Column constraint from
    # https://www.postgresql.org/docs/12/sql-createtable.html
    match_grammar = Sequence(
        OneOf(
            Sequence(
                "DEFAULT", OneOf(Ref("LiteralGrammar"), Ref("BareFunctionSegment"))
            ),
            Sequence("IDENTITY", Ref("NumericLiteralSegment", optional=True)),
            optional=True,
        ),
        Ref("CreateTableInlineConstraintSegment", optional=True),
        Ref("CommentIsGrammar", optional=True),
    )


@exasol_dialect.segment()
class CreateTableInlineConstraintSegment(BaseSegment):
    """Inline table constraint for CREATE TABLE."""

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
        OneOf("ENABLE", "DISABLE", optional=True),
    )


@exasol_dialect.segment()
class CreateTableOutOfLineConstraintSegment(BaseSegment):
    """Out of line table constraint for CREATE TABLE."""

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
        OneOf("ENABLE", "DISABLE", optional=True),
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
                    Ref("ColumnReferenceSegment"),
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
class DropScriptStatementSegment(BaseSegment):
    """A `DROP` statement for EXASOL scripts.

    https://docs.exasol.com/sql/drop_script.htm
    """

    type = "drop_script_statement"
    match_grammar = Sequence(
        "DROP",
        Ref.keyword("ADAPTER", optional=True),
        "SCRIPT",
        Sequence("IF", "EXISTS", optional=True),
        Ref("TableReferenceSegment"),
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
        Ref("DropStatementSegment"),
        Ref("DropTableStatementSegment"),
        Ref("DropScriptStatementSegment"),
        Ref("DropStatementCascadeSegment"),
        Ref("CreateSchemaStatementSegment"),
        Ref("CreateVirtualSchemaStatementSegment"),
        Ref("AlterSchemaStatementSegment"),
        Ref("AlterVirtualSchemaStatementSegment"),
        Ref("DropSchemaStatementSegment"),
        Ref("DropSimpleStatementSegment"),
        Ref("AccessStatementSegment"),
        Ref("CreateTableStatementSegment"),
        Ref("AlterTableStatementSegment"),
        Ref("CreateViewStatementSegment"),
        Ref("DeleteStatementSegment"),
        Ref("UpdateStatementSegment"),
    )
