"""The Azure Synapse Analytics dialect.

Azure Synapse Analytics is largely T-SQL compatible, but extends it with
PolyBase-style external table capabilities (CETAS) and Synapse-specific
options such as TABLE_OPTIONS.

https://learn.microsoft.com/en-us/azure/synapse-analytics/sql/
"""

from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.core.parser import (
    BaseSegment,
    Bracketed,
    Delimited,
    Matchable,
    OneOf,
    OptionallyBracketed,
    Ref,
    Sequence,
)
from sqlfluff.dialects import dialect_tsql as tsql
from sqlfluff.dialects.dialect_synapse_keywords import UNRESERVED_KEYWORDS

tsql_dialect = load_raw_dialect("tsql")
synapse_dialect = tsql_dialect.copy_as(
    "synapse",
    formatted_name="Azure Synapse Analytics",
    docstring="""The dialect for
`Azure Synapse Analytics`_.

.. _`Azure Synapse Analytics`:
    https://learn.microsoft.com/en-us/azure/synapse-analytics/sql/
""",
)

# Add Synapse-specific unreserved keywords on top of the inherited T-SQL set.
synapse_dialect.sets("unreserved_keywords").update(UNRESERVED_KEYWORDS)


# ---- Segment overrides / additions ----


class CreateExternalTableStatementSegment(tsql.CreateExternalTableStatementSegment):
    """A ``CREATE EXTERNAL TABLE`` statement for Azure Synapse Analytics.

    Extends the T-SQL definition with the Synapse-specific ``TABLE_OPTIONS``
    option.

    https://learn.microsoft.com/en-us/azure/synapse-analytics/sql/create-use-external-tables
    """

    match_grammar = Sequence(
        "CREATE",
        "EXTERNAL",
        "TABLE",
        Ref("ObjectReferenceSegment"),
        Bracketed(
            Delimited(
                Ref("ColumnDefinitionSegment"),
            ),
        ),
        "WITH",
        Bracketed(
            Delimited(
                Ref("TableLocationClause"),
                Sequence(
                    "DATA_SOURCE",
                    Ref("EqualsSegment"),
                    Ref("ObjectReferenceSegment"),
                ),
                Sequence(
                    "FILE_FORMAT",
                    Ref("EqualsSegment"),
                    Ref("ObjectReferenceSegment"),
                ),
                Sequence(
                    "REJECT_TYPE",
                    Ref("EqualsSegment"),
                    OneOf("value", "percentage"),
                ),
                Sequence(
                    "REJECT_VALUE",
                    Ref("EqualsSegment"),
                    Ref("NumericLiteralSegment"),
                ),
                Sequence(
                    "REJECT_SAMPLE_VALUE",
                    Ref("EqualsSegment"),
                    Ref("NumericLiteralSegment"),
                ),
                Sequence(
                    "REJECTED_ROW_LOCATION",
                    Ref("EqualsSegment"),
                    Ref("QuotedLiteralSegmentOptWithN"),
                ),
                # Synapse-specific: allows tolerating appendable files.
                Sequence(
                    "TABLE_OPTIONS",
                    Ref("EqualsSegment"),
                    Ref("QuotedLiteralSegmentOptWithN"),
                ),
            ),
        ),
    )


class CreateExternalTableAsSelectStatementSegment(BaseSegment):
    """A ``CREATE EXTERNAL TABLE … AS SELECT`` (CETAS) statement.

    This is specific to Azure Synapse Analytics (serverless and dedicated
    SQL pools).

    https://learn.microsoft.com/en-us/azure/synapse-analytics/sql/create-external-table-as-select
    """

    type = "create_external_table_as_select_statement"

    match_grammar: Matchable = Sequence(
        "CREATE",
        "EXTERNAL",
        "TABLE",
        Ref("TableReferenceSegment"),
        "WITH",
        Bracketed(
            Delimited(
                Ref("TableLocationClause"),
                Sequence(
                    "DATA_SOURCE",
                    Ref("EqualsSegment"),
                    Ref("ObjectReferenceSegment"),
                ),
                Sequence(
                    "FILE_FORMAT",
                    Ref("EqualsSegment"),
                    Ref("ObjectReferenceSegment"),
                ),
                Sequence(
                    "REJECT_TYPE",
                    Ref("EqualsSegment"),
                    OneOf("value", "percentage"),
                ),
                Sequence(
                    "REJECT_VALUE",
                    Ref("EqualsSegment"),
                    Ref("NumericLiteralSegment"),
                ),
                Sequence(
                    "REJECT_SAMPLE_VALUE",
                    Ref("EqualsSegment"),
                    Ref("NumericLiteralSegment"),
                ),
                Sequence(
                    "REJECTED_ROW_LOCATION",
                    Ref("EqualsSegment"),
                    Ref("QuotedLiteralSegmentOptWithN"),
                ),
            ),
        ),
        "AS",
        OptionallyBracketed(Ref("SelectableGrammar")),
    )


class StatementSegment(tsql.StatementSegment):
    """Extend T-SQL StatementSegment to include CETAS.

    All other statement types are inherited from the T-SQL dialect.
    """

    match_grammar = tsql.StatementSegment.match_grammar.copy(
        insert=[
            Ref("CreateExternalTableAsSelectStatementSegment"),
        ],
    )
