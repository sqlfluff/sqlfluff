"""Defines the plugin manager getter."""
import pluggy

from sqlfluff.core.plugin.hookspecs import PluginSpec
from sqlfluff.core.plugin import plugin_base_name, project_name


def get_plugin_manager() -> pluggy.PluginManager:
    """Initializes the PluginManager."""
    pm = pluggy.PluginManager(plugin_base_name)
    pm.add_hookspecs(PluginSpec)
    pm.load_setuptools_entrypoints(project_name)
    return pm
