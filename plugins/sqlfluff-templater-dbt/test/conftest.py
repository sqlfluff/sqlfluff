"""pytest fixtures."""

import os
import shutil
import subprocess
from pathlib import Path

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
def dbt_project_folder():
    """Fixture for a temporary dbt project directory."""
    folder_suffix = "180" if dbt_version_tuple >= (1, 8) else ""
    tmp = Path(f"plugins/sqlfluff-templater-dbt/test/fixtures/dbt{folder_suffix}")

    subprocess.run(
        [
            "dbt",
            "deps",
            "--project-dir",
            f"{tmp}/dbt_project",
            "--profiles-dir",
            f"{tmp}/profiles_yml",
        ],
        check=True,
    )

    # Remove tests from dbt_package
    shutil.rmtree(tmp / "dbt_project/dbt_packages/dbt_utils/tests", ignore_errors=True)

    yield tmp
