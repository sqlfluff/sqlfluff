"""The Databricks Dialect.

Functionally, it is quite similar to SparkSQL,
however it's much less strict on keywords.
It also has some extensions.
"""

from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.core.parser import (
    AnyNumberOf,
    Anything,
    BaseSegment,
    Bracketed,
    CodeSegment,
    CommentSegment,
    Dedent,
    Delimited,
    IdentifierSegment,
    Indent,
    Matchable,
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
    WordSegment,
)
from sqlfluff.dialects import dialect_ansi as ansi
from sqlfluff.dialects import dialect_sparksql as sparksql
from sqlfluff.dialects.dialect_databricks_keywords import (
    RESERVED_KEYWORDS,
    UNRESERVED_KEYWORDS,
)

sparksql_dialect = load_raw_dialect("sparksql")
databricks_dialect = sparksql_dialect.copy_as(
    "databricks",
    formatted_name="Databricks",
    docstring="The dialect for `Databricks <https://databricks.com/>`_.",
)

databricks_dialect.sets("unreserved_keywords").update(UNRESERVED_KEYWORDS)
databricks_dialect.sets("unreserved_keywords").update(
    sparksql_dialect.sets("reserved_keywords")
)
databricks_dialect.sets("unreserved_keywords").difference_update(RESERVED_KEYWORDS)
databricks_dialect.sets("reserved_keywords").clear()
databricks_dialect.sets("reserved_keywords").update(RESERVED_KEYWORDS)

databricks_dialect.sets("date_part_function_name").update(["TIMEDIFF"])


databricks_dialect.insert_lexer_matchers(
    # Named Function Parameters:
    # https://docs.databricks.com/en/sql/language-manual/sql-ref-function-invocation.html#named-parameter-invocation
    [
        StringLexer("right_arrow", "=>", CodeSegment),
    ],
    before="equals",
)


databricks_dialect.insert_lexer_matchers(
    # Notebook Cell Delimiter:
    # https://learn.microsoft.com/en-us/azure/databricks/notebooks/notebook-export-import#sql-1
    [
        RegexLexer("command", r"(\r?\n){2}-- COMMAND ----------(\r?\n)", CodeSegment),
    ],
    before="newline",
)

databricks_dialect.insert_lexer_matchers(
    # Databricks Notebook Start:
    # needed to insert "so early" to avoid magic + notebook
    # start to be interpreted as inline comments
    # https://learn.microsoft.com/en-us/azure/databricks/notebooks/notebooks-code#language-magic
    [
        RegexLexer(
            "notebook_start", r"-- Databricks notebook source(\r?\n){1}", CommentSegment
        ),
        RegexLexer(
            "magic_single_line",
            r"(-- MAGIC %)([^\n]{2,})( [^%]{1})([^\n]*)",
            CodeSegment,
        ),
        RegexLexer("magic_line", r"(-- MAGIC)( [^%]{1})([^\n]*)", CodeSegment),
        RegexLexer("magic_start", r"(-- MAGIC %)([^\n]{2,})(\r?\n)", CodeSegment),
    ],
    before="inline_comment",
)


databricks_dialect.add(
    CommandCellSegment=TypedParser("command", CodeSegment, type="statement_terminator"),
    DoubleQuotedUDFBody=TypedParser(
        "double_quote",
        CodeSegment,
        type="udf_body",
        trim_chars=('"',),
    ),
    SingleQuotedUDFBody=TypedParser(
        "single_quote",
        CodeSegment,
        type="udf_body",
        trim_chars=("'",),
    ),
    DollarQuotedUDFBody=TypedParser(
        "dollar_quote",
        CodeSegment,
        type="udf_body",
        trim_chars=("$",),
    ),
    RightArrowSegment=StringParser("=>", SymbolSegment, type="right_arrow"),
    # https://docs.databricks.com/en/sql/language-manual/sql-ref-principal.html
    PrincipalIdentifierSegment=OneOf(
        Ref("NakedIdentifierSegment"),
        Ref("BackQuotedIdentifierSegment"),
    ),
    PredictiveOptimizationGrammar=Sequence(
        OneOf("ENABLE", "DISABLE", "INHERIT"),
        "PREDICTIVE",
        "OPTIMIZATION",
    ),
    SetOwnerGrammar=Sequence(
        Ref.keyword("SET", optional=True),
        "OWNER",
        "TO",
        Ref("PrincipalIdentifierSegment"),
    ),
    SetTagsGrammar=Sequence(
        "SET",
        "TAGS",
        Ref("BracketedPropertyListGrammar"),
    ),
    UnsetTagsGrammar=Sequence(
        "UNSET",
        "TAGS",
        Ref("BracketedPropertyNameListGrammar"),
    ),
    ColumnDefaultGrammar=Sequence(
        "DEFAULT",
        OneOf(
            Ref("LiteralGrammar"),
            Ref("FunctionSegment"),
        ),
    ),
    ConstraintOptionGrammar=Sequence(
        Sequence("ENABLE", "NOVALIDATE", optional=True),
        Sequence("NOT", "ENFORCED", optional=True),
        Sequence("DEFERRABLE", optional=True),
        Sequence("INITIALLY", "DEFERRED", optional=True),
        OneOf("NORELY", "RELY", optional=True),
    ),
    ForeignKeyOptionGrammar=Sequence(
        Sequence("MATCH", "FULL", optional=True),
        Sequence("ON", "UPDATE", "NO", "ACTION", optional=True),
        Sequence("ON", "DELETE", "NO", "ACTION", optional=True),
    ),
    DropConstraintGrammar=Sequence(
        "DROP",
        OneOf(
            Sequence(
                Ref("PrimaryKeyGrammar"),
                Ref("IfExistsGrammar", optional=True),
                OneOf(
                    "RESTRICT",
                    "CASCADE",
                    optional=True,
                ),
            ),
            Sequence(
                Ref("ForeignKeyGrammar"),
                Ref("IfExistsGrammar", optional=True),
                Bracketed(
                    Delimited(
                        Ref("ColumnReferenceSegment"),
                    )
                ),
            ),
            Sequence(
                "CONSTRAINT",
                Ref("IfExistsGrammar", optional=True),
                Ref("ObjectReferenceSegment"),
                OneOf(
                    "RESTRICT",
                    "CASCADE",
                    optional=True,
                ),
            ),
        ),
    ),
    AlterPartitionGrammar=Sequence(
        "PARTITION",
        Bracketed(
            Delimited(
                AnyNumberOf(
                    OneOf(
                        Ref("ColumnReferenceSegment"),
                        Ref("SetClauseSegment"),
                    ),
                    min_times=1,
                ),
            ),
        ),
    ),
    RowFilterClauseGrammar=Sequence(
        "ROW",
        "FILTER",
        Ref("ObjectReferenceSegment"),
        "ON",
        Bracketed(
            Delimited(
                OneOf(
                    Ref("ColumnReferenceSegment"),
                    Ref("LiteralGrammar"),
                ),
                optional=True,
            ),
        ),
    ),
    PropertiesBackTickedIdentifierSegment=RegexParser(
        r"`.+`",
        IdentifierSegment,
        type="properties_naked_identifier",
    ),
    LocationWithCredentialGrammar=Sequence(
        "LOCATION",
        Ref("QuotedLiteralSegment"),
        Sequence(
            "WITH",
            Bracketed(
                "CREDENTIAL",
                Ref("PrincipalIdentifierSegment"),
            ),
            optional=True,
        ),
    ),
    NotebookStart=TypedParser("notebook_start", CommentSegment, type="notebook_start"),
    MagicSingleLineGrammar=TypedParser(
        "magic_single_line", CodeSegment, type="magic_single_line"
    ),
    MagicLineGrammar=TypedParser("magic_line", CodeSegment, type="magic_line"),
    MagicStartGrammar=TypedParser("magic_start", CodeSegment, type="magic_start"),
    VariableNameIdentifierSegment=OneOf(
        Ref("NakedIdentifierSegment"),
        Ref("BackQuotedIdentifierSegment"),
    ),
)

