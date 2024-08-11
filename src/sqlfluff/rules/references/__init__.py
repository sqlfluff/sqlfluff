"""The references plugin bundle."""

from typing import List, Type

from sqlfluff.core.plugin import hookimpl
from sqlfluff.core.rules import BaseRule


@hookimpl
def get_rules() -> List[Type[BaseRule]]:
    """Get plugin rules.

    NOTE: Rules are imported only on fetch to manage import times
    when rules aren't used.
    """
    from sqlfluff.rules.references.RF01 import Rule_RF01
    from sqlfluff.rules.references.RF02 import Rule_RF02
    from sqlfluff.rules.references.RF03 import Rule_RF03
    from sqlfluff.rules.references.RF04 import Rule_RF04
    from sqlfluff.rules.references.RF05 import Rule_RF05
    from sqlfluff.rules.references.RF06 import Rule_RF06

    return [Rule_RF01, Rule_RF02, Rule_RF03, Rule_RF04, Rule_RF05, Rule_RF06]
