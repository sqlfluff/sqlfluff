"""Defines the hook endpoints for the SQLMesh templater plugin."""

from sqlfluff.core.plugin import hookimpl
from sqlfluff_templater_sqlmesh.templater import SQLMeshTemplater


@hookimpl
def get_templaters():
    """Get templaters."""
    return [SQLMeshTemplater]
