"""Implementation of Rule L021."""
from typing import Optional

from sqlfluff.core.rules.base import BaseRule, LintResult, RuleContext
import sqlfluff.core.rules.functional.segment_predicates as segpred


class Rule_L021(BaseRule):
    """Ambiguous use of DISTINCT in select statement with GROUP BY.

    | **Anti-pattern**
    | DISTINCT and GROUP BY are conflicting.

    .. code-block:: sql

        SELECT DISTINCT
            a
        FROM foo
        GROUP BY a

    | **Best practice**
    | Remove DISTINCT or GROUP BY. In our case, removing GROUP BY is better.

    .. code-block:: sql

        SELECT DISTINCT
            a
        FROM foo
    """

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Ambiguous use of DISTINCT in select statement with GROUP BY."""
        segment = context.surrogates.segment
        if (
            segment.all(segpred.is_type("select_statement"))
            # Do we have a group by clause
            and segment.children(segpred.is_type("groupby_clause"))
        ):
            # Do we have the "DISTINCT" keyword in the select clause
            distinct = (
                segment.children(segpred.is_type("select_clause"))
                .children(segpred.is_type("select_clause_modifier"))
                .children(segpred.is_type("keyword"))
                .select([lambda s: s.name == "distinct"])
            )
            if distinct:
                return LintResult(anchor=distinct[0])
        return None
