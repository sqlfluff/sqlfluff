"""Tests for the dbt templater."""

import glob
import json
import logging
import os
import pickle
import shutil
import subprocess
from copy import deepcopy
from pathlib import Path
from unittest import mock

import pytest

from sqlfluff.cli.commands import lint
from sqlfluff.core import FluffConfig, Lexer, Linter
from sqlfluff.core.errors import SQLFluffSkipFile, SQLFluffUserError, SQLTemplaterError
from sqlfluff.utils.testing.cli import invoke_assert_code
from sqlfluff.utils.testing.logging import fluff_log_catcher
from sqlfluff_templater_dbt.templater import DbtTemplater


def test__templater_dbt_missing(dbt_templater, project_dir, dbt_fluff_config):
    """Check that a nice error is returned when dbt module is missing."""
    try:
        import dbt  # noqa: F401

        pytest.skip(reason="dbt is installed")
    except ModuleNotFoundError:
        pass

    with pytest.raises(ModuleNotFoundError, match=r"pip install sqlfluff\[dbt\]"):
        dbt_templater.process(
            in_str="",
            fname=os.path.join(project_dir, "models/my_new_project/test.sql"),
            config=FluffConfig(configs=dbt_fluff_config),
        )


def test__templater_dbt_profiles_dir_expanded(dbt_templater):
    """Check that the profiles_dir is expanded."""
    dbt_templater.sqlfluff_config = FluffConfig(
        configs={
            "core": {"dialect": "ansi"},
            "templater": {
                "dbt": {
                    "profiles_dir": "~/.dbt",
                    "profile": "default",
                    "target": "dev",
                    "target_path": "target",
                }
            },
        },
    )
    profiles_dir = dbt_templater._get_profiles_dir()
    # Normalise paths to control for OS variance
    assert os.path.normpath(profiles_dir) == os.path.normpath(
        os.path.expanduser("~/.dbt")
    )
    assert dbt_templater._get_profile() == "default"
    assert dbt_templater._get_target() == "dev"
    assert dbt_templater._get_target_path() == "target"


@pytest.mark.parametrize(
    "fname",
    [
        # dbt_utils
        "use_dbt_utils.sql",
        # macro calling another macro
        "macro_in_macro.sql",
        # config.get(...)
        "use_headers.sql",
        # var(...)
        "use_var.sql",
        # {# {{ 1 + 2 }} #}
        "templated_inside_comment.sql",
        # {{ dbt_utils.last_day(
        "last_day.sql",
        # Many newlines at end, tests templater newline handling
        "trailing_newlines.sql",
        # Ends with whitespace stripping, so trailing newline handling should
        # be disabled
        "ends_with_whitespace_stripping.sql",
        # Access dbt graph nodes
        "access_graph_nodes.sql",
        # Call statements
        "call_statement.sql",
    ],
)
def test__templater_dbt_templating_result(
    project_dir,
    dbt_templater,
    fname,
    dbt_fluff_config,
    dbt_project_folder,
):
    """Test that input sql file gets templated into output sql file."""
    _run_templater_and_verify_result(
        dbt_templater,
        project_dir,
        fname,
        dbt_fluff_config,
        dbt_project_folder,
    )


def test_dbt_profiles_dir_env_var_uppercase(
    project_dir,
    dbt_templater,
    tmpdir,
    monkeypatch,
    dbt_fluff_config,
    dbt_project_folder,
    profiles_dir,
):
    """Tests specifying the dbt profile dir with env var."""
    sub_profiles_dir = tmpdir.mkdir("SUBDIR")  # Use uppercase to test issue 2253
    monkeypatch.setenv("DBT_PROFILES_DIR", str(sub_profiles_dir))
    shutil.copy(os.path.join(profiles_dir, "profiles.yml"), str(sub_profiles_dir))
    _run_templater_and_verify_result(
        dbt_templater,
        project_dir,
        "use_dbt_utils.sql",
        dbt_fluff_config,
        dbt_project_folder,
    )


