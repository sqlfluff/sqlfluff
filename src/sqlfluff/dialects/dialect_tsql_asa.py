"""The MSSQL T-SQL PDW/Azure SQL DW/Azure Synapse Analytics dialect.

https://docs.microsoft.com/en-us/sql/t-sql/language-elements/language-elements-transact-sql
https://docs.microsoft.com/en-us/sql/analytics-platform-system/tsql-statements?view=aps-pdw-2016-au7
"""

from sqlfluff.core.parser import (
    BaseSegment,
    Sequence,
    OneOf,
    Bracketed,
    Ref,
    Anything,
    Nothing,
    RegexLexer,
    CodeSegment,
    RegexParser,
    Delimited,
    Matchable,
    NamedParser,
    StartsWith,
    OptionallyBracketed,
)

from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.dialects.tsql_asa_keywords import RESERVED_KEYWORDS
from sqlfluff.dialects.tsql_asa_keywords import UNRESERVED_KEYWORDS


ansi_dialect = load_raw_dialect("ansi")
tsql_dialect = load_raw_dialect("tsql")
tsql_asa_dialect = tsql_dialect.copy_as("tsql_asa")

tsql_asa_dialect.sets("unreserved_keywords").update(UNRESERVED_KEYWORDS)


@tsql_asa_dialect.segment(replace=True)
class CreateTableStatementSegment(BaseSegment):
    """A `CREATE TABLE` statement."""

    type = "create_table_statement"
    # https://crate.io/docs/sql-99/en/latest/chapters/18.html
    # https://docs.microsoft.com/en-us/sql/t-sql/statements/create-table-azure-sql-data-warehouse?view=aps-pdw-2016-au7
    match_grammar = Sequence(
        "CREATE",
        "TABLE",
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
            ),
            # Create AS syntax:
            Sequence(
                "AS",
                OptionallyBracketed(Ref("SelectableGrammar")),
            ),
            # Create like syntax
            Sequence("LIKE", Ref("TableReferenceSegment")),
        ),
        Ref("TableDistributionIndexClause", optional=True)
    )

    parse_grammar = match_grammar


@tsql_asa_dialect.segment()
class TableDistributionIndexClause(BaseSegment):
    """`CREATE TABLE` distribution / index clause."""

    type = "table_distribution_index_clause"

    match_grammar=Sequence(
        "WITH",
        Bracketed(
            OneOf(
                Sequence(Ref("TableDistributionClause"),Ref("CommaSegment"),Ref("TableIndexClause")),
                Sequence(Ref("TableIndexClause"),Ref("CommaSegment"),Ref("TableDistributionClause")),
                Ref("TableDistributionClause"),
                Ref("TableIndexClause"),
            )
        ),
    )


@tsql_asa_dialect.segment()
class TableDistributionClause(BaseSegment):
    """`CREATE TABLE` distribution clause."""

    type = "table_distribution_clause"

    match_grammar=Sequence(
        "DISTRIBUTION",
        Ref("EqualsSegment"),
        OneOf(
            "REPLICATE",
            "ROUND_ROBIN",
            Sequence(
                "HASH",
                Bracketed(Ref("ColumnReferenceSegment")),
            )
        )
    )

@tsql_asa_dialect.segment()
class TableIndexClause(BaseSegment):
    """`CREATE TABLE` table index clause."""

    type = "table_index_clause"

    match_grammar=Sequence(
        OneOf(
            "HEAP",
            Sequence(
                "CLUSTERED",
                "COLUMNSTORE",
                "INDEX"
            )
        )
    )


@tsql_asa_dialect.segment(replace=True)
class StatementSegment(ansi_dialect.get_segment("StatementSegment")):  # type: ignore
    """Overriding StatementSegment to allow for additional segment parsing."""

    parse_grammar = tsql_dialect.get_segment("StatementSegment").parse_grammar.copy(
        insert=[
            Ref("AlterTableSwitchStatementSegment"),
            Ref("CreateTableAsSelectStatementSegment"),
        ],
    )


@tsql_asa_dialect.segment()
class AlterTableSwitchStatementSegment(BaseSegment):
    """An `ALTER TABLE SWITCH` statement."""

    type = "alter_table_switch_statement"
    # https://docs.microsoft.com/en-us/sql/t-sql/statements/alter-table-transact-sql?view=sql-server-ver15
    # T-SQL's ALTER TABLE SWITCH grammar is different enough to core ALTER TABLE grammar to merit its own definition
    match_grammar = Sequence(
        "ALTER",
        "TABLE",
        Ref("ObjectReferenceSegment"),
        "SWITCH",
        Sequence("PARTITION", Ref("NumericLiteralSegment"), optional=True),
        "TO",
        Ref("ObjectReferenceSegment"),
        Sequence(
            "WITH",
            Bracketed("TRUNCATE_TARGET", Ref("EqualsSegment"), OneOf("ON","OFF")), 
            optional=True
        ),
    )


@tsql_asa_dialect.segment()
class CreateTableAsSelectStatementSegment(BaseSegment):
    """A `CREATE TABLE AS SELECT` statement."""

    type = "create_table_as_select_statement"
    # https://docs.microsoft.com/en-us/sql/t-sql/statements/create-table-as-select-azure-sql-data-warehouse?toc=/azure/synapse-analytics/sql-data-warehouse/toc.json&bc=/azure/synapse-analytics/sql-data-warehouse/breadcrumb/toc.json&view=azure-sqldw-latest&preserve-view=true
    match_grammar = Sequence(
        "CREATE",
        "TABLE",
        Ref("TableReferenceSegment"),
        Ref("TableDistributionIndexClause"),
        "AS",
        Ref("SelectableGrammar"),
    )

