"""Implementation of Rule L046."""
from typing import Tuple

from sqlfluff.core.rules.base import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.functional import rsp


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

    targets_templated = True

    @staticmethod
    def _get_whitespace_ends(s: str) -> Tuple[str, str, str]:
        """Remove tag ends and partition off any whitespace ends."""
        # Jinja tags all have a length of two. We can use slicing
        # to remove them easily.
        main = s[2:-2]
        # Optionally Jinja tags may also have plus of minus notation
        # https://jinja2docs.readthedocs.io/en/stable/templates.html#whitespace-control
        modifier_chars = ["+", "-"]
        if main and main[0] in modifier_chars:
            main = main[1:]
        if main and main[-1] in modifier_chars:
            main = main[:-1]
        inner = main.strip()
        pos = main.find(inner)
        return main[:pos], inner, main[pos + len(inner) :]

    def _eval(self, context: RuleContext) -> LintResult:
        """Look for non-literal segments."""
        if context.segment.is_raw() and not context.segment.pos_marker.is_literal():
            # Does it actually look like a tag?
            templated_raw_slices = context.functional.segment.raw_slices.select(
                rsp.is_slice_type("templated")
            )
            for raw_slice in templated_raw_slices:
                src_raw = raw_slice.raw
                if not src_raw or src_raw[0] != "{" or src_raw[-1] != "}":
                    return LintResult(memory=context.memory)  # pragma: no cover

                # Dedupe using a memory of source indexes.
                # This is important because several positions in the
                # templated file may refer to the same position in the
                # source file and we only want to get one violation.
                src_idx = raw_slice.source_idx
                if context.memory and src_idx in context.memory:
                    return LintResult(memory=context.memory)
                if not context.memory:
                    memory = set()
                else:
                    memory = context.memory
                memory.add(src_idx)

                # Get the inner section
                ws_pre, inner, ws_post = self._get_whitespace_ends(src_raw)

                # For the following section, whitespace should be a single
                # whitespace OR it should contain a newline.

                # Check the initial whitespace.
                if not ws_pre or (ws_pre != " " and "\n" not in ws_pre):
                    return LintResult(memory=memory, anchor=context.segment)
                # Check latter whitespace.
                if not ws_post or (ws_post != " " and "\n" not in ws_post):
                    return LintResult(memory=memory, anchor=context.segment)

                return LintResult(memory=memory)
        return LintResult(memory=context.memory)
