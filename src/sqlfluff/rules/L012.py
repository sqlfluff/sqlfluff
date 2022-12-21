"""Implementation of Rule L012."""
from typing import Optional

from sqlfluff.rules.L011 import Rule_L011
from sqlfluff.core.rules.doc_decorators import document_configuration, document_groups
from sqlfluff.core.rules import LintResult, RuleContext
from sqlfluff.utils.functional import FunctionalContext


@document_groups
@document_configuration
class Rule_L012(Rule_L011):
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

    groups = ("all", "core")
    config_keywords = ["aliasing"]
    # NB: crawl_behaviour is the same as Rule L011

    _target_elems = [
        ("type", "select_clause_element"),
    ]

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        # T-SQL supports alternative alias expressions for L012
        # select alias = value
        # instead of
        # select value as alias
        # Recognise this and exit early
        if FunctionalContext(context).segment.children()[-1].raw == "=":
            return None
        return super()._eval(context)
