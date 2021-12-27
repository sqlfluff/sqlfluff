"""Implementation of Rule L017."""

from apm import match, Check, Some

from sqlfluff.core.rules.base import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.doc_decorators import document_fix_compatible
from sqlfluff.core.rules.functional import sp


@document_fix_compatible
class Rule_L017(BaseRule):
    """Function name not immediately followed by bracket.

    | **Anti-pattern**
    | In this example, there is a space between the function and the parenthesis.

    .. code-block:: sql

        SELECT
            sum (a)
        FROM foo

    | **Best practice**
    | Remove the space between the function and the parenthesis.

    .. code-block:: sql

        SELECT
            sum(a)
        FROM foo

    """

    def _eval(self, context: RuleContext) -> LintResult:
        """Function name not immediately followed by bracket.

        Look for Function Segment with anything other than the
        function name before brackets
        """
        segment = context.functional.segment
        # We only trigger on start_bracket (open parenthesis)
        if segment.all(sp.is_type("function")):
            matched = match(
                segment.children(),
                [
                    "fn_name" @ Check(sp.is_type("function_name")),
                    "between"
                    @ Some(Check(sp.not_(sp.is_type("bracketed"))), at_least=1),
                    "bracket" @ Check(sp.is_type("bracketed")),
                ],
            )
            if matched:
                fixes = None
                if all(
                    seg.is_type("whitespace", "newline") for seg in matched["between"]
                ):
                    # Fix if there is only whitespace or newlines between.
                    fixes = [LintFix.delete(seg) for seg in matched["between"]]

                return LintResult(
                    anchor=matched["between"][0],
                    fixes=fixes,
                )
        return LintResult()
