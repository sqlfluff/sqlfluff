"""Tests for the dbt templater."""

import glob
import json
import logging
import os
import shutil
from copy import deepcopy
from pathlib import Path
from unittest import mock

import pytest

from sqlfluff.cli.commands import lint
from sqlfluff.core import FluffConfig, Lexer, Linter
from sqlfluff.core.errors import SQLFluffSkipFile
from sqlfluff.utils.testing.cli import invoke_assert_code
from sqlfluff.utils.testing.logging import fluff_log_catcher
from sqlfluff_templater_dbt.templater import DbtTemplater
from test.fixtures.dbt.templater import (  # noqa: F401
    DBT_FLUFF_CONFIG,
    dbt_templater,
    project_dir,
)


def test__templater_dbt_missing(dbt_templater, project_dir):  # noqa: F811
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
            config=FluffConfig(configs=DBT_FLUFF_CONFIG),
        )


def test__templater_dbt_profiles_dir_expanded(dbt_templater):  # noqa: F811
    """Check that the profiles_dir is expanded."""
    dbt_templater.sqlfluff_config = FluffConfig(
        configs={
            "core": {"dialect": "ansi"},
            "templater": {
                "dbt": {
                    "profiles_dir": "~/.dbt",
                    "profile": "default",
                    "target": "dev",
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
    project_dir, dbt_templater, fname  # noqa: F811
):
    """Test that input sql file gets templated into output sql file."""
    _run_templater_and_verify_result(dbt_templater, project_dir, fname)


def test_dbt_profiles_dir_env_var_uppercase(
    project_dir, dbt_templater, tmpdir, monkeypatch  # noqa: F811
):
    """Tests specifying the dbt profile dir with env var."""
    profiles_dir = tmpdir.mkdir("SUBDIR")  # Use uppercase to test issue 2253
    monkeypatch.setenv("DBT_PROFILES_DIR", str(profiles_dir))
    shutil.copy(
        os.path.join(project_dir, "../profiles_yml/profiles.yml"), str(profiles_dir)
    )
    _run_templater_and_verify_result(dbt_templater, project_dir, "use_dbt_utils.sql")


def _run_templater_and_verify_result(dbt_templater, project_dir, fname):  # noqa: F811
    path = Path(project_dir) / "models/my_new_project" / fname
    config = FluffConfig(configs=DBT_FLUFF_CONFIG)
    templated_file, _ = dbt_templater.process(
        in_str=path.read_text(),
        fname=str(path),
        config=config,
    )
    template_output_folder_path = Path(
        "plugins/sqlfluff-templater-dbt/test/fixtures/dbt/templated_output/"
    )
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
    project_dir, dbt_templater, fnames_input, fnames_expected_sequence  # noqa: F811
):
    """Test that dbt templater sequences files based on dependencies."""
    result = dbt_templater.sequence_files(
        [str(Path(project_dir) / fn) for fn in fnames_input],
        config=FluffConfig(configs=DBT_FLUFF_CONFIG),
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
    raw_file, templated_file, result, dbt_templater, caplog  # noqa: F811
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
    project_dir, dbt_templater, fname  # noqa: F811
):
    """Demonstrate the lexer works on both dbt models and dbt tests.

    Handle any number of newlines.
    """
    path = Path(project_dir) / fname
    config = FluffConfig(configs=DBT_FLUFF_CONFIG)
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
    path, reason, dbt_templater, project_dir  # noqa: F811
):
    """A disabled dbt model should be skipped."""
    with pytest.raises(SQLFluffSkipFile, match=reason):
        dbt_templater.process(
            in_str="",
            fname=os.path.join(project_dir, path),
            config=FluffConfig(configs=DBT_FLUFF_CONFIG),
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
    project_dir, fname, caplog  # noqa: F811
):
    """Test that templated dbt models do not raise a linting error."""
    linter = Linter(config=FluffConfig(configs=DBT_FLUFF_CONFIG))
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
            print(f"   {idx}:{v.get_info_dict()}")

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
    project_dir, path, caplog  # noqa: F811
):
    """Test issues where previously "sqlfluff fix" corrupted the file."""
    test_glob = os.path.join(project_dir, os.path.dirname(path), "*FIXED.sql")
    _clean_path(test_glob)
    lntr = Linter(config=FluffConfig(configs=DBT_FLUFF_CONFIG))
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
    project_dir, dbt_templater  # noqa: F811
):
    """Test that absolute path of input path does not cause RuntimeError."""
    try:
        dbt_templater.process(
            in_str="",
            fname=os.path.abspath(
                os.path.join(project_dir, "models/my_new_project/use_var.sql")
            ),
            config=FluffConfig(configs=DBT_FLUFF_CONFIG),
        )
    except Exception as e:
        pytest.fail(f"Unexpected RuntimeError: {e}")


