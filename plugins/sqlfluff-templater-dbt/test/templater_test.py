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
from types import SimpleNamespace
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


def test__templater_dbt_profiles_dir_from_dbt_engine_env_var(
    dbt_templater, tmp_path, monkeypatch
):
    """Check that the profiles_dir can be set by DBT_ENGINE_PROFILES_DIR."""
    profiles_dir = tmp_path / "engine_profiles"
    profiles_dir.mkdir()
    monkeypatch.setenv("DBT_ENGINE_PROFILES_DIR", str(profiles_dir))
    dbt_templater.sqlfluff_config = FluffConfig(
        configs={
            "core": {"dialect": "ansi"},
            "templater": {"dbt": {"profiles_dir": None}},
        },
    )

    assert dbt_templater._get_profiles_dir() == os.path.abspath(profiles_dir)


def test__templater_dbt_profiles_dir_dbt_engine_env_var_precedence(
    dbt_templater, tmp_path, monkeypatch
):
    """Check DBT_ENGINE_PROFILES_DIR takes precedence over DBT_PROFILES_DIR."""
    engine_profiles_dir = tmp_path / "engine_profiles"
    legacy_profiles_dir = tmp_path / "legacy_profiles"
    engine_profiles_dir.mkdir()
    legacy_profiles_dir.mkdir()
    monkeypatch.setenv("DBT_ENGINE_PROFILES_DIR", str(engine_profiles_dir))
    monkeypatch.setenv("DBT_PROFILES_DIR", str(legacy_profiles_dir))
    dbt_templater.sqlfluff_config = FluffConfig(
        configs={
            "core": {"dialect": "ansi"},
            "templater": {"dbt": {"profiles_dir": None}},
        },
    )

    assert dbt_templater._get_profiles_dir() == os.path.abspath(engine_profiles_dir)


def test__templater_dbt_profiles_dir_config_precedence(
    dbt_templater, tmp_path, monkeypatch
):
    """Check SQLFluff profiles_dir config takes precedence over dbt env vars."""
    config_profiles_dir = tmp_path / "config_profiles"
    engine_profiles_dir = tmp_path / "engine_profiles"
    legacy_profiles_dir = tmp_path / "legacy_profiles"
    config_profiles_dir.mkdir()
    engine_profiles_dir.mkdir()
    legacy_profiles_dir.mkdir()
    monkeypatch.setenv("DBT_ENGINE_PROFILES_DIR", str(engine_profiles_dir))
    monkeypatch.setenv("DBT_PROFILES_DIR", str(legacy_profiles_dir))
    dbt_templater.sqlfluff_config = FluffConfig(
        configs={
            "core": {"dialect": "ansi"},
            "templater": {"dbt": {"profiles_dir": str(config_profiles_dir)}},
        },
    )

    assert dbt_templater._get_profiles_dir() == os.path.abspath(config_profiles_dir)


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
        f"Loaded {path!r} (n_newlines: {n_trailing_newlines}): {source_dbt_sql!r}",
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


def test__find_node_with_symlinked_local_package(tmp_path):
    """Test that _find_node resolves symlinks for dbt local packages.

    When a dbt local package is used (via 'local:' in packages.yml), dbt deps
    creates a symlink in dbt_packages/ pointing to the local package directory.
    The manifest records the symlink path (dbt_packages/...) as original_file_path.
    _find_node must resolve symlinks to match input paths against manifest entries.
    """
    # Create a real file structure with a symlink mimicking dbt local packages:
    #   dbt_dir/
    #     packages/my_pkg/models/my_model.sql  <- real file
    #     dbt_packages/my_pkg -> ../packages/my_pkg  <- symlink created by dbt deps
    real_dir = tmp_path / "packages" / "my_pkg" / "models"
    real_dir.mkdir(parents=True)
    (real_dir / "my_model.sql").write_text("select 1 as id")

    pkg_dir = tmp_path / "dbt_packages"
    pkg_dir.mkdir()
    (pkg_dir / "my_pkg").symlink_to(tmp_path / "packages" / "my_pkg")

    # The manifest records the symlink path as original_file_path
    symlink_rel_path = "dbt_packages/my_pkg/models/my_model.sql"
    real_rel_path = "packages/my_pkg/models/my_model.sql"

    # Build a mock node whose original_file_path is the symlink path
    mock_node = mock.MagicMock()
    mock_node.original_file_path = symlink_rel_path

    # Build a mock manifest with this node
    mock_manifest = mock.MagicMock()
    mock_manifest.nodes = {"model.my_pkg.my_model": mock_node}
    mock_manifest.macros = {}
    mock_manifest.disabled = {}

    # The dbt path selector returns nothing (simulating the path mismatch)
    mock_selector = mock.MagicMock()
    mock_selector.search.return_value = []

    dbt_templater = FluffConfig(
        overrides={"dialect": "ansi", "templater": "dbt"}
    ).get_templater()
    dbt_templater.project_dir = str(tmp_path)
    config = FluffConfig(overrides={"dialect": "ansi", "templater": "dbt"})

    with (
        mock.patch.object(
            type(dbt_templater),
            "dbt_manifest",
            new_callable=lambda: property(lambda self: mock_manifest),
        ),
        mock.patch.object(
            type(dbt_templater),
            "dbt_selector_method",
            new_callable=lambda: property(lambda self: mock_selector),
        ),
    ):
        # Input via real path (packages/my_pkg/...) should find the node
        node = dbt_templater._find_node(
            fname=str(tmp_path / real_rel_path),
            config=config,
            dbt_dir=str(tmp_path),
        )
        assert node is mock_node

        # Input via symlink path (dbt_packages/my_pkg/...) should also find the node
        node = dbt_templater._find_node(
            fname=str(tmp_path / symlink_rel_path),
            config=config,
            dbt_dir=str(tmp_path),
        )
        assert node is mock_node