databricks_dialect.replace(
    DelimiterGrammar=OneOf(Ref("SemicolonSegment"), Ref("CommandCellSegment")),
    # https://docs.databricks.com/en/sql/language-manual/sql-ref-syntax-aux-describe-volume.html
    DescribeObjectGrammar=sparksql_dialect.get_grammar("DescribeObjectGrammar").copy(
        insert=[
            Sequence(
                "VOLUME",
                Ref("VolumeReferenceSegment"),
            ),
        ],
        at=0,
    ),
    FunctionContentsExpressionGrammar=OneOf(
        Ref("ExpressionSegment"),
        Ref("NamedArgumentSegment"),
    ),
    PropertiesNakedIdentifierSegment=RegexParser(
        r"[A-Z_][A-Z0-9_]*",
        IdentifierSegment,
        type="properties_naked_identifier",
    ),
    # https://docs.databricks.com/en/sql/language-manual/sql-ref-syntax-aux-show-schemas.html
    # Differences between this and the SparkSQL version:
    # - Support for `FROM`|`IN` at the catalog level
    # - `LIKE` keyword is optional
    ShowDatabasesSchemasGrammar=Sequence(
        # SHOW { DATABASES | SCHEMAS }
        OneOf("DATABASES", "SCHEMAS"),
        Sequence(
            OneOf("FROM", "IN"),
            Ref("DatabaseReferenceSegment"),
            optional=True,
        ),
        Sequence(
            Ref.keyword("LIKE", optional=True),
            Ref("QuotedLiteralSegment"),
            optional=True,
        ),
    ),
    # https://docs.databricks.com/en/sql/language-manual/sql-ref-syntax-aux-show-functions.html
    # Differences between this and the SparkSQL version:
    # - Support for `FROM`|`IN` at the schema level
    # - `LIKE` keyword is optional
    ShowFunctionsGrammar=Sequence(
        # SHOW FUNCTIONS
        OneOf("USER", "SYSTEM", "ALL", optional=True),
        "FUNCTIONS",
        Sequence(
            Sequence(
                OneOf("FROM", "IN"),
                Ref("DatabaseReferenceSegment"),
                optional=True,
            ),
            Sequence(
                Ref.keyword("LIKE", optional=True),
                OneOf(
                    # qualified function from a database
                    Sequence(
                        Ref("DatabaseReferenceSegment"),
                        Ref("DotSegment"),
                        Ref("FunctionNameSegment"),
                        allow_gaps=False,
                    ),
                    # non-qualified function
                    Ref("FunctionNameSegment"),
                    # Regex/like string
                    Ref("QuotedLiteralSegment"),
                ),
                optional=True,
            ),
            optional=True,
        ),
    ),
    # https://docs.databricks.com/en/sql/language-manual/sql-ref-syntax-aux-show-tables.html
    # Differences between this and the SparkSQL version:
    # - `LIKE` keyword is optional
    ShowTablesGrammar=Sequence(
        # SHOW TABLES
        "TABLES",
        Sequence(
            OneOf("FROM", "IN"),
            Ref("DatabaseReferenceSegment"),
            optional=True,
        ),
        Sequence(
            Ref.keyword("LIKE", optional=True),
            Ref("QuotedLiteralSegment"),
            optional=True,
        ),
    ),
    # https://docs.databricks.com/en/sql/language-manual/sql-ref-syntax-aux-show-views.html
    # Only difference between this and the SparkSQL version:
    # - `LIKE` keyword is optional
    ShowViewsGrammar=Sequence(
        # SHOW VIEWS
        "VIEWS",
        Sequence(
            OneOf("FROM", "IN"),
            Ref("DatabaseReferenceSegment"),
            optional=True,
        ),
        Sequence(
            Ref.keyword("LIKE", optional=True),
            Ref("QuotedLiteralSegment"),
            optional=True,
        ),
    ),
    # https://docs.databricks.com/en/sql/language-manual/sql-ref-syntax-aux-show-volumes.html
    ShowObjectGrammar=sparksql_dialect.get_grammar("ShowObjectGrammar").copy(
        insert=[
            Sequence(
                "VOLUMES",
                Sequence(
                    OneOf("FROM", "IN"),
                    Ref("DatabaseReferenceSegment"),
                    optional=True,
                ),
                Sequence(
                    Ref.keyword("LIKE", optional=True),
                    Ref("QuotedLiteralSegment"),
                    optional=True,
                ),
            )
        ],
    ),
    NotNullGrammar=Sequence(
        "NOT",
        "NULL",
    ),
    FunctionNameIdentifierSegment=OneOf(
        TypedParser("word", WordSegment, type="function_name_identifier"),
        Ref("BackQuotedIdentifierSegment"),
    ),
    PreTableFunctionKeywordsGrammar=OneOf("STREAM"),
)


