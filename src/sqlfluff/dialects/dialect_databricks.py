"""The Databricks Dialect.

Functionally, it is quite similar to SparkSQL,
however it's much less strict on keywords.
It also has some extensions.
"""

from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.core.parser import BaseSegment, OneOf, Ref, Sequence
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
        ]
    )
