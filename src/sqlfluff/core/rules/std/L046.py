"""Implementation of Rule L046."""

from sqlfluff.core.rules.base import BaseRule, LintResult


class Rule_L046(BaseRule):
    """Jinja tags should have a single whitespace on either side.

    | **Anti-pattern**
    | Jinja tags with either no whitespace or very long whitespace
    | are hard to read.

    .. code-block::

        SELECT {{    a     }} from {{ref('foo')}}

    | **Best practice**
    | A single whitespace surrounding Jinja tags.

    .. code-block::

        SELECT {{ a }} from {{ ref('foo') }}
    """

    targets_templated = True

    def _eval(self, segment, templated_file, memory, **kwargs):
        # Extract some data from the segment. Importantly, all
        # of these have defaults in case we don't have an
        # enriched position marker.
        source_slice = getattr(segment.pos_marker, "source_slice", None)
        is_literal = getattr(segment.pos_marker, "is_literal", None)
        source_str = getattr(templated_file, "source_str", None)

        if source_slice and source_str and not is_literal:
            # Does it actually look like a tag?
            src_raw = source_str[source_slice]
            if src_raw[0] != "{" or src_raw[-1] != "}":
                return LintResult(memory=memory)

            # Dedupe usign a memory of source indexes.
            # This is important because several positions in the
            # templated file may refer to the same position in the
            # source file and we only want to get one violation.
            src_idx = source_slice.start
            if memory and src_idx in memory:
                return LintResult(memory=memory)
            if not memory:
                memory = set()
            memory.add(src_idx)

            # Get the inner section
            inner_str = src_raw[2:-2]

            # Do we have too little whitespace?
            if len(inner_str) < 2 or inner_str[0] != " " or inner_str[-1] != " ":
                print("foo")
                return LintResult(memory=memory, anchor=segment)

            # Do we have too much whitespace?
            if len(inner_str) > 4 and (inner_str[1] == " " or inner_str[-2] == " "):
                print("bar")
                return LintResult(memory=memory, anchor=segment)
        return LintResult(memory=memory)