@pytest.mark.parametrize(
    "fname,exception_msg",
    [
        (
            "compiler_error.sql",
            "dbt compilation error on file 'models/my_new_project/compiler_error.sql'"
            ", Unexpected end of template. Jinja was looking for the following tags:"
            " 'endfor' or 'else'. The innermost block that needs to be closed is "
            "'for'.\n  line 5\n    {{ col }}",
        ),
        (
            "unknown_ref.sql",
            # https://github.com/sqlfluff/sqlfluff/issues/3849
            "Model 'model.my_new_project.unknown_ref' "
            "(models/my_new_project/unknown_ref.sql) depends on a node named "
            "'i_do_not_exist' which was not found",
        ),
        (
            "unknown_macro.sql",
            # https://github.com/sqlfluff/sqlfluff/issues/3849
            "Compilation Error in model unknown_macro "
            "(models/my_new_project/unknown_macro.sql)\n  'invalid_macro' is "
            "undefined. This can happen when calling a macro that does not exist.",
        ),
    ],
)
def test__templater_dbt_handle_exceptions(
    project_dir, dbt_templater, fname, exception_msg  # noqa: F811
):
    """Test that exceptions during compilation are returned as violation."""
    from dbt.adapters.factory import get_adapter

    src_fpath = "plugins/sqlfluff-templater-dbt/test/fixtures/dbt/error_models/" + fname
    target_fpath = os.path.abspath(
        os.path.join(project_dir, "models/my_new_project/", fname)
    )
    # We move the file that throws an error in and out of the project directory
    # as dbt throws an error if a node fails to parse while computing the DAG
    os.rename(src_fpath, target_fpath)
    try:
        _, violations = dbt_templater.process(
            in_str="",
            fname=target_fpath,
            config=FluffConfig(configs=DBT_FLUFF_CONFIG, overrides={"dialect": "ansi"}),
        )
    finally:
        os.rename(target_fpath, src_fpath)
        get_adapter(dbt_templater.dbt_config).connections.release()
    assert violations
    # NB: Replace slashes to deal with different platform paths being returned.
    assert exception_msg in violations[0].desc().replace("\\", "/")


@mock.patch("dbt.adapters.postgres.impl.PostgresAdapter.set_relations_cache")
def test__templater_dbt_handle_database_connection_failure(
    set_relations_cache, project_dir, dbt_templater  # noqa: F811
):
    """Test the result of a failed database connection."""
    from dbt.adapters.factory import get_adapter

    try:
        from dbt.exceptions import (
            FailedToConnectException as DbtFailedToConnectException,
        )
    except ImportError:
        from dbt.exceptions import (
            FailedToConnectError as DbtFailedToConnectException,
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
    dbt_fluff_config_fail = deepcopy(DBT_FLUFF_CONFIG)
    dbt_fluff_config_fail["templater"]["dbt"][
        "profiles_dir"
    ] = "plugins/sqlfluff-templater-dbt/test/fixtures/dbt/profiles_yml_fail"
    # We move the file that throws an error in and out of the project directory
    # as dbt throws an error if a node fails to parse while computing the DAG
    os.rename(src_fpath, target_fpath)
    try:
        _, violations = dbt_templater.process(
            in_str="",
            fname=target_fpath,
            config=FluffConfig(configs=DBT_FLUFF_CONFIG),
        )
    finally:
        os.rename(target_fpath, src_fpath)
        get_adapter(dbt_templater.dbt_config).connections.release()
    assert violations
    # NB: Replace slashes to deal with different platform paths being returned.
    assert (
        violations[0]
        .desc()
        .replace("\\", "/")
        .startswith("dbt tried to connect to the database")
    )


def test__project_dir_does_not_exist_error(dbt_templater):  # noqa: F811
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
    project_dir, dbt_templater, model_path, var_value  # noqa: F811
):
    """Test that variables inside .sqlfluff are passed to dbt."""
    context = {"passed_through_cli": var_value} if var_value else {}

    config_dict = deepcopy(DBT_FLUFF_CONFIG)
    config_dict["templater"]["dbt"]["context"] = context
    config = FluffConfig(config_dict)

    path = Path(project_dir) / model_path

    processed, violations = dbt_templater.process(
        in_str=path.read_text(), fname=str(path), config=config
    )

    assert violations == []
    assert str(var_value) in processed.templated_str


def test__dbt_log_supression():
    """Test that when we try and parse in JSON format we get JSON.

    This actually tests that we can successfully suppress unwanted
    logging from dbt.
    """
    oldcwd = os.getcwd()
    try:
        os.chdir("plugins/sqlfluff-templater-dbt/test/fixtures/dbt")
        result = invoke_assert_code(
            ret_code=1,
            args=[
                lint,
                [
                    "--disable-progress-bar",
                    "dbt_project/models/my_new_project/operator_errors.sql",
                    "-f",
                    "json",
                ],
            ],
        )
    finally:
        os.chdir(oldcwd)
    # Check that the full output parses as json
    parsed = json.loads(result.output)
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
