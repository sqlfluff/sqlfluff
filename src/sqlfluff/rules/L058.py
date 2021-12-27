"""Implementation of Rule L058."""

from apm import Check, match, Pattern, Some
from apm.core import MatchContext, MatchResult, Nested

from sqlfluff.core.rules.base import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.doc_decorators import document_fix_compatible
from sqlfluff.core.rules.functional import Segments, sp


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
                        "junk_before_end" @ Some(Check(sp.not_(sp.is_keyword("end")))),
                        Check(sp.is_keyword("end")),
                    ],
                )
                if matched:
                    # Determine what to delete from the end of the outer CASE.
                    return LintResult(
                        anchor=matched["nested_expression"],
                        fixes=[
                            # Replace outer ELSE with inner CASE body
                            LintFix.replace(
                                matched["else"],
                                self._to_keep_from_nested_case(matched),
                            ),
                            # Delete inner CASE
                            LintFix.delete(matched["nested_expression"]),
                        ]
                        # Delete stuff from the end of the outer CASE
                        + [
                            LintFix.delete(seg)
                            for seg in Segments(*matched["junk_before_end"]).select(
                                sp.not_(sp.is_meta())
                            )
                        ],
                    )
        return LintResult()

    @staticmethod
    def _to_keep_from_nested_case(matched):
        """Determine what to keep from the nested CASE."""
        nested_case_children = Segments(*matched["nested_case_expression"].segments)
        # First pass: From the first WHEN (inclusive) to the END
        # (excluding the END).
        start_seg = (
            nested_case_children.select(loop_while=sp.not_(sp.is_keyword("when")))
            .last()
            .get()
        )
        stop_seg = nested_case_children.last(sp.is_keyword("end")).get()
        to_keep = nested_case_children.select(
            start_seg=start_seg,
            stop_seg=stop_seg,
        )
        # Find any trailing "non-code". From this, keep all dedents
        # less 1 (i.e. drop the dedent associated with the nested
        # END).
        trailing_non_code = (
            to_keep.reversed().select(loop_while=sp.not_(sp.is_code())).reversed()
        )
        trailing_keep = trailing_non_code.select(sp.is_type("dedent"))[:-1]
        return to_keep[: -len(trailing_non_code)] + trailing_keep