@pytest.mark.parametrize(
    "fname",
    [
        # NOTE: `use_var.sql` is deliberately not in this list. It selects a
        # wildcard from a literal table, so it carries a genuine AM04
        # violation which has nothing to do with its templated WHERE clause.
        # It is covered by the test below instead.
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


def test__dbt_lint_error_outside_templated_section_is_reported(
    project_dir,
    dbt_fluff_config,
):
    """Violations outside a model's templated sections are still reported.

    `use_var.sql` selects a wildcard from a literal table, so AM04 applies to
    it; only its WHERE clause is templated. AM04 used to anchor the violation
    on the whole `select_statement`, which spans the `var()` call, so the
    violation was found and then discarded as templated - any dbt model
    selecting a wildcard was silently exempt from the rule.
    https://github.com/sqlfluff/sqlfluff/issues/6032
    """
    linter = Linter(config=FluffConfig(configs=dbt_fluff_config))
    lnt = linter.lint_path(
        path=os.path.join(project_dir, "models/my_new_project/use_var.sql")
    )
    # Line 2, position 8 is the wildcard, which is literal - not the start of
    # the select statement, which is not.
    assert lnt.check_tuples() == [("AM04", 2, 8)]


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
    ("fname", "exception_msg", "dbt_skip_compilation_error", "exception_class"),
    [
        (
            "compiler_error.sql",
            "Compilation Error in model compiler_error "
            "(models/my_new_project/compiler_error.sql)\n  "
            "Unexpected end of template. Jinja was looking for the following tags: "
            "'endfor' or 'else'.",
            True,
            SQLFluffUserError,
        ),
        (
            "unknown_ref.sql",
            # https://github.com/sqlfluff/sqlfluff/issues/3849
            "Model 'model.my_new_project.unknown_ref' "
            "(models/my_new_project/unknown_ref.sql) depends on a node named "
            "'i_do_not_exist' which was not found",
            True,
            SQLFluffUserError,
        ),
        (
            "unknown_macro.sql",
            # https://github.com/sqlfluff/sqlfluff/issues/3849
            "Compilation Error in model unknown_macro "
            "(models/my_new_project/unknown_macro.sql)\n  'invalid_macro' is "
            "undefined. This can happen when calling a macro that does not exist.",
            True,
            SQLTemplaterError,
        ),
        (
            "compile_missing_table.sql",
            # In the test suite we don't get a very helpful error message from dbt
            # but in live testing, the inclusion of the triggering error sometimes
            # gives us something much more useful.
            "because dbt raised a fatal exception during compilation",
            True,
            SQLFluffSkipFile,
        ),
        pytest.param(
            "compile_missing_table.sql",
            "Runtime Error",
            False,
            SQLTemplaterError,
            id="dbt_skip_compilation_error",
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
    dbt_skip_compilation_error,
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
    dbt_fluff_config["templater"]["dbt"]["dbt_skip_compilation_error"] = (
        dbt_skip_compilation_error
    )
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
    dbt_fluff_config_fail["templater"]["dbt"]["profiles_dir"] = (
        "plugins/sqlfluff-templater-dbt/test/fixtures/dbt/profiles_yml_fail"
    )
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


def test__project_dir_from_env(dbt_templater, project_dir, monkeypatch):
    """Test possibility to set project_dir from env variable."""
    dbt_templater.sqlfluff_config = FluffConfig(
        configs={
            "core": {"dialect": "ansi"},
            "templater": {"dbt": {"project_dir": None}},
        }
    )
    assert dbt_templater._get_project_dir() == os.path.abspath(os.getcwd())
    monkeypatch.setenv("DBT_PROJECT_DIR", project_dir)
    assert dbt_templater._get_project_dir() == os.path.abspath(project_dir)
    monkeypatch.setenv("DBT_ENGINE_PROJECT_DIR", os.getcwd())
    assert dbt_templater._get_project_dir() == os.path.abspath(os.getcwd())


def test__profile_from_env(dbt_templater, monkeypatch):
    """Test possibility to set profile from dbt profile env variables."""
    dbt_templater.sqlfluff_config = FluffConfig(
        configs={
            "core": {"dialect": "ansi"},
            "templater": {"dbt": {"profile": None}},
        }
    )
    assert dbt_templater._get_profile() is None
    monkeypatch.setenv("DBT_PROFILE", "legacy_profile")
    assert dbt_templater._get_profile() == "legacy_profile"
    monkeypatch.setenv("DBT_ENGINE_PROFILE", "engine_profile")
    assert dbt_templater._get_profile() == "engine_profile"


def test__profile_config_precedence(dbt_templater, monkeypatch):
    """Test SQLFluff profile config takes precedence over dbt profile env vars."""
    monkeypatch.setenv("DBT_ENGINE_PROFILE", "engine_profile")
    monkeypatch.setenv("DBT_PROFILE", "legacy_profile")
    dbt_templater.sqlfluff_config = FluffConfig(
        configs={
            "core": {"dialect": "ansi"},
            "templater": {"dbt": {"profile": "config_profile"}},
        }
    )

    assert dbt_templater._get_profile() == "config_profile"


def test__target_from_env(dbt_templater, monkeypatch):
    """Test possibility to set target from dbt target env variables."""
    dbt_templater.sqlfluff_config = FluffConfig(
        configs={
            "core": {"dialect": "ansi"},
            "templater": {"dbt": {"target": None}},
        }
    )
    assert dbt_templater._get_target() is None
    monkeypatch.setenv("DBT_TARGET", "dev")
    assert dbt_templater._get_target() == "dev"
    monkeypatch.setenv("DBT_ENGINE_TARGET", "prod")
    assert dbt_templater._get_target() == "prod"


def test__target_path_from_env(dbt_templater, monkeypatch):
    """Test possibility to set target_path from dbt target path env variables."""
    dbt_templater.sqlfluff_config = FluffConfig(
        configs={
            "core": {"dialect": "ansi"},
            "templater": {"dbt": {"target_path": None}},
        }
    )
    assert dbt_templater._get_target_path() is None
    monkeypatch.setenv("DBT_TARGET_PATH", "custom_target")
    assert dbt_templater._get_target_path() == "custom_target"
    monkeypatch.setenv("DBT_ENGINE_TARGET_PATH", "engine_target")
    assert dbt_templater._get_target_path() == "engine_target"


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
        f"dbt_project_dir: {dbt_project_dir} could not be accessed. Check it exists."
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


def test__templater_dbt_threads_default(dbt_templater):
    """When threads is not configured, _get_threads() returns None.

    This lets dbt use the value from profiles.yml rather than
    overriding it.
    """
    dbt_templater.sqlfluff_config = FluffConfig(
        configs={
            "core": {"dialect": "ansi"},
            "templater": {
                "dbt": {
                    "profiles_dir": "~/.dbt",
                }
            },
        },
    )
    assert dbt_templater._get_threads() is None


def test__templater_dbt_threads_explicit(dbt_templater):
    """When threads is set in the config, _get_threads() returns it as int."""
    dbt_templater.sqlfluff_config = FluffConfig(
        configs={
            "core": {"dialect": "ansi"},
            "templater": {
                "dbt": {
                    "profiles_dir": "~/.dbt",
                    "threads": "4",
                }
            },
        },
    )
    assert dbt_templater._get_threads() == 4


def _clear_populate_cache_env(monkeypatch):
    """Clear dbt cache environment variables for test isolation."""
    monkeypatch.delenv("DBT_ENGINE_POPULATE_CACHE", raising=False)
    monkeypatch.delenv("DBT_POPULATE_CACHE", raising=False)


def _make_dbt_cache_config(ctx=None, **dbt_overrides):
    """Build a FluffConfig for dbt populate_relations_cache tests."""
    dbt_section = (
        {"project_dir": ctx["project_dir"], "profiles_dir": ctx["profiles_dir"]}
        if ctx is not None
        else {}
    )
    dbt_section.update(dbt_overrides)
    return FluffConfig(
        configs={
            "core": {"dialect": "ansi", "templater": "dbt"},
            "templater": {"dbt": dbt_section},
        }
    )


def _make_mock_dbt_process_context(tmp_path, project_name="project"):
    """Create minimal fake dbt objects for unit testing process() -> connection()."""
    project_dir = tmp_path / project_name
    profiles_dir = tmp_path / f"{project_name}_profiles"
    (project_dir / "models").mkdir(parents=True)
    profiles_dir.mkdir(parents=True)
    model_sql = "select 1"
    model_file = project_dir / "models" / "my_model.sql"
    model_file.write_text(model_sql)

    node = SimpleNamespace(
        original_file_path="models/my_model.sql",
        compiled_code=model_sql,
        raw_code=model_sql,
        config=SimpleNamespace(materialized="view"),
        compiled=False,
    )
    manifest = mock.MagicMock()
    manifest.nodes = {"model.test.my_model": node}
    manifest.expect.return_value = node

    selector = mock.MagicMock()
    selector.search.return_value = ["model.test.my_model"]

    compiler = mock.MagicMock()
    compiler.compile_node.return_value = node

    dbt_config = SimpleNamespace(credentials=SimpleNamespace(type=project_name))
    return {
        "project_dir": str(project_dir),
        "profiles_dir": str(profiles_dir),
        "model_file": str(model_file),
        "model_sql": model_sql,
        "manifest": manifest,
        "selector": selector,
        "compiler": compiler,
        "adapter": mock.MagicMock(),
        "dbt_config": dbt_config,
    }


def _attach_mock_dbt_context(templater, ctx):
    """Attach mocked dbt runtime objects while preserving installed dbt version."""
    templater.dbt_config = ctx["dbt_config"]
    templater.dbt_manifest = ctx["manifest"]
    templater.dbt_selector_method = ctx["selector"]
    templater.dbt_compiler = ctx["compiler"]


def _patch_adapter_lookup(monkeypatch, lookup):
    """Patch FACTORY.lookup_adapter without replacing get_adapter module bindings."""
    from dbt.adapters.factory import FACTORY

    monkeypatch.setattr(FACTORY, "lookup_adapter", lookup)


@pytest.mark.parametrize(
    ("env_value", "expected_cache_calls"),
    [(None, 1), ("false", 0)],
    ids=["default_unset", "dbt_populate_cache_false"],
)
def test__templater_dbt_populate_relations_cache_process_regression(
    tmp_path, monkeypatch, env_value, expected_cache_calls
):
    """process() -> connection() warms cache by default and skips on opt-out."""
    _clear_populate_cache_env(monkeypatch)
    if env_value is not None:
        monkeypatch.setenv("DBT_POPULATE_CACHE", env_value)
    monkeypatch.setattr(DbtTemplater, "adapters", {})

    ctx = _make_mock_dbt_process_context(tmp_path)
    config = _make_dbt_cache_config(ctx)
    templater = config.get_templater()
    _attach_mock_dbt_context(templater, ctx)
    _patch_adapter_lookup(monkeypatch, lambda _type: ctx["adapter"])

    templated_file, violations = templater.process(
        fname=ctx["model_file"], in_str=ctx["model_sql"], config=config
    )

    assert violations == []
    assert templated_file.templated_str == ctx["model_sql"]
    assert ctx["adapter"].acquire_connection.call_args_list == [mock.call("master")]
    assert ctx["adapter"].set_relations_cache.call_count == expected_cache_calls
    if templater.dbt_version_tuple >= (1, 8):
        assert ctx["adapter"].set_macro_resolver.call_args_list == [
            mock.call(ctx["manifest"])
        ]
        assert ctx["adapter"].set_macro_context_generator.call_count == 1
    else:
        assert ctx["adapter"].set_macro_resolver.call_count == 0
        assert ctx["adapter"].set_macro_context_generator.call_count == 0


@pytest.mark.parametrize(
    ("config_value", "engine_env", "legacy_env", "expected"),
    [
        (None, None, None, True),
        (False, "true", "true", False),
        (True, "false", "false", True),
        ("false", "true", "true", False),
        ("true", "false", "false", True),
        ("0", "1", "1", False),
        ("1", "0", "0", True),
        (None, "false", "true", False),
        (None, "true", "false", True),
        (None, None, "false", False),
        (None, None, "true", True),
        (None, "", "false", False),
        (None, "", "true", True),
        (None, "", "", True),
        (None, None, "", True),
    ],
)
def test__templater_dbt_populate_relations_cache_precedence(
    dbt_templater, monkeypatch, config_value, engine_env, legacy_env, expected
):
    """Verify config > DBT_ENGINE_POPULATE_CACHE > DBT_POPULATE_CACHE > True."""
    _clear_populate_cache_env(monkeypatch)
    if engine_env is not None:
        monkeypatch.setenv("DBT_ENGINE_POPULATE_CACHE", engine_env)
    if legacy_env is not None:
        monkeypatch.setenv("DBT_POPULATE_CACHE", legacy_env)
    dbt_templater.sqlfluff_config = _make_dbt_cache_config(
        populate_relations_cache=config_value
    )
    assert dbt_templater._get_populate_relations_cache() is expected


def test__templater_dbt_populate_relations_cache_no_config_object(
    dbt_templater, monkeypatch
):
    """When sqlfluff_config is None, resolver falls through to env/default."""
    _clear_populate_cache_env(monkeypatch)
    dbt_templater.sqlfluff_config = None
    assert dbt_templater._get_populate_relations_cache() is True
    monkeypatch.setenv("DBT_POPULATE_CACHE", "false")
    assert dbt_templater._get_populate_relations_cache() is False


@pytest.mark.parametrize(
    ("raw_text", "expected"),
    [
        *(
            (tok, True)
            for tok in (
                "1",
                "true",
                "t",
                "yes",
                "y",
                "on",
                "TRUE",
                "TrUe",
                "YES",
                "On",
                "T",
                "Y",
                "  true \t",
                "\n 1 ",
            )
        ),
        *(
            (tok, False)
            for tok in (
                "0",
                "false",
                "f",
                "no",
                "n",
                "off",
                "FALSE",
                "FaLsE",
                "No",
                "OFF",
                "F",
                "N",
                "  false\n",
                "\t0  ",
            )
        ),
    ],
)
@pytest.mark.parametrize(
    "source", ["config", "DBT_ENGINE_POPULATE_CACHE", "DBT_POPULATE_CACHE"]
)
def test__templater_dbt_populate_relations_cache_text_tokens(
    dbt_templater, monkeypatch, source, raw_text, expected
):
    """Verify every accepted boolean text token, case variant, and trimming."""
    _clear_populate_cache_env(monkeypatch)
    overrides = {}
    if source == "config":
        overrides["populate_relations_cache"] = raw_text
    else:
        monkeypatch.setenv(source, raw_text)
    dbt_templater.sqlfluff_config = _make_dbt_cache_config(**overrides)
    assert dbt_templater._get_populate_relations_cache() is expected


@pytest.mark.parametrize(
    ("ini_line", "expected"),
    [
        ("populate_relations_cache = True", True),
        ("populate_relations_cache = False", False),
        ("populate_relations_cache = off", False),
        ("populate_relations_cache = yes", True),
        ("populate_relations_cache = None", False),  # falls through to env
    ],
)
def test__templater_dbt_populate_relations_cache_ini_config(
    dbt_templater, monkeypatch, ini_line, expected
):
    """Verify INI parsing for booleans, text tokens, and None fallthrough."""
    _clear_populate_cache_env(monkeypatch)
    monkeypatch.setenv("DBT_POPULATE_CACHE", "false")
    dbt_templater.sqlfluff_config = FluffConfig.from_string(
        f"[sqlfluff]\ndialect = ansi\n[sqlfluff:templater:dbt]\n{ini_line}\n"
    )
    assert dbt_templater._get_populate_relations_cache() is expected


@pytest.mark.parametrize(
    ("mode", "value", "expected_source"),
    [
        *(
            ("config", bad, "populate_relations_cache")
            for bad in (
                "",
                " ",
                "\t\n",
                "maybe",
                "2",
                "enabled",
                "none",
                0,
                1,
                1.5,
                ["true"],
                {"value": True},
            )
        ),
        *(
            ("ini", line, "populate_relations_cache")
            for line in (
                "populate_relations_cache =",
                "populate_relations_cache = 0",
                "populate_relations_cache = 1",
                "populate_relations_cache = maybe",
            )
        ),
        *(
            ("engine_env", bad, "DBT_ENGINE_POPULATE_CACHE")
            for bad in (" ", "\t\n", "maybe", "2", "none")
        ),
        *(
            ("legacy_env", bad, "DBT_POPULATE_CACHE")
            for bad in (" ", "\t\n", "maybe", "2", "none")
        ),
    ],
)
def test__templater_dbt_populate_relations_cache_invalid_values(
    dbt_templater, monkeypatch, mode, value, expected_source
):
    """Invalid selected config, INI, or env values error without fallback."""
    _clear_populate_cache_env(monkeypatch)
    if mode == "config":
        monkeypatch.setenv("DBT_ENGINE_POPULATE_CACHE", "true")
        monkeypatch.setenv("DBT_POPULATE_CACHE", "false")
        dbt_templater.sqlfluff_config = _make_dbt_cache_config(
            populate_relations_cache=value
        )
    elif mode == "ini":
        monkeypatch.setenv("DBT_POPULATE_CACHE", "false")
        dbt_templater.sqlfluff_config = FluffConfig.from_string(
            f"[sqlfluff]\ndialect = ansi\n[sqlfluff:templater:dbt]\n{value}\n"
        )
    elif mode == "engine_env":
        monkeypatch.setenv("DBT_ENGINE_POPULATE_CACHE", value)
        monkeypatch.setenv("DBT_POPULATE_CACHE", "false")
        dbt_templater.sqlfluff_config = _make_dbt_cache_config()
    else:
        monkeypatch.setenv("DBT_POPULATE_CACHE", value)
        dbt_templater.sqlfluff_config = _make_dbt_cache_config()

    with pytest.raises(SQLFluffUserError, match=expected_source):
        dbt_templater._get_populate_relations_cache()


@pytest.mark.parametrize(
    ("ini_line", "expected_value"),
    [
        ("populate_relations_cache = 0", 0),
        ("populate_relations_cache = 1", 1),
    ],
)
def test__templater_dbt_populate_relations_cache_ini_numeric_guidance(
    dbt_templater, monkeypatch, ini_line, expected_value
):
    """Numeric INI 0/1 error with source, string-token clarity, and INI advice."""
    _clear_populate_cache_env(monkeypatch)
    monkeypatch.setenv("DBT_POPULATE_CACHE", "false")
    dbt_templater.sqlfluff_config = FluffConfig.from_string(
        f"[sqlfluff]\ndialect = ansi\n[sqlfluff:templater:dbt]\n{ini_line}\n"
    )
    raw = dbt_templater.sqlfluff_config.get_section(
        ("templater", "dbt", "populate_relations_cache")
    )
    assert type(raw) is int and raw == expected_value

    with pytest.raises(SQLFluffUserError) as excinfo:
        dbt_templater._get_populate_relations_cache()

    message = str(excinfo.value)
    assert "[sqlfluff:templater:dbt] populate_relations_cache" in message
    assert f"Invalid boolean value {expected_value!r} for " in message
    assert "INI" in message and "True/False" in message
    assert "string" in message
    assert "'0'" in message and "'1'" in message


@pytest.mark.parametrize("dbt_version_tuple", [(1, 7), (1, 8)])
@pytest.mark.parametrize(
    ("config_value", "expected_warm"),
    [(None, True), (True, True), (False, False)],
    ids=["default", "explicit_true", "explicit_false"],
)
def test__templater_dbt_populate_relations_cache_connection_signatures(
    tmp_path, monkeypatch, dbt_version_tuple, config_value, expected_warm
):
    """Verify exact connection() calls and signatures for dbt 1.7 and >=1.8."""
    import dbt.context.providers as dbt_providers

    _clear_populate_cache_env(monkeypatch)
    monkeypatch.setattr(DbtTemplater, "adapters", {})
    ctx = _make_mock_dbt_process_context(tmp_path)

    nodes_sentinel = object()
    values_calls = 0

    class _TrackingNodes(dict):
        def values(self):
            nonlocal values_calls
            values_calls += 1
            return nodes_sentinel

    ctx["manifest"].nodes = _TrackingNodes(ctx["manifest"].nodes)
    overrides = (
        {"populate_relations_cache": config_value} if config_value is not None else {}
    )
    config = _make_dbt_cache_config(ctx, **overrides)
    templater = config.get_templater()
    templater.sqlfluff_config = config
    templater.project_dir = ctx["project_dir"]
    templater.dbt_version_tuple = dbt_version_tuple
    templater.dbt_config = ctx["dbt_config"]
    templater.dbt_manifest = ctx["manifest"]
    templater.populate_relations_cache = templater._get_populate_relations_cache()

    macro_ctx_gen = object()
    monkeypatch.setattr(
        dbt_providers, "generate_runtime_macro_context", macro_ctx_gen, raising=False
    )
    _patch_adapter_lookup(monkeypatch, lambda _type: ctx["adapter"])

    with templater.connection():
        pass

    assert ctx["adapter"].acquire_connection.call_args_list == [mock.call("master")]
    if dbt_version_tuple >= (1, 8):
        assert ctx["adapter"].set_macro_resolver.call_args_list == [
            mock.call(ctx["manifest"])
        ]
        assert ctx["adapter"].set_macro_context_generator.call_args_list == [
            mock.call(macro_ctx_gen)
        ]
        assert values_calls == int(expected_warm)
        expected_cache = [mock.call(nodes_sentinel)] if expected_warm else []
    else:
        assert ctx["adapter"].set_macro_resolver.call_count == 0
        assert ctx["adapter"].set_macro_context_generator.call_count == 0
        assert values_calls == 0
        expected_cache = [mock.call(ctx["manifest"])] if expected_warm else []
    assert ctx["adapter"].set_relations_cache.call_args_list == expected_cache


def test__templater_dbt_populate_relations_cache_direct_connection_default(
    tmp_path, monkeypatch
):
    """Direct connection() before process() preserves default True warm-up."""
    monkeypatch.setattr(DbtTemplater, "adapters", {})
    ctx = _make_mock_dbt_process_context(tmp_path)
    _patch_adapter_lookup(monkeypatch, lambda _type: ctx["adapter"])

    templater = DbtTemplater()
    assert templater.populate_relations_cache is True
    templater.project_dir = ctx["project_dir"]
    templater.dbt_config = ctx["dbt_config"]
    templater.dbt_manifest = ctx["manifest"]

    with templater.connection():
        pass

    assert ctx["adapter"].acquire_connection.call_args_list == [mock.call("master")]
    assert ctx["adapter"].set_relations_cache.call_count == 1


@pytest.mark.parametrize(
    ("config_value", "env_var", "env_value", "expected_source"),
    [
        ("invalid", None, None, "populate_relations_cache"),
        (0, None, None, "populate_relations_cache"),
        (None, "DBT_ENGINE_POPULATE_CACHE", "   ", "DBT_ENGINE_POPULATE_CACHE"),
        (None, "DBT_POPULATE_CACHE", "invalid", "DBT_POPULATE_CACHE"),
    ],
)
def test__templater_dbt_populate_relations_cache_error_timing_and_pickling(
    tmp_path, monkeypatch, config_value, env_var, env_value, expected_source
):
    """Invalid values fail before project/profile/dbt/adapter setup and pickle."""
    _clear_populate_cache_env(monkeypatch)
    if env_var is not None:
        monkeypatch.setenv(env_var, env_value)

    adapters_snapshot = {"/existing/project": object()}
    monkeypatch.setattr(DbtTemplater, "adapters", dict(adapters_snapshot))

    overrides = {"project_dir": str(tmp_path), "profiles_dir": str(tmp_path)}
    if config_value is not None:
        overrides["populate_relations_cache"] = config_value
    config = _make_dbt_cache_config(**overrides)
    templater = config.get_templater()

    def _forbid(*args, **kwargs):
        raise AssertionError("Should not run before cache flag validation")

    _patch_adapter_lookup(monkeypatch, _forbid)
    with (
        mock.patch.object(templater, "_get_project_dir", side_effect=_forbid),
        mock.patch.object(templater, "_get_profiles_dir", side_effect=_forbid),
        mock.patch.object(
            type(templater), "dbt_config", new_callable=lambda: property(_forbid)
        ),
        mock.patch.object(
            type(templater), "dbt_manifest", new_callable=lambda: property(_forbid)
        ),
        pytest.raises(SQLFluffUserError, match=expected_source) as excinfo,
    ):
        templater.process(
            fname=str(tmp_path / "models" / "my_model.sql"),
            in_str="select 1",
            config=config,
        )

    assert DbtTemplater.adapters == adapters_snapshot
    assert excinfo.value.__context__ is None
    assert excinfo.value.__cause__ is None
    roundtrip = pickle.loads(pickle.dumps(excinfo.value))
    assert isinstance(roundtrip, SQLFluffUserError)
    assert str(roundtrip) == str(excinfo.value)


def test__templater_dbt_populate_relations_cache_lifecycle(tmp_path, monkeypatch):
    """Preserve adapter reuse across entries/instances and independent projects."""
    _clear_populate_cache_env(monkeypatch)
    monkeypatch.setattr(DbtTemplater, "adapters", {})

    ctxs = {
        name: _make_mock_dbt_process_context(tmp_path, project_name=name)
        for name in ("project_a", "project_b", "project_c")
    }
    _patch_adapter_lookup(monkeypatch, lambda name: ctxs[name]["adapter"])

    def _run_step(ctx, populate_cache, templater=None, *, expected_warm):
        config = _make_dbt_cache_config(ctx, populate_relations_cache=populate_cache)
        if templater is None:
            templater = config.get_templater()
            _attach_mock_dbt_context(templater, ctx)
        templater.process(
            fname=ctx["model_file"], in_str=ctx["model_sql"], config=config
        )
        assert templater.populate_relations_cache is populate_cache
        assert ctx["adapter"].acquire_connection.call_count == 1
        assert ctx["adapter"].set_relations_cache.call_count == expected_warm
        assert DbtTemplater.adapters[ctx["project_dir"]] is ctx["adapter"]
        return templater

    # Project A: disabled -> repeat -> flip True -> 2nd instance (no retroactive warm)
    templater_a1 = _run_step(ctxs["project_a"], False, expected_warm=0)
    _run_step(ctxs["project_a"], False, templater=templater_a1, expected_warm=0)
    _run_step(ctxs["project_a"], True, templater=templater_a1, expected_warm=0)
    _run_step(ctxs["project_a"], True, expected_warm=0)

    # Project B: enabled -> flip False -> 2nd instance (no rewarm or cache clear)
    templater_b1 = _run_step(ctxs["project_b"], True, expected_warm=1)
    _run_step(ctxs["project_b"], False, templater=templater_b1, expected_warm=1)
    _run_step(ctxs["project_b"], False, expected_warm=1)
    assert ctxs["project_b"]["adapter"].cache.clear.call_count == 0

    # Distinct project C initializes independently while A and B remain registered
    _run_step(ctxs["project_c"], False, expected_warm=0)
    assert set(DbtTemplater.adapters) == {ctx["project_dir"] for ctx in ctxs.values()}


def test__templater_dbt_populate_relations_cache_real_dbt_flags_invalid_env(
    dbt_templater, monkeypatch
):
    """Verify SQLFluff selection vs installed dbt's own raw env flag validation."""
    import click
    from dbt import flags
    from dbt.cli.main import cli

    from sqlfluff_templater_dbt.templater import DbtConfigArgs

    envvar = next(
        param.envvar
        for param in cli.commands["run"].params
        if param.name == "populate_cache"
    )
    declared = {envvar} if isinstance(envvar, str) else set(envvar or ())
    assert "DBT_POPULATE_CACHE" in declared
    engine_env_supported = "DBT_ENGINE_POPULATE_CACHE" in declared

    original_flags = flags.get_flags()
    _clear_populate_cache_env(monkeypatch)
    dbt_templater.sqlfluff_config = _make_dbt_cache_config(
        populate_relations_cache=False
    )
    try:
        monkeypatch.setenv("DBT_POPULATE_CACHE", "not_a_bool")
        assert dbt_templater._get_populate_relations_cache() is False
        with pytest.raises(click.exceptions.BadParameter, match="not_a_bool"):
            flags.set_from_args(DbtConfigArgs(), None)

        monkeypatch.delenv("DBT_POPULATE_CACHE", raising=False)
        monkeypatch.setenv("DBT_ENGINE_POPULATE_CACHE", "not_a_bool")
        assert dbt_templater._get_populate_relations_cache() is False
        if engine_env_supported:
            with pytest.raises(click.exceptions.BadParameter, match="not_a_bool"):
                flags.set_from_args(DbtConfigArgs(), None)
        else:
            flags.set_from_args(DbtConfigArgs(), None)
    finally:
        flags.set_flags(original_flags)


@pytest.mark.parametrize("table_exists", [True, False], ids=["existing", "absent"])
def test__templater_dbt_populate_relations_cache_relation_consumer_mocked_db_boundary(
    tmp_path, monkeypatch, table_exists
):
    """Prove real is_incremental() / PostgresAdapter lookup at mocked DB boundary.

    Uses real DbtTemplater.process(), ManifestLoader, DbtCompiler,
    PostgresAdapter cache/get_relation/list_relations, and incremental.sql.
    Mocks only Postgres DB calls and forbids PostgresConnectionManager.open.
    """
    from dbt import flags
    from dbt.adapters.base.relation import RelationType
    from dbt.adapters.factory import reset_adapters
    from dbt.adapters.postgres.connections import PostgresConnectionManager
    from dbt.adapters.postgres.impl import PostgresAdapter
    from dbt.adapters.postgres.relation import PostgresRelation
    from dbt.compilation import Compiler as DbtCompiler

    incremental_sql = Path(
        "plugins/sqlfluff-templater-dbt/test/fixtures/dbt/dbt_project/"
        "models/my_new_project/incremental.sql"
    ).read_text()

    def _run_mode(populate_cache: bool):
        base = tmp_path / ("warm_on" if populate_cache else "warm_off")
        project_dir, profiles_dir = base / "dbt_project", base / "profiles"
        model_path = project_dir / "models" / "my_new_project" / "incremental.sql"
        model_path.parent.mkdir(parents=True)
        profiles_dir.mkdir(parents=True)

        (project_dir / "dbt_project.yml").write_text(
            "name: 'my_new_project'\nversion: '1.0.0'\nconfig-version: 2\n"
            "profile: 'default'\nmodels:\n  my_new_project:\n    materialized: view\n"
        )
        (profiles_dir / "profiles.yml").write_text(
            "default:\n  target: dev\n  outputs:\n    dev:\n      type: postgres\n"
            "      host: localhost\n      user: postgres\n      pass: password\n"
            "      port: 5432\n      dbname: postgres\n      schema: dbt_alice\n"
            "      threads: 1\n"
        )
        (project_dir / ".sqlfluff").write_text(
            "[sqlfluff]\ndialect = postgres\ntemplater = dbt\n"
            "[sqlfluff:templater:dbt]\n"
            f"project_dir = {project_dir}\nprofiles_dir = {profiles_dir}\n"
            f"populate_relations_cache = {populate_cache}\n"
        )
        model_path.write_text(incremental_sql)

        events: list[str] = []
        cache_at_compile: list[set[tuple[str | None, str]]] = []
        orig_set_cache = PostgresAdapter.set_relations_cache
        orig_compile = DbtCompiler.compile_node

        def _spy_set_cache(self, *args, **kwargs):
            events.append("set_relations_cache")
            return orig_set_cache(self, *args, **kwargs)

        def _spy_compile(self, *args, **kwargs):
            cache_at_compile.append(
                set(DbtTemplater.adapters[str(project_dir)].cache.schemas)
            )
            events.append("compile_node_start")
            return orig_compile(self, *args, **kwargs)

        def _fake_list_relations(self, schema_relation):
            events.append(f"list:{schema_relation.database}.{schema_relation.schema}")
            if table_exists and schema_relation.schema == "dbt_alice":
                return [
                    PostgresRelation.create(
                        database="postgres",
                        schema="dbt_alice",
                        identifier="incremental",
                        type=RelationType.Table,
                    )
                ]
            return []

        def _forbid_db_open(cls, connection):
            raise AssertionError("Live DB connection must not be opened in unit test")

        original_flags = flags.get_flags()
        monkeypatch.setattr(DbtTemplater, "adapters", {})
        reset_adapters()
        try:
            with (
                mock.patch.object(
                    PostgresAdapter, "set_relations_cache", _spy_set_cache
                ),
                mock.patch.object(
                    PostgresAdapter,
                    "list_relations_without_caching",
                    _fake_list_relations,
                ),
                mock.patch.object(
                    PostgresAdapter,
                    "_link_cached_database_relations",
                    lambda self, schemas: None,
                ),
                mock.patch.object(
                    PostgresConnectionManager, "open", classmethod(_forbid_db_open)
                ),
                mock.patch.object(DbtCompiler, "compile_node", _spy_compile),
            ):
                linted = Linter(
                    config=FluffConfig.from_path(str(project_dir))
                ).lint_path(path=str(model_path))
        finally:
            reset_adapters()
            flags.set_flags(original_flags)

        assert len(linted.files) == 1
        assert len(cache_at_compile) == 1
        return {
            "templated_str": linted.files[0].templated_file.templated_str,
            "violations": linted.check_tuples(),
            "events": events,
            "cache_at_compile": cache_at_compile[0],
        }

    _clear_populate_cache_env(monkeypatch)
    warm_on = _run_mode(populate_cache=True)
    warm_off = _run_mode(populate_cache=False)

    assert warm_off["templated_str"] == warm_on["templated_str"]
    assert warm_off["violations"] == warm_on["violations"]
    assert (
        "select max(valid_date_local) from" in warm_on["templated_str"]
    ) is table_exists

    on_idx = warm_on["events"].index("compile_node_start")
    assert warm_on["events"].count("set_relations_cache") == 1
    assert warm_on["events"].index("set_relations_cache") < on_idx
    assert any(e.startswith("list:") for e in warm_on["events"][:on_idx])
    assert not any(e.startswith("list:") for e in warm_on["events"][on_idx:])
    assert ("postgres", "dbt_alice") in warm_on["cache_at_compile"]

    off_idx = warm_off["events"].index("compile_node_start")
    assert "set_relations_cache" not in warm_off["events"]
    assert warm_off["cache_at_compile"] == set()
    assert not any(e.startswith("list:") for e in warm_off["events"][:off_idx])
    assert any(e.startswith("list:") for e in warm_off["events"][off_idx:])
