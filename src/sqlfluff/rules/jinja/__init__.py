"""The jinja rules plugin bundle."""

from sqlfluff.core.plugin import hookimpl
from sqlfluff.core.rules import BaseRule
from sqlfluff.rules.jinja.JJ01 import Rule_JJ01
from typing import List, Type


@hookimpl
def get_rules() -> List[Type[BaseRule]]:
    """Get plugin rules."""
    return [Rule_JJ01]
