"""Implementation of Rule L046."""

from sqlfluff.core.rules.base import BaseRule, LintResult


class Rule_L046(BaseRule):
    """Jinja tags should have a single whitespace on either side.

    | **Anti-pattern**
    | Jinja tags with either no whitespace or very long whitespace
    | are hard to read.

    .. code-block:: sql

        SELECT {{    a     }} from {{ref('foo')}}

    | **Best practice**
    | A single whitespace surrounding Jinja tags, alternatively
    | longer gaps containing newlines are acceptable.

    .. code-block:: sql

        SELECT {{ a }} from {{ ref('foo') }};
        SELECT {{ a }} from {{
            ref('foo')
        }};
    """

    targets_templated = True

    @staticmethod
    def _get_whitespace_ends(s):
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

    def _eval(self, segment, memory, **kwargs):
        """Look for non-literal segments."""
        if not segment.pos_marker.is_literal():
            # Does it actually look like a tag?
            src_raw = segment.pos_marker.source_str()
            if not src_raw or src_raw[0] != "{" or src_raw[-1] != "}":
                return LintResult(memory=memory)

            # Dedupe using a memory of source indexes.
            # This is important because several positions in the
            # templated file may refer to the same position in the
            # source file and we only want to get one violation.
            src_idx = segment.pos_marker.source_slice.start
            if memory and src_idx in memory:
                return LintResult(memory=memory)
            if not memory:
                memory = set()
            memory.add(src_idx)

            # Get the inner section
            ws_pre, inner, ws_post = self._get_whitespace_ends(src_raw)

            # For the following section, whitespace should be a single
            # whitespace OR it should contain a newline.

            # Check the initial whitespace.
            if not ws_pre or (ws_pre != " " and "\n" not in ws_pre):
                return LintResult(memory=memory, anchor=segment)
            # Check latter whitespace.
            if not ws_post or (ws_post != " " and "\n" not in ws_post):
                return LintResult(memory=memory, anchor=segment)

        return LintResult(memory=memory)
