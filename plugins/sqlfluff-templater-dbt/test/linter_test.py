"""The Test file for the linter class."""

import os
import os.path
import shutil

import pytest

from sqlfluff.core import Linter, FluffConfig
from sqlfluff.cli.commands import lint
from sqlfluff.utils.testing.cli import invoke_assert_code
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


def test_dbt_target_dir(tmpdir):
    """Test with dbt project in subdir that target/ is created in the correct place.

    https://github.com/sqlfluff/sqlfluff/issues/2895
    """
    tmp_base_dir = str(tmpdir)
    tmp_project_dir = os.path.join(tmp_base_dir, "dir1", "dir2", "dbt_project")
    os.makedirs(os.path.dirname(tmp_project_dir))
    shutil.copytree(
        "plugins/sqlfluff-templater-dbt/test/fixtures/dbt/dbt_project",
        tmp_project_dir,
    )
    old_cwd = os.getcwd()
    # Invoke SQLFluff from <<tmpdir>>, linting a file in the dbt project at
    # <<tmp_project_dir>>/dir1/dir2. Prior to the bug fix, a "target" directory
    # would incorrectly be created in <<tmp_project_dir>>. (It should be created
    # in <<tmp_project_dir>>/dir1/dir2/dbt_project.)
    os.chdir(tmp_base_dir)
    with open("pyproject.toml", "w") as f:
        print(
            """[tool.sqlfluff.core]
templater = "dbt"
dialect = "postgres"

[tool.sqlfluff.templater.dbt]
project_dir = "dir1/dir2/dbt_project"
""",
            file=f,
        )
    try:
        invoke_assert_code(
            ret_code=0,
            args=[
                lint,
                [
                    "dir1/dir2/dbt_project/models/my_new_project/use_dbt_utils.sql",
                ],
            ],
        )
        assert not os.path.exists("target")
        assert os.path.exists("dir1/dir2/dbt_project/target")
    finally:
        os.chdir(old_cwd)
