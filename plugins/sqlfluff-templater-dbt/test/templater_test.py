"""Tests for the dbt templater."""

from copy import deepcopy
import glob
import os
import logging
import shutil
from pathlib import Path
from unittest import mock

import pytest

from sqlfluff.core import FluffConfig, Lexer, Linter
from sqlfluff.core.errors import SQLFluffSkipFile
from sqlfluff_templater_dbt.templater import DBT_VERSION_TUPLE
from test.fixtures.dbt.templater import (  # noqa: F401
    DBT_FLUFF_CONFIG,
    dbt_templater,
    project_dir,
)
from sqlfluff_templater_dbt.templater import DbtFailedToConnectException


def test__templater_dbt_missing(dbt_templater, project_dir):  # noqa: F811
    """Check that a nice error is returned when dbt module is missing."""
    try:
        import dbt  # noqa: F401

        pytest.skip(msg="dbt is installed")
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
    templated_file, _ = dbt_templater.process(
        in_str="",
        fname=os.path.join(project_dir, "models/my_new_project/", fname),
        config=FluffConfig(configs=DBT_FLUFF_CONFIG),
    )
    template_output_folder_path = Path(
        "plugins/sqlfluff-templater-dbt/test/fixtures/dbt/templated_output/"
    )
    fixture_path = _get_fixture_path(template_output_folder_path, fname)
    assert str(templated_file) == fixture_path.read_text()


def _get_fixture_path(template_output_folder_path, fname):
    fixture_path: Path = template_output_folder_path / fname  # Default fixture location
    # Is there a version-specific version of the fixture file?
    if DBT_VERSION_TUPLE >= (1, 0):
        dbt_version_specific_fixture_folder = "dbt_utils_0.8.0"
    else:
        dbt_version_specific_fixture_folder = None

    if dbt_version_specific_fixture_folder:
        # Maybe. Determine where it would exist.
        version_specific_path = (
            Path(template_output_folder_path)
            / dbt_version_specific_fixture_folder
            / fname
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
    with caplog.at_level(logging.DEBUG, logger="sqlfluff.templater"):
        _, resp, _ = dbt_templater.slice_file(
            raw_file,
            templated_file,
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
    source_fpath = os.path.join(project_dir, fname)
    with open(source_fpath, "r") as source_dbt_model:
        source_dbt_sql = source_dbt_model.read()
    n_trailing_newlines = len(source_dbt_sql) - len(source_dbt_sql.rstrip("\n"))
    lexer = Lexer(config=FluffConfig(configs=DBT_FLUFF_CONFIG))
    templated_file, _ = dbt_templater.process(
        in_str="",
        fname=os.path.join(project_dir, fname),
        config=FluffConfig(configs=DBT_FLUFF_CONFIG),
    )
    tokens, lex_vs = lexer.lex(templated_file)
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
        "L034_test.sql",
    ],
)
def test__dbt_templated_models_do_not_raise_lint_error(
    project_dir, fname  # noqa: F811
):
    """Test that templated dbt models do not raise a linting error."""
    lntr = Linter(config=FluffConfig(configs=DBT_FLUFF_CONFIG))
    lnt = lntr.lint_path(
        path=os.path.join(project_dir, "models/my_new_project/", fname)
    )
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
            "dbt compilation error on file 'models/my_new_project/compiler_error.sql', "
            "Unexpected end of template. "
            "Jinja was looking for the following tags: 'endfor'",
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
        get_adapter(dbt_templater.dbt_config).connections.release()
        os.rename(target_fpath, src_fpath)
    assert violations
    # NB: Replace slashes to deal with different plaform paths being returned.
    assert violations[0].desc().replace("\\", "/").startswith(exception_msg)


@pytest.mark.skipif(
    DBT_VERSION_TUPLE < (1, 0), reason="mocks a function that's only used in dbt >= 1.0"
)
@mock.patch("dbt.adapters.postgres.impl.PostgresAdapter.set_relations_cache")
def test__templater_dbt_handle_database_connection_failure(
    set_relations_cache, project_dir, dbt_templater  # noqa: F811
):
    """Test the result of a failed database connection."""
    from dbt.adapters.factory import get_adapter

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
    dbt_fluff_config_fail = DBT_FLUFF_CONFIG.copy()
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
        get_adapter(dbt_templater.dbt_config).connections.release()
        os.rename(target_fpath, src_fpath)
    assert violations
    # NB: Replace slashes to deal with different plaform paths being returned.
    assert (
        violations[0]
        .desc()
        .replace("\\", "/")
        .startswith("dbt tried to connect to the database")
    )


def test__project_dir_does_not_exist_error(dbt_templater, caplog):  # noqa: F811
    """Test an error is logged if the given dbt project directory doesn't exist."""
    dbt_templater.sqlfluff_config = FluffConfig(
        configs={
            "core": {"dialect": "ansi"},
            "templater": {"dbt": {"project_dir": "./non_existing_directory"}},
        }
    )
    logger = logging.getLogger("sqlfluff")
    original_propagate_value = logger.propagate
    try:
        logger.propagate = True
        with caplog.at_level(logging.ERROR, logger="sqlfluff.templater"):
            dbt_project_dir = dbt_templater._get_project_dir()
        assert (
            f"dbt_project_dir: {dbt_project_dir} could not be accessed. "
            "Check it exists."
        ) in caplog.text
    finally:
        logger.propagate = original_propagate_value


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

    fname = os.path.abspath(os.path.join(project_dir, model_path))

    processed, violations = dbt_templater.process(in_str="", fname=fname, config=config)

    assert violations == []
    assert str(var_value) in processed.templated_str
