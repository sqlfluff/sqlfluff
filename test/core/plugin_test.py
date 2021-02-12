"""Plugin related tests."""
from sqlfluff.core.plugin.host import get_plugin_manager

def test__plugin_manager_registers_example_plugin():
    """Test that the example plugin is registered."""
    plugin_manager = get_plugin_manager()
    # The plugin import order is non-deterministic
    assert sorted([
        plugin_module.__name__ for plugin_module in plugin_manager.get_plugins()
    ]) == [
        "example",
        "sqlfluff.core.plugin.lib",
    ]
