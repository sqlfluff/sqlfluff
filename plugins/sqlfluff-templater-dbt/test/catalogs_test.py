"""Catalog registration before dbt manifest parsing."""

import importlib.util
import traceback
from types import SimpleNamespace
from unittest import mock

import pytest

from sqlfluff.core import FluffConfig
from sqlfluff.core.errors import SQLFluffUserError
from sqlfluff_templater_dbt.templater import DbtTemplater


@pytest.fixture
def catalog_templater(tmp_path, monkeypatch):
    """Use real dbt catalog loaders without opening a database connection."""
    from dbt import flags
    from dbt.adapters import factory

    templater = DbtTemplater()
    templater.__dict__["dbt_config"] = SimpleNamespace(
        project_root=str(tmp_path), project_name="example", cli_vars={}
    )

    class Adapter:
        def __init__(self, *args):
            self._catalog_client = SimpleNamespace()
            self.add_catalog_integration = mock.Mock()
            self.capabilities = mock.Mock()
            self.bridge_v2_catalog = mock.Mock()
            self.cleanup_connections = mock.Mock()

    adapter = Adapter()
    monkeypatch.setattr(factory, "get_adapter", lambda config: adapter)
    monkeypatch.setattr(flags, "GLOBAL_FLAGS", SimpleNamespace(USE_CATALOGS_V2=False))
    return templater, adapter, tmp_path


def test__templater_dbt_catalogs_legacy(catalog_templater):
    """Older dbt versions need no catalog APIs."""
    templater, adapter, _ = catalog_templater
    templater.__dict__["dbt_version_tuple"] = (1, 7)
    templater._register_catalog_integrations()
    adapter.add_catalog_integration.assert_not_called()


@pytest.mark.parametrize("version", [(1, 7), (1, 8), (1, 9), (1, 10), (1, 11)])
def test__templater_dbt_catalogs_v2_requires_supported_dbt(
    catalog_templater, monkeypatch, version
):
    """Check the unsupported flag before the legacy no-op."""
    from dbt import flags

    templater, _, _ = catalog_templater
    templater.__dict__["dbt_version_tuple"] = version
    monkeypatch.setattr(flags, "GLOBAL_FLAGS", SimpleNamespace(USE_CATALOGS_V2=True))
    with pytest.raises(SQLFluffUserError, match="1.12"):
        templater._register_catalog_integrations()


def test__templater_dbt_catalogs_v1(catalog_templater):
    """Render vars and register only the active v1 integration, once."""
    templater, adapter, project = catalog_templater
    if templater.dbt_version_tuple < (1, 10):
        pytest.skip("Catalogs require dbt 1.10+")
    templater.dbt_config.cli_vars = {"volume": "test-volume"}
    (project / "catalogs.yml").write_text(
        "catalogs:\n"
        "  - name: custom_catalog\n"
        "    active_write_integration: active\n"
        "    write_integrations:\n"
        "      - name: inactive\n"
        "        catalog_type: iceberg_rest\n"
        "      - name: active\n"
        "        catalog_type: iceberg_rest\n"
        "        external_volume: \"{{ var('volume') }}\"\n"
        "        adapter_properties:\n"
        "          nested: {option: original}\n"
    )
    templater._register_catalog_integrations()
    integration = adapter.add_catalog_integration.call_args.args[0]
    assert integration.name == "custom_catalog"
    assert integration.catalog_name == "active"
    assert integration.external_volume == "test-volume"
    assert integration.adapter_properties == {"nested": {"option": "original"}}
    templater._register_catalog_integrations()
    adapter.add_catalog_integration.assert_called_once()

    # New templater instances for the same project reuse registrations.
    other = DbtTemplater()
    other.__dict__["dbt_config"] = templater.dbt_config
    other._register_catalog_integrations()
    adapter.add_catalog_integration.assert_called_once()
    path = project / "catalogs.yml"
    path.write_text(path.read_text().replace("original", "changed"))
    with pytest.raises(SQLFluffUserError, match="different configuration"):
        other._register_catalog_integrations()
    adapter.add_catalog_integration.assert_called_once()


