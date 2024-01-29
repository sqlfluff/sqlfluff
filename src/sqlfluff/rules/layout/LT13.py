"""Implementation of Rule LT13."""

from typing import Optional

from sqlfluff.core.rules import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import RootOnlyCrawler
from sqlfluff.utils.functional import Segments, rsp, sp


class Rule_LT13(BaseRule):
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

    name = "layout.start_of_file"
    aliases = ("L050",)
    groups = ("all", "layout")
    targets_templated = True
    # Use the RootOnlyCrawler to only call _eval() ONCE, with the root segment.
    crawl_behaviour = RootOnlyCrawler()
    lint_phase = "post"
    is_fix_compatible = True

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Files must not begin with newlines or whitespace."""
        # Only check raw segments. This ensures we don't try and delete the same
        # whitespace multiple times (i.e. for non-raw segments higher in the
        # tree).
        raw_segments = []
        whitespace_types = {"newline", "whitespace", "indent", "dedent"}
        for seg in context.segment.recursive_crawl_all():
            if not seg.is_raw():
                continue

            if seg.is_type(*whitespace_types):
                raw_segments.append(seg)
                continue

            raw_stack = Segments(*raw_segments, templated_file=context.templated_file)
            # Non-whitespace segment.
            if (
                not raw_stack.all(sp.is_meta())
                # It is possible that a template segment (e.g.
                # {{ config(materialized='view') }}) renders to an empty string
                # and as such is omitted from the parsed tree. We therefore
                # should flag if a templated raw slice intersects with the
                # source slices in the raw stack and skip this rule to avoid
                # risking collisions with template objects.
                and not raw_stack.raw_slices.any(rsp.is_slice_type("templated"))
            ):
                return LintResult(
                    anchor=context.segment,
                    fixes=[LintFix.delete(d) for d in raw_stack],
                )
            else:
                break
        return None
