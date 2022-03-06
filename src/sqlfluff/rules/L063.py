"""Implementation of Rule L063."""

from typing import Optional

from sqlfluff.core.rules.base import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.doc_decorators import document_fix_compatible
from sqlfluff.core.rules.functional import sp


@document_fix_compatible
class Rule_L063(BaseRule):
    """Remove redundant semi-colons and ``GO`` delimiters.

    **Anti-pattern**

    Consecutive semi-colons are redundant and can be removed.

    .. code-block:: sql

        SELECT foo FROM bar;;
        ;

        -- Semi-colons at the start of the file are redundant.

        ;;SELECT x FROM y;

        -- Both of the above examples also apply
        -- to GO delimiters in T-SQL.
        GO GO
        SELECT foo FROM bar GO
        GO

    **Best practice**

    Terminate statements with a single semi-colon.

    .. code-block:: sql

        SELECT foo FROM bar;

        -- Remove semi-colons preceding the
        -- first statement of the file.

        SELECT x FROM y;

        -- Remove redundant GO delimiters.
        SELECT foo FROM bar GO

    """

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Remove redundant semi-colons and GO delimiters."""
        # Only care about statement_terminator segments or GO delimiters.
        if not context.segment.is_type("statement_terminator", "go_statement"):
            return None

        # Look at previous code segment.
        reversed_raw_stack = context.functional.raw_stack.reversed()
        previous_code_segment = reversed_raw_stack.first(sp.is_code())

        # Handle case where file starts with a semi-colon or GO delimiter.
        if not previous_code_segment:
            return LintResult(
                anchor=context.segment, fixes=[LintFix.delete(context.segment)]
            )

        # If the previous code segment exists and
        # is not the same type as the current segment
        # (i.e. GO corresponds to checking for GO,
        # semi-colon corresponds to checking for semi-colon)
        # then we have nothing to do.
        if context.segment.is_type(
            "statement_terminator"
        ) and not previous_code_segment[0].is_type("statement_terminator"):
            return None
        elif (
            context.segment.is_type("go_statement")
            and previous_code_segment[0].raw_upper != "GO"
        ):
            return None

        # We have found a consecutive semi-colon/GO delimiter.
        if context.segment.is_type("statement_terminator"):
            msg = "Remove redundant semi-colon."
        else:
            msg = "Remove redundant GO delimiter."

        return LintResult(
            anchor=context.segment,
            fixes=[LintFix.delete(context.segment)],
            description=msg,
        )
