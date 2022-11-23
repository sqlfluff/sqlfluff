"""Test fixtures for sqlfluff-templater-dbt."""
import pytest

import sqlfluff_templater_dbt
from sqlfluff_templater_dbt.osmosis import DbtProjectContainer


@pytest.fixture(autouse=True)
def reset_dbt_projects():
    """For each test, clear/reset the set of loaded dbt projects.

    This avoids cached projects causing an issue. Some tests make "in-place"
    changes to a project on disk, which would otherwise affect subsequent
    tests.
    """
    sqlfluff_templater_dbt.dbt_project_container = DbtProjectContainer()
