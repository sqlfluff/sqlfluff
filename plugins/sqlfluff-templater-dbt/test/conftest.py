"""pytest fixtures."""
import os

import pytest

from sqlfluff_templater_dbt import dbt_project_container


@pytest.fixture(autouse=True)
def dbt_project_container_reset():
    """Drops all projects before each test, to ensure tests are independent."""
    print("Dropping all projects")
    dbt_project_container.drop_all_projects()


@pytest.fixture(scope="session", autouse=True)
def dbt_flags():
    """Set dbt flags for dbt templater tests."""
    # Setting this to True disables some code in dbt-core that randomly runs
    # some test code in core/dbt/parser/models.py, ModelParser. render_update().
    # We've seen occasional runtime errors from that code:
    # TypeError: cannot pickle '_thread.RLock' object
    os.environ["DBT_USE_EXPERIMENTAL_PARSER"] = "True"
