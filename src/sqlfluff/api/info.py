"""Information API."""

from typing import List

from sqlfluff.core import dialect_readout, Linter
from sqlfluff.core.linter import RuleTuple
from sqlfluff.core.dialects import DialectTuple


def list_rules() -> List[RuleTuple]:
    """Return a list of available rule tuples."""
    linter = Linter()
    return linter.rule_tuples()


def list_dialects() -> List[DialectTuple]:
    """Return a list of available dialect info."""
    return list(dialect_readout())