@pytest.mark.parametrize("change", ["remove", "rename"])
def test__templater_dbt_catalogs_changed_membership(catalog_templater, change):
    """Removed definitions cannot resolve through a shared adapter's old state."""
    templater, adapter, project = catalog_templater
    if templater.dbt_version_tuple < (1, 10):
        pytest.skip("Catalogs require dbt 1.10+")
    path = project / "catalogs.yml"
    path.write_text(
        "catalogs:\n  - name: custom_catalog\n    write_integrations:\n"
        "      - {name: active, catalog_type: iceberg_rest}\n"
    )
    templater._register_catalog_integrations()
    if change == "remove":
        path.unlink()
    else:
        path.write_text(path.read_text().replace("custom_catalog", "renamed_catalog"))
    other = DbtTemplater()
    other.__dict__["dbt_config"] = templater.dbt_config
    with pytest.raises(SQLFluffUserError, match="different configuration"):
        other._register_catalog_integrations()
    adapter.add_catalog_integration.assert_called_once()


@pytest.mark.parametrize("second_catalog", [None, "other_catalog", "custom_catalog"])
def test__templater_dbt_catalogs_project_clients(
    catalog_templater, monkeypatch, second_catalog
):
    """Isolate real dbt catalog clients on every supported catalog version."""
    templater, adapter, project = catalog_templater
    if templater.dbt_version_tuple < (1, 10):
        pytest.skip("Catalogs require dbt 1.10+")
    from dbt.adapters import factory as dbt_factory
    from dbt.adapters.catalogs import (
        CatalogIntegrationClient,
        DbtCatalogIntegrationNotFoundError,
    )

    factory = mock.Mock(catalog_type="iceberg_rest", side_effect=lambda config: config)

    class CatalogAdapter(type(adapter)):
        def __init__(self, *args):
            super().__init__(*args)
            self._catalog_client = CatalogIntegrationClient([factory])
            self._catalog_client.add(
                SimpleNamespace(name="default_catalog", catalog_type="iceberg_rest")
            )

    adapter = CatalogAdapter()
    monkeypatch.setattr(dbt_factory, "get_adapter", lambda config: adapter)
    adapter.add_catalog_integration.side_effect = lambda config: (
        adapter._catalog_client.add(config)
    )

    def write_catalog(root, name, volume):
        (root / "catalogs.yml").write_text(
            f"catalogs:\n  - name: {name}\n    write_integrations:\n"
            "      - name: active\n        catalog_type: iceberg_rest\n"
            f"        external_volume: {volume}\n"
        )

    write_catalog(project, "custom_catalog", "first-volume")
    templater._register_catalog_integrations()
    original = adapter._catalog_client.get("custom_catalog")
    other_project = project / "other"
    other_project.mkdir()
    if second_catalog is not None:
        write_catalog(other_project, second_catalog, "second-volume")
    other = DbtTemplater()
    other.__dict__["dbt_config"] = SimpleNamespace(
        project_root=str(other_project), project_name="example", cli_vars={}
    )
    other._register_catalog_integrations()
    assert adapter._catalog_client.get("default_catalog").name == "default_catalog"
    if second_catalog is not None:
        assert (
            adapter._catalog_client.get(second_catalog).external_volume
            == "second-volume"
        )
    if second_catalog != "custom_catalog":
        with pytest.raises(DbtCatalogIntegrationNotFoundError):
            adapter._catalog_client.get("custom_catalog")
    templater._register_catalog_integrations()
    assert adapter._catalog_client.get("custom_catalog") is original
    assert adapter._catalog_client.get("default_catalog").name == "default_catalog"
    assert adapter.add_catalog_integration.call_count == (
        1 if second_catalog is None else 2
    )


