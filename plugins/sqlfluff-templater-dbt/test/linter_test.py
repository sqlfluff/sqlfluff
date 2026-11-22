"""The Test file for the linter class."""

import logging
import os
import os.path
import shutil

import pytest

from sqlfluff.cli.commands import lint
from sqlfluff.core import FluffConfig, Linter
from sqlfluff.core.linter import runner
from sqlfluff.core.linter.common import DeferredRenderTask
from sqlfluff.utils.testing.cli import invoke_assert_code
from sqlfluff.utils.testing.logging import fluff_log_catcher


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
    must yield callable partials (RenderedFile already attached), NOT
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
        # Must be a callable partial, not a DeferredRenderTask.
        assert callable(task)
        assert not isinstance(task, DeferredRenderTask)

    # Also verify that the full parallel lint run completes without error.
    results = list(thd_runner.run(files, fix=False))
    assert len(results) == 2


def test__linter__nested_dbt_templater_ignored(tmp_path, project_dir, profiles_dir):
    """The dbt templater can't be selected in a nested config.

    The file is rendered with the root templater, with a warning.
    """
    nested = tmp_path / "nested"
    nested.mkdir()
    tmp_path.joinpath(".sqlfluff").write_text(
        "[sqlfluff]\ndialect = postgres\ntemplater = jinja\n", encoding="utf-8"
    )
    nested.joinpath(".sqlfluff").write_text(
        "[sqlfluff]\ntemplater = dbt\n\n[sqlfluff:templater:dbt]\n"
        f"project_dir = {os.path.abspath(project_dir)}\n"
        f"profiles_dir = {os.path.abspath(profiles_dir)}\n",
        encoding="utf-8",
    )
    nested_file = nested / "query.sql"
    nested_file.write_text("select {{ 1 }}\n", encoding="utf-8")
    lntr = Linter(config=FluffConfig.from_path(str(tmp_path)))

    with fluff_log_catcher(logging.WARNING, "sqlfluff.linter") as caplog:
        rendered = lntr.render_file(str(nested_file), lntr.config)

    assert "Attempt to set templater to dbt failed" in caplog.text
    assert rendered.templated_variants[0].templated_str == "select 1\n"


@pytest.mark.parametrize("nested_templater", ["jinja", "placeholder"])
def test__linter__root_dbt_templater_used_for_nested_config(
    nested_templater, project_dir, dbt_fluff_config
):
    """A root dbt templater renders files whose nested config sets another one.

    The nested templater is ignored, with a warning.
    """
    lntr = Linter(config=FluffConfig(configs=dbt_fluff_config))
    file_config = FluffConfig(
        configs={
            **dbt_fluff_config,
            "core": {"templater": nested_templater, "dialect": "postgres"},
        }
    )
    fname = os.path.join(project_dir, "models/depends_on_ephemeral/b.sql")
    with open(fname) as f:
        in_str = f.read()

    with fluff_log_catcher(logging.WARNING, "sqlfluff.linter") as caplog:
        rendered = lntr.render_string(in_str, fname, file_config, "utf-8")

    assert f"Attempt to set templater to {nested_templater} failed" in caplog.text
    assert not rendered.templater_violations
    # Only dbt can resolve the `ref()`.
    assert "__dbt__cte__c" in rendered.templated_variants[0].templated_str
