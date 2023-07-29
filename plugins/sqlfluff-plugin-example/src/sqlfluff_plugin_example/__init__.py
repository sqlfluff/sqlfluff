"""An example of a custom rule implemented through the plugin system.

This uses the rules API supported from 0.4.0 onwards.
"""

from sqlfluff.core.plugin import hookimpl
from sqlfluff.core.rules import BaseRule
from typing import List, Type
import os.path
from sqlfluff.core.config import ConfigLoader


@hookimpl
def get_rules() -> List[Type[BaseRule]]:
    """Get plugin rules.

    NOTE: It is important that we only import the rule on demand.
    The root module of the plugin (i.e. this file which contains
    all of the hook implementations) must have fully loaded before
    we try and import the rules. This is partly for performance
    reasons - but more because the definition of a BaseRule requires
    that all of the get_configs_info() methods have both been
    defined _and have run_ before so all the validation information
    is available for the validation steps in the meta class.
    """
    from sqlfluff_plugin_example.rules import Rule_Example_L001

    return [Rule_Example_L001]


@hookimpl
def load_default_config() -> dict:
    """Loads the default configuration for the plugin."""
    return ConfigLoader.get_global().load_config_file(
        file_dir=os.path.dirname(__file__),
        file_name="plugin_default_config.cfg",
    )


@hookimpl
def get_configs_info() -> dict:
    """Get rule config validations and descriptions."""
    return {
        "forbidden_columns": {"definition": "A list of column to forbid"},
    }
