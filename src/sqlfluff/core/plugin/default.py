"""Base implementation for the plugin."""

from typing import List

import pluggy
from sqlfluff.core.plugin import plugin_base_name
from sqlfluff.core.rules.base import BaseCrawler
from sqlfluff.core.plugin import hookimpl

# No docstring here as it would appear in the rules docs.
# Rule definitions for the standard ruleset, dynamically imported from the directory.
# noqa

from sqlfluff.core.rules.std import get_rules_from_path

hookspec = pluggy.HookspecMarker(plugin_base_name)


@hookimpl
def get_rules() -> List[BaseCrawler]:
    """Get plugin rules."""
    return get_rules_from_path()
