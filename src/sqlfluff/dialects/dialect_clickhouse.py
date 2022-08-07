"""The clickhouse dialect.

https://clickhouse.com/
"""

from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.core.parser import (
    Bracketed,
    Matchable,
    OneOf,
    OptionallyBracketed,
    Ref,
    Sequence,
)
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
            Ref("CTEColumnList", optional=True),
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


class FromExpressionElementSegment(ansi.FromExpressionElementSegment):
    """A table expression.

    Overridden from ANSI to allow FINAL modifier.
    https://clickhouse.com/docs/en/sql-reference/statements/select/from#final-modifier
    """

    type = "from_expression_element"
    match_grammar: Matchable = Sequence(
        Ref("PreTableFunctionKeywordsGrammar", optional=True),
        OptionallyBracketed(Ref("TableExpressionSegment")),
        Ref(
            "AliasExpressionSegment",
            exclude=OneOf(
                Ref("SamplingExpressionSegment"),
                Ref("JoinLikeClauseGrammar"),
                Ref.keyword("Final"),
            ),
            optional=True,
        ),
        Ref.keyword("FINAL", optional=True),
        # https://cloud.google.com/bigquery/docs/reference/standard-sql/arrays#flattening_arrays
        Sequence("WITH", "OFFSET", Ref("AliasExpressionSegment"), optional=True),
        Ref("SamplingExpressionSegment", optional=True),
        Ref("PostTableExpressionGrammar", optional=True),
    )
