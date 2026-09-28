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


@pytest.mark.parametrize("use_catalogs_v2", [False, True])
def test__templater_dbt_manifest_resolves_catalog(tmp_path, use_catalogs_v2):
    """Parse a dbt BigQuery model using a catalog from catalogs.yml."""
    if DbtTemplater().dbt_version_tuple < (1, 10):
        pytest.skip("catalog integrations require dbt 1.10+")
    if use_catalogs_v2 and DbtTemplater().dbt_version_tuple < (1, 12):
        pytest.skip("catalogs.yml v2 requires dbt 1.12+")
    pytest.importorskip("dbt.adapters.bigquery")
    from dbt.adapters.factory import get_adapter

    (tmp_path / "models").mkdir()
    (tmp_path / "dbt_project.yml").write_text(
        "name: example\nversion: '1.0.0'\nconfig-version: 2\nprofile: example\n"
        f"flags:\n  use_catalogs_v2: {str(use_catalogs_v2).lower()}\n"
    )
    (tmp_path / "profiles.yml").write_text(
        "example:\n  target: dev\n  outputs:\n    dev:\n"
        "      type: bigquery\n      method: oauth\n"
        "      project: example-project\n      dataset: example_dataset\n"
        "      threads: 1\n"
    )
    if use_catalogs_v2:
        (tmp_path / "catalogs.yml").write_text(
            "catalogs:\n  - name: my_catalog\n    type: biglake_metastore\n"
            "    table_format: iceberg\n    config:\n      bigquery:\n"
            "        external_volume: gs://my-bucket\n        file_format: parquet\n"
        )
    else:
        (tmp_path / "catalogs.yml").write_text(
            "catalogs:\n  - name: my_catalog\n"
            "    active_write_integration: my_catalog\n"
            "    write_integrations:\n      - name: my_catalog\n"
            "        catalog_type: biglake_metastore\n"
            "        external_volume: gs://my-bucket\n"
        )
    (tmp_path / "models" / "my_model.sql").write_text(
        "{{ config(materialized='table', catalog_name='my_catalog', "
        "storage_uri='gs://my-bucket/my_model') }}\nSELECT 1 AS id\n"
    )

    templater = DbtTemplater()
    templater.sqlfluff_config = FluffConfig(
        overrides={"dialect": "bigquery", "templater": "dbt"}
    )
    templater.project_dir = str(tmp_path)
    templater.profiles_dir = str(tmp_path)

    try:
        assert "model.example.my_model" in templater.dbt_manifest.nodes
        assert (
            get_adapter(templater.dbt_config).get_catalog_integration("my_catalog").name
            == "my_catalog"
        )
    finally:
        from dbt.adapters.factory import reset_adapters

        reset_adapters()


def test__templater_dbt_legacy_catalog_before_manifest(tmp_path):
    """Register catalogs before manifest loading in the Postgres CI matrix."""
    if DbtTemplater().dbt_version_tuple < (1, 10):
        pytest.skip("catalog integrations require dbt 1.10+")
    from dbt.config import catalogs
    from dbt.parser.manifest import ManifestLoader

    (tmp_path / "catalogs.yml").write_text(
        "catalogs:\n  - name: my_catalog\n"
        "    active_write_integration: my_write\n"
        "    write_integrations:\n      - name: my_write\n"
        "        catalog_type: postgres\n"
    )
    templater = DbtTemplater()
    runtime_config = SimpleNamespace(
        flags={}, project_root=str(tmp_path), project_name="example", cli_vars={}
    )
    templater.__dict__["dbt_config"] = runtime_config
    adapter = mock.Mock()
    manifest = object()

    def manifest_after_registration(config):
        assert config is runtime_config
        adapter.add_catalog_integration.assert_called_once()
        integration = adapter.add_catalog_integration.call_args.args[0]
        assert integration.name == "my_catalog"
        assert integration.catalog_name == "my_write"
        return manifest

    with (
        mock.patch("dbt.adapters.factory.get_adapter", return_value=adapter),
        mock.patch.object(
            ManifestLoader, "get_full_manifest", side_effect=manifest_after_registration
        ),
    ):
        assert templater.dbt_manifest is manifest
    assert len(catalogs.load_catalogs(str(tmp_path), "example", {})) == 1


