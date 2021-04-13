"""The TSQL dialect.

https://docs.microsoft.com/en-us/sql/t-sql/language-elements/language-elements-transact-sql

"""

from sqlfluff.core.parser import (
    AnyNumberOf,
    BaseSegment,
    Bracketed,
    OptionallyBracketed,
    Dedent,
    Delimited,
    GreedyUntil,
    Indent,
    KeywordSegment,
    NamedSegment,
    Nothing,
    OneOf,
    Ref,
    ReSegment,
    Sequence,
    StartsWith,
)
from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.dialects.tsql_keywords import (
    # BARE_FUNCTIONS,
    RESERVED_KEYWORDS,
    # UNRESERVED_KEYWORDS,
)

ansi_dialect = load_raw_dialect("ansi")
tsql_dialect = ansi_dialect.copy_as("tsql")

# Update only RESERVED Keywords
tsql_dialect.sets("reserved_keywords").clear()
tsql_dialect.sets("reserved_keywords").update(RESERVED_KEYWORDS)
