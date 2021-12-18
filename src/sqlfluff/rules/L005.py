"""Implementation of Rule L005."""
from typing import Optional

from sqlfluff.core.rules.base import BaseRule, LintResult, LintFix, RuleContext
from sqlfluff.core.rules.doc_decorators import document_fix_compatible


@document_fix_compatible
class Rule_L005(BaseRule):
    """Commas should not have whitespace directly before them.

    Unless it's an indent. Trailing/leading commas are dealt with
    in a different rule.

    | **Anti-pattern**
    | The • character represents a space.
    | There is an extra space in line two before the comma.

    .. code-block:: sql
       :force:

        SELECT
            a•,
            b
        FROM foo

    | **Best practice**
    | Remove the space before the comma.

    .. code-block:: sql

        SELECT
            a,
            b
        FROM foo
    """

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Commas should not have whitespace directly before them.

        We need at least one segment behind us for this to work.

        """
        if len(context.raw_stack) >= 1:
            cm1 = context.raw_stack[-1]
            if (
                context.segment.is_type("comma")
                and cm1.is_type("whitespace")
                and cm1.pos_marker.line_pos > 1
            ):
                anchor = cm1
                return LintResult(anchor=anchor, fixes=[LintFix.delete(cm1)])
        # Otherwise fine
        return None