class IdentifierClauseSegment(BaseSegment):
    """An `IDENTIFIER` clause segment.

    https://docs.databricks.com/en/sql/language-manual/sql-ref-names-identifier-clause.html
    """

    type = "identifier_clause_segment"
    match_grammar = Sequence(
        "IDENTIFIER",
        Bracketed(Ref("ExpressionSegment")),
    )


class ObjectReferenceSegment(ansi.ObjectReferenceSegment):
    """A reference to an object."""

    # Allow whitespace
    match_grammar: Matchable = Delimited(
        OneOf(Ref("SingleIdentifierGrammar"), Ref("IdentifierClauseSegment")),
        delimiter=Ref("ObjectReferenceDelimiterGrammar"),
        terminators=[Ref("ObjectReferenceTerminatorGrammar")],
        allow_gaps=False,
    )


class DatabaseReferenceSegment(ObjectReferenceSegment):
    """A reference to a database."""

    type = "database_reference"


class TableReferenceSegment(ObjectReferenceSegment):
    """A reference to an table, CTE, subquery or alias."""

    type = "table_reference"


class SchemaReferenceSegment(ObjectReferenceSegment):
    """A reference to a schema."""

    type = "schema_reference"


class TableExpressionSegment(sparksql.TableExpressionSegment):
    """The main table expression e.g. within a FROM clause.

    Enhance to allow for additional clauses allowed in Spark and Delta Lake.
    """

    match_grammar = sparksql.TableExpressionSegment.match_grammar.copy(
        insert=[
            Ref("IdentifierClauseSegment"),
        ],
        before=Ref("ValuesClauseSegment"),
    )


class CatalogReferenceSegment(ansi.ObjectReferenceSegment):
    """A reference to a catalog.

    https://docs.databricks.com/data-governance/unity-catalog/create-catalogs.html
    """

    type = "catalog_reference"


class VolumeReferenceSegment(ansi.ObjectReferenceSegment):
    """Volume reference."""

    type = "volume_reference"


class AlterCatalogStatementSegment(BaseSegment):
    """An `ALTER CATALOG` statement.

    https://docs.databricks.com/sql/language-manual/sql-ref-syntax-ddl-alter-catalog.html
    """

    type = "alter_catalog_statement"
    match_grammar = Sequence(
        "ALTER",
        "CATALOG",
        Ref("CatalogReferenceSegment"),
        OneOf(
            Ref("SetOwnerGrammar"),
            Ref("SetTagsGrammar"),
            Ref("UnsetTagsGrammar"),
            Ref("PredictiveOptimizationGrammar"),
        ),
    )


class CreateCatalogStatementSegment(BaseSegment):
    """A `CREATE CATALOG` statement.

    https://docs.databricks.com/sql/language-manual/sql-ref-syntax-ddl-create-catalog.html
    """

    type = "create_catalog_statement"
    match_grammar = Sequence(
        "CREATE",
        "CATALOG",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("CatalogReferenceSegment"),
        Ref("CommentGrammar", optional=True),
    )


class DropCatalogStatementSegment(BaseSegment):
    """A `DROP CATALOG` statement.

    https://docs.databricks.com/sql/language-manual/sql-ref-syntax-ddl-drop-catalog.html
    """

    type = "drop_catalog_statement"
    match_grammar = Sequence(
        "DROP",
        "CATALOG",
        Ref("IfExistsGrammar", optional=True),
        Ref("CatalogReferenceSegment"),
        Ref("DropBehaviorGrammar", optional=True),
    )


class UseCatalogStatementSegment(BaseSegment):
    """A `USE CATALOG` statement.

    https://docs.databricks.com/sql/language-manual/sql-ref-syntax-ddl-use-catalog.html
    """

    type = "use_catalog_statement"
    match_grammar = Sequence(
        "USE",
        "CATALOG",
        Ref("CatalogReferenceSegment"),
    )


class UseDatabaseStatementSegment(sparksql.UseDatabaseStatementSegment):
    """A `USE DATABASE` statement.

    https://docs.databricks.com/sql/language-manual/sql-ref-syntax-ddl-usedb.html
    """

    type = "use_database_statement"
    match_grammar = Sequence(
        "USE",
        OneOf("DATABASE", "SCHEMA", optional=True),
        Ref("DatabaseReferenceSegment"),
    )


class AlterDatabaseStatementSegment(sparksql.AlterDatabaseStatementSegment):
    """An `ALTER DATABASE/SCHEMA` statement.

    https://docs.databricks.com/en/sql/language-manual/sql-ref-syntax-ddl-alter-schema.html
    """

    match_grammar = Sequence(
        "ALTER",
        OneOf("DATABASE", "SCHEMA"),
        Ref("DatabaseReferenceSegment"),
        OneOf(
            Sequence(
                "SET",
                Ref("DatabasePropertiesGrammar"),
            ),
            Ref("SetOwnerGrammar"),
            Ref("SetTagsGrammar"),
            Ref("UnsetTagsGrammar"),
            Ref("PredictiveOptimizationGrammar"),
        ),
    )


class AlterVolumeStatementSegment(BaseSegment):
    """Alter Volume Statement.

    https://docs.databricks.com/en/sql/language-manual/sql-ref-syntax-ddl-alter-volume.html
    """

    type = "alter_volume_statement"

    match_grammar = Sequence(
        "ALTER",
        "VOLUME",
        Ref("VolumeReferenceSegment"),
        OneOf(
            Sequence(
                "RENAME",
                "TO",
                Ref("VolumeReferenceSegment"),
            ),
            Ref("SetOwnerGrammar"),
            Ref("SetTagsGrammar"),
            Ref("UnsetTagsGrammar"),
        ),
    )


