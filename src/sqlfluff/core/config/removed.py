"""Records of deprecated and removed config variables."""

import logging
from dataclasses import dataclass
from typing import Callable, Optional, Union

from sqlfluff.core.errors import SQLFluffUserError
from sqlfluff.core.helpers.dict import (
    NestedStringDict,
    nested_dict_get,
    nested_dict_set,
    records_to_nested_dict,
)
from sqlfluff.core.types import ConfigMappingType, ConfigValueOrListType

# Instantiate the config logger
config_logger = logging.getLogger("sqlfluff.config")


@dataclass
class _RemovedConfig:
    old_path: tuple[str, ...]
    warning: str
    new_path: Optional[tuple[str, ...]] = None
    translation_func: Optional[
        Callable[[ConfigValueOrListType], ConfigValueOrListType]
    ] = None

    @property
    def formatted_old_key(self) -> str:
        """Format the old key in a way similar to a config file."""
        return ":".join(self.old_path)

    @property
    def formatted_new_key(self) -> str:
        """Format the new key (assuming it exists) in a way similar to a config file."""
        assert (
            self.new_path
        ), "`formatted_new_key` can only be called if a `new_path` is set."
        return ":".join(self.new_path)


RemovedConfigMapType = dict[str, Union[_RemovedConfig, "RemovedConfigMapType"]]


REMOVED_CONFIGS = [
    _RemovedConfig(
        ("rules", "L003", "hanging_indents"),
        (
            "Hanging indents are no longer supported in SQLFluff "
            "from version 2.0.0 onwards. See "
            "https://docs.sqlfluff.com/en/stable/perma/hanging_indents.html"
        ),
    ),
    _RemovedConfig(
        ("rules", "max_line_length"),
        (
            "The max_line_length config has moved "
            "from sqlfluff:rules to the root sqlfluff level."
        ),
        ("max_line_length",),
        (lambda x: x),
    ),
    _RemovedConfig(
        ("rules", "tab_space_size"),
        (
            "The tab_space_size config has moved "
            "from sqlfluff:rules to sqlfluff:indentation."
        ),
        ("indentation", "tab_space_size"),
        (lambda x: x),
    ),
    _RemovedConfig(
        ("rules", "L002", "tab_space_size"),
        (
            "The tab_space_size config has moved "
            "from sqlfluff:rules to sqlfluff:indentation."
        ),
        ("indentation", "tab_space_size"),
        (lambda x: x),
    ),
    _RemovedConfig(
        ("rules", "L003", "tab_space_size"),
        (
            "The tab_space_size config has moved "
            "from sqlfluff:rules to sqlfluff:indentation."
        ),
        ("indentation", "tab_space_size"),
        (lambda x: x),
    ),
    _RemovedConfig(
        ("rules", "L004", "tab_space_size"),
        (
            "The tab_space_size config has moved "
            "from sqlfluff:rules to sqlfluff:indentation."
        ),
        ("indentation", "tab_space_size"),
        (lambda x: x),
    ),
    _RemovedConfig(
        ("rules", "L016", "tab_space_size"),
        (
            "The tab_space_size config has moved "
            "from sqlfluff:rules to sqlfluff:indentation."
        ),
        ("indentation", "tab_space_size"),
        (lambda x: x),
    ),
    _RemovedConfig(
        ("rules", "indent_unit"),
        (
            "The indent_unit config has moved "
            "from sqlfluff:rules to sqlfluff:indentation."
        ),
        ("indentation", "indent_unit"),
        (lambda x: x),
    ),
    _RemovedConfig(
        ("rules", "LT03", "operator_new_lines"),
        (
            "Use the line_position config in the appropriate "
            "sqlfluff:layout section (e.g. sqlfluff:layout:type"
            ":binary_operator)."
        ),
        ("layout", "type", "binary_operator", "line_position"),
        (lambda x: "trailing" if x == "before" else "leading"),
    ),
    _RemovedConfig(
        ("rules", "comma_style"),
        (
            "Use the line_position config in the appropriate "
            "sqlfluff:layout section (e.g. sqlfluff:layout:type"
            ":comma)."
        ),
        ("layout", "type", "comma", "line_position"),
        (lambda x: x),
    ),
    # LT04 used to have a more specific version of the same /config itself.
    _RemovedConfig(
        ("rules", "LT04", "comma_style"),
        (
            "Use the line_position config in the appropriate "
            "sqlfluff:layout section (e.g. sqlfluff:layout:type"
            ":comma)."
        ),
        ("layout", "type", "comma", "line_position"),
        (lambda x: x),
    ),
    _RemovedConfig(
        ("rules", "L003", "lint_templated_tokens"),
        "No longer used.",
    ),
    _RemovedConfig(
        ("core", "recurse"),
        "Removed as unused in production and unnecessary for debugging.",
    ),
    _RemovedConfig(
        ("rules", "references.quoting", "force_enable"),
        "No longer used. The dialects which used to block this rule, no longer do.",
    ),
]

