"""The Trino dialect. https://trino.io/docs/current/language.html """

from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.core.parser import (
    Delimited,
    Ref,
    Sequence,
)
from sqlfluff.dialects import dialect_ansi as ansi

ansi_dialect = load_raw_dialect("ansi")
trino_dialect = ansi_dialect.copy_as("trino")

# Set the bare functions: https://trino.io/docs/current/functions/datetime.html
trino_dialect.sets("bare_functions").update(
    ["current_date", "current_time", "current_timestamp", "localtime", "localtimestamp"]
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
