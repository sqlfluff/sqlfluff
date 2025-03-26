"""Defines the specification to implement a plugin."""

from abc import abstractmethod
from typing import TYPE_CHECKING, Any

import pluggy

from sqlfluff.core.plugin import plugin_base_name

if TYPE_CHECKING:  # pragma: no cover
    # NOTE: This import is against the normal import rules, but is here for strict
    # type checking. We have an exception for this in the import linter.
    from sqlfluff.core.rules.base import BaseRule

hookspec = pluggy.HookspecMarker(plugin_base_name)


class PluginSpec:
    """Defines the method signatures for plugin implementations."""

    @hookspec
    @abstractmethod
    def get_rules(self) -> list[type["BaseRule"]]:
        """Get plugin rules."""

    @hookspec
    @abstractmethod
    def load_default_config(self) -> dict[str, Any]:
        """Loads the default configuration for the plugin."""

    @hookspec
    @abstractmethod
    # TODO: This type annotation could probably be more specific but that would
    # require making the config info object something more like a namedTuple rather
    # than a dict.
    def get_configs_info(self) -> dict[str, dict[str, Any]]:
        """Get rule config validations and descriptions."""
