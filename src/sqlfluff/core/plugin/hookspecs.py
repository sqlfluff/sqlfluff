"""Defines the specification to implement a plugin."""

from typing import List

import pluggy
from sqlfluff.core.plugin import plugin_base_name
from sqlfluff.core.rules.base import BaseCrawler

hookspec = pluggy.HookspecMarker(plugin_base_name)


@hookspec
def get_rules() -> List[BaseCrawler]:
    """Get plugin rules."""
