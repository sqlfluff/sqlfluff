"""The Amazon Redshift dialect.

This is based on postgres dialect, since it was initially based off of Postgres 8.
We should monitor in future and see if it should be rebased off of ANSI
"""

from sqlfluff.core.parser import OneOf, BaseSegment, Nothing

from sqlfluff.core.dialects import load_raw_dialect

from sqlfluff.dialects.dialect_redshift_keywords import (
    redshift_reserved_keywords,
    redshift_unreserved_keywords,
)


postgres_dialect = load_raw_dialect("postgres")
ansi_dialect = load_raw_dialect("ansi")

redshift_dialect = postgres_dialect.copy_as("redshift")

# Set Keywords
redshift_dialect.sets("unreserved_keywords").clear()
redshift_dialect.sets("unreserved_keywords").update(
    [n.strip().upper() for n in redshift_unreserved_keywords.split("\n")]
)

redshift_dialect.sets("reserved_keywords").clear()
redshift_dialect.sets("reserved_keywords").update(
    [n.strip().upper() for n in redshift_reserved_keywords.split("\n")]
)

redshift_dialect.sets("bare_functions").clear()
redshift_dialect.sets("bare_functions").update(
    ["current_date", "sysdate"]
)

redshift_dialect.replace(WellKnownTextGeometrySegment=Nothing())


@redshift_dialect.segment(replace=True)
class DatePartFunctionNameSegment(BaseSegment):
    """DATEADD function name segment.

    Override to support DATEDIFF as well
    """

    type = "function_name"
    match_grammar = OneOf("DATEADD", "DATEDIFF")


@redshift_dialect.segment(replace=True)
class FunctionSegment(BaseSegment):
    """A scalar or aggregate function.

    Revert back to the ANSI definition to support ignore nulls
    """

    type = "function"
    match_grammar = ansi_dialect.get_segment("FunctionSegment").match_grammar.copy()
