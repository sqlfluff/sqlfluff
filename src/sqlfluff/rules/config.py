"""Documenting and validating rule configuration.

Provide a mapping with all configuration options, with information
on valid inputs, default value, and definitions.

This mapping is used to validate rule config inputs, as well
as document rule configuration.
"""

from ..config import ConfigLoader


def create_config_info_dict():
    """Create a dictionary with all necessary rule configuration information."""
    # Initialize the dictionary with information that needs to
    # be coded manually
    config_info_dict = {
        "tab_space_size": {
            "validation": range(100),
            "definition": (
                "The number of spaces to consider equal to one tab. "
                "Used in the fixing step of this rule"
            )
        },
        "max_line_length": {
            "validation": range(1000),
            "definition": (
                "The maximum length of a line to allow without "
                "raising a violation"
            )
        },
        "indent_unit": {
            "validation": ["space", "tab"],
            "definition": "Whether to use tabs or spaces to add new indents"
        },
        "comma_style": {
            "validation": ["leading", "trailing"],
            "definition": "The comma style to to enforce"
        },
        "allow_scalar": {
            "validation": [True, False],
            "definition": (
                "Whether or not to allow a single element in the "
                " select clause to be without an alias"
            )
        },
        "single_table_references": {
            "validation": ["consistent", "qualified", "unqualified"],
            "definition": "The expectation for references in single-table select"
        },
        "only_aliases": {
            "validation": [True, False],
            "definition": (
                "Whether or not to flags violations for only alias expressions "
                "or all unquoted identifiers"
            )
        },
        "capitalisation_policy": {
            "validation": ["consistent", "upper", "lower", "capitalise"],
            "definition": "The capitalisation policy to enforce"
        },
    }
    # Load the rule configs from the default_config.ini
    config_loader = ConfigLoader()
    default_rules_config = config_loader.load_default_config_file()["rules"]
    # Take all rule specific configs and move them to the top level of the dict
    rule_specific_configs = {
        rule: config for rule, config in default_rules_config.items() if isinstance(config, dict)
    }
    for rule in rule_specific_configs:
        rule_config = default_rules_config.pop(rule)
        default_rules_config = {**default_rules_config, **rule_config}
    # Add default values + check for incorrect configs
    for config, info_dict in config_info_dict.items():
        try:
            info_dict["default"] = default_rules_config[config]
        except KeyError:
            raise KeyError(
                (
                    "{} is not a part of the default_config.ini. Please add it"
                    "to default_config.ini or double check your spelling."
                ).format(config)
            )
    return config_info_dict


CONFIG_INFO_DICT = create_config_info_dict()


def document_configuration(cls):
    """Add a 'Configuration' section to a Rule docstring.

    Utilize the the metadata in the global CONFIG_INFO_DICT to dynamically
    document the configuration options for a given rule.

    This is a little hacky, but it allows us to propogate configuration
    options in the docs, from a single source of truth.
    """
    config_doc = "\n    | **Configuration**"
    for keyword in cls.config_keywords:
        info_dict = CONFIG_INFO_DICT[keyword]
        config_doc += "\n    |     `{0}`: {1}. Must be one of {2}. Defaults to {3}.".format(
            keyword, info_dict["definition"], info_dict["validation"], info_dict["default"]
        )
        config_doc += "\n    |"
    # Add final blank line
    config_doc += "\n"
    # Add the configuration section immediately after the class description
    # docstring by inserting after the first line break, or first period,
    # if there is no line break.
    end_of_class_description = "." if "\n" not in cls.__doc__ else "\n"
    cls.__doc__ = cls.__doc__.replace(
        end_of_class_description, ".\n" + config_doc, 1
    )
    return cls
