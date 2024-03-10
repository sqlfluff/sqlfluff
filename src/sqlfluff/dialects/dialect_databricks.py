"""The Databricks Dialect.

Functionally, it is quite similar to SparkSQL,
however it's much less strict on keywords.
It also has some extensions.
"""

from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.core.parser import (
    AnyNumberOf,
    BaseSegment,
    Bracketed,
    CodeSegment,
    Delimited,
    Matchable,
    OneOf,
    Ref,
    Sequence,
    TypedParser,
)
from sqlfluff.dialects import dialect_ansi as ansi
from sqlfluff.dialects import dialect_sparksql as sparksql
from sqlfluff.dialects.dialect_databricks_keywords import (
    RESERVED_KEYWORDS,
    UNRESERVED_KEYWORDS,
)

sparksql_dialect = load_raw_dialect("sparksql")
databricks_dialect = sparksql_dialect.copy_as("databricks")

databricks_dialect.sets("unreserved_keywords").update(UNRESERVED_KEYWORDS)
databricks_dialect.sets("unreserved_keywords").update(
    sparksql_dialect.sets("reserved_keywords")
)
databricks_dialect.sets("unreserved_keywords").difference_update(RESERVED_KEYWORDS)
databricks_dialect.sets("reserved_keywords").clear()
databricks_dialect.sets("reserved_keywords").update(RESERVED_KEYWORDS)


databricks_dialect.add(
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
)


# Object References
class CatalogReferenceSegment(ansi.ObjectReferenceSegment):
    """A reference to a catalog.

    https://docs.databricks.com/data-governance/unity-catalog/create-catalogs.html
    """

    type = "catalog_reference"


# Data Definition Statements
# https://docs.databricks.com/sql/language-manual/index.html#ddl-statements
class AlterCatalogStatementSegment(BaseSegment):
    """An `ALTER CATALOG` statement.

    https://docs.databricks.com/sql/language-manual/sql-ref-syntax-ddl-alter-catalog.html
    """

    type = "alter_catalog_statement"
    match_grammar = Sequence(
        "ALTER",
        "CATALOG",
        Ref("CatalogReferenceSegment"),
        Ref.keyword("SET", optional=True),
        Sequence(
            "OWNER",
            "TO",
            Ref("SingleIdentifierGrammar"),
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
            Ref("SetTimeZoneStatementSegment"),
            Ref("OptimizeTableStatementSegment"),
            Ref("CreateDatabricksFunctionStatementSegment"),
            Ref("FunctionParameterListGrammarWithComments"),
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
            Ref("DatatypeSegment"),
            optional=True,
        ),
        Ref("FunctionDefinitionGrammar"),
    )
