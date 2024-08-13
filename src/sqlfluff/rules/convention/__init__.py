"""The convention plugin bundle."""

from typing import List, Type

from sqlfluff.core.plugin import hookimpl
from sqlfluff.core.rules import BaseRule


@hookimpl
def get_rules() -> List[Type[BaseRule]]:
    """Get plugin rules.

    NOTE: Rules are imported only on fetch to manage import times
    when rules aren't used.
    """
    from sqlfluff.rules.convention.CV01 import Rule_CV01
    from sqlfluff.rules.convention.CV02 import Rule_CV02
    from sqlfluff.rules.convention.CV03 import Rule_CV03
    from sqlfluff.rules.convention.CV04 import Rule_CV04
    from sqlfluff.rules.convention.CV05 import Rule_CV05
    from sqlfluff.rules.convention.CV06 import Rule_CV06
    from sqlfluff.rules.convention.CV07 import Rule_CV07
    from sqlfluff.rules.convention.CV08 import Rule_CV08
    from sqlfluff.rules.convention.CV09 import Rule_CV09
    from sqlfluff.rules.convention.CV10 import Rule_CV10
    from sqlfluff.rules.convention.CV11 import Rule_CV11

    return [
        Rule_CV01,
        Rule_CV02,
        Rule_CV03,
        Rule_CV04,
        Rule_CV05,
        Rule_CV06,
        Rule_CV07,
        Rule_CV08,
        Rule_CV09,
        Rule_CV10,
        Rule_CV11,
    ]
