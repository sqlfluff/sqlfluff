"""Fixtures for dbt templating tests."""

from sqlfluff.core.templaters import DbtTemplater
import pytest


DBT_FLUFF_CONFIG = {
    "core": {
        "templater": "dbt",
        "dialect": "postgres",
    },
    "templater": {
        "dbt": {
            "profiles_dir": "test/fixtures/dbt",
            "project_dir": "test/fixtures/dbt_project",
        },
    },
}


@pytest.fixture()
def project_dir():
    """Returns the dbt project directory"""
    return DBT_FLUFF_CONFIG["templater"]["dbt"]["project_dir"]


@pytest.fixture()
def dbt_templater():
    """Returns an instance of the DbtTemplater."""
    return DbtTemplater()