class CreateVolumeStatementSegment(BaseSegment):
    """Create Volume Statement.

    https://docs.databricks.com/en/sql/language-manual/sql-ref-syntax-ddl-create-volume.html
    """

    type = "create_volume_statement"

    match_grammar = OneOf(
        # You can create a non-external volume without a location
        Sequence(
            "CREATE",
            "VOLUME",
            Ref("IfNotExistsGrammar", optional=True),
            Ref("VolumeReferenceSegment"),
            Ref("CommentGrammar", optional=True),
        ),
        # Or you can create an external volume that must have a location
        Sequence(
            "CREATE",
            "EXTERNAL",
            "VOLUME",
            Ref("IfNotExistsGrammar", optional=True),
            Ref("VolumeReferenceSegment"),
            Ref("LocationGrammar"),
            Ref("CommentGrammar", optional=True),
        ),
    )


class DropVolumeStatementSegment(BaseSegment):
    """Drop Volume Statement.

    https://docs.databricks.com/en/sql/language-manual/sql-ref-syntax-ddl-drop-volume.html
    """

    type = "drop_volume_statement"

    match_grammar = Sequence(
        "DROP",
        "VOLUME",
        Ref("IfExistsGrammar", optional=True),
        Ref("VolumeReferenceSegment"),
    )


class CreateDatabaseStatementSegment(sparksql.CreateDatabaseStatementSegment):
    """A `CREATE DATABASE` statement.

    https://docs.databricks.com/en/sql/language-manual/sql-ref-syntax-ddl-create-schema.html
    """

    match_grammar = sparksql.CreateDatabaseStatementSegment.match_grammar.copy(
        insert=[
            Sequence(
                Ref.keyword("MANAGED", optional=True),
                "LOCATION",
                Ref("QuotedLiteralSegment"),
                optional=True,
            ),
        ],
        at=5,
        remove=[
            Ref("LocationGrammar", optional=True),
        ],
    )


class CreateViewStatementSegment(sparksql.CreateViewStatementSegment):
    """A `CREATE VIEW` statement.

    https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-create-view
    https://docs.databricks.com/aws/en/dlt-ref/dlt-sql-ref-create-materialized-view
    """

    match_grammar = sparksql.CreateViewStatementSegment.match_grammar.copy(
        insert=[
            Sequence(
                Ref.keyword("PRIVATE", optional=True),
                Ref.keyword("MATERIALIZED"),
                optional=True,
            ),
        ],
        before=Ref.keyword("MATERIALIZED", optional=True),
        remove=[
            Ref.keyword("MATERIALIZED", optional=True),
        ],
    )


class MaskStatementSegment(BaseSegment):
    """A `MASK` statement.

    https://docs.databricks.com/en/sql/language-manual/sql-ref-syntax-ddl-column-mask.html
    """

    type = "mask_statement"
    match_grammar = Sequence(
        "MASK",
        Ref("FunctionNameSegment"),
        Sequence(
            "USING",
            "COLUMNS",
            Bracketed(
                AnyNumberOf(
                    OneOf(
                        Ref("ColumnReferenceSegment"),
                        Ref("ExpressionSegment"),
                    ),
                ),
            ),
            optional=True,
        ),
    )


class ColumnFieldDefinitionSegment(ansi.ColumnDefinitionSegment):
    """A column field definition, e.g. for CREATE TABLE or ALTER TABLE.

    This supports the iceberg syntax and allows for iceberg syntax such
    as ADD COLUMN a.b.
    """

    match_grammar: Matchable = Sequence(
        Ref("ColumnReferenceSegment"),  # Column name
        Ref("DatatypeSegment"),  # Column type
        Bracketed(Anything(), optional=True),  # For types like VARCHAR(100)
        AnyNumberOf(
            Ref("ColumnConstraintSegment", optional=True),
            Ref("ColumnDefaultGrammar", optional=True),  # For default values
        ),
    )


class PropertyNameSegment(sparksql.PropertyNameSegment):
    """A property name segment. Databricks allows for back quoted segments."""

    match_grammar = Sequence(
        OneOf(
            Delimited(
                OneOf(
                    Ref("PropertiesNakedIdentifierSegment"),
                    Ref("PropertiesBackTickedIdentifierSegment"),
                ),
                delimiter=Ref("DotSegment"),
                allow_gaps=False,
            ),
            Ref("SingleIdentifierGrammar"),
        ),
    )


class TableConstraintSegment(ansi.TableConstraintSegment):
    """A table constraint, e.g. for CREATE TABLE or ALTER TABLE.

    https://docs.databricks.com/en/sql/language-manual/sql-ref-syntax-ddl-create-table-constraint.html
    """

    match_grammar = Sequence(
        "CONSTRAINT",
        OneOf(
            Sequence(
                Ref("ObjectReferenceSegment", optional=True),
                Ref("PrimaryKeyGrammar"),
                Bracketed(
                    Delimited(
                        Ref("ColumnReferenceSegment"),
                        Ref.keyword("TIMESERIES", optional=True),
                    ),
                ),
                Ref("ConstraintOptionGrammar", optional=True),
            ),
            Sequence(
                Ref("ObjectReferenceSegment", optional=True),
                Indent,
                Ref("ForeignKeyGrammar"),
                Bracketed(
                    Delimited(
                        Ref("ColumnReferenceSegment"),
                    ),
                ),
                "REFERENCES",
                Ref("TableReferenceSegment"),
                Ref("BracketedColumnReferenceListGrammar", optional=True),
                OneOf(
                    Ref("ForeignKeyOptionGrammar"),
                    Ref("ConstraintOptionGrammar"),
                    optional=True,
                ),
                Dedent,
            ),
            Sequence(
                Ref("ObjectReferenceSegment"),
                "CHECK",
                Bracketed(Ref("ExpressionSegment")),
                Ref.keyword("ENFORCED", optional=True),
            ),
        ),
    )


