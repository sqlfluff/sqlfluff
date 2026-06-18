"""The postgres rules plugin bundle.

This plugin bundles linting rules which apply exclusively to PostgreSQL. At some
point in the future it might be useful to spin this off into a separate
installable python package, but so long as the number of rules remain
low, it makes sense to keep it bundled with SQLFluff core.
"""

from sqlfluff.core.plugin import hookimpl
from sqlfluff.core.rules import BaseRule


@hookimpl
def get_rules() -> list[type[BaseRule]]:
    """Get plugin rules.

    NOTE: Rules are imported only on fetch to manage import times
    when rules aren't used.
    """
    from sqlfluff.rules.postgres.PG01 import Rule_PG01
    from sqlfluff.rules.postgres.PG02 import Rule_PG02

    return [Rule_PG01, Rule_PG02]
