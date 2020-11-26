"""init py for the new rules crawlers."""

from .std import std_rule_set
from .base import rules_logger  # noqa


def get_ruleset(name="standard"):
    """Get a ruleset by name."""
    lookup = {std_rule_set.name: std_rule_set}
    # Return a copy in case someone modifies the register.
    return lookup[name].copy()