class AlterTableStatementSegment(sparksql.AlterTableStatementSegment):
    """An `ALTER TABLE` statement.

    https://docs.databricks.com/en/sql/language-manual/sql-ref-syntax-ddl-alter-table.html
    """

    match_grammar = Sequence(
        "ALTER",
        "TABLE",
        Ref("TableReferenceSegment"),
        Indent,
        OneOf(
            Sequence(
                "RENAME",
                "TO",
                Ref("TableReferenceSegment"),
            ),
            Sequence(
                "ADD",
                OneOf("COLUMNS", "COLUMN"),
                Indent,
                Bracketed(
                    Delimited(
                        Sequence(
                            Ref("ColumnFieldDefinitionSegment"),
                            Ref("ColumnDefaultGrammar", optional=True),
                            Ref("CommentGrammar", optional=True),
                            Ref("FirstOrAfterGrammar", optional=True),
                            Ref("MaskStatementSegment", optional=True),
                        ),
                    ),
                ),
                Dedent,
            ),
            Sequence(
                OneOf("ALTER", "CHANGE"),
                Ref.keyword("COLUMN", optional=True),
                Ref("ColumnReferenceSegment"),
                OneOf(
                    Ref("CommentGrammar"),
                    Ref("FirstOrAfterGrammar"),
                    Sequence(
                        OneOf("SET", "DROP"),
                        "NOT",
                        "NULL",
                    ),
                    Sequence(
                        "TYPE",
                        Ref("DatatypeSegment"),
                    ),
                    Sequence(
                        "SET",
                        Ref("ColumnDefaultGrammar"),
                    ),
                    Sequence(
                        "DROP",
                        "DEFAULT",
                    ),
                    Sequence(
                        "SYNC",
                        "IDENTITY",
                    ),
                    Sequence(
                        "SET",
                        Ref("MaskStatementSegment"),
                    ),
                    Sequence(
                        "DROP",
                        "MASK",
                    ),
                    Ref("SetTagsGrammar"),
                    Ref("UnsetTagsGrammar"),
                ),
            ),
            Sequence(
                "DROP",
                OneOf("COLUMN", "COLUMNS", optional=True),
                Ref("IfExistsGrammar", optional=True),
                OptionallyBracketed(
                    Delimited(
                        Ref("ColumnReferenceSegment"),
                    ),
                ),
            ),
            Sequence(
                "RENAME",
                "COLUMN",
                Ref("ColumnReferenceSegment"),
                "TO",
                Ref("ColumnReferenceSegment"),
            ),
            Sequence(
                "ADD",
                Ref("TableConstraintSegment"),
            ),
            Ref("DropConstraintGrammar"),
            Sequence(
                "DROP",
                "FEATURE",
                Ref("ObjectReferenceSegment"),
                Sequence(
                    "TRUNCATE",
                    "HISTORY",
                    optional=True,
                ),
            ),
            Sequence(
                "ADD",
                Ref("IfNotExistsGrammar", optional=True),
                AnyNumberOf(Ref("AlterPartitionGrammar")),
            ),
            Sequence(
                "DROP",
                Ref("IfExistsGrammar", optional=True),
                AnyNumberOf(Ref("AlterPartitionGrammar")),
            ),
            Sequence(
                Ref("AlterPartitionGrammar"),
                "SET",
                Ref("LocationGrammar"),
            ),
            Sequence(
                Ref("AlterPartitionGrammar"),
                "RENAME",
                "TO",
                Ref("AlterPartitionGrammar"),
            ),
            Sequence(
                "RECOVER",
                "PARTITIONS",
            ),
            Sequence(
                "SET",
                Ref("RowFilterClauseGrammar"),
            ),
            Sequence(
                "DROP",
                "ROW",
                "FILTER",
            ),
            Sequence(
                "SET",
                Ref("TablePropertiesGrammar"),
            ),
            Ref("UnsetTablePropertiesGrammar"),
            Sequence(
                "SET",
                "SERDE",
                Ref("QuotedLiteralSegment"),
                Sequence(
                    "WITH",
                    "SERDEPROPERTIES",
                    Ref("BracketedPropertyListGrammar"),
                    optional=True,
                ),
            ),
            Sequence(
                "SET",
                Ref("LocationGrammar"),
            ),
            Ref("SetOwnerGrammar"),
            Sequence(
                Sequence(
                    "ALTER",
                    "COLUMN",
                    Ref("ColumnReferenceSegment"),
                    optional=True,
                ),
                Ref("SetTagsGrammar"),
            ),
            Sequence(
                Sequence(
                    "ALTER",
                    "COLUMN",
                    Ref("ColumnReferenceSegment"),
                    optional=True,
                ),
                Ref("UnsetTagsGrammar"),
            ),
            Ref("ClusterByClauseSegment"),
            Ref("PredictiveOptimizationGrammar"),
        ),
        Dedent,
    )


class AlterViewStatementSegment(sparksql.AlterViewStatementSegment):
    """An `ALTER VIEW` statement.

    https://docs.databricks.com/en/sql/language-manual/sql-ref-syntax-ddl-alter-view.html
    """

    match_grammar = Sequence(
        "ALTER",
        Ref.keyword("MATERIALIZED", optional=True),
        "VIEW",
        Ref("TableReferenceSegment"),
        OneOf(
            Sequence(
                "RENAME",
                "TO",
                Ref("TableReferenceSegment"),
            ),
            Sequence(
                "SET",
                Ref("TablePropertiesGrammar"),
            ),
            Ref("UnsetTablePropertiesGrammar"),
            Sequence(
                "AS",
                Ref("SelectStatementSegment"),
            ),
            Sequence(
                "WITH",
                "SCHEMA",
                OneOf(
                    "BINDING",
                    "COMPENSATION",
                    Sequence(
                        Ref.keyword("TYPE", optional=True),
                        "EVOLUTION",
                    ),
                ),
            ),
            Ref("SetOwnerGrammar"),
            Ref("SetTagsGrammar"),
            Ref("UnsetTagsGrammar"),
            Sequence(
                Indent,
                OneOf(
                    Sequence(
                        OneOf("ADD", "ALTER"),
                        "SCHEDULE",
                        Ref.keyword("REFRESH", optional=True),
                        "CRON",
                        Ref("QuotedLiteralSegment"),
                        Sequence(
                            "AT",
                            "TIME",
                            "ZONE",
                            Ref("QuotedLiteralSegment"),
                            optional=True,
                        ),
                    ),
                    Sequence(
                        "DROP",
                        "SCHEDULE",
                    ),
                ),
                Dedent,
            ),
        ),
    )