@pytest.mark.parametrize(
    "content",
    [
        pytest.param("catalogs: [", id="syntax"),
        pytest.param("catalogs: not-a-list", id="wrong-container"),
        pytest.param("catalogs: [42]", id="wrong-entry"),
        pytest.param("catalogs: [{name: private-sentinel}]", id="missing-fields"),
        pytest.param(
            "catalogs: [{name: private-sentinel, write_integrations: []}]",
            id="empty-integrations",
        ),
        pytest.param(b"\xffprivate-sentinel", id="encoding"),
        pytest.param("catalogs: " + "9" * 10000, id="oversized-number"),
        pytest.param("catalogs: " + "[" * 1500 + "0" + "]" * 1500, id="nesting"),
        pytest.param("catalogs: &recursive [*recursive]", id="recursion"),
        pytest.param(
            "catalogs: !!python/object:private-sentinel {}", id="unsafe-yaml-tag"
        ),
        pytest.param(
            "catalogs:\n  - name: private-sentinel\n"
            "    write_integrations:\n"
            "      - {name: duplicate, catalog_type: iceberg_rest}\n"
            "      - {name: duplicate, catalog_type: iceberg_rest}\n",
            id="duplicate-integration",
        ),
    ],
)
def test__templater_dbt_catalogs_invalid(catalog_templater, content):
    """Parse failures are stable, pickle-safe errors without config values."""
    templater, adapter, project = catalog_templater
    if templater.dbt_version_tuple < (1, 10):
        pytest.skip("Catalogs require dbt 1.10+")
    (project / "catalogs.yml").write_bytes(
        content.encode() if isinstance(content, str) else content
    )
    with pytest.raises(SQLFluffUserError, match="catalogs.yml") as error:
        templater._register_catalog_integrations()
    assert error.value.__context__ is None
    assert error.value.__cause__ is None
    assert "private-sentinel" not in "".join(traceback.format_exception(error.value))
    adapter.add_catalog_integration.assert_not_called()


def test__templater_dbt_catalogs_scalar_and_duplicate_fields(catalog_templater):
    """Keep dbt's YAML field semantics and support ordinary large strings."""
    templater, adapter, project = catalog_templater
    if templater.dbt_version_tuple < (1, 10):
        pytest.skip("Catalogs require dbt 1.10+")
    volume = "x" * 65536
    (project / "catalogs.yml").write_text(
        "catalogs:\n  - name: custom_catalog\n"
        "    write_integrations:\n      - name: active\n"
        "        catalog_type: iceberg_rest\n"
        "        external_volume: overridden\n"
        f"        external_volume: {volume}\n"
    )
    templater._register_catalog_integrations()
    assert adapter.add_catalog_integration.call_args.args[0].external_volume == volume


def test__templater_dbt_catalogs_duplicate_names(catalog_templater):
    """Idempotence across loads must not hide duplicate definitions in one file."""
    templater, adapter, project = catalog_templater
    if templater.dbt_version_tuple < (1, 10):
        pytest.skip("Catalogs require dbt 1.10+")
    catalog = (
        "  - name: private-sentinel\n    write_integrations:\n"
        "      - {name: active, catalog_type: iceberg_rest}\n"
    )
    (project / "catalogs.yml").write_text("catalogs:\n" + catalog * 2)
    with pytest.raises(SQLFluffUserError, match="catalogs.yml") as error:
        templater._register_catalog_integrations()
    assert "private-sentinel" not in "".join(traceback.format_exception(error.value))
    adapter.add_catalog_integration.assert_not_called()


