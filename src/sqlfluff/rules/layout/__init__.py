"""The aliasing plugin bundle."""

from sqlfluff.core.plugin import hookimpl

from sqlfluff.rules.layout.LT01 import Rule_LT01
from sqlfluff.rules.layout.LT02 import Rule_LT02
from sqlfluff.rules.layout.LT03 import Rule_LT03
from sqlfluff.rules.layout.LT04 import Rule_LT04


@hookimpl
def get_rules():
    """Get plugin rules."""
    return [Rule_LT01, Rule_LT02, Rule_LT03, Rule_LT04]
