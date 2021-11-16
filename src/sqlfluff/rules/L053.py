"""Implementation of Rule L053."""
from typing import Optional

from sqlfluff.core.rules.base import BaseRule, LintResult, LintFix, RuleContext
from sqlfluff.core.rules.doc_decorators import document_fix_compatible


@document_fix_compatible
class Rule_L053(BaseRule):
    """Lone statements should not be wrapped in brackets.

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

    targets_templated = True

    @staticmethod
    def _potential_template_collision(context: RuleContext) -> bool:
        """Check for any templated raw slices that intersect with source slices in the raw_stack.

        Returns:
            :obj:`bool` indicating a preceding templated raw slice has been detected.
        """
        templated_file = context.segment.pos_marker.templated_file
        for segment in context.raw_stack:
            source_slice = segment.pos_marker.source_slice
            raw_slices = templated_file.raw_slices_spanning_source_slice(source_slice)
            if any(
                raw_slice
                for raw_slice in raw_slices
                if raw_slice.slice_type == "templated"
            ):
                return True

        return False

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Files must not begin with newlines or whitespace."""
        # If parent_stack is empty we are currently at FileSegment.
        [segment.type for segment in context.parent_stack] == ["file", "statement"]
        if not (
            context.segment.is_type("bracketed")
            and [segment.type for segment in context.parent_stack]
            == ["file", "statement"]
        ):
            return None

        bracket_set = {"start_bracket", "end_bracket"}
        fixes = [
            LintFix(
                "edit",
                context.segment,
                [
                    segment
                    for segment in context.segment.segments
                    if segment.name not in bracket_set
                ],
            )
        ]
        # return None
        return LintResult(anchor=context.segment, fixes=fixes)
