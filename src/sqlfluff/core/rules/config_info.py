"""Documenting and validating rule configuration.

Provide a mapping with default configuration options, which are common
to multiple rules with information on valid inputs and definitions.

This mapping is used to validate rule config inputs, as well
as document rule configuration.

It is assumed that most rule bundles will define their own additional
sets of these which should be defined within that bundle rather than
here. Unless your config value is used across multiple bundles, or is
of more general wider use - please define it in the specific plugin
rather than here.
"""

from typing import Optional, TypedDict, Union

from sqlfluff.core.plugin.host import get_plugin_manager


class ConfigInfo(TypedDict, total=False):
    """Type definition for a single config info value.

    This TypedDict defines the structure for configuration information used across
    SQLFluff rules. Each config value must have a definition, and may optionally
    include validation criteria.

    Args:
        definition: Required string containing a detailed description of the config
            option and its purpose. This should be clear enough for users to
            understand when and how to use the config.
        validation: Optional list or range of valid values for the config option.
            Can contain boolean, string, or integer values. If not provided,
            the config option accepts any value of its expected type.
    """

    definition: str
    # NOTE: This type hint is a bit ugly, but necessary for now.
    # TODO: Tidy this up when we drop support for 3.9.
    validation: Optional[Union[list[Union[bool, str, int]], range]]


STANDARD_CONFIG_INFO_DICT: dict[str, ConfigInfo] = {
    "force_enable": {
        "validation": [True, False],
        "definition": (
            "Run this rule even for dialects where this rule is disabled by default."
        ),
    },
    "ignore_words": {
        "definition": ("Comma separated list of words to ignore from rule"),
    },
    "ignore_words_regex": {
        "definition": (
            "Words to ignore from rule if they are a partial match for the regular "
            "expression. To ignore only full matches you can use ``^`` (beginning "
            "of text) and ``$`` (end of text). Due to regular expression operator "
            "precedence, it is good practice to use parentheses around everything "
            "between ``^`` and ``$``."
        ),
    },
    "blocked_words": {
        "definition": (
            "Optional, comma-separated list of blocked words which should not be used "
            "in statements."
        ),
    },
    "blocked_regex": {
        "definition": (
            "Optional, regex of blocked pattern which should not be used in statements."
        ),
    },
    "match_source": {
        "definition": (
            "Optional, also match regex of blocked pattern before applying templating"
        ),
    },
    "case_sensitive": {
        "validation": [True, False],
        "definition": (
            "If ``False``, comparison is done case in-sensitively. "
            "Defaults to ``True``."
        ),
    },
}


def get_config_info() -> dict[str, ConfigInfo]:
    """Get the config from core sqlfluff and sqlfluff plugins and merges them.

    NOTE: This should be the entry point into getting config info rather than
    importing the default set above, as many values are defined only in rule
    packages.
    """
    plugin_manager = get_plugin_manager()
    configs_info = plugin_manager.hook.get_configs_info()
    return {
        k: v for config_info_dict in configs_info for k, v in config_info_dict.items()
    }
