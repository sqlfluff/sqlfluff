"""Implementation of Rule L009."""

from sqlfluff.core.parser import NewlineSegment

from sqlfluff.core.rules.base import BaseRule, LintResult, LintFix
from sqlfluff.core.rules.doc_decorators import document_fix_compatible


@document_fix_compatible
class Rule_L009(BaseRule):
    """Files must end with a trailing newline.

    | **Anti-pattern**
    | The content in file without ends without a trailing newline, the $ represents end of file.

    .. code-block:: sql

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

    | **Best practice**
    | Add trailing newline to the end, the $ character represents end of file.

    .. code-block:: sql

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

    def _eval(self, segment, siblings_post, parent_stack, **kwargs):
        """Files must end with a trailing newline.

        We only care about the segment and the siblings which come after it
        for this rule, we discard the others into the kwargs argument.

        """
        if len(self.filter_meta(siblings_post)) > 0:
            # This can only fail on the last segment
            return None
        elif len(segment.segments) > 0:
            # This can only fail on the last base segment
            return None
        elif segment.name == "newline":
            # If this is the last segment, and it's a newline then we're good
            return None
        elif segment.is_meta:
            # We can't fail on a meta segment
            return None
        else:
            # So this looks like the end of the file, but we
            # need to check that each parent segment is also the last.
            # We do this with reference to the templated file, because it's
            # the best we can do given the information available.
            file_len = len(segment.pos_marker.templated_file.templated_str)
            pos = segment.pos_marker.templated_slice.stop
            # Does the length of the file equal the end of the templated position?
            if file_len != pos:
                return None

        # We're going to make an edit because we're appending to the end and there's
        # no segment after it to match on. Otherwise we would never get a match!
        return LintResult(
            anchor=segment,
            fixes=[LintFix("edit", segment, [segment, NewlineSegment()])],
        )
