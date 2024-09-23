"""Defines the specification to implement a plugin."""

from abc import abstractmethod
from typing import Any, Dict, List, Type

import pluggy

from sqlfluff.core.plugin import plugin_base_name
from sqlfluff.core.types import RuleType

hookspec = pluggy.HookspecMarker(plugin_base_name)


class PluginSpec:
    """Defines the method signatures for plugin implementations."""

    @hookspec
    @abstractmethod
    def get_rules(self) -> List[Type[RuleType]]:
        """Get plugin rules.

        NOTE: While the type annotation for this method returns `Type[RuleType]`
        all plugin implementations should instead import `sqlfluff.core.rules` and
        return the more specific `Type[BaseRule]`. This base definition of the
        PluginSpec cannot import that yet as it would cause a circular import.
        """

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
