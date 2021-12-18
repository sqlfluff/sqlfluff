"""Implementation of Rule L008."""
from typing import Optional, Tuple

from sqlfluff.core.parser import WhitespaceSegment

from sqlfluff.core.rules.base import BaseRule, LintResult, LintFix, RuleContext
from sqlfluff.core.rules.doc_decorators import document_fix_compatible

from sqlfluff.core.parser.segments.base import BaseSegment


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

    def _get_subsequent_whitespace(
        self,
        context,
    ) -> Tuple[Optional[BaseSegment], Optional[BaseSegment]]:
        """Search forwards through the raw segments for subsequent whitespace.

        Return a tuple of both the trailing whitespace segment and the
        first non-whitespace segment discovered.
        """
        subsequent_whitespace = None
        # Get all raw segments and find position of the current comma within the list.
        file_segment = context.parent_stack[0]
        raw_segments = file_segment.get_raw_segments()
        # Raw stack is appropriate as the only segments we can care about are
        # comma, whitespace, newline, and comment, which are all raw.
        # Using the raw_segments allows us to account for possible unexpected
        # parse tree structures resulting from other rule fixes.
        next_raw_index = raw_segments.index(context.segment) + 1
        # Iterate forwards over raw segments to find both the whitespace segment and
        # the first non-whitespace segment.
        for s in raw_segments[next_raw_index:]:
            if s.is_meta:
                continue
            elif s.is_type("whitespace"):
                # Capture the whitespace segment.
                subsequent_whitespace = s
            else:
                # We've found a non-whitespace (and non-meta) segment.
                # Therefore return the stored whitespace segment
                # and this segment for analysis.
                return subsequent_whitespace, s

        # If we find ourselves here it's all
        # whitespace (or nothing) to the end of the file.
        # This can only happen in bigquery (see test_pass_bigquery_trailing_comma).
        return subsequent_whitespace, None

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Commas should be followed by a single whitespace unless followed by a comment."""
        # We only care about commas.
        if context.segment.name != "comma":
            return None

        # Get subsequent whitespace segment and the first non-whitespace segment.
        subsequent_whitespace, first_non_whitespace = self._get_subsequent_whitespace(
            context
        )

        if (
            (subsequent_whitespace is None)
            and (first_non_whitespace is not None)
            and (not first_non_whitespace.is_type("newline"))
        ):
            # No trailing whitespace and not followed by a newline,
            # therefore create a whitespace after the comma.
            return LintResult(
                anchor=first_non_whitespace,
                fixes=[LintFix.create_after(context.segment, [WhitespaceSegment()])],
            )
        elif (
            (subsequent_whitespace is not None)
            and (subsequent_whitespace.raw != " ")
            and (first_non_whitespace is not None)
            and (not first_non_whitespace.is_comment)
        ):
            # Excess trailing whitespace therefore edit to only be one space long.
            return LintResult(
                anchor=subsequent_whitespace,
                fixes=[LintFix.replace(subsequent_whitespace, [WhitespaceSegment()])],
            )

        return None
