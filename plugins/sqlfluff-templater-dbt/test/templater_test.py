"""Tests for the dbt templater."""

import glob
import os
import logging
from pathlib import Path

import pytest

from sqlfluff.core import FluffConfig, Lexer, Linter
from sqlfluff.core.errors import SQLTemplaterSkipFile
from test.fixtures.dbt.templater import (  # noqa: F401
    DBT_FLUFF_CONFIG,
    dbt_templater,
    project_dir,
)


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
        configs={"templater": {"dbt": {"profiles_dir": "~/.dbt"}}}
    )
    profiles_dir = dbt_templater._get_profiles_dir()
    # Normalise paths to control for OS variance
    assert os.path.normpath(profiles_dir) == os.path.normpath(
        os.path.expanduser("~/.dbt")
    )


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
    ],
)
def test__templater_dbt_templating_result(
    project_dir, dbt_templater, fname  # noqa: F811
):
    """Test that input sql file gets templated into output sql file."""
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
    dbt_version_specific_fixture_folder = {(1, 0): "dbt_utils_0.8.0"}.get(
        DBT_VERSION_TUPLE
    )
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
    """A test to demonstrate the lexer works on both dbt models (with any # of trailing newlines) and dbt tests."""
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


def test__templater_dbt_skips_disabled_model(dbt_templater, project_dir):  # noqa: F811
    """A disabled dbt model should be skipped."""
    with pytest.raises(SQLTemplaterSkipFile, match=r"model was disabled"):
        dbt_templater.process(
            in_str="",
            fname=os.path.join(project_dir, "models/my_new_project/disabled_model.sql"),
            config=FluffConfig(configs=DBT_FLUFF_CONFIG),
        )


@pytest.mark.parametrize(
    "fname",
    [
        "use_var.sql",
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


@pytest.mark.parametrize(
    "path", ["models/my_new_project/issue_1608.sql", "snapshots/issue_1771.sql"]
)
def test__dbt_templated_models_fix_does_not_corrupt_file(
    project_dir, path  # noqa: F811
):
    """Test fix for issue 1608. Previously "sqlfluff fix" corrupted the file."""
    for fsp in glob.glob(os.path.join(project_dir, "snapshots", "*FIXED.sql")):
        os.remove(fsp)
    lntr = Linter(config=FluffConfig(configs=DBT_FLUFF_CONFIG))
    lnt = lntr.lint_path(os.path.join(project_dir, path), fix=True)
    try:
        lnt.persist_changes(fixed_file_suffix="FIXED")
        with open(os.path.join(project_dir, path + ".after")) as f:
            comp_buff = f.read()
        with open(os.path.join(project_dir, path.replace(".sql", "FIXED.sql"))) as f:
            fixed_buff = f.read()
        assert fixed_buff == comp_buff
    finally:
        for fsp in glob.glob(os.path.join(project_dir, "snapshots", "*FIXED.sql")):
            os.remove(fsp)


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


def test__project_dir_does_not_exist_error(dbt_templater, caplog):  # noqa: F811
    """Test that an error is logged if the specified dbt project directory doesn't exist."""
    dbt_templater.sqlfluff_config = FluffConfig(
        configs={"templater": {"dbt": {"project_dir": "./non_existing_directory"}}}
    )
    logger = logging.getLogger("sqlfluff")
    original_propagate_value = logger.propagate
    try:
        logger.propagate = True
        with caplog.at_level(logging.ERROR, logger="sqlfluff.templater"):
            dbt_project_dir = dbt_templater._get_project_dir()
        assert (
            f"dbt_project_dir: {dbt_project_dir} could not be accessed. Check it exists."
            in caplog.text
        )
    finally:
        logger.propagate = original_propagate_value
