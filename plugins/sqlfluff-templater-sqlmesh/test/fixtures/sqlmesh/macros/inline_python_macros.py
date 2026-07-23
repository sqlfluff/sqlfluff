"""A project-defined Python macro used by fixtures."""

from sqlglot import exp
from sqlmesh import macro


@macro()
def to_upper(evaluator, column):
    """Uppercase a column reference (a trivial inline Python macro)."""
    return exp.Upper(this=column)
