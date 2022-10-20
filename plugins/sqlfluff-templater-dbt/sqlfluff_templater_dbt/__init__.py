"""Defines the hook endpoints for the dbt templater plugin."""

import dbt_osmosis.core.server_v2

from sqlfluff_templater_dbt.templater import DbtTemplater
from sqlfluff.core.plugin import hookimpl


@hookimpl
def get_templaters():
    """Get templaters."""

    def create_templater(**kwargs):
        return DbtTemplater(
            dbt_project_container=dbt_osmosis.core.server_v2.app.state.dbt_project_container,
            **kwargs
        )

    create_templater.name = DbtTemplater.name
    return [create_templater]
