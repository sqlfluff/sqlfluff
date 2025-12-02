"""Information API."""

from sqlfluff.core import Linter, dialect_readout
from sqlfluff.core.dialects import DialectTuple
from sqlfluff.core.linter import RuleTuple


def list_rules() -> list[RuleTuple]:
    """Return a list of available rule tuples."""
    linter = Linter()
    return linter.rule_tuples()


def list_dialects() -> list[DialectTuple]:
    """Return a list of available dialect info."""
    return list(dialect_readout())
