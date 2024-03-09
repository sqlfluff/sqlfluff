"""Defines the plugin manager getter.

NOTE: The plugin manager will load all of the plugins on
the first pass. Each plugin will also load the plugin
manager on load to register themselves. To ensure this is
as performant as possible, we cache the plugin manager within
the context of each thread.
"""

import importlib.metadata
import logging
from contextvars import ContextVar
from typing import Iterator, Optional, Tuple

import pluggy

from sqlfluff.core.plugin import plugin_base_name, project_name
from sqlfluff.core.plugin.hookspecs import PluginSpec

plugin_logger = logging.getLogger("sqlfluff.plugin")

_plugin_manager: ContextVar[Optional[pluggy.PluginManager]] = ContextVar(
    "_plugin_manager", default=None
)
plugins_loaded: ContextVar[bool] = ContextVar("plugins_loaded", default=False)
# NOTE: The is_main_process context var is defined here, but
# we rely on each parallel runner (found in `runner.py`) to
# maintain the value of this variable.
is_main_process: ContextVar[bool] = ContextVar("is_main_process", default=True)


def _get_sqlfluff_version() -> str:
    """Get the SQLFluff package version from importlib.

    NOTE: At the stage of loading plugins, SQLFluff isn't fully
    initialised and so we can't use the normal methods.
    """
    return importlib.metadata.version("sqlfluff")


def _discover_plugins() -> Iterator[Tuple[importlib.metadata.EntryPoint, str, str]]:
    """Uses the same mechanism as pluggy to introspect available plugins.

    This method is then intended to allow loading of plugins individually,
    for better error handling.
    """
    for dist in list(importlib.metadata.distributions()):
        for ep in dist.entry_points:
            # Check it's a SQLFluff one
            if ep.group != project_name:
                continue
            yield ep, ep.name, dist.version


def _load_plugin(
    plugin_manager: pluggy.PluginManager,
    entry_point: importlib.metadata.EntryPoint,
    plugin_name: str,
    plugin_version: str,
) -> None:
    """Loads a single plugin with a bit of error handling."""
    # NOTE: If the plugin is already loaded, then .register() will fail,
    # so it's important that we check whether it's loaded at this point.
    if plugin_manager.get_plugin(plugin_name):  # pragma: no cover
        plugin_logger.info("...already loaded")
        return None
    try:
        plugin = entry_point.load()
    except Exception as err:
        plugin_logger.error(
            "ERROR: Failed to load SQLFluff plugin "
            f"{plugin_name} version {plugin_version}. "
            "Check your packages are compatible with the current SQLFluff version "
            f"({_get_sqlfluff_version()})."
            f"\n\n    {err!r}\n\n"
        )
        return None
    plugin_manager.register(plugin, name=plugin_name)
    return None


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

    # Discover available plugins and load them individually.
    # If any fail, log the issue and carry on.
    for entry_point, plugin_name, plugin_version in _discover_plugins():
        plugin_logger.info(f"Loading plugin {plugin_name} version {plugin_version}.")
        _load_plugin(plugin_manager, entry_point, plugin_name, plugin_version)

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
