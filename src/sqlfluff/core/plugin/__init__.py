"""Marker to be imported and used in plugins (and for own implementations)."""
import pluggy

project_name = "sqlfluff"
plugin_base_name = f"{project_name}-plugin"
hookimpl = pluggy.HookimplMarker(plugin_base_name)
