"""The sqlite dialect.

https://www.sqlite.org/
"""

from sqlfluff.core.parser import (
    OneOf,
    Ref,
    Sequence,
    BaseSegment,
)

from sqlfluff.core.dialects import load_raw_dialect

ansi_dialect = load_raw_dialect("ansi")

sqlite_dialect = ansi_dialect.copy_as("sqlite")

sqlite_dialect.replace(
    BooleanBinaryOperatorGrammar=OneOf(
        Ref("AndKeywordSegment"), Ref("OrKeywordSegment"), "REGEXP"
    ),
)


@sqlite_dialect.segment(replace=True)
class TableEndClauseSegment(BaseSegment):
    """Support WITHOUT ROWID at end of tables.

    https://www.sqlite.org/withoutrowid.html
    """

    type = "table_end_clause_segment"
    match_grammar = Sequence("WITHOUT", "ROWID")