@pytest.mark.parametrize("supported", [False, True])
def test__templater_dbt_catalogs_v2_capability(
    catalog_templater, monkeypatch, supported
):
    """Only bridge v2 configurations when the adapter supports them."""
    templater, adapter, project = catalog_templater
    if templater.dbt_version_tuple < (1, 12):
        pytest.skip("Catalogs v2 require dbt 1.12+")
    from dbt import flags
    from dbt.adapters.capability import (
        Capability,
        CapabilityDict,
        CapabilitySupport,
        Support,
    )
    from dbt.artifacts.resources import CatalogWriteIntegrationConfig

    monkeypatch.setattr(flags, "GLOBAL_FLAGS", SimpleNamespace(USE_CATALOGS_V2=True))
    adapter.capabilities.return_value = CapabilityDict(
        {
            Capability.CatalogsV2: CapabilitySupport(
                Support.Full if supported else Support.Unsupported
            )
        }
    )
    (project / "catalogs.yml").write_text(
        "catalogs:\n  - name: custom_catalog\n    type: iceberg_rest\n"
        "    table_format: iceberg\n    config: {}\n"
    )
    integration = CatalogWriteIntegrationConfig(
        name="custom_catalog", catalog_type="iceberg_rest", catalog_name="active"
    )
    adapter.bridge_v2_catalog.return_value = integration
    if supported:
        templater._register_catalog_integrations()
        adapter.bridge_v2_catalog.assert_called_once()
        adapter.add_catalog_integration.assert_called_once_with(integration)
    else:
        with pytest.raises(SQLFluffUserError, match="does not support"):
            templater._register_catalog_integrations()
        adapter.bridge_v2_catalog.assert_not_called()
        adapter.add_catalog_integration.assert_not_called()


def test__templater_dbt_catalogs_v2_duplicate_names(catalog_templater, monkeypatch):
    """Keep the official v2 loader's duplicate-name validation."""
    templater, adapter, project = catalog_templater
    if templater.dbt_version_tuple < (1, 12):
        pytest.skip("Catalogs v2 require dbt 1.12+")
    from dbt import flags

    monkeypatch.setattr(flags, "GLOBAL_FLAGS", SimpleNamespace(USE_CATALOGS_V2=True))
    catalog = (
        "  - name: private-sentinel\n    type: iceberg_rest\n"
        "    table_format: iceberg\n    config: {}\n"
    )
    (project / "catalogs.yml").write_text("catalogs:\n" + catalog * 2)
    with pytest.raises(SQLFluffUserError, match="catalogs.yml") as error:
        templater._register_catalog_integrations()
    assert error.value.__context__ is None
    assert "private-sentinel" not in "".join(traceback.format_exception(error.value))
    adapter.add_catalog_integration.assert_not_called()


@pytest.mark.parametrize(
    "exception", [ValueError, TypeError, RecursionError, RuntimeError]
)
def test__templater_dbt_catalogs_validation_errors(
    catalog_templater, monkeypatch, exception
):
    """Include loader/renderer validation callbacks in the error boundary."""
    templater, _, _ = catalog_templater
    if templater.dbt_version_tuple < (1, 10):
        pytest.skip("Catalogs require dbt 1.10+")
    from dbt.config import catalogs

    def fail(*args):
        raise exception("private-sentinel")

    monkeypatch.setattr(catalogs, "load_catalogs", fail)
    with pytest.raises(SQLFluffUserError, match="catalogs.yml") as error:
        templater._register_catalog_integrations()
    assert error.value.__context__ is None
    assert "private-sentinel" not in "".join(traceback.format_exception(error.value))


@pytest.mark.parametrize("exception", [KeyboardInterrupt, SystemExit])
def test__templater_dbt_catalogs_interrupts(catalog_templater, monkeypatch, exception):
    """User interrupts must leave the catalog loading stage unchanged."""
    templater, _, _ = catalog_templater
    if templater.dbt_version_tuple < (1, 10):
        pytest.skip("Catalogs require dbt 1.10+")
    from dbt.config import catalogs

    def fail(*args):
        raise exception()

    monkeypatch.setattr(catalogs, "load_catalogs", fail)
    with pytest.raises(exception):
        templater._register_catalog_integrations()


