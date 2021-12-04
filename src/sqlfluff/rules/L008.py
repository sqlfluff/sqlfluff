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
        """Search forwards through the tree for subsequent whitespace.

        We navigate the parse tree to discover any trailing whitespace and
        return a tuple of both the trailing whitespace segment and the
        first non-whitespace segment discovered.
        """
        # In this algorithm we traverse backwards up the parent stack looking
        # at the siblings_post at each level to determine if the next segment
        # is a whitespace and what the first non-whitespace segment is.
        subsequent_whitespace = None
        child = context.segment
        for parent in context.parent_stack[::-1]:
            next_child_index = parent.segments.index(child) + 1
            if next_child_index == len(parent.segments):
                # We are at the end of the current parents children.
                # Continue up the parent stack.
                child = parent
                continue
            # Similar to iterating over context.siblings_post
            # but applied at each level up the parent stack.
            for s in parent.segments[next_child_index:]:
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
            # Current parent becomes the current child
            # of the next parent stack level.
            child = parent

        # If we find ourselves here it's all
        # whitespace (or nothing) to the end of the file.
        # Don't think there's any grammar that allows
        # a comma as the last character in a file so
        # this should never get triggered,
        # but we handle just in case.
        return subsequent_whitespace, None

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Commas should be followed by a single whitespace unless followed by a comment."""
        # We only care about commas.
        if not context.segment.name == "comma":
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
                fixes=[LintFix("create_after", context.segment, WhitespaceSegment())],
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
                fixes=[LintFix("edit", subsequent_whitespace, WhitespaceSegment())],
            )

        return None
