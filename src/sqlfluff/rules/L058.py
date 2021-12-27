"""Implementation of Rule L058."""

from apm import Check, match, Pattern, Some
from apm.core import MatchContext, MatchResult, Nested

from sqlfluff.core.rules.base import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.doc_decorators import document_fix_compatible
from sqlfluff.core.rules.functional import sp


class Attr(Pattern, Nested):
    """Extension class for apm. Allows processing of an object field.

    Adapted from the package's similar "At" class.
    """

    def __init__(self, path, pattern):
        if isinstance(path, str):
            self._path = path.split(".")
        else:
            self._path = list(path)
        self._pattern = pattern

    def match(self, value, *, ctx: MatchContext, strict: bool) -> MatchResult:
        """Override abstract parent function."""
        for k in self._path:
            try:
                value = getattr(value, k)
            except AttributeError:
                return ctx.no_match()
        return ctx.match(value, self._pattern)

    def descend(self, f):
        """Override abstract parent function."""
        return Attr(path=self._path, pattern=f(self._pattern))


@document_fix_compatible
class Rule_L058(BaseRule):
    """Nested CASE statements could be flattened.

    | **Anti-pattern**
    | In this example, the outer CASE's "ELSE" is another CASE.

    .. code-block:: sql

        SELECT
          CASE
            WHEN species = 'Cat' THEN 'Meow'
            ELSE
            CASE
               WHEN species = 'Dog' THEN 'Woof'
            END
          END as sound
        FROM mytable

    | **Best practice**
    | Move the body of the inner "CASE" to the end of the outer one.

    .. code-block:: sql

        SELECT
          CASE
            WHEN species = 'Cat' THEN 'Meow'
            WHEN species = 'Dog' THEN 'Woof'
          END AS sound
        FROM mytable

    """

    def _eval(self, context: RuleContext) -> LintResult:
        """Nested CASE should be simplified."""
        segment = context.functional.segment
        if segment.all(sp.is_type("case_expression")):
            children = segment.children()

            # Search for occurrences of the pattern: WHEN <<expression>> ELSE CASE <<expression>>
            matched = MatchResult(matches=True, context=None, match_stack=None)
            while matched:
                matched = match(
                    children,
                    [
                        # WHEN <<expression>>
                        Some(Check(sp.not_(sp.is_keyword("when")))),
                        Check(sp.is_keyword("when")),
                        Some(Check(sp.not_(sp.is_type("expression")))),
                        Check(sp.is_type("expression")),
                        # ELSE <<expression>>
                        Some(Check(sp.not_(sp.is_keyword("else")))),
                        "else" @ Check(sp.is_keyword("else")),
                        Some(Check(sp.not_(sp.is_type("expression")))),
                        "nested_expression"
                        @ Attr(
                            "segments",
                            [
                                # case_expression
                                "nested_case_expression"
                                @ Check(sp.is_type("case_expression"))
                            ],
                        ),
                        Some(...),
                    ],
                )
                if matched:
                    return LintResult(
                        anchor=matched["nested_expression"],
                        fixes=[
                            LintFix.replace(
                                matched["else"],
                                matched["nested_case_expression"].segments[1:-1],
                            ),
                            LintFix.delete(matched["nested_expression"]),
                        ],
                    )
        return LintResult()
