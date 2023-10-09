"""The capitalisation plugin bundle."""

from typing import List, Type

from sqlfluff.core.plugin import hookimpl
from sqlfluff.core.rules import BaseRule


@hookimpl
def get_rules() -> List[Type[BaseRule]]:
    """Get plugin rules.

    NOTE: Rules are imported only on fetch to manage import times
    when rules aren't used.
    """
    from sqlfluff.rules.capitalisation.CP01 import Rule_CP01
    from sqlfluff.rules.capitalisation.CP02 import Rule_CP02
    from sqlfluff.rules.capitalisation.CP03 import Rule_CP03
    from sqlfluff.rules.capitalisation.CP04 import Rule_CP04
    from sqlfluff.rules.capitalisation.CP05 import Rule_CP05

    return [Rule_CP01, Rule_CP02, Rule_CP03, Rule_CP04, Rule_CP05]
