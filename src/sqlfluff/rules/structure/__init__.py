"""The structure plugin bundle."""

from sqlfluff.core.plugin import hookimpl

from sqlfluff.rules.structure.ST01 import Rule_ST01
from sqlfluff.rules.structure.ST02 import Rule_ST02
from sqlfluff.rules.structure.ST03 import Rule_ST03
from sqlfluff.rules.structure.ST04 import Rule_ST04
from sqlfluff.rules.structure.ST05 import Rule_ST05
from sqlfluff.rules.structure.ST06 import Rule_ST06
from sqlfluff.rules.structure.ST07 import Rule_ST07
from sqlfluff.rules.structure.ST08 import Rule_ST08


@hookimpl
def get_rules():
    """Get plugin rules."""
    return [
        Rule_ST01,
        Rule_ST02,
        Rule_ST03,
        Rule_ST04,
        Rule_ST05,
        Rule_ST06,
        Rule_ST07,
        Rule_ST08,
    ]
