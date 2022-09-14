"""Methods to set up appropriate reflow config from file."""


# Until we have a proper structure this will work.
# TODO: Migrate this to the config file.
from dataclasses import dataclass
from typing import Dict, Set

from sqlfluff.core.config import FluffConfig

ConfigElementType = Dict[str, str]
ConfigDictType = Dict[str, ConfigElementType]


@dataclass(frozen=True)
class ReflowConfig:
    """An interface onto the configuration of how segments should reflow.

    This acts as the primary translation engine between configuration
    held either in dicts for testing, or in the FluffConfig in live
    usage, and the configuration used during reflow operations.
    """

    _config_dict: ConfigDictType
    config_types: Set[str]

    @classmethod
    def from_dict(cls, config_dict: ConfigDictType):
        """Construct a ReflowConfig from a dict."""
        config_types = set(config_dict.keys())
        return cls(_config_dict=config_dict, config_types=config_types)

    @classmethod
    def from_fluff_config(cls, config: FluffConfig):
        """Constructs a ReflowConfig from a FluffConfig."""
        return cls.from_dict(config.get_section(["layout", "type"]))

    def get_block_config(self, point_class_types: Set[str]):
        """Given the class types of a ReflowBlock return spacing config."""
        # set intersection to get the class types which matter
        configured_types = point_class_types.intersection(self.config_types)
        # Start with a default config.
        block_config = {
            "spacing_before": "single",
            "spacing_after": "single",
            "spacing_within": None,
        }
        # Update with the config from any specific classes.
        # Unless someone is doing something complicated with their configuration
        # there should only be one.
        # TODO: Extend (or at least harden) this code to handle multiple
        # configured (and matched) types much better.
        for seg_type in configured_types:
            # The default is the existing value in both cases.
            block_config["spacing_after"] = self._config_dict[seg_type].get(
                "spacing_after", block_config["spacing_after"]
            )
            block_config["spacing_before"] = self._config_dict[seg_type].get(
                "spacing_before", block_config["spacing_before"]
            )
            block_config["spacing_within"] = self._config_dict[seg_type].get(
                "spacing_within", block_config["spacing_within"]
            )
        return block_config
