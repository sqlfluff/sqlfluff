"""Implementation of Rule L050."""
from typing import Optional

from sqlfluff.core.rules.base import BaseRule, LintResult, LintFix, RuleContext
from sqlfluff.core.rules.doc_decorators import document_fix_compatible


@document_fix_compatible
class Rule_L050(BaseRule):
    """Files must not begin with newlines or whitespace.

    | **Anti-pattern**
    | The content in file begins with newlines or whitespace, the ^ represents the beginning of file.

    .. code-block:: sql
       :force:

        ^

        SELECT
            a
        FROM foo

        -- Beginning on an indented line is also forbidden,
        -- (the • represents space).

        ••••SELECT
        ••••a
        FROM
        ••••foo

    | **Best practice**
    | Start file on either code or comment, the ^ represents the beginning of file.

    .. code-block:: sql
       :force:


        ^SELECT
            a
        FROM foo

        -- Including an initial block comment.

        ^/*
        This is a description of my SQL code.
        */
        SELECT
            a
        FROM
            foo

        -- Including an initial inline comment.

        ^--This is a description of my SQL code.
        SELECT
            a
        FROM
            foo
    """

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Files must not begin with newlines or whitespace."""
        # If parent_stack is empty we are currently at FileSegment.
        if len(context.parent_stack) == 0:
            return None

        # If the current segment is either comment or code and all
        # previous segments are forms of whitespace then we can
        # remove these earlier segments.
        # Given the tree stucture, we make sure we are at the
        # first leaf to avoid repeated detection.
        if (
            (context.segment.is_comment or context.segment.is_code)
            & (len(context.raw_stack) > 0)
            & set(segment.name for segment in context.raw_stack).issubset(
                {"newline", "whitespace", "Dedent"}
            )
            & (not context.segment.is_expandable)
        ):
            context.memory = {"first": True}
            return LintResult(
                anchor=context.parent_stack[0],
                fixes=[LintFix("delete", d) for d in context.raw_stack],
            )

        return None
