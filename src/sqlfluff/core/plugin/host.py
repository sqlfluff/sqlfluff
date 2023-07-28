"""Defines the plugin manager getter.

NOTE: The plugin manager will load all of the plugins on
the first pass. Each plugin will also load the plugin
manager on load to register themselves. To ensure this is
as performant as possible, we cache the plugin manager within
the context of each thread.
"""

from contextvars import ContextVar
import pluggy

from sqlfluff.core.plugin.hookspecs import PluginSpec
from sqlfluff.core.plugin import plugin_base_name, project_name

_plugin_manager = ContextVar("_plugin_manager", default=None)


def get_plugin_manager() -> pluggy.PluginManager:
    """Initializes the PluginManager.

    NOTE: We cache the plugin manager as a global to
    avoid reloading all the plugins each time.
    """
    plugin_manager = _plugin_manager.get()
    if plugin_manager:
        return plugin_manager
    plugin_manager = pluggy.PluginManager(plugin_base_name)
    plugin_manager.add_hookspecs(PluginSpec)

    # NOTE: We set the plugin manager before loading the
    # entrypoints. This is because when we load the entry
    # points, this function gets called again - and we only
    # want to load the entry points once!
    _plugin_manager.set(plugin_manager)
    print(f"get_plugin_manager LOADING ENTRY POINTS")
    plugin_manager.load_setuptools_entrypoints(project_name)
    return plugin_manager