@pytest.fixture
def bigquery_catalog_project(tmp_path, monkeypatch):
    """Create projects sharing a real BigQuery adapter, without a connection."""
    if DbtTemplater().dbt_version_tuple < (1, 12):
        pytest.skip("This integration uses dbt 1.12+ and BigQuery")
    if importlib.util.find_spec("dbt.adapters.bigquery") is None:
        pytest.skip("Optional BigQuery adapter is not installed")
    from dbt.adapters import factory

    # Keep dbt's process-global adapter registry separate from other tests.
    registry = factory.AdapterContainer()
    monkeypatch.setattr(factory, "FACTORY", registry)

    def make_project(name, v2, catalog_name="my_catalog", volume="gs://my-bucket"):
        project = tmp_path / name
        (project / "models").mkdir(parents=True)
        (project / "dbt_project.yml").write_text(
            "name: example\nversion: '1.0.0'\nconfig-version: 2\nprofile: example\n"
            f"flags:\n  use_catalogs_v2: {str(v2).lower()}\n"
        )
        (project / "profiles.yml").write_text(
            "example:\n  target: dev\n  outputs:\n    dev:\n"
            "      type: bigquery\n      method: oauth\n      project: dummy-project\n"
            "      dataset: dummy_dataset\n      threads: 1\n"
        )
        if catalog_name is not None:
            (project / "catalogs.yml").write_text(
                f"catalogs:\n  - name: {catalog_name}\n"
                + (
                    "    type: biglake_metastore\n    table_format: iceberg\n"
                    f"    config:\n      bigquery:\n        external_volume: {volume}\n"
                    "        file_format: parquet\n"
                    if v2
                    else "    write_integrations:\n      - name: biglake\n"
                    "        catalog_type: biglake_metastore\n        table_format: iceberg\n"
                    f"        external_volume: {volume}\n        file_format: parquet\n"
                )
            )
        (project / "models/my_model.sql").write_text(
            (
                "{{ config(materialized='table', "
                f"catalog_name='{catalog_name}', storage_uri='{volume}/my_model') "
                "}}\n"
                if catalog_name is not None
                else ""
            )
            + "SELECT 1 AS id\n"
        )
        templater = DbtTemplater()
        templater.project_dir = templater.profiles_dir = str(project)
        templater.sqlfluff_config = FluffConfig(
            configs={"core": {"dialect": "bigquery", "templater": "dbt"}}
        )
        return templater, project

    try:
        yield make_project
    finally:
        registry.cleanup_connections()


@pytest.mark.parametrize("v2", [False, True])
@pytest.mark.parametrize("catalog_change", ["remove", "rename"])
def test__templater_dbt_catalogs_bigquery_manifest(
    bigquery_catalog_project, v2, catalog_change
):
    """Parse the reported project with a real BigQuery adapter, offline."""
    from dbt.adapters import factory

    templater, project = bigquery_catalog_project("first", v2)
    assert "model.example.my_model" in templater.dbt_manifest.nodes
    adapter = factory.get_adapter(templater.dbt_config)
    integration = adapter.get_catalog_integration("my_catalog")
    assert integration.external_volume == "gs://my-bucket"
    assert integration.file_format == "parquet"
    # New instances can load the same project through the shared adapter.
    other = DbtTemplater()
    other.project_dir = other.profiles_dir = str(project)
    other.sqlfluff_config = templater.sqlfluff_config
    assert "model.example.my_model" in other.dbt_manifest.nodes
    catalog_path = project / "catalogs.yml"
    if catalog_change == "remove":
        catalog_path.unlink()
    else:
        catalog_path.write_text(
            catalog_path.read_text().replace("my_catalog", "renamed_catalog")
        )
    changed = DbtTemplater()
    changed.project_dir = changed.profiles_dir = str(project)
    changed.sqlfluff_config = templater.sqlfluff_config
    with pytest.raises(SQLFluffUserError, match="different configuration"):
        _ = changed.dbt_manifest


