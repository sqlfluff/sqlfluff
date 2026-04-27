"""Defines the hook endpoints for the SQLMesh templater plugin."""

from sqlfluff.core.plugin import hookimpl
from sqlfluff.core.rules import BaseRule
from sqlfluff_templater_sqlmesh.templater import SQLMeshTemplater


@hookimpl
def get_templaters():
    """Get templaters."""
    return [SQLMeshTemplater]


@hookimpl
def get_rules() -> list[type[BaseRule]]:
    """Get SQLMesh-specific linting rules."""
    from sqlfluff_templater_sqlmesh.rules import Rule_SM01, Rule_SM02, Rule_SM03

    return [Rule_SM01, Rule_SM02, Rule_SM03]