def _run_templater_and_verify_result(
    dbt_templater,
    project_dir,
    fname,
    dbt_fluff_config,
    dbt_project_folder,
):
    path = Path(project_dir) / "models/my_new_project" / fname
    config = FluffConfig(configs=dbt_fluff_config)
    templated_file, _ = dbt_templater.process(
        in_str=path.read_text(),
        fname=str(path),
        config=config,
    )
    template_output_folder_path = dbt_project_folder / "templated_output/"
    fixture_path = _get_fixture_path(template_output_folder_path, fname)
    assert str(templated_file) == fixture_path.read_text()
    # Check we can lex the output too.
    # https://github.com/sqlfluff/sqlfluff/issues/4013
    lexer = Lexer(config=config)
    _, lexing_violations = lexer.lex(templated_file)
    assert not lexing_violations


def _get_fixture_path(template_output_folder_path, fname):
    fixture_path: Path = template_output_folder_path / fname  # Default fixture location
    dbt_version_specific_fixture_folder = "dbt_utils_0.8.0"
    # Determine where it would exist.
    version_specific_path = (
        Path(template_output_folder_path) / dbt_version_specific_fixture_folder / fname
    )
    if version_specific_path.is_file():
        # Ok, it exists. Use this path instead.
        fixture_path = version_specific_path
    return fixture_path


@pytest.mark.parametrize(
    "fnames_input, fnames_expected_sequence",
    [
        [
            (
                Path("models") / "depends_on_ephemeral" / "a.sql",
                Path("models") / "depends_on_ephemeral" / "b.sql",
                Path("models") / "depends_on_ephemeral" / "d.sql",
            ),
            # c.sql is not present in the original list and should not appear here,
            # even though b.sql depends on it. This test ensures that "out of scope"
            # files, e.g. those ignored using ".sqlfluffignore" or in directories
            # outside what was specified, are not inadvertently processed.
            (
                Path("models") / "depends_on_ephemeral" / "a.sql",
                Path("models") / "depends_on_ephemeral" / "b.sql",
                Path("models") / "depends_on_ephemeral" / "d.sql",
            ),
        ],
        [
            (
                Path("models") / "depends_on_ephemeral" / "a.sql",
                Path("models") / "depends_on_ephemeral" / "b.sql",
                Path("models") / "depends_on_ephemeral" / "c.sql",
                Path("models") / "depends_on_ephemeral" / "d.sql",
            ),
            # c.sql should come before b.sql because b.sql depends on c.sql.
            # It also comes first overall because ephemeral models come first.
            (
                Path("models") / "depends_on_ephemeral" / "c.sql",
                Path("models") / "depends_on_ephemeral" / "a.sql",
                Path("models") / "depends_on_ephemeral" / "b.sql",
                Path("models") / "depends_on_ephemeral" / "d.sql",
            ),
        ],
    ],
)
def test__templater_dbt_sequence_files_ephemeral_dependency(
    project_dir,
    dbt_templater,
    fnames_input,
    fnames_expected_sequence,
    dbt_fluff_config,
):
    """Test that dbt templater sequences files based on dependencies."""
    result = dbt_templater.sequence_files(
        [str(Path(project_dir) / fn) for fn in fnames_input],
        config=FluffConfig(configs=dbt_fluff_config),
    )
    pd = Path(project_dir)
    expected = [str(pd / fn) for fn in fnames_expected_sequence]
    assert list(result) == expected


