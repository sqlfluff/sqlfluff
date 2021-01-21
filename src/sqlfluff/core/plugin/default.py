"""Base implementation for the plugin."""

from typing import List

import pluggy
from sqlfluff.core.plugin import plugin_base_name, hookimpl
from sqlfluff.core.rules.base import BaseCrawler
from sqlfluff.core.config import ConfigLoader

# No docstring here as it would appear in the rules docs.
# Rule definitions for the standard ruleset, dynamically imported from the directory.
# noqa

from sqlfluff.core.rules.std import get_rules_from_path
import os.path

hookspec = pluggy.HookspecMarker(plugin_base_name)


@hookimpl
def get_rules() -> List[BaseCrawler]:
    """Get plugin rules."""
    return get_rules_from_path()


@hookimpl
def load_default_config() -> dict:
    """Loads the default configuration for the plugin."""
    return ConfigLoader.get_global().load_default_config_file(
        file_dir=os.path.join(os.path.dirname(os.path.dirname(__file__))),
        file_name="default_config.cfg",
    )
