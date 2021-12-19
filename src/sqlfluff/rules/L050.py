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
        if len(context.parent_stack) == 0:
            return None

        # If raw_stack is empty there can be nothing to remove.
        if len(context.raw_stack) == 0:
            return None

        # If the current segment is either comment or code and all
        # previous segments are forms of whitespace then we can
        # remove these earlier segments.
        # Given the tree stucture, we make sure we are at the
        # first leaf to avoid repeated detection.
        whitespace_set = {"newline", "whitespace", "Indent", "Dedent"}
        if (
            # Non-whitespace segment.
            (context.segment.name not in whitespace_set)
            # We want first Non-whitespace segment so
            # all preceding segments must be whitespace
            # and at least one is not meta.
            and all(segment.name in whitespace_set for segment in context.raw_stack)
            and not all(segment.is_meta for segment in context.raw_stack)
            # Found leaf of parse tree.
            and (not context.segment.is_expandable)
        ):
            # It is possible that a template segment (e.g. {{ config(materialized='view') }})
            # renders to an empty string and as such is omitted from the parsed tree.
            # We therefore should flag if a templated raw slice intersects with the
            # source slices in the raw stack and skip this rule to avoid risking
            # collisions with template objects.
            if self._potential_template_collision(context):
                return None

            return LintResult(
                anchor=context.parent_stack[0],
                fixes=[LintFix.delete(d) for d in context.raw_stack],
            )

        return None
