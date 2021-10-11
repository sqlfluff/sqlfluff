"""Defines the hook endpoints for the dbt templater plugin."""

from sqlfluff_templater_dbt.templater import DbtTemplater
from sqlfluff.core.plugin import hookimpl


@hookimpl
def get_templaters():
    """Get templaters."""
    return [DbtTemplater]
