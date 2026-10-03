"""The Test file for the linter class."""

import os
import os.path
import shutil
from pathlib import Path
from unittest import mock

import pytest

from sqlfluff.cli.commands import lint
from sqlfluff.core import FluffConfig, Linter
from sqlfluff.core.linter import runner
from sqlfluff.core.linter.common import DeferredRenderTask, RenderedLintTask
from sqlfluff.utils.testing.cli import invoke_assert_code


def _write_config(path: Path, contents: str) -> None:
    """Write a test configuration file."""
    path.write_text(contents, encoding="utf-8")


@pytest.mark.parametrize(
    "path", ["models/my_new_project/disabled_model.sql", "macros/echo.sql"]
)
def test__linter__skip_file(path, project_dir, dbt_fluff_config):
    """Test that the linter skips disabled dbt models and macros."""
    conf = FluffConfig(configs=dbt_fluff_config)
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


def test__linter__lint_ephemeral_3_level(project_dir, dbt_fluff_config):
    """Test linter can lint a project with 3-level ephemeral dependencies."""
    # This was previously crashing inside dbt, in a function named
    # inject_ctes_into_sql(). (issue 2671).
    conf = FluffConfig(configs=dbt_fluff_config)
    lntr = Linter(config=conf)
    model_file_path = os.path.join(project_dir, "models/ephemeral_3_level")
    lntr.lint_path(path=model_file_path)


def test__linter__config_pairs(dbt_fluff_config):
    """Test that the dbt templater returns version information in it's config."""
    conf = FluffConfig(configs=dbt_fluff_config)
    lntr = Linter(config=conf)
    # NOTE: This method is called within the config readout.
    assert lntr.templater.config_pairs() == [
        ("templater", "dbt"),
        ("dbt", lntr.templater.dbt_version),
    ]


def test_dbt_target_dir(tmpdir, dbt_project_folder, profiles_dir):
    """Test with dbt project in subdir that target/ is created in the correct place.

    https://github.com/sqlfluff/sqlfluff/issues/2895
    """
    tmp_base_dir = str(tmpdir)
    tmp_dbt_dir = os.path.join(tmp_base_dir, "dir1", "dir2", "dbt")
    tmp_project_dir = os.path.join(tmp_dbt_dir, "dbt_project")
    os.makedirs(os.path.dirname(tmp_dbt_dir))
    shutil.copytree(
        dbt_project_folder,
        tmp_dbt_dir,
    )
    os.unlink(os.path.join(tmp_dbt_dir, ".sqlfluff"))
    old_cwd = os.getcwd()
    # Invoke SQLFluff from <<tmpdir>>, linting a file in the dbt project at
    # <<tmp_project_dir>>/dir1/dir2/dbt/dbt_project. Prior to the bug fix, a
    # "target" directory would incorrectly be created in <<tmp_project_dir>>.
    # (It should be created in <<tmp_project_dir>>/dir1/dir2/dbt/dbt_project.)
    os.chdir(tmp_base_dir)
    with open(".sqlfluff", "w") as f:
        print(
            f"""[sqlfluff]
templater = dbt
dialect = postgres

[sqlfluff:templater:dbt]
project_dir = {tmp_project_dir}
profiles_dir = {old_cwd}/{profiles_dir}
""",
            file=f,
        )
    try:
        invoke_assert_code(
            ret_code=0,
            args=[
                lint,
                [
                    "dir1/dir2/dbt/dbt_project/models/my_new_project/use_dbt_utils.sql",
                ],
            ],
        )
        assert not os.path.exists("target")
        assert os.path.exists("dir1/dir2/dbt/dbt_project/target")
    finally:
        os.chdir(old_cwd)


def test__dbt_templater__templates_in_worker_false():
    """DbtTemplater.templates_in_worker must be False.

    The dbt templater holds a compiled dbt manifest in memory that is not
    safe to rebuild inside a worker process. Parallel runners check this flag
    and fall back to the main-process (fat-path) templating when it is False,
    sending only the pre-rendered RenderedFile across the IPC boundary.
    """
    from sqlfluff_templater_dbt.templater import DbtTemplater

    assert DbtTemplater.templates_in_worker is False


