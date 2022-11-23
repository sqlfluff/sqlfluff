"""Test fixtures for sqlfluff-templater-dbt."""
import pytest

import sqlfluff_templater_dbt


@pytest.fixture(autouse=True)
def reset_dbt_projects():
    """For each test, drop all loaded dbt projects.

    This avoids cached projects causing an issue. Some tests make "in-place"
    changes to a project on disk, which would otherwise affect subsequent
    tests.
    """
    sqlfluff_templater_dbt.dbt_project_container.drop_all_projects()
