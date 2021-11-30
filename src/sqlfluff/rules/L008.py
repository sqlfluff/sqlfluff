"""Implementation of Rule L008."""
from typing import Optional

from sqlfluff.core.parser import WhitespaceSegment

from sqlfluff.core.rules.base import BaseRule, LintResult, LintFix, RuleContext
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
       :force:

        SELECT
            *
        FROM foo
        WHERE a IN ('plop',•'zoo')
    """

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Commas should be followed by a single whitespace unless followed by a comment.

        This is a slightly odd one, because we'll almost always evaluate from a point a few places
        after the problem site. NB: We need at least two segments behind us for this to work.
        """
        # Initialise the memory, we need to check that we haven't already flagged a comma before.
        if not context.memory.get("L008_fixed_comma_segments"):
            context.memory["L008_fixed_comma_segments"] = []

        if len(context.raw_stack) < 1:
            return LintResult(memory=context.memory)

        # Get the first element of this segment.
        first_elem = context.segment.get_raw_segments()[0]

        cm1 = context.raw_stack[-1]
        if cm1 in context.memory["L008_fixed_comma_segments"]:
            # We've fixed this comma before, we are just in a subsegment
            # of the same segment that follows the comma.
            return LintResult(memory=context.memory)

        if cm1.name == "comma":
            # comma followed by something that isn't whitespace?
            if first_elem.name not in ["whitespace", "newline", "Dedent"]:
                self.logger.debug(
                    "Comma followed by something other than whitespace: %s", first_elem
                )
                context.memory["L008_fixed_comma_segments"].append(cm1)
                ins = WhitespaceSegment(raw=" ")
                return LintResult(
                    anchor=cm1,
                    fixes=[LintFix("edit", context.segment, [ins, context.segment])],
                    memory=context.memory,
                )

        if len(context.raw_stack) < 2:
            return LintResult(memory=context.memory)

        cm2 = context.raw_stack[-2]
        if cm2 in context.memory["L008_fixed_comma_segments"]:
            # We've fixed this comma before, we are just in a subsegment
            # of the same segment that follows the comma.
            return LintResult(memory=context.memory)

        if cm2.name == "comma":
            # comma followed by too much whitespace?
            if (
                cm1.is_whitespace  # Must be whitespace
                and cm1.raw != " "  # ...and not a single one
                and cm1.name != "newline"  # ...and not a newline
                and not first_elem.is_comment  # ...and not followed by a comment
            ):
                self.logger.debug("Comma followed by too much whitespace: %s", cm1)
                context.memory["L008_fixed_comma_segments"].append(cm2)
                repl = WhitespaceSegment(raw=" ")
                return LintResult(
                    anchor=cm1,
                    fixes=[LintFix("edit", cm1, repl)],
                    memory=context.memory,
                )
        # Otherwise we're fine
        return LintResult(memory=context.memory)
