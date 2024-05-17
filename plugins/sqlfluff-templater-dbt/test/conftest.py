"""pytest fixtures."""

import os
import shutil

import pytest

from sqlfluff.core import FluffConfig
from sqlfluff_templater_dbt.templater import DbtTemplater

dbt_version_tuple = DbtTemplater().dbt_version_tuple


@pytest.fixture(scope="session", autouse=True)
def dbt_flags():
    """Set dbt flags for dbt templater tests."""
    # Setting this to True disables some code in dbt-core that randomly runs
    # some test code in core/dbt/parser/models.py, ModelParser. render_update().
    # We've seen occasional runtime errors from that code:
    # TypeError: cannot pickle '_thread.RLock' object
    os.environ["DBT_USE_EXPERIMENTAL_PARSER"] = "True"


@pytest.fixture()
def dbt_fluff_config(dbt_project_folder):
    """Returns SQLFluff dbt configuration dictionary."""
    return {
        "core": {
            "templater": "dbt",
            "dialect": "postgres",
        },
        "templater": {
            "dbt": {
                "profiles_dir": f"{dbt_project_folder}/profiles_yml",
                "project_dir": f"{dbt_project_folder}/dbt_project",
            },
        },
    }


@pytest.fixture()
def project_dir(dbt_fluff_config):
    """Returns the dbt project directory."""
    return dbt_fluff_config["templater"]["dbt"]["project_dir"]


@pytest.fixture()
def profiles_dir(dbt_fluff_config):
    """Returns the dbt project directory."""
    return dbt_fluff_config["templater"]["dbt"]["profiles_dir"]


@pytest.fixture()
def dbt_templater():
    """Returns an instance of the DbtTemplater."""
    return FluffConfig(overrides={"dialect": "ansi"}).get_templater("dbt")


@pytest.fixture(scope="session")
def dbt_project_folder(tmp_path_factory):
    """Fixture for a temporary dbt project directory."""
    tmp = tmp_path_factory.mktemp("dbt")
    shutil.copytree(
        "plugins/sqlfluff-templater-dbt/test/fixtures/dbt",
        tmp,
        dirs_exist_ok=True,
    )
    if dbt_version_tuple >= (1, 8):
        shutil.copytree(
            "plugins/sqlfluff-templater-dbt/test/fixtures/dbt180",
            tmp,
            dirs_exist_ok=True,
        )

    yield tmp

    shutil.rmtree(tmp)
