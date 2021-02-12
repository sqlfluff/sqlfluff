"""Base implementation for the plugin."""

import os.path
from sqlfluff.core.config import ConfigLoader
from sqlfluff.core.plugin import hookimpl
from sqlfluff.core.rules.config_info import STANDARD_CONFIG_INFO_DICT
from sqlfluff.core.rules.std import get_rules_from_path


@hookimpl
def get_rules():
    """Get plugin rules."""
    return get_rules_from_path()


@hookimpl
def load_default_config() -> dict:
    """Loads the default configuration for the plugin."""
    return ConfigLoader.get_global().load_default_config_file(
        file_dir=os.path.join(os.path.dirname(os.path.dirname(__file__))),
        file_name="default_config.cfg",
    )


@hookimpl
def get_configs_info() -> dict:
    """Get rule config validations and descriptions."""
    return STANDARD_CONFIG_INFO_DICT
