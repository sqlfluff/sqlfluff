"""The aliasing plugin bundle."""

from sqlfluff.core.plugin import hookimpl

from sqlfluff.rules.layout.LT01 import Rule_LT01
from sqlfluff.rules.layout.LT02 import Rule_LT02


@hookimpl
def get_rules():
    """Get plugin rules."""
    return [Rule_LT01, Rule_LT02]
