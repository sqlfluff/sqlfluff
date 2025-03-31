"""Base implementation for the plugin."""

from typing import Any

from sqlfluff.core.config import load_config_resource
from sqlfluff.core.plugin import hookimpl
from sqlfluff.core.rules import BaseRule, ConfigInfo
from sqlfluff.core.rules.config_info import STANDARD_CONFIG_INFO_DICT
from sqlfluff.core.rules.loader import get_rules_from_path
from sqlfluff.core.templaters import RawTemplater, core_templaters


@hookimpl
def get_rules() -> list[type[BaseRule]]:
    """Get plugin rules.

    NOTE: All standard rules will eventually be loaded as
    plugins and so before 2.0.0, once all legacy plugin definitions
    are migrated, this function will be amended to return no rules.
    """
    return get_rules_from_path()


@hookimpl
def get_templaters() -> list[type[RawTemplater]]:
    """Get templaters."""
    templaters = list(t for t in core_templaters())
    return templaters


@hookimpl
def load_default_config() -> dict[str, Any]:
    """Loads the default configuration for the plugin."""
    return load_config_resource(
        package="sqlfluff.core",
        file_name="default_config.cfg",
    )


@hookimpl
def get_configs_info() -> dict[str, ConfigInfo]:
    """Get rule config validations and descriptions."""
    return STANDARD_CONFIG_INFO_DICT
