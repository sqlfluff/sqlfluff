"""SQLFluff discovery hook for the experimental dbt2 templater."""

from sqlfluff.core.plugin import hookimpl
from sqlfluff.core.templaters.base import RawTemplater


@hookimpl
def get_templaters() -> list[type[RawTemplater]]:
    """Load the templater without importing or starting dbt."""
    from sqlfluff_templater_dbt2.templater import Dbt2Templater

    return [Dbt2Templater]
