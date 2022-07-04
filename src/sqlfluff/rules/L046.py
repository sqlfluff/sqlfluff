"""Implementation of Rule L046."""
from typing import Tuple

from sqlfluff.core.rules.base import (
    BaseRule,
    EvalResultType,
    LintResult,
    RuleContext,
)
from sqlfluff.core.rules.doc_decorators import document_groups


@document_groups
class Rule_L046(BaseRule):
    """Jinja tags should have a single whitespace on either side.

    **Anti-pattern**

    Jinja tags with either no whitespace or very long whitespace
    are hard to read.

    .. code-block:: sql
       :force:

        SELECT {{    a     }} from {{ref('foo')}}

    **Best practice**

    A single whitespace surrounding Jinja tags, alternatively
    longer gaps containing newlines are acceptable.

    .. code-block:: sql
       :force:

        SELECT {{ a }} from {{ ref('foo') }};
        SELECT {{ a }} from {{
            ref('foo')
        }};
    """

    groups = ("all", "core")
    targets_templated = True

    @staticmethod
    def _get_whitespace_ends(s: str) -> Tuple[str, str, str]:
        """Remove tag ends and partition off any whitespace ends."""
        # Jinja tags all have a length of two. We can use slicing
        # to remove them easily.
        main = s[2:-2]
        pre = s[:2]
        post = s[-2:]
        # Optionally Jinja tags may also have plus of minus notation
        # https://jinja2docs.readthedocs.io/en/stable/templates.html#whitespace-control
        modifier_chars = ["+", "-"]
        if main and main[0] in modifier_chars:
            main = main[1:]
            pre = s[:3]
        if main and main[-1] in modifier_chars:
            main = main[:-1]
            post = s[-3:]
        inner = main.strip()
        pos = main.find(inner)
        return pre, main[:pos], inner, main[pos + len(inner) :], post

    def _eval(self, context: RuleContext) -> EvalResultType:
        """Look for non-literal segments."""
        assert context.segment.pos_marker
        if context.segment.is_raw() and not context.segment.pos_marker.is_literal():
            if not context.memory:
                memory = set()
            else:
                memory = context.memory

            # Check whether there's a source representation
            if not context.segment.source_raw:
                return LintResult(memory=memory)

            # Get source representation and strip it
            stripped = context.segment.source_raw.strip()

            # Check for tag presence
            if not stripped or stripped[0] != "{" or stripped[-1] != "}":
                return LintResult(memory=memory)

            self.logger.debug(
                "Tag found @ %s: %r ", context.segment.pos_marker, stripped
            )

            # Have we found this tag already? Abort if so.
            # This is important because several positions in the
            # templated file may refer to the same position in the
            # source file and we only want to get one violation.
            src_pos = context.segment.pos_marker.source_slice.start
            if context.memory and src_pos in context.memory:
                self.logger.debug("Already handled.")
                return LintResult(memory=memory)
            memory.add(src_pos)

            # Partition and Position
            tag_pre, ws_pre, inner, ws_post, tag_post = self._get_whitespace_ends(
                stripped
            )
            position = context.segment.source_raw.find(stripped[0])

            self.logger.debug(
                "Tag string segments: %r | %r | %r | %r | %r @ %s",
                tag_pre,
                ws_pre,
                inner,
                ws_post,
                tag_post,
                position,
            )

            # For the following section, whitespace should be a single
            # whitespace OR it should contain a newline.

            pre_fix = None
            post_fix = None
            # Check the initial whitespace.
            if not ws_pre or (ws_pre != " " and "\n" not in ws_pre):
                pre_fix = " "
            # Check latter whitespace.
            elif not ws_post or (ws_post != " " and "\n" not in ws_post):
                post_fix = " "

            if pre_fix is not None or post_fix is not None:
                # Precalculate the fix even though we don't have the framework to use it yet.
                # fixed = tag_pre + (pre_fix or ws_pre) + inner + (post_fix or ws_post) + tag_post
                return LintResult(
                    memory=memory,
                    anchor=context.segment,
                    description=f"Jinja tags should have a single "
                    f"whitespace on either side: {stripped}",
                )
        return LintResult(memory=context.memory)
