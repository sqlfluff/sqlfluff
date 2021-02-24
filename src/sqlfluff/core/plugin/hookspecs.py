"""Defines the specification to implement a plugin."""

import pluggy
from sqlfluff.core.plugin import plugin_base_name

hookspec = pluggy.HookspecMarker(plugin_base_name)


class PluginSpec:
    """Defines the method signatures for plugin implementations."""

    @hookspec
    def get_rules(self):
        """Get plugin rules."""

    def load_default_config(self) -> dict:
        """Loads the default configuration for the plugin."""

    @hookspec
    def get_configs_info(self) -> dict:
        """Get rule config validations and descriptions."""
