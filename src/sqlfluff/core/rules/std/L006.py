"""Implementation of Rule L006."""


from sqlfluff.core.rules.base import BaseCrawler, LintResult, LintFix
from sqlfluff.core.rules.doc_decorators import document_fix_compatible


@document_fix_compatible
class Rule_L006(BaseCrawler):
    """Operators should be surrounded by a single whitespace.

    | **Anti-pattern**
    | The • character represents a space.
    | In this example, there is a space missing space between the operator and 'b'.

    .. code-block:: sql

        SELECT
            a +b
        FROM foo


    | **Best practice**
    | Keep a single space.

    .. code-block:: sql

        SELECT
            a + b
        FROM foo
    """

    def _eval(self, segment, memory, parent_stack, **kwargs):
        """Operators should be surrounded by a single whitespace.

        We use the memory to keep track of whitespace up to now, and
        whether the last code segment was an operator or not.

        """

        def _handle_previous_segments(segments_since_code, anchor, this_segment, fixes):
            """Handle the list of previous segments and return the new anchor and fixes.

            NB: This function mutates `fixes`.
            """
            if len(segments_since_code) == 0:
                # No whitespace, anchor is the segment AFTER where the whitespace
                # should be.
                anchor = this_segment
                fixes.append(
                    LintFix(
                        "create",
                        this_segment,
                        self.make_whitespace(
                            raw=" ", pos_marker=this_segment.pos_marker
                        ),
                    )
                )
            elif len(segments_since_code) > 1 or any(
                elem.is_type("newline") for elem in segments_since_code
            ):
                # TODO: This is a case we should deal with, but there are probably
                # some cases that SHOULDN'T apply here (like comments and newlines)
                # so let's deal with them later
                anchor = None
            else:
                # We know it's just one thing.
                gap_seg = segments_since_code[-1]
                if gap_seg.raw != " ":
                    # It's not just a single space
                    anchor = gap_seg
                    fixes.append(
                        LintFix(
                            "edit",
                            gap_seg,
                            self.make_whitespace(
                                raw=" ", pos_marker=gap_seg.pos_marker
                            ),
                        )
                    )
                else:
                    # We have just the right amount of whitespace!
                    # Unset our signal.
                    anchor = None
            return anchor, fixes

        # anchor is our signal as to whether there's a problem
        anchor = None
        fixes = []
        description = None

        # The parent stack tells us whether we're in an expression or not.
        if parent_stack and parent_stack[-1].is_type("expression"):
            if segment.is_code:
                # This is code, what kind?
                if segment.is_type("binary_operator", "comparison_operator"):
                    # It's an operator, we can evaluate whitespace before it.
                    anchor, fixes = _handle_previous_segments(
                        memory["since_code"],
                        anchor=segment,
                        this_segment=segment,
                        fixes=fixes,
                    )
                    if anchor:
                        description = "Operators should be preceded by a space."
                else:
                    # It's not an operator, we can evaluate what happened after an
                    # operator if that's the last code we saw.
                    if memory["last_code"] and memory["last_code"].is_type(
                        "binary_operator", "comparison_operator"
                    ):
                        # Evaluate whitespace AFTER the operator
                        anchor, fixes = _handle_previous_segments(
                            memory["since_code"],
                            anchor=memory["last_code"],
                            this_segment=segment,
                            fixes=fixes,
                        )
                        if anchor:
                            description = "Operators should be followed by a space."
                    else:
                        # This isn't an operator, and the thing before it wasn't
                        # either. I don't think that's an issue for now.
                        pass
                # Prepare memory for later
                memory["last_code"] = segment
                memory["since_code"] = []
            else:
                # This isn't a code segment...
                # Prepare memory for later
                memory["since_code"].append(segment)
        else:
            # Reset the memory if we're not in an expression
            memory = {"last_code": None, "since_code": []}

        # Anchor is our signal as to whether there's a problem
        if anchor:
            return LintResult(
                anchor=anchor, memory=memory, fixes=fixes, description=description
            )
        else:
            return LintResult(memory=memory)