@pytest.mark.parametrize(
    "raw_file,templated_file,result",
    [
        (
            "select * from a",
            """
with dbt__CTE__INTERNAL_test as (
select * from a
)select count(*) from dbt__CTE__INTERNAL_test
""",
            # The unwrapper should trim the ends.
            [
                ("literal", slice(0, 15, None), slice(0, 15, None)),
            ],
        )
    ],
)
def test__templater_dbt_slice_file_wrapped_test(
    raw_file,
    templated_file,
    result,
    dbt_templater,
    caplog,
):
    """Test that wrapped queries are sliced safely using _check_for_wrapped()."""

    def _render_func(in_str) -> str:
        """Create a dummy render func.

        Importantly one that does actually allow different content to be added.
        """
        # Find the raw location in the template for the test case.
        loc = templated_file.find(raw_file)
        # Replace the new content at the previous position.
        # NOTE: Doing this allows the tracer logic to do what it needs to do.
        return templated_file[:loc] + in_str + templated_file[loc + len(raw_file) :]

    with caplog.at_level(logging.DEBUG, logger="sqlfluff.templater"):
        _, resp, _ = dbt_templater.slice_file(
            raw_file,
            render_func=_render_func,
        )
    assert resp == result


@pytest.mark.parametrize(
    "fname",
    [
        "tests/test.sql",
        "models/my_new_project/single_trailing_newline.sql",
        "models/my_new_project/multiple_trailing_newline.sql",
    ],
)
def test__templater_dbt_templating_test_lex(
    project_dir,
    dbt_templater,
    fname,
    dbt_fluff_config,
):
    """Demonstrate the lexer works on both dbt models and dbt tests.

    Handle any number of newlines.
    """
    path = Path(project_dir) / fname
    config = FluffConfig(configs=dbt_fluff_config)
    source_dbt_sql = path.read_text()
    # Count the newlines.
    n_trailing_newlines = len(source_dbt_sql) - len(source_dbt_sql.rstrip("\n"))
    print(
        f"Loaded {path!r} (n_newlines: {n_trailing_newlines}): " f"{source_dbt_sql!r}",
    )

    templated_file, _ = dbt_templater.process(
        in_str=source_dbt_sql,
        fname=str(path),
        config=config,
    )

    lexer = Lexer(config=config)
    # Test that it successfully lexes.
    _, _ = lexer.lex(templated_file)

    assert (
        templated_file.source_str
        == "select a\nfrom table_a" + "\n" * n_trailing_newlines
    )
    assert (
        templated_file.templated_str
        == "select a\nfrom table_a" + "\n" * n_trailing_newlines
    )


@pytest.mark.parametrize(
    "path,reason",
    [
        (
            "models/my_new_project/disabled_model.sql",
            "it is disabled",
        ),
        (
            "macros/echo.sql",
            "it is a macro",
        ),
    ],
)
def test__templater_dbt_skips_file(
    path,
    reason,
    dbt_templater,
    project_dir,
    dbt_fluff_config,
):
    """A disabled dbt model should be skipped."""
    with pytest.raises(SQLFluffSkipFile, match=reason):
        dbt_templater.process(
            in_str="",
            fname=os.path.join(project_dir, path),
            config=FluffConfig(configs=dbt_fluff_config),
        )


def test_dbt_fails_stdin(dbt_templater, dbt_fluff_config):
    """Reading from stdin is not supported with dbt templater."""
    with pytest.raises(SQLFluffUserError):
        dbt_templater.process(
            in_str="",
            fname="stdin",
            config=FluffConfig(configs=dbt_fluff_config),
        )


@pytest.mark.parametrize(
    "fname",
    [
        "use_var.sql",
        "incremental.sql",
        "single_trailing_newline.sql",
        "ST06_test.sql",
    ],
)
def test__dbt_templated_models_do_not_raise_lint_error(
    project_dir,
    fname,
    caplog,
    dbt_fluff_config,
):
    """Test that templated dbt models do not raise a linting error."""
    linter = Linter(config=FluffConfig(configs=dbt_fluff_config))
    # Log rules output.
    with caplog.at_level(logging.DEBUG, logger="sqlfluff.rules"):
        lnt = linter.lint_path(
            path=os.path.join(project_dir, "models/my_new_project/", fname)
        )
    for linted_file in lnt.files:
        # Log the rendered file to facilitate better debugging of the files.
        print(f"## FILE: {linted_file.path}")
        print("\n\n## RENDERED FILE:\n\n")
        print(linted_file.templated_file.templated_str)
        print("\n\n## PARSED TREE:\n\n")
        print(linted_file.tree.stringify())
        print("\n\n## VIOLATIONS:")
        for idx, v in enumerate(linted_file.violations):
            print(f"   {idx}:{v.to_dict()}")

    violations = lnt.check_tuples()
    assert len(violations) == 0


