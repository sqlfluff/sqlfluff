"""Implementation of Rule AL02."""

from typing import Optional

from sqlfluff.core.rules import LintResult, RuleContext
from sqlfluff.rules.aliasing.AL01 import Rule_AL01
from sqlfluff.utils.functional import FunctionalContext


class Rule_AL02(Rule_AL01):
    """Implicit/explicit aliasing of columns.

    Aliasing of columns to follow preference
    (explicit using an ``AS`` clause is default).

    **Anti-pattern**

    In this example, the alias for column ``a`` is implicit.

    .. code-block:: sql

        SELECT
            a alias_col
        FROM foo

    **Best practice**

    Add ``AS`` to make it explicit.

    .. code-block:: sql

        SELECT
            a AS alias_col
        FROM foo

    """

    name = "aliasing.column"
    aliases = ("L012",)
    groups = ("all", "core", "aliasing")
    config_keywords = ["aliasing"]
    # NB: crawl_behaviour is the same as Rule AL01

    _target_parent_types = ("select_clause_element",)

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        # T-SQL supports alternative alias expressions for AL02
        # select alias = value
        # instead of
        # select value as alias
        # Recognise this and exit early
        if FunctionalContext(context).segment.children()[-1].raw == "=":
            return None
        return super()._eval(context)
