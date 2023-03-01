"""The ambiguous plugin bundle.

NOTE: Yes the title of this bundle is ...ambiguous. 😁
"""

from sqlfluff.core.plugin import hookimpl

from sqlfluff.rules.ambiguous.AM01 import Rule_AM01
from sqlfluff.rules.ambiguous.AM02 import Rule_AM02
from sqlfluff.rules.ambiguous.AM03 import Rule_AM03
from sqlfluff.rules.ambiguous.AM04 import Rule_AM04
from sqlfluff.rules.ambiguous.AM05 import Rule_AM05
from sqlfluff.rules.ambiguous.AM06 import Rule_AM06
from sqlfluff.rules.ambiguous.AM07 import Rule_AM07


@hookimpl
def get_rules():
    """Get plugin rules."""
    return [Rule_AM01, Rule_AM02, Rule_AM03, Rule_AM04, Rule_AM05, Rule_AM06, Rule_AM07]
