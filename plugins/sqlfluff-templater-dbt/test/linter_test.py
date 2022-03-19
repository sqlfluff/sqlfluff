"""The Test file for the linter class."""

import os
import os.path

import pytest

from sqlfluff.core import Linter, FluffConfig
from test.fixtures.dbt.templater import DBT_FLUFF_CONFIG, project_dir  # noqa: F401


@pytest.mark.parametrize(
    "path", ["models/my_new_project/disabled_model.sql", "macros/echo.sql"]
)
def test__linter__skip_file(path, project_dir):  # noqa
    """Test that the linter skips disabled dbt models and macros."""
    conf = FluffConfig(configs=DBT_FLUFF_CONFIG)
    lntr = Linter(config=conf)
    model_file_path = os.path.join(project_dir, path)
    linted_path = lntr.lint_path(path=model_file_path)
    # Check that the file is still there
    assert len(linted_path.files) == 1
    linted_file = linted_path.files[0]
    # Normalise paths to control for OS variance
    assert os.path.normpath(linted_file.path) == os.path.normpath(model_file_path)
    assert not linted_file.templated_file
    assert not linted_file.tree


def test__linter__lint_ephemeral_3_level(project_dir):  # noqa
    """Test linter can lint a project with 3-level ephemeral dependencies."""
    # This was previously crashing inside dbt, in a function named
    # inject_ctes_into_sql(). (issue 2671).
    conf = FluffConfig(configs=DBT_FLUFF_CONFIG)
    lntr = Linter(config=conf)
    model_file_path = os.path.join(project_dir, "models/ephemeral_3_level")
    lntr.lint_path(path=model_file_path)
