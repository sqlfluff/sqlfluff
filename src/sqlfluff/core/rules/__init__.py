"""Register all the rule classes with their corresponding rulesets (just std currently)."""

from .base import RuleSet
from .config_info import STANDARD_CONFIG_INFO_DICT
from .std import rules


std_rule_set = RuleSet(name="standard", config_info=STANDARD_CONFIG_INFO_DICT)

for name, val in rules.items():
    std_rule_set.register(val)


def get_ruleset(name: str = "standard") -> RuleSet:
    """Get a ruleset by name."""
    lookup = {std_rule_set.name: std_rule_set}
    # Return a copy in case someone modifies the register.
    return lookup[name].copy()