# Actually make a dict which matches the structure.
REMOVED_CONFIG_MAP = records_to_nested_dict(
    (removed_config.old_path, removed_config) for removed_config in REMOVED_CONFIGS
)


def validate_config_dict_for_removed(
    config: ConfigMappingType,
    logging_reference: str,
    removed_config: NestedStringDict[_RemovedConfig] = REMOVED_CONFIG_MAP,
    root_config_ref: Optional[ConfigMappingType] = None,
) -> None:
    """Validates a config dict against removed values.

    Where a value can be updated or translated, it mutates the config object.

    In general the `removed_config` & `root_config_ref` arguments are present
    only to enable recursion and shouldn't be necessary for general use of this
    function.
    """
    # If no root ref provided, then assume it's the config provided.
    # NOTE: During recursion, this should be set explicitly.
    root_config_ref = root_config_ref or config

    # Iterate through a copy of the config keys, so we can safely mutate
    # the underlying dict.
    for key in list(config.keys()):
        # Is there a removed config to compare to?
        if key not in removed_config:
            continue
        removed_value = removed_config[key]

        # If it's a section, recurse
        if isinstance(removed_value, dict):
            config_section = config[key]
            assert isinstance(
                config_section, dict
            ), f"Expected `{key}` to be a section not a value."
            validate_config_dict_for_removed(
                config_section,
                logging_reference=logging_reference,
                removed_config=removed_value,
                root_config_ref=root_config_ref,
            )
            # If that validation resulted in an empty dict, also remove
            # the reference in this layer.
            if not config_section:
                del config[key]
            continue

        # Otherwise handle it directly.
        assert isinstance(removed_value, _RemovedConfig)

        # If there isn't a mapping option, just raise an error
        if not (removed_value.translation_func and removed_value.new_path):
            raise SQLFluffUserError(
                f"Config file {logging_reference!r} set an outdated config "
                f"value {removed_value.formatted_old_key}."
                f"\n\n{removed_value.warning}\n\n"
                "See https://docs.sqlfluff.com/en/stable/perma/"
                "configuration.html for more details."
            )

        # Otherwise perform the translation.
        # First check whether we have already set the new path?
        try:
            # Try and fetch a value at the new path.
            # NOTE: We don't actually handle the return value.
            nested_dict_get(root_config_ref, removed_value.new_path)
            # Raise an warning.
            config_logger.warning(
                f"\nWARNING: Config file {logging_reference} set a deprecated "
                f"config value `{removed_value.formatted_old_key}` (which can be "
                "migrated) but ALSO set the value it would be migrated to. The new "
                f"value (`{removed_value.formatted_new_key}`) takes precedence. "
                "Please update your configuration to remove this warning. "
                f"\n\n{removed_value.warning}\n\n"
                "See https://docs.sqlfluff.com/en/stable/perma/"
                "configuration.html for more details.\n"
            )
            # Remove the corresponding value from the dict object as invalid.
            del config[key]
            continue
        except KeyError:
            pass

        # If we haven't already set the new path then mutate and warn.
        old_value = config[key]
        assert not isinstance(
            old_value, dict
        ), f"Expected `{key}` to be a value not a section."
        new_value = removed_value.translation_func(old_value)
        # NOTE: At the stage of emitting this warning, we may not yet
        # have set up red logging because we haven't yet loaded the config
        # file. For that reason, this error message has a bit more padding.
        config_logger.warning(
            f"\nWARNING: Config file {logging_reference} set a deprecated config "
            f"value `{removed_value.formatted_old_key}`. This will be "
            "removed in a later release. This has been mapped to "
            f"`{removed_value.formatted_new_key}` set to a value of "
            f"{new_value!r} for this run. "
            "Please update your configuration to remove this warning. "
            f"\n\n{removed_value.warning}\n\n"
            "See https://docs.sqlfluff.com/en/stable/perma/"
            "configuration.html for more details.\n"
        )
        # Write the new value and delete the old
        nested_dict_set(root_config_ref, removed_value.new_path, new_value)
        del config[key]
