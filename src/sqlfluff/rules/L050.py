"""Implementation of Rule L050."""
from typing import Optional

from sqlfluff.core.rules.base import BaseRule, LintFix, LintResult, RuleContext
import sqlfluff.core.rules.functional.segment_predicates as sp
import sqlfluff.core.rules.functional.raw_file_slice_predicates as rsp
from sqlfluff.core.rules.doc_decorators import document_fix_compatible


@document_fix_compatible
class Rule_L050(BaseRule):
    """Files must not begin with newlines or whitespace.

    **Anti-pattern**

    The file begins with newlines or whitespace. The ``^``
    represents the beginning of the file.

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

    **Best practice**

    Start file on either code or comment. (The ``^`` represents the beginning
    of the file.)

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

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Files must not begin with newlines or whitespace."""
        # If parent_stack is empty we are currently at FileSegment.
        if len(context.parent_stack) == 0:
            return None

        # If raw_stack is empty there can be nothing to remove.
        if len(context.raw_stack) == 0:
            return None

        segment = context.functional.segment
        raw_stack = context.functional.raw_stack
        whitespace_types = {"newline", "whitespace", "indent", "dedent"}
        # Non-whitespace segment.
        if (
            # Non-whitespace segment.
            not segment.all(sp.is_type(*whitespace_types))
            # We want first Non-whitespace segment so
            # all preceding segments must be whitespace
            # and at least one is not meta.
            and raw_stack.all(sp.is_type(*whitespace_types))
            and not raw_stack.all(sp.is_meta())
            # Found leaf of parse tree.
            and not segment.all(sp.is_expandable())
            # It is possible that a template segment (e.g.
            # {{ config(materialized='view') }}) renders to an empty string and as such
            # is omitted from the parsed tree. We therefore should flag if a templated
            # raw slice intersects with the source slices in the raw stack and skip this
            # rule to avoid risking collisions with template objects.
            and not raw_stack.raw_slices.any(rsp.is_slice_type("templated"))
        ):
            return LintResult(
                anchor=context.parent_stack[0],
                fixes=[LintFix.delete(d) for d in raw_stack],
            )
        return None
