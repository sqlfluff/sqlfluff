"""Implementation of Rule L008."""
from typing import Optional, Tuple

from sqlfluff.core.parser import WhitespaceSegment

from sqlfluff.core.rules.base import BaseRule, LintResult, LintFix, RuleContext
from sqlfluff.core.rules.doc_decorators import document_fix_compatible
import sqlfluff.core.rules.functional.segment_predicates as sp

from sqlfluff.core.parser.segments.base import BaseSegment


@document_fix_compatible
class Rule_L008(BaseRule):
    """Commas should be followed by a single whitespace unless followed by a comment.

    **Anti-pattern**

    In this example, there is no space between the comma and ``'zoo'``.

    .. code-block:: sql

        SELECT
            *
        FROM foo
        WHERE a IN ('plop','zoo')

    **Best practice**

    Keep a single space after the comma. The ``•`` character represents a space.

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
        # Get all raw segments. "raw_segments" is appropriate as the
        # only segments we can care about are comma, whitespace,
        # newline, and comment, which are all raw. Using the
        # raw_segments allows us to account for possible unexpected
        # parse tree structures resulting from other rule fixes.
        raw_segments = context.functional.raw_segments
        # Start after the current comma within the list. Get all the
        # following whitespace.
        following_segments = raw_segments.select(
            loop_while=sp.or_(sp.is_meta(), sp.is_type("whitespace")),
            start_seg=context.segment,
        )
        subsequent_whitespace = following_segments.last(sp.is_type("whitespace"))
        try:
            return (
                subsequent_whitespace[0] if subsequent_whitespace else None,
                raw_segments[
                    raw_segments.index(context.segment) + len(following_segments) + 1
                ],
            )
        except IndexError:
            # If we find ourselves here it's all whitespace (or nothing) to the
            # end of the file. This can only happen in bigquery (see
            # test_pass_bigquery_trailing_comma).
            return subsequent_whitespace, None

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        # We only care about commas.
        if context.segment.name != "comma":
            return None

        # Get subsequent whitespace segment and the first non-whitespace segment.
        subsequent_whitespace, first_non_whitespace = self._get_subsequent_whitespace(
            context
        )

        if (
            not subsequent_whitespace
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
            subsequent_whitespace
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