def _clean_path(glob_expression):
    """Clear out files matching the provided glob expression."""
    for fsp in glob.glob(glob_expression):
        os.remove(fsp)


@pytest.mark.parametrize(
    "path", ["models/my_new_project/issue_1608.sql", "snapshots/issue_1771.sql"]
)
def test__dbt_templated_models_fix_does_not_corrupt_file(
    project_dir,
    path,
    caplog,
    dbt_fluff_config,
):
    """Test issues where previously "sqlfluff fix" corrupted the file."""
    test_glob = os.path.join(project_dir, os.path.dirname(path), "*FIXED.sql")
    _clean_path(test_glob)
    lntr = Linter(config=FluffConfig(configs=dbt_fluff_config))
    with caplog.at_level(logging.INFO, logger="sqlfluff.linter"):
        lnt = lntr.lint_path(os.path.join(project_dir, path), fix=True)
    try:
        lnt.persist_changes(fixed_file_suffix="FIXED")
        with open(os.path.join(project_dir, path + ".after")) as f:
            comp_buff = f.read()
        with open(os.path.join(project_dir, path.replace(".sql", "FIXED.sql"))) as f:
            fixed_buff = f.read()
        assert fixed_buff == comp_buff
    finally:
        _clean_path(test_glob)


def test__templater_dbt_templating_absolute_path(
    project_dir,
    dbt_templater,
    dbt_fluff_config,
):
    """Test that absolute path of input path does not cause RuntimeError."""
    try:
        dbt_templater.process(
            in_str="",
            fname=os.path.abspath(
                os.path.join(project_dir, "models/my_new_project/use_var.sql")
            ),
            config=FluffConfig(configs=dbt_fluff_config),
        )
    except Exception as e:
        pytest.fail(f"Unexpected RuntimeError: {e}")


