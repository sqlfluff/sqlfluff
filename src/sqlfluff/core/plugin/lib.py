"""Base implementation for the plugin."""

import pluggy
import os.path
from sqlfluff.core.plugin import hookimpl

class Plugin:
    @hookimpl
    def get_rules(self):
        """Get plugin rules."""
        from sqlfluff.core.rules.std import get_rules_from_path

        return get_rules_from_path()


    @hookimpl
    def load_default_config(self) -> dict:
        """Loads the default configuration for the plugin."""
        from sqlfluff.core.config import ConfigLoader

        return ConfigLoader.get_global().load_default_config_file(
            file_dir=os.path.join(os.path.dirname(os.path.dirname(__file__))),
            file_name="default_config.cfg",
        )


    @hookimpl
    def get_configs_info(self) -> dict:
        """Get rule config validations and descriptions."""
        from sqlfluff.core.rules.config_info import STANDARD_CONFIG_INFO_DICT

        return STANDARD_CONFIG_INFO_DICT

