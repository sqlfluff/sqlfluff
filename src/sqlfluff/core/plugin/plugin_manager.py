"""Integrates the plugins with sqlfluff."""

from pluggy import PluginManager
from sqlfluff.core.plugin import default, hookspecs, plugin_base_name, project_name


def get_plugin_manager() -> PluginManager:
    """Initializes the PluginManager."""
    pm = PluginManager(plugin_base_name)
    pm.add_hookspecs(hookspecs)
    pm.load_setuptools_entrypoints(project_name)
    pm.register(default)
    return pm