@pytest.mark.parametrize(
    "fname,exception_msg,exception_class",
    [
        (
            "compiler_error.sql",
            "Compilation Error in model compiler_error "
            "(models/my_new_project/compiler_error.sql)\n  "
            "Unexpected end of template. Jinja was looking for the following tags: "
            "'endfor' or 'else'.",
            SQLFluffUserError,
        ),
        (
            "unknown_ref.sql",
            # https://github.com/sqlfluff/sqlfluff/issues/3849
            "Model 'model.my_new_project.unknown_ref' "
            "(models/my_new_project/unknown_ref.sql) depends on a node named "
            "'i_do_not_exist' which was not found",
            SQLFluffUserError,
        ),
        (
            "unknown_macro.sql",
            # https://github.com/sqlfluff/sqlfluff/issues/3849
            "Compilation Error in model unknown_macro "
            "(models/my_new_project/unknown_macro.sql)\n  'invalid_macro' is "
            "undefined. This can happen when calling a macro that does not exist.",
            SQLTemplaterError,
        ),
        (
            "compile_missing_table.sql",
            # In the test suite we don't get a very helpful error message from dbt
            # but in live testing, the inclusion of the triggering error sometimes
            # gives us something much more useful.
            "because dbt raised a fatal exception during compilation",
            SQLFluffSkipFile,
        ),
    ],
)
def test__templater_dbt_handle_exceptions(
    project_dir,
    dbt_templater,
    dbt_fluff_config,
    dbt_project_folder,
    fname,
    exception_msg,
    exception_class,
):
    """Test that exceptions during compilation are returned as violation."""
    from dbt.adapters.factory import get_adapter

    src_fpath = dbt_project_folder / "error_models" / fname
    target_fpath = os.path.abspath(
        os.path.join(project_dir, "models/my_new_project/", fname)
    )
    # We move the file that throws an error in and out of the project directory
    # as dbt throws an error if a node fails to parse while computing the DAG
    shutil.move(src_fpath, target_fpath)
    try:
        with pytest.raises(exception_class) as excinfo:
            dbt_templater.process(
                in_str="",
                fname=target_fpath,
                config=FluffConfig(
                    configs=dbt_fluff_config, overrides={"dialect": "ansi"}
                ),
            )
    finally:
        shutil.move(target_fpath, src_fpath)
        get_adapter(dbt_templater.dbt_config).connections.release()

    # Debug logging.
    print("Raised:", excinfo.value)
    for trace in excinfo.traceback:
        print(trace)

    # NB: Replace slashes to deal with different platform paths being returned.
    if exception_class is SQLTemplaterError:
        _msg = excinfo.value.desc().replace("\\", "/")
    else:
        _msg = str(excinfo.value).replace("\\", "/")
    assert exception_msg in _msg
    # Ensure that there's no context parent exception, because they don't pickle well.
    # https://github.com/sqlfluff/sqlfluff/issues/6037
    # We *should* be stripping any inherited exceptions from anything returned here.
    # Any residual dbt exceptions are a risk for pickling errors.
    assert not excinfo.value.__context__
    assert not excinfo.value.__cause__
    # We also ensure that the exception can be pickled and unpickled safely.
    # Pickling of exceptions happens during parallel operation and so if it can't
    # be done safely then that will cause bugs.
    pickled_exception = pickle.dumps(excinfo.value)
    roundtrip_exception = pickle.loads(pickled_exception)
    assert isinstance(roundtrip_exception, type(excinfo.value))
    assert str(roundtrip_exception) == str(excinfo.value)


@mock.patch("dbt.adapters.postgres.impl.PostgresAdapter.set_relations_cache")
def test__templater_dbt_handle_database_connection_failure(
    set_relations_cache,
    project_dir,
    dbt_templater,
    dbt_fluff_config,
):
    """Test the result of a failed database connection."""
    from dbt.adapters.factory import get_adapter

    try:
        from dbt.adapters.exceptions import (
            FailedToConnectError as DbtFailedToConnectException,
        )
    except ImportError:
        try:
            from dbt.exceptions import (
                FailedToConnectError as DbtFailedToConnectException,
            )
        except ImportError:
            from dbt.exceptions import (
                FailedToConnectException as DbtFailedToConnectException,
            )

    # Clear the adapter cache to force this test to create a new connection.
    DbtTemplater.adapters.clear()

    set_relations_cache.side_effect = DbtFailedToConnectException("dummy error")

    src_fpath = (
        "plugins/sqlfluff-templater-dbt/test/fixtures/dbt/error_models"
        "/exception_connect_database.sql"
    )
    target_fpath = os.path.abspath(
        os.path.join(
            project_dir, "models/my_new_project/exception_connect_database.sql"
        )
    )
    dbt_fluff_config_fail = deepcopy(dbt_fluff_config)
    dbt_fluff_config_fail["templater"]["dbt"][
        "profiles_dir"
    ] = "plugins/sqlfluff-templater-dbt/test/fixtures/dbt/profiles_yml_fail"
    # We move the file that throws an error in and out of the project directory
    # as dbt throws an error if a node fails to parse while computing the DAG
    shutil.move(src_fpath, target_fpath)
    try:
        with pytest.raises(SQLTemplaterError) as excinfo:
            dbt_templater.process(
                in_str="",
                fname=target_fpath,
                config=FluffConfig(configs=dbt_fluff_config),
            )
    finally:
        shutil.move(target_fpath, src_fpath)
        get_adapter(dbt_templater.dbt_config).connections.release()
    # NB: Replace slashes to deal with different platform paths being returned.
    error_message = excinfo.value.desc().replace("\\", "/")
    assert "dbt tried to connect to the database" in error_message


