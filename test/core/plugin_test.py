"""Plugin related tests."""
from sqlfluff.core.plugin.host import get_plugin_manager
from sqlfluff.core.config import FluffConfig


def test__plugin_manager_registers_example_plugin():
    """Test that the example plugin is registered."""
    plugin_manager = get_plugin_manager()
    # The plugin import order is non-deterministic
    assert sorted(
        [plugin_module.__name__ for plugin_module in plugin_manager.get_plugins()]
    ) == [
        "example.rules",
        "sqlfluff.core.plugin.lib",
    ]


def test__plugin_example_rules_returned():
    """Test that the example rules from the plugin are returned."""
    plugin_manager = get_plugin_manager()
    # The plugin import order is non-deterministic
    assert "Rule_Example_L001" in [
        rule.__name__ for rules in plugin_manager.hook.get_rules() for rule in rules
    ]


def test__plugin_default_config_read():
    """Test that the example plugin default config is merged into FluffConfig."""
    fluff_config = FluffConfig()
    # The plugin import order is non-deterministic
    assert "forbidden_columns" in fluff_config._configs["rules"]["Example_L001"]
