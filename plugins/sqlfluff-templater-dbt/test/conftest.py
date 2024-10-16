"""pytest fixtures."""

import os
import shutil
import subprocess
from importlib import metadata
from pathlib import Path

import pytest

from sqlfluff.core import FluffConfig
from sqlfluff_templater_dbt.templater import DbtTemplater


def pytest_report_header() -> list[str]:
    """Return a list of strings to be displayed in the header of the report."""
    return [
        f"dbt-core: {metadata.version('dbt-core')}",
        f"dbt-postgres: {metadata.version('dbt-postgres')}",
    ]


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
    return FluffConfig(
        overrides={"dialect": "ansi", "templater": "dbt"}
    ).get_templater()


@pytest.fixture(scope="session")
def dbt_project_folder():
    """Fixture for a temporary dbt project directory."""
    src = Path("plugins/sqlfluff-templater-dbt/test/fixtures/dbt")
    tmp = Path("plugins/sqlfluff-templater-dbt/test/temp_dbt_project")
    tmp.mkdir(exist_ok=True)
    shutil.copytree(src, tmp, dirs_exist_ok=True)
    if DbtTemplater().dbt_version_tuple >= (1, 8):
        # Configuration overrides for dbt 1.8+
        dbt180_fixtures = src.with_name("dbt180")
        shutil.copytree(dbt180_fixtures, tmp, dirs_exist_ok=True)

    subprocess.Popen(
        [
            "dbt",
            "deps",
            "--project-dir",
            f"{tmp}/dbt_project",
            "--profiles-dir",
            f"{tmp}/profiles_yml",
        ]
    ).wait(120)

    # Placeholder value for testing
    os.environ["passed_through_env"] = "_"

    yield tmp

    shutil.rmtree(tmp)
