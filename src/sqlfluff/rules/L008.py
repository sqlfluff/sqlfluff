"""Implementation of Rule L008."""

from sqlfluff.core.parser import WhitespaceSegment

from sqlfluff.core.rules.base import BaseRule, LintResult, LintFix
from sqlfluff.core.rules.doc_decorators import document_fix_compatible


@document_fix_compatible
class Rule_L008(BaseRule):
    """Commas should be followed by a single whitespace unless followed by a comment.

    | **Anti-pattern**
    | The • character represents a space.
    | In this example, there is no space between the comma and 'zoo'.

    .. code-block:: sql

        SELECT
            *
        FROM foo
        WHERE a IN ('plop','zoo')

    | **Best practice**
    | Keep a single space after the comma.

    .. code-block:: sql

        SELECT
            *
        FROM foo
        WHERE a IN ('plop',•'zoo')
    """

    def _eval(self, segment, raw_stack, **kwargs):
        """Commas should be followed by a single whitespace unless followed by a comment.

        This is a slightly odd one, because we'll almost always evaluate from a point a few places
        after the problem site. NB: We need at least two segments behind us for this to work.
        """
        if len(raw_stack) < 1:
            return None

        # Get the first element of this segment.
        first_elem = next(segment.iter_raw_seg())

        cm1 = raw_stack[-1]
        if cm1.name == "comma":
            # comma followed by something that isn't whitespace?
            if first_elem.name not in ["whitespace", "newline"]:
                self.logger.debug(
                    "Comma followed by something other than whitespace: %s", first_elem
                )
                ins = WhitespaceSegment(raw=" ")
                return LintResult(
                    anchor=cm1, fixes=[LintFix("edit", segment, [ins, segment])]
                )

        if len(raw_stack) < 2:
            return None

        cm2 = raw_stack[-2]
        if cm2.name == "comma":
            # comma followed by too much whitespace?
            if (
                cm1.is_whitespace  # Must be whitespace
                and cm1.raw != " "  # ...and not a single one
                and cm1.name != "newline"  # ...and not a newline
                and not first_elem.is_comment  # ...and not followed by a comment
            ):
                self.logger.debug("Comma followed by too much whitespace: %s", cm1)
                repl = WhitespaceSegment(raw=" ")
                return LintResult(anchor=cm1, fixes=[LintFix("edit", cm1, repl)])
        # Otherwise we're fine
        return None
