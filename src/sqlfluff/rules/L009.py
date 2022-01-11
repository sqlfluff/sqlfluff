"""Implementation of Rule L009."""
from typing import Optional

from sqlfluff.core.parser import NewlineSegment

from sqlfluff.core.rules.base import BaseRule, LintResult, LintFix, RuleContext
from sqlfluff.core.rules.doc_decorators import document_fix_compatible
from sqlfluff.core.rules.functional import Segments, rsp, sp


@document_fix_compatible
class Rule_L009(BaseRule):
    """Files must end with a single trailing newline.

    | **Anti-pattern**
    | The content in file does not end with a single trailing newline, the $ represents end of file.

    .. code-block:: sql
       :force:

        SELECT
            a
        FROM foo$

        -- Ending on an indented line means there is no newline at the end of the file, the • represents space.

        SELECT
        ••••a
        FROM
        ••••foo
        ••••$

        -- Ending on a semi-colon means the last line is not a newline.

        SELECT
            a
        FROM foo
        ;$

        -- Ending with multiple newlines.

        SELECT
            a
        FROM foo

        $

    | **Best practice**
    | Add trailing newline to the end, the $ character represents end of file.

    .. code-block:: sql
       :force:

        SELECT
            a
        FROM foo
        $

        -- Ensuring the last line is not indented so is just a newline.

        SELECT
        ••••a
        FROM
        ••••foo
        $

        -- Even when ending on a semi-colon, ensure there is a newline after

        SELECT
            a
        FROM foo
        ;
        $

    """

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Files must end with a single trailing newline.

        We only care about the segment and the siblings which come after it
        for this rule, we discard the others into the kwargs argument.

        """
        # We only care about the final segment of the parse tree.
        if not self.is_final_segment(context):
            return None

        # Include current segment for complete stack and reverse.
        parent_stack: Segments = context.functional.parent_stack
        complete_stack: Segments = (
            context.functional.raw_stack + context.functional.segment
        )
        reversed_complete_stack = complete_stack.reversed()

        # Find the trailing newline segments.
        trailing_newlines = reversed_complete_stack.select(
            select_if=sp.is_type("newline"),
            loop_while=sp.or_(sp.is_whitespace(), sp.is_type("dedent")),
        )

        if not trailing_newlines:
            # We make an edit to create this segment after the child of the FileSegment.
            if len(parent_stack) == 1:
                fix_anchor_segment = context.segment
            else:
                fix_anchor_segment = parent_stack[1]

            return LintResult(
                anchor=context.segment,
                fixes=[
                    LintFix.create_after(
                        fix_anchor_segment,
                        [NewlineSegment()],
                    )
                ],
            )
        else:
            # There are one or more trailing newlines in templated space.
            # Translate to "raw" space and count them there. Delete any extras.
            extra_newlines = trailing_newlines[1:].select(
                loop_while=lambda seg: sp.raw_slices(seg, context.templated_file).all(
                    rsp.is_slice_type("literal")
                )
            )
            if extra_newlines:
                return LintResult(
                    anchor=context.segment,
                    fixes=[LintFix.delete(d) for d in extra_newlines],
                )
            # Single newline, no need for fix.
            return None
