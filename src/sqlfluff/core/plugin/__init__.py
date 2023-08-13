"""Marker to be imported and used in plugins (and for own implementations)."""
import pluggy
from typing import TypeVar, Callable, Any, cast

# Improvement suggested by @oremanj on python/typing gitter
F = TypeVar("F", bound=Callable[..., Any])

project_name = "sqlfluff"
plugin_base_name = f"{project_name}-plugin"
hookimpl = cast(Callable[[F], F], pluggy.HookimplMarker(plugin_base_name))