def test__dbt_linter__parallel_partials_path(project_dir, dbt_fluff_config):
    """Parallel linting with the dbt templater uses the main-process render path.

    Because DbtTemplater.templates_in_worker=False, ParallelRunner.iter_partials
    must yield rendered tasks (RenderedFile already attached), not
    DeferredRenderTask objects. This ensures the manifest is only compiled once
    in the main process and the worker only handles the lint step.
    """
    conf = FluffConfig(configs=dbt_fluff_config)
    lntr = Linter(config=conf)
    models_dir = os.path.join(project_dir, "models", "my_new_project")
    files = [
        os.path.join(models_dir, "operator_errors.sql"),
        os.path.join(models_dir, "single_trailing_newline.sql"),
    ]

    thd_runner = runner.MultiThreadRunner(lntr, conf, processes=2)
    partials = list(thd_runner.iter_partials(files, fix=False))

    assert len(partials) == 2
    for _fname, task in partials:
        assert isinstance(task, RenderedLintTask)
        assert not isinstance(task, DeferredRenderTask)

    # Also verify that the full parallel lint run completes without error.
    results = list(thd_runner.run(files, fix=False))
    assert len(results) == 2


@pytest.mark.parametrize("processes", [1, 2])
@mock.patch("dbt.adapters.postgres.impl.PostgresAdapter.set_relations_cache")
def test__linter__supports_nested_dbt_projects(
    set_relations_cache, tmp_path, dbt_project_folder, processes
):
    """Lint built-in and independent nested dbt templaters together."""
    root = tmp_path / "mixed_projects"
    root.mkdir()
    jinja_file = root / "jinja.sql"
    jinja_file.write_text("select 1 from {{ table_name }}\n", encoding="utf-8")
    _write_config(
        root / ".sqlfluff",
        """[sqlfluff]
dialect = postgres
templater = jinja

[sqlfluff:templater:jinja:context]
table_name = table_a
""",
    )

    profiles_dir = Path(dbt_project_folder, "profiles_yml").resolve()
    dbt_files = []
    expected_rendered = {}
    for project_index, project_name in enumerate(("project_a", "project_b"), start=1):
        project_root = root / project_name
        shutil.copytree(Path(dbt_project_folder, "dbt_project"), project_root)
        _write_config(
            project_root / ".sqlfluff",
            f"""[sqlfluff]
dialect = postgres
templater = dbt

[sqlfluff:templater:dbt]
profiles_dir = {profiles_dir}
project_dir = {project_root}

[sqlfluff:templater:dbt:context]
passed_through_cli = {project_index}
""",
        )
        dbt_file = str(project_root / "models/vars_from_cli.sql")
        dbt_files.append(dbt_file)
        expected_rendered[dbt_file] = f"-- Issue #1262\nSELECT {project_index}\n"

    config = FluffConfig.from_path(str(root))
    linter = Linter(config=config)
    result = linter.lint_paths(
        (str(jinja_file), *dbt_files),
        processes=processes,
    )

    linted_files = {
        linted_file.path: linted_file
        for linted_path in result.paths
        for linted_file in linted_path.files
    }
    assert len(linted_files) == 3
    assert not [violation for violation in result.get_violations() if violation.fatal]
    assert linted_files[str(jinja_file)].templated_file.templated_str == (
        "select 1 from table_a\n"
    )
    for dbt_file, rendered_sql in expected_rendered.items():
        assert linted_files[dbt_file].templated_file.templated_str == rendered_sql

    reversed_result = linter.lint_paths(tuple(reversed(dbt_files)), processes=processes)
    reversed_files = {
        linted_file.path: linted_file
        for linted_path in reversed_result.paths
        for linted_file in linted_path.files
    }
    assert list(reversed_files) == list(reversed(dbt_files))
    for dbt_file, rendered_sql in expected_rendered.items():
        assert reversed_files[dbt_file].templated_file.templated_str == rendered_sql
