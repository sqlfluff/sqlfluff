"""The clickhouse dialect.

https://clickhouse.com/
"""

from sqlfluff.core.parser import (
    Bracketed,
    Matchable,
    OneOf,
    Ref,
    Sequence,
)

from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.dialects import dialect_ansi as ansi

ansi_dialect = load_raw_dialect("ansi")

clickhouse_dialect = ansi_dialect.copy_as("clickhouse")


class CTEDefinitionSegment(ansi.CTEDefinitionSegment):
    """A CTE Definition from a WITH statement.

    Overridden from ANSI to allow expression CTEs.
    https://clickhouse.com/docs/en/sql-reference/statements/select/with/
    """

    type = "common_table_expression"
    match_grammar: Matchable = OneOf(
        Sequence(
            Ref("SingleIdentifierGrammar"),
            Bracketed(
                Ref("SingleIdentifierListSegment"),
                optional=True,
            ),
            "AS",
            Bracketed(
                # Ephemeral here to subdivide the query.
                Ref("SelectableGrammar", ephemeral_name="SelectableGrammar")
            ),
        ),
        Sequence(
            Ref("ExpressionSegment"),
            "AS",
            Ref("SingleIdentifierGrammar"),
        ),
    )
