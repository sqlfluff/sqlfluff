"""The Trino dialect. https://trino.io/docs/current/language.html """

from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.core.parser import (
    BaseSegment,
    Delimited,
    OneOf,
    Ref,
    Sequence,
    Matchable,
    TypedParser,
)
from sqlfluff.dialects import dialect_ansi as ansi

ansi_dialect = load_raw_dialect("ansi")
trino_dialect = ansi_dialect.copy_as("trino")

# Set the bare functions: https://trino.io/docs/current/functions/datetime.html
trino_dialect.sets("bare_functions").update(
    ["current_date", "current_time", "current_timestamp", "localtime", "localtimestamp"]
)

trino_dialect.replace(
    DateTimeLiteralGrammar=OneOf(
        Sequence(
            OneOf("DATE", "TIME", "TIMESTAMP"),
            TypedParser(
                "single_quote", ansi.LiteralSegment, type="date_constructor_literal"
            ),
        ),
        Ref("IntervalExpressionSegment"),
    )
)


class ValuesClauseSegment(ansi.ValuesClauseSegment):
    """A `VALUES` clause within in `WITH`, `SELECT`, `INSERT`."""

    match_grammar = Sequence(
        "VALUES",
        Delimited(
            Ref("ExpressionSegment"),
            ephemeral_name="ValuesClauseElements",
        ),
    )


class IntervalExpressionSegment(BaseSegment):
    """An interval representing a span of time.

    https://trino.io/docs/current/language/types.html#interval-year-to-month
    https://trino.io/docs/current/functions/datetime.html#date-and-time-operators
    """

    type = "interval_expression"
    match_grammar = Sequence(
        "INTERVAL",
        Ref("QuotedLiteralSegment"),
        OneOf("YEAR", "MONTH", "DAY", "HOUR", "MINUTE", "SECOND"),
    )


class FrameClauseSegment(BaseSegment):
    """A frame clause for window functions.

    https://trino.io/blog/2021/03/10/introducing-new-window-features.html
    """

    type = "frame_clause"

    _frame_extent = OneOf(
        Sequence("CURRENT", "ROW"),
        Sequence(
            OneOf(
                Ref("NumericLiteralSegment"), Ref("DateTimeLiteralGrammar"), "UNBOUNDED"
            ),
            OneOf("PRECEDING", "FOLLOWING"),
        ),
    )

    match_grammar: Matchable = Sequence(
        Ref("FrameClauseUnitGrammar"),
        OneOf(_frame_extent, Sequence("BETWEEN", _frame_extent, "AND", _frame_extent)),
    )