class SetTimeZoneStatementSegment(BaseSegment):
    """A `SET TIME ZONE` statement.

    https://docs.databricks.com/sql/language-manual/sql-ref-syntax-aux-conf-mgmt-set-timezone.html
    """

    type = "set_timezone_statement"
    match_grammar = Sequence(
        "SET",
        "TIME",
        "ZONE",
        OneOf("LOCAL", Ref("QuotedLiteralSegment"), Ref("IntervalExpressionSegment")),
    )


class OptimizeTableStatementSegment(BaseSegment):
    """An `OPTIMIZE` statement.

    https://docs.databricks.com/en/sql/language-manual/delta-optimize.html
    """

    type = "optimize_table_statement"
    match_grammar = Sequence(
        "OPTIMIZE",
        Ref("TableReferenceSegment"),
        Sequence(
            "WHERE",
            Ref("ExpressionSegment"),
            optional=True,
        ),
        Sequence(
            "ZORDER",
            "BY",
            Bracketed(Delimited(Ref("ColumnReferenceSegment"))),
            optional=True,
        ),
    )


class StatementSegment(sparksql.StatementSegment):
    """Overriding StatementSegment to allow for additional segment parsing."""

    match_grammar = sparksql.StatementSegment.match_grammar.copy(
        # Segments defined in Databricks SQL dialect
        insert=[
            # Unity Catalog
            Ref("AlterCatalogStatementSegment"),
            Ref("CreateCatalogStatementSegment"),
            Ref("DropCatalogStatementSegment"),
            Ref("UseCatalogStatementSegment"),
            Ref("AlterVolumeStatementSegment"),
            Ref("CreateVolumeStatementSegment"),
            Ref("DropVolumeStatementSegment"),
            Ref("CreateDatabaseStatementSegment"),
            Ref("SetTimeZoneStatementSegment"),
            Ref("OptimizeTableStatementSegment"),
            Ref("CreateDatabricksFunctionStatementSegment"),
            Ref("FunctionParameterListGrammarWithComments"),
            Ref("DeclareOrReplaceVariableStatementSegment"),
            Ref("CommentOnStatementSegment"),
            # Notebook grammar
            Ref("MagicCellStatementSegment"),
        ]
    )


class FunctionParameterListGrammarWithComments(BaseSegment):
    """The parameters for a function ie. `(column type COMMENT 'comment')`."""

    type = "function_parameter_list_with_comments"

    match_grammar: Matchable = Bracketed(
        Delimited(
            Sequence(
                Ref("FunctionParameterGrammar"),
                AnyNumberOf(
                    Sequence("DEFAULT", Ref("LiteralGrammar"), optional=True),
                    Ref("CommentClauseSegment", optional=True),
                ),
            ),
            optional=True,
        ),
    )


class FunctionDefinitionGrammar(ansi.FunctionDefinitionGrammar):
    """This is the body of a `CREATE FUNCTION AS` statement."""

    match_grammar = Sequence(
        AnyNumberOf(
            Sequence(
                "LANGUAGE",
                OneOf(Ref.keyword("SQL"), Ref.keyword("PYTHON")),
                optional=True,
            ),
            Sequence(
                OneOf("DETERMINISTIC", Sequence("NOT", "DETERMINISTIC")),
                optional=True,
            ),
            Ref("CommentClauseSegment", optional=True),
            Sequence(
                OneOf(Sequence("CONTAINS", "SQL"), Sequence("READS", "SQL", "DATA")),
                optional=True,
            ),
            Sequence(
                OneOf(
                    Sequence(
                        "AS",
                        OneOf(
                            Ref("DoubleQuotedUDFBody"),
                            Ref("SingleQuotedUDFBody"),
                            Ref("DollarQuotedUDFBody"),
                            Bracketed(
                                OneOf(
                                    Ref("ExpressionSegment"),
                                    Ref("SelectStatementSegment"),
                                )
                            ),
                        ),
                    ),
                    Sequence(
                        "RETURN",
                        OneOf(
                            Ref("ExpressionSegment"),
                            Ref("SelectStatementSegment"),
                            Ref("WithCompoundStatementSegment"),
                        ),
                    ),
                )
            ),
        )
    )


class CreateDatabricksFunctionStatementSegment(BaseSegment):
    """A `CREATE FUNCTION` statement.

    https://docs.databricks.com/en/sql/language-manual/sql-ref-syntax-ddl-create-sql-function.html
    """

    type = "create_sql_function_statement"

    match_grammar: Matchable = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        Ref("TemporaryGrammar", optional=True),
        "FUNCTION",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("FunctionNameSegment"),
        Ref("FunctionParameterListGrammarWithComments"),
        Sequence(
            "RETURNS",
            OneOf(
                Ref("DatatypeSegment"),
                Sequence(
                    "TABLE",
                    Sequence(
                        Bracketed(
                            Delimited(
                                Sequence(
                                    Ref("ColumnReferenceSegment"),
                                    Ref("DatatypeSegment"),
                                    Ref("CommentGrammar", optional=True),
                                ),
                            ),
                        ),
                        optional=True,
                    ),
                ),
            ),
            optional=True,
        ),
        Ref("FunctionDefinitionGrammar"),
    )


class NamedArgumentSegment(BaseSegment):
    """Named argument to a function.

    https://docs.databricks.com/en/sql/language-manual/sql-ref-function-invocation.html#named-parameter-invocation
    """

    type = "named_argument"
    match_grammar = Sequence(
        Ref("NakedIdentifierSegment"),
        Ref("RightArrowSegment"),
        Ref("ExpressionSegment"),
    )


