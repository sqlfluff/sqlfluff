"""Configuration and examples for individual rules."""

from sqlfluff.core.plugin.host import get_plugin_manager
from sqlfluff.core.rules.base import (
    BaseRule,
    EvalResultType,
    LintResult,
    RuleGhost,
    RulePack,
    RuleSet,
)
from sqlfluff.core.rules.config_info import STANDARD_CONFIG_INFO_DICT
from sqlfluff.core.rules.context import RuleContext
from sqlfluff.core.rules.fix import LintFix


def _load_standard_rules() -> RuleSet:
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


__all__ = (
    "get_ruleset",
    "RuleSet",
    "RulePack",
    "BaseRule",
    "LintResult",
    "LintFix",
    "RuleContext",
    "RuleGhost",
    "EvalResultType",
)
