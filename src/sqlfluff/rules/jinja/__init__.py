"""The jinja rules plugin bundle."""

from sqlfluff.core.plugin import hookimpl

from sqlfluff.rules.jinja.JJ01 import Rule_JJ01


@hookimpl
def get_rules():
    """Get plugin rules."""
    return [Rule_JJ01]