class AliasExpressionSegment(sparksql.AliasExpressionSegment):
    """A reference to an object with an `AS` clause.

    The optional AS keyword allows both implicit and explicit aliasing.
    Note also that it's possible to specify just column aliases without aliasing the
    table as well:
    .. code-block:: sql

        SELECT * FROM VALUES (1,2) as t (a, b);
        SELECT * FROM VALUES (1,2) as (a, b);
        SELECT * FROM VALUES (1,2) as t;

    Note that in Spark SQL, identifiers are quoted using backticks (`my_table`) rather
    than double quotes ("my_table"). Quoted identifiers are allowed in aliases, but
    unlike ANSI which allows single quoted identifiers ('my_table') in aliases, this is
    not allowed in Spark and so the definition of this segment must depart from ANSI.
    """

    match_grammar = Sequence(
        Indent,
        Ref("AsAliasOperatorSegment", optional=True),
        OneOf(
            # maybe table alias and column aliases
            Sequence(
                Ref("SingleIdentifierGrammar", optional=True),
                Bracketed(Ref("SingleIdentifierListSegment")),
            ),
            # just a table alias
            Ref("SingleIdentifierGrammar"),
            exclude=OneOf(
                "LATERAL",
                Ref("JoinTypeKeywords"),
                "WINDOW",
                "PIVOT",
                "KEYS",
                "FROM",
                "FOR",
            ),
        ),
        Dedent,
    )


class GroupByClauseSegment(sparksql.GroupByClauseSegment):
    """Enhance `GROUP BY` clause like in `SELECT` for `CUBE`, `ROLLUP`, and `ALL`.

    https://docs.databricks.com/en/sql/language-manual/sql-ref-syntax-qry-select-groupby.html
    """

    match_grammar = Sequence(
        "GROUP",
        "BY",
        Indent,
        OneOf(
            "ALL",
            Delimited(
                Ref("CubeRollupClauseSegment"),
                Ref("GroupingSetsClauseSegment"),
                Ref("ColumnReferenceSegment"),
                # Can `GROUP BY 1`
                Ref("NumericLiteralSegment"),
                # Can `GROUP BY coalesce(col, 1)`
                Ref("ExpressionSegment"),
            ),
            Sequence(
                Delimited(
                    Ref("ColumnReferenceSegment"),
                    # Can `GROUP BY 1`
                    Ref("NumericLiteralSegment"),
                    # Can `GROUP BY coalesce(col, 1)`
                    Ref("ExpressionSegment"),
                ),
                OneOf(
                    Ref("WithCubeRollupClauseSegment"),
                    Ref("GroupingSetsClauseSegment"),
                ),
            ),
        ),
        Dedent,
    )


class ColumnConstraintSegment(ansi.ColumnConstraintSegment):
    """A column constraint, e.g. for CREATE TABLE or ALTER TABLE.

    https://docs.databricks.com/en/sql/language-manual/sql-ref-syntax-ddl-create-table-constraint.html
    """

    match_grammar = Sequence(
        Ref("NotNullGrammar", optional=True),
        Sequence(
            Sequence(
                "CONSTRAINT",
                Ref("ObjectReferenceSegment"),
                optional=True,
            ),
            OneOf(
                Sequence(
                    Ref("PrimaryKeyGrammar"),
                    Ref("ConstraintOptionGrammar", optional=True),
                ),
                Sequence(
                    Ref("ForeignKeyGrammar", optional=True),
                    "REFERENCES",
                    Ref("TableReferenceSegment"),
                    Ref("BracketedColumnReferenceListGrammar", optional=True),
                    OneOf(
                        Ref("ForeignKeyOptionGrammar"),
                        Ref("ConstraintOptionGrammar"),
                        optional=True,
                    ),
                ),
            ),
            optional=True,
        ),
    )


class CreateTableUsingStatementSegment(sparksql.CreateTableStatementSegment):
    """A `CREATE TABLE [USING]` statement.

    https://docs.databricks.com/en/sql/language-manual/sql-ref-syntax-ddl-create-table-using.html
    """

    type = "create_table_using_statement"

    match_grammar = Sequence(
        OneOf(
            Sequence(
                Sequence(
                    "CREATE",
                    "OR",
                    optional=True,
                ),
                "REPLACE",
                "TABLE",
            ),
            Sequence(
                "CREATE",
                Ref.keyword("EXTERNAL", optional=True),
                "TABLE",
                Ref("IfNotExistsGrammar", optional=True),
            ),
        ),
        Ref("TableReferenceSegment"),
        Ref("TableSpecificationSegment", optional=True),
        Sequence(
            "USING",
            Ref("DataSourceSegment"),
            optional=True,
        ),
        AnyNumberOf(Ref("TableClausesSegment")),
        Sequence(
            "AS",
            OneOf(
                Ref("SelectStatementSegment"),
                Ref("ValuesClauseSegment"),
            ),
            optional=True,
        ),
    )


class TableSpecificationSegment(BaseSegment):
    """A table specification, e.g. for CREATE TABLE or ALTER TABLE.

    https://docs.databricks.com/en/sql/language-manual/sql-ref-syntax-ddl-create-table-spec.html
    """

    type = "table_specification_segment"

    match_grammar = Bracketed(
        Delimited(
            Sequence(
                Ref("ColumnReferenceSegment"),
                Ref("DatatypeSegment"),
                AnyNumberOf(
                    Ref("ColumnPropertiesSegment"),
                ),
            ),
        ),
    )


class ColumnPropertiesSegment(BaseSegment):
    """Properties for a column in a table specification.

    https://docs.databricks.com/en/sql/language-manual/sql-ref-syntax-ddl-create-table-spec.html
    """

    type = "column_properties_segment"

    match_grammar = OneOf(
        Ref("NotNullGrammar"),
        Ref("GeneratedColumnDefinitionSegment"),
        Sequence(
            "DEFAULT",
            Ref("ColumnConstraintDefaultGrammar"),
        ),
        Ref("CommentGrammar"),
        Ref("ColumnConstraintSegment"),
        Ref("MaskStatementSegment"),
    )


