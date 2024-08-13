"""The aliasing plugin bundle."""

from typing import List, Type

from sqlfluff.core.plugin import hookimpl
from sqlfluff.core.rules import BaseRule


@hookimpl
def get_rules() -> List[Type[BaseRule]]:
    """Get plugin rules.

    NOTE: Rules are imported only on fetch to manage import times
    when rules aren't used.
    """
    from sqlfluff.rules.aliasing.AL01 import Rule_AL01
    from sqlfluff.rules.aliasing.AL02 import Rule_AL02
    from sqlfluff.rules.aliasing.AL03 import Rule_AL03
    from sqlfluff.rules.aliasing.AL04 import Rule_AL04
    from sqlfluff.rules.aliasing.AL05 import Rule_AL05
    from sqlfluff.rules.aliasing.AL06 import Rule_AL06
    from sqlfluff.rules.aliasing.AL07 import Rule_AL07
    from sqlfluff.rules.aliasing.AL08 import Rule_AL08
    from sqlfluff.rules.aliasing.AL09 import Rule_AL09

    return [
        Rule_AL01,
        Rule_AL02,
        Rule_AL03,
        Rule_AL04,
        Rule_AL05,
        Rule_AL06,
        Rule_AL07,
        Rule_AL08,
        Rule_AL09,
    ]
