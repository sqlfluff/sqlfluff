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
            # So this looks like the end of the file, but we
            # need to check that each parent segment is also the last.
            # We do this with reference to the templated file, because it's
            # the best we can do given the information available.
            file_len = len(context.segment.pos_marker.templated_file.templated_str)
            pos = context.segment.pos_marker.templated_slice.stop
            # Does the length of the file equal the end of the templated position?
            if file_len != pos:
                return None

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
            # We're going to make an edit because we're appending to the end and there's
            # no segment after it to match on. Otherwise we would never get a match!
            return LintResult(
                anchor=anchor_segment,
                fixes=[
                    LintFix(
                        "edit", context.segment, [context.segment, NewlineSegment()]
                    )
                ],
            )
        else:
            # There are excess newlines so delete all bar one.
            return LintResult(
                anchor=anchor_segment,
                fixes=[LintFix("delete", d) for d in eof_newline_segments[1:]],
            )
