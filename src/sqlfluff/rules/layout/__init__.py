"""The aliasing plugin bundle."""

from sqlfluff.core.plugin import hookimpl

from sqlfluff.rules.layout.LT01 import Rule_LT01


@hookimpl
def get_rules():
    """Get plugin rules."""
    return [Rule_LT01]
