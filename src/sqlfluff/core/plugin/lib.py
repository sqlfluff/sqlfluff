"""Base implementation for the plugin."""

import os.path

from typing import List, Type

from sqlfluff.core.config import ConfigLoader
from sqlfluff.core.plugin import hookimpl
from sqlfluff.core.rules.config_info import STANDARD_CONFIG_INFO_DICT
from sqlfluff.core.rules.loader import get_rules_from_path
from sqlfluff.core.rules import BaseRule
from sqlfluff.core.templaters import core_templaters, RawTemplater


@hookimpl
def get_rules() -> List[Type[BaseRule]]:
    """Get plugin rules.

    NOTE: All standard rules will eventually be loaded as
    plugins and so before 2.0.0, once all legacy plugin definitions
    are migrated, this function will be amended to return no rules.
    """
    return get_rules_from_path()


@hookimpl
def get_templaters() -> List[Type[RawTemplater]]:
    """Get templaters."""
    return core_templaters()


@hookimpl
def load_default_config() -> dict:
    """Loads the default configuration for the plugin."""
    return ConfigLoader.get_global().load_config_file(
        file_dir=os.path.join(os.path.dirname(os.path.dirname(__file__))),
        file_name="default_config.cfg",
    )


@hookimpl
def get_configs_info() -> dict:
    """Get rule config validations and descriptions."""
    return STANDARD_CONFIG_INFO_DICT
