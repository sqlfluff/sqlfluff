"""The sqlite dialect.

https://www.sqlite.org/
"""

from sqlfluff.core.parser import (
    OneOf,
    Ref,
)

from sqlfluff.core.dialects import load_raw_dialect

ansi_dialect = load_raw_dialect("ansi")

sqlite_dialect = ansi_dialect.copy_as("sqlite")

sqlite_dialect.replace(
    BooleanBinaryOperatorGrammar=OneOf(
        Ref("AndKeywordSegment"), Ref("OrKeywordSegment"), "REGEXP"
    ),
)
