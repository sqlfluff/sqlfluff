"""Implementation of Rule L012."""
from typing import Optional

from sqlfluff.rules.L011 import Rule_L011
from sqlfluff.core.rules.doc_decorators import document_configuration
from sqlfluff.core.rules.base import LintResult, RuleContext


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

    config_keywords = ["aliasing"]

    _target_elems = ("select_clause_element",)

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        # T-SQL supports alternative alias expressions for L012
        # select alias = value
        # instead of
        # select value as alias
        # Recognise this and exit early
        if (
            context.segment.is_type("alias_expression")
            and context.functional.segment.children()[-1].name == "raw_equals"
        ):
            return None
        return super()._eval(context)
