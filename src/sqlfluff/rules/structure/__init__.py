"""The structure plugin bundle."""

from typing import List, Type

from sqlfluff.core.plugin import hookimpl
from sqlfluff.core.rules import BaseRule


@hookimpl
def get_rules() -> List[Type[BaseRule]]:
    """Get plugin rules.

    NOTE: Rules are imported only on fetch to manage import times
    when rules aren't used.
    """
    from sqlfluff.rules.structure.ST01 import Rule_ST01
    from sqlfluff.rules.structure.ST02 import Rule_ST02
    from sqlfluff.rules.structure.ST03 import Rule_ST03
    from sqlfluff.rules.structure.ST04 import Rule_ST04
    from sqlfluff.rules.structure.ST05 import Rule_ST05
    from sqlfluff.rules.structure.ST06 import Rule_ST06
    from sqlfluff.rules.structure.ST07 import Rule_ST07
    from sqlfluff.rules.structure.ST08 import Rule_ST08
    from sqlfluff.rules.structure.ST09 import Rule_ST09

    return [
        Rule_ST01,
        Rule_ST02,
        Rule_ST03,
        Rule_ST04,
        Rule_ST05,
        Rule_ST06,
        Rule_ST07,
        Rule_ST08,
        Rule_ST09,
    ]
