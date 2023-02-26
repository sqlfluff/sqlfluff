"""Plugin related tests."""
import pytest

from sqlfluff.core.plugin.host import get_plugin_manager
from sqlfluff.core.config import FluffConfig


def test__plugin_manager_registers_example_plugin():
    """Test that the example plugin is registered."""
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
            # Check that both the v1 and v2 example are correctly
            # installed.
            "example.rules",
            "sqlfluff.core.plugin.lib",
        }
    )


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
