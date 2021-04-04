"""Register all the rule classes with their corresponding rulesets (just std currently)."""

from sqlfluff.core.rules.base import RuleSet
from sqlfluff.core.rules.config_info import STANDARD_CONFIG_INFO_DICT
from sqlfluff.core.plugin.host import get_plugin_manager

std_rule_set = RuleSet(name="standard", config_info=STANDARD_CONFIG_INFO_DICT)

# Sphinx effectively runs an import * from this module in rules.rst, so initialise
# __all__ with an empty list before we populate it with the rule names.
__all__ = []

# Iterate through the rules list and register each rule with the std_rule_set
for plugin_rules in get_plugin_manager().hook.get_rules():
    for rule in plugin_rules:
        std_rule_set.register(rule)

        # Add the Rule classes to the module namespace with globals() so that they can
        # be found by Sphinx automodule documentation in rules.rst
        # The result is the same as declaring the classes in this file.
        # Rules coming from the "Example" plugin are excluded from the
        # documentation.
        globals()[rule.__name__] = rule
        # Add the rule class names to __all__ for Sphinx automodule discovery
        __all__.append(rule.__name__)


def get_ruleset(name: str = "standard") -> RuleSet:
    """Get a ruleset by name."""
    lookup = {std_rule_set.name: std_rule_set}
    # Return a copy in case someone modifies the register.
    return lookup[name].copy()
