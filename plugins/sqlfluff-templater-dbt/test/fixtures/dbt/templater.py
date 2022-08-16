"""Fixtures for dbt templating tests."""

import pytest
from sqlfluff.core import FluffConfig


DBT_FLUFF_CONFIG = {
    "core": {
        "templater": "dbt",
        "dialect": "postgres",
    },
    "templater": {
        "dbt": {
            "profiles_dir": (
                "plugins/sqlfluff-templater-dbt/test/fixtures/dbt/profiles_yml"
            ),
            "project_dir": (
                "plugins/sqlfluff-templater-dbt/test/fixtures/dbt/dbt_project"
            ),
        },
    },
}


@pytest.fixture()
def project_dir():
    """Returns the dbt project directory."""
    return DBT_FLUFF_CONFIG["templater"]["dbt"]["project_dir"]


@pytest.fixture()
def dbt_templater():
    """Returns an instance of the DbtTemplater."""
    return FluffConfig(overrides={"dialect": "ansi"}).get_templater("dbt")