def test__project_dir_does_not_exist_error(dbt_templater):
    """Test an error is logged if the given dbt project directory doesn't exist."""
    dbt_templater.sqlfluff_config = FluffConfig(
        configs={
            "core": {"dialect": "ansi"},
            "templater": {"dbt": {"project_dir": "./non_existing_directory"}},
        }
    )
    with fluff_log_catcher(logging.ERROR, "sqlfluff.templater") as caplog:
        dbt_project_dir = dbt_templater._get_project_dir()
    assert (
        f"dbt_project_dir: {dbt_project_dir} could not be accessed. " "Check it exists."
    ) in caplog.text


@pytest.mark.parametrize(
    ("model_path", "var_value"),
    [
        ("models/vars_from_cli.sql", "expected_value"),
        ("models/vars_from_cli.sql", [1]),
        ("models/vars_from_cli.sql", {"nested": 1}),
    ],
)
def test__context_in_config_is_loaded(
    project_dir,
    dbt_templater,
    model_path,
    var_value,
    dbt_fluff_config,
):
    """Test that variables inside .sqlfluff are passed to dbt."""
    context = {"passed_through_cli": var_value} if var_value else {}

    config_dict = deepcopy(dbt_fluff_config)
    config_dict["templater"]["dbt"]["context"] = context
    config = FluffConfig(config_dict)

    path = Path(project_dir) / model_path

    processed, violations = dbt_templater.process(
        in_str=path.read_text(), fname=str(path), config=config
    )

    assert violations == []
    assert str(var_value) in processed.templated_str


@pytest.mark.parametrize(
    ("model_path", "var_value"),
    [
        ("models/vars_from_env.sql", "expected_value"),
    ],
)
def test__context_in_env_is_loaded(
    project_dir,
    dbt_templater,
    model_path,
    var_value,
    dbt_fluff_config,
):
    """Test that variables inside env are passed to dbt."""
    os.environ["passed_through_env"] = var_value

    config = FluffConfig(dbt_fluff_config)
    path = Path(project_dir) / model_path

    processed, violations = dbt_templater.process(
        in_str=path.read_text(), fname=str(path), config=config
    )

    assert violations == []
    assert str(var_value) in processed.templated_str


def test__dbt_log_supression(dbt_project_folder):
    """Test that when we try and parse in JSON format we get JSON.

    This actually tests that we can successfully suppress unwanted
    logging from dbt.
    """
    oldcwd = os.getcwd()
    try:
        os.chdir(dbt_project_folder)

        cli_options = [
            "--disable-progress-bar",
            "dbt_project/models/my_new_project/operator_errors.sql",
            "-f",
            "json",
        ]

        result = invoke_assert_code(
            ret_code=1,
            args=[
                lint,
                cli_options,
            ],
        )
        # the CliRunner isn't isolated from the dbt plugin loading
        isolated_lint = subprocess.run(
            ["sqlfluff", "lint"] + cli_options, capture_output=True
        )
    finally:
        os.chdir(oldcwd)
    # Check that the full output parses as json
    parsed = json.loads(result.output)
    assert isolated_lint.returncode == 1
    assert b" Registered adapter:" not in isolated_lint.stdout
    assert isinstance(parsed, list)
    assert len(parsed) == 1
    first_file = parsed[0]
    assert isinstance(first_file, dict)
    # NOTE: Path translation for linux/windows.
    assert (
        first_file["filepath"].replace("\\", "/")
        == "dbt_project/models/my_new_project/operator_errors.sql"
    )
    assert len(first_file["violations"]) == 2
