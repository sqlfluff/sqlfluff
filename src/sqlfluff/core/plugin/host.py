"""Defines the plugin manager getter.

NOTE: The plugin manager will load all of the plugins on
the first pass. Each plugin will also load the plugin
manager on load to register themselves. To ensure this is
as performant as possible, we cache the plugin manager within
the context of each thread.
"""

from contextvars import ContextVar
from typing import Optional

import pluggy

from sqlfluff.core.plugin import plugin_base_name, project_name
from sqlfluff.core.plugin.hookspecs import PluginSpec

_plugin_manager: ContextVar[Optional[pluggy.PluginManager]] = ContextVar(
    "_plugin_manager", default=None
)
plugins_loaded: ContextVar[bool] = ContextVar("plugins_loaded", default=False)
# NOTE: The is_main_process context var is defined here, but
# we rely on each parallel runner (found in `runner.py`) to
# maintain the value of this variable.
is_main_process: ContextVar[bool] = ContextVar("is_main_process", default=True)


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
    plugin_manager.load_setuptools_entrypoints(project_name)

    # Once plugins are loaded we set a second context var
    # to indicate that loading is complete. Other parts of
    # the codebase can use this to detect whether it's safe.
    plugins_loaded.set(True)

    return plugin_manager


def purge_plugin_manager() -> None:
    """Purge the current loaded plugin manager.

    NOTE: This method should not be used in normal SQFluff
    operation, but exists so that in the test suite we can
    reliably clear the cached plugin manager and force
    plugins to be reload.
    """
    # Reset back to defaults.
    _plugin_manager.set(None)
    plugins_loaded.set(False)
