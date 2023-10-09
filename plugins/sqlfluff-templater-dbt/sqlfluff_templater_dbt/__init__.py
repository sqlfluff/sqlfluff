"""Defines the hook endpoints for the dbt templater plugin."""

from sqlfluff.core.plugin import hookimpl
from sqlfluff_templater_dbt.templater import DbtTemplater


@hookimpl
def get_templaters():
    """Get templaters."""
    return [DbtTemplater]
