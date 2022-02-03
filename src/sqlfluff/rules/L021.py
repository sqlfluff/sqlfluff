"""Implementation of Rule L021."""
from typing import Optional

from sqlfluff.core.rules.base import BaseRule, LintResult, RuleContext
import sqlfluff.core.rules.functional.segment_predicates as sp


class Rule_L021(BaseRule):
    """Ambiguous use of ``DISTINCT`` in a ``SELECT`` statement with ``GROUP BY``.

    When using ``GROUP BY`` a `DISTINCT`` clause should not be necessary as every
    non-distinct ``SELECT`` clause must be included in the ``GROUP BY`` clause.

    **Anti-pattern**

    ``DISTINCT`` and ``GROUP BY`` are conflicting.

    .. code-block:: sql

        SELECT DISTINCT
            a
        FROM foo
        GROUP BY a

    **Best practice**

    Remove ``DISTINCT`` or ``GROUP BY``. In our case, removing ``GROUP BY`` is better.

    .. code-block:: sql

        SELECT DISTINCT
            a
        FROM foo
    """

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Ambiguous use of DISTINCT in select statement with GROUP BY."""
        segment = context.functional.segment
        if (
            segment.all(sp.is_type("select_statement"))
            # Do we have a group by clause
            and segment.children(sp.is_type("groupby_clause"))
        ):
            # Do we have the "DISTINCT" keyword in the select clause
            distinct = (
                segment.children(sp.is_type("select_clause"))
                .children(sp.is_type("select_clause_modifier"))
                .children(sp.is_type("keyword"))
                .select(sp.is_name("distinct"))
            )
            if distinct:
                return LintResult(anchor=distinct[0])
        return None
