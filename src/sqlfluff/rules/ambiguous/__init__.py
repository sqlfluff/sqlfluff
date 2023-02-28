"""The ambiguous plugin bundle.

NOTE: Yes the title of this bundle is ...ambiguous. 😁
"""

from sqlfluff.core.plugin import hookimpl

from sqlfluff.rules.ambiguous.AB01 import Rule_AB01
from sqlfluff.rules.ambiguous.AB02 import Rule_AB02
from sqlfluff.rules.ambiguous.AB03 import Rule_AB03
from sqlfluff.rules.ambiguous.AB04 import Rule_AB04
from sqlfluff.rules.ambiguous.AB05 import Rule_AB05
from sqlfluff.rules.ambiguous.AB06 import Rule_AB06
from sqlfluff.rules.ambiguous.AB07 import Rule_AB07


@hookimpl
def get_rules():
    """Get plugin rules."""
    return [Rule_AB01, Rule_AB02, Rule_AB03, Rule_AB04, Rule_AB05, Rule_AB06, Rule_AB07]
