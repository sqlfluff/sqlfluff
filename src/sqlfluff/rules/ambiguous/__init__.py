"""The ambiguous plugin bundle.

NOTE: Yes the title of this bundle is ...ambiguous. 😁
"""

from typing import List, Type

from sqlfluff.core.plugin import hookimpl
from sqlfluff.core.rules import BaseRule


@hookimpl
def get_rules() -> List[Type[BaseRule]]:
    """Get plugin rules.

    NOTE: Rules are imported only on fetch to manage import times
    when rules aren't used.
    """
    from sqlfluff.rules.ambiguous.AM01 import Rule_AM01
    from sqlfluff.rules.ambiguous.AM02 import Rule_AM02
    from sqlfluff.rules.ambiguous.AM03 import Rule_AM03
    from sqlfluff.rules.ambiguous.AM04 import Rule_AM04
    from sqlfluff.rules.ambiguous.AM05 import Rule_AM05
    from sqlfluff.rules.ambiguous.AM06 import Rule_AM06
    from sqlfluff.rules.ambiguous.AM07 import Rule_AM07

    return [Rule_AM01, Rule_AM02, Rule_AM03, Rule_AM04, Rule_AM05, Rule_AM06, Rule_AM07]
