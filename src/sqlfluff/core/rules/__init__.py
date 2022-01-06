"""Configuration and examples for individual rules."""

from sqlfluff.core.rules.base import RuleSet
from sqlfluff.core.rules.config_info import STANDARD_CONFIG_INFO_DICT
from sqlfluff.core.plugin.host import get_plugin_manager

# Sphinx effectively runs an import * from this module in rules.rst, so initialise
# __all__ with an empty list before we populate it with the rule names.
__all__ = []

# Iterate through the rules list and register each rule as a global for documentation
for plugin_rules in get_plugin_manager().hook.get_rules():
    for rule in plugin_rules:
        # Add the Rule classes to the module namespace with globals() so that they can
        # be found by Sphinx automodule documentation in rules.rst
        # The result is the same as declaring the classes in this file.
        # Rules coming from the "Example" plugin are excluded from the
        # documentation.
        globals()[rule.__name__] = rule
        # Add the rule class names to __all__ for Sphinx automodule discovery
        __all__.append(rule.__name__)


def _load_standard_rules():
    """Initialise the standard ruleset.

    We do this on each call so that dynamic rules changes
    are possible.
    """
    std_rule_set = RuleSet(name="standard", config_info=STANDARD_CONFIG_INFO_DICT)

    # Iterate through the rules list and register each rule with the standard set.
    for plugin_rules in get_plugin_manager().hook.get_rules():
        for rule in plugin_rules:
            std_rule_set.register(rule)

    return std_rule_set


def get_ruleset(name: str = "standard") -> RuleSet:
    """Get a ruleset by name."""
    std_rules = _load_standard_rules()
    lookup = {std_rules.name: std_rules}
    # Return a copy in case someone modifies the register.
    return lookup[name].copy()
