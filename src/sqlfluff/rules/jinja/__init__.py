"""The jinja rules plugin bundle."""

from sqlfluff.core.plugin import hookimpl


@hookimpl
def get_rules():
    """Get plugin rules.

    NOTE: Rules are imported only on fetch to manage import times
    when rules aren't used.
    """
    from sqlfluff.rules.jinja.JJ01 import Rule_JJ01

    return [Rule_JJ01]