class TableClausesSegment(BaseSegment):
    """Clauses for a table specification.

    https://docs.databricks.com/en/sql/language-manual/sql-ref-syntax-ddl-create-table-spec.html
    """

    type = "table_clauses_segment"

    match_grammar = OneOf(
        Ref("PartitionClauseSegment"),
        Ref("ClusterByClauseSegment"),
        Ref("LocationWithCredentialGrammar"),
        Ref("OptionsGrammar"),
        Ref("CommentGrammar"),
        Ref("TablePropertiesGrammar"),
        Sequence(
            "WITH",
            Ref("RowFilterClauseGrammar"),
        ),
    )


class GeneratedColumnDefinitionSegment(sparksql.GeneratedColumnDefinitionSegment):
    """A generated column definition, e.g. for CREATE TABLE or ALTER TABLE.

    https://docs.databricks.com/en/sql/language-manual/sql-ref-syntax-ddl-create-table-using.html
    """

    match_grammar: Matchable = Sequence(
        Ref("SingleIdentifierGrammar"),  # Column name
        Ref("DatatypeSegment"),  # Column type
        Bracketed(Anything(), optional=True),  # For types like DECIMAL(3, 2)
        OneOf(
            Sequence(
                "GENERATED",
                "ALWAYS",
                "AS",
                Bracketed(
                    OneOf(
                        Ref("FunctionSegment"),
                        Ref("BareFunctionSegment"),
                        Ref("ExpressionSegment"),
                    ),
                ),
            ),
            Sequence(
                "GENERATED",
                OneOf(
                    "ALWAYS",
                    Sequence("BY", "DEFAULT"),
                ),
                "AS",
                "IDENTITY",
                Bracketed(
                    Sequence(
                        Sequence(
                            "START",
                            "WITH",
                            Ref("NumericLiteralSegment"),
                            optional=True,
                        ),
                        Sequence(
                            "INCREMENT",
                            "BY",
                            Ref("NumericLiteralSegment"),
                            optional=True,
                        ),
                    ),
                    optional=True,
                ),
            ),
        ),
    )


class DeclareOrReplaceVariableStatementSegment(BaseSegment):
    """A `DECLARE [OR REPLACE] VARIABLE` statement.

    https://docs.databricks.com/en/sql/language-manual/sql-ref-syntax-ddl-declare-variable.html
    """

    type = "declare_or_replace_variable_statement"
    match_grammar = Sequence(
        Ref.keyword("DECLARE"),
        Ref("OrReplaceGrammar", optional=True),
        Ref.keyword("VARIABLE", optional=True),
        Ref("SingleIdentifierGrammar"),  # Variable name
        Ref("DatatypeSegment", optional=True),  # Variable type
        Sequence(
            OneOf("DEFAULT", Ref("EqualsSegment")),
            Ref("ExpressionSegment"),
            optional=True,
        ),
    )


class CommentOnStatementSegment(BaseSegment):
    """`COMMENT ON` statement.

    https://docs.databricks.com/en/sql/language-manual/sql-ref-syntax-ddl-comment.html
    """

    type = "comment_clause"

    match_grammar = Sequence(
        "COMMENT",
        "ON",
        OneOf(
            Sequence(
                "CATALOG",
                Ref("CatalogReferenceSegment"),
            ),
            Sequence(
                OneOf("DATABASE", "SCHEMA"),
                Ref("DatabaseReferenceSegment"),
            ),
            Sequence(
                "TABLE",
                Ref("TableReferenceSegment"),
            ),
            Sequence(
                "VOLUME",
                Ref("VolumeReferenceSegment"),
            ),
            # TODO: Split out individual items if they have references
            Sequence(
                OneOf(
                    "CONNECTION",
                    "PROVIDER",
                    "RECIPIENT",
                    "SHARE",
                ),
                Ref("ObjectReferenceSegment"),
            ),
        ),
        "IS",
        OneOf(Ref("QuotedLiteralSegment"), "NULL"),
    )


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
        Ref("FunctionNameIdentifierSegment", terminators=[Ref("BracketedSegment")]),
        allow_gaps=False,
    )


class MagicCellStatementSegment(BaseSegment):
    """Treat -- MAGIC %md/py/sh/... Cells as their own segments.

    N.B. This is a workaround, to make databricks notebooks
    with leading parsable by sqlfluff.

    https://learn.microsoft.com/en-us/azure/databricks/notebooks/notebooks-code#language-magic
    """

    type = "magic_cell_segment"
    match_grammar = Sequence(
        Ref("NotebookStart", optional=True),
        OneOf(
            Sequence(
                Ref("MagicStartGrammar", optional=True),
                AnyNumberOf(Ref("MagicLineGrammar"), optional=True),
            ),
            Ref("MagicSingleLineGrammar", optional=True),
        ),
        terminators=[Ref("CommandCellSegment", optional=True)],
        reset_terminators=True,
    )


class SetVariableStatementSegment(BaseSegment):
    """A `SET VARIABLE` statement used to set session variables.

    https://docs.databricks.com/en/sql/language-manual/sql-ref-syntax-aux-set-variable.html
    """

    type = "set_variable_statement"

    # set var v1=val, v2=val2;
    set_kv_pair = Sequence(
        Delimited(
            Ref("VariableNameIdentifierSegment"),
            Ref("EqualsSegment"),
            OneOf("DEFAULT", OptionallyBracketed(Ref("ExpressionSegment"))),
        )
    )
    # set var (v1,v2) = (values(100,200))
    set_bracketed = Sequence(
        Bracketed(
            Ref("VariableNameIdentifierSegment"),
        ),
        Ref("EqualsSegment"),
        Bracketed(
            OneOf(
                Ref("SelectStatementSegment"),
                Ref("ValuesClauseSegment"),
            )
        ),
    )

    match_grammar = Sequence(
        "SET",
        OneOf(
            "VAR",
            "VARIABLE",
        ),
        OneOf(
            set_kv_pair,
            set_bracketed,
        ),
        allow_gaps=True,
    )
