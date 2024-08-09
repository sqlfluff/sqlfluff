"""Plugin related tests."""

import importlib.metadata
import logging
import sys

import pytest

from sqlfluff import __version__ as pkg_version
from sqlfluff.core.config import FluffConfig
from sqlfluff.core.plugin.host import (
    _get_sqlfluff_version,
    _load_plugin,
    get_plugin_manager,
    purge_plugin_manager,
)
from sqlfluff.utils.testing.logging import fluff_log_catcher


def test__plugin_manager_registers_example_plugin():
    """Test that the example plugin is registered.

    This test also tests that warnings are raised on the import of
    plugins which have their imports in the wrong place (e.g. the
    example plugin). That means we need to make sure the plugin is
    definitely reimported at the start of this test, so we can see
    any warnings raised on imports.

    To do this we clear the plugin manager cache and also forcibly
    unload the example plugin modules if they are already loaded.
    This ensures that we can capture any warnings raised by importing the
    module.
    """
    purge_plugin_manager()
    # We still to a try/except here, even though it's only run within
    # the context of a test because the module may or may not already
    # be imported depending on the order that the tests run in.
    try:
        del sys.modules["sqlfluff_plugin_example"]
    except KeyError:
        pass
    try:
        del sys.modules["sqlfluff_plugin_example.rules"]
    except KeyError:
        pass

    with fluff_log_catcher(logging.WARNING, "sqlfluff.rules") as caplog:
        plugin_manager = get_plugin_manager()
        # The plugin import order is non-deterministic.
        # Use sets in case the dbt plugin (or other plugins) are
        # already installed too.
        installed_plugins = set(
            plugin_module.__name__ for plugin_module in plugin_manager.get_plugins()
        )

    print(f"Installed plugins: {installed_plugins}")
    assert installed_plugins.issuperset(
        {
            "sqlfluff_plugin_example",
            "sqlfluff.core.plugin.lib",
        }
    )

    # At this stage we should also check that the example plugin
    # also raises a warning for it's import location.
    assert (
        "Rule 'Rule_Example_L001' has been imported before all plugins "
        "have been fully loaded"
    ) in caplog.text


@pytest.mark.parametrize(
    "rule_ref",
    # Check both V1 plugin
    ["Rule_Example_L001"],
)
def test__plugin_example_rules_returned(rule_ref):
    """Test that the example rules from the plugin are returned."""
    plugin_manager = get_plugin_manager()
    # The plugin import order is non-deterministic
    rule_names = [
        rule.__name__ for rules in plugin_manager.hook.get_rules() for rule in rules
    ]
    print(f"Rule names: {rule_names}")
    assert rule_ref in rule_names


@pytest.mark.parametrize(
    "rule_ref,config_option",
    # Check both V1 and V2 rule plugins.
    [("Example_L001", "forbidden_columns")],
)
def test__plugin_default_config_read(rule_ref, config_option):
    """Test that the example plugin default config is merged into FluffConfig."""
    fluff_config = FluffConfig(overrides={"dialect": "ansi"})
    # The plugin import order is non-deterministic
    print(f"Detected config sections: {fluff_config._configs['rules'].keys()}")
    # Check V1
    assert config_option in fluff_config._configs["rules"][rule_ref]


class MockEntryPoint(importlib.metadata.EntryPoint):
    """Fake Entry Point which just raises an exception on load."""

    def load(self):
        """Raise an exception on load."""
        raise ValueError("TEST ERROR")


def test__plugin_handle_bad_load():
    """Test that we can safely survive a plugin which fails to load."""
    # Mock fake plugin
    ep = MockEntryPoint("test_name", "test_value", "sqlfluff")

    plugin_manager = get_plugin_manager()
    with fluff_log_catcher(logging.WARNING, "sqlfluff.plugin") as caplog:
        _load_plugin(plugin_manager, ep, "plugin_name", "v1.2.3")
    # Assert that there was a warning
    assert "ERROR: Failed to load SQLFluff plugin" in caplog.text
    assert "plugin_name" in caplog.text
    assert "TEST ERROR" in caplog.text


def test__plugin_get_version():
    """Test the plugin method of getting the version gets the right version."""
    assert _get_sqlfluff_version() == pkg_version
