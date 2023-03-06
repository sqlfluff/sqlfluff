"""The aliasing plugin bundle."""

from sqlfluff.core.plugin import hookimpl

from sqlfluff.rules.aliasing.AL01 import Rule_AL01
from sqlfluff.rules.aliasing.AL02 import Rule_AL02
from sqlfluff.rules.aliasing.AL03 import Rule_AL03
from sqlfluff.rules.aliasing.AL04 import Rule_AL04
from sqlfluff.rules.aliasing.AL05 import Rule_AL05
from sqlfluff.rules.aliasing.AL06 import Rule_AL06
from sqlfluff.rules.aliasing.AL07 import Rule_AL07


@hookimpl
def get_rules():
    """Get plugin rules."""
    return [Rule_AL01, Rule_AL02, Rule_AL03, Rule_AL04, Rule_AL05, Rule_AL06, Rule_AL07]
