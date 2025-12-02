"""Marker to be imported and used in plugins (and for own implementations)."""

from typing import Any, Callable, TypeVar, cast

import pluggy

# Improvement suggested by @oremanj on python/typing gitter
F = TypeVar("F", bound=Callable[..., Any])

project_name = "sqlfluff"
plugin_base_name = f"{project_name}-plugin"
hookimpl = cast(Callable[[F], F], pluggy.HookimplMarker(plugin_base_name))
