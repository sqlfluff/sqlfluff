"""The references plugin bundle."""

from sqlfluff.core.plugin import hookimpl

from sqlfluff.rules.references.RF01 import Rule_RF01
from sqlfluff.rules.references.RF02 import Rule_RF02
from sqlfluff.rules.references.RF03 import Rule_RF03
from sqlfluff.rules.references.RF04 import Rule_RF04
from sqlfluff.rules.references.RF05 import Rule_RF05
from sqlfluff.rules.references.RF06 import Rule_RF06


@hookimpl
def get_rules():
    """Get plugin rules."""
    return [Rule_RF01, Rule_RF02, Rule_RF03, Rule_RF04, Rule_RF05, Rule_RF06]
