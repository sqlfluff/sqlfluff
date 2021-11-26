"""Implementation of Rule L009."""
from typing import List, Optional

from sqlfluff.core.parser import NewlineSegment
from sqlfluff.core.parser.segments.base import BaseSegment

from sqlfluff.core.rules.base import BaseRule, LintResult, LintFix, RuleContext
from sqlfluff.core.rules.doc_decorators import document_fix_compatible


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
        if len(self.filter_meta(context.siblings_post)) > 0:
            # This can only fail on the last segment
            return None
        elif len(context.segment.segments) > 0:
            # This can only fail on the last base segment
            return None
        elif context.segment.is_meta:
            # We can't fail on a meta segment
            return None
        else:
            # We know we are at a leaf of the tree but not necessarily at the end of the tree.
            # Therefore we look backwards up the parent stack and ask if any of the parent segments
            # have another non-meta child segment after the current one.
            child_segment = context.segment
            for parent_segment in context.parent_stack[::-1]:
                possible_children = [s for s in parent_segment.segments if not s.is_meta]
                if len(possible_children) > possible_children.index(child_segment) + 1:
                    return None
                child_segment = parent_segment

        # Include current segment for complete stack.
        complete_stack: List[BaseSegment] = list(context.raw_stack)
        complete_stack.append(context.segment)

        # Iterate backwards over complete stack to find
        # last non-newline/whitespace/Dedent segment
        # and the newline segments following it.
        anchor_segment = context.segment
        eof_newline_segments = []
        for segment in complete_stack[::-1]:
            if segment.is_type("newline"):
                eof_newline_segments.append(segment)
            elif segment.name not in ("whitespace", "Dedent"):
                break
            anchor_segment = segment

        if len(eof_newline_segments) == 1:
            # No need for fix if single new line exists.
            return None
        elif len(eof_newline_segments) == 0:
            # We make an edit to create this segment after the child of the FileSegment.
            return LintResult(
                anchor=anchor_segment,
                fixes=[
                    LintFix(
                        "edit",
                        context.parent_stack[1],
                        [context.parent_stack[1], NewlineSegment()],
                    )
                ],
            )
        else:
            # There are excess newlines so delete all bar one.
            return LintResult(
                anchor=anchor_segment,
                fixes=[LintFix("delete", d) for d in eof_newline_segments[1:]],
            )
