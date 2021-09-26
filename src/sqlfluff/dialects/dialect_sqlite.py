"""The sqlite dialect.

https://www.sqlite.org/
"""

from sqlfluff.core.parser import (
    OneOf,
    Ref,
)

from sqlfluff.core.dialects import load_raw_dialect

postgres_dialect = load_raw_dialect("postgres")

sqlite_dialect = postgres_dialect.copy_as("sqlite")

# Add the REGEXP keyword
sqlite_dialect.sets("unreserved_keywords").add("REGEXP")

sqlite_dialect.replace(
    BooleanBinaryOperatorGrammar=OneOf(
        Ref("AndKeywordSegment"), Ref("OrKeywordSegment"), "REGEXP"
    ),
)