@pytest.mark.parametrize("v2", [False, True])
@pytest.mark.parametrize("second_catalog", [None, "other_catalog", "my_catalog"])
def test__templater_dbt_catalogs_separate_projects(
    bigquery_catalog_project, monkeypatch, v2, second_catalog
):
    """Switch projects without leaking catalogs or losing same-project guards."""
    from dbt.adapters import factory
    from dbt.adapters.catalogs import DbtCatalogIntegrationNotFoundError

    first, first_project = bigquery_catalog_project("first", v2)
    assert "model.example.my_model" in first.dbt_manifest.nodes
    adapter = factory.get_adapter(first.dbt_config)
    original = adapter.get_catalog_integration("my_catalog")

    second, second_project = bigquery_catalog_project(
        "second", v2, second_catalog, "gs://other-bucket"
    )
    assert "model.example.my_model" in second.dbt_manifest.nodes
    assert factory.get_adapter(second.dbt_config) is adapter
    if second_catalog is not None:
        assert (
            adapter.get_catalog_integration(second_catalog).external_volume
            == "gs://other-bucket"
        )
    if second_catalog != "my_catalog":
        with pytest.raises(DbtCatalogIntegrationNotFoundError):
            adapter.get_catalog_integration("my_catalog")

    # Reuse the cached manifests and connections, as a long-lived API caller does.
    # Pre-populate connections to keep this BigQuery integration offline.
    monkeypatch.setattr(
        DbtTemplater,
        "adapters",
        {str(first_project): adapter, str(second_project): adapter},
    )
    with first.connection():
        assert adapter.get_catalog_integration("my_catalog") is original
        if second_catalog == "other_catalog":
            with pytest.raises(DbtCatalogIntegrationNotFoundError):
                adapter.get_catalog_integration("other_catalog")
    with second.connection():
        if second_catalog is not None:
            assert (
                adapter.get_catalog_integration(second_catalog).external_volume
                == "gs://other-bucket"
            )
        else:
            with pytest.raises(DbtCatalogIntegrationNotFoundError):
                adapter.get_catalog_integration("my_catalog")

    (first_project / "catalogs.yml").unlink()
    changed = DbtTemplater()
    changed.project_dir = changed.profiles_dir = str(first_project)
    changed.sqlfluff_config = first.sqlfluff_config
    with pytest.raises(SQLFluffUserError, match="different configuration"):
        _ = changed.dbt_manifest


@pytest.mark.parametrize("v2", [False, True])
@pytest.mark.parametrize(
    "project_name, catalog_name",
    [("second", None), ("second", "my_catalog"), ("first", "my_catalog")],
)
def test__templater_dbt_catalogs_after_dbt_parse(
    bigquery_catalog_project, v2, project_name, catalog_name
):
    """A prior dbt invocation must not seed SQLFluff's project catalogs."""
    from dbt.adapters import factory
    from dbt.adapters.catalogs import DbtCatalogIntegrationNotFoundError
    from dbt.cli.main import dbtRunner

    first, first_project = bigquery_catalog_project("first", v2)
    result = dbtRunner().invoke(
        [
            "parse",
            "--project-dir",
            str(first_project),
            "--profiles-dir",
            str(first_project),
            "--no-partial-parse",
        ]
    )
    assert result.success, result.exception
    adapter = factory.get_adapter(first.dbt_config)
    assert (
        adapter.get_catalog_integration("my_catalog").external_volume
        == "gs://my-bucket"
    )

    volume = "gs://my-bucket" if project_name == "first" else "gs://other-bucket"
    if project_name == "first":
        templater = first
    else:
        templater, _ = bigquery_catalog_project(project_name, v2, catalog_name, volume)
    assert "model.example.my_model" in templater.dbt_manifest.nodes
    assert factory.get_adapter(templater.dbt_config) is adapter
    if catalog_name is None:
        with pytest.raises(DbtCatalogIntegrationNotFoundError):
            adapter.get_catalog_integration("my_catalog")
    else:
        assert adapter.get_catalog_integration(catalog_name).external_volume == volume
