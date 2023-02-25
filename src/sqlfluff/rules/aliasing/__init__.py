"""The capitalisation plugin bundle."""

from sqlfluff.core.plugin import hookimpl

from sqlfluff.rules.capitalisation.CP01 import Rule_CP01
from sqlfluff.rules.capitalisation.CP02 import Rule_CP02
from sqlfluff.rules.capitalisation.CP03 import Rule_CP03
from sqlfluff.rules.capitalisation.CP04 import Rule_CP04
from sqlfluff.rules.capitalisation.CP05 import Rule_CP05


@hookimpl
def get_rules():
    """Get plugin rules."""
    return [Rule_CP01, Rule_CP02, Rule_CP03, Rule_CP04, Rule_CP05]
