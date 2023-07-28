"""Defines the plugin manager getter."""
import pluggy
from typing import Optional

from sqlfluff.core.plugin.hookspecs import PluginSpec
from sqlfluff.core.plugin import plugin_base_name, project_name

_plugin_manager: Optional[pluggy.PluginManager] = None


def get_plugin_manager() -> pluggy.PluginManager:
    """Initializes the PluginManager.

    NOTE: We cache the plugin manager as a global to
    avoid reloading all the plugins each time.
    """
    global _plugin_manager
    if _plugin_manager:
        return _plugin_manager

    pm = pluggy.PluginManager(plugin_base_name)
    pm.add_hookspecs(PluginSpec)
    pm.load_setuptools_entrypoints(project_name)
    _plugin_manager = pm
    return pm
