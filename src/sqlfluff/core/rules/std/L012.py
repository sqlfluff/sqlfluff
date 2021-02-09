"""Implementation of Rule L012."""

from sqlfluff.core.rules.std.L011 import Rule_L011


class Rule_L012(Rule_L011):
    """Implicit aliasing of column not allowed. Use explicit `AS` clause.

    NB: This rule inherits its functionality from obj:`Rule_L011` but is
    separate so that they can be enabled and disabled separately.

    """

    _target_elems = ("select_target_element",)