def test__templater_dbt_duplicate_catalog_is_idempotent(tmp_path):
    """Ignore an equivalent catalog already registered by another project."""
    if DbtTemplater().dbt_version_tuple < (1, 10):
        pytest.skip("catalog integrations require dbt 1.10+")
    from dbt.adapters.catalogs import DbtCatalogIntegrationAlreadyExistsError
    from dbt.parser.manifest import ManifestLoader

    (tmp_path / "catalogs.yml").write_text(
        "catalogs:\n  - name: my_catalog\n"
        "    active_write_integration: my_write\n"
        "    write_integrations:\n      - name: my_write\n"
        "        catalog_type: postgres\n"
    )
    templater = DbtTemplater()
    templater.__dict__["dbt_config"] = SimpleNamespace(
        flags={}, project_root=str(tmp_path), project_name="example", cli_vars={}
    )
    adapter = mock.Mock()
    adapter.add_catalog_integration.side_effect = (
        DbtCatalogIntegrationAlreadyExistsError("my_catalog")
    )
    adapter.get_catalog_integration.return_value = SimpleNamespace(
        catalog_type="postgres",
        catalog_name="my_write",
        table_format=None,
        file_format=None,
        external_volume=None,
        catalog_database=None,
    )
    with (
        mock.patch("dbt.adapters.factory.get_adapter", return_value=adapter),
        mock.patch.object(ManifestLoader, "get_full_manifest") as load_manifest,
    ):
        assert templater.dbt_manifest is load_manifest.return_value
    load_manifest.assert_called_once()


def test__templater_dbt_mismatched_duplicate_catalog_raises(tmp_path):
    """Do not hide a different catalog definition under the same name."""
    if DbtTemplater().dbt_version_tuple < (1, 10):
        pytest.skip("catalog integrations require dbt 1.10+")
    from dbt.adapters.catalogs import DbtCatalogIntegrationAlreadyExistsError
    from dbt.parser.manifest import ManifestLoader

    (tmp_path / "catalogs.yml").write_text(
        "catalogs:\n  - name: my_catalog\n"
        "    active_write_integration: my_write\n"
        "    write_integrations:\n      - name: my_write\n"
        "        catalog_type: postgres\n"
    )
    templater = DbtTemplater()
    templater.__dict__["dbt_config"] = SimpleNamespace(
        flags={}, project_root=str(tmp_path), project_name="example", cli_vars={}
    )
    adapter = mock.Mock()
    adapter.add_catalog_integration.side_effect = (
        DbtCatalogIntegrationAlreadyExistsError("my_catalog")
    )
    adapter.get_catalog_integration.return_value = SimpleNamespace(
        catalog_type="postgres",
        catalog_name="different_catalog",
        table_format=None,
        file_format=None,
        external_volume=None,
        catalog_database=None,
    )
    with (
        mock.patch("dbt.adapters.factory.get_adapter", return_value=adapter),
        mock.patch.object(ManifestLoader, "get_full_manifest") as load_manifest,
        pytest.raises(SQLFluffUserError, match="Catalog already exists: my_catalog"),
    ):
        _ = templater.dbt_manifest
    load_manifest.assert_not_called()


def test__templater_dbt_v2_rejects_unsupported_adapter(tmp_path):
    """Give an actionable error before bridging a v2 catalog on older adapters."""
    if DbtTemplater().dbt_version_tuple < (1, 12):
        pytest.skip("catalogs.yml v2 requires dbt 1.12+")
    from dbt.adapters.capability import Capability
    from dbt.config import catalogs
    from dbt.parser.manifest import ManifestLoader

    (tmp_path / "catalogs.yml").write_text(
        "catalogs:\n  - name: my_catalog\n"
        "    type: biglake_metastore\n    table_format: iceberg\n"
        "    config:\n      bigquery:\n"
        "        external_volume: gs://my-bucket\n"
    )
    templater = DbtTemplater()
    templater.__dict__["dbt_config"] = SimpleNamespace(
        flags={"use_catalogs_v2": True},
        project_root=str(tmp_path),
        project_name="example",
        cli_vars={},
    )
    adapter = mock.Mock()
    adapter.type.return_value = "unsupported"
    adapter.capabilities.return_value = {Capability.CatalogsV2: False}
    with (
        mock.patch("dbt.adapters.factory.get_adapter", return_value=adapter),
        mock.patch.object(ManifestLoader, "get_full_manifest") as load_manifest,
        pytest.raises(SQLFluffUserError, match="does not support catalogs.yml v2"),
    ):
        _ = templater.dbt_manifest
    adapter.bridge_v2_catalog.assert_not_called()
    load_manifest.assert_not_called()
    assert len(catalogs.load_catalogs_v2(str(tmp_path), "example", {})) == 1


def test__templater_dbt_v2_requires_supported_dbt():
    """Explain when catalogs.yml v2 is requested on an older dbt version."""
    if DbtTemplater().dbt_version_tuple >= (1, 12):
        pytest.skip("catalogs.yml v2 is available in dbt 1.12+")
    from dbt.parser.manifest import ManifestLoader

    templater = DbtTemplater()
    templater.__dict__["dbt_config"] = SimpleNamespace(
        flags={"use_catalogs_v2": True},
        project_root="/project",
        project_name="example",
        cli_vars={},
    )
    with (
        mock.patch("dbt.adapters.factory.get_adapter"),
        mock.patch.object(ManifestLoader, "get_full_manifest") as load_manifest,
        pytest.raises(SQLFluffUserError, match="does not support catalogs.yml v2"),
    ):
        _ = templater.dbt_manifest
    load_manifest.assert_not_called()


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
