"""Defines the specification to implement a plugin."""

from abc import abstractmethod
from typing import TYPE_CHECKING, Any, Dict, List, Type

import pluggy

from sqlfluff.core.plugin import plugin_base_name

if TYPE_CHECKING:
    from sqlfluff.core.rules import BaseRule

hookspec = pluggy.HookspecMarker(plugin_base_name)


class PluginSpec:
    """Defines the method signatures for plugin implementations."""

    @hookspec
    @abstractmethod
    def get_rules(self) -> List[Type["BaseRule"]]:
        """Get plugin rules."""

    @hookspec
    @abstractmethod
    def load_default_config(self) -> Dict[str, Any]:
        """Loads the default configuration for the plugin."""

    @hookspec
    @abstractmethod
    # TODO: This type annotation could probably be more specific but that would
    # require making the config info object something more like a namedTuple rather
    # than a dict.
    def get_configs_info(self) -> Dict[str, Dict[str, Any]]:
        """Get rule config validations and descriptions."""
